# Initial support of images in Markdown

## WHAT

StrictDoc should support displaying images in Markdown.

Maybe the support is already there but we can to double-check this by adding integration tests.

## WHY

Displaying images is a common feature of any format such as SDoc or Markdown.

## HOW

- Ensure that the images referenced from Markdown files can be discovered in a similar way like they are with SDoc/RST.
- Write integration tests:
  - The .md file and the _assets folder are at the rool level of the project.
  - The .md file and the _assets folder are in a nested folder in the project dir.
