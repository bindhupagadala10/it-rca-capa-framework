import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.inference.qwen_inference import generate_rca

prompt = """
Problem Description:
Database outage due to replication lag.

Business Impact:
Customer transactions delayed.

Technical Investigation Timeline:
Replication stopped.
Primary node overloaded.
Failover initiated.
"""

output = generate_rca(prompt)

print(output)