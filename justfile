# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

# AOI arguments are GADM name paths (e.g. Lamongan/Tikung)
# or GeoJSON files, see src/tikungcrops/pipeline/aoi.py.

set default-list := true
set shell := ["bash", "-euo", "pipefail", "-c"]

# https://docs.astral.sh/uv
uv := require("uv")

# Recipes that reach MongoDB run behind this prefix, so SecretSpec supplies the MONGO_ variables.
secrets := require("secretspec") + ' run --reason "run the project database" --'

aoi := "Lamongan/Tikung"
py := "uv run python -m tikungcrops"
PATHS := "src tests scripts app.py"

# Install the project and its dev tools
sync:
    uv sync

# Run dekit, which starts the dev tasks in dekit.yaml: just dekit up
[group("dev")]
@dekit *args:
    uv run dekit {{ args }}

# Check Docker is installed and the daemon is reachable
[private]
docker-check:
    @command -v docker >/dev/null || { echo "docker not found, install Docker Engine: https://docs.docker.com/engine/install/"; exit 1; }
    @docker info >/dev/null 2>&1 || { echo "docker daemon not reachable, start it (e.g. sudo service docker start)"; exit 1; }

# Start MongoDB and wait until healthy
[group("db")]
up: docker-check
    {{ secrets }} docker compose up -d --wait

# Stop MongoDB
[group("db")]
down: docker-check
    {{ secrets }} docker compose down

# Open a Mongo shell on the project db
[group("db")]
mongosh:
    {{ secrets }} bash -c '{{ require("mongosh") }} "$MONGO_URI" --eval "db = db.getSiblingDB(\"$MONGO_DB\")" --shell'

# Print aggregation results and query plans (IXSCAN vs COLLSCAN)
[group("db")]
agg: up
    {{ secrets }} {{ py }}.mongo_agg

# Sentinel-1/2 bronze for an area and month range, e.g. `just sentinel Lamongan/Tikung 2020-01 2020-12`, defaults previous month
[group("pipeline")]
sentinel aoi=aoi start="" end="":
    {{ py }}.pipeline.load_sentinel "{{ aoi }}" {{ start }} {{ end }}

# Paddy share per cell from the official Lahan Baku Sawah map (needs the Sentinel cells)
[group("pipeline")]
paddy aoi=aoi:
    {{ py }}.pipeline.load_paddy "{{ aoi }}"

# Soil properties per cell and unit from SoilGrids (needs the Sentinel cells)
[group("pipeline")]
soilgrids aoi=aoi:
    {{ py }}.pipeline.load_soilgrids "{{ aoi }}"

# CHIRPS monthly rainfall per unit (needs the Sentinel cells), add --refresh to refetch all months
[group("pipeline")]
chirps aoi=aoi *args:
    {{ py }}.pipeline.load_chirps "{{ aoi }}" {{ args }}

# Rebuild the 5-day silver time series for an area from all bronze months
[group("pipeline")]
silver aoi=aoi:
    {{ py }}.pipeline.silver_sentinel "{{ aoi }}"

# Detect seasons per cell (flooding, green-up, peak, harvest, rice) and summarise per unit
[group("pipeline")]
gold aoi=aoi:
    {{ py }}.pipeline.gold_sentinel "{{ aoi }}"

# Expected harvested area per unit and week for seasons still running (needs gold and CHIRPS)
[group("pipeline")]
outlook aoi=aoi:
    {{ py }}.pipeline.harvest_outlook "{{ aoi }}"

# Replay the outlook on past dates (several minutes), then fit its range offsets for `just outlook`
[group("pipeline")]
calibrate first="2025-06-01" last="2026-08-15" step="14":
    uv run python scripts/backtest_forecast.py {{ first }} {{ last }} {{ step }}
    uv run python scripts/calibrate_forecast.py

# Compare season areas with the area's reference statistics (data/reference/<aoi>/), if any
[group("pipeline")]
validate aoi=aoi:
    {{ py }}.pipeline.validate_reference "{{ aoi }}"

