# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Synthetic rice harvests for Kampung Pandu Sakti (variety PMJ 01).

Stand-in training data while the mitra desa (Kecamatan Tikung) has not replied.
It is SYNTHETIC: every row carries `is_synthetic`, the seed and the generation time.
Distribution parameters come from sources listed in data/raw/sumber-data/README.md;
the ones that are assumptions are marked where they are defined.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from jotosanur_agri.pipeline import save
from jotosanur_agri.pipeline.realistic_baseline import sample_season_baselines

# 60% of the 10.5 ha Kampung Pandu Sakti (program news, 2025)
LAND_HA_TOTAL = 6.3

# ASSUMPTION, sources contradict each other and are not averaged:
# - best demo plot 8-11 t/ha "with optimal care" (Pangdam V/Brawijaya, dailynotif.com,
#   2025-06-17), i.e. +13% to +55% over the BPS baseline of 7.11-7.25 t/ha;
# - actual Jotosanur harvest 1.5 t from 2 ha = 0.75 t/ha (suaranasional.com,
#   2025-07-11), -89%, likely an early trial plot partly kept as seed; kabarjagad.id
#   (Apr 2025) says the variety's fertiliser formula was still being trialled.
# The range below is narrower than both extremes, not a reconciliation of them.
# Report the disagreement; never quote either figure alone.
PMJ01_YIELD_UPLIFT_RANGE = (-0.10, 0.30)

CYCLE_DAYS_RANGE = (80, 85)  # kabarbaik.co
HARVESTS_PER_YEAR = 3
RAINFALL_MONTHLY_RANGE = (3, 572)  # mm, BPS Kec. Tikung 2020 table 1.6
RAINFALL_MONTHLY_MEAN = 139

# Urea dosage for Indonesian paddy across 5 studies: 125-300 kg/ha (Jauhari 2021
# Banyubiru; PHSL Ngawi/Jember, repository.pertanian.go.id; Yunianti et al. 2022
# Pucakwangi; UB thesis, Ciherang Blitar). Not Jotosanur-specific.
FERTILIZER_KG_PER_HA_RANGE = (150, 300)

# Concave (diminishing-returns) response. Reported gains of optimal over farmer
# practice: +6.18% (Yunianti et al. 2022, SSNM) to +28.4% (Jauhari 2021, PUTS);
# the midpoint of ~15% is used.
FERTILIZER_YIELD_UPLIFT_MAX = 0.15

# Per-plot residual (soil, pests, anything no feature captures) as a CV of the season
# baseline, so it scales with the baseline. CVs measured in Indonesian paddy
# production-risk studies: Landak 0.23, Tanjung Morawa 0.22, Tebo 0.3875,
# Sandai/Ketapang high-yield varieties 0.3336. Conservative midpoint 0.25.
RESIDUAL_YIELD_CV = 0.25

# Caps the rainfall penalty so it cannot swamp the fertiliser signal
MAX_RAIN_PENALTY = 0.10
MIN_YIELD_TON_PER_HA = 0.5

BRONZE_SCHEMA = {
    "record_id": pl.Utf8,
    "musim_tanam_ke": pl.Int32,
    "plot_id": pl.Utf8,
    "tanggal_tanam": pl.Date,
    "tanggal_panen": pl.Date,
    "siklus_hari": pl.Int32,
    "luas_ha": pl.Float64,
    "varietas": pl.Utf8,
    "curah_hujan_mm": pl.Float64,
    "pupuk_kg_per_ha": pl.Float64,
    "produktivitas_ton_per_ha": pl.Float64,
    "produksi_ton": pl.Float64,
    "is_synthetic": pl.Boolean,
    "generation_seed": pl.Int32,
    "generated_at": pl.Datetime,
}


def _make_plots(n_plots: int, land_ha_total: float, rng: np.random.Generator) -> list[tuple[str, float]]:
    """Split the land into plots of random size that sum to `land_ha_total`."""
    weights = rng.dirichlet(np.ones(n_plots))
    return [(f"plot-{i + 1:02d}", round(land_ha_total * w, 3)) for i, w in enumerate(weights)]


