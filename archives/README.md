# archives

Code parked on 2026-09-23 when the prediction module moved to satellite-based crop
monitoring (Sentinel-1/2). Kept for reference and for the final report; nothing in
`src/` or `app.py` imports it.

- `src/jotosanur_agri/ml/`: fuzzy Tsukamoto yield rules, random-forest baseline on
  synthetic data (circular, see documents/local/adr-integrasi-data-cimmyt.md) and the
  CIMMYT random-forest benchmark with its shared evaluation code.
- `src/jotosanur_agri/pipeline/`: synthetic rice/cattle/pond generators, the Gaussian
  copula baseline fitted to BPS data, the CIMMYT bronze/silver pipeline, and the
  previous `load_mongo.py` that also loaded the synthetic data.
- `app.py`: previous dashboard with synthetic charts and both predictors.
- `sumber-data/`: the original source notes (Indonesian) and the tables no pipeline
  reads any more: BPS cattle 2013/2020, Dinas Perikanan fish production and pond
  potential 2021. The rice/maize tables moved to `data/reference/`.
- `data/`, `models/` (not tracked): CIMMYT CSVs and trained model files.

Why it was parked: a CIMMYT model restricted to inputs available for Jotosanur did not
transfer (negative R² on every held-out region, 4.15 t/ha predicted vs 6.82/7.25 t/ha
measured by BPS), and no local field data will become available.

To run anything here, move it back under `src/jotosanur_agri/` first; imports still use
the `jotosanur_agri` package paths.
