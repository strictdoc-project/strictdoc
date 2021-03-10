# StrictDoc

![](https://github.com/stanislaw/strictdoc/workflows/StrictDoc%20on%20macOS/badge.svg?branch=master)
![](https://github.com/stanislaw/strictdoc/workflows/StrictDoc%20on%20Linux/badge.svg?branch=master)
![](https://github.com/stanislaw/strictdoc/workflows/StrictDoc%20on%20Windows/badge.svg?branch=master)

StrictDoc is software for writing technical requirements and specifications.

Summary of StrictDoc features:

- The documentation files are stored as human-readable text files.
- A simple domain-specific language DSL is used for writing the documents. The
  text format for encoding this language is called SDoc (strict-doc).
- StrictDoc reads `*.sdoc` files and builds an in-memory representation of the
  document tree.
- From this in-memory representation, StrictDoc can generate the documentation
  into a number of formats including HTML, RST, PDF, Excel.
- The focus of the tool is modeling requirements and specifications documents.
  Such documents consist of multiple statements like "system X shall do Y"
  called requirements.
- The requirements can be linked together to form the relationships, such as
  "parent-child", and from these connections, many useful features, such as
  [Requirements Traceability](https://en.wikipedia.org/wiki/Requirements_traceability)
  and Documentation Coverage, can be derived.
- Good performance of the [textX](https://github.com/textX/textX) parser and
  parallelized incremental generation of documents: generation of document trees
  with up to 2000-3000 requirements into HTML pages stays within a few seconds.
  From the second run, only changed documents are regenerated. Further
  performance tuning should be possible.

**Warning:** The StrictDoc project is alpha quality. See the
[Roadmap](https://strictdoc.readthedocs.io/en/latest/StrictDoc.html#roadmap)
section to get an idea of the overall project direction.

The documentation is hosted on Read the Docs:
[StrictDoc documentation](https://strictdoc.readthedocs.io/en/latest/).
