# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Expected harvested area per unit and week for seasons still running.

Uses each cell's state at the end of the series (`gold_sentinel.current_season`) and the
forecasts of `forecast_harvest`, trained on every reliable complete season:
    - `planted` cells get the planting forecast (flooding -> harvest) from
      `ISSUE_AFTER_GREENUP_DAYS` to `MAX_ISSUE_AGE_DAYS` after green-up. A green-up that
      is older with still no peak was usually a false rise seen through clouds (weeds,
      the previous crop) and the real planting came later: in Tikung January backtests
      the error was 30 days within 30 days of green-up, 53 days at 30-60 and 92+ beyond,
      all too early.
    - `peaked` cells get the peak forecast (peak -> harvest).
Each cell's area (paddy share, else 1 ha) is spread evenly over the days of its 80%
range, then summed per unit and ISO week, so the weekly curve carries the uncertainty.

`backtest` replays the outlook as it would have been issued on past dates: silver is
cut at the date, seasons and states are rebuilt from that series alone, the models are
trained only on seasons harvested before it, and the forecasts are compared with the
harvest the full series later detected for the same season (undetected harvests are left
out rather than matched to the next season).

Outputs: data/gold/sentinel/<aoi>_outlook_cells.parquet (per forecast cell) and
<aoi>_outlook_weekly.parquet (unit, week start, expected ha, cells).
Usage: `python -m jotosanur_agri.pipeline.harvest_outlook [AOI] [--backtest DATE ...]`.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from jotosanur_agri.pipeline import save
from jotosanur_agri.pipeline.aoi import resolve
from jotosanur_agri.pipeline.forecast_harvest import ISSUE_AFTER_GREENUP_DAYS, fit, training_table
from jotosanur_agri.pipeline.gold_sentinel import build_gold
from jotosanur_agri.pipeline.load_sentinel import DEFAULT_AOI

ANCHOR = {
    "planting": "flood_date",
    "peak": "peak_date",
}
PEAK_MATCH_DAYS = 30
MAX_ISSUE_AGE_DAYS = 30


def forecast_rows(
    current: pl.DataFrame,
    rain: pl.DataFrame,
) -> dict[str, pl.DataFrame]:
    """Cells ready for each forecast, with the same features as `training_table`."""
    base = current.with_columns(
        pl.col("flood_date").dt.ordinal_day().alias("flood_doy"),
        pl.col("peak_date").dt.ordinal_day().alias("peak_doy"),
        (pl.col("greenup_date") - pl.col("flood_date")).dt.total_days().alias("greenup_after_flood"),
        (pl.col("peak_date") - pl.col("flood_date")).dt.total_days().alias("peak_after_flood"),
        (pl.col("peak_date") - pl.col("greenup_date")).dt.total_days().alias("peak_after_greenup"),
        pl.col("rice").cast(pl.Float64),
        pl.col("flood_passes").cast(pl.Float64),
    ).join(
        rain.select("unit", "year", "month", pl.col("precip_mm").alias("rain_mm")),
        left_on=["unit", pl.col("flood_date").dt.year(), pl.col("flood_date").dt.month()],
        right_on=["unit", "year", "month"],
        how="left",
    )
    age = (pl.col("as_of") - pl.col("greenup_date")).dt.total_days()
    ready = age.is_between(
        ISSUE_AFTER_GREENUP_DAYS,
        MAX_ISSUE_AGE_DAYS,
    )
    return {
        "planting": base.filter(
            pl.col("stage") == "planted",
            pl.col("flood_date").is_not_null(),
            ready,
        ),
        "peak": base.filter(
            pl.col("stage") == "peaked",
            pl.col("peak_date").is_not_null(),
        ),
    }


def predict(
    train: pl.DataFrame,
    rows: dict[
        str,
        pl.DataFrame,
    ],
    units: list[str],
) -> pl.DataFrame:
    """Predicted harvest date and 80% range per ready cell."""
    out = []
    for forecast, df in rows.items():
        if df.is_empty():
            continue
        point, low, high = fit(
            train,
            forecast,
            units,
        ).predict(df)
        anchor = ANCHOR[forecast]
        predicted = {
            "harvest": point,
            "harvest_low": low,
            "harvest_high": high,
        }
        out.append(
            df.select("cell_id", "unit", "as_of", anchor, "w")
            .with_columns(
                pl.Series(
                    f"{name}_days",
                    np.round(v).astype("int64"),
                )
                for name, v in predicted.items()
            )
            .with_columns(
                pl.lit(forecast).alias("forecast"),
                *(
                    (
                        pl.col(anchor)
                        + pl.duration(
                            days=pl.col(f"{name}_days"),
                        )
                    ).alias(name)
                    for name in predicted
                ),
            )
            .rename({anchor: "anchor_date"})
            .drop(*(f"{name}_days" for name in predicted))
        )
    return pl.concat(out) if out else pl.DataFrame()


