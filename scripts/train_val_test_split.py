import json
import random
from pathlib import Path

random.seed(42)

DATASETS = [
    "data/processed/rca_train.jsonl",
    "data/processed/capa_train.jsonl"
]

for dataset in DATASETS:

    with open(dataset, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    random.shuffle(data)

    n = len(data)

    train_end = int(0.8 * n)
    val_end = int(0.9 * n)

    train = data[:train_end]
    val = data[train_end:val_end]
    test = data[val_end:]

    name = Path(dataset).stem

    outdir = Path("data/splits")
    outdir.mkdir(parents=True, exist_ok=True)

    for split_name, split_data in [
        ("train", train),
        ("val", val),
        ("test", test)
    ]:

        output_file = outdir / f"{name}_{split_name}.jsonl"

        with open(output_file, "w", encoding="utf-8") as f:
            for row in split_data:
                f.write(
                    json.dumps(
                        row,
                        ensure_ascii=False
                    ) + "\n"
                )

    print(f"\n{name}")
    print("Train:", len(train))
    print("Val  :", len(val))
    print("Test :", len(test))