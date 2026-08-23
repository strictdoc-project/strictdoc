{
  description = "StrictDoc: open-source software for technical documentation and requirements management";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      pyproject-nix,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        # This pulls in all of the python dependencies defined by
        # pyproject.toml, but none of the per-task extras that tasks.py
        # installs into build/uv/<flavor> via uv. This means we have enough
        # to run strictdoc, but not the developer tooling.
        project = pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };

        # Use 3.13 for the environment because the nixpkgs cache contains
        # cached builds for some of the larger python dependencies like
        # scipy. When using 3.12, it requires building scipy from source.
        python = pkgs.python313.override {
          self = python;
          packageOverrides = pkgs.lib.composeExtensions treeSitterOverrides versionOverrides;
        };

        # pyproject.toml pins versions that are not in nixpkgs, so we override
        # the versions with the following. The uv2nix project (a subproject
        # of pyproject-nix) could use uv.lock to resolve these automatically
        # instead, but that is a larger step than this flake takes today.
        versionOverrides = final: prev: {
          reqif = prev.reqif.overrideAttrs (_old: rec {
            version = "0.1.0";
            # From the repository rather than the sdist, because nixpkgs' own
            # derivation patches a file under tests/, which the sdist omits.
            src = pkgs.fetchFromGitHub {
              owner = "strictdoc-project";
              repo = "reqif";
              tag = version;
              hash = "sha256-aMjq2x9/aC7HRDL2T2v/yvz+TP+AAKSY3e/TmboKq9Q=";
            };
          });

          python-datauri = prev.python-datauri.overrideAttrs (_old: rec {
            version = "2.2.0";
            src = final.fetchPypi {
              inherit version;
              pname = "python_datauri";
              hash = "sha256-j6WCIpdf7lQc455rC51WU878wkga0mKe/AN41IsT9Ds=";
            };

            # tests/assets holds fixture files, one of which is EBCDIC-encoded
            # and named test_*, so pytest tries to collect it as a module and
            # fails to decode it. In 2.2.0 that directory is not excluded for us.
            disabledTestPaths = [ "tests/assets" ];
          });
        };

        treeSitterOverrides = final: _prev: {
          # nixpkgs packages most of the tree-sitter grammars for Python, but
          # not these two. Both are built the same way as their siblings there,
          # from the grammar's own repository.
          tree-sitter-c = final.buildPythonPackage rec {
            pname = "tree-sitter-c";
            version = "0.24.2";
            pyproject = true;

            src = pkgs.fetchFromGitHub {
              owner = "tree-sitter";
              repo = "tree-sitter-c";
              tag = "v${version}";
              hash = "sha256-Juuf57GQI7OAP6O03KtSzyKJAoXtGKjyYJ+sTM1A4mU=";
            };

            build-system = [ final.setuptools ];
            doCheck = false; # The grammar carries no Python tests.
            pythonImportsCheck = [ "tree_sitter_c" ];
          };

          tree-sitter-cpp = final.buildPythonPackage rec {
            pname = "tree-sitter-cpp";
            version = "0.23.4";
            pyproject = true;

            src = pkgs.fetchFromGitHub {
              owner = "tree-sitter";
              repo = "tree-sitter-cpp";
              tag = "v${version}";
              hash = "sha256-tP5Tu747V8QMCEBYwOEmMQUm8OjojpJdlRmjcJTbe2k=";
            };

            build-system = [ final.setuptools ];
            doCheck = false;
            pythonImportsCheck = [ "tree_sitter_cpp" ];
          };
        };

        # The runtime dependencies plus the "development" extra (invoke, uv).
        # Everything else tasks.py's per-flavor UvEnvironments need is still
        # installed by uv itself, from PyPI, into build/uv/<flavor>.
        pythonEnv = python.withPackages (
          project.renderers.withPackages {
            inherit python;
            extras = [ "development" ];
          }
        );

        # nixpkgs' invoke wrapper puts its own `bin/` first on PATH and drops
        # `NIX_PYTHONPATH`, so the `invoke ...` that tasks.py spawns runs a bare
        # invoke with no access to our Python environment.
        # `python -m invoke` skips that wrapper.
        invokeWrapper = pkgs.writeShellScriptBin "invoke" ''
          exec ${pythonEnv}/bin/python3 -m invoke "$@"
        '';

        # pyproject.toml declares the version dynamic, so the renderer below
        # cannot supply one. hatchling reads it out of this file. Read it the
        # same way rather than repeating the number here.
        version =
          let
            match = builtins.match ''.*__version__ = "([^"]+)".*'' (builtins.readFile ./strictdoc/__init__.py);
          in
          if match == null then
            throw "flake.nix: no __version__ found in strictdoc/__init__.py"
          else
            builtins.head match;

        strictdoc = python.pkgs.buildPythonPackage (
          project.renderers.buildPythonPackage { inherit python; } // { inherit version; }
        );
      in
      {
        # This shell provides the Python environment the project declares,
        # plus the system-level tools that are not Python packages at all:
        # libtidy (pytidylib, integration tests), a browser and a matching
        # driver, both of which seleniumbase picks up from PATH
        # (end2end and screencast tests), and github_changelog_generator.
        devShells.default = pkgs.mkShell {
          packages = [
            invokeWrapper # Must come before pythonEnv, to shadow its `invoke`.
            pythonEnv
            pkgs.html-tidy
            pkgs.chromium
            pkgs.chromedriver
            pkgs.github-changelog-generator
          ];

          # Keep __pycache__ out of the source tree.
          PYTHONPYCACHEPREFIX = "build/pycache";

          # The packages that uv installs from PyPI load shared libraries the
          # way a normal FHS distribution provides them: pytidylib dlopen()s
          # libtidy.so.58 by name, and manylinux wheels link their C extensions
          # against libstdc++/libz. A Nix interpreter does not search any of the
          # usual locations for them, so point the dynamic linker at the
          # Nix-provided copies. Without this, `import numpy` inside a
          # build/uv/<flavor> environment fails with
          # "libstdc++.so.6: cannot open shared object file".
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
            pkgs.html-tidy
          ];

          # tasks.py runs every task through uv, and uv creates its own
          # virtualenvs under build/uv/<flavor>. Put this environment's
          # site-packages on their PYTHONPATH, so that the runtime
          # dependencies of pyproject.toml come from Nix and uv only installs
          # each flavor's extra dependency group. Unlike tox, uv-managed
          # venvs are plain subprocesses that inherit the shell's environment
          # as-is, so a shell-level PYTHONPATH reaches them with no
          # per-environment override needed.
          PYTHONPATH = "${pythonEnv}/${python.sitePackages}";
        };

        # `nix build` and, through the app below, `nix run <this flake>`.
        packages.default = strictdoc;

        apps.default = {
          type = "app";
          program = "${strictdoc}/bin/strictdoc";
        };
      }
    );
}