def generate_bronze(
    n_plots: int = 12,
    n_seasons: int = 8,
    seed: int = 42,
    start_date: dt.date = dt.date(2024, 1, 1),
) -> pl.DataFrame:
    """Generate one synthetic harvest row per plot and season.

    Yield = season baseline x (1 + variety uplift + rain penalty + fertiliser effect)
    + proportional noise, floored at `MIN_YIELD_TON_PER_HA`.

    Args:
        n_plots: Plots the land is split into.
        n_seasons: Consecutive planting seasons.
        seed: RNG seed; the same seed reproduces the same rows.
        start_date: Planting date of the first season.

    Returns:
        Bronze table matching `BRONZE_SCHEMA`.
    """
    rng = np.random.default_rng(seed)
    plots = _make_plots(n_plots, LAND_HA_TOTAL, rng)
    generated_at = dt.datetime.now(dt.UTC)
    # Drawn once per run: it is a property of the variety, not of a season. Drawing
    # it per season adds an offset no feature can explain.
    uplift = rng.uniform(*PMJ01_YIELD_UPLIFT_RANGE)
    season_baselines = sample_season_baselines(n_seasons, seed=seed)

    rows: list[dict[str, Any]] = []
    current_start = start_date
    for musim in range(1, n_seasons + 1):
        cycle_days = int(rng.integers(*CYCLE_DAYS_RANGE, endpoint=True))
        tanggal_tanam = current_start
        tanggal_panen = tanggal_tanam + dt.timedelta(days=cycle_days)
        rainfall = float(np.clip(rng.normal(RAINFALL_MONTHLY_MEAN, 100), *RAINFALL_MONTHLY_RANGE))
        # Very dry or very wet months lower yield
        rain_penalty = np.clip(
            -0.15 * abs(rainfall - RAINFALL_MONTHLY_MEAN) / RAINFALL_MONTHLY_MEAN, -MAX_RAIN_PENALTY, 0.0
        )
        season_baseline = float(season_baselines.iloc[musim - 1]["produktivitas_ton_per_ha"])

        for plot_id, luas_ha in plots:
            pupuk = float(rng.uniform(*FERTILIZER_KG_PER_HA_RANGE))
            low, high = FERTILIZER_KG_PER_HA_RANGE
            pupuk_effect = FERTILIZER_YIELD_UPLIFT_MAX * np.sqrt((pupuk - low) / (high - low))
            noise = rng.normal(0, RESIDUAL_YIELD_CV * season_baseline)
            produktivitas = max(
                MIN_YIELD_TON_PER_HA,
                season_baseline * (1 + uplift + rain_penalty + pupuk_effect) + noise,
            )
            rows.append(
                {
                    "record_id": f"{musim:02d}-{plot_id}",
                    "musim_tanam_ke": musim,
                    "plot_id": plot_id,
                    "tanggal_tanam": tanggal_tanam,
                    "tanggal_panen": tanggal_panen,
                    "siklus_hari": cycle_days,
                    "luas_ha": luas_ha,
                    "varietas": "PMJ01",
                    "curah_hujan_mm": round(rainfall, 1),
                    "pupuk_kg_per_ha": round(pupuk, 1),
                    "produktivitas_ton_per_ha": round(produktivitas, 3),
                    "produksi_ton": round(produktivitas * luas_ha, 3),
                    "is_synthetic": True,
                    "generation_seed": seed,
                    "generated_at": generated_at,
                }
            )

        # Next season starts after this harvest plus the replanting gap
        current_start = tanggal_panen + dt.timedelta(days=max(1, (365 // HARVESTS_PER_YEAR) - cycle_days))

    return pl.DataFrame(rows, schema=BRONZE_SCHEMA)


def validate_silver(bronze: pl.DataFrame) -> pl.DataFrame:
    """Drop rows with non-positive area or yield or a harvest before planting; add `tahun_tanam`."""
    silver = bronze.filter(
        pl.col("luas_ha") > 0,
        pl.col("produktivitas_ton_per_ha") > 0,
        pl.col("tanggal_panen") > pl.col("tanggal_tanam"),
    ).with_columns(pl.col("tanggal_tanam").dt.year().alias("tahun_tanam"))
    dropped = bronze.height - silver.height
    if dropped:
        print(f"[silver] dropped {dropped} invalid rows")
    return silver


def run_pipeline(out_dir: str | Path = "data", n_plots: int = 12, n_seasons: int = 8, seed: int = 42) -> dict[str, Any]:
    """Generate bronze, validate to silver and write both as parquet.

    Returns:
        Row counts, output paths and the seed.
    """
    out_dir = Path(out_dir)
    bronze = generate_bronze(n_plots=n_plots, n_seasons=n_seasons, seed=seed)
    bronze_path = save(bronze, out_dir / "bronze" / "kampung_pandu_harvest.parquet")
    silver = validate_silver(bronze)
    silver_path = save(silver, out_dir / "silver" / "kampung_pandu_harvest.parquet")
    return {
        "rows_bronze": bronze.height,
        "rows_silver": silver.height,
        "bronze_path": bronze_path,
        "silver_path": silver_path,
        "seed": seed,
    }


if __name__ == "__main__":
    print(run_pipeline())
