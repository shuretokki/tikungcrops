# jotosanur-agri

## Prerequisites

- [Nix](https://nixos.org/download/) with flakes, optionally [direnv](https://direnv.net/) (`.envrc` runs `use flake`).
  The devshell provides `uv`, `just`, `typst`, `mongosh`, `sqlite`.
- Docker Engine ≥ 24 with Compose v2: https://docs.docker.com/engine/install/
- `cp .env.example .env` and set `MONGO_ROOT_PASSWORD` (and the same password in `MONGO_URI`).

## Usage

```sh
nix develop     # or: direnv allow
just            # list recipes
just up         # start MongoDB
just setup      # full batch pipeline, after a first `just sentinel` run
just app        # dashboard
just dekit up   # dev tasks from dekit.yaml: site on :3017, then just dekit start app (needs mongo)
```

Data layout: `data/README.md`. Reference statistics and their provenance: `data/reference/README.md`.

## Scheduled extraction

`.github/workflows/monthly.yml` runs on the 25th of each month once the repo has a GitHub
remote: CHIRPS plus the previous month's Sentinel-1/2 scenes, uploaded as a workflow
artifact (kept 90 days). It needs no secrets; every source is public. Silver needs all past
months, so rebuild it where the bronze history lives: `just silver`. The same job runs
locally with `just monthly`.

## Data and credits

The pipeline reads public data that keeps its own licence. The web site shows these credits in its footer.

| Data | Licence | Credit |
|---|---|---|
| Sentinel-1 and Sentinel-2 | Copernicus free and open data licence | Contains modified Copernicus Sentinel data |
| ESA WorldCover 2021 v200 | CC BY 4.0 | ESA WorldCover project, Zanaga et al. 2022 |
| CHIRPS v3 | CC BY 4.0 | UCSB Climate Hazards Center, Funk et al. |
| SoilGrids 2.0 | CC BY 4.0 | ISRIC World Soil Information, Poggio et al. 2021 |
| geoBoundaries gbHumanitarian IDN ADM3/ADM4 | CC BY 3.0 IGO | OCHA ROAP and BPS 2019, Runfola et al. 2020 |
| GADM 4.1 | non-commercial, no redistribution | gadm.org, used only to define the units and never published |
| Lahan Baku Sawah | licence not stated, check before publishing more than the paddy share | Badan Informasi Geospasial |
| BPS and DKPP figures | the source is cited in `data/reference/README.md` | Badan Pusat Statistik and Pemerintah Kabupaten Lamongan |
| OpenFreeMap basemap | OpenStreetMap data under ODbL | © OpenStreetMap contributors, OpenFreeMap |

## License

The code is Apache-2.0, and the transcribed reference figures are CC BY 4.0.
Fonts, the UNESA logo and the palette colors keep their own licences, as `REUSE.toml` lists file by file.
The licence texts are in `LICENSES/`. Run `just license-check` to check every file with REUSE.
