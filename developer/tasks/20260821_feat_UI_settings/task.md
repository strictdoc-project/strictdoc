# Project configuration page

## WHAT

StrictDoc provides a dedicated Project configuration page. The shared
navigation links to this page.

StrictDoc generates the page in both server output and static HTML output.
The static page shows the same configuration information as the server page
but has no editing controls.

The ``Project tree configuration`` block sits in the page sidebar and shows,
each only when the underlying list is not empty:

- input paths;
- included and excluded document paths;
- the source root path;
- included and excluded source paths.

The page shows these main project values as read-only data:

- the active configuration file path;
- project title;
- server host and port.

The page has a separate read-only block for additional configuration:

- lazy document loading threshold, with the installed version's default shown
  alongside it (for example, ``200 by default``);
- output directory;
- grammar aliases;
- custom CSS path;
- favicon path;
- launcher logo path;
- document line width;
- HTML2PDF strict mode, template, and forced page-break nodes;
- ReqIF profile, multiline XHTML mode, MID mode, and import markup.

None of these values are editable through the UI. To change them, a user
edits the active configuration file directly.

### Project features

The page shows a ``Project features`` row with the full list of active
features. When ``ALL_FEATURES`` is among them, the row shows
``ALL_FEATURES:`` followed by the other active features on the same line.

``project_features`` is the only setting the UI can edit. In server mode, the
page shows one of two things in its place, never both:

- an **Enable / disable features** action, when StrictDoc can safely edit
  ``project_features`` in the active configuration file;
- an explanation instead of the action, when it cannot. The explanation
  states why: the file is not a Python file, StrictDoc could not identify a
  single safely editable ``ProjectConfig(...)`` call or extending-config
  assignment, the current value is not a plain list or ``ProjectFeature.all()``
  call, or the file's directory is not writable.

Neither the action nor the explanation appears in static HTML output.

### Editing modal

The Enable / disable features action opens a modal with:

- an **Enable all features** checkbox for ``ALL_FEATURES``;
- individual feature checkboxes in two groups, **Default** (features enabled
  by default) and **Optional** (the rest).

Checking or unchecking **Enable all features** does not change which
individual checkboxes are checked. It only dims the individual checkboxes and
makes them non-interactive while checked; their values still submit with the
form. Unchecking **Enable all features** restores their interactivity. This
way, ``ALL_FEATURES`` never overwrites a user's individual selections.

The modal keeps changes in the browser until the user applies or discards
them. Checking or unchecking a control does not write the configuration file
or reload the project.

The modal footer shows, in order: Close or Cancel, then Apply. Close changes
to Cancel once the form has pending changes. Apply is visible only when at
least one setting is editable, and disabled until the form has a change.

A changed field shows a visible changed state.

Escape closes a modal with no pending changes. With pending changes, the
first Escape asks whether to discard them, offering ``Discard`` and
``Continue editing``. A second Escape while this confirmation is open chooses
Discard, same as clicking Discard.

### Applying changes

Apply validates and saves the submitted value. If validation or writing
fails, the modal stays open, shows the error, and keeps the submitted value.
The active configuration and its file stay unchanged after a failed save.
StrictDoc does not write the file or reload the project when the submitted
value has not changed from the current one.

StrictDoc edits the configuration file it loaded. When the server runs with
``strictdoc server --config <path>``, Apply edits that file, not
``strictdoc_config.py`` in the project root.

The editor supports two Python configuration forms:

- a literal ``project_features`` argument in ``ProjectConfig(...)``;
- a literal assignment, ``config.project_features = [...]``, to the object a
  ``create_config()`` function returns (an "extending" configuration file
  that loads and overrides a base configuration).

For an extending file, Apply edits that file only, never the base
configuration file it imports.

The editor replaces ``config.project_features = ProjectFeature.all()`` with
the explicit list submitted from the form. Any other expression (a computed
value, an imported constant, and similar) stays read-only, with a
manual-edit instruction shown in the page and the modal.

