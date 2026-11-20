# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs @ { flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      perSystem = { config, pkgs, system, ... }: {
        devShells.default = pkgs.mkShell{
          packages = with pkgs; [
            uv
            python313
            just
            typst
            mongosh
            sqlite
            ruff
            basedpyright
            reuse
            pnpm
          ];
          TYPST_FONT_PATHS = "${pkgs.source-sans}/share/fonts";
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
          ];
          shellHook = ''
            export UV_PROJECT_ENVIRONMENT="$HOME/.cache/venvs/mini-project"
            export pnpm_config_virtual_store_dir="$HOME/.cache/node-stores/mini-project-site"
            export pnpm_config_store_dir="$HOME/.cache/pnpm-store"
            export pnpm_config_pm_on_fail=ignore
          '';
        };
      };
  };
}