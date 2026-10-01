"""Unit tests for farm CSV preprocessing helpers."""

import pandas as pd

from carbonseco_livestock.preprocessing import parse_date, parse_farm_file, parse_to_float


def test_parse_to_float_valid() -> None:
    assert parse_to_float("12.5") == 12.5


def test_parse_to_float_invalid() -> None:
    assert parse_to_float("abc") is None


def test_parse_date_month_end_2021() -> None:
    assert parse_date(1) == pd.Timestamp("2021-01-31")
    assert parse_date(2) == pd.Timestamp("2021-02-28")


def test_parse_farm_file_seeded_is_deterministic(tmp_path) -> None:
    from carbonseco_livestock.config import get_project_paths

    raw = get_project_paths().raw_farm_csv
    out1 = tmp_path / "a.csv"
    out2 = tmp_path / "b.csv"
    df1 = parse_farm_file(raw, output_path=out1, random_seed=123, write_output=True)
    df2 = parse_farm_file(raw, output_path=out2, random_seed=123, write_output=True)
    pd.testing.assert_frame_equal(df1, df2)
    assert {"energyDensity", "dryMatterIntake"}.issubset(df1.columns)
