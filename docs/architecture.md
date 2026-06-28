# IT RCA-CAPA Framework Architecture

## Objective

Build an enterprise-grade AI framework capable of automatically generating ServiceNow-style Root Cause Analysis (RCA) and Corrective and Preventive Action (CAPA) reports from incident investigation data.

The framework is designed as a multi-stage pipeline so that organizations can later retrain on large internal datasets (100k+ records) while preserving explainability and auditability.

---

# System Architecture

Incident Data
│
├── Problem Description
├── Business Impact
└── Technical Investigation Timeline
│
▼

RCA Engine
(Qwen2.5-3B-Instruct)

Input:

* Problem Description
* Business Impact
* Investigation Timeline

Output:

* 5 Why Analysis
* Root Cause Summary

│
▼

CAPA Engine
(Mistral-7B-Instruct)

Input:

* 5 Why Analysis
* Root Cause Summary

Output:

* Corrective Actions
* Preventive Actions
* Lessons Learned

│
▼

Report Generator

Input:

* RCA Output
* CAPA Output

Output:

* Enterprise RCA Report
* PDF Document

---

# Design Rationale

## Why Two Models?

Root Cause Analysis and CAPA generation represent different reasoning tasks.

### RCA Task

Goal:

Determine why the incident occurred.

Required reasoning:

* Timeline analysis
* Failure chain reconstruction
* Causal reasoning
* Root cause identification

Output:

* 5 Why Analysis
* Root Cause Summary

---

### CAPA Task

Goal:

Determine how to fix the issue and prevent recurrence.

Required reasoning:

* Remediation planning
* Control improvement
* Risk mitigation
* Process improvement

Output:

* Corrective Actions
* Preventive Actions
* Lessons Learned

Separating these tasks allows each model to specialize and simplifies future retraining.

---

# Model Selection

## RCA Engine

Model:

Qwen2.5-3B-Instruct

Reasons:

* Strong reasoning capability
* Excellent structured output generation
* Efficient QLoRA fine-tuning
* Suitable for timeline-based analysis

Training Dataset:

1455 RCA records

---

## CAPA Engine

Model:

Mistral-7B-Instruct

Reasons:

* Strong instruction-following behavior
* High-quality enterprise text generation
* Effective remediation recommendation generation

Training Dataset:

1454 CAPA records

---

# Training Pipeline

Raw Dataset
(1464 records)

↓

Data Cleaning

↓

Schema Normalization

↓

1455 Clean Records

↓

RCA Dataset Generation

↓

CAPA Dataset Generation

↓

Train / Validation / Test Split

↓

QLoRA Fine-Tuning

---

# Dataset Construction

## RCA Dataset

Input

* Problem Description
* Business Impact
* Technical Investigation Timeline

Output

* 5 Why Analysis
* Root Cause Summary

Records:

1455

---

## CAPA Dataset

Input

* 5 Why Analysis
* Root Cause Summary

Output

* Corrective Actions
* Preventive Actions
* Lessons Learned

Records:

1454

---

# Future Enhancements

## Phase 2

Model Training

* Qwen RCA Fine-Tuning
* Mistral CAPA Fine-Tuning

---

## Phase 3

Enterprise Report Generation

* HTML Templates
* PDF Generation
* Editable Report Workflow

---

## Phase 4

RAG Integration

External Knowledge Sources:

* SOP Documents
* Knowledge Articles
* ServiceNow Knowledge Base
* Historical RCA Reports

Retrieved context will be injected into the RCA engine before inference.

---

# Enterprise Vision

The framework is intended to serve as a reusable architecture that can later be trained on large-scale enterprise incident datasets.

Target Future Dataset Size:

100,000+ RCA Reports

Target Outcome:

Automated generation of enterprise-grade RCA and CAPA documentation with human review and approval workflows.

Streamlit UI
│
├── Input Validator
│
├── RCA Inference Wrapper
│      │
│      └── Qwen Adapter
│
├── RCA Validator
│
├── CAPA Inference Wrapper
│      │
│      └── Mistral Adapter
│
├── CAPA Validator
│
└── DOCX Generator

Models are lazily loaded.
Models are unloaded immediately after inference.
Only one model occupies GPU memory at a time.