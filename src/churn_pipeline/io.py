"""Local file IO helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_raw_csv(path: str | Path) -> pd.DataFrame:
    """Load a raw customer CSV from a local path."""

    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV does not exist: {csv_path}")

    return pd.read_csv(csv_path, keep_default_na=True)


def write_feature_csv(df: pd.DataFrame, path: str | Path) -> None:
    """Write processed features to a local CSV path, creating parents."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
