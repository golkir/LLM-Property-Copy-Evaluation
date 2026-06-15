# LLM-based Property Listing Generation + Evaluation Pipeline

This project builds a **property listing content generation system** that converts structured property rental data into grounded and structured marketing copy. The quality of the generated content is evaluated using custom metrics with `inspect-ai` and LLM-as-a-Judge models.

---

## Key components

We implement:

- **Property data modelling**  
  Based on the raw JSON property data, we construct verifiable Pydantic models that enforce typing and provide data normalization, such as stripping HTML tags.

- **Generation pipeline**  
  We use a foundational LLM model to create marketing copy based on property data and enforce structured generated output, including hero heading, description, amenity highlights, and house policies.

- **Evaluation framework**  
  Built on `inspect-ai` to measure groundedness and structure compliance.

- **Testable architecture**  
  Using Pytest.

- **Notebook-driven workflow** (`evals.ipynb`)  
  For evaluation pipeline execution and results analysis.

---

## Evaluation System

We use `inspect-ai` to run evaluations and store logs for reproducibility. We provide generated evaluation logs in the `.logs` directory (see how to read them below).

---

## Metrics

### 1. Groundedness (Chain-of-Thought Scorer)

- Metric: `groundedness_scorer_cot`
- Evaluates whether each claim in generated text is supported by raw property data
- Produces:
  - Per-claim audit
  - Final normalized score (0–1) based on the supported/unsupported claims ratio
  - Failure breakdown (wrong claims vs total claims)

---

### 2. Structured Output Compliance

- Metric: `structure_scorer`
- Validates that output:
  - Conforms to `MarketingCopy` schema
  - Contains exactly 3 amenity highlights
  - Produces valid JSON structure

---

## How to Run

### 1. Setup environment

We use **Python 3.13** and `uv`.

```bash
uv sync
uv pip install -e .
```

## Interactive execution

The main entry point is:

`evals.ipynb`

This notebook:

- Runs the full generation pipeline  
- Executes `inspect-ai` evaluation tasks  
- Stores logs  
- Performs metric aggregation and visualization  

---

## Reading Existing Logs (inspect-ai)

You can fully reproduce analysis without rerunning the pipeline by loading stored logs.

Inside `evals.ipynb`:

```python
from inspect_ai.log import read_eval_log

log = read_eval_log("path/to/log.json")