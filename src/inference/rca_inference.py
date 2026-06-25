from src.inference.qwen_inference import generate_rca as _generate_rca


def generate_rca_from_incident(
    problem_description,
    business_impact,
    timeline,
    feedback=""
):

    prompt = f"""
Problem Description:
{problem_description}

Business Impact:
{business_impact}

Investigation Timeline:
{timeline}

Additional Reviewer Feedback:
{feedback}

Generate a complete Root Cause Analysis including:
- Investigation Summary
- Five Why Analysis
- Root Cause
"""

    return _generate_rca(prompt)


def generate_rca(incident_text, feedback=""):
    from src.report.doc_generator import _parse_incident
    parsed = _parse_incident(incident_text)
    return generate_rca_from_incident(
        problem_description=parsed.get("Problem Description", ""),
        business_impact=parsed.get("Business Impact", ""),
        timeline=parsed.get("Investigation Timeline", ""),
        feedback=feedback
    )