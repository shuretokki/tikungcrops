# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Season yield baselines sampled from a Gaussian copula fitted to real BPS data.

Training data: rice in the 13 desa of Kecamatan Tikung for 2013 and 2020 (BPS
Kecamatan Tikung Dalam Angka 2014 and 2021), 26 rows. The copula keeps the real
marginals and the correlation between area, production and yield, instead of
assuming independent Gaussians.

`copulas` is used directly rather than the full SDV package: SDV pulls in torch for
CTGAN/TVAE, which is unneeded for 26 rows, where classical statistics fit better.

Limitations to state wherever this is cited:
    - Rows are annual averages per desa (many farmers and plots), not per-plot,
      per-season data.
    - Pre-program baseline, not PMJ01 performance (see
      `pipeline.generate_synthetic.PMJ01_YIELD_UPLIFT_RANGE`).
    - Two years seven years apart capture how different years can be, not the
      season-to-season pattern.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from copulas.multivariate import GaussianMultivariate

REAL_DATA_PATHS = [
    Path("data/raw/sumber-data/bps-tikung-2013-pertanian.csv"),
    Path("data/raw/sumber-data/bps-tikung-2020-pertanian.csv"),
]
COPULA_COLUMNS = ["luas_panen_ha", "produksi_ton", "produktivitas_ton_per_ha"]
DESA_PER_YEAR = 13
MIN_YIELD_TON_PER_HA = 0.5


def load_real_padi(paths: list[Path] = REAL_DATA_PATHS) -> pd.DataFrame:
    """Load rice rows from the BPS CSVs.

    Raises:
        ValueError: If a file does not have exactly one rice row per desa.
    """
    frames = []
    for path in paths:
        df = pd.read_csv(path)
        padi = df[df["komoditas"] == "padi"][COPULA_COLUMNS]
        if len(padi) != DESA_PER_YEAR:
            raise ValueError(f"expected {DESA_PER_YEAR} rice rows (one per desa) in {path}, got {len(padi)}")
        frames.append(padi)
    return pd.concat(frames, ignore_index=True)


def sample_season_baselines(n_seasons: int, seed: int = 42) -> pd.DataFrame:
    """Sample `n_seasons` desa-season-like rows from the copula.

    Args:
        n_seasons: Rows to sample.
        seed: Seed for the numpy global RNG, which `copulas` samples from.

    Returns:
        Columns `COPULA_COLUMNS`, yield floored at `MIN_YIELD_TON_PER_HA`
        because the copula tails can go below zero.
    """
    np.random.seed(seed)
    model = GaussianMultivariate()
    model.fit(load_real_padi())
    sampled = model.sample(n_seasons)
    sampled["produktivitas_ton_per_ha"] = sampled["produktivitas_ton_per_ha"].clip(lower=MIN_YIELD_TON_PER_HA)
    return sampled.reset_index(drop=True)


if __name__ == "__main__":
    print(f"Real data ({DESA_PER_YEAR} desa x 2 years):")
    print(load_real_padi().describe())
    print("\nCopula sample (8 seasons):")
    print(sample_season_baselines(8))
