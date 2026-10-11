from __future__ import annotations

import ast
from pathlib import Path

import pytest
from util import MockFileFilter

from pytestarch.eval_structure_generation.file_import.converter import ImportConverter
from pytestarch.eval_structure_generation.file_import.import_types import NamedModule
from pytestarch.eval_structure_generation.file_import.parser import Parser

SOURCE_ROOT = Path(__file__).parent.parent
RESOURCES_DIR = SOURCE_ROOT / "resources/importer/level0"


def test_converter_retains_all_non_empty_modules() -> None:
    parser = Parser(MockFileFilter(), SOURCE_ROOT)
    all_modules, asts = parser.parse(RESOURCES_DIR)

    converter = ImportConverter()
    imports = converter.convert(asts, "", set())

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
        "__future__",
    }

    assert set(map(lambda i: i.importee(), imports)) == expected_imports


@pytest.mark.parametrize(
    "source, importer, prefix, internal_modules, expected_imports",
    [
        pytest.param(
            "from app import web",
            "src.main",
            "src",
            {"src.app", "src.app.web"},
            {("src.main", "src.app"), ("src.main", "src.app.web")},
            id="submodule",
        ),
        pytest.param(
            "from app import web as w",
            "src.main",
            "src",
            {"src.app", "src.app.web"},
            {("src.main", "src.app"), ("src.main", "src.app.web")},
            id="aliased submodule",
        ),
        pytest.param(
            "from app import web, helper",
            "src.main",
            "src",
            {"src.app", "src.app.web"},
            {("src.main", "src.app"), ("src.main", "src.app.web")},
            id="submodule next to attribute",
        ),
        pytest.param(
            "from app import web",
            "main",
            "",
            {"app", "app.web"},
            {("main", "app"), ("main", "app.web")},
            id="submodule without root prefix",
        ),
        pytest.param(
            "from app import helper",
            "src.main",
            "src",
            {"src.app"},
            {("src.main", "src.app")},
            id="attribute",
        ),
        pytest.param(
            "from app import *",
            "src.main",
            "src",
            {"src.app"},
            {("src.main", "src.app")},
            id="star import",
        ),
    ],
)
def test_import_from_package_emits_expected_imports(
    source: str,
    importer: str,
    prefix: str,
    internal_modules: set[str],
    expected_imports: set[tuple[str, str]],
) -> None:
    converter = ImportConverter()
    imports = converter.convert(
        [NamedModule(ast.parse(source), importer)], prefix, internal_modules
    )

    assert {(i.importer(), i.importee()) for i in imports} == expected_imports
