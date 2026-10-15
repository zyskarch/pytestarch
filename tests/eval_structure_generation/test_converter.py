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
    parser = Parser(MockFileFilter(), SOURCE_ROOT, "tests")
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
    "source, importer, root_module_name, internal_modules, expected_imports",
    [
        pytest.param(
            "from package2 import module2",
            "src.package1.module1",
            "src",
            {
                "src",
                "src.package1",
                "src.package1.module1",
                "src.package2",
                "src.package2.module2",
            },
            {
                ("src.package1.module1", "src.package2"),
                ("src.package1.module1", "src.package2.module2"),
            },
            id="root-relative import resolved to prefixed names",
        ),
        pytest.param(
            "from package2 import module2",
            "package1.module1",
            "",
            {"package1", "package1.module1", "package2", "package2.module2"},
            {
                ("package1.module1", "package2"),
                ("package1.module1", "package2.module2"),
            },
            id="relative naming: prefix-less import matched without probing",
        ),
        pytest.param(
            "import sys",
            "src.package1.module1",
            "src",
            {"src", "src.package1", "src.package1.module1"},
            {("src.package1.module1", "sys")},
            id="external import not prefixed with root module name",
        ),
        pytest.param(
            "from package2 import module2",
            "src.package1.module1",
            "src",
            {"src", "src.package1", "src.package1.module1"},
            {("src.package1.module1", "package2")},
            id="root-relative import of unknown module kept as written",
        ),
        pytest.param(
            "import src",
            "src.package1.module1",
            "src",
            {"src", "src.package1", "src.package1.module1"},
            {("src.package1.module1", "src")},
            id="root module import not double-prefixed",
        ),
    ],
)
def test_absolute_import_probed_with_root_module_name(
    source: str,
    importer: str,
    root_module_name: str,
    internal_modules: set[str],
    expected_imports: set[tuple[str, str]],
) -> None:
    """Absolute imports written root-relative are resolved by additionally probing
    against internal modules prefixed with the root module name (default naming of
    container roots)."""
    converter = ImportConverter()
    imports = converter.convert(
        [NamedModule(ast.parse(source), importer)],
        "",
        internal_modules,
        root_module_name,
    )

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


@pytest.mark.parametrize(
    "source, expected_imports",
    [
        # The descent is attribute-based, so one node type per statement-list
        # attribute suffices: `orelse` via If (with a compound node inside) and
        # Try, `handlers`/`finalbody` via Try and TryStar, `cases` via Match.
        pytest.param(
            "if x:\n    import alpha\nelse:\n    for i in y:\n        import beta\n",
            {("src.main", "src.alpha"), ("src.main", "src.beta")},
            id="if else",
        ),
        pytest.param(
            "try:\n    import alpha\nexcept ValueError:\n"
            "    import beta\nexcept Exception:\n"
            "    import gamma\nelse:\n    import epsilon\n"
            "finally:\n    import delta\n",
            {
                ("src.main", "src.alpha"),
                ("src.main", "src.beta"),
                ("src.main", "src.gamma"),
                ("src.main", "src.epsilon"),
                ("src.main", "src.delta"),
            },
            id="try except else finally",
        ),
        pytest.param(
            "try:\n    import alpha\nexcept* ValueError:\n"
            "    import beta\nelse:\n    import gamma\n"
            "finally:\n    import delta\n",
            {
                ("src.main", "src.alpha"),
                ("src.main", "src.beta"),
                ("src.main", "src.gamma"),
                ("src.main", "src.delta"),
            },
            id="try star",
        ),
        pytest.param(
            "match x:\n    case 1:\n        import alpha\n"
            "    case _:\n        import beta\n",
            {("src.main", "src.alpha"), ("src.main", "src.beta")},
            id="match cases",
        ),
        pytest.param(
            "if x:\n    try:\n        pass\n"
            "    except Exception:\n"
            "        match y:\n"
            "            case _:\n"
            "                with z:\n"
            "                    import alpha\n",
            {("src.main", "src.alpha")},
            id="nested compound statements",
        ),
        pytest.param(
            "if x:\n    from . import gamma\nelse:\n    from .delta import epsilon\n",
            {
                ("src.main", "src.gamma"),
                ("src.main", "src.delta"),
                ("src.main", "src.delta.epsilon"),
            },
            id="relative imports in branches",
        ),
    ],
)
def test_imports_in_conditional_blocks_are_converted(
    source: str,
    expected_imports: set[tuple[str, str]],
) -> None:
    internal_modules = {
        "src",
        "src.main",
        "src.alpha",
        "src.beta",
        "src.gamma",
        "src.delta",
        "src.delta.epsilon",
        "src.epsilon",
    }
    converter = ImportConverter()
    imports = converter.convert(
        [NamedModule(ast.parse(source), "src.main")], "src", internal_modules
    )

    assert len(imports) == len(expected_imports)
    assert {(i.importer(), i.importee()) for i in imports} == expected_imports


def test_duplicate_import_in_exclusive_branches_is_emitted_twice() -> None:
    """An import repeated in exclusive branches must not be deduplicated here;
    the dependency graph takes care of filtering duplicate edges."""
    source = "if x:\n    import alpha\nelse:\n    import alpha\n"
    converter = ImportConverter()
    imports = converter.convert(
        [NamedModule(ast.parse(source), "src.main")],
        "src",
        {"src", "src.main", "src.alpha"},
    )

    assert [(i.importer(), i.importee()) for i in imports] == [
        ("src.main", "src.alpha"),
        ("src.main", "src.alpha"),
    ]