If StrictDoc starts without a configuration file, it uses its default
project configuration, and the page and its edit action are still available.
The first successful Apply creates ``strictdoc_config.py`` in the project
root with the edited ``project_features`` value.

Before replacing an existing configuration file, StrictDoc saves its current
contents as a timestamped version beside it and keeps the five most recent
versions, deleting older ones. The first Apply for a missing configuration
file does not create an empty saved version. Saved configuration version
filenames are ignored by Git. The page does not list, restore, or delete
these versions; managing them in the UI is outside this task.

After a successful Apply, StrictDoc reloads the project configuration and
rebuilds the server state once, under the existing write lock, replacing the
active state only after the rebuild succeeds. Connected browser tabs reload
automatically once the new state is ready.

If the reload fails, StrictDoc keeps the previous in-memory project state,
and the modal shows a settings-specific error in place of the reload
message. The changed configuration file and its saved previous version stay
on disk.

### Failed requests

If opening or applying the modal fails at the network level, or the server
responds with a non-2xx status (for example, an internal error), StrictDoc
does not inject the raw response into the page. It shows a small, dismissible
error message in the modal area instead, with no automatic retry.

### Scope

The page and modal are for users who do not need to know the Python
configuration API. Labels, descriptions, errors, and manual-edit instructions
describe user actions and results. They do not expose AST rules, Python call
shapes, or internal value-source labels.

This version does not add authorization to the configuration routes. It uses
the same access model as the existing editing routes.

Tests shall cover:

- the Project configuration page in server and static output;
- absence of ``Project tree configuration`` on the project index;
- the read-only main and additional configuration blocks;
- absence of editing controls in static output;
- the Enable / disable features action versus its read-only explanation;
- opening and closing the editing modal;
- clean and dirty modal states;
- Cancel and both Escape behaviors;
- disabled and enabled Apply states;
- ``ALL_FEATURES`` without loss of individual feature selections;
- direct ``ProjectConfig(...)`` arguments;
- literal assignments in an extending configuration file;
- replacement of ``ProjectFeature.all()`` with an explicit list;
- a missing configuration file;
- validation and write errors;
- saved-version retention;
- one application-level reload after Apply;
- reload failure without replacement of the active in-memory state.

## WHY

Users need one page where they can inspect the full project configuration
and safely change the one setting, ``project_features``, that StrictDoc can
update through the UI without touching the Python configuration file
directly.

## HOW

The Project configuration screen is generated by
``ProjectConfigurationHTMLGenerator`` and rendered through
``ProjectConfigurationViewObject``, shared by the server router and the
static HTML export. Only the Edit action and its modal are server-only;
everything else renders identically in both modes.

``ProjectSettingsManager`` (``strictdoc/server/project_settings.py``) owns
the editable-settings catalog. It currently defines one editable setting,
``project_features``. It inspects the active configuration file with
Python's ``ast`` module to decide, per request, whether the value is a
supported literal, an ``ALL_FEATURES`` call, or something else the UI must
leave read-only, and whether the target directory is writable.
``ProjectConfigurationViewObject`` calls the same manager to decide whether
the read-only page shows the Edit action or the explanation in its place.

The manager supports a direct ``ProjectConfig(...)`` call and an assignment
to the object an extending ``create_config()`` function returns. It updates
only the ``project_features`` value, preserving unrelated imports, comments,
assignments, and configuration values through targeted source-range edits.

Before replacing the file, the manager builds the candidate source, parses
it, and loads it as a full ``ProjectConfig`` to validate it. It saves and
rotates the five previous versions and writes the new file atomically only
after validation succeeds.

The Apply route reloads the configuration from disk and rebuilds the project
under the existing write lock, replacing the active server state only after
the rebuild succeeds, then broadcasts a WebSocket message so connected
browsers reload; a failed rebuild broadcasts an error message instead and
leaves the previous state in place.

The modal's fetch handlers in ``project_settings.js`` check the response
status before using it. A network error or a non-2xx response shows a
self-contained error notice instead of inserting the server's response body,
which for an internal error would otherwise be a full HTML page, not a modal
fragment.
