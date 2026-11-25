"""Build a copy of the data root in which Landsat dates count as optical dates, to test if they help.

The copy `data_ls/` links everything from `data/` that does not change and rewrites the monthly
Sentinel bronze files with the Landsat rows added under the sensor name "S2", so the silver and gold
steps use them without any code change. Silver and gold are then rebuilt inside `data_ls/`.
The back-test is run on both roots and compared (see `scripts/analyze_forecast.py`).

Run after `load_landsat` has filled data/bronze/landsat:
    nix develop -c uv run --no-sync python scripts/build_landsat_experiment.py
"""

from pathlib import Path

import polars as pl

from tikungcrops.pipeline.aoi import resolve
from tikungcrops.pipeline.gold_sentinel import run_gold_sentinel
from tikungcrops.pipeline.load_sentinel import DEFAULT_AOI
from tikungcrops.pipeline.silver_sentinel import run_silver_sentinel

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data"
DST = ROOT / "data_ls"


def link(rel: str) -> None:
    """Link one path of the data root into the experiment root."""
    target = DST / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.symlink_to(SRC / rel)


def main() -> None:
    """Link the fixed inputs, merge the monthly files, and rebuild silver and gold."""
    slug = resolve(DEFAULT_AOI).slug
    for rel in ("external", "bronze/chirps", "silver/chirps", "silver/soilgrids", "reference"):
        if (SRC / rel).exists():
            link(rel)
    sentinel = SRC / "bronze" / "sentinel" / slug
    out = DST / "bronze" / "sentinel" / slug
    out.mkdir(parents=True, exist_ok=True)
    for name in ("cells.parquet", "paddy.parquet"):
        if (sentinel / name).exists():
            link(f"bronze/sentinel/{slug}/{name}")
    added = 0
    for month in sorted(sentinel.glob("[0-9]*.parquet")):
        base = pl.read_parquet(month)
        extra_path = SRC / "bronze" / "landsat" / slug / month.name
        if extra_path.exists():
            extra = pl.read_parquet(extra_path).with_columns(pl.lit("S2").alias("sensor"))
            base = pl.concat([base, extra.select(base.columns)], how="vertical_relaxed")
            added += extra["date"].n_unique()
        base.write_parquet(out / month.name)
    print(f"{added} Landsat dates added to the optical series")
    print(run_silver_sentinel(DEFAULT_AOI, DST))
    print(run_gold_sentinel(DEFAULT_AOI, DST))


if __name__ == "__main__":
    main()
