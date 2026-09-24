# AOI arguments are GADM name paths (e.g. Lamongan/Tikung)
# or GeoJSON files; see src/jotosanur_agri/pipeline/aoi.py.

set dotenv-load
set default-list := true

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
sentinel aoi="Lamongan/Tikung" start="" end="":
    {{py}}.pipeline.load_sentinel "{{aoi}}" {{start}} {{end}}

# Paddy share per cell from the official Lahan Baku Sawah map (needs the Sentinel cells)
paddy aoi="Lamongan/Tikung":
    {{py}}.pipeline.load_paddy "{{aoi}}"

# Soil properties per cell and unit from SoilGrids (needs the Sentinel cells)
soilgrids aoi="Lamongan/Tikung":
    {{py}}.pipeline.load_soilgrids "{{aoi}}"

# CHIRPS monthly rainfall per unit (needs the Sentinel cells); add --refresh to refetch all months
chirps aoi="Lamongan/Tikung" *args:
    {{py}}.pipeline.load_chirps "{{aoi}}" {{args}}

# Rebuild the 5-day silver time series for an area from all bronze months
silver aoi="Lamongan/Tikung":
    {{py}}.pipeline.silver_sentinel "{{aoi}}"

# Detect seasons per cell (flooding, green-up, peak, harvest, rice) and summarise per unit
gold aoi="Lamongan/Tikung":
    {{py}}.pipeline.gold_sentinel "{{aoi}}"

# Score harvest-date forecasts (planting and peak) with leave-one-year-out; needs gold and CHIRPS
forecast aoi="Lamongan/Tikung":
    {{py}}.pipeline.forecast_harvest "{{aoi}}"

# Compare season areas with the area's reference statistics (data/reference/<aoi>/), if any
validate aoi="Lamongan/Tikung":
    {{py}}.pipeline.validate_reference "{{aoi}}"

# Sync the area's reference statistics and season summaries into MongoDB
mongo aoi="Lamongan/Tikung": up
    {{py}}.pipeline.load_mongo "{{aoi}}"

# Print aggregation results and query plans (IXSCAN vs COLLSCAN)
agg: up
    {{py}}.mongo_agg

# What the scheduled job runs: last month's scenes, CHIRPS, silver, gold, MongoDB
monthly aoi="Lamongan/Tikung": (sentinel aoi) (chirps aoi) (silver aoi) (gold aoi) (mongo aoi)

# Setup of an area after its first `just sentinel` run
setup aoi="Lamongan/Tikung": (paddy aoi) (soilgrids aoi) (chirps aoi) (silver aoi) (gold aoi) (validate aoi) (mongo aoi)

# Run the dashboard
app:
    uv run streamlit run app.py

# Compile a typst as PDF
pdf target="proposal":
    typst compile documents/{{target}}.typ
