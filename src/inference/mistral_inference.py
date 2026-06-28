import gc
import torch
from unsloth import FastLanguageModel

MODEL_NAME = "unsloth/mistral-7b-instruct-v0.3-bnb-4bit"

ADAPTER_PATH = "/content/it-rca-capa-framework/IT_RCA_CAPA/mistral_capa_adapter/emergency_mistral_epoch1"

model = None
tokenizer = None


def load_mistral():

    global model, tokenizer

    if model is not None:
        return

    print("Loading Mistral...")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=4096,
        load_in_4bit=True,
    )

    model.load_adapter(ADAPTER_PATH)

    FastLanguageModel.for_inference(model)

    print("Mistral Loaded")


def unload_mistral():

    global model, tokenizer

    if model is None:
        return

    print("Unloading Mistral...")

    del model
    del tokenizer

    model = None
    tokenizer = None

    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

    print("Mistral Unloaded")


def generate_capa(prompt):

    load_mistral()

    messages = [
        {
            "role": "user",
            "content": prompt,
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

    with torch.inference_mode():

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

    unload_mistral()

    return response