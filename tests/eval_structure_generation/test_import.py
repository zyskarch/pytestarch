from __future__ import annotations

from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport


def test_parent_modules_as_expected() -> None:
    imp = AbsoluteImport("test.test1.test2", "importee.importee2")

    assert set(imp.importer_parent_modules()) == {"test", "test.test1"}
    assert set(imp.importee_parent_modules()) == {"importee"}
