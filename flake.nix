{
  description = "StrictDoc: open-source software for technical documentation and requirements management";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Built by nixpkgs itself -- numpy/pandas's compiled extensions
        # are already correctly linked against Nix's own libstdc++ (no
        # patchelf needed for these specifically). Symlinked directly
        # into .venv-nix's site-packages in shellHook below, instead of
        # pip-installing this whole stack from PyPI. six/python-dateutil/
        # pytz/tzdata are pandas's own runtime deps, pulled in the same
        # way so pip never needs to touch any of this.
        nixNumpyStack = with pkgs.python312Packages; [
          numpy
          pandas
          six
          python-dateutil
          pytz
          tzdata
        ];
      in
      {
        # `nix develop` (or ./bootstrap_nix.sh) gives a shell with the
        # system-level dependencies that pip cannot install: a Python
        # interpreter, libtidy (used by pytidylib in integration tests),
        # a browser (seleniumbase/playwright end2end + screencast tests),
        # and Ruby (`gem install github_changelog_generator`).
        #
        # All Python dependencies themselves are still installed via pip,
        # exactly as the existing `.envrc` workflow already does -- this
        # flake does not attempt to map them onto nixpkgs' own Python
        # package set.
        #
        # This shell uses its own `.venv-nix/`, separate from `.envrc`'s
        # `.venv/`. Sharing one venv between Nix's Python and the system
        # Python is unsafe: re-running `python -m venv` against an
        # existing venv rewrites pyvenv.cfg to point at whichever python3
        # is currently first on PATH, but does NOT repoint the bin/python
        # symlink -- so alternating between the two providers leaves
        # compiled stdlib extensions (_ssl, termios, ...) mismatched
        # against the running interpreter's glibc, breaking imports with
        # GLIBC_* errors. Separate venv directories avoid that entirely.
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python312
            pkgs.html-tidy
            pkgs.chromium
            pkgs.ruby
          ];

          shellHook = ''
            export PYTHONPYCACHEPREFIX=build/pycache
            # Read by developer/pip_install_strictdoc_deps.py: when set,
            # it symlinks these store paths' packages into whichever venv
            # it's running in (e.g. tox's build/tox/py312-check) instead
            # of pip-installing numpy/pandas from PyPI there too. Only
            # ever set inside this Nix shell, so it's a complete no-op
            # for anyone not using Nix.
            export STRICTDOC_NIX_NUMPY_STACK="${toString nixNumpyStack}"
            echo "strictdoc: activating virtual environment (.venv-nix)."
            # Pip-install the project's own bootstrap set (toml, invoke,
            # packaging, ...) once, right when .venv-nix is first created,
            # so `invoke` and scripts like
            # developer/pip_install_strictdoc_deps.py work immediately
            # without a manual step.
            #
            # numpy/pandas and pandas's own runtime deps are NOT
            # pip-installed at all -- symlinked in from nixNumpyStack
            # instead (module dir + .dist-info, so pip still recognizes
            # them as installed and won't try to pull its own).
            if [ ! -d .venv-nix ]; then
              python3 -m venv .venv-nix/
              site_packages=".venv-nix/lib/python3.12/site-packages"
              for nix_pkg_path in ${toString nixNumpyStack}; do
                for entry in "$nix_pkg_path"/lib/python3.12/site-packages/*; do
                  ln -s "$entry" "$site_packages/$(basename "$entry")"
                done
              done
              .venv-nix/bin/pip install --quiet -r requirements.bootstrap.txt
            fi
            source .venv-nix/bin/activate
          '';
        };
      });
}
