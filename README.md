# tikungcrops

tikungcrops turns public satellite data into a planting calendar for paddy farmers in Kecamatan Tikung, Lamongan. See it live at https://tikungcrops.web.id.

## Prerequisites

- [Nix](https://nixos.org/download/) and [devenv](https://devenv.sh/getting-started/), optionally [direnv](https://direnv.net/) (`.envrc` runs `use devenv`).
  Its shell provides `uv`, `just`, `typst`, `mongosh`, `sqlite`, `ruff`, `basedpyright`, `reuse`, `pnpm`, `typos`, `lychee` and `zizmor`.
- Docker Engine ≥ 24 with Compose v2: https://docs.docker.com/engine/install/
- A [SecretSpec](https://secretspec.dev) provider of your choice, such as your system keyring, 1Password or Bitwarden. `secretspec.toml` lists the names and each person picks where the values live.
  Run `secretspec config global init` once to choose it, then `secretspec set MONGO_ROOT_PASSWORD` and `secretspec set MONGO_URI`, using the same password in both.
  Its shell includes the Bitwarden CLI for anyone who picks `bw://`, which needs an unlocked `BW_SESSION`.

## Usage

```sh
devenv shell    # or: direnv allow
just            # list recipes
just up         # start MongoDB
just setup      # full batch pipeline, after a first `just sentinel` run
just app        # dashboard
just dekit up   # dev tasks from dekit.yaml: site on :3017, then just dekit start app (needs mongo)
```

See `data/README.md` for the data layout, and `data/reference/README.md` for reference statistics and where they came from.

Run these checks before you open a pull request:

```sh
just test            # Python tests
just lint            # ruff and basedpyright
just license-check   # REUSE
just site            # build the static site into site/.output/public
cd site && pnpm test && pnpm lint && pnpm typecheck && pnpm knip
```

Run them inside `devenv shell`, because it sets the library path that the Python wheels need.
It also keeps the pnpm store on the home drive, since native Node modules cannot load from an NTFS mount.

`.github/workflows/monthly.yml` runs on the 25th of each month. It restores the data history from a private R2 bucket, adds last month's Sentinel and CHIRPS data, rebuilds the web JSON and publishes the site.
It needs four secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY`.
Fill the bucket once with `just r2-seed` on the machine that holds the history.
`just monthly` runs the pipeline part locally, and `just deploy` publishes the site.

## Data and credits

This pipeline reads public data, and each source keeps its own licence. These credits also appear in the web site footer.

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
