import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.validators.input_validator import validate_incident_input

errors = validate_incident_input(
    problem_description="""
SAP production users experienced intermittent login failures after a
database connection pool reached its configured maximum.
""",
    business_impact="""
Around 500 users were unable to process purchase orders,
causing SLA breach risk.
""",
    investigation_timeline="""
09:00 Alert triggered
09:05 Incident bridge opened
09:15 Database team engaged
09:45 Service restored
"""
)

print(errors)