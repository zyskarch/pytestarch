from __future__ import annotations

from pathlib import Path

from pytestarch.eval_structure_generation.file_import.import_filter import (
    ExternalImportFilter,
)
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport
from pytestarch.pytestarch import get_evaluable_architecture

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


def test_get_evaluable_architecture_with_none_regex_exclusions_excludes_nothing(
    tmp_path: Path,
) -> None:
    """regex_exclusions=None (the public signature default) behaves as no
    exclusions at all."""
    root = tmp_path / "root"
    module = root / "main"
    module.mkdir(parents=True)
    (module / "keep.py").write_text("")
    (module / "skip_me.py").write_text("")

    evaluable = get_evaluable_architecture(
        str(root),
        str(module),
        exclusions=(),
        # regex_exclusions left as its None default
    )
    assert set(evaluable.modules) == {
        "root",
        "root.main",
        "root.main.keep",
        "root.main.skip_me",
    }

    explicitly_excluded = get_evaluable_architecture(
        str(root),
        str(module),
        exclusions=("*skip_me*",),
    )
    assert "root.main.skip_me" not in explicitly_excluded.modules


def test_get_evaluable_architecture_with_none_external_exclusions_keeps_externals(
    tmp_path: Path,
) -> None:
    """external_exclusions and regex_external_exclusions default to None, which
    must behave as no external exclusions."""
    root = tmp_path / "root"
    module = root / "main"
    module.mkdir(parents=True)
    (module / "app.py").write_text("import os\n")

    evaluable = get_evaluable_architecture(
        str(root),
        str(module),
        exclusions=(),
        exclude_external_libraries=False,
        # external_exclusions and regex_external_exclusions left as their None defaults
    )

    assert "os" in evaluable.modules
