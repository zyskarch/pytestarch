from __future__ import annotations

import ast
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest
from util import MockFileFilter

from pytestarch.eval_structure.types import get_parent_modules
from pytestarch.eval_structure_generation.file_import.converter import ImportConverter
from pytestarch.eval_structure_generation.file_import.import_roots import (
    ImportRoot,
    ImportRoots,
)
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
        "tests.resources.importer.level0",
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
    converter = ImportConverter(
        import_roots_from_projects(
            {root_module_name: (root_module_name,)}, internal_modules
        )
        if root_module_name
        else None
    )
    imports = converter.convert(
        [NamedModule(ast.parse(source), importer)],
        "",
        internal_modules,
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
            {("src.app.blue", "src.app"), ("src.app.blue", "src.app.web")},
            id="submodule of current package",
        ),
        pytest.param(
            "from . import helper",
            {"src.app"},
            {("src.app.blue", "src.app")},
            id="attribute",
        ),
        pytest.param(
            "from . import *",
            {"src.app"},
            {("src.app.blue", "src.app")},
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
            {("src.app.blue", "src"), ("src.app.blue", "src.web")},
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
                ("src.main", "src"),
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


def _direct_child_packages(prefix: str, known_modules: set[str]) -> set[str]:
    """Names the given module layout holds directly below the import root."""
    if not prefix:
        return {module.split(".", 1)[0] for module in known_modules if module}

    start = f"{prefix}."
    return {
        module[len(start) :]
        for module in known_modules
        if module.startswith(start) and "." not in module[len(start) :]
    }


def import_roots_from_projects(
    projects: Mapping[str, Sequence[str]], modules: set[str]
) -> ImportRoots:
    """Builds the import-root registry from a project-to-import-root mapping
    and a module layout, without touching the file system."""
    module_names = set(modules)
    known_names = set(module_names)
    for module_name in module_names:
        known_names.update(get_parent_modules(module_name))

    return ImportRoots(
        ImportRoot(
            prefix=prefix,
            packages=frozenset(_direct_child_packages(prefix, known_names)),
            scope=project,
        )
        for project, prefixes in projects.items()
        for prefix in prefixes
    )


MONOREPO_PROJECTS = {
    "mono.svc_a": ("mono.svc_a",),
    "mono.svc_b": ("mono.svc_b",),
    "mono.shared": ("mono.shared",),
}
MONOREPO_MODULES = {
    "mono",
    "mono.svc_a",
    "mono.svc_a.svc_a",
    "mono.svc_a.svc_a.api",
    "mono.svc_a.utils",
    "mono.svc_a.utils.helpers",
    "mono.svc_b",
    "mono.svc_b.svc_b",
    "mono.svc_b.svc_b.client",
    "mono.svc_b.utils",
    "mono.svc_b.utils.helpers",
    "mono.shared",
    "mono.shared.shared",
    "mono.shared.shared.util",
}


def _monorepo_imports(
    source: str,
    importer: str,
    projects: dict[str, tuple[str, ...]] | None = None,
    internal_modules: set[str] | None = None,
    layout_modules: set[str] | None = None,
) -> set[tuple[str, str]]:
    project_map = MONOREPO_PROJECTS if projects is None else projects
    converter = ImportConverter(
        import_roots_from_projects(
            project_map,
            MONOREPO_MODULES if layout_modules is None else layout_modules,
        )
    )
    imports = converter.convert(
        [NamedModule(ast.parse(source), importer)],
        "",
        MONOREPO_MODULES if internal_modules is None else internal_modules,
    )

    return {(i.importer(), i.importee()) for i in imports}


def test_import_resolves_to_other_project_of_monorepo() -> None:
    importer = "mono.svc_a.svc_a.api"

    assert _monorepo_imports("import svc_b.client", importer) == {
        (importer, "mono.svc_b.svc_b.client")
    }


def test_bare_package_import_resolves_to_package_not_project_directory() -> None:
    importer = "mono.svc_a.svc_a.api"

    assert _monorepo_imports("import svc_b", importer) == {
        (importer, "mono.svc_b.svc_b")
    }


def test_from_import_of_submodule_resolves_in_other_project() -> None:
    importer = "mono.svc_a.svc_a.api"

    assert _monorepo_imports("from shared import util", importer) == {
        (importer, "mono.shared.shared"),
        (importer, "mono.shared.shared.util"),
    }


def test_import_prefers_module_of_own_project_over_same_name_elsewhere() -> None:
    assert _monorepo_imports("import utils.helpers", "mono.svc_a.svc_a.api") == {
        ("mono.svc_a.svc_a.api", "mono.svc_a.utils.helpers")
    }
    assert _monorepo_imports("import utils.helpers", "mono.svc_b.svc_b.client") == {
        ("mono.svc_b.svc_b.client", "mono.svc_b.utils.helpers")
    }


def test_import_provided_by_several_other_projects_stays_unresolved() -> None:
    importer = "mono.shared.shared.util"

    assert _monorepo_imports("import utils.helpers", importer) == {
        (importer, "utils.helpers")
    }


@pytest.mark.parametrize(
    "source", ["import utils.helpers", "from utils import helpers"]
)
@pytest.mark.parametrize(
    "importer",
    ["mono.svc_a.svc_a.api", "mono.shared.shared.util", "mono.tools.build"],
    ids=["own-package", "ambiguous-other-projects", "outside-projects"],
)
def test_submodule_does_not_select_a_different_package_provider(
    source: str, importer: str
) -> None:
    modules = MONOREPO_MODULES - {"mono.svc_a.utils.helpers"}
    if source == "import utils.helpers":
        expected_importee = "utils.helpers"
    elif importer == "mono.svc_a.svc_a.api":
        expected_importee = "mono.svc_a.utils"
    else:
        expected_importee = "utils"

    assert _monorepo_imports(source, importer, internal_modules=modules) == {
        (importer, expected_importee)
    }


def test_package_provider_is_found_for_partial_scan_without_parent_modules() -> None:
    importer = "mono.svc_a.svc_a.api"

    assert _monorepo_imports(
        "import svc_a.api", importer, internal_modules={importer}
    ) == {(importer, importer)}


@pytest.mark.parametrize(
    "source", ["import utils.helpers", "from utils import helpers"]
)
def test_submodule_stays_with_first_package_provider_within_own_project(
    source: str,
) -> None:
    importer = "mono.svc_a.svc_a.api"
    projects: dict[str, tuple[str, ...]] = {
        **MONOREPO_PROJECTS,
        "mono.svc_a": ("mono.svc_a", "mono.svc_a.src"),
    }
    modules = (MONOREPO_MODULES - {"mono.svc_a.utils.helpers"}) | {
        "mono.svc_a.src.utils",
        "mono.svc_a.src.utils.helpers",
    }
    expected_importee = (
        "utils.helpers" if source.startswith("import") else "mono.svc_a.utils"
    )

    assert _monorepo_imports(
        source,
        importer,
        projects,
        internal_modules=modules,
        layout_modules=modules,
    ) == {(importer, expected_importee)}


def test_import_of_module_outside_all_projects_stays_unchanged() -> None:
    importer = "mono.svc_a.svc_a.api"

    assert _monorepo_imports("import os\nimport requests", importer) == {
        (importer, "os"),
        (importer, "requests"),
    }


def test_importer_outside_projects_resolves_unique_project_module() -> None:
    importer = "mono.tools.build"

    assert _monorepo_imports("import shared.util", importer) == {
        (importer, "mono.shared.shared.util")
    }


def test_importer_outside_projects_does_not_guess_between_projects() -> None:
    importer = "mono.tools.build"

    assert _monorepo_imports("import utils.helpers", importer) == {
        (importer, "utils.helpers")
    }


def test_own_project_is_matched_on_module_boundary() -> None:
    importer = "mono.svc_ab.pkg.module"
    modules = {"mono.svc_a.utils", "mono.svc_ab.utils"}

    imports = ImportConverter(
        import_roots_from_projects(
            {"mono.svc_a": ("mono.svc_a",), "mono.svc_ab": ("mono.svc_ab",)},
            modules,
        )
    ).convert([NamedModule(ast.parse("import utils"), importer)], "", modules)

    assert {(i.importer(), i.importee()) for i in imports} == {
        (importer, "mono.svc_ab.utils")
    }


def test_import_resolution_without_projects_is_unchanged() -> None:
    importer = "mono.svc_a.svc_a.api"

    assert _monorepo_imports("import svc_b.client", importer, projects={}) == {
        (importer, "svc_b.client")
    }


def test_project_resolution_with_relative_naming() -> None:
    importer = "svc_a.svc_a.api"
    modules = {m.removeprefix("mono.") for m in MONOREPO_MODULES if m != "mono"}

    imports = ImportConverter(
        import_roots_from_projects(
            {"svc_a": ("svc_a",), "svc_b": ("svc_b",), "shared": ("shared",)},
            modules,
        )
    ).convert([NamedModule(ast.parse("import svc_b.client"), importer)], "", modules)

    assert {(i.importer(), i.importee()) for i in imports} == {
        (importer, "svc_b.svc_b.client")
    }


SRC_MONOREPO_PROJECTS = {
    "mono.svc_a": ("mono.svc_a.src",),
    "mono.svc_b": ("mono.svc_b.src",),
    "mono.shared": ("mono.shared",),
}
SRC_MONOREPO_MODULES = {
    "mono",
    "mono.svc_a",
    "mono.svc_a.src",
    "mono.svc_a.src.svc_a",
    "mono.svc_a.src.svc_a.api",
    "mono.svc_a.src.utils",
    "mono.svc_a.tests",
    "mono.svc_a.tests.test_api",
    "mono.svc_b",
    "mono.svc_b.src",
    "mono.svc_b.src.svc_b",
    "mono.svc_b.src.svc_b.client",
    "mono.svc_b.src.utils",
    "mono.shared",
    "mono.shared.shared",
    "mono.shared.shared.util",
}


def _src_monorepo_imports(source: str, importer: str) -> set[tuple[str, str]]:
    imports = ImportConverter(
        import_roots_from_projects(SRC_MONOREPO_PROJECTS, SRC_MONOREPO_MODULES)
    ).convert(
        [NamedModule(ast.parse(source), importer)],
        "",
        SRC_MONOREPO_MODULES,
    )

    return {(i.importer(), i.importee()) for i in imports}


def test_import_resolves_into_src_folder_of_other_project() -> None:
    importer = "mono.svc_a.src.svc_a.api"

    assert _src_monorepo_imports(
        "import svc_b.client\nimport shared.util", importer
    ) == {
        (importer, "mono.svc_b.src.svc_b.client"),
        (importer, "mono.shared.shared.util"),
    }


def test_module_next_to_src_folder_belongs_to_own_project() -> None:
    importer = "mono.svc_a.tests.test_api"

    assert _src_monorepo_imports("import utils\nimport svc_a.api", importer) == {
        (importer, "mono.svc_a.src.utils"),
        (importer, "mono.svc_a.src.svc_a.api"),
    }


def test_same_name_in_src_folders_of_several_projects_stays_unresolved() -> None:
    importer = "mono.shared.shared.util"

    assert _src_monorepo_imports("import utils", importer) == {(importer, "utils")}


def test_project_with_flat_and_src_import_roots_is_probed_in_both() -> None:
    modules = {"mono.a.src.pkg_src", "mono.a.pkg_flat", "mono.b.main"}
    converter = ImportConverter(
        import_roots_from_projects(
            {"mono.a": ("mono.a", "mono.a.src"), "mono.b": ("mono.b",)},
            modules,
        )
    )

    imports = converter.convert(
        [NamedModule(ast.parse("import pkg_src\nimport pkg_flat"), "mono.b.main")],
        "",
        modules,
    )

    assert {i.importee() for i in imports} == {"mono.a.src.pkg_src", "mono.a.pkg_flat"}


def test_provider_binding_precedes_partial_scan_prefix_probing() -> None:
    importer = "mono.svc_a.svc_a.api"
    modules = MONOREPO_MODULES - {"mono.svc_a.utils.helpers"}
    converter = ImportConverter(
        import_roots_from_projects(MONOREPO_PROJECTS, MONOREPO_MODULES)
    )

    imports = converter.convert(
        [NamedModule(ast.parse("import utils.helpers"), importer)],
        "mono.svc_b",
        modules,
    )

    assert {(i.importer(), i.importee()) for i in imports} == {
        (importer, "utils.helpers")
    }


def test_unresolved_import_does_not_collide_with_an_implicit_parent_node() -> None:
    importer = "mono.svc_a.svc_a.api"
    converter = ImportConverter(
        import_roots_from_projects(MONOREPO_PROJECTS, MONOREPO_MODULES)
    )

    imports = converter.convert(
        [NamedModule(ast.parse("import utils.missing"), importer)],
        "",
        {importer, "utils.helpers"},
    )

    assert not imports


def test_unknown_provider_does_not_create_a_child_of_an_internal_node() -> None:
    assert not _monorepo_imports("import mono.missing", "mono.svc_a.svc_a.api")
