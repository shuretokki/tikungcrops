# Task runner. `just` lists recipes.

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

# Stop MongoDB (data volume is kept)
down: docker-check
    docker compose down

# Open a Mongo shell on the project db
mongosh:
    {{require("mongosh")}} "$MONGO_URI" --eval 'db = db.getSiblingDB("'"$MONGO_DB"'")' --shell

# SoilGrids pull; pass --refresh to refetch
soilgrids *args:
    {{py}}.pipeline.load_soilgrids {{args}}

# CHIRPS monthly rainfall; pass --refresh to refetch all months
chirps *args:
    {{py}}.pipeline.load_chirps {{args}}

# Sentinel-1/2 bronze for a month range, e.g. `just sentinel Jotosanur 2020-01 2020-12`; no months = previous month
sentinel desa="Jotosanur" start="" end="":
    {{py}}.pipeline.load_sentinel {{desa}} {{start}} {{end}}

# Rebuild the 5-day silver time series for one desa from all bronze months
silver desa="Jotosanur":
    {{py}}.pipeline.silver_sentinel {{desa}}

# Detect rice seasons (flooding, green-up, peak, harvest) per cell from silver
gold desa="Jotosanur":
    {{py}}.pipeline.gold_sentinel {{desa}}

# What the scheduled job runs: CHIRPS update, last month's Sentinel scenes, silver and gold rebuild
monthly desa="Jotosanur": chirps (sentinel desa) (silver desa) (gold desa)

# Load harvest/livestock into MongoDB
mongo: up
    {{py}}.pipeline.load_mongo

# Print aggregation results and query plans (IXSCAN vs COLLSCAN)
agg: up
    {{py}}.mongo_agg

# Full batch ETL, in dependency order
etl: soilgrids chirps mongo

# Run the dashboard
app:
    uv run streamlit run app.py

# Compile the proposal PDF
pdf:
    typst compile documents/proposal.typ
