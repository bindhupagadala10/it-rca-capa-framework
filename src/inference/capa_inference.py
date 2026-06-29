import src.inference.mistral_inference as mistral


def generate_capa_from_rca(
    incident_text,
    rca_text,
    feedback="",
    current_capa=""
):
    """
    Generates CAPA from RCA and incident context.
    Returns the RAW model output.
    """

    if feedback.strip() and current_capa.strip():
        # Regeneration Prompt
        prompt = f"""You are a senior IT incident investigator and manager.
Analyze the incident details, approved RCA, current CAPA, and reviewer feedback, then regenerate a revised CAPA plan.

Incident Context:
{incident_text}

Approved RCA:
{rca_text}

Current CAPA:
{current_capa}

Reviewer Feedback:
{feedback}

Instructions:
1. Revise the Current CAPA by incorporating the Reviewer Feedback.
2. Edit only the necessary parts to incorporate the feedback, and preserve the rest of the Current CAPA's structure and valid information. Do NOT start from scratch.
3. The output must contain exactly these sections in this order:
Corrective Action
Preventive Action
Lessons Learned

4. Under "Corrective Action", describe the immediate action(s) to resolve the root cause. You must dynamically assign ownership to a specific responsible team (e.g. Network Team, Database Team, Application Team, Infrastructure Team, DevOps, SRE, etc.) based on the specific incident and RCA context. Do NOT use boilerplate ownership placeholders.
5. Under "Preventive Action", describe long-term technical and operational improvements to prevent recurrence. You must specify concrete monitoring, alerting, metrics, dashboards, logging, or threshold improvements.
6. Under "Lessons Learned", describe lessons learned from the incident.
7. Focus strictly on actionable, specific, and detailed tasks. Do NOT use weak, vague, or non-actionable language (e.g. do not write "investigate further", "look into issue", "review system", "monitor closely", "check logs", "continue monitoring", "analyze issue", or "follow up later").
8. Do NOT use boilerplate placeholder phrasing (e.g. do not write "best practices", "take necessary action", "appropriate measures", "prevent recurrence", "ensure issue does not happen again", "improve process", or "follow standard procedures").
9. Keep the CAPA plan focused. Do NOT repeat the incident context or the RCA content. Do NOT add any conversational introduction/conclusion.
"""
    else:
        # Initial Generation Prompt
        prompt = f"""You are a senior IT incident investigator and manager.
Develop a Corrective and Preventive Action (CAPA) plan based on the incident details and the approved RCA.

Incident Context:
{incident_text}

Approved RCA:
{rca_text}

Instructions:
1. Technical Analysis: Formulate a concrete, technical response to address the systemic failures identified in the RCA.
2. The output must contain exactly these sections in this order:
Corrective Action
Preventive Action
Lessons Learned

3. Under "Corrective Action", describe the immediate action(s) to resolve the root cause. You must dynamically assign ownership to a specific responsible team (e.g. Network Team, Database Team, Application Team, Infrastructure Team, DevOps, SRE, etc.) based on the specific incident and RCA context. Do NOT use boilerplate ownership placeholders.
4. Under "Preventive Action", describe long-term technical and operational improvements to prevent recurrence. You must specify concrete monitoring, alerting, metrics, dashboards, logging, or threshold improvements.
5. Under "Lessons Learned", describe lessons learned from the incident.
6. Focus strictly on actionable, specific, and detailed tasks. Do NOT use weak, vague, or non-actionable language (e.g. do not write "investigate further", "look into issue", "review system", "monitor closely", "check logs", "continue monitoring", "analyze issue", or "follow up later").
7. Do NOT use boilerplate placeholder phrasing (e.g. do not write "best practices", "take necessary action", "appropriate measures", "prevent recurrence", "ensure issue does not happen again", "improve process", or "follow standard procedures").
8. Keep the CAPA plan focused. Do NOT repeat the incident context or the RCA content. Do NOT add any conversational introduction/conclusion.
"""

    return mistral.generate_capa(prompt)


# -------------------------------------------------
# Compatibility wrapper for Streamlit app
# -------------------------------------------------

def generate_capa(
    incident_text,
    rca_text,
    feedback="",
    current_capa=""
):
    """
    Compatible wrapper that calls generate_capa_from_rca.
    Returns the RAW model output.
    """

    return generate_capa_from_rca(
        incident_text=incident_text,
        rca_text=rca_text,
        feedback=feedback,
        current_capa=current_capa,
    )