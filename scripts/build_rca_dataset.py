import json

INPUT_FILE = "data/processed/clean_dataset.jsonl"
OUTPUT_FILE = "data/processed/rca_train.jsonl"

created = 0
skipped = 0


def business_impact_text(summary):
    impact = summary.get("Business_Impact", [])

    if isinstance(impact, list):
        return "\n".join(str(x) for x in impact)

    return str(impact)


def timeline_text(investigation):

    lines = []

    for item in investigation:

        if not isinstance(item, dict):
            continue

        ts = item.get("Timestamp", "")
        activity = item.get("Activity", "")

        if activity:
            lines.append(
                f"{ts} - {activity}".strip(" -")
            )

    return "\n".join(lines)


def why_text(whys):

    output = []

    for idx, item in enumerate(whys, start=1):

        if not isinstance(item, dict):
            continue

        q = item.get("Question", "")
        a = item.get("Answer", "")

        output.append(
            f"Why {idx}: {q}\nAnswer: {a}"
        )

    return "\n\n".join(output)


with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

    for line in infile:

        try:

            record = json.loads(line)

            summary = record.get(
                "1.0_Problem_Summary",
                {}
            )

            problem = summary.get(
                "Problem_Description",
                ""
            ).strip()

            impact = business_impact_text(summary)

            timeline = timeline_text(
                record.get(
                    "2.0_Incident_Review_Technical_Investigation",
                    []
                )
            )

            whys = why_text(
                record.get(
                    "3.0_5_Why_Analysis",
                    []
                )
            )

            root = record.get(
                "Root_Cause_Summary",
                {}
            ).get(
                "Statement",
                ""
            ).strip()

            if (
                not problem
                or not timeline
                or not whys
                or not root
            ):
                skipped += 1
                continue

            sample = {
                "messages": [
                    {
                        "role": "user",
                        "content":
                        f"Problem Description:\n{problem}\n\n"
                        f"Business Impact:\n{impact}\n\n"
                        f"Technical Investigation Timeline:\n{timeline}"
                    },
                    {
                        "role": "assistant",
                        "content":
                        f"5 Why Analysis:\n{whys}\n\n"
                        f"Root Cause Summary:\n{root}"
                    }
                ]
            }

            outfile.write(
                json.dumps(
                    sample,
                    ensure_ascii=False
                ) + "\n"
            )

            created += 1

        except Exception as e:

            skipped += 1
            print("Skipped:", e)

print("\n===== RCA DATASET CREATED =====")
print("Samples Created :", created)
print("Samples Skipped :", skipped)
print("Saved To :", OUTPUT_FILE)