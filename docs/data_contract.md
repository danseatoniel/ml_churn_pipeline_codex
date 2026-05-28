# Data Contract

The pipeline expects one row per customer in a CSV file.

## Required Columns

- `customer_id`
- `signup_date`
- `last_login_date`
- `country`
- `age`
- `plan_type`
- `monthly_spend`
- `num_support_tickets`
- `is_active`
- `churned`

## Validation Rules

- `customer_id` must be present, non-blank, and unique.
- `age` must be numeric and between 0 and 120 when provided.
- `monthly_spend` must be numeric and non-negative when provided.
- `num_support_tickets` must be numeric and non-negative when provided.
- `plan_type` must be one of `free`, `basic`, `pro`, or `enterprise` when provided.
- `signup_date` must parse as a date and is required.
- `last_login_date` must parse as a date when provided.
- `last_login_date` cannot be earlier than `signup_date`.
- `is_active` accepts boolean-like values such as `true`, `false`, `yes`, `no`, `1`, and `0`.
- `churned` accepts the same boolean-like values and is required.

Invalid non-missing values raise `ValidationError` with a clear message. The pipeline avoids silent coercion for values that look malformed.

## Missing Values

The pipeline applies a small set of documented defaults:

- Missing `country` becomes `unknown`.
- Missing `plan_type` becomes `free`.
- Missing `last_login_date` becomes `signup_date`.
- Missing `age` becomes the median age in the file, or `0` if all ages are missing.
- Missing `monthly_spend` becomes `0`.
- Missing `num_support_tickets` becomes `0`.
- Missing `is_active` becomes `False`.

Missing `customer_id`, `signup_date`, or `churned` is rejected.

## Feature Columns

- `account_age_days`: Days from `signup_date` to the pipeline reference date.
- `days_since_last_login`: Days from `last_login_date` to the pipeline reference date.
- `spend_per_ticket`: `monthly_spend / num_support_tickets`, or `0` when ticket count is zero.
- `is_premium_plan`: `True` for `pro` and `enterprise`.
- `support_ticket_bucket`: `none`, `low`, `medium`, or `high`.
- `country_group`: Coarse geographic grouping used by downstream modeling.

If no reference date is provided, the newest `last_login_date` in the input is used. This keeps local runs deterministic for a fixed input file.
