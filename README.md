# tikungcrops

## Prerequisites

- [Nix](https://nixos.org/download/) and [devenv](https://devenv.sh/getting-started/), optionally [direnv](https://direnv.net/) (`.envrc` runs `use devenv`).
  Its shell provides `uv`, `just`, `typst`, `mongosh`, `sqlite`, `ruff`, `basedpyright`, `reuse`, `pnpm`, `typos`, `lychee` and `zizmor`.
- Docker Engine ≥ 24 with Compose v2: https://docs.docker.com/engine/install/
- An unlocked Bitwarden session (`BW_SESSION`), because SecretSpec reads the database settings from it.
  Run `secretspec set MONGO_ROOT_PASSWORD` and `secretspec set MONGO_URI` once, using the same password in both.

## Usage

```sh
devenv shell    # or: direnv allow
just            # list recipes
just up         # start MongoDB
just setup      # full batch pipeline, after a first `just sentinel` run
just app        # dashboard
just dekit up   # dev tasks from dekit.yaml: site on :3017, then just dekit start app (needs mongo)
```

Data layout: `data/README.md`. Reference statistics and their provenance: `data/reference/README.md`.

Checks run with these commands:

```sh
just test            # Python tests
just lint            # ruff and basedpyright
just license-check   # REUSE
just site            # build the static site into site/.output/public
cd site && pnpm test && pnpm lint && pnpm typecheck && pnpm knip
```

Run these inside `devenv shell`, because it sets the library path that the Python wheels need.
It also keeps the pnpm store on the home drive, since native Node modules cannot load from an NTFS mount.

`.github/workflows/monthly.yml` runs on the 25th of each month. It fetches CHIRPS plus the previous month's Sentinel-1 and Sentinel-2 scenes.
Scenes are uploaded as a workflow artifact that is kept for 90 days.
It needs no secrets, since every source is public.
Silver needs all past months, so rebuild it where the bronze history lives with `just silver`.
Locally, `just monthly` runs this same job.

## Data and credits

This pipeline reads public data that keeps its own licence. These credits appear in the web site footer.

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

Code is Apache-2.0, and the transcribed reference figures are CC BY 4.0.
Fonts, the UNESA logo and the palette colors keep their own licences, as `REUSE.toml` lists file by file.
`LICENSES/` holds the licence texts. Run `just license-check` to check every file with REUSE.
