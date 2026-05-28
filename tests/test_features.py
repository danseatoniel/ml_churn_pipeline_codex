from __future__ import annotations

from churn_pipeline.features import build_features
from churn_pipeline.io import load_raw_csv
from churn_pipeline.preprocessing import preprocess_customers
from churn_pipeline.schemas import FEATURE_COLUMNS


def test_feature_columns_are_created_with_expected_values(valid_csv):
    customers = preprocess_customers(load_raw_csv(valid_csv))

    features = build_features(customers, reference_date="2024-04-01")

    for column in FEATURE_COLUMNS:
        assert column in features.columns

    row = features.set_index("customer_id").loc["c001"]
    assert row["account_age_days"] == 91
    assert row["days_since_last_login"] == 12
    assert row["spend_per_ticket"] == 33.33
    assert bool(row["is_premium_plan"]) is True
    assert row["support_ticket_bucket"] == "medium"
    assert row["country_group"] == "north_america"


def test_spend_per_ticket_handles_zero_support_tickets_safely(valid_csv):
    customers = preprocess_customers(load_raw_csv(valid_csv))

    features = build_features(customers, reference_date="2024-04-01")

    row = features.set_index("customer_id").loc["c002"]
    assert row["num_support_tickets"] == 0
    assert row["spend_per_ticket"] == 0


def test_account_age_and_login_recency_are_calculated_correctly(valid_csv):
    customers = preprocess_customers(load_raw_csv(valid_csv))

    features = build_features(customers, reference_date="2024-04-01")

    row = features.set_index("customer_id").loc["c003"]
    assert row["account_age_days"] == 51
    assert row["days_since_last_login"] == 41


def test_country_group_defaults_to_other_for_unmapped_countries(valid_csv):
    customers = preprocess_customers(load_raw_csv(valid_csv))

    features = build_features(customers, reference_date="2024-04-01")

    assert features.set_index("customer_id").loc["c004", "country_group"] == "other"
