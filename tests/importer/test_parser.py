from pathlib import Path

from pytestarch.config.config import Config
from pytestarch.importer.file_filter import FileFilter
from pytestarch.importer.parser import Parser

SOURCE_ROOT = Path(__file__).parent.parent
RESOURCES_DIR = SOURCE_ROOT / "resources/importer"


def test_parser_parses_all_files_in_directory() -> None:
    parser = Parser(SOURCE_ROOT, FileFilter(Config(("*__pycache__",))), False)

    all_modules, parsed_modules = parser.parse(RESOURCES_DIR)

    assert len(all_modules) == 22
    assert len(parsed_modules) == 14

    expected_modules = {
        "resources.importer.sub_dir.__init__",
        "resources.importer.file",
    }

    assert set(map(lambda module: module.name, parsed_modules)) >= expected_modules
