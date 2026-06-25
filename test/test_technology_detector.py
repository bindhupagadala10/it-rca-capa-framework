import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.validators.technology_detector import (
    find_introduced_technologies
)

incident = """
NGINX load balancer outage.
"""

output = """
Deploy Kafka and Prometheus.
"""

print(
    find_introduced_technologies(
        incident,
        output
    )
)