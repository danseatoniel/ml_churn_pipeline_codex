from __future__ import annotations

import pandas as pd
import pytest

from churn_pipeline.io import load_raw_csv
from churn_pipeline.preprocessing import preprocess_customers
from churn_pipeline.validation import ValidationError


def test_date_fields_are_parsed_correctly(valid_csv):
    processed = preprocess_customers(load_raw_csv(valid_csv))

    assert pd.api.types.is_datetime64_any_dtype(processed["signup_date"])
    assert pd.api.types.is_datetime64_any_dtype(processed["last_login_date"])
    assert processed.loc[0, "signup_date"] == pd.Timestamp("2024-01-01")
    assert processed.loc[3, "last_login_date"] == pd.Timestamp("2024-03-01")


def test_bad_dates_raise_validation_error(fixtures_dir):
    df = load_raw_csv(fixtures_dir / "raw_customers_bad_dates.csv")

    with pytest.raises(ValidationError, match="signup_date contains invalid dates"):
        preprocess_customers(df)


def test_boolean_values_are_parsed_consistently(valid_csv):
    processed = preprocess_customers(load_raw_csv(valid_csv))

    assert processed["is_active"].tolist() == [True, True, True, False]
    assert processed["churned"].tolist() == [False, False, False, True]


def test_invalid_boolean_value_is_rejected(valid_csv):
    df = load_raw_csv(valid_csv)
    df.loc[0, "is_active"] = "sometimes"

    with pytest.raises(ValidationError, match="is_active must be a boolean-like value"):
        preprocess_customers(df)


def test_missing_values_get_documented_defaults(valid_csv):
    processed = preprocess_customers(load_raw_csv(valid_csv))

    assert processed.loc[3, "age"] == 34
    assert processed.loc[3, "monthly_spend"] == 0
    assert processed.loc[3, "last_login_date"] == processed.loc[3, "signup_date"]
