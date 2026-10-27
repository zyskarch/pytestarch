"""Tests for scans spanning multiple top-level packages (issue #144): a 'src' root
without __init__.py holding the sibling packages 'package1' and 'package2', where
'package1.module1' imports its sibling via a root-relative import (one written
relative to the scan root).

Legacy mode preserves directory-prefixed names; like in a package root, a
root-relative sibling import resolves against them instead of staying external.
With mode="multi_module", module names are prefix-less and imports resolve
against the sibling packages directly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import resources
from pytestarch import EvaluableArchitecture, Rule, get_evaluable_architecture
from pytestarch.query_language.exceptions import ImproperlyConfigured

SRC = Path(resources.__file__).parent / "multiple_packages_project" / "src"
PACKAGE_1 = SRC / "package1"

DEFAULT_MODULES = {
    "src",
    "src.package1",
    "src.package1.__init__",
    "src.package1.module1",
    "src.package2",
    "src.package2.__init__",
    "src.package2.module2",
}
# the sibling import resolves internally, so only 'sys' stays external
DEFAULT_MODULES_WITH_EXTERNAL = DEFAULT_MODULES | {"sys"}
DEFAULT_HIERARCHY_EDGES = {
    ("src", "src.package1"),
    ("src", "src.package2"),
    ("src.package1", "src.package1.__init__"),
    ("src.package1", "src.package1.module1"),
    ("src.package2", "src.package2.__init__"),
    ("src.package2", "src.package2.module2"),
}
DEFAULT_FULL_EDGES = DEFAULT_HIERARCHY_EDGES | {
    ("src.package1.module1", "src.package2"),
    ("src.package1.module1", "src.package2.module2"),
}
# The partial scan only parses package1: the sibling package2 is not part of the
# scanned module set, so its root-relative import cannot be resolved and stays
# external (as in previous pytestarch versions for this naming).
DEFAULT_PACKAGE_1_MODULES = {
    "src",
    "src.package1",
    "src.package1.__init__",
    "src.package1.module1",
}
DEFAULT_PACKAGE_1_MODULES_WITH_EXTERNAL = DEFAULT_PACKAGE_1_MODULES | {
    "package2",
    "sys",
}
DEFAULT_PACKAGE_1_HIERARCHY_EDGES = {
    ("src", "src.package1"),
    ("src.package1", "src.package1.__init__"),
    ("src.package1", "src.package1.module1"),
}

MULTI_MODULE_MODULES = {
    "package1",
    "package1.__init__",
    "package1.module1",
    "package2",
    "package2.__init__",
    "package2.module2",
}
MULTI_MODULE_MODULES_WITH_EXTERNAL = MULTI_MODULE_MODULES | {"sys"}
MULTI_MODULE_FULL_EDGES = {
    ("package1", "package1.__init__"),
    ("package1", "package1.module1"),
    ("package2", "package2.__init__"),
    ("package2", "package2.module2"),
    ("package1.module1", "package2"),
    ("package1.module1", "package2.module2"),
}
MULTI_MODULE_PACKAGE_1_MODULES = {"package1", "package1.__init__", "package1.module1"}
MULTI_MODULE_PACKAGE_1_HIERARCHY_EDGES = {
    ("package1", "package1.__init__"),
    ("package1", "package1.module1"),
}


@pytest.fixture(scope="module")
def graph_from_src_root() -> EvaluableArchitecture:
    return get_evaluable_architecture(str(SRC), str(SRC), ("*__pycache__",))


@pytest.fixture(scope="module")
def graph_from_src_root_with_external() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        str(SRC),
        str(SRC),
        ("*__pycache__",),
        exclude_external_libraries=False,
    )


@pytest.fixture(scope="module")
def graph_from_src_root_multi_module() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        str(SRC),
        str(SRC),
        ("*__pycache__",),
        mode="multi_module",
    )


@pytest.fixture(scope="module")
def graph_from_src_root_multi_module_with_external() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        str(SRC),
        str(SRC),
        ("*__pycache__",),
        exclude_external_libraries=False,
        mode="multi_module",
    )


@pytest.fixture(scope="module")
def graph_from_package_1() -> EvaluableArchitecture:
    return get_evaluable_architecture(str(SRC), str(PACKAGE_1), ("*__pycache__",))


@pytest.fixture(scope="module")
def graph_from_package_1_with_external() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        str(SRC),
        str(PACKAGE_1),
        ("*__pycache__",),
        exclude_external_libraries=False,
    )


@pytest.fixture(scope="module")
def graph_from_package_1_multi_module() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        str(SRC),
        str(PACKAGE_1),
        ("*__pycache__",),
        mode="multi_module",
    )


@pytest.fixture(scope="module")
def graph_from_package_1_multi_module_with_external() -> EvaluableArchitecture:
    return get_evaluable_architecture(
        str(SRC),
        str(PACKAGE_1),
        ("*__pycache__",),
        exclude_external_libraries=False,
        mode="multi_module",
    )


# Legacy mode: module names prefixed with the root directory's name ------------


def test_modules_prefixed_with_root_dir_name(
    graph_from_src_root: EvaluableArchitecture,
) -> None:
    assert set(graph_from_src_root.modules) == DEFAULT_MODULES
    # no duplicate prefix-less nodes next to the prefixed ones
    assert "package1" not in set(graph_from_src_root.modules)
    assert "package2" not in set(graph_from_src_root.modules)


def test_legacy_mode_resolves_root_relative_import_to_prefixed_module(
    graph_from_src_root: EvaluableArchitecture,
) -> None:
    actual_edges = set(graph_from_src_root._graph._graph.edges)  # type: ignore
    assert actual_edges == DEFAULT_FULL_EDGES

    # sibling packages: no external 'sys' dependency kept (default excludes externals)
    assert "sys" not in set(graph_from_src_root.modules)


def test_legacy_mode_resolves_sibling_import_without_bare_external_node(
    graph_from_src_root_with_external: EvaluableArchitecture,
) -> None:
    assert (
        set(graph_from_src_root_with_external.modules) == DEFAULT_MODULES_WITH_EXTERNAL
    )

    actual_edges = set(graph_from_src_root_with_external._graph._graph.edges)  # type: ignore
    assert actual_edges == DEFAULT_FULL_EDGES | {
        ("src.package1.module1", "sys"),
    }


def test_partial_scan_excludes_out_of_scope_packages(
    graph_from_package_1: EvaluableArchitecture,
) -> None:
    assert set(graph_from_package_1.modules) == DEFAULT_PACKAGE_1_MODULES

    actual_edges = set(graph_from_package_1._graph._graph.edges)  # type: ignore
    assert actual_edges == DEFAULT_PACKAGE_1_HIERARCHY_EDGES


def test_partial_scan_no_duplicates_when_including_external_libraries(
    graph_from_package_1_with_external: EvaluableArchitecture,
) -> None:
    assert set(graph_from_package_1_with_external.modules) == (
        DEFAULT_PACKAGE_1_MODULES_WITH_EXTERNAL
    )

    actual_edges = set(graph_from_package_1_with_external._graph._graph.edges)  # type: ignore
    assert actual_edges == DEFAULT_PACKAGE_1_HIERARCHY_EDGES | {
        ("src.package1.module1", "sys"),
        ("src.package1.module1", "package2"),
    }

    # the sibling package itself is not part of the scanned module set
    assert "src.package2" not in set(graph_from_package_1_with_external.modules)


def test_legacy_rules_see_root_relative_package_dependencies(
    graph_from_src_root: EvaluableArchitecture,
) -> None:
    rule_forbidding_dependency = (
        Rule()
        .modules_that()
        .are_named("src.package2")
        .should_not()
        .be_imported_by_modules_that()
        .are_named("src.package1.module1")
    )
    with pytest.raises(AssertionError):
        rule_forbidding_dependency.assert_applies(graph_from_src_root)

    rule_requiring_dependency = (
        Rule()
        .modules_that()
        .are_named("src.package2")
        .should()
        .be_imported_by_modules_that()
        .are_named("src.package1.module1")
    )
    rule_requiring_dependency.assert_applies(graph_from_src_root)


def test_external_exclusions_remove_only_matching_externals() -> None:
    graph = get_evaluable_architecture(
        str(SRC),
        str(SRC),
        ("*__pycache__",),
        exclude_external_libraries=False,
        external_exclusions=("sys",),
    )

    # the root-relative sibling import is internal now, so no bare 'package2'
    # node exists; only the excluded 'sys' external is gone
    assert set(graph.modules) == DEFAULT_MODULES

    actual_edges = set(graph._graph._graph.edges)  # type: ignore
    assert actual_edges == DEFAULT_FULL_EDGES
    assert ("src.package1.module1", "sys") not in actual_edges


def test_nested_partial_scan_resolves_imports_written_relative_to_parent_package(
    tmp_path: Path,
) -> None:
    """Default-naming container root partial scan: 'from b import x' in a module
    below '../a/b' must be resolved to its full name '<root>.a.b' by the converter's
    probe against the detected module set, not survive as the external module 'b'."""
    package_a = tmp_path / "a"
    package_b = package_a / "b"
    package_b.mkdir(parents=True)
    (package_a / "__init__.py").write_text("")
    (package_b / "__init__.py").write_text("")
    (package_b / "x.py").write_text("value = 1")
    (package_b / "mod.py").write_text("from b import x")

    graph = get_evaluable_architecture(str(tmp_path), str(package_b), ("*__pycache__",))

    root_prefix = tmp_path.name
    # Walking starts at the module path (a/b), so the packages 'a' and the root itself
    # are never parsed as modules of their own - they only appear as hierarchy parents.
    assert set(graph.modules) == {
        root_prefix,
        f"{root_prefix}.a",
        f"{root_prefix}.a.b",
        f"{root_prefix}.a.b.__init__",
        f"{root_prefix}.a.b.mod",
        f"{root_prefix}.a.b.x",
    }

    actual_edges = set(graph._graph._graph.edges)  # type: ignore
    assert actual_edges == {
        (root_prefix, f"{root_prefix}.a"),
        (f"{root_prefix}.a", f"{root_prefix}.a.b"),
        (f"{root_prefix}.a.b", f"{root_prefix}.a.b.__init__"),
        (f"{root_prefix}.a.b", f"{root_prefix}.a.b.mod"),
        (f"{root_prefix}.a.b", f"{root_prefix}.a.b.x"),
        # the import edges: the module-relative importee 'b' was probed into
        # '<root>.a.b', and the imported name 'x' refers to 'a.b.x'
        (f"{root_prefix}.a.b.mod", f"{root_prefix}.a.b"),
        (f"{root_prefix}.a.b.mod", f"{root_prefix}.a.b.x"),
    }


def test_level_limit_flattens_container_graph(
    graph_from_src_root: EvaluableArchitecture,
) -> None:
    """With the default naming the root directory's name fills the hierarchy level
    again (as for package roots), so level_limit=1 includes the packages below the
    root; imports below the limit are reassigned to their level-limit ancestor."""
    graph = get_evaluable_architecture(
        str(SRC),
        str(SRC),
        ("*__pycache__",),
        level_limit=1,
    )

    assert set(graph.modules) == {"src", "src.package1", "src.package2"}

    actual_edges = set(graph._graph._graph.edges)  # type: ignore
    # Hierarchy edges flatten into self-loops and are dropped; the import of
    # package2 is reassigned to package1, the level-1 ancestor of module1.
    assert actual_edges == {
        ("src", "src.package1"),
        ("src", "src.package2"),
        ("src.package1", "src.package2"),
    }


# Multi-module mode: prefix-less module names ------------------------------------


def test_multi_module_modules_not_prefixed_with_root_dir_name(
    graph_from_src_root_multi_module: EvaluableArchitecture,
) -> None:
    assert set(graph_from_src_root_multi_module.modules) == MULTI_MODULE_MODULES
    assert not any(
        module_name.startswith("src")
        for module_name in graph_from_src_root_multi_module.modules
    )
    assert "src" not in set(graph_from_src_root_multi_module.modules)


def test_multi_module_internal_dependency_retained_between_sibling_packages(
    graph_from_src_root_multi_module: EvaluableArchitecture,
) -> None:
    actual_edges = set(graph_from_src_root_multi_module._graph._graph.edges)  # type: ignore
    assert actual_edges == MULTI_MODULE_FULL_EDGES

    assert "sys" not in set(graph_from_src_root_multi_module.modules)


def test_multi_module_no_duplicate_modules_when_including_external_libraries(
    graph_from_src_root_multi_module_with_external: EvaluableArchitecture,
) -> None:
    assert set(graph_from_src_root_multi_module_with_external.modules) == (
        MULTI_MODULE_MODULES_WITH_EXTERNAL
    )

    actual_edges = set(
        graph_from_src_root_multi_module_with_external._graph._graph.edges
    )  # type: ignore
    assert actual_edges == MULTI_MODULE_FULL_EDGES | {("package1.module1", "sys")}


def test_multi_module_partial_scan_excludes_out_of_scope_packages(
    graph_from_package_1_multi_module: EvaluableArchitecture,
) -> None:
    assert (
        set(graph_from_package_1_multi_module.modules) == MULTI_MODULE_PACKAGE_1_MODULES
    )

    actual_edges = set(graph_from_package_1_multi_module._graph._graph.edges)  # type: ignore
    assert actual_edges == MULTI_MODULE_PACKAGE_1_HIERARCHY_EDGES


def test_multi_module_partial_scan_no_duplicates_when_including_external_libraries(
    graph_from_package_1_multi_module_with_external: EvaluableArchitecture,
) -> None:
    """Partial scan, externals included: the sibling package2 lies outside the
    scanned module set, so its root-relative import cannot be resolved and its
    dependency is listed under the bare name - the same external-node contract the
    default naming has always had."""
    assert set(graph_from_package_1_multi_module_with_external.modules) == (
        MULTI_MODULE_PACKAGE_1_MODULES | {"package2", "sys"}
    )

    actual_edges = set(
        graph_from_package_1_multi_module_with_external._graph._graph.edges
    )  # type: ignore
    assert actual_edges == MULTI_MODULE_PACKAGE_1_HIERARCHY_EDGES | {
        ("package1.module1", "sys"),
        ("package1.module1", "package2"),
    }


def test_multi_module_rules_work_on_multiple_top_level_packages(
    graph_from_src_root_multi_module: EvaluableArchitecture,
) -> None:
    rule_forbidding_dependency = (
        Rule()
        .modules_that()
        .are_named("package2")
        .should_not()
        .be_imported_by_modules_that()
        .are_named("package1.module1")
    )
    with pytest.raises(AssertionError):
        rule_forbidding_dependency.assert_applies(graph_from_src_root_multi_module)

    rule_requiring_dependency = (
        Rule()
        .modules_that()
        .are_named("package2")
        .should()
        .be_imported_by_modules_that()
        .are_named("package1.module1")
    )
    rule_requiring_dependency.assert_applies(graph_from_src_root_multi_module)


def test_multi_module_nested_partial_scan_resolves_imports_written_relative_to_parent_package(
    tmp_path: Path,
) -> None:
    """Relative-naming container root partial scan: 'from b import x' must be resolved
    to 'a.b' by the converter's probe against the detected module set, not survive as
    the external module 'b'."""
    package_a = tmp_path / "a"
    package_b = package_a / "b"
    package_b.mkdir(parents=True)
    (package_a / "__init__.py").write_text("")
    (package_b / "__init__.py").write_text("")
    (package_b / "x.py").write_text("value = 1")
    (package_b / "mod.py").write_text("from b import x")

    graph = get_evaluable_architecture(
        str(tmp_path), str(package_b), ("*__pycache__",), mode="multi_module"
    )

    # Walking starts at the module path (a/b), so the package 'a' itself is never
    # parsed as a module of its own - it only appears as the hierarchy parent of 'a.b'.
    assert set(graph.modules) == {"a", "a.b", "a.b.__init__", "a.b.mod", "a.b.x"}

    actual_edges = set(graph._graph._graph.edges)  # type: ignore
    assert actual_edges == {
        ("a", "a.b"),
        ("a.b", "a.b.__init__"),
        ("a.b", "a.b.mod"),
        ("a.b", "a.b.x"),
        # the import edges: the module-relative importee 'b' was probed into 'a.b',
        # and the imported name 'x' refers to the known internal module 'a.b.x'
        ("a.b.mod", "a.b"),
        ("a.b.mod", "a.b.x"),
    }


def test_multi_module_level_limit_flattens_container_graph() -> None:
    """In multi-module mode the root itself is not a module: level_limit=1 contains
    only the top level packages, and imports are reassigned to their level-limit
    ancestor."""
    graph = get_evaluable_architecture(
        str(SRC),
        str(SRC),
        ("*__pycache__",),
        level_limit=1,
        mode="multi_module",
    )

    assert set(graph.modules) == {"package1", "package2"}

    actual_edges = set(graph._graph._graph.edges)  # type: ignore
    # hierarchy edges flatten into self-loops and are dropped; the import of
    # package2 is reassigned to package1, the level-1 ancestor of module1
    assert actual_edges == {("package1", "package2")}


def test_multi_module_level_limit_zero_raises() -> None:
    """In multi-module mode the root itself is not a module, so a level limit of 0
    would not leave any module in the graph."""
    with pytest.raises(ImproperlyConfigured, match="level_limit must be at least 1"):
        get_evaluable_architecture(
            str(SRC),
            str(SRC),
            ("*__pycache__",),
            level_limit=0,
            mode="multi_module",
        )
