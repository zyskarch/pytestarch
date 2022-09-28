from pathlib import Path
from typing import List

import pytest

from pytestarch.config.config import Config
from pytestarch.importer.file_filter import FileFilter

test_cases = [
    # ['A', 'B', 'a.main.b'],
    ["A", "B", "development.C"],
    ["A", "B", "C.master"],
    ["A", "B", "dev"],
]


@pytest.mark.parametrize("input_modules", test_cases)
def test_import_filter(input_modules: List[str]) -> None:
    config = Config(("*main*", "*master", "development*", "dev"))
    filter = FileFilter(config)

    modules = [
        module for module in input_modules if not filter.is_excluded(Path(module))
    ]

    assert len(modules) == 2
    assert "A" in modules
    assert "B" in modules


def test_exclude_files_in_directory() -> None:
    config = Config(("*Test.py", "*__pycache_dummy__", "*__init__*"))
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