# Sync the area's reference statistics and season summaries into MongoDB
[group("pipeline")]
mongo aoi=aoi: up
    {{ secrets }} {{ py }}.pipeline.load_mongo "{{ aoi }}"

# Publishable unit outlines (geoBoundaries) for the web map in data/web/<aoi>/
[group("pipeline")]
boundaries aoi=aoi:
    {{ py }}.pipeline.load_boundaries "{{ aoi }}"

# Static JSON for the public web app in data/web/<aoi>/ (needs gold)
[group("pipeline")]
web aoi=aoi:
    {{ py }}.pipeline.export_web "{{ aoi }}"

# What the scheduled job runs: last month's scenes, CHIRPS, silver, gold, harvest outlook, MongoDB, web JSON
[group("pipeline")]
monthly aoi=aoi: (sentinel aoi) (chirps aoi) (silver aoi) (gold aoi) (outlook aoi) (mongo aoi) (web aoi)

# Setup of an area after its first `just sentinel` run
[group("pipeline")]
setup aoi=aoi: (paddy aoi) (soilgrids aoi) (chirps aoi) (silver aoi) (gold aoi) (validate aoi) (outlook aoi) (mongo aoi) (boundaries aoi) (web aoi)

# Score harvest-date forecasts (planting and peak) with leave-one-year-out, needs gold and CHIRPS
[group("model")]
forecast aoi=aoi:
    {{ py }}.pipeline.forecast_harvest "{{ aoi }}"

# Compare untuned models (linear, spline, HGB, CatBoost, XGBoost, LightGBM, voting, stacking) and two fair ensembles with the same year-out loop
[group("model")]
compare-defaults aoi=aoi:
    {{ py }}.pipeline.compare_models "{{ aoi }}" --defaults

# Compare baseline, Ridge, random forest and gradient boosting, each tuned with Optuna inside the training years (~2 h for Tikung)
[group("model")]
compare aoi=aoi:
    {{ py }}.pipeline.compare_models "{{ aoi }}"

# Build the public web site into site/.output/public (needs `just web` for each area first)
[group("web")]
[working-directory("site")]
site: _site-data
    {{ require("pnpm") }} install --frozen-lockfile
    pnpm generate

# Serve the web site with live reload
[group("web")]
[working-directory("site")]
site-dev: _site-data
    {{ require("pnpm") }} dev

