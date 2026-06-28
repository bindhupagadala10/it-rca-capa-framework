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