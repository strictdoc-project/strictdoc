import os
import threading

from strictdoc.server.document_watcher import DocumentWatcher


def _make_watcher(tmp_path, on_documents_changed, output_dir=None):
    return DocumentWatcher(
        watch_paths=[str(tmp_path)],
        output_dir_abs_path=output_dir,
        on_documents_changed=on_documents_changed,
        debounce_seconds=0.05,
    )


def _abs(path) -> str:
    return os.path.abspath(str(path))


# ---------------------------------------------------------------------------
# is_watched_document — pure logic, no I/O
# ---------------------------------------------------------------------------


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


def test_is_watched_document_rejects_hidden_directories(tmp_path):
    watcher = _make_watcher(tmp_path, lambda: None)

    assert (
        watcher.is_watched_document(str(tmp_path / ".venv" / "pkg" / "x.md"))
        is False
    )


# ---------------------------------------------------------------------------
# _process_pending_paths — hash-change logic tested directly, no timers
#
# Watchdog events are simulated by seeding _content_hashes and adding paths
# to _pending_paths, then calling _process_pending_paths() synchronously.
# ---------------------------------------------------------------------------


def test_process_pending_invokes_callback_when_content_changes(tmp_path):
    called = []
    document_path = tmp_path / "doc.sdoc"
    document_path.write_text("[DOCUMENT]\nTITLE: Doc\n", encoding="utf8")

    watcher = _make_watcher(tmp_path, lambda: called.append(True))
    watcher._seed_content_hashes()
    document_path.write_text("[DOCUMENT]\nTITLE: Edited\n", encoding="utf8")
    watcher._pending_paths.add(_abs(document_path))
    watcher._process_pending_paths()

    assert called == [True]


def test_process_pending_ignores_rewrite_with_identical_content(tmp_path):
    called = []
    document_path = tmp_path / "doc.sdoc"
    document_path.write_text("[DOCUMENT]\nTITLE: Doc\n", encoding="utf8")

    watcher = _make_watcher(tmp_path, lambda: called.append(True))
    watcher._seed_content_hashes()
    # Rewrite with the same bytes — hash is unchanged.
    document_path.write_text("[DOCUMENT]\nTITLE: Doc\n", encoding="utf8")
    watcher._pending_paths.add(_abs(document_path))
    watcher._process_pending_paths()

    assert called == []


def test_inhibit_next_change_suppresses_rebuild_for_ui_write(tmp_path):
    called = []
    document_path = tmp_path / "doc.sdoc"
    document_path.write_text("[DOCUMENT]\nTITLE: Doc\n", encoding="utf8")

    watcher = _make_watcher(tmp_path, lambda: called.append(True))
    watcher._seed_content_hashes()
    # Server registers intent before writing — no race window possible.
    watcher.inhibit_next_change(str(document_path))
    document_path.write_text("[DOCUMENT]\nTITLE: Edited\n", encoding="utf8")
    # Watchdog fires and queues the path.
    watcher._pending_paths.add(_abs(document_path))
    watcher._process_pending_paths()

    assert called == []


def test_inhibit_is_consumed_once_so_subsequent_external_change_rebuilds(
    tmp_path,
):
    called = []
    document_path = tmp_path / "doc.sdoc"
    document_path.write_text("[DOCUMENT]\nTITLE: Doc\n", encoding="utf8")

    watcher = _make_watcher(tmp_path, lambda: called.append(True))
    watcher._seed_content_hashes()
    # UI write — suppressed.
    watcher.inhibit_next_change(str(document_path))
    document_path.write_text("[DOCUMENT]\nTITLE: Edited\n", encoding="utf8")
    watcher._pending_paths.add(_abs(document_path))
    watcher._process_pending_paths()
    assert called == []

    # Subsequent external change — inhibit already consumed, rebuild fires.
    document_path.write_text("[DOCUMENT]\nTITLE: External\n", encoding="utf8")
    watcher._pending_paths.add(_abs(document_path))
    watcher._process_pending_paths()
    assert called == [True]


# ---------------------------------------------------------------------------
# Real-watchdog integration — one test to verify end-to-end wiring.
# Uses a positive assertion so it exits as soon as the callback fires
# (~debounce_seconds); the timeout is only a safety net.
# ---------------------------------------------------------------------------


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
