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
2. Edit only the necessary parts to incorporate the feedback while preserving all valid technical findings. Do NOT rewrite the RCA from scratch.
3. Keep the analysis strictly focused on the evidence and systems mentioned in the incident details. Do NOT introduce unrelated technologies, products, software, hardware, or assumptions.
4. Provide technical, specific, and evidence-based reasoning. Avoid vague explanations such as "human error", "mistake", "issue occurred", or "lack of awareness".

Generate EXACTLY the following sections in this order:

Root Cause

Why 1

Why 2

Why 3

Why 4

Why 5

Requirements:

• Under "Root Cause", write a Root Cause Summary consisting of 4-6 complete sentences.
• This section MUST NOT be empty.
• Summarize the underlying technical failure, contributing factors, and systemic cause identified from the complete 5-Why analysis.
• Do NOT simply copy Why 5.
• The Root Cause Summary must be consistent with the 5-Why analysis.

For each Why section:

Why X
Write one specific WHY question.

Answer:
Write the detailed technical answer on the next line.

Generate EXACTLY five Why sections.
Stop after Why 5.
Do NOT generate Why 6 or any additional sections.

Output ONLY the RCA.
Do NOT repeat the incident description, business impact, investigation timeline, reviewer feedback, or add any introduction or conclusion.
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

1. Perform a complete 5-Why analysis to identify the underlying systemic technical root cause.
2. Keep the analysis strictly focused on the evidence contained in the incident. Do NOT introduce unrelated technologies, products, software, hardware, or assumptions.
3. Provide technical, specific, and evidence-based reasoning. Avoid vague explanations such as "human error", "mistake", "issue occurred", or "lack of awareness".

Generate EXACTLY the following sections in this order:

Root Cause

Why 1

Why 2

Why 3

Why 4

Why 5

Requirements:

• Under "Root Cause", write a Root Cause Summary consisting of 4-6 complete sentences.
• This section MUST NOT be empty.
• Summarize the overall technical failure, contributing factors, and systemic cause discovered from the complete 5-Why analysis.
• Do NOT simply repeat Why 5.
• The Root Cause Summary should synthesize the entire analysis.

For each Why section:

Why X
Write one specific WHY question.

Answer:
Write the detailed technical answer on the next line.

Generate EXACTLY five Why sections.
Stop after Why 5.
Do NOT generate Why 6 or any additional sections.

Output ONLY the RCA.
Do NOT repeat the incident description, business impact, investigation timeline, or add any introduction or conclusion.
Output EXACTLY in this format.

Root Cause
<Write a 4-6 sentence root cause summary here>

Why 1
<Write one Why question>
Answer:
<Write one answer>

Why 2
<Write one Why question>
Answer:
<Write one answer>

Why 3
<Write one Why question>
Answer:
<Write one answer>

Why 4
<Write one Why question>
Answer:
<Write one answer>

Why 5
<Write one Why question>
Answer:
<Write one answer>

The Root Cause section must appear BEFORE Why 1.
Do not move it.
Do not repeat it.
Do not generate Why 6.
End the response immediately after the Why 5 answer.
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
          Output EXACTLY in this format.

      Root Cause
      <Write a 4-6 sentence root cause summary here>

      Why 1
      <Write one Why question>
      Answer:
      <Write one answer>

      Why 2
      <Write one Why question>
      Answer:
      <Write one answer>

      Why 3
      <Write one Why question>
      Answer:
      <Write one answer>

      Why 4
      <Write one Why question>
      Answer:
      <Write one answer>

      Why 5
      <Write one Why question>
      Answer:
      <Write one answer>

      The Root Cause section must appear BEFORE Why 1.
      Do not move it.
      Do not repeat it.
      Do not generate Why 6.
      End the response immediately after the Why 5 answer.
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