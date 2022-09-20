from pathlib import Path

from pytestarch.importer.converter import ImportConverter
from pytestarch.importer.parser import Parser
from util import MockFileFilter

SOURCE_ROOT = Path(__file__).parent.parent
RESOURCES_DIR = SOURCE_ROOT / "resources/importer/level0"


def test_converter_retains_all_non_empty_modules() -> None:
    parser = Parser(SOURCE_ROOT, MockFileFilter(), False)
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
        "resources.importer.level0.test_dummy_2",
        "resources.importer.level0.test_dummy_3",
        "pytest",
        "resources.importer.level0.test_dummy",
        "urllib",
    }

    assert set(map(lambda i: i.importee(), imports)) == expected_imports
