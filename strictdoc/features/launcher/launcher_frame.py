import os
import re
import json
import toml
import sys
import threading
import webbrowser
import subprocess
import tkinter as tk
import strictdoc.features.launcher.git_action as git_action
from tkinter import filedialog, messagebox, ttk
from importlib.resources import files
from typing import Any

STRICTDOC_RES = files("strictdoc")

LOGO = STRICTDOC_RES / "sw_logo.png"
ICON = STRICTDOC_RES / "export" / "html" / "_static" / "favicon.ico"

LOGO_PATH = str(LOGO)
ICON_PATH = str(ICON)

from strictdoc.commands.export import EXPORT_FORMATS
from strictdoc.helpers.module import import_from_path

if sys.platform == "win32":
    try:
        import winreg
    except Exception:  # noqa: BLE001
        winreg = None
else:
    winreg = None


class StrictDocLauncher(tk.Tk):
    help_links = {
        "User Guide StrictDoc": "https://strictdoc.readthedocs.io/en/stable/stable/docs/strictdoc_01_user_guide.html",
        "User Guide RST docutils": "https://docutils.sourceforge.io/docs/ref/rst/directives.html",
        "User Guide RST sphinx": "https://sphinx-tutorial.readthedocs.io/step-1/",
    }
    min_width = 420
    min_height = 230
    launcher_settings_filename = ".strictdoc_launcher.json"
    launcher_registry_key = r"Software\StrictDoc\Launcher"
    launcher_registry_value = "settings_json"
    max_recent_workspaces = 5
    log_text_width_chars = 160

    def __init__(self, initial_workspace: str | None = None, initial_open_browser: str | None = None) -> None:
        super().__init__()
        self.title("StrictDoc Launcher")

        # Try to set a window icon. On Windows, use the .ico file via
        # iconbitmap(); on other platforms fall back to PhotoImage if
        # the format is supported. This is best-effort only.
        try:
            if ICON_PATH.lower().endswith(".ico") and sys.platform == "win32":
                self.iconbitmap(ICON_PATH)
            else:
                self.iconphoto(False, tk.PhotoImage(file=ICON_PATH))
        except Exception:  # noqa: BLE001
            pass

        # Allow resizing; layout will use grid weights so that
        # text fields and the log grow, while buttons keep
        # their natural size.
        self.resizable(True, True)
        self.minsize(self.min_width, self.min_height)

        try:
            style = ttk.Style()
            style.configure("green.TButton", foreground="green")
            style.configure("red.TButton", foreground="red")
            # if "clam" in style.theme_names():
            #     style.theme_use("clam")
        except Exception:  # noqa: BLE001
            pass

        # Center the main window on the primary screen.
        try:
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            width = self._collapsed_min_width
            height = self._collapsed_min_height
            x = max(0, (screen_w - width) // 2)
            y = max(0, (screen_h - height) // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            # Best-effort only; do not fail the launcher if positioning fails.
            pass

        # State
        self.workspace_dir: str | None = None
        self._recent_workspaces: list[str] = self._load_recent_workspaces()
        self.server_process: subprocess.Popen | None = None
        self._log_thread: threading.Thread | None = None
        self._server_ready = False

        # Export state
        self._export_in_progress = False

        # Server connection settings used both for starting the server
        # and for constructing the browser URL.
        self.server_host: str = "127.0.0.1"
        self.server_port: int = 5111

        # Supported export formats (single selection), derived from
        # StrictDoc's own EXPORT_FORMATS constant so this list stays
        # in sync with the CLI.
        self._export_formats = list(EXPORT_FORMATS)
        self.export_format_var = tk.StringVar(value="html2pdf")

        # Optional project title, can be written into strictdoc.toml
        # in the selected workspace.
        self.project_title_var = tk.StringVar()

        # Export target path (full path). By default this will be
        # "<workspace>/export" once a workspace has been selected,
        # but the user can customize it via the Browse button.
        self.export_path_var = tk.StringVar()

        self._build_ui()

        # Restore persisted launcher preferences.
        remembered_open_browser = self._load_auto_open_browser_state()
        preferred_open_browser = (
            initial_open_browser
            if initial_open_browser is not None and str(initial_open_browser).strip()
            else remembered_open_browser
        )

        # Resolve workspace preference: explicit CLI argument wins over
        # persisted launcher preference from the previous run.
        remembered_workspace = self._load_last_workspace()
        preferred_workspace = (
            initial_workspace
            if initial_workspace is not None and str(initial_workspace).strip()
            else remembered_workspace
        )

        # Apply an initial/remembered workspace path, if available.
        if preferred_workspace is not None and str(preferred_workspace).strip():
            workspace_path = os.path.abspath(preferred_workspace)
            if os.path.isdir(workspace_path):
                self.workspace_dir = workspace_path
                if hasattr(self, "workspace_var"):
                    self.workspace_var.set(workspace_path)

                # Set default export path to "<workspace>/export".
                default_export_path = os.path.join(workspace_path, "export")
                if hasattr(self, "export_path_var"):
                    self.export_path_var.set(default_export_path)

                # Validate and load project metadata; this will also enable
                # workspace-dependent actions when the directory exists.
                self._ensure_workspace()
                self._load_project_title_from_config()
                self.set_status(f"Workspace set: {workspace_path}")

        # After the UI is built, enforce a minimum window size equal
        # to the requested size of the collapsed layout so widgets
        # cannot be clipped by resizing the window too small.
        self.update_idletasks()
        self._collapsed_min_width = self.winfo_reqwidth()
        self._collapsed_min_height = self.winfo_reqheight()
        self.minsize(self._collapsed_min_width, self._collapsed_min_height)

    # UI -----------------------------------------------------------------
    def _build_ui(self) -> None:
        PADDING: dict[str, Any] = {"padx": 5, "pady": 5}

        # Konfiguration des Haupt-Grids
        self.columnconfigure(0, weight=0) # Label Spalte (fest)
        self.columnconfigure(1, weight=1) # Entry Spalte (flexibel)
        self.columnconfigure(2, weight=0) # Button Spalte (fest)

        main = ttk.Frame(self)
        main.grid(row=0, column=0, sticky="nsew", **PADDING)

        # Title / header
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="we", **PADDING)
        header_frame.columnconfigure(0, weight=1)

        header = ttk.Label(
            header_frame, 
            text="StrictDoc Launcher", 
            font=("Segoe UI", 11, "bold")
        )
        header.grid(row=0, column=0, sticky="w")

        # Logo (rechts)
        self._logo_image = None
        if os.path.isfile(LOGO_PATH):
            try:
                self._logo_image = tk.PhotoImage(file=LOGO_PATH)
                self._logo_image = self._logo_image.subsample(3)
                logo_label = ttk.Label(self, image=self._logo_image)
                logo_label.grid(row=0, column=1, columnspan=2, sticky="e", **PADDING)
            except Exception:
                self._logo_image = None

        # Workspace selection
        ttk.Label(self, text="Workspace:").grid(row=1, column=0, sticky="w", **PADDING)

        self.workspace_var = tk.StringVar()
        self.workspace_entry = ttk.Combobox(
            self,
            width=40,
            textvariable=self.workspace_var,
            values=self._recent_workspaces,
        )

        self.workspace_entry.grid(row=1, column=1, sticky="we", **PADDING)
        # Pressing Enter in the workspace field validates and applies the path.
        self.workspace_entry.bind("<Return>", lambda _event: self._on_workspace_enter())
        self.workspace_entry.bind(
            "<<ComboboxSelected>>", lambda _event: self._on_workspace_enter()
        )

        self.workspace_select_btn = ttk.Button(self, text="Select ...", command=self.choose_workspace)
        self.workspace_select_btn.grid(row=1, column=2, sticky="we", **PADDING)

        # Maintenance controls
        maintenance_frame = ttk.LabelFrame(self, text="Maintenance")
        maintenance_frame.grid(row=2, column=0, columnspan=3, sticky="we", **PADDING)

        self.change_config_btn = ttk.Button(
            maintenance_frame,
            text="Change Config ...",
            command=self._open_config_dialog,
        )
        self.change_config_btn.grid(row=0, column=0, sticky="w", **PADDING)

        self.export_btn = ttk.Button(
            maintenance_frame,
            text="Export ...",
            command=self._open_export_dialog,
        )
        self.export_btn.grid(row=0, column=1, sticky="w", **PADDING)

        # Open Folder button: opens the selected workspace in the system file explorer.
        self.open_folder_btn = ttk.Button(
            maintenance_frame,
            text="Open Folder",
            command=self.open_workspace_in_explorer,
            state="disabled",
        )
        self.open_folder_btn.grid(row=0, column=2, sticky="e", **PADDING)

        # Repair ID button
        self.repair_id_btn = ttk.Button(
            maintenance_frame,
            text="Repair IDs",
            command=self._repair_ids,
        )

        self.repair_id_btn.grid(row=0, column=3, sticky="w", **PADDING)

        self.git_actions_dropdown = ttk.Menubutton(
            maintenance_frame,
            text="Git",
        )
        maintenance_frame.columnconfigure(4, weight=1)

        git_menu = tk.Menu(self.git_actions_dropdown, tearoff=0)
        git_actions = [
            ("Git Pull", lambda: git_action._git_pull(self)),
            (
                "Git Commit & Push",
                lambda: (git_action._git_commit(self), git_action._git_push(self)),
            ),
            ("Git Commit", lambda: git_action._git_commit(self)),
            ("Git Push", lambda: git_action._git_push(self)),
        ]
        for label, command in git_actions:
            git_menu.add_command(label=label, command=command)
        self.git_actions_dropdown["menu"] = git_menu
        self.git_actions_dropdown.grid(row=0, column=5, sticky="e", **PADDING)

        # Server controls
        work_frame = ttk.LabelFrame(self, text="Work")
        work_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", **PADDING)

        self.server_btn = ttk.Button(
            work_frame,
            text="Start server",
            style="green.TButton",
            command=self._toggle_server,
        )
        self.server_btn.grid(row=0, column=0, sticky="w", **PADDING)

        self.open_browser_btn = ttk.Button(
            work_frame,
            text="Open Browser",
            command=self.open_browser,
            state="disabled",
        )
        self.open_browser_btn.grid(row=0, column=1, sticky="w", **PADDING)

        # Auto-open browser option. Use a BooleanVar so checking the box
        # only sets the preference — it must not immediately open the browser.
        self.auto_open_browser_var = tk.BooleanVar(value=False)
        self.auto_open_browser = ttk.Checkbutton(
            work_frame,
            text="Auto open browser",
            variable=self.auto_open_browser_var,
            onvalue=True,
            offvalue=False,
            command=self._on_auto_open_browser_changed,
        )
        self.auto_open_browser.grid(row=0, column=2, sticky="w", **PADDING)

        # Help/documentation chooser: show a small '?' Menubutton on the
        # right side of the work frame that opens a menu with links.
        self.helper_docs_var = tk.StringVar(value="?")

        self.helper_docs_dropdown = ttk.Menubutton(
            work_frame,
            text="?",
        )

        # Create a Menu and attach it to the Menubutton. Each menu item
        # invokes _open_help_link with the selected name.
        menu = tk.Menu(self.helper_docs_dropdown, tearoff=0)
        for name in self.help_links.keys():
            menu.add_command(
                label=name,
                command=lambda n=name: self._open_help_link(n),
            )
        self.helper_docs_dropdown["menu"] = menu
        self.helper_docs_dropdown.grid(row=0, column=3, sticky="e", **PADDING)

        # Log header row
        log_header_frame = ttk.Frame(self)
        log_header_frame.grid(row=4, column=0, columnspan=3, sticky="we", **PADDING)

        self._log_expanded = False
        self.log_toggle_label = ttk.Label(
            log_header_frame,
            text="▶ Server log",
            cursor="hand2",
        )
        self.log_toggle_label.grid(row=0, column=0, sticky="w", **PADDING)
        self.log_toggle_label.bind("<Button-1>", lambda _event: self._toggle_log())

        self.clear_log_btn = ttk.Button(
            log_header_frame,
            text="Clear Log",
            command=self._clear_log,
        )
        self.clear_log_btn.grid(row=0, column=1, sticky="w", **PADDING)
        self.clear_log_btn.grid_remove()

        # Collapsible log area
        self.log_frame = ttk.Frame(self)
        self.log_text = tk.Text(
            self.log_frame,
            height=30,
            width=self.log_text_width_chars,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
        )
        scrollbar = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        # Configure tags for colored log output
        try:
            self.log_text.tag_configure("error", foreground="#c00000")
            self.log_text.tag_configure("warning", foreground="#b06a00")
            self.log_text.tag_configure("success", foreground="#007a00")
            self.log_text.tag_configure("info", foreground="#000000")
        except Exception:
            pass
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        # Layout weights
        work_frame.columnconfigure(0, weight=0)
        work_frame.columnconfigure(1, weight=0)
        work_frame.columnconfigure(2, weight=1)
        # Reserve a row for the collapsible log content (row 5). The log
        # header stays on row 4, the log content is placed on row 5 when
        # expanded so the header and controls remain visible.
        self.rowconfigure(5, weight=1)

        # Status bar
        ttk.Separator(self, orient="horizontal").grid(
            row=6, column=0, columnspan=3, sticky="we"
        )
        ttk.Label(self, text="Status:").grid(row=7, column=0, sticky="w")
        self.status_var = tk.StringVar(value="Ready.")
        status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            relief="sunken",
            borderwidth=1,
            anchor="w",
        )
        status_label.grid(
            row=7,
            column=1,
            sticky="we",
            **PADDING
        )

        version_text = f"StrictDoc {self._get_strictdoc_version()}"
        version_label = ttk.Label(self, text=version_text, anchor="e")
        version_label.grid(row=7, column=2, sticky="e", **PADDING)

        # Clean up on close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # Helpers ------------------------------------------------------------
    def set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.update_idletasks()

    def _open_help_link(self, selection: str | None = None) -> None:
        """Open the selected help/documentation link in the default browser."""
        sel = selection or getattr(self, "helper_docs_var", tk.StringVar()).get()
        if not sel:
            return
        url = self.help_links.get(sel)
        if not url:
            messagebox.showinfo("Help", "No link available for the selected item.")
            return
        try:
            webbrowser.open(url)
            self.set_status(f"Opening help: {sel}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Open help failed", str(exc))

    def _get_strictdoc_version(self) -> str:
        try:
            import strictdoc  # type: ignore[import]

            return strictdoc.__version__
        except Exception:
            return "unknown"

    def _launcher_settings_path(self) -> str:
        return os.path.join(
            os.path.expanduser("~"),
            self.launcher_settings_filename,
        )

    def _load_launcher_settings(self) -> dict[str, object]:
        if sys.platform == "win32" and winreg is not None:
            try:
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    self.launcher_registry_key,
                    0,
                    winreg.KEY_READ,
                ) as key:
                    raw_value, _reg_type = winreg.QueryValueEx(
                        key, self.launcher_registry_value
                    )
                    if isinstance(raw_value, str):
                        loaded = json.loads(raw_value)
                        if isinstance(loaded, dict):
                            return loaded
            except Exception:  # noqa: BLE001
                return {}
            return {}

        settings_path = self._launcher_settings_path()
        if not os.path.isfile(settings_path):
            return {}
        try:
            with open(settings_path, "r", encoding="utf8") as settings_file:
                loaded = json.load(settings_file)
            if isinstance(loaded, dict):
                return loaded
        except Exception:  # noqa: BLE001
            return {}
        return {}

    def _save_launcher_settings(self, settings: dict[str, object]) -> None:
        if sys.platform == "win32" and winreg is not None:
            try:
                payload = json.dumps(settings)
                with winreg.CreateKey(
                    winreg.HKEY_CURRENT_USER,
                    self.launcher_registry_key,
                ) as key:
                    winreg.SetValueEx(
                        key,
                        self.launcher_registry_value,
                        0,
                        winreg.REG_SZ,
                        payload,
                    )
            except Exception:  # noqa: BLE001
                pass
            return

        try:
            settings_path = self._launcher_settings_path()
            with open(settings_path, "w", encoding="utf8") as settings_file:
                json.dump(settings, settings_file, ensure_ascii=False, indent=2)
        except Exception:  # noqa: BLE001
            pass

    def _load_last_workspace(self) -> str | None:
        settings = self._load_launcher_settings()
        launcher_section = settings.get("launcher", {})
        if isinstance(launcher_section, dict):
            value = launcher_section.get("last_workspace")
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _load_recent_workspaces(self) -> list[str]:
        settings = self._load_launcher_settings()
        launcher_section = settings.get("launcher", {})
        if not isinstance(launcher_section, dict):
            return []

        value = launcher_section.get("recent_workspaces")
        if not isinstance(value, list):
            return []

        result: list[str] = []
        for entry in value:
            if not isinstance(entry, str):
                continue
            normalized = entry.strip()
            if not normalized:
                continue
            normalized = os.path.abspath(normalized)
            if normalized in result:
                continue
            result.append(normalized)
            if len(result) >= self.max_recent_workspaces:
                break
        return result

    def _refresh_recent_workspaces_ui(self) -> None:
        if hasattr(self, "workspace_entry"):
            self.workspace_entry.configure(values=self._recent_workspaces)

    def _save_last_workspace(self, workspace_path: str) -> None:
        settings = self._load_launcher_settings()
        launcher_section = settings.get("launcher", {})
        if not isinstance(launcher_section, dict):
            launcher_section = {}

        normalized_workspace = os.path.abspath(workspace_path)
        previous_workspaces = launcher_section.get("recent_workspaces", [])
        previous_recent: list[str] = []
        if isinstance(previous_workspaces, list):
            for entry in previous_workspaces:
                if not isinstance(entry, str):
                    continue
                normalized_entry = entry.strip()
                if not normalized_entry:
                    continue
                normalized_entry = os.path.abspath(normalized_entry)
                if normalized_entry in previous_recent:
                    continue
                previous_recent.append(normalized_entry)

        recent_workspaces = [
            normalized_workspace,
            *[path for path in previous_recent if path != normalized_workspace],
        ][: self.max_recent_workspaces]

        launcher_section["last_workspace"] = normalized_workspace
        launcher_section["recent_workspaces"] = recent_workspaces
        settings["launcher"] = launcher_section
        self._save_launcher_settings(settings)

        self._recent_workspaces = recent_workspaces
        self._refresh_recent_workspaces_ui()

    def _load_auto_open_browser_state(self) -> None:
        settings = self._load_launcher_settings()
        launcher_section = settings.get("launcher", {})
        if not isinstance(launcher_section, dict):
            return

        value = launcher_section.get("auto_open_browser")
        if isinstance(value, bool) and hasattr(self, "auto_open_browser_var"):
            self.auto_open_browser_var.set(value)

    def _save_auto_open_browser_state(self) -> None:
        settings = self._load_launcher_settings()
        launcher_section = settings.get("launcher", {})
        if not isinstance(launcher_section, dict):
            launcher_section = {}
        launcher_section["auto_open_browser"] = bool(
            self.auto_open_browser_var.get() if hasattr(self, "auto_open_browser_var") else False
        )
        settings["launcher"] = launcher_section
        self._save_launcher_settings(settings)

    def _on_auto_open_browser_changed(self) -> None:
        self._save_auto_open_browser_state()

    def _busy_cursor_name(self) -> str:
        if sys.platform == "win32":
            return "wait"
        return "watch"

    def _start_export_progress(self) -> None:
        """Show and start the indeterminate export progress bar."""
        self._export_in_progress = True

        self.export_btn.configure(state="disabled", text="Export läuft...")

        # Disable controls that should not be changed during export.
        self.workspace_entry.configure(state="disabled")
        self.workspace_select_btn.configure(state="disabled")
        self.change_config_btn.configure(state="disabled")
        self.open_folder_btn.configure(state="disabled")
        self.repair_id_btn.configure(state="disabled")
        self.server_btn.configure(state="disabled")
        self.open_browser_btn.configure(state="disabled")

        try:
            self.configure(cursor=self._busy_cursor_name())
        except Exception:  # noqa: BLE001
            pass

    def _stop_export_progress(self) -> None:
        """Stop and hide the export progress bar."""
        self._export_in_progress = False

        try:
            self.configure(cursor="")
        except Exception:  # noqa: BLE001
            pass

        # Restore UI depending on server state.
        if self._is_server_running():
            self._set_server_running_ui()
        else:
            self._set_server_stopped_ui()

    def choose_workspace(self) -> None:
        """Open a directory selection dialog to choose the StrictDoc workspace."""
        directory = filedialog.askdirectory(title="Select StrictDoc workspace")
        if not directory:
            return

        self.workspace_dir = directory
        self.workspace_var.set(directory)

        default_export_path = os.path.join(directory, "export")
        self.export_path_var.set(default_export_path)

        self._ensure_workspace()
        self._load_project_title_from_config()
        self.set_status(f"Workspace set: {directory}")

    def _on_workspace_enter(self) -> None:
        """Handle Enter key in the workspace field."""
        if not self._ensure_workspace():
            return

        assert self.workspace_dir is not None
        directory = self.workspace_dir

        default_export_path = os.path.join(directory, "export")
        self.export_path_var.set(default_export_path)
        self._load_project_title_from_config()
        self.set_status(f"Workspace set: {directory}")

    def _ensure_workspace(self) -> bool:
        """Validate and synchronize the workspace path from the entry field."""
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

        self.workspace_dir = os.path.abspath(self.workspace_dir)
        if hasattr(self, "workspace_var"):
            self.workspace_var.set(self.workspace_dir)
        self._save_last_workspace(self.workspace_dir)

        if hasattr(self, "open_folder_btn"):
            self.open_folder_btn.configure(state="normal")
        return True

    def open_workspace_in_explorer(self) -> None:
        if not self._ensure_workspace():
            return
        assert self.workspace_dir is not None
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
        """Best-effort: pre-fill project title from configuration.

        Order:
        1. strictdoc_config.py (Python config) via create_config().project_title
        2. strictdoc.toml ([project].title)
        3. Workspace folder name as fallback suggestion
        """
        self.project_title_var.set("")
        if not self.workspace_dir:
            return

        workspace_dir = os.path.abspath(self.workspace_dir)
        config_py_path = os.path.join(workspace_dir, "strictdoc_config.py")
        config_toml_path = os.path.join(workspace_dir, "strictdoc.toml")

        # 1) Prefer Python config
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
                pass

        # 2) TOML config (legacy)
        if os.path.isfile(config_toml_path):
            try:
                config_dict = toml.load(config_toml_path)
                project_section = config_dict.get("project", {})
                title_value = project_section.get("title")
                if isinstance(title_value, str) and title_value.strip():
                    self.project_title_var.set(title_value)
                    return
            except Exception:  # noqa: BLE001
                # On any error, leave the field empty.
                pass

        # 3) No config file: use folder name as initial value.
        if not os.path.isfile(config_py_path) and not os.path.isfile(config_toml_path):
            folder_name = os.path.basename(workspace_dir.rstrip("/\\"))
            if folder_name:
                self.project_title_var.set(folder_name)

    def _run_export_thread(self, output_dir, export_format, on_success, on_error):
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

        def worker():
            try:
                completed = subprocess.run(
                    cmd,
                    cwd=self.workspace_dir,
                    capture_output=True,
                    text=True,
                )

                if completed.returncode == 0:
                    self.after(0, on_success)
                else:
                    error_text = completed.stderr or completed.stdout or ""
                    msg = f"RC={completed.returncode}\n\n{error_text}"
                    self.after(0, lambda: on_error(msg))

            except Exception as exc:
                self.after(0, lambda: on_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _open_export_dialog(self) -> None:
        """Open a dialog to select export format and target directory."""

        if not self._ensure_workspace():
            return

        # Ensure we have a sensible default export path when the dialog opens.
        if not self.export_path_var.get().strip() and self.workspace_dir:
            default_export_path = os.path.join(self.workspace_dir, "export")
            self.export_path_var.set(default_export_path)

        dialog = tk.Toplevel(self)
        dialog.title("Export")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.columnconfigure(0, weight=1)

        padding: dict[str, Any] = {"padx": 6, "pady": 3}

        content = ttk.Frame(dialog)
        content.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        content.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=1, column=0, sticky="e", padx=8, pady=(0, 8))

        # Reserve vertical space for the progress bar so it can appear
        # later without resizing the dialog.
        progress_area = ttk.Frame(content, height=20)
        progress_area.grid(row=2, column=0, columnspan=3, sticky="we", pady=(6, 0))
        progress_area.grid_propagate(False)
        progress_area.columnconfigure(0, weight=1)

        # Export format -------------------------------------------------
        ttk.Label(content, text="Format:").grid(row=0, column=0, sticky="w", **padding)

        # Make sure a valid format is selected.
        if self.export_format_var.get() not in self._export_formats:
            if self._export_formats:
                self.export_format_var.set(self._export_formats[0])

        format_combo = ttk.Combobox(
            content,
            textvariable=self.export_format_var,
            values=self._export_formats,
            state="readonly",
            width=15,
        )
        format_combo.grid(row=0, column=1, sticky="we", **padding)

        # Export target path -------------------------------------------
        ttk.Label(content, text="Path:").grid(row=1, column=0, sticky="w", **padding)

        path_entry = ttk.Entry(content, textvariable=self.export_path_var, width=40)
        path_entry.grid(row=1, column=1, sticky="we", **padding)

        browse_btn = ttk.Button(content, text="Browse ...", command=self.choose_export_path)
        browse_btn.grid(row=1, column=2, **padding)

        # ProgressBar  -------------------------------------------------
        progress = ttk.Progressbar(progress_area, mode="indeterminate")
        progress.grid(row=0, column=0, sticky="we")
        progress.grid_remove()

        # Action buttons -----------------------------------------------
        export_btn = ttk.Button(button_frame, text="Export")
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)

        export_btn.grid(row=0, column=0, padx=(0, 8))
        cancel_btn.grid(row=0, column=1)

        # Status Bar ---------------------------------------------------
        ttk.Separator(dialog, orient="horizontal").grid(
            row=2, column=0, sticky="we", padx=8
        )

        status_frame = ttk.Frame(dialog)
        status_frame.grid(row=3, column=0, sticky="we", padx=8, pady=(6, 8))
        status_frame.columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky="w")
        status_var = tk.StringVar(value="Ready.")
        status_label = ttk.Label(
            status_frame,
            textvariable=status_var,
            relief="sunken",
            borderwidth=1,
            anchor="w",
        )
        status_label.grid(row=0, column=1, sticky="we", padx=(6, 0))

        # Freeze the dialog to a typical fixed-size dialog behavior.
        dialog.update_idletasks()
        dialog_width = dialog.winfo_reqwidth()
        dialog_height = dialog.winfo_reqheight()
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        dialog_x = parent_x + max(0, (parent_width - dialog_width) // 2)
        dialog_y = parent_y + max(0, (parent_height - dialog_height) // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{dialog_x}+{dialog_y}")

        # Export-Logik im Dialog
        def start_export():
            if self._export_in_progress:
                return
            self._export_in_progress = True

            output_dir = self.export_path_var.get().strip()
            if not output_dir and self.workspace_dir:
                output_dir = os.path.join(self.workspace_dir, "export")
                self.export_path_var.set(output_dir)

            progress.grid()
            progress.start(10)

            export_btn.configure(state="disabled")
            cancel_btn.configure(state="disabled")

            status_var.set("Export running...")

            def on_export_success(output_dir: str) -> None:
                self._export_in_progress = False
                progress.stop()
                progress.grid_remove()
                status_var.set("Export finished.")
                dialog.destroy()

                if not messagebox.askyesno(
                    "Export",
                    f"Export completed in:\n{output_dir}\n\nOpen export folder?"
                ):
                    return

                try:
                    if sys.platform.startswith("win"):
                        os.startfile(output_dir)  # type: ignore[attr-defined]
                    elif sys.platform.startswith("darwin"):
                        subprocess.run(["open", output_dir], check=True)
                    else:
                        subprocess.run(["xdg-open", output_dir], check=True)
                except Exception as exc:
                    messagebox.showerror(
                        "Error opening folder",
                        f"The export folder could not be opened:\n{exc}",
                    )

            def on_export_error(msg: str) -> None:
                self._export_in_progress = False
                progress.stop()
                progress.grid_remove()
                export_btn.configure(state="normal")
                cancel_btn.configure(state="normal")
                status_var.set("Export failed.")
                messagebox.showerror("Export failed", msg)

            self._run_export_thread(
                output_dir=output_dir,
                export_format=self.export_format_var.get(),
                on_success=lambda: on_export_success(output_dir),
                on_error=on_export_error,
            )

        export_btn.configure(command=start_export)

        dialog.bind("<Return>", lambda _e: start_export())
        dialog.bind("<Escape>", lambda _e: dialog.destroy())

    def _open_config_dialog(self) -> None:
        """Open a dialog window to edit basic project configuration.

        Currently this provides a simple field for the project title and
        an "Advanced" button that opens a raw editor for strictdoc config.
        """

        if not self._ensure_workspace():
            return

        # Refresh cached title suggestion from config (or folder name).
        self._load_project_title_from_config()
        initial_title = self.project_title_var.get().strip()

        dialog = tk.Toplevel(self)
        dialog.title("StrictDoc Configuration")
        dialog.transient(self)
        dialog.grab_set()

        padding: dict[str, Any] = {"padx": 12, "pady": 6}

        ttk.Label(dialog, text="Project title:").grid(
            row=0, column=0, sticky="w", **padding
        )
        title_var = tk.StringVar(value=initial_title)
        title_entry = ttk.Entry(dialog, textvariable=title_var, width=40)
        title_entry.grid(row=0, column=1, sticky="we", **padding)
        title_entry.focus_set()

        dialog.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=1, column=0, columnspan=3, sticky="e", **padding)

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

        ttk.Button(button_frame, text="Advanced ...", command=on_advanced).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(button_frame, text="Cancel", command=on_cancel).grid(
            row=0, column=1, padx=(0, 8)
        )
        ttk.Button(button_frame, text="Save", command=on_save).grid(
            row=0, column=2
        )

        dialog.bind("<Return>", lambda _event: on_save())
        dialog.bind("<Escape>", lambda _event: on_cancel())

    def _sync_project_config_from_ui(self) -> None:
        """Write the project title from the launcher into the project configuration.

        Strategy / precedence:
        - If strictdoc_config.py exists: update project_title there
          (default for new/updated projects).
        - If only strictdoc.toml exists: update [project].title there.
        - If neither strictdoc_config.py nor strictdoc.toml exists:
          create a minimal strictdoc_config.py with the project title.
        """

        if not self._ensure_workspace():
            return

        title = self.project_title_var.get().strip()
        if not title:
            # Nothing to do if no title is set.
            return

        workspace_dir_value = self.workspace_dir
        assert workspace_dir_value is not None
        workspace_dir = os.path.abspath(workspace_dir_value)
        config_py_path = os.path.join(workspace_dir, "strictdoc_config.py")
        config_toml_path = os.path.join(workspace_dir, "strictdoc.toml")

        # 1) strictdoc_config.py exists -> try to update project_title there.
        if os.path.isfile(config_py_path):
            try:
                with open(config_py_path, "r", encoding="utf8") as config_file:
                    config_text = config_file.read()

                # Simple, conservative replacement of the project_title= argument.
                pattern = re.compile(
                    r"(project_title\s*=\s*)([\"'])(.*?)([\"'])",
                    re.DOTALL,
                )

                def _replace_title(match: re.Match[str]) -> str:  # type: ignore[name-defined]
                    prefix = match.group(1)
                    quote = match.group(2)
                    # Escape any existing quote characters in the title.
                    escaped_title = title.replace(quote, "\\" + quote)
                    return f"{prefix}{quote}{escaped_title}{quote}"

                new_text, count = pattern.subn(_replace_title, config_text, count=1)

                if count == 0:
                    messagebox.showinfo(
                        "Config not automatically adjustable",
                        (
                            "The project title in strictdoc_config.py could not be "
                            "found/updated automatically. Please adjust it manually "
                            "in the advanced editor."
                        ),
                    )
                    return

                with open(config_py_path, "w", encoding="utf8") as config_file:
                    config_file.write(new_text)

                self.set_status(f"Config gespeichert: {config_py_path}")
                return
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror(
                    "Configuration error",
                    (
                        "The Python configuration (strictdoc_config.py) could not be updated.\n\n"
                        f"Details: {exc}"
                    ),
                )
                return

        # 2) Only strictdoc.toml exists -> keep legacy path.
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
                    "Configuration error",
                    (
                        "The TOML configuration (strictdoc.toml) could not be updated.\n\n"
                        f"Details: {exc}"
                    ),
                )
                return

        # 3) No config file -> create new strictdoc_config.py with minimal content.
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

            self.set_status(f"Config created: {config_py_path}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(
                "Configuration error",
                (
                    "The Python configuration (strictdoc_config.py) could not be created.\n\n"
                    f"Details: {exc}"
                ),
            )

    def _open_advanced_config_editor(self) -> None:
        """Open a raw text editor for strictdoc.toml (advanced mode).

        strictdoc_config.py (Python config) is preferred; if only
        strictdoc.toml exists, that file is opened instead. New projects
        use a Python configuration by default.
        """

        if not self._ensure_workspace():
            return

        workspace_dir_value = self.workspace_dir
        assert workspace_dir_value is not None
        workspace_dir = os.path.abspath(workspace_dir_value)
        config_py_path = os.path.join(workspace_dir, "strictdoc_config.py")
        config_toml_path = os.path.join(workspace_dir, "strictdoc.toml")

        # Decide which file should be edited.
        target_path: str
        mode: str  # "py" or "toml"
        if os.path.isfile(config_py_path):
            target_path = config_py_path
            mode = "py"
        elif os.path.isfile(config_toml_path):
            target_path = config_toml_path
            mode = "toml"
        else:
            # New project: by default, suggest a Python config file.
            target_path = config_py_path
            mode = "py"

        initial_text = ""
        if os.path.isfile(target_path):
            try:
                with open(target_path, "r", encoding="utf8") as config_file:
                    initial_text = config_file.read()
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror(
                    "Configuration error",
                    (
                        f"The existing configuration ({os.path.basename(target_path)}) could not be read.\n\n"
                        f"Details: {exc}"
                    ),
                )
                return
        else:
            # No file yet: create a reasonable default content.
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
            editor.title("strictdoc_config.py – Advanced")
        else:
            editor.title("strictdoc.toml – Advanced")
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
        button_frame.grid(row=1, column=0, columnspan=3, sticky="e", padx=12, pady=(6, 12))

        def on_save_advanced() -> None:
            new_text = text_widget.get("1.0", "end-1c")

            if mode == "py":
                # Only check syntax, do not execute.
                try:
                    compile(new_text, target_path, "exec")
                except SyntaxError as exc:
                    messagebox.showerror(
                        "Configuration error",
                        (
                            "strictdoc_config.py is syntactically invalid and was not saved.\n\n"
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
                        "Configuration error",
                        (
                            "strictdoc.toml is syntactically invalid and was not saved.\n\n"
                            f"Details: {exc}"
                        ),
                    )
                    return

            try:
                with open(target_path, "w", encoding="utf8") as config_file:
                    config_file.write(new_text)
                self.set_status(f"Config saved: {target_path}")
                editor.destroy()
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror(
                    "Configuration error",
                    (
                        f"{os.path.basename(target_path)} could not be written.\n\n"
                        f"Details: {exc}"
                    ),
                )

        def on_cancel_advanced() -> None:
            editor.destroy()

        ttk.Button(button_frame, text="Cancel", command=on_cancel_advanced).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(button_frame, text="Save", command=on_save_advanced).grid(
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

        self.server_btn.configure(text="Stop server", style="red.TButton")
        self.open_browser_btn.configure(state="disabled", style="green.TButton")
        self.auto_open_browser.configure(state="disabled")
        self.export_btn.configure(state="disabled")
        self._server_ready = False

        # Lock all controls that would modify project layout/config
        # while the server is active.
        self.workspace_entry.configure(state="disabled")
        self.workspace_select_btn.configure(state="disabled")
        self.change_config_btn.configure(state="disabled")
        self.open_folder_btn.configure(state="disabled")
        self.repair_id_btn.configure(state="disabled")

    def _set_server_stopped_ui(self) -> None:
        """Re-enable config/workspace controls when server is stopped."""

        self.server_btn.configure(text="Start server", style="green.TButton")
        self.open_browser_btn.configure(state="disabled", style="red.TButton")
        self.auto_open_browser.configure(state="normal")
        self.export_btn.configure(state="normal")
        self._server_ready = False

        self.workspace_entry.configure(state="normal")
        self.workspace_select_btn.configure(state="normal")
        self.change_config_btn.configure(state="normal")
        self.open_folder_btn.configure(state="normal")
        self.repair_id_btn.configure(state="normal")

    def _toggle_server(self) -> None:
        """Toggle between starting and stopping the server based on state."""

        if self._is_server_running():
            # Server is running -> stop it.
            self.stop_server()
        else:
            # Server is not running -> start it.
            self.start_server()

    def _toggle_log(self) -> None:
        """Expand/collapse the server log area and adjust window height.

        When the log is expanded, the window grows as needed to fit
        the additional content and the minimum size is updated so the
        content cannot be clipped. When the log is collapsed again,
        the minimum size is reset to the collapsed layout and the
        window height is shrunk back to that baseline.
        """

        self._log_expanded = not self._log_expanded
        if self._log_expanded:
            # Place log frame in the main grid, below the log header (row 5).
            self.log_frame.grid(
                row=5,
                column=0,
                columnspan=3,
                sticky="nsew",
                padx=5,
                pady=(0, 5),
            )
            self.log_toggle_label.configure(text="▼ Server log")
            self.clear_log_btn.grid()

            # Recompute requested size with log visible. Width grows only
            # as needed, while the collapsed size stays compact.
            self.update_idletasks()
            req_width = self.winfo_reqwidth()
            req_height = self.winfo_reqheight()
            target_width = max(self._collapsed_min_width, req_width)
            self.minsize(target_width, req_height)

            # Ensure the current window is large enough in both dimensions.
            cur_width = self.winfo_width()
            cur_height = self.winfo_height()
            target_width = max(cur_width, req_width)
            target_height = max(cur_height, req_height)
            self.geometry(f"{target_width}x{target_height}")
        else:
            self.log_frame.grid_forget()
            self.log_toggle_label.configure(text="▶ Server log")
            self.clear_log_btn.grid_remove()

            # Recompute requested height of the collapsed layout. Width stays
            # fixed at the precomputed minimum so the window never shrinks
            # horizontally when the log is toggled.
            self.update_idletasks()
            req_height = self.winfo_reqheight()
            self._collapsed_min_height = req_height
            self.minsize(self._collapsed_min_width, req_height)

            self.geometry(f"{self._collapsed_min_width}x{req_height}")

    def _repair_ids(self) -> None:
        """Run StrictDoc's auto-UID management on the current workspace.

        This wraps the CLI command

            strictdoc manage auto-uid <workspace> --include-sections

        and runs it in a background thread while streaming output to
        the launcher log area.
        """

        if not self._ensure_workspace():
            return

        assert self.workspace_dir is not None
        workspace_dir = self.workspace_dir

        cmd = [
            self._python_executable(),
            "-m",
            "strictdoc.cli.main",
            "manage",
            "auto-uid",
            workspace_dir,
            "--include-sections",
        ]

        self._append_log(
            f"[REPAIR] strictdoc manage auto-uid {workspace_dir}\n"
        )
        self.set_status("Repairing IDs...")

        def run_repair() -> None:
            try:
                completed = subprocess.run(
                    cmd,
                    cwd=workspace_dir,
                    capture_output=True,
                    text=True,
                )
            except Exception as exc:  # noqa: BLE001

                def _handle_exc() -> None:
                    self.set_status("Repair failed.")
                    self._append_log(f"[REPAIR ERROR] {exc}\n")
                    messagebox.showerror("Repair IDs error", str(exc))

                self.after(0, _handle_exc)
                return

            def _handle_result() -> None:
                if completed.returncode == 0:
                    self.set_status("Repair completed.")
                    self._append_log("[REPAIR OK] IDs repaired successfully.\n")
                    if completed.stdout:
                        self._append_log(
                            "[REPAIR STDOUT]\n" + completed.stdout + "\n"
                        )
                    messagebox.showinfo(
                        "Repair IDs", "ID repair completed successfully."
                    )
                else:
                    self.set_status("Repair failed.")
                    self._append_log(
                        "[REPAIR FAILED] rc="
                        f"{completed.returncode}\n"
                    )
                    if completed.stdout:
                        self._append_log(
                            "[REPAIR STDOUT]\n" + completed.stdout + "\n"
                        )
                    if completed.stderr:
                        self._append_log(
                            "[REPAIR STDERR]\n" + completed.stderr + "\n"
                        )
                    messagebox.showerror(
                        "Repair IDs failed",
                        "Return code: "
                        f"{completed.returncode}\n\nSTDOUT:\n{completed.stdout}\n\nSTDERR:\n{completed.stderr}",
                    )

            self.after(0, _handle_result)

        threading.Thread(target=run_repair, daemon=True).start()

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
            title="Select base folder for export",
            initialdir=initial_dir or os.getcwd(),
            mustexist=True,
        )
        if not directory:
            return

        new_export_path = os.path.join(directory, "export")
        self.export_path_var.set(new_export_path)
        self.set_status(f"Export path set: {new_export_path}")

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

        process = self.server_process
        if process is None:
            self._set_server_stopped_ui()
            self.set_status("Server is not running.")
            return

        try:
            process.terminate()
            process.wait(timeout=5)
            self.set_status("Server stopped.")
        except Exception:  # noqa: BLE001
            try:
                process.kill()
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
                self.after(0, lambda l=line: self._handle_server_log_line(l))

        self._log_thread = threading.Thread(target=reader, daemon=True)
        self._log_thread.start()

    def _handle_server_log_line(self, text: str) -> None:
        self._append_log(text)

        # If the server outputs an error/exception/traceback, auto-expand
        # the log area so the user can inspect the failure immediately.
        try:
            normalized = text.strip().lower()
            # Detect common error indicators. Use word-boundary for 'error'
            # to reduce false positives.
            if (
                "traceback" in normalized
                or "exception" in normalized
                or "failed" in normalized
                or re.search(r"\berror\b", normalized)
            ):
                try:
                    if not self._log_expanded:
                        self._toggle_log()
                    # Try to bring the window to the front to draw attention.
                    try:
                        self.lift()
                        self.focus_force()
                        try:
                            # Temporarily set topmost to ensure visibility on some platforms.
                            self.attributes("-topmost", True)
                            self.after(200, lambda: self.attributes("-topmost", False))
                        except Exception:
                            pass
                    except Exception:
                        pass
                    self.set_status("Server error detected. See log.")
                except Exception:
                    pass
        except Exception:
            # Never let log-handling failures crash the launcher.
            pass

        if self._server_ready:
            return

        normalized = text.strip().lower()
        ready_markers = (
            "uvicorn running on",
            "application startup complete",
            "started server process",
        )
        if any(marker in normalized for marker in ready_markers):
            self._server_ready = True
            self.open_browser_btn.configure(state="normal", style="green.TButton")
            self.set_status("Server is ready.")
            try:
                if getattr(self, "auto_open_browser_var", None) and self.auto_open_browser_var.get():
                    # Ensure we call open_browser on the main thread.
                    self.after(100, self.open_browser)
            except Exception:
                pass

    def _append_log(self, text: str) -> None:
        # keep log text widget editable only internally
        try:
            self.log_text.configure(state="normal")

            normalized = text.strip().lower()
            tag = None
            if "traceback" in normalized or "exception" in normalized or re.search(r"\berror\b", normalized) or "failed" in normalized:
                tag = "error"
            elif "warning" in normalized or "warn" in normalized:
                tag = "warning"
            elif "started" in normalized or "ok" in normalized or "completed" in normalized:
                tag = "success"
            else:
                tag = "info"

            if tag:
                try:
                    self.log_text.insert("end", text, (tag,))
                except Exception:
                    # Fall back to plain insert if tag insertion fails.
                    self.log_text.insert("end", text)
            else:
                self.log_text.insert("end", text)

            self.log_text.see("end")
        finally:
            try:
                self.log_text.configure(state="disabled")
            except Exception:
                pass

    def _clear_log(self) -> None:
        # Clear all text from the log widget
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
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
        if not self._server_ready:
            messagebox.showinfo(
                "Server not ready",
                "Please wait until the server has finished starting.",
            )
            return

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


def main(workspace: str | None = None) -> None:
    open_browser_state = None
    app = StrictDocLauncher(initial_workspace=workspace, initial_open_browser=open_browser_state)
    app.mainloop()
