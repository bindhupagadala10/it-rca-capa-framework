from src.inference.qwen_inference import generate_rca as qwen_generate_rca


def generate_rca_from_incident(
    problem_description,
    business_impact,
    timeline,
    feedback="",
    current_rca=""
):
    """
    Generates RCA from structured incident fields and optional feedback/previous RCA.
    Returns the RAW model output.
    """

    if feedback.strip() and current_rca.strip():
        # Regeneration Prompt
        prompt = f"""You are a senior IT incident investigator.
Analyze the incident details, the current RCA, and the reviewer's feedback, then regenerate a revised Root Cause Analysis.

Incident Details:
- Problem Description: {problem_description}
- Business Impact: {business_impact}
- Investigation Timeline: {timeline}

Current RCA:
{current_rca}

Reviewer Feedback:
{feedback}

Instructions:
1. Revise the Current RCA by addressing the Reviewer Feedback.
2. Edit only the necessary parts to incorporate the feedback, and preserve the rest of the Current RCA's structure and valid information. Do NOT start from scratch.
3. Keep the analysis strictly focused on the evidence and systems mentioned in the incident details. Do NOT introduce unrelated software tools, hardware, or technologies that are not part of the incident context.
4. Provide a technical, specific, and detailed explanation. Do NOT use generic or vague phrases (e.g., do not write lazy explanations like "human error", "mistake", "issue occurred", or "lack of awareness").
5. The output must contain exactly these sections in this order:
Root Cause
Why 1
Why 2
Why 3
Why 4
Why 5

6. For each "Why [Number]" section, provide a specific question on one line, followed by the word "Answer:" on its own line, followed by the specific technical answer explaining the cause. For example:
Why 1
Why did the application fail to connect to the database?
Answer:
The connection pool was exhausted because long-running reports held onto connections.

7. Output ONLY the RCA sections. Do NOT repeat the incident description, business impact, timeline, or add any conversational introduction/conclusion.
"""
    else:
        # Initial Generation Prompt
        prompt = f"""You are a senior IT incident investigator.
Analyze the incident details below and generate a Root Cause Analysis (RCA).

Incident Details:
- Problem Description: {problem_description}
- Business Impact: {business_impact}
- Investigation Timeline: {timeline}

Instructions:
1. Perform a thorough 5-Why analysis to trace the technical failure to its systemic root cause.
2. Keep the analysis strictly focused on the evidence and systems mentioned in the incident details. Do NOT introduce unrelated software tools, hardware, or technologies that are not part of the incident context.
3. Provide a technical, specific, and detailed explanation. Do NOT use generic or vague phrases (e.g., do not write lazy explanations like "human error", "mistake", "issue occurred", or "lack of awareness").
4. The output must contain exactly these sections in this order:
Root Cause
Why 1
Why 2
Why 3
Why 4
Why 5

5. For each "Why [Number]" section, provide a specific question on one line, followed by the word "Answer:" on its own line, followed by the specific technical answer explaining the cause. For example:
Why 1
Why did the application fail to connect to the database?
Answer:
The connection pool was exhausted because long-running reports held onto connections.

6. Output ONLY the RCA sections. Do NOT repeat the incident description, business impact, timeline, or add any conversational introduction/conclusion.
"""

    return qwen_generate_rca(prompt)


# -------------------------------------------------------
# Compatibility wrapper for Streamlit app
# -------------------------------------------------------

def generate_rca(
    incident_text,
    feedback="",
    current_rca=""
):
    """
    Compatible wrapper that parses incident_text and calls generate_rca_from_incident.
    Returns the RAW model output.
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
        current_rca=current_rca,
    )