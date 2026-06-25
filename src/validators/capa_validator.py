# src/validators/capa_validator.py

import re

from src.validators.technology_detector import (
    extract_technologies,
    find_introduced_technologies
)


class CAPAValidator:

    def __init__(self):
        self.flags = []

    def validate(self, incident_text, capa_text):

        self.flags = []

        self._check_technology_introduction(
            incident_text,
            capa_text
        )

        self._check_missing_monitoring(capa_text)

        self._check_missing_ownership(capa_text)

        self._check_non_actionable(capa_text)

        self._check_boilerplate(capa_text)

        return self.flags

    # --------------------------------------------------
    # CAPA001
    # --------------------------------------------------

    def _check_technology_introduction(
        self,
        incident_text,
        capa_text
    ):

        introduced = find_introduced_technologies(
            incident_text,
            capa_text
        )

        if introduced:

            self.flags.append(
                {
                    "id": "CAPA001",
                    "severity": "HIGH",
                    "message": (
                        "CAPA introduces unsupported "
                        f"technology references: {introduced}"
                    )
                }
            )

    # --------------------------------------------------
    # CAPA002
    # --------------------------------------------------

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

            self.flags.append(
                {
                    "id": "CAPA002",
                    "severity": "MEDIUM",
                    "message": (
                        "CAPA does not contain "
                        "monitoring or detection improvements."
                    )
                }
            )

    # --------------------------------------------------
    # CAPA003
    # --------------------------------------------------

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

            if re.search(
                pattern,
                capa_text,
                flags=re.IGNORECASE
            ):
                found = True
                break

        if not found:

            self.flags.append(
                {
                    "id": "CAPA003",
                    "severity": "MEDIUM",
                    "message": (
                        "No ownership or responsible "
                        "team identified in CAPA."
                    )
                }
            )

    # --------------------------------------------------
    # CAPA004
    # --------------------------------------------------

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

            self.flags.append(
                {
                    "id": "CAPA004",
                    "severity": "HIGH",
                    "message": (
                        "CAPA contains non-actionable "
                        f"statements: {hits}"
                    )
                }
            )

    # --------------------------------------------------
    # CAPA005
    # --------------------------------------------------

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

            self.flags.append(
                {
                    "id": "CAPA005",
                    "severity": "LOW",
                    "message": (
                        "Potential boilerplate CAPA "
                        f"language detected: {hits}"
                    )
                }
            )