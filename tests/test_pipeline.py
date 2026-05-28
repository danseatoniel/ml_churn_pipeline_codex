from __future__ import annotations

import pandas as pd

from churn_pipeline.config import PipelineConfig
from churn_pipeline.pipeline import run_pipeline
from churn_pipeline.schemas import PROCESSED_COLUMNS


def test_full_pipeline_writes_output_file_with_expected_columns(valid_csv, tmp_path):
    output_path = tmp_path / "features.csv"

    features = run_pipeline(
        valid_csv,
        output_path,
        PipelineConfig(reference_date="2024-04-01"),
    )

    assert output_path.exists()
    assert features.columns.tolist() == PROCESSED_COLUMNS

    written = pd.read_csv(output_path)
    assert written.columns.tolist() == PROCESSED_COLUMNS
    assert len(written) == 4
    assert written.loc[0, "account_age_days"] == 91


def test_full_pipeline_runs_with_synthetic_10_row_csv(synthetic_10_row_csv, tmp_path):
    output_path = tmp_path / "synthetic_features.csv"

    features = run_pipeline(
        synthetic_10_row_csv,
        output_path,
        PipelineConfig(reference_date="2024-04-01"),
    )

    assert output_path.exists()
    assert features.columns.tolist() == PROCESSED_COLUMNS
    assert len(features) == 10
    assert features["customer_id"].is_unique
    assert features.loc[features["customer_id"].eq("c1006"), "monthly_spend"].item() == 0
    assert features.loc[features["customer_id"].eq("c1006"), "last_login_date"].item() == pd.Timestamp(
        "2023-08-01"
    )
