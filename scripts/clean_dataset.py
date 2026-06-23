import json

INPUT_FILE = "data/raw/dataset_it.jsonl"
OUTPUT_FILE = "data/processed/clean_dataset.jsonl"

total = 0
kept = 0

removed_missing_problem = 0
removed_missing_timeline = 0
removed_missing_why = 0
removed_missing_root = 0

parse_errors = 0


def unwrap_record(record):
    """
    Handle:
    {...}
    [{...}]
    [[{...}]]

    until we reach the actual dict.
    """

    while isinstance(record, list):

        if len(record) == 0:
            return None

        record = record[0]

    return record


def normalize_root_cause(record):

    root = record.get("Root_Cause_Summary")

    if not root:
        root = record.get("2.0_Root_Cause_Summary")

    if isinstance(root, list):

        if len(root) > 0:
            root = root[0]
        else:
            root = {}

    if not isinstance(root, dict):
        root = {}

    return root


def normalize_lessons(record):

    lessons = record.get("5.0_Lessons_Learned")

    if not lessons:
        lessons = record.get("5.0_Lessons_Lenared", [])

    if not isinstance(lessons, list):
        lessons = []

    return lessons


with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

    for line in infile:

        total += 1

        try:

            record = json.loads(line)

            record = unwrap_record(record)

            if record is None:
                continue

            if not isinstance(record, dict):
                continue

            summary = record.get(
                "1.0_Problem_Summary",
                {}
            )

            if not isinstance(summary, dict):
                summary = {}

            problem = summary.get(
                "Problem_Description",
                ""
            ).strip()

            timeline = record.get(
                "2.0_Incident_Review_Technical_Investigation",
                []
            )

            if not isinstance(timeline, list):
                timeline = []

            whys = record.get(
                "3.0_5_Why_Analysis",
                []
            )

            if not isinstance(whys, list):
                whys = []

            root = normalize_root_cause(record)

            root_statement = root.get(
                "Statement",
                ""
            ).strip()

            # ------------------
            # Validation
            # ------------------

            if not problem:
                removed_missing_problem += 1
                continue

            if len(timeline) == 0:
                removed_missing_timeline += 1
                continue

            if len(whys) == 0:
                removed_missing_why += 1
                continue

            if not root_statement:
                removed_missing_root += 1
                continue

            # ------------------
            # Normalization
            # ------------------

            record["Root_Cause_Summary"] = root

            record["5.0_Lessons_Learned"] = normalize_lessons(
                record
            )

            record.pop(
                "5.0_Lessons_Lenared",
                None
            )

            record.pop(
                "2.0_Root_Cause_Summary",
                None
            )

            outfile.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

            kept += 1

        except Exception as e:

            parse_errors += 1

            print(
                f"Record {total} failed: {e}"
            )

print("\n==============================")
print("DATASET CLEANING COMPLETE")
print("==============================\n")

print("Original Records :", total)
print("Clean Records    :", kept)

print("\nRemoved Records")
print("----------------------------")
print("Missing Problem  :", removed_missing_problem)
print("Missing Timeline :", removed_missing_timeline)
print("Missing 5 Why    :", removed_missing_why)
print("Missing Root     :", removed_missing_root)

print("\nParse Errors     :", parse_errors)

print("\nSaved File")
print("----------------------------")
print(OUTPUT_FILE)