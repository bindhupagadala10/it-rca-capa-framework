import json

with open(
    "results/rca_predictions_10.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

print(type(data))
print(len(data))

print("\nKEYS:")
print(data[0].keys())

print("\nFIRST RECORD:")
print(data[0])