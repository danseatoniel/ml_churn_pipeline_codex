from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_csv(fixtures_dir: Path) -> Path:
    return fixtures_dir / "raw_customers_valid.csv"


@pytest.fixture
def synthetic_10_row_csv(fixtures_dir: Path) -> Path:
    return fixtures_dir / "raw_customers_synthetic_10.csv"
