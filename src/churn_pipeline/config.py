"""Shared pipeline configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineConfig:
    """Runtime options for a feature pipeline execution."""

    reference_date: str | None = None


SUPPORTED_PLAN_TYPES = {"free", "basic", "pro", "enterprise"}
PREMIUM_PLAN_TYPES = {"pro", "enterprise"}

COUNTRY_GROUPS = {
    "US": "north_america",
    "CA": "north_america",
    "MX": "north_america",
    "GB": "europe",
    "UK": "europe",
    "DE": "europe",
    "FR": "europe",
    "ES": "europe",
    "IN": "asia_pacific",
    "JP": "asia_pacific",
    "AU": "asia_pacific",
}
