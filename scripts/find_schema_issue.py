import json

INPUT_FILE = "data/raw/dataset_it.jsonl"

for idx, line in enumerate(open(INPUT_FILE, encoding="utf-8"), start=1):

    try:
        record = json.loads(line)

        root = (
            record.get("Root_Cause_Summary")
            or record.get("2.0_Root_Cause_Summary")
        )

        if isinstance(root, list):
            print(f"\nRecord {idx}")
            print(type(root))
            print(root[:1])
            break

    except Exception:
        pass