# src/validators/input_validator.py

import re


def validate_incident_input(
    problem_description: str,
    business_impact: str,
    investigation_timeline: str,
):
    """
    Validate mandatory incident fields before invoking the RCA model.

    Returns:
        list[str]: List of validation error messages.
    """

    errors = []

    # --------------------------------------------------
    # Problem Description
    # --------------------------------------------------

    if not problem_description.strip():

        errors.append("Problem Description is required.")

    else:

        if len(problem_description.strip()) < 50:

            errors.append(
                "Problem Description must be at least 50 characters."
            )

        words = re.findall(r"[A-Za-z]+", problem_description)

        if len(words) < 8:

            errors.append(
                "Problem Description should contain meaningful incident details."
            )

    # --------------------------------------------------
    # Business Impact
    # --------------------------------------------------

    if not business_impact.strip():

        errors.append("Business Impact is required.")

    else:

        if len(business_impact.strip()) < 20:

            errors.append(
                "Business Impact must be at least 20 characters."
            )

    # --------------------------------------------------
    # Investigation Timeline
    # --------------------------------------------------

    if not investigation_timeline.strip():

        errors.append(
            "Investigation Timeline is required."
        )

    else:

        if len(investigation_timeline.strip()) < 20:

            errors.append(
                "Investigation Timeline must contain sufficient details."
            )

    return errors