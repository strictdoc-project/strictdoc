"""
@relation(SDOC-SRS-126, scope=file)
"""

import hashlib
import os
import threading
from typing import Callable, Dict, List, Optional, Set, Union

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

WATCHED_DOCUMENT_EXTENSIONS = (
    ".sdoc",
    ".gra.md",
    ".md",
    ".markdown",
    ".sgra",
    ".reqif",
    ".junit.xml",
    ".gcov.json",
    ".robot.xml",
)


def _as_str(path: Union[str, bytes]) -> str:
    if isinstance(path, bytes):
        return path.decode("utf-8", "surrogateescape")
    return path


def _hash_file(path: str) -> Optional[str]:
    try:
        with open(path, "rb") as file:
            return hashlib.sha256(file.read()).hexdigest()
    except OSError:
        return None


class _ChangeEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        *,
        is_watched_document: Callable[[str], bool],
        on_document_touched: Callable[[str], None],
    ) -> None:
        self._is_watched_document = is_watched_document
        self._on_document_touched = on_document_touched

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        for path in (event.src_path, getattr(event, "dest_path", "")):
            if path:
                document_path = _as_str(path)
                if self._is_watched_document(document_path):
                    self._on_document_touched(document_path)


class DocumentWatcher:
    def __init__(
        self,
        *,
        watch_paths: List[str],
        output_dir_abs_path: Optional[str],
        on_documents_changed: Callable[[], None],
        debounce_seconds: float = 0.3,
    ) -> None:
        self._watch_paths = [os.path.abspath(path) for path in watch_paths]
        self._output_dir_abs_path = (
            os.path.abspath(output_dir_abs_path)
            if output_dir_abs_path is not None
            else None
        )
        self._on_documents_changed = on_documents_changed
        self._debounce_seconds = debounce_seconds
        self._observer: Optional[BaseObserver] = None
        self._debounce_timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._pending_paths: Set[str] = set()
        self._content_hashes: Dict[str, Optional[str]] = {}

    def is_watched_document(self, path: str) -> bool:
        absolute_path = os.path.abspath(path)
        if self._output_dir_abs_path is not None and absolute_path.startswith(
            self._output_dir_abs_path
        ):
            return False
        if self._is_inside_hidden_directory(absolute_path):
            return False
        return absolute_path.endswith(WATCHED_DOCUMENT_EXTENSIONS)

    def _is_inside_hidden_directory(self, absolute_path: str) -> bool:
        for watch_path in self._watch_paths:
            prefix = watch_path + os.sep
            if absolute_path.startswith(prefix):
                directory_parts = absolute_path[len(prefix) :].split(os.sep)[
                    :-1
                ]
                return any(part.startswith(".") for part in directory_parts)
        return False

    def _seed_content_hashes(self) -> None:
        for watch_path in self._watch_paths:
            for current_dir, child_dirs, file_names in os.walk(watch_path):
                child_dirs[:] = [
                    child_dir
                    for child_dir in child_dirs
                    if not child_dir.startswith(".")
                    and not self._is_output_dir(
                        os.path.join(current_dir, child_dir)
                    )
                ]
                for file_name in file_names:
                    document_path = os.path.join(current_dir, file_name)
                    if self.is_watched_document(document_path):
                        absolute_path = os.path.abspath(document_path)
                        self._content_hashes[absolute_path] = _hash_file(
                            absolute_path
                        )

    def _is_output_dir(self, path: str) -> bool:
        return (
            self._output_dir_abs_path is not None
            and os.path.abspath(path) == self._output_dir_abs_path
        )

    def _on_document_touched(self, path: str) -> None:
        with self._lock:
            self._pending_paths.add(os.path.abspath(path))
            if self._debounce_timer is not None:
                self._debounce_timer.cancel()
            self._debounce_timer = threading.Timer(
                self._debounce_seconds, self._process_pending_paths
            )
            self._debounce_timer.daemon = True
            self._debounce_timer.start()

    def _process_pending_paths(self) -> None:
        with self._lock:
            pending_paths = self._pending_paths
            self._pending_paths = set()
        content_changed = False
        for path in pending_paths:
            new_hash = _hash_file(path)
            if new_hash != self._content_hashes.get(path):
                content_changed = True
            self._content_hashes[path] = new_hash
        if content_changed:
            self._on_documents_changed()

    def start(self) -> None:
        self._seed_content_hashes()
        handler = _ChangeEventHandler(
            is_watched_document=self.is_watched_document,
            on_document_touched=self._on_document_touched,
        )
        observer = Observer()
        for watch_path in self._watch_paths:
            if os.path.isdir(watch_path):
                observer.schedule(handler, watch_path, recursive=True)
        observer.daemon = True
        observer.start()
        self._observer = observer

    def stop(self) -> None:
        with self._lock:
            if self._debounce_timer is not None:
                self._debounce_timer.cancel()
                self._debounce_timer = None
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None
