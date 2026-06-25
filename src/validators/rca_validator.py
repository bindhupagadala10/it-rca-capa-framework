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


def validate_rca(incident_text,rca_text):

    flags = []

    # RCA001 - Unsupported Technology Introduction
    introduced = find_introduced_technologies(
        incident_text,
        rca_text
    )

    if introduced:

        flags.append({
            "id": "RCA001",
            "severity": "HIGH",
            "message": (
                f"Unsupported technologies introduced: "
                f"{introduced}"
            )
        })

    # RCA002 - Generic Root Cause Phrases
    rca_lower = rca_text.lower()

    for phrase in GENERIC_PHRASES:

        if phrase in rca_lower:

            flags.append({
                "id": "RCA002",
                "severity": "HIGH",
                "message": (
                    f"Generic RCA phrase detected: "
                    f"{phrase}"
                )
            })

    # RCA003 - Too Short
    if len(rca_text.split()) < 50:

        flags.append({
            "id": "RCA003",
            "severity": "MEDIUM",
            "message": (
                "RCA appears unusually short."
            )
        })

    # RCA004 - Missing Root Cause Section
    if "root cause" not in rca_lower:

        flags.append({
            "id": "RCA004",
            "severity": "HIGH",
            "message": (
                "Root Cause Summary missing."
            )
        })

    # RCA005 - Missing Why Levels
    why_count = 0

    for i in range(1, 6):

        if f"why {i}" in rca_lower:

            why_count += 1

    if why_count < 5:

        flags.append({
            "id": "RCA005",
            "severity": "HIGH",
            "message": (
                f"Only {why_count}/5 Why levels found."
            )
        })

    # RCA006 - Weak Evidence Support
    overlap = keyword_overlap(
        incident_text,
        rca_text
    )

    if overlap < 5:

        flags.append({
            "id": "RCA006",
            "severity": "MEDIUM",
            "message": (
                "Weak evidence support from incident details."
            )
        })

    return flags