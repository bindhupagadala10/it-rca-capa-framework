import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.inference.rca_inference import generate_rca_from_incident

response = generate_rca_from_incident(
    problem_description="SAP production outage affecting 500 users",
    business_impact="Order processing unavailable",
    timeline="""
09:00 Alert received
09:05 Investigation started
09:20 Database team engaged
09:45 Service restored
"""
)

print(response)