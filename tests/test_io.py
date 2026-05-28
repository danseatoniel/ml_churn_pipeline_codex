from __future__ import annotations

import pandas as pd

from churn_pipeline.io import load_raw_csv, write_feature_csv


def test_valid_csv_input_loads_successfully(valid_csv):
    df = load_raw_csv(valid_csv)

    assert len(df) == 4
    assert "customer_id" in df.columns
    assert df.loc[0, "customer_id"] == "c001"


def test_loads_single_customer_record(fixtures_dir):
    df = load_raw_csv(fixtures_dir / "test_1.csv")

    assert df.to_dict("records") == [
        {
            "customer_id": "c_na_001",
            "signup_date": "2024-01-01",
            "last_login_date": "2024-03-15",
            "country": "NA",
            "age": 39,
            "plan_type": "basic",
            "monthly_spend": 29.99,
            "num_support_tickets": 1,
            "is_active": True,
            "churned": False,
        }
    ]


def test_loads_customer_identifier_values(fixtures_dir):
    df = load_raw_csv(fixtures_dir / "test_2.csv")

    assert df["customer_id"].tolist() == ["00123", "00124"]


def test_write_feature_csv_creates_parent_directory(tmp_path):
    output_path = tmp_path / "nested" / "features.csv"
    df = pd.DataFrame({"customer_id": ["c001"], "account_age_days": [10]})

    write_feature_csv(df, output_path)

    assert output_path.exists()
    written = pd.read_csv(output_path)
    assert written.to_dict("records") == [{"customer_id": "c001", "account_age_days": 10}]
