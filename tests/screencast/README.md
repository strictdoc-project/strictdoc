# Demo Video Pipeline

This directory contains the tooling used to generate demo videos for the StrictDoc website.

The goal is to keep the entire pipeline reproducible:

- demo pages are defined as HTML/CSS/JS;
- browser interaction is scripted with Playwright;
- videos can be regenerated automatically after UI changes.

The generated video assets are intended for the Hugo website and are not part of the StrictDoc application itself.

## Setup

Install the Node dependencies and the Playwright browser binary,\
from `strictdoc-project.github.io`:

```bash
npm install --prefix demo
npx --prefix demo playwright install chromium
```

Only Chromium is needed — `demo.js` doesn't use other browsers.

The demo server scripts also need a local checkout of the
[strictdoc](https://github.com/strictdoc-project/strictdoc) repository and
`tox` to run its dev environment:

- by default, the StrictDoc checkout is expected as a sibling directory:
  `../strictdoc` relative to this repository's root;
- `tox` is expected on `PATH` (e.g. `pip install tox`).

If your setup differs, override with environment variables instead of
editing the scripts:

| Variable | Purpose | Default |
| --- | --- | --- |
| `STRICTDOC_ROOT` | Path to the strictdoc checkout | `../strictdoc` (sibling of this repo) |
| `STRICTDOC_TOX` | Path to the `tox` executable | resolved from `PATH`, falling back to a pyenv-versions guess |
| `STRICTDOC_PYTHON_VERSION` | Python version used in the pyenv fallback above | `3.10.16` |
| `STRICTDOC_SITE_URL` | URL for the manual dev server | `http://127.0.0.1:5111/` |
| `STRICTDOC_VIDEO_SITE_URL` | URL for the temporary recording server | `http://127.0.0.1:5112/` |

## Running the demo server

For manual development and inspecting the demo in the browser,\
from `strictdoc-project.github.io`:

```bash
python3 demo/run_server.py
```

This starts the StrictDoc with the demo fixture at **5111**:
`http://127.0.0.1:5111`.

This server can stay open while developing or inspecting the demo in the browser.

The script:

- stops an existing demo server on the same port;
- starts StrictDoc with the fixture project;
- keeps the server running until stopped manually;
- shuts down the complete StrictDoc process tree on exit.

## Recording the demo video

To generate the demo video,\
from `strictdoc-project.github.io`:

```bash
python3 demo/run_demo.py
```

The video recording uses a separate temporary StrictDoc server.

Using a separate port allows the manual development server to stay open while regenerating videos.

The recording pipeline:

- starts a temporary StrictDoc server at **5112**: `http://127.0.0.1:5112`.
- waits until the server is available;
- runs the Playwright recording scenario;
- stops the complete StrictDoc server process tree afterwards.

The generated videos are written to `demo/output/`.

Each video scenario defines its own output file name.

Each scenario defines:

- the list of recorded steps;
- the output video file name.

Scenarios can combine different sources, for example standalone HTML scenes
(for terminal or IDE-style recordings) and live StrictDoc UI screens.

Standalone HTML scenes (`demo.html`) use a fake typing effect: characters are
appended directly to a page element's text content to *look* like typing.
This is a visual effect only — it does not simulate keyboard input and does
not type into a real input, textarea, or code editor.

## StrictDoc server setup

The helper scripts start StrictDoc automatically. The server can also be started manually from the StrictDoc repository:

```bash
cd /path/to/strictdoc

invoke server \
  --input-path=/path/to/strictdoc-project.github.io/demo/fixtures/strictdoc-demo-project \
  --config=/path/to/strictdoc-project.github.io/demo/fixtures/strictdoc-demo-project/strictdoc_config.py
```

The `input-path` argument points to the demo project root. The `--config` argument points to the demo project's configuration file. Both are required.

*Note*: `invoke server` always uses the default StrictDoc server port.
The video recording script starts StrictDoc through the CLI directly because
it needs a separate temporary port. The `invoke server` wrapper does not expose
port configuration.
