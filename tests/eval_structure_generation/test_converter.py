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
    imports = converter.convert(asts, "", set(all_modules))

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

    assert len(imports) == len(expected_imports)
    assert {(i.importer(), i.importee()) for i in imports} == expected_imports


@pytest.mark.parametrize(
    "source, internal_modules, expected_imports",
    [
        pytest.param(
            "from .pkg import web",
            {"src.app", "src.app.pkg", "src.app.pkg.web"},
            {("src.app.blue", "src.app.pkg"), ("src.app.blue", "src.app.pkg.web")},
            id="submodule",
        ),
        pytest.param(
            "from .pkg import web as w",
            {"src.app", "src.app.pkg", "src.app.pkg.web"},
            {("src.app.blue", "src.app.pkg"), ("src.app.blue", "src.app.pkg.web")},
            id="aliased submodule",
        ),
        pytest.param(
            "from .pkg import web, helper",
            {"src.app", "src.app.pkg", "src.app.pkg.web"},
            {("src.app.blue", "src.app.pkg"), ("src.app.blue", "src.app.pkg.web")},
            id="submodule next to attribute",
        ),
        pytest.param(
            "from .pkg import helper_a, helper_b",
            {"src.app", "src.app.pkg"},
            {("src.app.blue", "src.app.pkg")},
            id="attributes emit single base import",
        ),
        pytest.param(
            "from . import web",
            {"src.app", "src.app.web"},
            {("src.app.blue", "src.app.web")},
            id="submodule of current package",
        ),
        pytest.param(
            "from . import helper",
            {"src.app"},
            set(),
            id="attribute",
        ),
        pytest.param(
            "from . import *",
            {"src.app"},
            set(),
            id="star import",
        ),
        pytest.param(
            "from .pkg import *",
            {"src.app", "src.app.pkg"},
            {("src.app.blue", "src.app.pkg")},
            id="star import with module",
        ),
        pytest.param(
            "from .. import web",
            {"src", "src.web"},
            {("src.app.blue", "src.web")},
            id="submodule of parent package",
        ),
        pytest.param(
            "from ..red.red2 import Red2",
            {"src", "src.red", "src.red.red2"},
            {("src.app.blue", "src.red.red2")},
            id="class import",
        ),
    ],
)
def test_relative_import_emits_expected_imports(
    source: str,
    internal_modules: set[str],
    expected_imports: set[tuple[str, str]],
) -> None:
    converter = ImportConverter()
    imports = converter.convert(
        [NamedModule(ast.parse(source), "src.app.blue")], "src", internal_modules
    )

    assert len(imports) == len(expected_imports)
    assert {(i.importer(), i.importee()) for i in imports} == expected_imports
