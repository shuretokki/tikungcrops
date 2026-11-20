# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Checks for the comparison of satellite season areas with reference statistics."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import polars as pl
import pytest

from jotosanur_agri.pipeline.load_sentinel import month_range
from jotosanur_agri.pipeline.validate_reference import compare, covered_years, summarize


def units(rows: list[tuple[str, int, float, float]]) -> pl.DataFrame:
    return pl.DataFrame(rows, schema=["unit", "year", "rice_area_ha", "area_ha"], orient="row")


def reference(rows: list[tuple[str, int, str, float]]) -> pl.DataFrame:
    return pl.DataFrame(rows, schema=["unit", "year", "crop", "harvested_area_ha"], orient="row")


def pairs(sat: list[float], ref: list[float]) -> pl.DataFrame:
    n = len(sat)
    return pl.DataFrame(
        {
            "unit": [f"U{i}" for i in range(n)],
            "year": [2021] * n,
            "measure": ["rice"] * n,
            "reference_ha": ref,
            "satellite_ha": sat,
        }
    )


def test_compare_counts_only_rice_names_in_the_rice_measure() -> None:
    out = compare(
        units([("A", 2021, 80.0, 150.0)]),
        reference([("A", 2021, "padi", 100.0), ("A", 2021, "jagung", 40.0)]),
    )
    got = {r["measure"]: (r["reference_ha"], r["satellite_ha"]) for r in out.to_dicts()}
    assert got == {"rice": (100.0, 80.0), "all_crops": (140.0, 150.0)}


def test_compare_sums_the_seasons_of_a_year() -> None:
    out = compare(
        units([("A", 2021, 50.0, 60.0), ("A", 2021, 30.0, 40.0)]),
        reference([("A", 2021, "rice", 100.0)]),
    )
    rice = out.filter(pl.col("measure") == "rice").row(0, named=True)
    assert rice["satellite_ha"] == 80.0


def test_compare_treats_a_unit_without_satellite_rows_as_zero_hectares() -> None:
    out = compare(
        units([("A", 2021, 10.0, 10.0)]),
        reference([("A", 2021, "padi", 10.0), ("B", 2021, "padi", 20.0)]),
    )
    b = out.filter((pl.col("unit") == "B") & (pl.col("measure") == "rice")).row(0, named=True)
    assert b["satellite_ha"] == 0.0


def test_summarize_a_perfect_match() -> None:
    row = summarize(pairs([10, 20, 30], [10, 20, 30])).row(0, named=True)
    assert row["units"] == 3
    assert row["r"] == pytest.approx(1.0)
    assert row["ratio"] == pytest.approx(1.0)
    assert row["median_abs_diff_pct"] == pytest.approx(0.0)


def test_summarize_reports_the_ratio_of_totals_and_the_median_difference() -> None:
    row = summarize(pairs([5, 10, 15], [10, 20, 30])).row(0, named=True)
    assert row["ratio"] == pytest.approx(0.5)
    assert row["median_abs_diff_pct"] == pytest.approx(50.0)


def test_summarize_gives_no_correlation_below_three_units() -> None:
    row = summarize(pairs([10, 20], [10, 20])).row(0, named=True)
    assert row["r"] is None
    assert row["ratio"] == pytest.approx(1.0)


def test_summarize_gives_no_correlation_when_one_side_is_constant() -> None:
    row = summarize(pairs([10, 10, 10], [10, 20, 30])).row(0, named=True)
    assert row["r"] is None


def test_summarize_leaves_out_units_without_reference_area() -> None:
    row = summarize(pairs([10, 20, 30, 99], [10, 20, 30, 0])).row(0, named=True)
    assert row["units"] == 3


def test_summarize_has_no_ratio_when_the_reference_is_empty() -> None:
    row = summarize(pairs([1, 2, 3], [0, 0, 0])).row(0, named=True)
    assert row["units"] == 0
    assert row["ratio"] is None
    assert row["median_abs_diff_pct"] is None


def silver(tmp_path: Path, months: list[str], blank: list[str] | None = None) -> Path:
    """A silver file with one reading per month, and no readings in the `blank` months."""
    blank = blank or []
    rows = [
        {"date": date(int(m[:4]), int(m[5:]), 15), "ndvi": None if m in blank else 0.5, "vh_db": None} for m in months
    ]
    path = tmp_path / "silver.parquet"
    pl.DataFrame(rows, schema={"date": pl.Date, "ndvi": pl.Float64, "vh_db": pl.Float64}).write_parquet(path)
    return path


def test_a_year_is_covered_from_september_before_to_april_after(tmp_path: Path) -> None:
    path = silver(tmp_path, month_range("2019-09", "2021-04"))
    assert covered_years(path, [2020, 2021]) == {2020}


def test_a_month_without_readings_uncovers_the_year(tmp_path: Path) -> None:
    months = month_range("2019-09", "2021-04")
    path = silver(tmp_path, months, blank=["2020-06"])
    assert covered_years(path, [2020]) == set()
