import json

INPUT_FILE = "data/processed/clean_dataset.jsonl"
OUTPUT_FILE = "data/processed/capa_train.jsonl"

created = 0
skipped = 0


def business_impact_text(summary):

    impact = summary.get(
        "Business_Impact",
        []
    )

    if isinstance(impact, list):
        return "\n".join(
            str(x)
            for x in impact
        )

    return str(impact)


def timeline_text(investigation):

    lines = []

    for item in investigation:

        if not isinstance(item, dict):
            continue

        ts = item.get(
            "Timestamp",
            ""
        )

        activity = item.get(
            "Activity",
            ""
        )

        if activity:
            lines.append(
                f"{ts} - {activity}".strip(" -")
            )

    return "\n".join(lines)


def why_text(whys):

    output = []

    for idx, item in enumerate(
        whys,
        start=1
    ):

        if not isinstance(item, dict):
            continue

        q = item.get(
            "Question",
            ""
        )

        a = item.get(
            "Answer",
            ""
        )

        output.append(
            f"Why {idx}: {q}\nAnswer: {a}"
        )

    return "\n\n".join(output)


def extract_actions(actions):

    corrective = []
    preventive = []

    for item in actions:

        if not isinstance(item, dict):
            continue

        action_type = str(
            item.get(
                "Action_Type",
                ""
            )
        ).strip().upper()

        description = (
            item.get(
                "Action_Description"
            )
            or item.get(
                "Description"
            )
            or item.get(
                "Action"
            )
            or ""
        )

        if not description:
            continue

        if action_type == "CA":
            corrective.append(
                description
            )

        elif action_type == "PA":
            preventive.append(
                description
            )

    return corrective, preventive


def extract_lessons(lessons):

    output = []

    for item in lessons:

        if isinstance(item, dict):

            text = (
                item.get(
                    "Lesson"
                )
                or item.get(
                    "Description"
                )
                or item.get(
                    "Observation"
                )
                or ""
            )

            if text:
                output.append(
                    text
                )

        elif isinstance(item, str):

            output.append(
                item
            )

    return output


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

            impact = business_impact_text(
                summary
            )

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

            corrective, preventive = extract_actions(
                record.get(
                    "4.0_Corrective_and_Preventive_Actions",
                    []
                )
            )

            lessons = extract_lessons(
                record.get(
                    "5.0_Lessons_Learned",
                    []
                )
            )

            if (
                not root
                or (
                    len(corrective) == 0
                    and len(preventive) == 0
                )
            ):
                skipped += 1
                continue

            assistant_output = ""

            assistant_output += (
                "Corrective Actions:\n"
            )

            assistant_output += "\n".join(
                f"- {x}"
                for x in corrective
            )

            assistant_output += "\n\n"

            assistant_output += (
                "Preventive Actions:\n"
            )

            assistant_output += "\n".join(
                f"- {x}"
                for x in preventive
            )

            assistant_output += "\n\n"

            assistant_output += (
                "Lessons Learned:\n"
            )

            assistant_output += "\n".join(
                f"- {x}"
                for x in lessons
            )

            sample = {
                "messages": [
                    {
                        "role": "user",
                        "content":
                        f"Problem Description:\n{problem}\n\n"
                        f"Business Impact:\n{impact}\n\n"
                        f"Technical Investigation Timeline:\n{timeline}\n\n"
                        f"5 Why Analysis:\n{whys}\n\n"
                        f"Root Cause Summary:\n{root}"
                    },
                    {
                        "role": "assistant",
                        "content":
                        assistant_output
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

print("\n===== CAPA DATASET CREATED =====")
print("Samples Created :", created)
print("Samples Skipped :", skipped)
print("Saved To :", OUTPUT_FILE)