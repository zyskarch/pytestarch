from __future__ import annotations

from pathlib import Path

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
        FileFilter(Config([convert_partial_match_to_regex("*__pycache__")])),
        SOURCE_ROOT,
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
