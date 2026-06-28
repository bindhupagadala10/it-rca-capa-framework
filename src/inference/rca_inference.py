

from src.inference.qwen_inference import generate_rca


def generate_rca_from_incident(
    problem_description,
    business_impact,
    timeline,
    feedback=""
):

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

Please regenerate the RCA by incorporating the reviewer feedback.
"""

    return generate_rca(prompt)