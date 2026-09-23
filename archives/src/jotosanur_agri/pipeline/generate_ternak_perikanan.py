"""Synthetic cattle census and pond harvests for Kampung Pandu Sakti.

Kept apart from `generate_synthetic` (rice) because the dynamics differ: cattle
are a periodic population census, ponds are harvest cycles like rice but with
other parameters. SYNTHETIC data; sources in data/raw/sumber-data/README.md
sections 5-6.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from jotosanur_agri.pipeline import save

# Jotosanur, BPS Tikung 2020: 60 head, 33 households raising cattle (RTP)
SAPI_BASELINE_EKOR = 60
SAPI_BASELINE_RTP = 33
# Local trend from two real BPS counts: 78 head (2013) -> 60 (2020), about -3.68%/year
# or -1.86% per semester. The range is centred there. The East Java provincial trend
# (+1.47% to +2.9%/year) was used before and pointed the wrong way for this desa:
# provincial proxies can invert local reality. Two points give direction and scale,
# not a variance estimate.
# Not used: disnak.jatimprov.go.id shows cattle falling from 4.9M (2023) to 239k (2024)
# to 0 (2025), which is an incomplete backfill, not a real decline.
SAPI_GROWTH_RATE_PER_PERIODE_RANGE = (-0.06, 0.02)
SAPI_CENSUS_PERIODS_PER_YEAR = 2
# Households grow at half the herd's rate
RTP_GROWTH_FACTOR = 0.5

KOLAM_HARVESTS_PER_YEAR = 4
KOLAM_CYCLE_DAYS_RANGE = (75, 90)  # typical for consumption-size lele/nila, not site-specific
# Yield baseline from the kabupaten ratio: 3,394 t lele over 51.35 ha of ponds
# (Dinas Perikanan Lamongan 2021) = ~66 t/ha/year, split over the cycles per year.
# A kabupaten-wide proxy; no Jotosanur figure exists.
KABUPATEN_KOLAM_LUAS_HA = 51.35
KABUPATEN_LELE_PRODUKSI_TON = 3394.02
LELE_YIELD_PER_SIKLUS_TON_PER_HA = KABUPATEN_LELE_PRODUKSI_TON / KABUPATEN_KOLAM_LUAS_HA / KOLAM_HARVESTS_PER_YEAR
# Production CV from a lele farming risk study in Kabupaten Kediri (East Java, the
# closest comparable site). A Lampung study reported 0.04 but differs in province
# and pond system.
LELE_YIELD_CV = 0.217
# Only yield is generated: Kampung Pandu Sakti's pond area is not public, so area and
# total production would need an invented number. Multiply by a real area once the
# mitra provides one.

TERNAK_SCHEMA = {
    "periode_ke": pl.Int32,
    "tanggal_sensus": pl.Date,
    "rtp": pl.Int32,
    "jumlah_ekor": pl.Int32,
    "jenis_ternak": pl.Utf8,
    "is_synthetic": pl.Boolean,
    "generation_seed": pl.Int32,
    "generated_at": pl.Datetime,
}

KOLAM_SCHEMA = {
    "record_id": pl.Utf8,
    "siklus_ke": pl.Int32,
    "tanggal_tebar": pl.Date,
    "tanggal_panen": pl.Date,
    "siklus_hari": pl.Int32,
    "komoditas": pl.Utf8,
    "produktivitas_ton_per_ha": pl.Float64,
    "is_synthetic": pl.Boolean,
    "generation_seed": pl.Int32,
    "generated_at": pl.Datetime,
}


def generate_ternak_sapi(n_periods: int = 8, seed: int = 42, start_date: dt.date = dt.date(2024, 1, 1)) -> pl.DataFrame:
    """Generate a semesterly cattle census as a random walk from the 2020 BPS baseline.

    Args:
        n_periods: Census periods.
        seed: RNG seed; offset internally so it does not mirror the rice draws.
        start_date: First census date.

    Returns:
        Table matching `TERNAK_SCHEMA`.
    """
    rng = np.random.default_rng(seed + 1)
    generated_at = dt.datetime.now(dt.UTC)

    ekor, rtp = SAPI_BASELINE_EKOR, SAPI_BASELINE_RTP
    rows: list[dict[str, Any]] = []
    tanggal = start_date
    for periode in range(1, n_periods + 1):
        growth = rng.uniform(*SAPI_GROWTH_RATE_PER_PERIODE_RANGE)
        ekor = max(1, round(ekor * (1 + growth)))
        rtp = max(1, round(rtp * (1 + growth * RTP_GROWTH_FACTOR)))
        rows.append(
            {
                "periode_ke": periode,
                "tanggal_sensus": tanggal,
                "rtp": rtp,
                "jumlah_ekor": ekor,
                "jenis_ternak": "sapi_potong",
                "is_synthetic": True,
                "generation_seed": seed,
                "generated_at": generated_at,
            }
        )
        tanggal += dt.timedelta(days=365 // SAPI_CENSUS_PERIODS_PER_YEAR)

    return pl.DataFrame(rows, schema=TERNAK_SCHEMA)


def generate_kolam_ikan(n_siklus: int = 8, seed: int = 42, start_date: dt.date = dt.date(2024, 1, 1)) -> pl.DataFrame:
    """Generate consecutive lele harvest cycles in one pond.

    Args:
        n_siklus: Harvest cycles.
        seed: RNG seed; offset internally so it does not mirror the rice draws.
        start_date: First stocking date.

    Returns:
        Table matching `KOLAM_SCHEMA`.
    """
    rng = np.random.default_rng(seed + 2)
    generated_at = dt.datetime.now(dt.UTC)

    rows: list[dict[str, Any]] = []
    tanggal_tebar = start_date
    for siklus in range(1, n_siklus + 1):
        cycle_days = int(rng.integers(*KOLAM_CYCLE_DAYS_RANGE, endpoint=True))
        tanggal_panen = tanggal_tebar + dt.timedelta(days=cycle_days)
        noise = rng.normal(0, LELE_YIELD_CV * LELE_YIELD_PER_SIKLUS_TON_PER_HA)
        produktivitas = max(0.05, LELE_YIELD_PER_SIKLUS_TON_PER_HA + noise)
        rows.append(
            {
                "record_id": f"kolam-{siklus:02d}",
                "siklus_ke": siklus,
                "tanggal_tebar": tanggal_tebar,
                "tanggal_panen": tanggal_panen,
                "siklus_hari": cycle_days,
                "komoditas": "lele",
                "produktivitas_ton_per_ha": round(produktivitas, 4),
                "is_synthetic": True,
                "generation_seed": seed,
                "generated_at": generated_at,
            }
        )
        tanggal_tebar = tanggal_panen + dt.timedelta(days=max(1, (365 // KOLAM_HARVESTS_PER_YEAR) - cycle_days))

    return pl.DataFrame(rows, schema=KOLAM_SCHEMA)


def run_ternak_perikanan_pipeline(out_dir: str | Path = "data", seed: int = 42) -> dict[str, Any]:
    """Generate both tables and write them to the bronze layer.

    Returns:
        Row counts, output paths and the seed.
    """
    bronze_dir = Path(out_dir) / "bronze"
    ternak = generate_ternak_sapi(seed=seed)
    kolam = generate_kolam_ikan(seed=seed)
    return {
        "rows_ternak": ternak.height,
        "rows_kolam": kolam.height,
        "ternak_path": save(ternak, bronze_dir / "ternak_sapi.parquet"),
        "kolam_path": save(kolam, bronze_dir / "kolam_ikan.parquet"),
        "seed": seed,
    }


if __name__ == "__main__":
    print(run_ternak_perikanan_pipeline())
