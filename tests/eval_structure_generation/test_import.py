from __future__ import annotations

import pytest

from pytestarch.eval_structure_generation.file_import.exceptions import ImportException
from pytestarch.eval_structure_generation.file_import.import_types import (
    AbsoluteImport,
    RelativeImport,
)


def test_parent_modules_as_expected() -> None:
    imp = AbsoluteImport("test.test1.test2", "importee.importee2")

    assert set(imp.importer_parent_modules()) == {"test", "test.test1"}
    assert set(imp.importee_parent_modules()) == {"importee"}


def test_relative_import_parent_modules_as_expected() -> None:
    imp = RelativeImport("test.test1.test2", "importee", "importee2", 1)

    assert set(imp.importer_parent_modules()) == {"test", "test.test1"}
    assert set(imp.importee_parent_modules()) == {
        "test",
        "test.test1",
        "test.test1.importee",
    }


def test_relative_import_without_module_and_name_is_the_base_package() -> None:
    """The bare 'from . import <name>' form imports the containing package as
    well; an import without module and name represents exactly that package."""

    imp = RelativeImport("test.test1.test2", None, None, 1)

    assert imp.importee() == "test.test1"
    assert set(imp.importee_parent_modules()) == {"test"}

    imp_level_2 = RelativeImport("test.test1.test2", None, None, 2)

    assert imp_level_2.importee() == "test"
    assert set(imp_level_2.importee_parent_modules()) == set()


def test_relative_import_from_init_file_resolves_to_the_package_itself() -> None:
    """A package's __init__ file is named '<package>.__init__': a level-1
    relative import from it targets the package itself, level 2 its parent."""

    imp = RelativeImport("test.test1.__init__", None, None, 1)

    assert imp.importee() == "test.test1"

    imp_parent = RelativeImport("test.test1.__init__", None, None, 2)

    assert imp_parent.importee() == "test"


def test_relative_import_with_level_below_one_raises() -> None:
    with pytest.raises(ImportException, match="at least one leading dot"):
        RelativeImport("test.test1.test2", None, None, 0)
