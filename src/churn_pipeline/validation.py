"""Validation for raw churn customer data."""

from __future__ import annotations

import pandas as pd

from churn_pipeline.config import SUPPORTED_PLAN_TYPES
from churn_pipeline.schemas import RAW_COLUMNS


class ValidationError(ValueError):
    """Raised when raw data violates the churn pipeline contract."""


def validate_raw_dataframe(df: pd.DataFrame) -> None:
    """Run all raw-data validation checks before preprocessing."""

    validate_required_columns(df)
    validate_customer_ids(df)
    validate_numeric_ranges(df)
    validate_plan_types(df)


def validate_required_columns(df: pd.DataFrame) -> None:
    missing = [column for column in RAW_COLUMNS if column not in df.columns]
    if missing:
        raise ValidationError(f"Missing required columns: {', '.join(missing)}")


def validate_customer_ids(df: pd.DataFrame) -> None:
    ids = _normalized_text(df["customer_id"])

    if ids.isna().any() or ids.eq("").any():
        raise ValidationError("customer_id contains missing or blank values")

    duplicate_ids = sorted(ids[ids.duplicated()].unique().tolist())
    if duplicate_ids:
        raise ValidationError(f"Duplicate customer_id values: {', '.join(duplicate_ids)}")


def validate_numeric_ranges(df: pd.DataFrame) -> None:
    age = _numeric_series(df["age"], "age")
    monthly_spend = _numeric_series(df["monthly_spend"], "monthly_spend")
    tickets = _numeric_series(df["num_support_tickets"], "num_support_tickets")

    invalid_age = age.notna() & ~age.between(0, 120)
    if invalid_age.any():
        raise ValidationError("age must be between 0 and 120")

    if (monthly_spend.dropna() < 0).any():
        raise ValidationError("monthly_spend must be non-negative")

    if (tickets.dropna() < 0).any():
        raise ValidationError("num_support_tickets must be non-negative")


def validate_plan_types(df: pd.DataFrame) -> None:
    plan_type = _normalized_text(df["plan_type"]).str.lower()
    invalid = plan_type.notna() & plan_type.ne("") & ~plan_type.isin(SUPPORTED_PLAN_TYPES)
    if invalid.any():
        values = sorted(plan_type[invalid].unique().tolist())
        raise ValidationError(
            "plan_type must be one of free, basic, pro, enterprise; "
            f"got: {', '.join(values)}"
        )


def _numeric_series(series: pd.Series, column_name: str) -> pd.Series:
    parsed = pd.to_numeric(series, errors="coerce")
    bad_values = series.notna() & parsed.isna()
    if bad_values.any():
        raise ValidationError(f"{column_name} contains non-numeric values")
    return parsed


def _normalized_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip()
