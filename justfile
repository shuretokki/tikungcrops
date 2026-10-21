# AOI arguments are GADM name paths (e.g. Lamongan/Tikung)
# or GeoJSON files; see src/jotosanur_agri/pipeline/aoi.py.

set dotenv-load
set default-list := true

aoi := "Lamongan/Tikung"
py := "uv run python -m jotosanur_agri"

# Check Docker is installed and the daemon is reachable
[private]
docker-check:
    @command -v docker >/dev/null || { echo "docker not found; install Docker Engine: https://docs.docker.com/engine/install/"; exit 1; }
    @docker info >/dev/null 2>&1 || { echo "docker daemon not reachable; start it (e.g. sudo service docker start)"; exit 1; }

# Start MongoDB and wait until healthy
up: docker-check
    docker compose up -d --wait

# Stop MongoDB
down: docker-check
    docker compose down

# Open a Mongo shell on the project db
mongosh:
    {{require("mongosh")}} "$MONGO_URI" --eval 'db = db.getSiblingDB("'"$MONGO_DB"'")' --shell

# Sentinel-1/2 bronze for an area and month range, e.g. `just sentinel Lamongan/Tikung 2020-01 2020-12`, defaults previous month
sentinel aoi=aoi start="" end="":
    {{py}}.pipeline.load_sentinel "{{aoi}}" {{start}} {{end}}

# Paddy share per cell from the official Lahan Baku Sawah map (needs the Sentinel cells)
paddy aoi=aoi:
    {{py}}.pipeline.load_paddy "{{aoi}}"

# Soil properties per cell and unit from SoilGrids (needs the Sentinel cells)
soilgrids aoi=aoi:
    {{py}}.pipeline.load_soilgrids "{{aoi}}"

# CHIRPS monthly rainfall per unit (needs the Sentinel cells); add --refresh to refetch all months
chirps aoi=aoi *args:
    {{py}}.pipeline.load_chirps "{{aoi}}" {{args}}

# Rebuild the 5-day silver time series for an area from all bronze months
silver aoi=aoi:
    {{py}}.pipeline.silver_sentinel "{{aoi}}"

# Detect seasons per cell (flooding, green-up, peak, harvest, rice) and summarise per unit
gold aoi=aoi:
    {{py}}.pipeline.gold_sentinel "{{aoi}}"

# Expected harvested area per unit and week for seasons still running (needs gold and CHIRPS)
outlook aoi=aoi:
    {{py}}.pipeline.harvest_outlook "{{aoi}}"

# Score harvest-date forecasts (planting and peak) with leave-one-year-out; needs gold and CHIRPS
forecast aoi=aoi:
    {{py}}.pipeline.forecast_harvest "{{aoi}}"

# Compare baseline, Ridge, random forest and gradient boosting, each tuned with Optuna inside the training years (~1 h for Tikung)
compare aoi=aoi:
    {{py}}.pipeline.compare_models "{{aoi}}"

# Run the test suite
test:
    uv run pytest

# Compare season areas with the area's reference statistics (data/reference/<aoi>/), if any
validate aoi=aoi:
    {{py}}.pipeline.validate_reference "{{aoi}}"

# Sync the area's reference statistics and season summaries into MongoDB
mongo aoi=aoi: up
    {{py}}.pipeline.load_mongo "{{aoi}}"

# Publishable unit outlines (geoBoundaries) for the web map in data/web/<aoi>/
boundaries aoi=aoi:
    {{py}}.pipeline.load_boundaries "{{aoi}}"

# Static JSON for the public web app in data/web/<aoi>/ (needs gold)
web aoi=aoi:
    {{py}}.pipeline.export_web "{{aoi}}"

# Print aggregation results and query plans (IXSCAN vs COLLSCAN)
agg: up
    {{py}}.mongo_agg

# What the scheduled job runs: last month's scenes, CHIRPS, silver, gold, harvest outlook, MongoDB, web JSON
monthly aoi=aoi: (sentinel aoi) (chirps aoi) (silver aoi) (gold aoi) (outlook aoi) (mongo aoi) (web aoi)

# Setup of an area after its first `just sentinel` run
setup aoi=aoi: (paddy aoi) (soilgrids aoi) (chirps aoi) (silver aoi) (gold aoi) (validate aoi) (outlook aoi) (mongo aoi) (boundaries aoi) (web aoi)

# Build the public web site into web/.output/public (needs `just web` for each area first)
site:
    rm -rf web/public/json && mkdir -p web/public/json && cp -r data/web/* web/public/json/
    cd web && pnpm install --frozen-lockfile && pnpm generate

# Web site with live reload
site-dev:
    cd web && pnpm dev

# Run the dashboard
app:
    uv run streamlit run app.py

# Compile a typst as PDF
pdf target="proposal":
    typst compile documents/{{target}}.typ
