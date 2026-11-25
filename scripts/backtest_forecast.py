"""Replay the harvest outlook on many past dates and save one scored row per forecast cell.

Each date rebuilds the seasons from the series cut at that date and trains the forecast only on
seasons harvested before it, so the replay is honest about what was known at that time.

Output: data/gold/sentinel/<aoi>_backtest_cells.parquet.
Run from the project root (it takes several minutes):
    nix develop -c uv run --no-sync python scripts/backtest_forecast.py [FIRST] [LAST] [STEP_DAYS] [DATA_DIR]
"""

import sys
from datetime import date, timedelta
from pathlib import Path

from tikungcrops.pipeline.aoi import resolve
from tikungcrops.pipeline.harvest_outlook import backtest_cells
from tikungcrops.pipeline.load_sentinel import DEFAULT_AOI

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / (sys.argv[4] if len(sys.argv) > 4 else "data")


def main() -> None:
    """Run the replay for a regular grid of dates and write the parquet file."""
    first = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date(2023, 10, 1)
    last = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date(2026, 9, 1)
    step = int(sys.argv[3]) if len(sys.argv) > 3 else 21
    days = [first + timedelta(days=i) for i in range(0, (last - first).days + 1, step)]
    print(f"{len(days)} dates from {days[0]} to {days[-1]}", flush=True)
    result = backtest_cells(DEFAULT_AOI, days, DATA)
    out = DATA / "gold" / "sentinel" / f"{resolve(DEFAULT_AOI).slug}_backtest_cells.parquet"
    result.write_parquet(out)
    print(f"wrote {out} with {result.height} rows")


if __name__ == "__main__":
    main()
