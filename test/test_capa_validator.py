# test_capa_validator.py
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
import json

from src.validators.capa_validator import CAPAValidator

validator = CAPAValidator()

with open(
    "results/capa_predictions_10.json",
    "r",
    encoding="utf-8"
) as f:

    records = json.load(f)

print("\nCAPA VALIDATION RESULTS\n")

for idx, record in enumerate(records, start=1):

    incident = record.get(
        "input",
        ""
    )

    prediction = record.get(
        "prediction",
        ""
    )

    flags = validator.validate(
        incident,
        prediction
    )

    print("=" * 80)

    print(f"Record {idx}")

    if flags:

        for flag in flags:
            print(flag)

    else:
        print("PASS")