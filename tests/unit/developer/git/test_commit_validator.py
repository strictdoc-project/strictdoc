import pytest

from developer.git.commit_validator import validate_commits


def test_validate_commit():
    good_commits = [
        "docs: update release notes",
        'feat(html2pdf): introduce a new "html2pdf_forced_page_break_nodes" option',
        "fix(backend/sdoc_source_code): enable support for requirement identifiers",
        'refactor(cli): migrate "import excel" and "import reqif" to a command pattern',
        "chore(cli): rename shared.py -> _shared.py",
        "chore(.github): switch the macOS tests to macos-latest",
        "docs!: update release notes",
        "chore(cli)!: rename shared.py -> _shared.py",
        "WIP",
        "WIP: Some work",
    ]
    for good_commit_ in good_commits:
        validate_commits([good_commit_])

    bad_commits = [
        "docs",
        "foo: bar",
    ]
    for bad_commit_ in bad_commits:
        with pytest.raises(ValueError):
            validate_commits([bad_commit_])
