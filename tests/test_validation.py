from __future__ import annotations

import pandas as pd
import pytest

from churn_pipeline.io import load_raw_csv
from churn_pipeline.validation import ValidationError, validate_raw_dataframe


def test_missing_required_columns_raise_clear_validation_error(fixtures_dir):
    df = load_raw_csv(fixtures_dir / "raw_customers_missing_columns.csv")

    with pytest.raises(ValidationError, match="Missing required columns: plan_type"):
        validate_raw_dataframe(df)


def test_duplicate_customer_ids_are_rejected(valid_csv):
    df = load_raw_csv(valid_csv)
    df.loc[1, "customer_id"] = "c001"

    with pytest.raises(ValidationError, match="Duplicate customer_id values: c001"):
        validate_raw_dataframe(df)


@pytest.mark.parametrize(
    ("column", "bad_value", "message"),
    [
        ("age", -1, "age must be between 0 and 120"),
        ("age", 121, "age must be between 0 and 120"),
        ("monthly_spend", -0.01, "monthly_spend must be non-negative"),
        ("num_support_tickets", -1, "num_support_tickets must be non-negative"),
    ],
)
def test_invalid_numeric_ranges_are_rejected(valid_csv, column, bad_value, message):
    df = load_raw_csv(valid_csv)
    df.loc[0, column] = bad_value

    with pytest.raises(ValidationError, match=message):
        validate_raw_dataframe(df)


def test_rejects_invalid_ticket_count_values(valid_csv):
    df = load_raw_csv(valid_csv.parent / "test_3.csv")

    with pytest.raises(ValidationError, match="num_support_tickets must be a whole number"):
        validate_raw_dataframe(df)


def test_invalid_plan_type_is_rejected(valid_csv):
    df = load_raw_csv(valid_csv)
    df.loc[0, "plan_type"] = "vip"

    with pytest.raises(ValidationError, match="plan_type must be one of"):
        validate_raw_dataframe(df)


def test_fixture_with_invalid_values_is_rejected(fixtures_dir):
    df = load_raw_csv(fixtures_dir / "raw_customers_invalid_values.csv")

    with pytest.raises(ValidationError):
        validate_raw_dataframe(df)


def test_blank_customer_id_is_rejected():
    df = pd.DataFrame(
        {
            "customer_id": [""],
            "signup_date": ["2024-01-01"],
            "last_login_date": ["2024-01-02"],
            "country": ["US"],
            "age": [34],
            "plan_type": ["basic"],
            "monthly_spend": [10],
            "num_support_tickets": [0],
            "is_active": ["true"],
            "churned": ["false"],
        }
    )

    with pytest.raises(ValidationError, match="customer_id contains missing or blank values"):
        validate_raw_dataframe(df)
