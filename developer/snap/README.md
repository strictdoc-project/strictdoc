# Build

## Note from the maintainer

The workflow of building snap packages with every release of StrictDoc has not
been automated and will be enabled only if someone contributes a Pull Request
that provides a complete and robust automation.

Otherwise, a default way of installing StrictDoc is always via Pip packages.

## Installing snapcraft 

Change into the directory (`./snap`) where this file (`README.md`) is located in.

Install `snapcraft`: `sudo apt install snapcraft`

Build `strictdoc_0.0.18_amd64.snap`: `snapcraft`

## Installation

Change into the directory (`./snap`) where this file (`README.md`) is located in.

Install: `sudo snap install strictdoc_*.snap --devmode --dangerous`

## Usage

```
wget path-to-the-built-strictdoc_0.0.18_amd64.snap
sudo snap install strictdoc_*.snap --devmode --dangerous
```
