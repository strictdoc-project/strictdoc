# Using XPATH to search text containing &nbsp;
# https://stackoverflow.com/a/59699055
NBSP = "\u00a0"

TEXT_WITH_TRAILING_WHITESPACES = """
Hello world!    
    
Hello world!    
    
Hello world!    
                """  # noqa: W291, W293

BROKEN_RST_MARKUP = """
- Broken RST markup

  - AAA
  ---
    """.strip()  # noqa: W291, W293

RST_STRING_THAT_NEEDS_HTML_ESCAPING = """
-
--- MODIFIED BY TEST

`Link does not get corrupted <https://github.com/strictdoc-project/sphinx-latex-reqspec-template>`_

`Link does not get corrupted <https://github.com/strictdoc-project/sphinx-latex-reqspec-template>`_

`Link does not get corrupted <https://github.com/strictdoc-project/sphinx-latex-reqspec-template>`_
""".strip()  # noqa: E501
