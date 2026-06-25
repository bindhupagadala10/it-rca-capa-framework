import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import json

from src.validators.rca_validator import (
    validate_rca
)

print("=" * 80)
print("RCA VALIDATION")
print("=" * 80)

with open(
    "results/rca_predictions_10.json",
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)

for i, sample in enumerate(data[:3]):

    prediction = sample["prediction"]

    flags = validate_rca(
        prediction,
        prediction,
    )

    print(f"\nRecord {i+1}")

    if not flags:

        print("PASS")

    else:

        for flag in flags:

            print(flag)