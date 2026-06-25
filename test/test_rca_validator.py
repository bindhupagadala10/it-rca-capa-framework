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

with open(
    "results/rca_predictions_10.json",
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)

sample = data[0]

prediction = sample["prediction"]

incident_text = prediction

flags = validate_rca(
    incident_text,
    prediction,
)

print("\nFLAGS\n")

if not flags:

    print("PASS")

else:

    for flag in flags:

        print(flag)