import threading

from strictdoc.server.document_watcher import DocumentWatcher


def _make_watcher(tmp_path, on_documents_changed, output_dir=None):
    return DocumentWatcher(
        watch_paths=[str(tmp_path)],
        output_dir_abs_path=output_dir,
        on_documents_changed=on_documents_changed,
        debounce_seconds=0.05,
    )


def test_is_watched_document_accepts_sdoc(tmp_path):
    watcher = _make_watcher(tmp_path, lambda: None)

    assert watcher.is_watched_document(str(tmp_path / "doc.sdoc")) is True


def test_is_watched_document_rejects_unrelated_extension(tmp_path):
    watcher = _make_watcher(tmp_path, lambda: None)

    assert watcher.is_watched_document(str(tmp_path / "notes.txt")) is False


def test_is_watched_document_rejects_paths_inside_output_dir(tmp_path):
    output_dir = tmp_path / "output"
    watcher = _make_watcher(tmp_path, lambda: None, output_dir=str(output_dir))

    assert (
        watcher.is_watched_document(str(output_dir / "generated.sdoc")) is False
    )


def test_start_invokes_callback_when_watched_file_changes(tmp_path):
    changed = threading.Event()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    watcher = _make_watcher(tmp_path, changed.set, output_dir=str(output_dir))
    watcher.start()
    try:
        document_path = tmp_path / "doc.sdoc"
        document_path.write_text("[DOCUMENT]\nTITLE: Doc\n", encoding="utf8")
        assert changed.wait(timeout=5) is True
    finally:
        watcher.stop()


def test_start_ignores_changes_inside_output_dir(tmp_path):
    changed = threading.Event()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    watcher = _make_watcher(tmp_path, changed.set, output_dir=str(output_dir))
    watcher.start()
    try:
        generated_path = output_dir / "generated.sdoc"
        generated_path.write_text("[DOCUMENT]\nTITLE: Gen\n", encoding="utf8")
        assert changed.wait(timeout=1) is False
    finally:
        watcher.stop()


def test_start_ignores_rewrite_with_identical_content(tmp_path):
    changed = threading.Event()
    document_path = tmp_path / "doc.sdoc"
    document_path.write_text("[DOCUMENT]\nTITLE: Doc\n", encoding="utf8")

    watcher = _make_watcher(tmp_path, changed.set)
    watcher.start()
    try:
        document_path.write_text("[DOCUMENT]\nTITLE: Doc\n", encoding="utf8")
        assert changed.wait(timeout=1) is False
    finally:
        watcher.stop()


def test_start_invokes_callback_when_content_actually_changes(tmp_path):
    changed = threading.Event()
    document_path = tmp_path / "doc.sdoc"
    document_path.write_text("[DOCUMENT]\nTITLE: Doc\n", encoding="utf8")

    watcher = _make_watcher(tmp_path, changed.set)
    watcher.start()
    try:
        document_path.write_text("[DOCUMENT]\nTITLE: Edited\n", encoding="utf8")
        assert changed.wait(timeout=5) is True
    finally:
        watcher.stop()


def test_is_watched_document_rejects_hidden_directories(tmp_path):
    watcher = _make_watcher(tmp_path, lambda: None)

    assert (
        watcher.is_watched_document(str(tmp_path / ".venv" / "pkg" / "x.md"))
        is False
    )
