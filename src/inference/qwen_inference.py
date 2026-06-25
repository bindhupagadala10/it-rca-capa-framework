from unsloth import FastLanguageModel

MODEL_NAME = "unsloth/Qwen2.5-3B-Instruct-bnb-4bit"
ADAPTER_PATH = "qwen_rca_adapter"

model = None
tokenizer = None


def load_model():

    global model
    global tokenizer

    if model is not None:
        return model, tokenizer

    print("Loading Qwen model...")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=4096,
        load_in_4bit=True,
    )

    model.load_adapter(ADAPTER_PATH)

    FastLanguageModel.for_inference(model)

    print("Qwen loaded.")

    return model, tokenizer


def generate_rca(user_prompt):

    model, tokenizer = load_model()

    messages = [
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        text,
        return_tensors="pt",
    ).to("cuda")

    outputs = model.generate(
        **inputs,
        max_new_tokens=1200,
        temperature=0.1,
        do_sample=False,
    )

    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )

    return response