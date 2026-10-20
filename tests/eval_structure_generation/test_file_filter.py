from __future__ import annotations

from pathlib import Path

import pytest

from pytestarch.eval_structure_generation.file_import.config import Config
from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)

test_cases = [
    ["A", "B", "development.C"],
    ["A", "B", "C.master"],
    ["A", "B", "dev"],
]


@pytest.mark.parametrize("input_modules", test_cases)
def test_modules_matching_exclusion_patterns_are_removed(
    input_modules: list[str],
) -> None:
    config = Config(
        tuple(
            map(
                lambda s: convert_partial_match_to_regex(s),
                ("*main*", "*master", "development*", "dev"),
            )
        )
    )
    filter = FileFilter(config)

    modules = [
        module for module in input_modules if not filter.is_excluded(Path(module))
    ]

    assert len(modules) == 2
    assert "A" in modules
    assert "B" in modules


exclusion_test_cases = [
    pytest.param(
        map(
            lambda s: convert_partial_match_to_regex(s),
            ("*Test.py", "*__pycache_dummy__", "*__init__*"),
        ),
        id="partial_match",
    ),
    pytest.param((".*Test.py$", ".*__pycache_dummy__$", ".*__init__.*"), id="regex"),
]


@pytest.mark.parametrize("exclusions", exclusion_test_cases)
def test_exclude_files_in_directory(exclusions: tuple[str, ...]) -> None:
    config = Config(exclusions)
    filter = FileFilter(config)

    expected_file = "test_allowed_file.py"
    files = [
        "level0.DummyTest.py",
        "main.test.__pycache_dummy__",
        "level1.__init__.py",
        expected_file,
    ]

    filtered_files = [file for file in files if not filter.is_excluded(Path(file))]

    assert filtered_files == [expected_file]


def test_path_exclusions_match_forward_slash_patterns() -> None:
    """Exclusion patterns are matched against paths in forward-slash form, so
    'src/skipdir'-style patterns work on Windows as well."""
    filter = FileFilter(Config(("src/skipdir",)))

    assert filter.is_excluded(Path("src") / "skipdir" / "skipped.py")
    assert not filter.is_excluded(Path("src") / "keepdir" / "kept.py")