def weekly(cells: pl.DataFrame) -> pl.DataFrame:
    """Expected harvested area per unit and ISO week, each cell spread over its range."""
    days = (
        cells.with_columns(
            pl.date_ranges(
                "harvest_low",
                "harvest_high",
                "1d",
            ).alias("day")
        )
        .with_columns(
            (pl.col("w") / pl.col("day").list.len()).alias(
                "w_day",
            )
        )
        .explode("day")
    )
    return (
        days.group_by(
            "unit",
            pl.col("day").dt.truncate("1w").alias("week"),
        )
        .agg(
            pl.col("w_day").sum().alias("expected_ha"),
            pl.col("cell_id").n_unique().alias("cells"),
        )
        .sort(
            "unit",
            "week",
        )
    )


def _inputs(
    data: Path,
    slug: str,
) -> tuple[
    pl.DataFrame,
    pl.DataFrame,
    list[Any],
]:
    """Cells with unit and area weight, unit monthly rainfall, and Sentinel-1 dates."""
    cells = pl.read_parquet(
        data / "bronze" / "sentinel" / slug / "cells.parquet",
    ).select(
        "cell_id",
        "unit",
    )
    paddy = data / "bronze" / "sentinel" / slug / "paddy.parquet"
    cells = cells.with_columns(
        pl.lit(1.0).alias("w"),
    )
    if paddy.exists():
        cells = (
            cells.drop("w")
            .join(
                pl.read_parquet(paddy),
                on="cell_id",
                how="left",
            )
            .with_columns(
                pl.col("paddy_frac").fill_null(0.0).alias("w"),
            )
        )
    rain = pl.read_parquet(
        data / "silver" / "chirps" / f"{slug}_monthly.parquet",
    )
    s1_dates = (
        pl.scan_parquet(data / "bronze" / "sentinel" / slug / "[0-9]*.parquet")
        .filter(pl.col("sensor") == "S1")
        .select(pl.col("date").unique())
        .collect()["date"]
        .to_list()
    )
    return (
        cells.select(
            "cell_id",
            "unit",
            "w",
        ),
        rain,
        s1_dates,
    )


def run_outlook(
    aoi_spec: str = DEFAULT_AOI,
    data_dir: str | Path = "data",
) -> dict[str, Any]:
    """Issue the outlook as of the end of the series and write cell and weekly tables."""
    data = Path(data_dir)
    slug = resolve(aoi_spec).slug
    cells, rain, _ = _inputs(data, slug)
    gold_dir = data / "gold" / "sentinel"
    seasons = pl.read_parquet(
        gold_dir / f"{slug}_seasons.parquet",
    )
    current = pl.read_parquet(
        gold_dir / f"{slug}_current.parquet",
    ).drop(
        "unit",
        "paddy_frac",
        strict=False,
    )
    current = current.join(
        cells,
        on="cell_id",
        how="left",
    )
    units = sorted(cells["unit"].unique().to_list())
    per_cell = predict(
        training_table(seasons, rain),
        forecast_rows(current, rain),
        units,
    )
    week = weekly(per_cell) if not per_cell.is_empty() else pl.DataFrame()
    return {
        "aoi": slug,
        "as_of": str(current["as_of"].max()),
        "cells_forecast": dict(
            per_cell.group_by("forecast").len().iter_rows(),
        )
        if not per_cell.is_empty()
        else {},
        "expected_ha": round(
            float(per_cell["w"].sum()),
            1,
        )
        if not per_cell.is_empty()
        else 0.0,
        "cells_path": save(
            per_cell,
            gold_dir / f"{slug}_outlook_cells.parquet",
        ),
        "weekly_path": save(
            week,
            gold_dir / f"{slug}_outlook_weekly.parquet",
        ),
    }


def _mean(
    values: pl.Series,
    digits: int,
) -> float | None:
    return (
        round(
            float(
                np.mean(values.cast(pl.Float64).to_numpy()),
            ),
            digits,
        )
        if values.len()
        else None
    )


