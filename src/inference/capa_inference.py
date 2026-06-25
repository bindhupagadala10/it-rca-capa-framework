from collections.abc import Callable
from importlib import import_module
from typing import Any


def _validate_text(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")

    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError(f"{name} cannot be empty.")

    return normalized_value


def _load_capa_generator() -> Callable[[str], Any]:
    inference_module = import_module("src.inference.mistral_inference")

    for function_name in ("generate_capa", "generate_text", "generate"):
        generator = getattr(inference_module, function_name, None)
        if callable(generator):
            return generator

    raise RuntimeError(
        "src.inference.mistral_inference does not expose a supported CAPA "
        "generation function."
    )


def _extract_generated_text(response: Any) -> str:
    if isinstance(response, str):
        generated_text = response
    elif isinstance(response, dict):
        generated_text = next(
            (
                response[key]
                for key in ("generated_text", "text", "content", "response")
                if isinstance(response.get(key), str)
            ),
            "",
        )
    elif isinstance(response, (list, tuple)) and response:
        return _extract_generated_text(response[0])
    else:
        generated_text = ""

    generated_text = generated_text.strip()
    if not generated_text:
        raise RuntimeError("The CAPA model returned an empty or unsupported response.")

    return generated_text


def generate_capa_from_rca(
    incident_text: str,
    rca_text: str,
    feedback: str = "",
) -> str:
    incident = _validate_text("incident_text", incident_text)
    rca = _validate_text("rca_text", rca_text)

    if not isinstance(feedback, str):
        raise TypeError("feedback must be a string.")

    reviewer_feedback = feedback.strip() or "No additional reviewer feedback."

    prompt = f"""
You are an enterprise IT service management specialist.

Create a complete Corrective and Preventive Action plan using only the
confirmed incident and approved Root Cause Analysis below.

Incident:
{incident}

Approved Root Cause Analysis:
{rca}

Reviewer Feedback:
{reviewer_feedback}

Return a specific, actionable CAPA containing:
1. Immediate Corrective Actions
2. Long-Term Preventive Actions
3. Responsible Owner for every action
4. Target Completion or Review Cadence
5. Monitoring, Alerting, and Effectiveness Measures
6. Closure Criteria

Do not introduce technologies or facts that are absent from the incident or
approved RCA. Avoid generic recommendations and non-actionable language.
""".strip()

    generator = _load_capa_generator()
    return _extract_generated_text(generator(prompt))


generate_capa = generate_capa_from_rca
