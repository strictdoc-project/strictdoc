{
  description = "StrictDoc: open-source software for technical documentation and requirements management";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        # uv.lock is the single source of truth for every Python dependency.
        # It records the exact version of each package and the PyPI artifact
        # that supplies it. uv2nix creates a derivation for each locked
        # package, two virtual environments use these derivations: The dev
        # shell environment gets the development dependencies. The package
        # environment gets only what strictdoc needs to run as a binary.
        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

        # Prefer wheels (pre-built) over sdist (source dist) packages.
        overlay = workspace.mkPyprojectOverlay {
          sourcePreference = "wheel";
        };

        # Use the newest version that pyproject.toml and nixpkgs agree on.
        python = pkgs.lib.last (
          pyproject-nix.lib.util.filterPythonInterpreters {
            inherit (workspace) requires-python;
            inherit (pkgs) pythonInterpreters;
          }
        );

        # The uv2nix description of the runtime Python environment.
        pythonSet = (pkgs.callPackage pyproject-nix.build.packages { inherit python; }).overrideScope (
          pkgs.lib.composeManyExtensions [
            pyproject-build-systems.overlays.wheel
            overlay
          ]
        );

        # The uv2nix description of the runtime + development Python environment.
        editablePythonSet =
          let
            # In the dev shell, strictdoc itself is installed editable.
            # Point at the working tree rather than at a copy in the store.
            # the devShell hook will define REPO_ROOT.
            editableOverlay = workspace.mkEditablePyprojectOverlay {
              root = "$REPO_ROOT";
            };

            # An editable build only has to see enough of the tree for hatchling
            # to work out the package layout and read the project metadata. The
            # code itself is imported from the working tree at runtime.
            # Narrowing the source this way keeps an edit under strictdoc/ from
            # invalidating/rebuilding the dev environment.
            filteredSourceOverlay = final: prev: {
              strictdoc = prev.strictdoc.overrideAttrs (old: {
                src = pkgs.lib.fileset.toSource {
                  root = ./.;
                  fileset = pkgs.lib.fileset.unions [
                    ./pyproject.toml
                    ./README.md
                    ./strictdoc/__init__.py
                  ];
                };

                # hatchling delegates editable installs to `editables`, and
                # pyproject.toml has no reason to declare it, we must add it.
                nativeBuildInputs = old.nativeBuildInputs ++ final.resolveBuildSystem { editables = [ ]; };
              });
            };
          in
          pythonSet.overrideScope (
            pkgs.lib.composeManyExtensions [
              editableOverlay
              filteredSourceOverlay
            ]
          );

        # The runtime dependencies strictdoc, with no development dependencies.
        strictdocVenv = pythonSet.mkVirtualEnv "strictdoc-env" workspace.deps.default;

        # The same, plus the "development" extra (invoke, uv), and with
        # strictdoc editable. Everything else tasks.py's per-flavor
        # UvEnvironments need is still installed by uv itself, from PyPI,
        # into build/uv/<flavor>.
        devVenv = editablePythonSet.mkVirtualEnv "strictdoc-dev-env" (
          workspace.deps.default // { strictdoc = [ "development" ]; }
        );

        # mkApplication exposes bin/strictdoc and the rest of the package's
        # own output, but not the interpreter, the activation scripts or the
        # pyvenv.cfg that come with a virtual environment.
        strictdoc = (pkgs.callPackages pyproject-nix.build.util { }).mkApplication {
          venv = strictdocVenv;
          package = pythonSet.strictdoc;
        };
      in
      {
        # This shell provides the Python environment the project declares,
        # plus the system-level tools that are not Python packages at all:
        # libtidy (pytidylib, integration tests), a browser and a matching
        # driver, both of which seleniumbase picks up from PATH
        # (end2end and screencast tests), and github_changelog_generator.
        devShells.default = pkgs.mkShell {
          packages = [
            devVenv
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

          # tasks.py runs every task through uv. uv creates a virtual
          # environment for each flavor under build/uv/<flavor>. This
          # PYTHONPATH adds the site-packages of the Nix environment to those
          # virtual environments, so the runtime dependencies resolve to the
          # Nix copies. uv also installs the same dependencies into each
          # flavor environment. Both sets come from uv.lock, so the versions
          # agree. uv runs each task as a plain subprocess that inherits the
          # shell environment, so this one variable reaches every flavor.
          PYTHONPATH = "${devVenv}/${python.sitePackages}";

          # Build those virtualenvs from this interpreter, and never from one
          # uv downloaded for itself.
          UV_PYTHON = "${devVenv}/bin/python";
          UV_PYTHON_DOWNLOADS = "never";

          # Fulfill the need of the editable overlay. This points the editable
          # path back to the repository the shell is created it.
          shellHook = ''
            export REPO_ROOT=$(git rev-parse --show-toplevel)
          '';
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
