"""Check CHIRPS monthly rainfall against two ground stations near Tikung.

The stations are the synoptic stations Surabaya Perak and Surabaya Juanda in NOAA GHCN-Daily, which only hold daily rain for 1973 to 2005.
They report BMKG observations, but they are about 50 km from Kecamatan Tikung, so this test
checks the quality of the CHIRPS product in the region, not the value in a desa.
CHIRPS v3 is sampled at the station coordinates, month by month, and compared with the monthly
sum of the station's daily rain. A month counts only when the station has at least 27 valid days.

Output: data/gold/sentinel/verify_rain.csv and a short table on screen.
Run from the project root:
    nix develop -c uv run --no-sync python scripts/verify_rain.py
"""

import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl
import rasterio

from tikungcrops.pipeline.load_chirps import BASE_URL, list_months
from tikungcrops.pipeline.load_sentinel import GDAL_ENV

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "external" / "ghcn"
OUT = ROOT / "data" / "gold" / "sentinel" / "verify_rain.csv"
TIKUNG_RAIN = ROOT / "data" / "silver" / "chirps" / "idn-jawatimur-lamongan-tikung_monthly.parquet"
STATIONS = {
    "Surabaya Juanda": ("IDM00096935", -7.38, 112.787),
    "Surabaya Perak": ("IDM00096933", -7.217, 112.717),
}
FIRST_YEAR = 1981
MIN_DAYS = 27
MIN_PAIRS = 6
WET = {11, 12, 1, 2, 3, 4}


def station_months(station_id: str) -> pl.DataFrame:
    """Return the monthly rain sum in mm of one GHCN-Daily station, for complete months only."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{station_id}.dly"
    if not path.exists():
        url = f"https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/{station_id}.dly"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (student project)"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            path.write_bytes(resp.read())
    rows = []
    for line in path.read_text().splitlines():
        if line[17:21] != "PRCP":
            continue
        year, month = int(line[11:15]), int(line[15:17])
        values = []
        for day in range(31):
            start = 21 + day * 8
            value = int(line[start : start + 5])
            quality = line[start + 6 : start + 7].strip()
            if value != -9999 and not quality:
                values.append(value / 10)
        if len(values) >= MIN_DAYS:
            rows.append({"year": year, "month": month, "station_mm": float(np.sum(values))})
    return pl.DataFrame(rows, schema={"year": pl.Int64, "month": pl.Int64, "station_mm": pl.Float64})


def chirps_at(year: int, month: int, lon: float, lat: float) -> float | None:
    """Return the CHIRPS monthly value in mm at one point, or None when the pixel has no data."""
    url = f"/vsicurl/{BASE_URL}/chirps-v3.0.{year}.{month:02d}.cog"
    for attempt in range(3):
        try:
            with rasterio.Env(**GDAL_ENV), rasterio.open(url) as src:
                value = float(next(src.sample([(lon, lat)]))[0])
            return value if value >= 0 else None
        except rasterio.errors.RasterioIOError:
            if attempt == 2:
                return None
    return None


def score(frame: pl.DataFrame) -> dict[str, float]:
    """Return bias in percent, correlation, RMSE and MAE in mm for paired monthly values."""
    s, c = frame["station_mm"].to_numpy(), frame["chirps_mm"].to_numpy()
    return {
        "n": len(frame),
        "mean_station_mm": float(s.mean()),
        "mean_chirps_mm": float(c.mean()),
        "bias_pct": float((c.sum() - s.sum()) / s.sum() * 100),
        "r": float(np.corrcoef(s, c)[0, 1]),
        "rmse_mm": float(np.sqrt(np.mean((c - s) ** 2))),
        "mae_mm": float(np.mean(np.abs(c - s))),
    }


def main() -> None:
    """Pair station and CHIRPS months, score them by season and write the table."""
    published = {ym for ym in list_months() if ym[0] >= FIRST_YEAR}
    tikung = (
        pl.read_parquet(TIKUNG_RAIN).group_by(["year", "month"]).agg(pl.col("precip_mm").mean().alias("tikung_mm"))
        if TIKUNG_RAIN.exists()
        else None
    )
    results = []
    for name, (station_id, lat, lon) in STATIONS.items():
        months = station_months(station_id).filter(pl.col("year") >= FIRST_YEAR)
        wanted = [(y, m) for y, m in zip(months["year"], months["month"], strict=True) if (y, m) in published]
        with ThreadPoolExecutor(2) as pool:
            values = list(pool.map(lambda ym, lon=lon, lat=lat: chirps_at(ym[0], ym[1], lon, lat), wanted))
        paired = (
            pl.DataFrame({"year": [y for y, _ in wanted], "month": [m for _, m in wanted], "chirps_mm": values})
            .join(months, on=["year", "month"])
            .drop_nulls("chirps_mm")
        )
        groups = {
            "all": paired,
            "wet Nov-Apr": paired.filter(pl.col("month").is_in(WET)),
            "dry May-Oct": paired.filter(~pl.col("month").is_in(WET)),
        }
        for label, frame in groups.items():
            if len(frame) >= MIN_PAIRS:
                results.append({"station": name, "season": label, **score(frame)})
        if tikung is not None:
            ours = paired.join(tikung, on=["year", "month"]).drop_nulls("tikung_mm")
            if len(ours) >= MIN_PAIRS:
                tikung_score = score(ours.rename({"chirps_mm": "point_mm"}).rename({"tikung_mm": "chirps_mm"}))
                results.append({"station": f"{name} vs Tikung CHIRPS", "season": "all", **tikung_score})
    table = pl.DataFrame(results)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.write_csv(OUT)
    with pl.Config(tbl_rows=30, tbl_cols=12, float_precision=2, fmt_str_lengths=40):
        print(table)


if __name__ == "__main__":
    main()
