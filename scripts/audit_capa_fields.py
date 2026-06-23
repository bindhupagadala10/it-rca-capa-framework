import json
from collections import Counter

INPUT_FILE = "data/processed/clean_dataset.jsonl"

total = 0

empty_capa = 0
empty_lessons = 0

corrective_count = 0
preventive_count = 0

action_type_counter = Counter()

for line in open(INPUT_FILE, encoding="utf-8"):

    total += 1

    record = json.loads(line)

    capa = record.get(
        "4.0_Corrective_and_Preventive_Actions",
        []
    )

    lessons = record.get(
        "5.0_Lessons_Learned",
        []
    )

    if len(capa) == 0:
        empty_capa += 1

    if len(lessons) == 0:
        empty_lessons += 1

    for action in capa:

        if not isinstance(action, dict):
            continue

        action_type = str(
            action.get(
                "Action_Type",
                "MISSING"
            )
        ).strip()

        action_type_counter[action_type] += 1

        if "correct" in action_type.lower():
            corrective_count += 1

        if "prevent" in action_type.lower():
            preventive_count += 1

print("\n===== CAPA AUDIT =====\n")

print("Records:", total)

print("\nEmpty Sections")
print("----------------")
print("Empty CAPA:", empty_capa)
print("Empty Lessons:", empty_lessons)

print("\nDetected Counts")
print("----------------")
print("Corrective:", corrective_count)
print("Preventive:", preventive_count)

print("\nAction Types")
print("----------------")

for k, v in action_type_counter.most_common(20):
    print(f"{k}: {v}")