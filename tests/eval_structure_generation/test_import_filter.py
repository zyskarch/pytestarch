from __future__ import annotations

from pathlib import Path

import pytest

from pytestarch.eval_structure_generation.file_import.import_filter import (
    ExternalImportFilter,
)
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport
from pytestarch.pytestarch import get_evaluable_architecture

# Modules detected under the scanned root, including their parent modules. In package
# mode, the graph generator derives this set from all parsed module names starting with
# the root module name prefix, so an importee is internal if and only if it is one of
# these modules or one of their parents.
INTERNAL_MODULES = {"A", "A.B", "A.B.C"}

imports = [
    AbsoluteImport("X", "A.B.C"),
    AbsoluteImport("Y", "A.D"),
]


@pytest.mark.parametrize(
    "exclude_external_libraries, expected_importees",
    [
        pytest.param(True, ["A.B.C"], id="exclude_external_dependencies"),
        pytest.param(False, ["A.B.C", "A.D"], id="include_external_dependencies"),
    ],
)
def test_import_filter(
    exclude_external_libraries: bool, expected_importees: list[str]
) -> None:
    filter = ExternalImportFilter(exclude_external_libraries, INTERNAL_MODULES, ())
    filtered_imports = filter.filter(imports)

    assert [i.importee() for i in filtered_imports] == expected_importees


def test_importee_equal_to_internal_module_name_is_internal() -> None:
    """An importee equal to one of the detected internal modules (e.g. the scanned
    package's __init__) counts as internal."""
    filter = ExternalImportFilter(True, INTERNAL_MODULES, ())
    filtered_imports = filter.filter([AbsoluteImport("X", "A.B")])

    assert [i.importee() for i in filtered_imports] == ["A.B"]


def test_importee_sharing_internal_module_name_prefix_is_external() -> None:
    """'A.BC' shares the internal modules' name prefix, but as importees are matched
    exactly against the detected set, it is not mistaken for a submodule of 'A.B'
    (analogously: 'appstart' is not part of an internal module 'app')."""
    filter = ExternalImportFilter(True, INTERNAL_MODULES, ())
    filtered_imports = filter.filter([AbsoluteImport("X", "A.BC")])

    assert filtered_imports == []


def test_import_filter_retains_internal_and_non_matching_external_imports() -> None:
    filter = ExternalImportFilter(False, INTERNAL_MODULES, ("W\\.X",))
    filtered_imports = filter.filter(imports)

    assert len(filtered_imports) == 2
    assert filtered_imports[0].importee() == "A.B.C"
    assert filtered_imports[1].importee() == "A.D"


def test_import_filter_removes_external_imports_matching_exclusion_pattern() -> None:
    filter = ExternalImportFilter(False, INTERNAL_MODULES, ("A\\.D",))
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
