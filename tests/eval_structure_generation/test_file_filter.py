from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pytest

from pytestarch.eval_structure_generation.file_import.config import Config
from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)

test_cases = [
    # ['A', 'B', 'a.main.b'],
    ["A", "B", "development.C"],
    ["A", "B", "C.master"],
    ["A", "B", "dev"],
]


@pytest.mark.parametrize("input_modules", test_cases)
def test_import_filter(input_modules: List[str]) -> None:
    config = Config(
        map(
            lambda s: convert_partial_match_to_regex(s),
            ("*main*", "*master", "development*", "dev"),
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
def test_exclude_files_in_directory(exclusions: Tuple[str, ...]) -> None:
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
