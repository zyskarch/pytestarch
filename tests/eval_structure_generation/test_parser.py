from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from pytestarch.eval_structure_generation.file_import.config import Config
from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter
from pytestarch.eval_structure_generation.file_import.parser import Parser
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)

SOURCE_ROOT = Path(__file__).parent.parent
RESOURCES_DIR = SOURCE_ROOT / "resources/importer"


def test_parser_parses_all_files_in_directory() -> None:
    parser = Parser(
        FileFilter(Config((convert_partial_match_to_regex("*__pycache__"),))),
        SOURCE_ROOT,
        "tests",
    )

    all_modules, parsed_modules = parser.parse(RESOURCES_DIR)

    assert len(all_modules) == 22
    assert len(parsed_modules) == 14

    expected_modules = {
        "tests.resources.importer.file",
        "tests.resources.importer.level0.level1.level2.__init__",
        "tests.resources.importer.level0.test_dummy_3",
        "tests.resources.importer.level0.level1.level2.level3.level4.level5.module_level_5",
        "tests.resources.importer.level0.test_dummy_2",
        "tests.resources.importer.sub_dir.__init__",
        "tests.resources.importer.level0.DummyTest",
        "tests.resources.importer.level0.level1.level2.level3.level4.level5.__init__",
        "tests.resources.importer.level0.level1.level2.level3.__init__",
        "tests.resources.importer.__init__",
        "tests.resources.importer.level0.level1.__init__",
        "tests.resources.importer.level0.test_dummy",
        "tests.resources.importer.level0.level1.level2.level3.level4.__init__",
        "tests.resources.importer.level0.__init__",
    }

    assert set(map(lambda module: module.name, parsed_modules)) == expected_modules


@pytest.mark.parametrize("root_module_name_is_root_dir_name", [False, True])
def test_parser_prefixes_module_names_with_root_module_name(
    tmp_path, root_module_name_is_root_dir_name: bool
) -> None:
    """Module names are prefixed with the given root module name. With the default
    module naming, that is the root directory's name - no matter whether the root
    directory contains an __init__.py. Only relative module naming for a container
    root (root_module_name="") yields prefix-less module names, and then the root
    itself is not added as a module."""
    (tmp_path / "pkg_a").mkdir()
    (tmp_path / "pkg_a" / "__init__.py").write_text("")
    (tmp_path / "pkg_a" / "mod.py").write_text("x = 1")

    if root_module_name_is_root_dir_name:
        root_module_name = tmp_path.name
        prefix = f"{root_module_name}."
        expected_root_module = {root_module_name}
    else:
        root_module_name = ""
        prefix = ""
        expected_root_module = set()

    parser = Parser(FileFilter(Config(())), tmp_path, root_module_name)

    all_modules, parsed_modules = parser.parse(tmp_path)

    assert set(map(lambda module: module.name, parsed_modules)) == {
        f"{prefix}pkg_a.__init__",
        f"{prefix}pkg_a.mod",
    }
    assert set(all_modules) == expected_root_module | {
        f"{prefix}pkg_a",
        f"{prefix}pkg_a.__init__",
        f"{prefix}pkg_a.mod",
    }


@pytest.mark.parametrize(
    "contents",
    [
        "print('content')",
        "print('「content」😭')",
    ],
)
def test_parser_reads_special_chars(tmp_path, contents) -> None:
    """
    Tests that parser handles special chars in the file it parses.
    """
    code_file = tmp_path / "code.py"
    code_file.write_text(contents, encoding="utf-8")
    result: subprocess.CompletedProcess = subprocess.run(  # noqa:S603 // Input is entirely controlled by test.
        [
            sys.executable,
            "-c",
            f"""
from pytestarch.eval_structure_generation import file_import as fi
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)
from pathlib import Path
fi.parser.Parser(
    fi.file_filter.FileFilter(fi.config.Config((convert_partial_match_to_regex("*__pycache__"),))),
    Path("{tmp_path!s}"),
    Path("{tmp_path!s}").name,
).parse(Path("{tmp_path!s}"))
            """,
        ],
        env={
            **os.environ,
            **{
                "LC_ALL": "C",
                "PYTHONUTF8": "0",
                "LANG": "C",
                "PYTHONCOERCELOCALE": "0",
            },
        },
        capture_output=True,
    )

    assert "UnicodeDecodeError" not in result.stderr.decode("utf-8"), (
        "Parser fails to parse code files with utf-8 character contents."
    )
