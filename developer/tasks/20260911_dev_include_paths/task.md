# Include development documents outside the project filters

## WHAT

1. The project configuration shall accept an optional ``dev_include_paths``
   list.

2. StrictDoc shall apply ``dev_include_paths`` only when the web server runs
   in development mode. ``invoke server`` starts the server in this mode.

3. StrictDoc shall silently ignore ``dev_include_paths`` in all other modes.
   A valid development path shall not cause an error in these modes.

4. Each development path shall be relative to the server input root. A leading
   slash shall refer to that root, not the file-system root.

5. Development paths shall remain inside the server input root. Path masks
   containing ``..`` shall remain invalid. A leading slash shall retain the
   root-relative meaning defined above.

6. Development paths shall form an additional document selection. They shall
   bypass ``include_doc_paths``, ``exclude_doc_paths``, and exclusions loaded
   from ``.gitignore``.

7. A development path may select a supported document or a directory. A
   selected directory shall include supported documents in its selected
   subtree.

8. StrictDoc shall export ``_assets`` directories selected by a development
   path. The files in these directories shall be available to the selected
   documents.

9. StrictDoc shall not add a document twice when normal and development paths
   select the same file.

10. ``dev_include_paths`` shall not override the system exclusions for
    ``.git``, the active output directory, or the StrictDoc cache directory.
    If a development path matches one of these directories, StrictDoc shall
    not include its contents and shall not report an error.

11. The development server shall watch selected development documents. A file
    change shall refresh the project through the existing watch mechanism.

12. The server shall allow existing selected development documents to open,
    edit, and save. It shall apply the same path rules when creating a document
    in a selected development directory.

13. The feature shall preserve current document discovery when
    ``dev_include_paths`` is empty or inactive.

## WHY

Developers may keep local documents and fixtures outside the normal
documentation tree. These files may also be excluded from Git. The development
server needs to load them without requiring changes to the regular project
filters or Git exclusions.

## HOW

Implement development paths as a second document selection rooted at the
server input path. Merge this selection with the normal file tree before
parsing documents. Reuse the existing document format dispatch and asset export
pipeline.

Keep normal include and exclude filters unchanged. Pass development paths to
the file and asset finders only when both server mode and development mode are
active. The finders shall traverse an excluded directory when it may contain a
development path, without scanning unrelated excluded trees.

Keep system exclusions separate from configurable exclusions. The development
selection shall never reopen ``.git``, the active output directory, or the
cache directory.

Apply the same development path masks to document discovery, asset discovery,
server path validation, and the file watcher. The project tree, editing
operations, and live reload must follow the same selection rules.
