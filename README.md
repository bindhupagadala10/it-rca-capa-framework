# IT RCA-CAPA Framework

## Overview

IT RCA-CAPA Framework is an enterprise AI system designed to automate ServiceNow-style Root Cause Analysis (RCA) and Corrective and Preventive Action (CAPA) report generation from incident investigation data.

The project uses a multi-stage architecture:

1. RCA Engine (Qwen 2.5 3B)

   * Generates:

     * 5 Why Analysis
     * Root Cause Summary

2. CAPA Engine (Mistral 7B)

   * Generates:

     * Corrective Actions
     * Preventive Actions
     * Lessons Learned

3. Report Generator

   * Converts structured outputs into standardized enterprise RCA documents and PDFs.

---

## Architecture

User Input

* Problem Description
* Business Impact
* Technical Investigation Timeline

↓

Qwen 2.5 3B

↓

* 5 Why Analysis
* Root Cause Summary

↓

Mistral 7B

↓

* Corrective Actions
* Preventive Actions
* Lessons Learned

↓

PDF Generator

↓

Enterprise RCA Report

---

## Dataset

### Original Dataset

* 1464 synthetic enterprise RCA records

### Cleaned Dataset

* 1455 valid RCA records

### Dataset Domains

* Kubernetes Failures
* IAM Authentication Issues
* Database Incidents
* Middleware Failures
* API Gateway Failures
* Network Outages
* DNS Failures
* Storage Failures
* Cloud Infrastructure Incidents
* Queue Backlogs
* Message Broker Failures
* Deployment Failures

---

## Training Datasets

### RCA Dataset

Input

* Problem Description
* Business Impact
* Technical Investigation Timeline

Output

* 5 Why Analysis
* Root Cause Summary

Samples: 1455

---

### CAPA Dataset

Input

* 5 Why Analysis
* Root Cause Summary

Output

* Corrective Actions
* Preventive Actions
* Lessons Learned

Samples: 1454

---

## Training Approach

* QLoRA
* 4-bit Quantization
* Unsloth
* Google Colab

---

## Repository Structure

data/
├── raw/
├── processed/
└── splits/

scripts/
├── audit_dataset.py
├── clean_dataset.py
├── build_rca_dataset.py
├── build_capa_dataset.py
├── dataset_stats.py
└── train_val_test_split.py

training/

results/

docs/

---

## Current Status

Phase 1: Dataset Engineering
Status: Complete

Phase 2: RCA Model Training
Status: In Progress

Phase 3: CAPA Model Training
Status: Planned

Phase 4: PDF Report Generation
Status: Planned

Phase 5: RAG Integration with Enterprise SOPs
Status: Planned
