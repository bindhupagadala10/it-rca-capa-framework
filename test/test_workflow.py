import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.validators.rca_validator import (
    validate_rca
)

incident = """
Problem Description:
Database outage due to replication lag.

Business Impact:
Transactions delayed.

Timeline:
Replication stopped.
Primary overloaded.
"""

generated_rca = """
5 Why Analysis:
...

Root Cause Summary:
Replication monitoring was absent and failover thresholds were improperly configured.
"""

flags = validate_rca(
    incident,
    generated_rca,
)

print("\nRCA FLAGS\n")

if not flags:

    print("PASS")

else:

    for flag in flags:

        print(flag)