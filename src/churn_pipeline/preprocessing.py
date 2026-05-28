"""Cleaning and type normalization for churn customers."""

from __future__ import annotations

import pandas as pd

from churn_pipeline.config import SUPPORTED_PLAN_TYPES
from churn_pipeline.schemas import RAW_COLUMNS
from churn_pipeline.validation import ValidationError, validate_raw_dataframe

TRUE_VALUES = {"true", "t", "yes", "y", "1"}
FALSE_VALUES = {"false", "f", "no", "n", "0"}


def preprocess_customers(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Validate, clean, and type-normalize raw customer records."""

    validate_raw_dataframe(raw_df)
    df = raw_df.loc[:, RAW_COLUMNS].copy()

    df["customer_id"] = _clean_text(df["customer_id"])
    df["country"] = _clean_text(df["country"]).fillna("unknown")
    df.loc[df["country"].eq(""), "country"] = "unknown"
    df["country"] = df["country"].str.upper()

    df["plan_type"] = _clean_text(df["plan_type"]).str.lower()
    df["plan_type"] = df["plan_type"].replace("", pd.NA).fillna("free")
    invalid_plans = ~df["plan_type"].isin(SUPPORTED_PLAN_TYPES)
    if invalid_plans.any():
        values = sorted(df.loc[invalid_plans, "plan_type"].unique().tolist())
        raise ValidationError(f"Unsupported plan_type values after cleanup: {', '.join(values)}")

    df["signup_date"] = _parse_date_column(df["signup_date"], "signup_date", required=True)
    df["last_login_date"] = _parse_date_column(df["last_login_date"], "last_login_date", required=False)
    df["last_login_date"] = df["last_login_date"].fillna(df["signup_date"])

    login_before_signup = df["last_login_date"] < df["signup_date"]
    if login_before_signup.any():
        raise ValidationError("last_login_date cannot be before signup_date")

    df["age"] = _fill_numeric(df["age"], "age", fill_strategy="median").astype("int64")
    df["monthly_spend"] = _fill_numeric(df["monthly_spend"], "monthly_spend", fill_strategy="zero")
    df["num_support_tickets"] = (
        _fill_numeric(df["num_support_tickets"], "num_support_tickets", fill_strategy="zero")
        .round()
        .astype("int64")
    )

    df["is_active"] = _parse_bool_column(df["is_active"], "is_active", required=False).fillna(False)
    df["churned"] = _parse_bool_column(df["churned"], "churned", required=True)

    return df


def _clean_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip()


def _parse_date_column(series: pd.Series, column_name: str, *, required: bool) -> pd.Series:
    missing = series.isna() | series.astype("string").str.strip().eq("")
    if required and missing.any():
        raise ValidationError(f"{column_name} contains missing values")

    parsed = pd.to_datetime(series.mask(missing), errors="coerce", format="mixed")
    invalid = ~missing & parsed.isna()
    if invalid.any():
        rows = [str(index) for index in series.index[invalid].tolist()]
        raise ValidationError(f"{column_name} contains invalid dates at rows: {', '.join(rows)}")

    return parsed.dt.normalize()


def _fill_numeric(series: pd.Series, column_name: str, *, fill_strategy: str) -> pd.Series:
    parsed = pd.to_numeric(series, errors="coerce")
    bad_values = series.notna() & parsed.isna()
    if bad_values.any():
        raise ValidationError(f"{column_name} contains non-numeric values")

    if fill_strategy == "median":
        median = parsed.median()
        fill_value = 0 if pd.isna(median) else median
    elif fill_strategy == "zero":
        fill_value = 0
    else:
        raise ValueError(f"Unsupported fill strategy: {fill_strategy}")

    return parsed.fillna(fill_value)


def _parse_bool_column(series: pd.Series, column_name: str, *, required: bool) -> pd.Series:
    normalized = series.astype("string").str.strip().str.lower()
    missing = series.isna() | normalized.eq("")

    if required and missing.any():
        raise ValidationError(f"{column_name} contains missing values")

    parsed = normalized.map({value: True for value in TRUE_VALUES})
    parsed = parsed.fillna(normalized.map({value: False for value in FALSE_VALUES}))

    invalid = ~missing & parsed.isna()
    if invalid.any():
        values = sorted(normalized[invalid].unique().tolist())
        raise ValidationError(
            f"{column_name} must be a boolean-like value; got: {', '.join(values)}"
        )

    return parsed.astype("boolean")
