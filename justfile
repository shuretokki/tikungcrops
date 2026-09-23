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

# Sentinel-1/2 cell x date table for one desa and year, e.g. `just sentinel Jotosanur 2020`
sentinel desa="Jotosanur" year="2020":
    {{py}}.pipeline.load_sentinel {{desa}} {{year}}

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
