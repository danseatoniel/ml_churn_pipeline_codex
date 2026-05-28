"""Orchestration for the churn feature pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from churn_pipeline.config import PipelineConfig
from churn_pipeline.features import build_features
from churn_pipeline.io import load_raw_csv, write_feature_csv
from churn_pipeline.preprocessing import preprocess_customers


def run_pipeline(
    input_path: str | Path,
    output_path: str | Path,
    config: PipelineConfig | None = None,
) -> pd.DataFrame:
    """Run the full local CSV-to-feature-CSV workflow."""

    pipeline_config = config or PipelineConfig()
    raw_df = load_raw_csv(input_path)
    customers = preprocess_customers(raw_df)
    features = build_features(customers, reference_date=pipeline_config.reference_date)
    write_feature_csv(features, output_path)
    return features
