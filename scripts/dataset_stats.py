import json

FILES = [
    "data/processed/rca_train.jsonl",
    "data/processed/capa_train.jsonl"
]

for file in FILES:

    samples = 0

    input_words = []
    output_words = []

    with open(file, "r", encoding="utf-8") as f:

        for line in f:

            row = json.loads(line)

            messages = row["messages"]

            user_text = messages[0]["content"]
            assistant_text = messages[1]["content"]

            input_words.append(
                len(user_text.split())
            )

            output_words.append(
                len(assistant_text.split())
            )

            samples += 1

    print("\n========================")
    print(file)
    print("========================")

    print("Samples:", samples)

    print("\nINPUT")
    print("Min:", min(input_words))
    print("Avg:", round(sum(input_words)/len(input_words), 2))
    print("Max:", max(input_words))

    print("\nOUTPUT")
    print("Min:", min(output_words))
    print("Avg:", round(sum(output_words)/len(output_words), 2))
    print("Max:", max(output_words))