# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Bronze/silver pipeline for the CIMMYT rice survey (real data, South Asia).

Context: data/raw/sumber-data/README.md section 8 and
documents/local/adr-integrasi-data-cimmyt.md.

Bronze is the raw copy of all 136 columns. Silver drops implausible rows and the
columns listed in `DROP_ALWAYS` and `FERTILIZER_BREAKDOWN_COLS`, and keeps the rest
unencoded: one-hot, ordinal and log1p transforms happen inside the scikit-learn
pipeline so they are only ever fitted on training folds.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl

from jotosanur_agri.pipeline import save

RAW_CSV_PATH = "data/external/cimmyt/NUE_survey_dataset_v2.csv"

# Merged_ID: pure identifier. PFPn: yield_kg_ha / N_kg_ha per the CIMMYT dictionary,
# so it leaks the target. *_rel dates duplicate SDATE/TDATE. Prices are economic,
# outside yield prediction.
DROP_ALWAYS = [
    "Merged_ID",
    "PFPn",
    "SDATE_rel",
    "TDATE_rel",
    "FGPRICE_quintal",
    "Urea_price",
]

# Per-product, per-application fertiliser detail. Kept in bronze; dropped in silver
# because N_kg_ha, P2O5_ha, K2O_ha etc. already summarise it and the detail columns
# are highly correlated with them.
FERTILIZER_BREAKDOWN_COLS = [
    "TOTSSP",
    "TOTTSP",
    "TOTMOP",
    "TOTGYP",
    "TOTBOR",
    "TOTZNSO4",
    "Organic_fert_kg_plot",
    "N_in_NPK",
    "N_in_NPKS",
    "N_in_BOFERT",
    "N_in_FTDOFERT",
    "N_in_STDOFERT",
    "N_in_TTDOFERT",
    "BUREA",
    "FTDUREA",
    "FTDUREADY",
    "STDUREA",
    "STDUREADY",
    "TTDUREA",
    "TTDUREADY",
    "BDAP",
    "FTDDAP",
    "FTDDAPDY",
    "STDDAP",
    "STDDAPDY",
    "TTDDAP",
    "TTDDAPDY",
    "BNPK",
    "FTDNPK",
    "FTDNPKDY",
    "STDNPK",
    "STDNPKDY",
    "TTDNPK",
    "TTDNPKDY",
    "BNPKS",
    "FTDNPKS",
    "FTDNPKSDY",
    "STDNPKS",
    "STDNPKSDY",
    "TTDNPKS",
    "TTDNPKSDY",
    "BOFERTAT",
    "FTDOFERTAT",
    "FTDOFERTDY",
    "STDOFERTAT",
    "STDOFERTDY",
    "TTDOFERTAT",
    "TTDOFERTDY",
    "FourthTDUREA",
    "FourthTDUREADY",
    "UREA_N",
    "DAP_N",
    "NPK_N",
    "NPKS_N",
    "OFERT_N",
    "Total_N",
]

TARGET = "yield_kg_ha"
# Sub-survey id: the GroupKFold key, never a model feature
GROUP_KEY = "Dataset"

