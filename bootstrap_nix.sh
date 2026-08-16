#!/usr/bin/env bash
#
# Enters the Nix dev shell defined in flake.nix. That shell provides a Python
# interpreter with the runtime dependencies of pyproject.toml and with Invoke
# and Tox, plus the tools that are not Python packages: libtidy (integration
# tests), Chromium and a matching driver (end2end and screencast tests), and
# github_changelog_generator.
#
# Tox still creates its own virtual environments under build/tox/, but it
# installs only the development dependencies of tox.ini there. The runtime
# dependencies of pyproject.toml come from the Nix shell.
#
# This is an alternative to the .envrc + .venv + invoke workflow, which keeps
# working unchanged. The two do not share a virtual environment.
#
# Usage:
#   ./bootstrap_nix.sh        # enter an interactive dev shell
#   ./bootstrap_nix.sh <cmd>  # run a single command inside the dev shell
#
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if ! command -v nix >/dev/null 2>&1; then
  echo "error: nix is not installed. See https://nixos.org/download/" >&2
  exit 1
fi

# -v: Nix explains what it's doing (evaluating, copying/substituting
#     store paths, ...), not just the end result.
# -L (--print-build-logs): stream the actual build output of any
#     derivation that needs building, instead of hiding it behind a
#     spinner.
echo "strictdoc: entering Nix dev shell (see flake.nix) -- verbose, so you can see what Nix is doing." >&2

if [ "$#" -eq 0 ]; then
  exec nix develop -v -L
else
  exec nix develop -v -L --command "$@"
fi
