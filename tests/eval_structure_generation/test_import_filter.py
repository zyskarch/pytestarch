from __future__ import annotations

from pathlib import Path

from pytestarch.eval_structure_generation.file_import.import_filter import (
    ExternalImportFilter,
)
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport

ROOT_PATH = Path("A.B")

imports = [
    AbsoluteImport("X", "A.B.C"),
    AbsoluteImport("Y", "A.D"),
]


def test_import_filter_excludes_external_dependencies() -> None:
    filter = ExternalImportFilter(True, str(ROOT_PATH), ())
    filtered_imports = filter.filter(imports)

    assert len(filtered_imports) == 1
    assert filtered_imports[0].importee() == "A.B.C"


def test_import_filter_includes_internal_dependencies() -> None:
    filter = ExternalImportFilter(False, str(ROOT_PATH), ())
    filtered_imports = filter.filter(imports)

    assert len(filtered_imports) == 2
    assert filtered_imports[0].importee() == "A.B.C"
    assert filtered_imports[1].importee() == "A.D"


def test_importee_equal_to_internal_module_name_is_internal() -> None:
    """The internal module itself (e.g. the scanned package's __init__) counts as
    internal, consistent with the importee module calculator's handling of
    importees equal to the root module name."""
    filter = ExternalImportFilter(True, str(ROOT_PATH), ())
    filtered_imports = filter.filter([AbsoluteImport("X", "A.B")])

    assert [i.importee() for i in filtered_imports] == ["A.B"]


def test_importee_sharing_internal_module_name_prefix_is_external() -> None:
    """'A.BC' shares the internal module's name prefix, but the dot-suffixed check
    must not mistake it for a submodule of 'A.B' (analogously: 'appstart' is not
    part of an internal module 'app')."""
    filter = ExternalImportFilter(True, str(ROOT_PATH), ())
    filtered_imports = filter.filter([AbsoluteImport("X", "A.BC")])

    assert filtered_imports == []


def test_import_filter_retains_internal_and_non_matching_external_imports() -> None:
    filter = ExternalImportFilter(False, str(ROOT_PATH), ("W\\.X",))
    filtered_imports = filter.filter(imports)

    assert len(filtered_imports) == 2
    assert filtered_imports[0].importee() == "A.B.C"
    assert filtered_imports[1].importee() == "A.D"


def test_import_filter_removes_external_imports_matching_exclusion_pattern() -> None:
    filter = ExternalImportFilter(False, str(ROOT_PATH), ("A\\.D",))
    imports_with_excludable_external_importees = [
        AbsoluteImport("X", "A.B.C"),
        AbsoluteImport("Y", "A.D"),
        AbsoluteImport("Z", "A.D.sub"),  # parent module A.D matches the pattern
    ]
    filtered_imports = filter.filter(imports_with_excludable_external_importees)

    assert len(filtered_imports) == 1
    assert filtered_imports[0].importee() == "A.B.C"
