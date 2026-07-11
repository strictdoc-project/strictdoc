# Connect CLI "import" command to Format classes

## WHAT

- For each Format that supports importing, make each Format be responsible for building its import command via argparse.
- The available import formats for the `import` command should be read from the available Formats.
- This change shall be surgically precise since a two-staged parsing of strictdoc_config.py is needed:
first, to evaluate the path to the project config and then to use the parsed first-stage project config to know how to populate the import and export commands.

