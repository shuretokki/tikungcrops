# jotosanur-agri — Desa Jotosanur agri dashboard

## Prerequisites

- [Nix](https://nixos.org/download/) with flakes, optionally [direnv](https://direnv.net/) (`.envrc` runs `use flake`).
  The devshell provides `uv`, `just`, `typst`, `mongosh`, `sqlite`.
- Docker Engine ≥ 24 with Compose v2 (system install, not from Nix): https://docs.docker.com/engine/install/
- `cp .env.example .env` and set `MONGO_ROOT_PASSWORD` (and the same password in `MONGO_URI`).

## Usage

```sh
nix develop     # or: direnv allow
just            # list recipes
just up         # start MongoDB
just etl        # full batch pipeline
just app        # dashboard
```

Data sources and their provenance: `data/raw/sumber-data/README.md`.