def backtest(
    aoi_spec: str,
    as_of: list[date],
    data_dir: str | Path = "data",
) -> pl.DataFrame:
    """Replay the outlook on past dates and score it against later detected harvests."""
    data = Path(data_dir)
    slug = resolve(aoi_spec).slug
    cells, rain, s1_dates = _inputs(data, slug)
    silver = pl.read_parquet(
        data / "silver" / "sentinel" / f"{slug}.parquet",
    )
    full = pl.read_parquet(
        data / "gold" / "sentinel" / f"{slug}_seasons.parquet",
    ).drop(
        "unit",
        "paddy_frac",
        strict=False,
    )
    units = sorted(cells["unit"].unique().to_list())
    rows = []
    for day in as_of:
        past, current = build_gold(
            silver.filter(pl.col("date") <= day),
            [d for d in s1_dates if d <= day],
        )
        train = training_table(
            past.join(
                cells,
                on="cell_id",
                how="left",
            ),
            rain,
        ).filter(
            pl.col("harvest_date") <= day,
        )
        per_cell = predict(
            train,
            forecast_rows(
                current.join(
                    cells,
                    on="cell_id",
                    how="left",
                ),
                rain,
            ),
            units,
        )
        # the harvest of the same season in the full series, the season whose peak
        # matches or the first peak after the issue date.
        # Undetected harvests stay null rather than borrowing the next season's.
        later = full.filter(
            pl.col("peak_date") >= day - timedelta(days=PEAK_MATCH_DAYS),
        ).sort("peak_date")
        first_after = (
            later.group_by("cell_id")
            .first()
            .select(
                "cell_id",
                pl.col("harvest_date").alias(
                    "next_harvest",
                ),
            )
        )
        same_peak = (
            per_cell.filter(pl.col("forecast") == "peak")
            .select(
                "cell_id",
                "anchor_date",
            )
            .join(
                full.select(
                    "cell_id",
                    "peak_date",
                    "harvest_date",
                ),
                on="cell_id",
            )
            .filter(
                (
                    pl.col("peak_date")
                    - pl.col(
                        "anchor_date",
                    )
                )
                .dt.total_days()
                .abs()
                <= PEAK_MATCH_DAYS,
            )
            .group_by("cell_id")
            .first()
            .select("cell_id", pl.col("harvest_date").alias("peak_harvest"))
        )
        scored = (
            per_cell.join(
                first_after,
                on="cell_id",
                how="left",
            )
            .join(
                same_peak,
                on="cell_id",
                how="left",
            )
            .with_columns(
                pl.when(pl.col("forecast") == "peak")
                .then(pl.col("peak_harvest"))
                .otherwise(pl.col("next_harvest"))
                .alias("actual")
            )
        ).with_columns(
            (
                pl.col("harvest")
                - pl.col(
                    "actual",
                )
            )
            .dt.total_days()
            .abs()
            .alias("err"),
            pl.col("actual")
            .is_between(
                "harvest_low",
                "harvest_high",
            )
            .alias("inside"),
        )
        for (forecast,), g in scored.group_by("forecast"):
            found = g.filter(
                pl.col("actual").is_not_null(),
            )
            rows.append(
                {
                    "as_of": day,
                    "forecast": forecast,
                    "cells": g.height,
                    "harvest_found": round(found.height / max(g.height, 1), 2),
                    "mae_days": _mean(found["err"], 1),
                    "range_coverage": _mean(found["inside"], 2),
                }
            )
        # per unit: median predicted vs detected harvest date
        per_unit = (
            scored.filter(
                pl.col("actual").is_not_null(),
            )
            .group_by("unit")
            .agg(
                pl.len().alias("n"),
                pl.col("harvest")
                .cast(pl.Int32)
                .median()
                .alias(
                    "p",
                ),
                pl.col("actual")
                .cast(pl.Int32)
                .median()
                .alias(
                    "a",
                ),
            )
            .filter(pl.col("n") >= 10)
        )
        if not per_unit.is_empty():
            rows.append(
                {
                    "as_of": day,
                    "forecast": "unit_median",
                    "cells": int(per_unit["n"].sum()),
                    "harvest_found": None,
                    "mae_days": _mean((per_unit["p"] - per_unit["a"]).abs(), 1),
                    "range_coverage": None,
                }
            )
    return pl.DataFrame(rows)


if __name__ == "__main__":
    args = sys.argv[1:]
    aoi = args[0] if args and not args[0].startswith("--") else DEFAULT_AOI
    if "--backtest" in args:
        dates = [
            date.fromisoformat(a)
            for a in args[
                args.index(
                    "--backtest",
                )
                + 1 :
            ]
        ]
        with pl.Config(tbl_rows=50):
            print(backtest(aoi, dates))
    else:
        print(run_outlook(aoi))
