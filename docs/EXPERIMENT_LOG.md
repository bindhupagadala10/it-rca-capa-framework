Experiment 001

Model:
Qwen2.5-3B-Instruct

Method:
QLoRA (Unsloth)

Dataset:
1455 records

Train:
1164

Validation:
145

Test:
146

Epochs:
3

Training Time:
61 minutes

Train Loss:
1.5247

Validation Loss:
1.7055

Evaluation:
ROUGE-1: 0.5331
ROUGE-2: 0.2629
ROUGE-L: 0.2728
BERTScore F1: 0.8417

Status:
Successful baseline RCA model.

Experiment 2

Model:
Mistral-7B-Instruct-v0.3

Method:
QLoRA (4-bit)

Dataset:
1163 Train
145 Validation
146 Test

Training:
1 Epoch Completed
Training interrupted due to TRL checkpoint serialization issue

Validation Loss:
1.3978

Evaluation:
ROUGE-1 : 0.5173
ROUGE-2 : 0.1439
ROUGE-L : 0.2352
BERTScore F1 : 0.8798

Observations:
Model successfully generates structured corrective actions, preventive actions, and lessons learned.
Outputs are semantically aligned with ground truth while often using different wording.

Experiment 1
------------
Model: Qwen2.5-3B-Instruct
Task: RCA Generation
ROUGE-1: 0.5331
ROUGE-2: 0.2629
ROUGE-L: 0.2728
BERTScore F1: 0.8417

Experiment 2
------------
Model: Mistral-7B-Instruct-v0.3
Task: CAPA Generation
ROUGE-1: 0.5173
ROUGE-2: 0.1439
ROUGE-L: 0.2352
BERTScore F1: 0.8798
Validation Loss: 1.3978

### v0.x

Added

- Lazy loading for Qwen and Mistral
- Wrapper inference modules
- CAPA generation pipeline
- Validation workflow
- Streamlit integration

Changed

- Parser updated for RCA
- Parser updated for CAPA

Fixed

- 5 Why rendering
- Streamlit inference pipeline