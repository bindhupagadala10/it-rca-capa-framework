import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
from src.validators.rca_validator import validate_rca
from src.validators.capa_validator import CAPAValidator


def run_pipeline(
    incident_text,
    rca_text,
    capa_text
):

    rca_flags = validate_rca(
        incident_text,
        rca_text
    )

    capa_validator = CAPAValidator()

    capa_flags = capa_validator.validate(
        incident_text,
        capa_text
    )

    print("\nRCA FLAGS\n")

    if rca_flags:
        for flag in rca_flags:
            print(flag)
    else:
        print("PASS")

    print("\nCAPA FLAGS\n")

    if capa_flags:
        for flag in capa_flags:
            print(flag)
    else:
        print("PASS")

if __name__ == "__main__":

    incident_text = """
    Application outage affecting SAP production users.
    """

    rca_text = """
    Root Cause:
    Database connection pool exhausted.

    Why 1:
    Connection pool reached maximum limit.

    Why 2:
    Long running queries were not terminated.

    Why 3:
    Query optimization was missing.

    Why 4:
    Database maintenance procedure was skipped.

    Why 5:
    Ownership of maintenance schedule was unclear.
    """

    capa_text = """
    Corrective Action:
    Increase connection pool size.

    Preventive Action:
    Configure monitoring dashboard and alerts.

    Database Team will review pool utilization weekly.
    """

    run_pipeline(
        incident_text,
        rca_text,
        capa_text
    )