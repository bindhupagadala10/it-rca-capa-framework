from src.inference.qwen_inference import generate_rca as qwen_generate_rca


def generate_rca_from_incident(
    problem_description,
    business_impact,
    timeline,
    feedback=""
):
    """
    Generates RCA from structured incident fields.
    """

    prompt = f"""
Problem Description

{problem_description}

Business Impact

{business_impact}

Investigation Timeline

{timeline}
"""

    if feedback.strip():

        prompt += f"""

Reviewer Feedback

{feedback}

Please regenerate the RCA by incorporating the reviewer feedback while preserving the complete RCA structure.

Return ALL of the following sections:

Root Cause

Why 1

Why 2

Why 3

Why 4

Why 5
"""

    return qwen_generate_rca(prompt)


# -------------------------------------------------------
# Compatibility wrapper for Streamlit app
# -------------------------------------------------------

def generate_rca(
    incident_text,
    feedback=""
):
    """
    Compatible with app.py.

    incident_text format:

    Problem Description

    ...

    Business Impact

    ...

    Investigation Timeline

    ...
    """

    problem_description = ""
    business_impact = ""
    timeline = ""

    current = None

    for line in incident_text.splitlines():

        text = line.strip()

        if text == "Problem Description":
            current = "problem"
            continue

        elif text == "Business Impact":
            current = "impact"
            continue

        elif text == "Investigation Timeline":
            current = "timeline"
            continue

        if current == "problem":
            problem_description += line + "\n"

        elif current == "impact":
            business_impact += line + "\n"

        elif current == "timeline":
            timeline += line + "\n"

    return generate_rca_from_incident(
        problem_description=problem_description.strip(),
        business_impact=business_impact.strip(),
        timeline=timeline.strip(),
        feedback=feedback,
    )