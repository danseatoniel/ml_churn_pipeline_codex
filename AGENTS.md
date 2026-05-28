# AGENTS.md

## Purpose

This repo is a compact, local-first Python  machine learning data pipeline for customer churn feature engineering. It ingests raw customer CSV data, validates the data contract, normalizes types and missing values, creates model-ready tabular features, and writes a processed CSV.

The project is intentionally small and modular so changes can be diagnosed quickly.

## Core Flow

1. `churn_pipeline.io.load_raw_csv` reads a local CSV into pandas.
2. `churn_pipeline.validation.validate_raw_dataframe` checks required columns, duplicate IDs, numeric ranges, and categorical values.
3. `churn_pipeline.preprocessing.preprocess_customers` parses dates and booleans, normalizes text, and applies documented missing-value defaults.
4. `churn_pipeline.features.build_features` creates feature columns such as account age, login recency, spend per ticket, plan tier, ticket bucket, and country group.
5. `churn_pipeline.pipeline.run_pipeline` orchestrates the full input-to-output workflow.
6. `churn_pipeline.cli` exposes the `churn-pipeline run` command.

## Key Files

- `src/churn_pipeline/io.py`: local CSV input/output.
- `src/churn_pipeline/validation.py`: explicit data contract validation and `ValidationError`.
- `src/churn_pipeline/preprocessing.py`: type parsing, text cleanup, and missing-value handling.
- `src/churn_pipeline/features.py`: deterministic feature engineering.
- `src/churn_pipeline/pipeline.py`: orchestration.
- `src/churn_pipeline/cli.py`: command-line interface.
- `src/churn_pipeline/schemas.py`: raw and processed column lists.
- `src/churn_pipeline/config.py`: allowed plans, country groups, and runtime config.
- `tests/fixtures/`: small CSV fixtures.
- `docs/data_contract.md`: expected input schema and transformation rules.
- `docs/aws_future_deployment.md`: future deployment notes.

## Running

Use non-editable installs in this workspace:

```bash
uv sync --no-editable
uv run --no-editable pytest
uv run --no-editable churn-pipeline run --input data/sample/raw_customers.csv --output data/processed/features.csv
```

## Notes For Agents

- Prefer fixing behavior in the smallest relevant module.
- Keep validation errors explicit rather than silently coercing malformed data.
- Identifiers should be treated as identifiers, not numeric model features.
- Date-derived features should stay deterministic; pass `reference_date` in tests.
- Do not add external services or AWS code. The repo is local-first.
