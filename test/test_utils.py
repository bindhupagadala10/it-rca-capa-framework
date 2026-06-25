import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
from src.utils.text_utils import find_new_terms

incident = """
NGINX load balancer outage
"""

output = """
Install Apache Kafka and update NGINX monitoring.
"""

print(find_new_terms(incident, output))