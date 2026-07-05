# StrictDoc Demo Project

This project is used by the screencast scenario/video generation pipeline
in `tests/screencast/`.

## Directory layout

The demo project must keep its documents under the `docs/` directory.

```text
strictdoc-demo-project/
├── docs/
│   └── requirements.sdoc
└── strictdoc_config.py
```

Currently, \
`include_doc_paths = ["/"]` does not behave as expected for this demo project. Although StrictDoc discovers and parses the documents successfully, the generated project tree is empty. Using an explicit top-level directory such as `/docs/` produces the expected project tree.

## Notes

* This fixture is intentionally independent of the main StrictDoc documentation.
* The fixture is used exclusively for reproducible demo video generation.
* The demo project is intended to remain small, deterministic, and independent of the main StrictDoc documentation so that demo videos remain reproducible.
