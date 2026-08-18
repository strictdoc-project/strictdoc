import sys

import pytest

from strictdoc import environment
from strictdoc.helpers.timing import measure_performance_loop


def test_debug_mode_prints_one_full_line_per_item(monkeypatch, capsys):
    monkeypatch.setattr(environment, "is_debug_mode", True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    with measure_performance_loop("Reading items", 2) as report_progress:
        with report_progress("item one"):
            pass
        with report_progress("item two"):
            pass

    captured = capsys.readouterr()
    lines = captured.out.splitlines()

    assert len(lines) == 2
    assert "item one" in lines[0]
    assert "item two" in lines[1]
    assert "\r" not in captured.out
    assert "\x1b[K" not in captured.out


def test_tty_overwrites_progress_in_place(monkeypatch, capsys):
    monkeypatch.setattr(environment, "is_debug_mode", False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    with measure_performance_loop("Reading items", 3) as report_progress:
        for index in range(3):
            with report_progress(f"item {index}"):
                pass

    captured = capsys.readouterr()

    assert captured.out.count("\r") == 3
    assert captured.out.count("\x1b[K") == 3
    assert "item 0" in captured.out
    assert "item 1" in captured.out
    assert "item 2" in captured.out
    # Exactly one trailing newline, emitted once after the loop finishes.
    assert captured.out.endswith("\n")
    assert captured.out.count("\n") == 1


def test_tty_trailing_newline_is_emitted_even_if_loop_raises(
    monkeypatch, capsys
):
    monkeypatch.setattr(environment, "is_debug_mode", False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    class BoomError(Exception):
        pass

    with pytest.raises(BoomError):
        with measure_performance_loop("Reading items", 2) as report_progress:
            with report_progress("item one"):
                pass
            with report_progress("item two"):
                raise BoomError

    captured = capsys.readouterr()

    assert captured.out.endswith("\n")
    assert captured.out.count("\n") == 1


def test_non_tty_prints_summary_line_then_a_dot_per_item(monkeypatch, capsys):
    monkeypatch.setattr(environment, "is_debug_mode", False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    with measure_performance_loop("Reading items", 5) as report_progress:
        for index in range(5):
            with report_progress(f"item {index}"):
                pass

    captured = capsys.readouterr()

    assert captured.out == "Reading items: 5 tasks\n.....\n"


def test_non_tty_trailing_newline_is_emitted_even_if_loop_raises(
    monkeypatch, capsys
):
    monkeypatch.setattr(environment, "is_debug_mode", False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    class BoomError(Exception):
        pass

    with pytest.raises(BoomError):
        with measure_performance_loop("Reading items", 2) as report_progress:
            with report_progress("item one"):
                pass
            with report_progress("item two"):
                raise BoomError

    captured = capsys.readouterr()

    assert captured.out == "Reading items: 2 tasks\n.\n"
