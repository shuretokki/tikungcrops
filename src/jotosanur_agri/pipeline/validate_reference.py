"""Compare satellite season areas of an AOI with its reference statistics.

For every year that has reference data and satellite coverage for all its seasons, each
unit's satellite area is summed over the year's seasons and compared with the reference
harvested area (which also counts each season):
    - rice: rice-season area (`rice_area_ha`) vs reference rice.
    - all crops: all-season area (`area_ha`) vs the sum of every reference crop that
      year (rice only in years whose source lists nothing else).

A year counts as covered when the silver series (what gold was built from) has data in
every month from September of the year before
(wet-season crops planted then peak in the year) to April of the year after (so
September-December crops are not cut off before harvest). Seasons cut by missing months
are left out of the unit summaries, which would understate the year.

Reported per year: units compared, Pearson r across units (None below 3 units or when
either side is constant), the ratio of totals (satellite / reference) and the median
absolute difference per unit in percent.
Without reference data for the AOI the check is skipped, and the pipeline results are then
unvalidated for that area.

Outputs: data/gold/sentinel/<aoi>_validation.csv (per year and measure) and
<aoi>_validation_units.csv (per unit, for charts).
Usage: `python -m jotosanur_agri.pipeline.validate_reference [AOI]`.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI, month_range
from jotosanur_agri.pipeline.reference import ReferenceDataError, read_reference, reference_path

RICE = ["padi", "padi_sawah", "rice"]


def covered_years(silver_path: Path, years: list[int]) -> set[int]:
    """Those of `years` whose seasons fall wholly inside months the silver series has data for."""
    have = set(
        pl.scan_parquet(silver_path)
        .filter(pl.col("ndvi").is_not_null() | pl.col("vh_db").is_not_null())
        .select(pl.col("date").dt.strftime("%Y-%m").unique())
        .collect()
        .to_series()
        .to_list()
    )
    return {y for y in years if set(month_range(f"{y - 1}-09", f"{y + 1}-04")) <= have}


def compare(units: pl.DataFrame, reference: pl.DataFrame) -> pl.DataFrame:
    """Per unit, year and measure: satellite and reference area."""
    satellite = units.group_by("unit", "year").agg(
        pl.col("rice_area_ha").sum().alias("rice"), pl.col("area_ha").sum().alias("all_crops")
    )
    ref = reference.group_by("unit", "year").agg(
        pl.col("harvested_area_ha").filter(pl.col("crop").is_in(RICE)).sum().alias("rice"),
        pl.col("harvested_area_ha").sum().alias("all_crops"),
    )
    return (
        ref.unpivot(index=["unit", "year"], variable_name="measure", value_name="reference_ha")
        .join(
            satellite.unpivot(index=["unit", "year"], variable_name="measure", value_name="satellite_ha"),
            on=["unit", "year", "measure"],
            how="left",
        )
        .with_columns(pl.col("satellite_ha").fill_null(0.0))
        .sort("year", "measure", "unit")
    )


def summarize(pairs: pl.DataFrame) -> pl.DataFrame:
    """Per year and measure: n, r, ratio of totals and median absolute percent difference."""
    rows = []
    for (year, measure), g in pairs.group_by("year", "measure", maintain_order=True):
        sat, ref = g["satellite_ha"].to_numpy(), g["reference_ha"].to_numpy()
        valid = ref > 0
        comparable = valid.sum() > 2 and sat[valid].std() > 0 and ref[valid].std() > 0
        rows.append(
            {
                "year": year,
                "measure": measure,
                "units": int(valid.sum()),
                "r": float(np.corrcoef(sat[valid], ref[valid])[0, 1]) if comparable else None,
                "ratio": float(sat.sum() / ref.sum()) if ref.sum() else None,
                "median_abs_diff_pct": float(np.median(np.abs(sat[valid] / ref[valid] - 1)) * 100)
                if valid.any()
                else None,
            }
        )
    return pl.DataFrame(rows)


def run_validation(aoi_spec: str = DEFAULT_AOI, data_dir: str | Path = "data") -> dict[str, Any]:
    """Compare an AOI's gold unit summaries with its reference statistics.

    Returns:
        The per-year summary rows, reference years left out for lack of satellite data,
        and output paths, or a note when there is nothing to compare.

    Raises:
        ReferenceDataError: If the reference file has problems (all listed).
        FileNotFoundError: If the AOI has reference data but no silver or gold output yet.
    """
    data = Path(data_dir)
    aoi = resolve(aoi_spec)
    slug = aoi.slug
    reference = read_reference(aoi, data)
    if reference is None:
        return {"aoi": slug, "note": f"no reference statistics ({reference_path(aoi, data)}), results are unvalidated"}
    units_path = data / "gold" / "sentinel" / f"{slug}_units.parquet"
    silver_path = data / "silver" / "sentinel" / f"{slug}.parquet"
    if not units_path.exists() or not silver_path.exists():
        raise FileNotFoundError(f"{units_path} or {silver_path} not found, run `just silver` and `just gold` first")

    ref_years = sorted(set(reference["year"].to_list()))
    years = covered_years(silver_path, ref_years)
    if not years:
        return {"aoi": slug, "note": f"no reference year {ref_years} is fully covered by satellite months"}
    units = pl.read_parquet(units_path)
    pairs = compare(units, reference.filter(pl.col("year").is_in(sorted(years))))
    summary = summarize(pairs)

    out = data / "gold" / "sentinel"
    summary.write_csv(out / f"{slug}_validation.csv")
    pairs.write_csv(out / f"{slug}_validation_units.csv")
    return {
        "aoi": slug,
        "summary": summary.to_dicts(),
        "skipped_years": sorted(set(ref_years) - years),
        "path": str(out / f"{slug}_validation.csv"),
    }


if __name__ == "__main__":
    try:
        result = run_validation(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AOI)
    except (ReferenceDataError, FileNotFoundError) as e:
        sys.exit(str(e))
    if "summary" not in result:
        print(result["note"])
        sys.exit(0)
    print(f"{result['aoi']}: reference years without full satellite coverage: {result['skipped_years'] or 'none'}")
    for row in result["summary"]:
        r = "-" if row["r"] is None else f"{row['r']:.2f}"
        print(
            f"  {row['year']} {row['measure']:<9} units={row['units']:>3}  r={r:>5}  "
            f"ratio={row['ratio']:.2f}  median |diff|={row['median_abs_diff_pct']:.0f}%"
        )
