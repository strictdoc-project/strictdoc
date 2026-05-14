# StrictDoc

StrictDoc is open-source software for technical documentation and requirements
management.

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

## Quick Start

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

## Project Links

- Documentation: <https://strictdoc.readthedocs.io/en/stable/>
- Source code: <https://github.com/strictdoc-project/strictdoc>
- Examples: <https://github.com/strictdoc-project/strictdoc-examples>
- Templates: <https://github.com/strictdoc-project/strictdoc-templates>

## License

StrictDoc is licensed under the Apache License 2.0. See
[LICENSE](LICENSE) for details.
