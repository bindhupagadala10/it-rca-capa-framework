import json
from collections import defaultdict

INPUT_FILE = "data/raw/dataset_it.jsonl"

types = defaultdict(set)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        try:
            record = json.loads(line)

            for key, value in record.items():
                types[key].add(type(value).__name__)

        except:
            pass

for k, v in sorted(types.items()):
    print(k)
    print(" ", v)