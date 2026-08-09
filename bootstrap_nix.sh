#!/usr/bin/env bash
#
# Enters the Nix dev shell defined in flake.nix, which provides the
# system-level dependencies (Python, libtidy, a browser for
# end2end/screencast tests, Ruby for the changelog generator) that the
# existing .envrc + .venv + invoke workflow does not install by itself.
#
# Uses its own .venv-nix/ (separate from .envrc's .venv/) so switching
# between the system Python and Nix's Python never corrupts either venv.
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
