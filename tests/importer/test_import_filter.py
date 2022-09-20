from pathlib import Path

from pytestarch.importer.import_filter import ImportFilter
from pytestarch.importer.import_types import AbsoluteImport

ROOT_PATH = Path("A.B")

imports = [
    AbsoluteImport("X", "A.B.C"),
    AbsoluteImport("Y", "A.D"),
]


def test_import_filter_excludes_external_dependencies() -> None:
    filter = ImportFilter(True, ROOT_PATH)
    filtered_imports = filter.filter(imports)

    assert len(filtered_imports) == 1
    assert filtered_imports[0].importee() == "A.B.C"


def test_import_filter_includes_internal_dependencies() -> None:
    filter = ImportFilter(False, ROOT_PATH)
    filtered_imports = filter.filter(imports)

    assert len(filtered_imports) == 2
    assert filtered_imports[0].importee() == "A.B.C"
    assert filtered_imports[1].importee() == "A.D"
