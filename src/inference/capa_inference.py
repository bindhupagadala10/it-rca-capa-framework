import src.inference.mistral_inference as mistral


def generate_capa_from_rca(
    rca_text,
    feedback=""
):

    prompt = rca_text

    if feedback.strip():

        prompt += f"""

Reviewer Feedback

{feedback}

Please regenerate the CAPA by incorporating the reviewer feedback.
"""

    return mistral.generate_capa(prompt)


# -------------------------------------------------
# Compatibility wrapper for Streamlit app
# -------------------------------------------------

def generate_capa(
    incident_text,
    rca_text,
    feedback=""
):
    """
    incident_text is accepted for compatibility with app.py.
    Currently the CAPA model only uses the approved RCA.
    """

    return generate_capa_from_rca(
        rca_text=rca_text,
        feedback=feedback,
    )