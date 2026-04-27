import os
import re
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk

import toml

from strictdoc.commands.export import EXPORT_FORMATS
from strictdoc.helpers.module import import_from_path


class StrictDocLauncher(tk.Tk):
    min_width = 600
    min_height = 350

    def __init__(self) -> None:
        super().__init__()
        self.title("StrictDoc Launcher")
        # Allow resizing; layout will use grid weights so that
        # text fields and the log grow, while buttons keep
        # their natural size.
        self.resizable(True, True)
        self.minsize(self.min_width, self.min_height)

        # Make the default ttk theme a bit nicer if possible.
        # This is best-effort only; on some platforms the theme
        # names differ, so we fall back silently.
        try:
            style = ttk.Style()
            if "equilux" in style.theme_names():
                style.theme_use("equilux")
        except Exception:  # noqa: BLE001
            pass

        # State
        self.workspace_dir: str | None = None
        self.server_process: subprocess.Popen | None = None
        self._log_thread: threading.Thread | None = None

        # Server connection settings used both for starting the server
        # and for constructing the browser URL.
        self.server_host: str = "127.0.0.1"
        self.server_port: int = 5111

        # Supported export formats (single selection), derived from
        # StrictDoc's own EXPORT_FORMATS constant so this list stays
        # in sync with the CLI.
        self._export_formats = list(EXPORT_FORMATS)
        self.export_format_var = tk.StringVar(value="html")

        # Optional project title, can be written into strictdoc.toml
        # in the selected workspace.
        self.project_title_var = tk.StringVar()

        # Export target path (full path). By default this will be
        # "<workspace>/export" once a workspace has been selected,
        # but the user can customize it via the Browse button.
        self.export_path_var = tk.StringVar()

        self._build_ui()

    # UI -----------------------------------------------------------------
    def _build_ui(self) -> None:
        PADDING = {"padx": 12, "pady": 6}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        main = ttk.Frame(self)
        main.grid(row=0, column=0, sticky="nsew", **PADDING)

        # Title / header
        header = ttk.Label(
            main,
            text="StrictDoc Launcher",
            font=("Segoe UI", 11, "bold"),
        )
        header.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))

        # Workspace selection
        ttk.Label(main, text="Workspace:").grid(row=1, column=0, sticky="w")

        self.workspace_var = tk.StringVar()
        self.workspace_entry = ttk.Entry(
            main, textvariable=self.workspace_var, width=40
        )
        self.workspace_entry.grid(row=1, column=1, sticky="we", **PADDING)

        self.workspace_select_btn = ttk.Button(
            main, text="Select ...", command=self.choose_workspace
        )
        self.workspace_select_btn.grid(row=1, column=2, sticky="e")

        # Open Folder button: opens the selected workspace in the system file explorer.
        self.open_folder_btn = ttk.Button(
            main,
            text="Open Folder",
            command=self.open_workspace_in_explorer,
            state="disabled",
        )
        self.open_folder_btn.grid(row=1, column=3, sticky="e", **PADDING)


        # Project config: open a separate dialog instead of inline editing.
        ttk.Label(main, text="Config:").grid(row=2, column=0, sticky="w")
        self.change_config_btn = ttk.Button(
            main,
            text="Change Config ...",
            command=self._open_config_dialog,
        )
        self.change_config_btn.grid(row=2, column=1, sticky="w", **PADDING)

        # Export controls
        export_frame = ttk.LabelFrame(main, text="Export")
        export_frame.grid(row=3, column=0, columnspan=4, sticky="we", **PADDING)

        ttk.Label(export_frame, text="Format:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.export_format_combo = ttk.Combobox(
            export_frame,
            textvariable=self.export_format_var,
            values=self._export_formats,
            state="readonly",
            width=15,
        )
        self.export_format_combo.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        self.export_format_combo.current(0)

        self.export_btn = ttk.Button(
            export_frame,
            text="Export ...",
            command=self.export_html,
        )
        self.export_btn.grid(row=0, column=2, padx=5, pady=5)

        # Export target path: defaults to "<workspace>/export" but can be
        # changed by the user.
        ttk.Label(export_frame, text="Pfad:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )
        self.export_path_entry = ttk.Entry(
            export_frame,
            textvariable=self.export_path_var,
            width=40,
        )
        self.export_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        self.export_browse_btn = ttk.Button(
            export_frame,
            text="Browse ...",
            command=self.choose_export_path,
        )
        self.export_browse_btn.grid(row=1, column=2, padx=5, pady=5, sticky="e")

        # Server controls
        server_frame = ttk.LabelFrame(main, text="Server")
        server_frame.grid(row=4, column=0, columnspan=4, sticky="nsew", **PADDING)

        # Single toggle button: starts or stops the server depending on state.
        self.server_btn = ttk.Button(
            server_frame, text="Start server", command=self._toggle_server
        )
        self.server_btn.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Open browser button: opens default browser pointing at the
        # running StrictDoc server. Enabled only while the server
        # process is running.
        self.open_browser_btn = ttk.Button(
            server_frame,
            text="Open Browser",
            command=self.open_browser,
            state="disabled",
        )
        self.open_browser_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Toggle for server log (inside Server frame)
        self._log_visible = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            server_frame,
            text="Server log anzeigen",
            variable=self._log_visible,
            command=self._toggle_log,
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 5))

        # Collapsible log area (inside Server frame)
        self.log_frame = ttk.LabelFrame(server_frame, text="Server output")
        self.log_text = tk.Text(
            self.log_frame,
            height=10,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
        )
        scrollbar = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)

        # initially hidden
        # self.log_frame will be gridded in _toggle_log when needed
        server_frame.columnconfigure(0, weight=1)
        server_frame.rowconfigure(2, weight=1)

        # Let the server row take up extra vertical space so that the
        # status bar always stays at the bottom.
        main.rowconfigure(4, weight=1)

        # Status bar
        ttk.Separator(main, orient="horizontal").grid(
            row=5, column=0, columnspan=4, sticky="we"
        )
        ttk.Label(main, text="Status:").grid(row=6, column=0, sticky="w")
        self.status_var = tk.StringVar(value="Ready.")
        status_label = ttk.Label(
            main,
            textvariable=self.status_var,
            relief="sunken",
            borderwidth=1,
            anchor="w",
        )
        status_label.grid(
            row=6,
            column=1,
            columnspan=2,
            sticky="we",
            padx=0,
            pady=(2, 0),
        )

        # Column/row weights: column 1 (middle) grows horizontally.
        main.columnconfigure(1, weight=1)

        # Inside export frame, let the combobox column stretch.
        export_frame.columnconfigure(1, weight=1)

        # Clean up on close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # Helpers ------------------------------------------------------------
    def set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.update_idletasks()

    def choose_workspace(self) -> None:
        directory = filedialog.askdirectory(title="StrictDoc Workspace wählen")
        if directory:
            self.workspace_dir = directory
            self.workspace_var.set(directory)
            # Set default export path to "<workspace>/export".
            default_export_path = os.path.join(directory, "export")
            self.export_path_var.set(default_export_path)
            self._load_project_title_from_config()
            self.set_status(f"Workspace set: {directory}")

    def _ensure_workspace(self) -> bool:
        """Validate and synchronize the workspace path from the entry field.

        This method ensures that manual text input in the Workspace field is
        taken into account and that the path actually exists.
        """

        # Prefer the value from the entry field, if present.
        workspace_from_entry = getattr(self, "workspace_var", None)
        if workspace_from_entry is not None:
            value = workspace_from_entry.get().strip()
            if value:
                self.workspace_dir = value

        if not self.workspace_dir:
            messagebox.showwarning(
                "Workspace missing", "Please select a workspace first."
            )
            return False
        if not os.path.isdir(self.workspace_dir):
            messagebox.showerror(
                "Invalid Workspace",
                f"Directory does not exist: {self.workspace_dir}",
            )
            return False
        # At this point the workspace path is valid: enable helper actions
        # that operate on the workspace directory.
        if hasattr(self, "open_folder_btn"):
            self.open_folder_btn.configure(state="normal")

        return True
    
    def open_workspace_in_explorer(self) -> None:
        if not self._ensure_workspace():
            return
        path = os.path.abspath(self.workspace_dir)
        try:
            if sys.platform == "win32":
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", path], check=True)
            else:
                subprocess.run(["xdg-open", path], check=True)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(
                "Error opening folder",
                f"Could not open folder in file explorer:\n{exc}",
            )

    def _load_project_title_from_config(self) -> None:
        """Best effort: Projekt-Titel aus Konfiguration vorbefüllen.

        Reihenfolge:
        1. strictdoc_config.py (Python-Config) via create_config().project_title
        2. strictdoc.toml ([project].title)
        3. Workspace-Ordnername als Vorschlag
        """

        self.project_title_var.set("")
        if not self.workspace_dir:
            return

        workspace_dir_value = self.workspace_dir
        assert workspace_dir_value is not None
        workspace_dir = os.path.abspath(workspace_dir_value)
        config_py_path = os.path.join(workspace_dir, "strictdoc_config.py")
        config_toml_path = os.path.join(workspace_dir, "strictdoc.toml")

        # 1) Python-Config bevorzugen
        if os.path.isfile(config_py_path):
            try:
                module = import_from_path(config_py_path)
                create_config = getattr(module, "create_config", None)
                if callable(create_config):
                    project_config = create_config()
                    title_value = getattr(project_config, "project_title", None)
                    if isinstance(title_value, str) and title_value.strip():
                        self.project_title_var.set(title_value)
                        return
            except Exception:  # noqa: BLE001
                # Bei Problemen das Feld einfach leer lassen und ggf. auf TOML/Fallback gehen.
                pass

        # 2) TOML-Config (Legacy)
        if os.path.isfile(config_toml_path):
            try:
                config_dict = toml.load(config_toml_path)
                project_section = config_dict.get("project", {})
                title_value = project_section.get("title")
                if isinstance(title_value, str) and title_value.strip():
                    self.project_title_var.set(title_value)
                    return
            except Exception:  # noqa: BLE001
                # Bei Problemen das Feld einfach leer lassen.
                pass

        # 3) Kein Config-File: Ordnername als Startwert.
        if not os.path.isfile(config_py_path) and not os.path.isfile(config_toml_path):
            folder_name = os.path.basename(workspace_dir.rstrip("/\\"))
            if folder_name:
                self.project_title_var.set(folder_name)

    def _open_config_dialog(self) -> None:
        """Open a dialog window to edit basic project config.

        Currently this provides a simple field for the project title and
        an "Erweitert" button that opens a raw editor for strictdoc.toml.
        """

        if not self._ensure_workspace():
            return

        # Refresh cached title suggestion from config (or folder name).
        self._load_project_title_from_config()
        initial_title = self.project_title_var.get().strip()

        dialog = tk.Toplevel(self)
        dialog.title("StrictDoc Konfiguration")
        dialog.transient(self)
        dialog.grab_set()

        padding = {"padx": 12, "pady": 6}

        ttk.Label(dialog, text="Projekttitel:").grid(
            row=0, column=0, sticky="w", **padding
        )
        title_var = tk.StringVar(value=initial_title)
        title_entry = ttk.Entry(dialog, textvariable=title_var, width=40)
        title_entry.grid(row=0, column=1, sticky="we", **padding)
        title_entry.focus_set()

        dialog.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="e", **padding)

        def on_save() -> None:
            self.project_title_var.set(title_var.get().strip())
            self._sync_project_config_from_ui()
            dialog.destroy()

        def on_cancel() -> None:
            dialog.destroy()

        def on_advanced() -> None:
            # Keep the simple title value as a suggestion for advanced mode.
            self.project_title_var.set(title_var.get().strip())
            dialog.destroy()
            self._open_advanced_config_editor()

        ttk.Button(button_frame, text="Erweitert ...", command=on_advanced).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(button_frame, text="Abbrechen", command=on_cancel).grid(
            row=0, column=1, padx=(0, 8)
        )
        ttk.Button(button_frame, text="Speichern", command=on_save).grid(
            row=0, column=2
        )

        dialog.bind("<Return>", lambda _event: on_save())
        dialog.bind("<Escape>", lambda _event: on_cancel())

    def _sync_project_config_from_ui(self) -> None:
        """Projekttitel aus dem Launcher in die Projektkonfiguration schreiben.

        Reihenfolge/Strategie:
        - Falls strictdoc_config.py existiert: Projekt-Titel dort aktualisieren
            (Standardfall für neue/aktualisierte Projekte).
        - Falls nur strictdoc.toml existiert: [project].title aktualisieren.
        - Falls weder strictdoc_config.py noch strictdoc.toml existiert:
            eine minimale strictdoc_config.py mit Projekt-Titel anlegen.
        """

        if not self._ensure_workspace():
            return

        title = self.project_title_var.get().strip()
        if not title:
            # Nichts zu tun, wenn kein Titel gesetzt ist.
            return

        workspace_dir_value = self.workspace_dir
        assert workspace_dir_value is not None
        workspace_dir = os.path.abspath(workspace_dir_value)
        config_py_path = os.path.join(workspace_dir, "strictdoc_config.py")
        config_toml_path = os.path.join(workspace_dir, "strictdoc.toml")

        # 1) strictdoc_config.py existiert -> versuchen, project_title dort zu aktualisieren.
        if os.path.isfile(config_py_path):
            try:
                with open(config_py_path, "r", encoding="utf8") as config_file:
                    config_text = config_file.read()

                # Einfache, konservative Ersetzung des Arguments project_title=...
                pattern = re.compile(
                    r"(project_title\s*=\s*)([\"'])(.*?)([\"'])",
                    re.DOTALL,
                )

                def _replace_title(match: re.Match[str]) -> str:  # type: ignore[name-defined]
                    prefix = match.group(1)
                    quote = match.group(2)
                    # vorhandenes Quote-Zeichen im Titel escapen
                    escaped_title = title.replace(quote, "\\" + quote)
                    return f"{prefix}{quote}{escaped_title}{quote}"

                new_text, count = pattern.subn(_replace_title, config_text, count=1)

                if count == 0:
                    messagebox.showinfo(
                        "Config nicht automatisch anpassbar",
                        (
                            "Der Projekttitel konnte in strictdoc_config.py nicht automatisch "
                            "gefunden/aktualisiert werden. Bitte im erweiterten Editor manuell anpassen."
                        ),
                    )
                    return

                with open(config_py_path, "w", encoding="utf8") as config_file:
                    config_file.write(new_text)

                self.set_status(f"Config gespeichert: {config_py_path}")
                return
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror(
                    "Config-Fehler",
                    (
                        "Die Python-Konfiguration (strictdoc_config.py) konnte nicht aktualisiert werden.\n\n"
                        f"Details: {exc}"
                    ),
                )
                return

        # 2) Nur strictdoc.toml existiert -> Legacy-Pfad beibehalten.
        if os.path.isfile(config_toml_path):
            try:
                config_dict = toml.load(config_toml_path)
                project_section = config_dict.get("project", {})
                project_section["title"] = title
                config_dict["project"] = project_section

                with open(config_toml_path, "w", encoding="utf8") as config_file:
                    toml.dump(config_dict, config_file)

                self.set_status(f"Config gespeichert: {config_toml_path}")
                return
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror(
                    "Config-Fehler",
                    (
                        "Die TOML-Konfiguration (strictdoc.toml) konnte nicht aktualisiert werden.\n\n"
                        f"Details: {exc}"
                    ),
                )
                return

        # 3) Kein Config-File -> neue strictdoc_config.py mit minimalem Inhalt erzeugen.
        try:
            config_py_template = (
                "from strictdoc.core.project_config import ProjectConfig\n\n"
                "\n"
                "def create_config() -> ProjectConfig:\n"
                "    return ProjectConfig(\n"
                f"        project_title=\"{title.replace('\\', '\\\\').replace('\"', r'\\\"')}\",\n"
                "    )\n"
            )
            with open(config_py_path, "w", encoding="utf8") as config_file:
                config_file.write(config_py_template)

            self.set_status(f"Config erstellt: {config_py_path}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(
                "Config-Fehler",
                (
                    "Die Python-Konfiguration (strictdoc_config.py) konnte nicht erzeugt werden.\n\n"
                    f"Details: {exc}"
                ),
            )

    def _open_advanced_config_editor(self) -> None:
        """Open a raw text editor for strictdoc.toml (advanced mode).

        Bevorzugt wird strictdoc_config.py (Python-Config); falls nur
        strictdoc.toml existiert, wird diese geöffnet. Neue Projekte
        erhalten standardmäßig eine Python-Config.
        """

        if not self._ensure_workspace():
            return

        workspace_dir_value = self.workspace_dir
        assert workspace_dir_value is not None
        workspace_dir = os.path.abspath(workspace_dir_value)
        config_py_path = os.path.join(workspace_dir, "strictdoc_config.py")
        config_toml_path = os.path.join(workspace_dir, "strictdoc.toml")

        # Entscheiden, welche Datei bearbeitet wird.
        target_path: str
        mode: str  # "py" oder "toml"
        if os.path.isfile(config_py_path):
            target_path = config_py_path
            mode = "py"
        elif os.path.isfile(config_toml_path):
            target_path = config_toml_path
            mode = "toml"
        else:
            # Neues Projekt: standardmäßig eine Python-Config vorschlagen.
            target_path = config_py_path
            mode = "py"

        initial_text = ""
        if os.path.isfile(target_path):
            try:
                with open(target_path, "r", encoding="utf8") as config_file:
                    initial_text = config_file.read()
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror(
                    "Config-Fehler",
                    (
                        f"Die bestehende Konfiguration ({os.path.basename(target_path)}) konnte nicht gelesen werden.\n\n"
                        f"Details: {exc}"
                    ),
                )
                return
        else:
            # Noch keine Datei vorhanden: sinnvollen Startinhalt erzeugen.
            title = self.project_title_var.get().strip()
            if not title:
                folder_name = os.path.basename(workspace_dir.rstrip("/\\"))
                title = folder_name

            if mode == "py":
                config_py_template = (
                    "from strictdoc.core.project_config import ProjectConfig\n\n"
                    "\n"
                    "def create_config() -> ProjectConfig:\n"
                    "    return ProjectConfig(\n"
                    f"        project_title=\"{title.replace('\\', '\\\\').replace('\"', r'\\\"')}\",\n"
                    "    )\n"
                )
                initial_text = config_py_template
            else:
                config_dict: dict[str, object] = {"project": {}}
                if title:
                    assert isinstance(config_dict["project"], dict)
                    config_dict["project"]["title"] = title
                initial_text = toml.dumps(config_dict)

        editor = tk.Toplevel(self)
        if mode == "py":
            editor.title("strictdoc_config.py – Erweitert")
        else:
            editor.title("strictdoc.toml – Erweitert")
        editor.transient(self)
        editor.grab_set()
        editor.geometry("800x500")

        text_widget = tk.Text(editor, wrap="none", font=("Consolas", 9))
        vscrollbar = ttk.Scrollbar(editor, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=vscrollbar.set)
        text_widget.grid(row=0, column=0, sticky="nsew")
        vscrollbar.grid(row=0, column=1, sticky="ns")

        editor.columnconfigure(0, weight=1)
        editor.rowconfigure(0, weight=1)

        text_widget.insert("1.0", initial_text)

        button_frame = ttk.Frame(editor)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="e", padx=12, pady=(6, 12))

        def on_save_advanced() -> None:
            new_text = text_widget.get("1.0", "end-1c")

            if mode == "py":
                # Nur Syntax prüfen, keine Ausführung.
                try:
                    compile(new_text, target_path, "exec")
                except SyntaxError as exc:
                    messagebox.showerror(
                        "Config-Fehler",
                        (
                            "strictdoc_config.py ist syntaktisch ungültig und wurde nicht gespeichert.\n\n"
                            f"Details: {exc}"
                        ),
                    )
                    return
            else:
                try:
                    # Validate TOML syntax before writing to disk.
                    toml.loads(new_text)
                except toml.TomlDecodeError as exc:  # type: ignore[attr-defined]
                    messagebox.showerror(
                        "Config-Fehler",
                        (
                            "strictdoc.toml ist syntaktisch ungültig und wurde nicht gespeichert.\n\n"
                            f"Details: {exc}"
                        ),
                    )
                    return

            try:
                with open(target_path, "w", encoding="utf8") as config_file:
                    config_file.write(new_text)
                self.set_status(f"Config gespeichert: {target_path}")
                editor.destroy()
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror(
                    "Config-Fehler",
                    (
                        f"{os.path.basename(target_path)} konnte nicht geschrieben werden.\n\n"
                        f"Details: {exc}"
                    ),
                )

        def on_cancel_advanced() -> None:
            editor.destroy()

        ttk.Button(button_frame, text="Abbrechen", command=on_cancel_advanced).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(button_frame, text="Speichern", command=on_save_advanced).grid(
            row=0, column=1
        )

        editor.bind("<Control-s>", lambda _event: on_save_advanced())
        editor.bind("<Escape>", lambda _event: on_cancel_advanced())

    def _python_executable(self) -> str:
        return sys.executable or "python"

    def _is_server_running(self) -> bool:
        return bool(self.server_process and self.server_process.poll() is None)

    def _set_server_running_ui(self) -> None:
        """Disable config/workspace changes while the server is running."""

        self.server_btn.configure(text="Stop server")
        self.open_browser_btn.configure(state="normal")
        self.export_btn.configure(state="disabled")

        # Lock all controls that would modify project layout/config
        # or export destination while the server is active.
        self.workspace_entry.configure(state="disabled")
        self.workspace_select_btn.configure(state="disabled")
        self.change_config_btn.configure(state="disabled")
        self.export_path_entry.configure(state="disabled")
        self.export_browse_btn.configure(state="disabled")
        self.export_format_combo.configure(state="disabled")

    def _set_server_stopped_ui(self) -> None:
        """Re-enable config/workspace controls when server is stopped."""

        self.server_btn.configure(text="Start server")
        self.open_browser_btn.configure(state="disabled")
        self.export_btn.configure(state="normal")

        self.workspace_entry.configure(state="normal")
        self.workspace_select_btn.configure(state="normal")
        self.change_config_btn.configure(state="normal")
        self.export_path_entry.configure(state="normal")
        self.export_browse_btn.configure(state="normal")
        self.export_format_combo.configure(state="readonly")

    def _toggle_server(self) -> None:
        """Toggle between starting and stopping the server based on state."""

        if self._is_server_running():
            # Server is running -> stop it.
            self.stop_server()
        else:
            # Server is not running -> start it.
            self.start_server()

    def _toggle_log(self) -> None:
        if self._log_visible.get():
            # Place log frame inside the server frame, below the buttons.
            self.log_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0, 5))
            self.minsize(self.min_width, self.min_height + 100)
        else:
            self.log_frame.grid_forget()
            self.minsize(self.min_width, self.min_height)

    # Export -------------------------------------------------------------
    def choose_export_path(self) -> None:
        """Let the user change the export target base directory.

        The effective export directory is always "<selected>/export",
        same behavior as before but now visible and editable.
        """

        # Prefer the current export path or the workspace as the
        # starting point in the dialog.
        initial_dir = None
        current_path = self.export_path_var.get()
        if current_path:
            initial_dir = os.path.dirname(current_path)
        elif self.workspace_dir:
            initial_dir = self.workspace_dir

        directory = filedialog.askdirectory(
            title="Basisordner für Export wählen",
            initialdir=initial_dir or os.getcwd(),
            mustexist=True,
        )
        if not directory:
            return

        new_export_path = os.path.join(directory, "export")
        self.export_path_var.set(new_export_path)
        self.set_status(f"Exportpfad gesetzt: {new_export_path}")

    def export_html(self) -> None:
        if not self._ensure_workspace():
            return

        # Resolve target directory. If the field is empty (e.g. user
        # hasn't changed anything and workspace was set before), fall
        # back to the default "<workspace>/export".
        output_dir = self.export_path_var.get().strip()
        if not output_dir:
            assert self.workspace_dir is not None
            output_dir = os.path.join(self.workspace_dir, "export")
            self.export_path_var.set(output_dir)

        export_format = self.export_format_var.get() or "html"

        cmd = [
            self._python_executable(),
            "-m",
            "strictdoc.cli.main",
            "export",
            self.workspace_dir,
            f"--formats={export_format}",
            "--output-dir",
            output_dir,
        ]

        # Log export start
        self._append_log(
            f"[EXPORT] format={export_format} target={output_dir}\n"
        )
        self.set_status("Export running...")

        def run_export() -> None:
            try:
                completed = subprocess.run(
                    cmd,
                    cwd=self.workspace_dir,
                    capture_output=True,
                    text=True,
                )
                if completed.returncode == 0:
                    self.after(0, lambda: self._export_ok(output_dir))
                else:
                    self.after(0, lambda: self._export_failed(completed))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._export_exception(exc))

        threading.Thread(target=run_export, daemon=True).start()

    def _export_ok(self, output_dir: str) -> None:
        export_format = self.export_format_var.get() or "html"
        self.set_status(f"Export completed: {output_dir}")
        self._append_log(
            f"[EXPORT OK] format={export_format} target={output_dir}\n"
        )
        messagebox.showinfo("Export", f"HTML export completed in:\n{output_dir}")

    def _export_failed(self, completed: subprocess.CompletedProcess) -> None:
        self.set_status("Export failed.")
        export_format = self.export_format_var.get() or "html"
        self._append_log(
            "[EXPORT FAILED] format="
            f"{export_format} rc={completed.returncode}\n"
        )
        if completed.stdout:
            self._append_log("[EXPORT STDOUT]\n" + completed.stdout + "\n")
        if completed.stderr:
            self._append_log("[EXPORT STDERR]\n" + completed.stderr + "\n")
        messagebox.showerror(
            "Export failed",
            "Return code: "
            f"{completed.returncode}\n\nSTDOUT:\n{completed.stdout}\n\nSTDERR:\n{completed.stderr}",
        )

    def _export_exception(self, exc: Exception) -> None:
        self.set_status("Export failed.")
        self._append_log(f"[EXPORT ERROR] {exc}\n")
        messagebox.showerror("Export error", str(exc))

        # Server -------------------------------------------------------------
    def start_server(self) -> None:
        if not self._ensure_workspace():
            return
        if self.server_process and self.server_process.poll() is None:
            messagebox.showinfo("Server running", "The server is already running.")
            return

        cmd = [
            self._python_executable(),
            "-m",
            "strictdoc.cli.main",
            "--debug",
            "server",
            self.workspace_dir,
            "--host",
            self.server_host,
            "--port",
            str(self.server_port),
        ]

        try:
            # Start the server in a background thread so that the UI isn't blocked.
            def run_server() -> None:
                try:
                    self.server_process = subprocess.Popen(
                        cmd,
                        cwd=self.workspace_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                    )
                    self._start_log_reader()
                    self._schedule_server_poll()
                except Exception as exc:  # noqa: BLE001
                    self.after(0, lambda: self._server_failed(exc))

            threading.Thread(target=run_server, daemon=True).start()

            # Update button/controls: now in "running" state.
            self._set_server_running_ui()
            self.set_status("Server started (see terminal for logs).")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error starting server", str(exc))
            self.set_status("Error starting server.")

    def _server_failed(self, exc: Exception) -> None:
        messagebox.showerror(
            "Server error", f"Server could not be started:\n{exc}"
        )
        self._set_server_stopped_ui()
        self.set_status("Failed to start server.")

    def stop_server(self) -> None:
        if not self._is_server_running():
            # Mark log reader thread as finished
            self._log_thread = None
            self._set_server_stopped_ui()
            self.set_status("Server is not running.")
            return

        try:
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            self.set_status("Server stopped.")
        except Exception:  # noqa: BLE001
            try:
                self.server_process.kill()
            except Exception:  # noqa: BLE001
                pass
            self.set_status("Server process was terminated.")
        finally:
            self.server_process = None
            self._set_server_stopped_ui()

    # Log handling ------------------------------------------------------
    def _start_log_reader(self) -> None:
        if not self.server_process or self.server_process.stdout is None:
            return

        def reader() -> None:
            assert self.server_process is not None
            assert self.server_process.stdout is not None
            for line in self.server_process.stdout:
                if line is None:
                    break
                self.after(0, lambda l=line: self._append_log(l))

        self._log_thread = threading.Thread(target=reader, daemon=True)
        self._log_thread.start()

    def _append_log(self, text: str) -> None:
        # keep log text widget editable only internally
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # Process monitoring -------------------------------------------------
    def _schedule_server_poll(self) -> None:
        """Schedule periodic checks to detect if the server exited on its own."""

        # Keep polling as long as we have a process object.
        if self.server_process is None:
            return
        self.after(1000, self._poll_server)

    def _poll_server(self) -> None:
        if self.server_process is None:
            return

        # If poll() is None, the process is still running.
        return_code = self.server_process.poll()
        if return_code is None:
            self._schedule_server_poll()
            return

        # Process has exited without going through stop_server().
        self.server_process = None
        self._set_server_stopped_ui()
        self._append_log(f"[SERVER EXITED] return code={return_code}\n")
        self.set_status("Server stopped.")

    def open_browser(self) -> None:
        """Open the default web browser pointing to the running server."""

        # Only meaningful if the server is actually running.
        if not (self.server_process and self.server_process.poll() is None):
            messagebox.showinfo(
                "Server not running",
                "Please start the server before opening the browser.",
            )
            return

        url = f"http://{self.server_host}:{self.server_port}/"
        try:
            webbrowser.open(url)
            self.set_status(f"Opening browser: {url}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Open browser failed", str(exc))

    # Shutdown -----------------------------------------------------------
    def on_close(self) -> None:
        try:
            self.stop_server()
        finally:
            self.destroy()


def main() -> None:
    app = StrictDocLauncher()
    app.mainloop()
