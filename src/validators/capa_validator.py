# src/validators/capa_validator.py

import re

from src.validators.technology_detector import (
    find_introduced_technologies
)


def extract_capa_section(text, heading, following_headings):
    if not following_headings:
        match = re.search(
            rf"(?ims)^\s*{re.escape(heading)}\s*:?\s*$\s*(.*)\Z",
            text,
        )
        return match.group(1).strip() if match else ""

    end_pattern = "|".join(re.escape(item) for item in following_headings)
    match = re.search(
        rf"(?ims)^\s*{re.escape(heading)}\s*:?\s*$\s*(.*?)"
        rf"(?=^\s*(?:{end_pattern})\s*:?\s*$|\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


class CAPAValidator:

    def __init__(self):
        self.flags = []

    def validate(self, incident_text, capa_text, rca_text=""):
        self.flags = []

        # 1. Structural Checks First (Empty/Malformed)
        if not capa_text or not capa_text.strip():
            self.flags.append({
                "id": "CAPA004",
                "severity": "HIGH",
                "message": "CAPA plan is empty."
            })
            return self.flags

        # Validate required sections
        capa_headings = ("Preventive Action", "Lessons Learned")
        corrective_action = extract_capa_section(capa_text, "Corrective Action", capa_headings)
        preventive_action = extract_capa_section(capa_text, "Preventive Action", ("Lessons Learned",))
        lessons_learned = extract_capa_section(capa_text, "Lessons Learned", ())

        sections_content = []

        if not corrective_action:
            self.flags.append({
                "id": "CAPA004",
                "severity": "HIGH",
                "message": "Corrective Action section is missing or empty."
            })
        else:
            sections_content.append(corrective_action.lower())

        if not preventive_action:
            self.flags.append({
                "id": "CAPA004",
                "severity": "HIGH",
                "message": "Preventive Action section is missing or empty."
            })
        else:
            sections_content.append(preventive_action.lower())

        if not lessons_learned:
            self.flags.append({
                "id": "CAPA004",
                "severity": "HIGH",
                "message": "Lessons Learned section is missing or empty."
            })
        else:
            sections_content.append(lessons_learned.lower())

        # If any major structural section is missing, we stop here or continue.
        # Let's continue to gather all details unless it was completely empty.

        # 2. Consistency Checks
        # CAPA001: Unsupported Technology Introduction
        introduced = find_introduced_technologies(incident_text, capa_text)
        if introduced:
            self.flags.append({
                "id": "CAPA001",
                "severity": "HIGH",
                "message": f"CAPA introduces unsupported technology references: {introduced}"
            })

        # Evidence overlap / keyword overlap check (Incident consistency)
        capa_words = set(re.findall(r"\b[a-zA-Z]{5,}\b", capa_text.lower()))
        incident_words = set(re.findall(r"\b[a-zA-Z]{5,}\b", incident_text.lower()))
        overlap_incident = incident_words.intersection(capa_words)
        if len(overlap_incident) < 3:
            self.flags.append({
                "id": "CAPA006",
                "severity": "MEDIUM",
                "message": "Weak evidence support (very low keyword overlap between CAPA and incident)."
            })

        # RCA-CAPA Consistency Check
        if rca_text:
            rca_words = set(re.findall(r"\b[a-zA-Z]{5,}\b", rca_text.lower()))
            overlap_rca = rca_words.intersection(capa_words)
            if len(overlap_rca) < 3:
                self.flags.append({
                    "id": "CAPA006",
                    "severity": "MEDIUM",
                    "message": "RCA-CAPA inconsistency (low keyword overlap between CAPA and approved RCA)."
                })

        # 3. Quality Checks
        # CAPA002: Missing Monitoring
        self._check_missing_monitoring(capa_text)

        # CAPA003: Missing Ownership
        self._check_missing_ownership(capa_text)

        # CAPA004: Non-actionable Statements
        self._check_non_actionable(capa_text)

        # CAPA005: Boilerplate Language
        self._check_boilerplate(capa_text)

        # Repeated/duplicated content check across sections
        unique_sections = set()
        has_dupes = False
        for content in sections_content:
            cleaned_content = re.sub(r'\s+', ' ', content).strip()
            if cleaned_content:
                if cleaned_content in unique_sections:
                    has_dupes = True
                unique_sections.add(cleaned_content)
        if has_dupes:
            self.flags.append({
                "id": "CAPA005",
                "severity": "HIGH",
                "message": "Repeated/copied content detected across different CAPA sections."
            })

        return self.flags

    def _check_missing_monitoring(self, capa_text):
        monitoring_keywords = [
            "monitor",
            "monitoring",
            "alert",
            "alerts",
            "dashboard",
            "metric",
            "metrics",
            "threshold",
            "observability",
            "logging",
            "log review"
        ]

        found = any(
            word.lower() in capa_text.lower()
            for word in monitoring_keywords
        )

        if not found:
            self.flags.append({
                "id": "CAPA002",
                "severity": "MEDIUM",
                "message": "CAPA does not contain monitoring or detection improvements."
            })

    def _check_missing_ownership(self, capa_text):
        ownership_patterns = [
            r"\bteam\b",
            r"\bowner\b",
            r"\bapplication team\b",
            r"\binfrastructure team\b",
            r"\bdatabase team\b",
            r"\bnetwork team\b",
            r"\bsre\b",
            r"\bdevops\b",
            r"\bplatform team\b",
            r"\bservice owner\b"
        ]

        found = False
        for pattern in ownership_patterns:
            if re.search(pattern, capa_text, flags=re.IGNORECASE):
                found = True
                break

        if not found:
            self.flags.append({
                "id": "CAPA003",
                "severity": "MEDIUM",
                "message": "No ownership or responsible team identified in CAPA."
            })

    def _check_non_actionable(self, capa_text):
        weak_phrases = [
            "investigate further",
            "look into issue",
            "review system",
            "monitor closely",
            "check logs",
            "continue monitoring",
            "analyze issue",
            "follow up later"
        ]

        hits = []
        for phrase in weak_phrases:
            if phrase.lower() in capa_text.lower():
                hits.append(phrase)

        if hits:
            self.flags.append({
                "id": "CAPA004",
                "severity": "HIGH",
                "message": f"CAPA contains non-actionable statements: {hits}"
            })

    def _check_boilerplate(self, capa_text):
        boilerplate_phrases = [
            "best practices",
            "take necessary action",
            "appropriate measures",
            "prevent recurrence",
            "ensure issue does not happen again",
            "improve process",
            "follow standard procedures"
        ]

        hits = []
        for phrase in boilerplate_phrases:
            if phrase.lower() in capa_text.lower():
                hits.append(phrase)

        if hits:
            self.flags.append({
                "id": "CAPA005",
                "severity": "LOW",
                "message": f"Potential boilerplate CAPA language detected: {hits}"
            })