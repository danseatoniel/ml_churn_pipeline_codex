"""Column definitions for raw and processed churn data."""

RAW_COLUMNS = [
    "customer_id",
    "signup_date",
    "last_login_date",
    "country",
    "age",
    "plan_type",
    "monthly_spend",
    "num_support_tickets",
    "is_active",
    "churned",
]

FEATURE_COLUMNS = [
    "account_age_days",
    "days_since_last_login",
    "spend_per_ticket",
    "is_premium_plan",
    "support_ticket_bucket",
    "country_group",
]

PROCESSED_COLUMNS = [
    "customer_id",
    "signup_date",
    "last_login_date",
    "country",
    "age",
    "plan_type",
    "monthly_spend",
    "num_support_tickets",
    "is_active",
    "churned",
    *FEATURE_COLUMNS,
]
