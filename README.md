# StrictDoc

StrictDoc is open-source software for technical documentation and requirements
management.

## About this fork

This repository (`Robotics010/strictdoc`) is a fork of
[`strictdoc-project/strictdoc`](https://github.com/strictdoc-project/strictdoc),
adapted as a System Engineering tool for a student robotics course building a
Eurobot mobile robot. See `AGENTS.md` for how this fork's conventions relate to
upstream's own developer guide.

## Documentation

The main StrictDoc documentation is hosted on Read the Docs:

The documentation is hosted on Read the Docs:
[StrictDoc documentation](https://strictdoc.readthedocs.io/en/stable/).

For a quick visual overview, see the
[StrictDoc project slide deck](https://github.com/strictdoc-project/strictdoc/blob/main/about/StrictDoc.pdf).

## Installation

StrictDoc requires Python 3.10 or newer.

```bash
pip install strictdoc
```

See the
[StrictDoc user guide](https://strictdoc.readthedocs.io/en/stable/stable/docs/strictdoc_01_user_guide.html)
section of the Read the Docs site for more details.

## Quick start

Create a small `hello_world.sdoc` file:

```text
[DOCUMENT]
TITLE: StrictDoc

[REQUIREMENT]
UID: SDOC-HIGH-REQS-MANAGEMENT
TITLE: Requirements management
STATEMENT: StrictDoc shall enable requirements management.
```

Export it to static HTML:

```bash
strictdoc export .
```

Or run the local web server:

```bash
strictdoc server .
```

StrictDoc starts the server on `http://127.0.0.1:5111` by default.

## Project links

- Source code (this fork): <https://github.com/Robotics010/strictdoc>
- Upstream StrictDoc documentation: <https://strictdoc.readthedocs.io/en/stable/>
- Upstream StrictDoc examples: <https://github.com/strictdoc-project/strictdoc-examples>
- Upstream StrictDoc templates: <https://github.com/strictdoc-project/strictdoc-templates>

This fork does not host separate documentation; the links above to upstream
StrictDoc's docs/examples/templates describe the underlying tool, not the
course-specific setup.

## License

StrictDoc is licensed under the Apache License 2.0. See
[LICENSE](LICENSE) for details.
