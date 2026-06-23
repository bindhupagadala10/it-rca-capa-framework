import json
from collections import Counter

INPUT_FILE = "data/raw/dataset_it.jsonl"

total = 0

missing_problem = 0
missing_impact = 0
missing_investigation = 0
missing_5why = 0
missing_rootcause = 0
missing_capa = 0
missing_lessons = 0

root_categories = Counter()

problem_lengths = []
root_lengths = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        total += 1

        try:
            record = json.loads(line)

            summary = record.get("1.0_Problem_Summary", {})

            problem = summary.get(
                "Problem_Description", ""
            ).strip()

            impact = summary.get(
                "Business_Impact", []
            )

            investigation = record.get(
                "2.0_Incident_Review_Technical_Investigation",
                []
            )

            whys = record.get(
                "3.0_5_Why_Analysis",
                []
            )

            root = record.get(
                "Root_Cause_Summary",
                {}
            )

            capa = record.get(
                "4.0_Corrective_and_Preventive_Actions",
                []
            )

            lessons = record.get(
                "5.0_Lessons_Learned",
                []
            )

            if not problem:
                missing_problem += 1

            if not impact:
                missing_impact += 1

            if not investigation:
                missing_investigation += 1

            if len(whys) < 5:
                missing_5why += 1

            if not root.get("Statement", "").strip():
                missing_rootcause += 1

            if not capa:
                missing_capa += 1

            if not lessons:
                missing_lessons += 1

            category = root.get(
                "Root_Cause_Category",
                "UNKNOWN"
            )

            root_categories[category] += 1

            if problem:
                problem_lengths.append(
                    len(problem.split())
                )

            if root.get("Statement"):
                root_lengths.append(
                    len(
                        root["Statement"].split()
                    )
                )

        except Exception as e:
            print(
                f"Failed record {total}: {e}"
            )

print("\n===== DATASET AUDIT =====\n")

print("Total Records:", total)

print("\nMissing Sections")
print("----------------")
print("Problem:", missing_problem)
print("Business Impact:", missing_impact)
print("Investigation:", missing_investigation)
print("5 Why:", missing_5why)
print("Root Cause:", missing_rootcause)
print("CAPA:", missing_capa)
print("Lessons:", missing_lessons)

print("\nRoot Cause Categories")
print("---------------------")

for k, v in root_categories.most_common():
    print(f"{k}: {v}")

if problem_lengths:
    print("\nProblem Description")
    print("-------------------")
    print("Min Words:", min(problem_lengths))
    print("Avg Words:", round(sum(problem_lengths)/len(problem_lengths), 2))
    print("Max Words:", max(problem_lengths))

if root_lengths:
    print("\nRoot Cause Statement")
    print("--------------------")
    print("Min Words:", min(root_lengths))
    print("Avg Words:", round(sum(root_lengths)/len(root_lengths), 2))
    print("Max Words:", max(root_lengths))