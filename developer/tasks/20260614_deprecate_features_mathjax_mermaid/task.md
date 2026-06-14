# Deprecate project config's features: MathJax and Mermaid

## WHAT

If a user has the `MATHJAX` or `MERMAID` features enabled in their project
configuration, print a deprecation warning informing them that these options no
longer have any effect because both features are now enabled by default.

## WHY

The MathJax and Mermaid are now default features. Their JS assets are always
copied to the HTML export folder.

## HOW

- Use the existing `DEPRECATION_ENGINE` to print the deprecation message.
- Add an integration test.
- Update README in case the status of Mermaid and MathJax is still experimental.
