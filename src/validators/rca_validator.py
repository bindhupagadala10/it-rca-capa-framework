import re

from src.validators.technology_detector import (
    find_introduced_technologies
)

GENERIC_PHRASES = [
    "human error",
    "issue occurred",
    "team mistake",
    "lack of awareness",
    "user mistake",
]


def keyword_overlap(
    incident_text,
    rca_text,
):
    incident_words = set(
        re.findall(
            r"\b[a-zA-Z]{5,}\b",
            incident_text.lower()
        )
    )

    rca_words = set(
        re.findall(
            r"\b[a-zA-Z]{5,}\b",
            rca_text.lower()
        )
    )

    overlap = incident_words.intersection(
        rca_words
    )

    return len(overlap)


def extract_rca_section(text, heading, following_headings):
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


def parse_why_section(section):
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    if not lines:
        return "", ""
    question = lines[0]
    answer_lines = []
    answer_started = False
    for line in lines[1:]:
        if line.lower().startswith("answer"):
            answer_started = True
            continue
        if answer_started:
            answer_lines.append(line)
    answer = "\n".join(answer_lines)
    return question, answer


def validate_rca(incident_text, rca_text):
    flags = []

    # 1. Structural Checks First (Empty/Malformed)
    if not rca_text or not rca_text.strip():
        flags.append({
            "id": "RCA004",
            "severity": "HIGH",
            "message": "RCA output is empty."
        })
        return flags

    # Check Root Cause section
    why_headings = tuple(f"Why {index}" for index in range(1, 6))
    root_cause = extract_rca_section(rca_text, "Root Cause", why_headings)
    if not root_cause:
        flags.append({
            "id": "RCA004",
            "severity": "HIGH",
            "message": "Root Cause section is missing or empty."
        })

    # Check Why levels and answers
    why_count = 0
    sections_content = []
    if root_cause:
        sections_content.append(root_cause.lower())

    for index in range(1, 6):
        following = tuple(f"Why {item}" for item in range(index + 1, 6))
        section = extract_rca_section(rca_text, f"Why {index}", following)
        
        if not section:
            flags.append({
                "id": "RCA005",
                "severity": "HIGH",
                "message": f"Why {index} level is missing or empty."
            })
        else:
            why_count += 1
            sections_content.append(section.lower())
            question, answer = parse_why_section(section)
            if not question:
                flags.append({
                    "id": "RCA005",
                    "severity": "HIGH",
                    "message": f"Why {index} level is missing a question."
                })
            if not answer:
                flags.append({
                    "id": "RCA005",
                    "severity": "HIGH",
                    "message": f"Why {index} level is missing an answer (must follow 'Answer:' on its own line)."
                })

    if why_count < 5:
        flags.append({
            "id": "RCA005",
            "severity": "HIGH",
            "message": f"Only {why_count}/5 Why levels found."
        })

    # 2. Consistency Checks
    # Unsupported Technology Introduction (RCA001)
    introduced = find_introduced_technologies(incident_text, rca_text)
    if introduced:
        flags.append({
            "id": "RCA001",
            "severity": "HIGH",
            "message": f"Unsupported technologies introduced: {introduced}"
        })

    # Weak Evidence Support (RCA006)
    overlap = keyword_overlap(incident_text, rca_text)
    if overlap < 5:
        flags.append({
            "id": "RCA006",
            "severity": "MEDIUM",
            "message": "Weak evidence support from incident details (low keyword overlap)."
        })

    # 3. Quality Checks
    # Generic Root Cause Phrases (RCA002)
    rca_lower = rca_text.lower()
    for phrase in GENERIC_PHRASES:
        if phrase in rca_lower:
            flags.append({
                "id": "RCA002",
                "severity": "HIGH",
                "message": f"Generic RCA phrase detected: '{phrase}'."
            })

    # Word Count check (RCA003)
    if len(rca_text.split()) < 50:
        flags.append({
            "id": "RCA003",
            "severity": "MEDIUM",
            "message": "RCA appears unusually short (less than 50 words)."
        })

    # Repeated content across sections check
    unique_sections = set()
    has_dupes = False
    for content in sections_content:
        cleaned_content = re.sub(r'\s+', ' ', content).strip()
        if cleaned_content:
            if cleaned_content in unique_sections:
                has_dupes = True
            unique_sections.add(cleaned_content)
    if has_dupes:
        flags.append({
            "id": "RCA002",
            "severity": "HIGH",
            "message": "Repeated/copied content detected across different RCA sections."
        })

    return flags