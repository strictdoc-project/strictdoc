from strictdoc.cli import main


def test_command_registry_does_not_include_launcher_when_tkinter_is_missing(
    monkeypatch,
):
    monkeypatch.setattr(main, "is_launcher_available", lambda: False)

    command_registry = main.create_command_registry()

    assert "launcher" not in command_registry


def test_command_registry_includes_launcher_when_tkinter_is_available(
    monkeypatch,
):
    monkeypatch.setattr(main, "is_launcher_available", lambda: True)

    command_registry = main.create_command_registry()

    assert command_registry["launcher"] is main.LauncherCommand
