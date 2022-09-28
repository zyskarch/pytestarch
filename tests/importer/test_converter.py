from pathlib import Path

from util import MockFileFilter

from pytestarch.importer.converter import ImportConverter
from pytestarch.importer.parser import Parser

SOURCE_ROOT = Path(__file__).parent.parent
RESOURCES_DIR = SOURCE_ROOT / "resources/importer/level0"


def test_converter_retains_all_non_empty_modules() -> None:
    parser = Parser(MockFileFilter(), SOURCE_ROOT)
    all_modules, asts = parser.parse(RESOURCES_DIR)

    converter = ImportConverter()
    imports = converter.convert(asts)

    expected_imports = {
        "pytestarch.pytestarch",
        "typing",
        "sys",
        "io",
        "os",
        "ast",
        "itertools",
        "pathlib",
        "tests.resources.importer.level0.test_dummy_2",
        "tests.resources.importer.level0.test_dummy_3",
        "pytest",
        "tests.resources.importer.level0.test_dummy",
        "urllib",
    }

    assert set(map(lambda i: i.importee(), imports)) == expected_imports
