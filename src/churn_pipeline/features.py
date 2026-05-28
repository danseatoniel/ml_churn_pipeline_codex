"""Feature engineering for normalized churn customers."""

from __future__ import annotations

import pandas as pd

from churn_pipeline.config import COUNTRY_GROUPS, PREMIUM_PLAN_TYPES
from churn_pipeline.schemas import PROCESSED_COLUMNS


def build_features(customers: pd.DataFrame, reference_date: str | pd.Timestamp | None = None) -> pd.DataFrame:
    """Create model-ready features from preprocessed customer records."""

    df = customers.copy()
    snapshot_date = _resolve_reference_date(df, reference_date)

    df["account_age_days"] = (snapshot_date - df["signup_date"]).dt.days.clip(lower=0)
    df["days_since_last_login"] = (snapshot_date - df["last_login_date"]).dt.days.clip(lower=0)
    df["spend_per_ticket"] = _safe_spend_per_ticket(df)
    df["is_premium_plan"] = df["plan_type"].isin(PREMIUM_PLAN_TYPES)
    df["support_ticket_bucket"] = df["num_support_tickets"].map(_ticket_bucket)
    df["country_group"] = df["country"].map(COUNTRY_GROUPS).fillna("other")

    return df.loc[:, PROCESSED_COLUMNS]


def _resolve_reference_date(df: pd.DataFrame, reference_date: str | pd.Timestamp | None) -> pd.Timestamp:
    if reference_date is not None:
        return pd.Timestamp(reference_date).normalize()

    latest_login = df["last_login_date"].max()
    if pd.isna(latest_login):
        return pd.Timestamp.utcnow().tz_localize(None).normalize()

    return pd.Timestamp(latest_login).normalize()


def _safe_spend_per_ticket(df: pd.DataFrame) -> pd.Series:
    has_tickets = df["num_support_tickets"] > 0
    spend_per_ticket = pd.Series(0.0, index=df.index)
    spend_per_ticket.loc[has_tickets] = (
        df.loc[has_tickets, "monthly_spend"] / df.loc[has_tickets, "num_support_tickets"]
    )
    return spend_per_ticket.round(2)


def _ticket_bucket(ticket_count: int) -> str:
    if ticket_count == 0:
        return "none"
    if ticket_count <= 2:
        return "low"
    if ticket_count <= 5:
        return "medium"
    return "high"
