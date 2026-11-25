{
  pkgs,
  lib,
  config,
  inputs,
  ...
}:

{
  # https://devenv.sh/basics/
  env.TYPST_FONT_PATHS = "${pkgs.source-sans}/share/fonts";
  env.LD_LIBRARY_PATH = lib.makeLibraryPath [
    pkgs.stdenv.cc.cc.lib
    pkgs.zlib
    pkgs.expat
  ];
  env.pnpm_config_pm_on_fail = "ignore";

  # https://devenv.sh/packages/
  packages = with pkgs; [
    git
    uv
    python313
    just
    typst
    mongosh
    sqlite
    ruff
    basedpyright
    nodejs_24
    pnpm
    wrangler
    bitwarden-cli
    secretspec
    zizmor
    pinact
    typos
    lychee
    reuse
  ];

  # https://devenv.sh/languages/
  # languages.rust.enable = true;

  # https://devenv.sh/processes/
  # processes.dev.exec = "${lib.getExe pkgs.watchexec} -n -- ls -la";

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/scripts/
  scripts.lint-actions.exec = "zizmor --offline .github/workflows";

  # https://devenv.sh/basics/
  enterShell = ''
    export UV_PROJECT_ENVIRONMENT="$HOME/.cache/venvs/mini-project"
    export pnpm_config_virtual_store_dir="$HOME/.cache/node-stores/mini-project-site"
    export pnpm_config_store_dir="$HOME/.cache/pnpm-store"
    git --version
  '';

  # https://devenv.sh/tasks/
  # tasks = {
  #   "myproj:setup".exec = "mytool build";
  #   "devenv:enterShell".after = [ "myproj:setup" ];
  # };

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';

  # https://devenv.sh/git-hooks/
  git-hooks.hooks.typos.enable = true;
  git-hooks.hooks.lychee.enable = true;
  git-hooks.hooks.lychee.files = "\\.(md|typ)$";
  git-hooks.hooks.lychee.settings.configPath = "lychee.toml";
  git-hooks.hooks.reuse.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
