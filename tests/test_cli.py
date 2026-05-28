from __future__ import annotations

from churn_pipeline.cli import main


def test_cli_returns_success_for_valid_input(valid_csv, tmp_path, capsys):
    output_path = tmp_path / "features.csv"

    exit_code = main(
        [
            "run",
            "--input",
            str(valid_csv),
            "--output",
            str(output_path),
            "--reference-date",
            "2024-04-01",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert output_path.exists()
    assert "Wrote 4 rows" in captured.out


def test_cli_returns_non_zero_status_for_invalid_input(fixtures_dir, tmp_path, capsys):
    output_path = tmp_path / "features.csv"

    exit_code = main(
        [
            "run",
            "--input",
            str(fixtures_dir / "raw_customers_missing_columns.csv"),
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert not output_path.exists()
    assert "Missing required columns" in captured.err
