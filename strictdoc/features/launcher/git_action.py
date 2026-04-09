import subprocess
import threading
from tkinter import messagebox, simpledialog


def _ensure_git_workspace(self) -> bool:
        if not self._ensure_workspace():
            return False

        assert self.workspace_dir is not None
        try:
            completed = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Git error", str(exc))
            return False

        if completed.returncode != 0 or completed.stdout.strip().lower() != "true":
            messagebox.showerror(
                "Git repository missing",
                "The selected workspace is not a Git repository.",
            )
            return False

        return True

def _run_git_action(self, action_name: str, git_args: list[str]) -> None:
        """Run a Git command in the current workspace in the background."""

        if not self._ensure_git_workspace():
            return

        assert self.workspace_dir is not None
        workspace_dir = self.workspace_dir
        git_command_text = "git " + " ".join(git_args)
        self.set_status(f"{action_name}...")
        self._append_log(f"[{action_name.upper()}] {git_command_text}\n")

        def run_git_action() -> None:
            try:
                completed = subprocess.run(
                    ["git", *git_args],
                    cwd=workspace_dir,
                    capture_output=True,
                    text=True,
                )
            except Exception as exc:  # noqa: BLE001

                def _handle_exc() -> None:
                    self.set_status(f"{action_name} failed.")
                    self._append_log(f"[{action_name.upper()} ERROR] {exc}\n")
                    messagebox.showerror(f"{action_name} error", str(exc))

                self.after(0, _handle_exc)
                return

            def _handle_result() -> None:
                if completed.returncode == 0:
                    self.set_status(f"{action_name} completed.")
                    self._append_log(
                        f"[{action_name.upper()} OK] {git_command_text}\n"
                    )
                    if completed.stdout:
                        self._append_log(
                            f"[{action_name.upper()} STDOUT]\n"
                            + completed.stdout
                            + "\n"
                        )
                    if completed.stderr:
                        self._append_log(
                            f"[{action_name.upper()} STDERR]\n"
                            + completed.stderr
                            + "\n"
                        )
                    messagebox.showinfo(
                        action_name,
                        f"{action_name} completed successfully.",
                    )
                elif "commit " in git_args:
                    self.set_status(f"{action_name} completed.")
                    self._append_log(
                        f"[{action_name.upper()}] Update from StrictDoc Launcher\n"
                    )
                    if completed.stdout:
                        self._append_log(
                            f"[{action_name.upper()} STDOUT]\n"
                            + completed.stdout
                            + "\n"
                        )
                    if completed.stderr:
                        self._append_log(
                            f"[{action_name.upper()} STDERR]\n"
                            + completed.stderr
                            + "\n"
                        )
                else:
                    self.set_status(f"{action_name} failed.")
                    self._append_log(
                        f"[{action_name.upper()} FAILED] rc="
                        f"{completed.returncode}\n"
                    )
                    if completed.stdout:
                        self._append_log(
                            f"[{action_name.upper()} STDOUT]\n"
                            + completed.stdout
                            + "\n"
                        )
                    if completed.stderr:
                        self._append_log(
                            f"[{action_name.upper()} STDERR]\n"
                            + completed.stderr
                            + "\n"
                        )
                    messagebox.showerror(
                        f"{action_name} failed",
                        "Return code: "
                        f"{completed.returncode}\n\nSTDOUT:\n{completed.stdout}\n\nSTDERR:\n{completed.stderr}",
                    )

            self.after(0, _handle_result)

        threading.Thread(target=run_git_action, daemon=True).start()

def _git_pull(self) -> None:
    self._run_git_action("Git pull", ["pull"])

def _git_commit(self) -> None:
    commit_message = simpledialog.askstring(
        "Git Commit",
        "Enter the commit message:",
        parent=self,
        initialvalue="Update from StrictDoc Launcher",
    )
    if commit_message is None:
        return

    commit_message = commit_message.strip()
    if not commit_message:
        messagebox.showwarning("Git Commit", "Commit message cannot be empty.")
        return

    self._run_git_action(
        "Git commit",
        ["commit", "-a", "-m", commit_message],
    )

def _git_push(self) -> None:
    self._run_git_action("Git push", ["push"])