NOMINAL_CATEGORICAL = [
    "Region",
    "SEASON",
    "GEN",
    "VARTYPE",
    "EST_line",
    "EST_binary",
    "IRRIAVA",
    "PCRRB",
    "SOCCAT",
]
ORDINAL_CATEGORICAL = [
    "EDU",
    "SOPER",
    "SOILTEX",
    "DCLASS",
    "WSEV",
    "INSEV",
    "DISEV",
    "DRSEV",
    "FLSEV",
]
NUMERIC_SKEWED = ["CRLPARHA", "Total_landholding_ha"]  # log1p is applied in the model pipeline
NUMERIC_OTHER = [
    "CRARHA",
    "CRARHA_riceonly",
    "HHMEM",
    "SPRODMR",
    "HIFAG",
    "INFRCR",
    "DISMR",
    "PCRR",
    "SRATEHA",
    "IRRINU",
    "LOD",
    "N_kg_ha",
    "P2O5_ha",
    "K2O_ha",
    "GYP_ha",
    "BOR_ha",
    "Zn_ha",
    "Organic_ha",
    "Nperc_pre_7_DAT",
    "MaxUnsplit_Nperc_within_1_days",
    "Nperc_7to30_DAT",
    "SoilGrids_bdod",
    "SoilGrids_cfvo",
    "SoilGrids_clay",
    "SoilGrids_nitrogen",
    "SoilGrids_ocd",
    "SoilGrids_phh2o",
    "SoilGrids_sand",
    "SoilGrids_silt",
    "SoilGrids_soc",
    "total_precip",
    "num_dry_days",
    "num_wet_days",
    "avg_dspell_length",
    "avg_wspell_length",
    "monsoon_onset",
    "monsoon_retreat",
    "monsoon_length",
    "Nursery_duration",
    "Crop_duration",
    "Field_duration",
    "TDATE_yday",
    "year",
    "LAT",
    "LONG",
]

SILVER_COLUMNS = [TARGET, GROUP_KEY] + NOMINAL_CATEGORICAL + ORDINAL_CATEGORICAL + NUMERIC_SKEWED + NUMERIC_OTHER


def load_bronze(path: str | Path = RAW_CSV_PATH) -> pl.DataFrame:
    """Read the raw CSV with all 136 columns and no row filtering."""
    # The CSV spells missing and infinite values as text ("NA", "Inf"); without these
    # tokens Polars infers those numeric columns as strings.
    return pl.read_csv(
        path,
        infer_schema_length=10000,
        ignore_errors=True,
        null_values=["NA", "N/A", "Inf", "-Inf", "inf", "-inf", ""],
    )


def validate_silver(bronze: pl.DataFrame) -> pl.DataFrame:
    """Drop rows with implausible yield or nitrogen and keep only `SILVER_COLUMNS`."""
    n_before = bronze.height

    valid = (
        bronze.lazy()
        # Unparseable values become null and are filtered out below
        .with_columns(
            pl.col(TARGET).cast(pl.Float64, strict=False),
            pl.col("N_kg_ha").cast(pl.Float64, strict=False),
        )
        .filter(
            pl.col(TARGET).is_not_null(),
            pl.col(TARGET).is_finite(),
            # 365 rows (0.8%) report 1-100 kg/ha, most likely unit errors at data entry
            # (the "obvious inaccuracies" CIMMYT warns about). 300 kg/ha still admits
            # genuinely bad harvests.
            pl.col(TARGET) >= 300,
            pl.col(TARGET) <= 15000,
            pl.col("N_kg_ha").is_not_null(),
            pl.col("N_kg_ha").is_finite(),
            pl.col("N_kg_ha") >= 0,
            pl.col("N_kg_ha") <= 500,
        )
        .select([c for c in SILVER_COLUMNS if c in bronze.columns])
        .collect()
    )
    dropped = n_before - valid.height
    print(f"[cimmyt silver] dropped {dropped} rows ({dropped / n_before * 100:.2f}%)")
    return valid


def run_cimmyt_pipeline(out_dir: str | Path = "data", raw_path: str | Path = RAW_CSV_PATH) -> dict[str, Any]:
    """Write bronze and silver parquet files.

    Returns:
        Row and column counts and output paths.
    """
    out_dir = Path(out_dir)
    bronze = load_bronze(raw_path)
    bronze_path = save(bronze, out_dir / "bronze" / "cimmyt.parquet")
    silver = validate_silver(bronze)
    return {
        "rows_bronze": bronze.height,
        "rows_silver": silver.height,
        "cols_bronze": bronze.width,
        "cols_silver": silver.width,
        "bronze_path": bronze_path,
        "silver_path": save(silver, out_dir / "silver" / "cimmyt.parquet"),
    }


if __name__ == "__main__":
    result = run_cimmyt_pipeline()
    print(result)
