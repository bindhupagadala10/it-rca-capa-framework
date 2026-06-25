# src/inference/mock_inference.py

import random

ROOT_CAUSES = [
    "Database connection pool exhaustion.",
    "Application server memory leak.",
    "Network latency between application and database.",
    "Expired authentication token configuration.",
    "Load balancer routing misconfiguration."
]


def generate_mock_rca(incident, feedback=""):

    cause = random.choice(ROOT_CAUSES)

    version = random.randint(1000, 9999)

    return f"""
RCA Version : {version}

Incident

{incident}

Reviewer Feedback

{feedback if feedback else "None"}

Root Cause

{cause}

Why 1
Immediate failure occurred.

Why 2
Monitoring thresholds were insufficient.

Why 3
Operational process was not followed.

Why 4
Ownership review was missed.

Why 5
Governance controls were ineffective.
"""


def generate_mock_capa(incident, rca, feedback=""):

    version = random.randint(1000, 9999)

    return f"""
CAPA Version : {version}

Corrective Action

Resolve the identified root cause immediately.

Preventive Action

Implement monitoring dashboards.

Ownership

Infrastructure Team

Monitoring

Weekly operational review.

Reviewer Feedback

{feedback if feedback else "None"}
"""