# Copy every area's exported JSON into the site's download folder
@_site-data:
    rm -rf site/public/json
    mkdir -p site/public/json
    cp -r data/web/* site/public/json/

# Run the Streamlit dashboard with the input forms
[group("web")]
app:
    {{ secrets }} uv run streamlit run app.py

# Lint and check types
[group("checks")]
@lint:
    ruff check {{ PATHS }}
    ruff format --check {{ PATHS }}
    basedpyright --pythonpath "${UV_PROJECT_ENVIRONMENT:-.venv}/bin/python" src tests

# Check that every file has a license and a copyright holder, and that LICENSES/ matches (REUSE)
[group("checks")]
@license-check:
    reuse lint

# Run the tests, or only some: just test tests/test_gold_sentinel.py -k rice
[group("test")]
@test *args:
    uv run pytest {{ args }}
alias t := test

# Run the tests with line coverage
[group("test")]
@coverage:
    uv run pytest --cov=tikungcrops --cov-report=term-missing


# Compile a typst document as PDF, e.g. `just pdf laporan-akhir/main` or `just pdf paparan-akhir/main`
[group("docs")]
pdf target="proposal":
    {{ require("typst") }} compile --root documents documents/{{ target }}.typ

# Capture the laporan's website figures listed in scripts/figures.yml (start `just site-dev` first)
[group("docs")]
figures *args:
    #!/usr/bin/env bash
    set -euo pipefail
    # NixOS cannot run the browser that Playwright downloads, so the recipe uses the nixpkgs browsers.
    # Playwright must match the nixpkgs build, so the recipe pins the Python package to the same version.
    version=$(nix eval --raw nixpkgs#playwright-driver.version)
    PLAYWRIGHT_BROWSERS_PATH=$(nix build nixpkgs#playwright-driver.browsers --no-link --print-out-paths)
    export PLAYWRIGHT_BROWSERS_PATH
    export PLAYWRIGHT_NODEJS_PATH
    PLAYWRIGHT_NODEJS_PATH=$(command -v node)
    export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
    uvx --from shot-scraper==1.12 --with "playwright==$version" shot-scraper multi scripts/figures.yml --retina --auth scripts/figures-light.json {{ args }}

# Run the site checks: lint, typecheck, tests, knip and a static build (inside the devenv shell)
[group("checks")]
[working-directory("site")]
site-check:
    bash -c 'pnpm lint && pnpm typecheck && pnpm test && pnpm knip && pnpm generate'

# Log in to Cloudflare, needed once and again when the token expires
[group("deploy")]
[working-directory("site")]
cf-login:
    pnpm wrangler login

# Show which Cloudflare account Wrangler is using
[group("deploy")]
[working-directory("site")]
cf-whoami:
    pnpm wrangler whoami

# Build the site and publish it to Cloudflare Workers as tikungcrops, needs a Cloudflare login
[group("deploy")]
[working-directory("site")]
deploy: _site-data
    pnpm deploy

# Upload the data history of one area to the R2 bucket tikungcrops-data, once, from the machine that holds it
[group("deploy")]
[script("bash")]
r2-seed slug="idn-jawatimur-lamongan-tikung":
    set -euo pipefail
    cd site
    find ../data/bronze/sentinel/{{ slug }} ../data/bronze/chirps/{{ slug }}_monthly.parquet \
      ../data/silver/soilgrids/{{ slug }}_*.parquet ../data/gold/sentinel/{{ slug }}_calibration.json \
      ../data/gold/sentinel/{{ slug }}_forecast_eval.csv ../data/web/{{ slug }}/boundaries.geojson -type f | while read -r file; do
      pnpm wrangler r2 object put "tikungcrops-data/data/${file#../data/}" --file "$file" --remote
    done

# Pin the workflow actions to commit hashes and audit them for security problems
[group("check")]
lint-actions:
    {{ require("pinact") }} run
    {{ require("zizmor") }} --gh-token $( {{ require("gh") }} auth token) .github/workflows/ --fix

# Spell check the repository
[group("check")]
typos:
    git ls-files -z | xargs -0 {{ require("typos") }} --force-exclude

# Check the links in the Markdown files
[group("check")]
links:
    git ls-files -z '*.md' | xargs -0 {{ require("lychee") }} --config lychee.toml --no-progress

# Push the current branch to GitHub, without the library path the nix shell leaks into git
[group("deploy")]
push *args:
    env -u LD_LIBRARY_PATH git push {{ args }}

# Build the site icons and the share image from site/public/logo.png: the logo in white on the brand blue
[group("web")]
[working-directory("site/public")]
icons:
    #!/usr/bin/env bash
    set -euo pipefail
    tmp=$(mktemp -d)
    im() { nix run nixpkgs#imagemagick -- "$@"; }
    im logo.png -channel RGB -fill white -colorize 100 -resize 330x330 -background none -gravity center -extent 512x512 "$tmp"/icon-logo.png
    im -size 512x512 xc:none -fill '#0066cc' -draw 'roundrectangle 0,0 511,511 112,112' "$tmp"/icon-bg.png
    im "$tmp"/icon-bg.png "$tmp"/icon-logo.png -gravity center -composite icon-512.png
    im icon-512.png -resize 192x192 icon-192.png
    im icon-512.png -resize 180x180 apple-touch-icon.png
    im icon-512.png -define icon:auto-resize=48,32,16 favicon.ico
    im -size 1200x630 xc:'#0066cc' "$tmp"/og-bg.png
    im "$tmp"/icon-logo.png -resize 380x380 "$tmp"/og-logo.png
    im "$tmp"/og-bg.png "$tmp"/og-logo.png -gravity center -composite og.png
