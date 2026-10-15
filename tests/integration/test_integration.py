from __future__ import annotations

import os
from pathlib import Path

import pytest
from rule_assessment.test_rule_matcher import (
    ALL_MODULES,
    MODULE_1,
    MODULE_2,
    MODULE_3,
)

from integration.interesting_rules_for_tests import (
    A,
    partial_name_match_test_cases,
    single_rule_subject_multiple_rule_objects_error_message_test_cases,
    single_rule_subject_single_rule_object_error_message_test_cases,
)
from pytestarch import EvaluableArchitecture, Rule, get_evaluable_architecture
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.exceptions import ImportException
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport
from pytestarch.pytestarch import get_evaluable_architecture_for_module_objects
from pytestarch.query_language.exceptions import ImproperlyConfigured
from resources import nested_root_module_mismatch_project, root_module_mismatch_project
from resources.from_import_project import app as from_import_app
from resources.nested_root_module_mismatch_project.dir1.dir2 import nested_app
from resources.root_module_mismatch_project import app
from resources.test_project import src
from resources.test_project.src import moduleA


@pytest.mark.parametrize(
    "rule, expected_error_message",
    single_rule_subject_single_rule_object_error_message_test_cases,
)
def test_rule_violated_raises_proper_error_message(
    rule: Rule,
    expected_error_message: str,
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    with pytest.raises(AssertionError, match=expected_error_message):
        rule.assert_applies(graph_based_on_string_module_names)


@pytest.mark.parametrize(
    "rule, expected_error_message",
    single_rule_subject_multiple_rule_objects_error_message_test_cases,
)
def test_rule_violated_with_multiple_rule_objects_raises_proper_error_message(
    rule: Rule,
    expected_error_message: str,
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    with pytest.raises(AssertionError, match=expected_error_message):
        rule.assert_applies(graph_based_on_string_module_names)


@pytest.mark.parametrize("rule, violation", partial_name_match_test_cases)
def test_rule_violation_correctly_detected_for_partial_name_matches(
    rule: Rule,
    violation: bool,
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    if violation:
        with pytest.raises(AssertionError):
            rule.assert_applies(graph_based_on_string_module_names)
    else:
        rule.assert_applies(graph_based_on_string_module_names)
        # no exception


def test_root_module_mismatch_handled_as_expected() -> None:
    evaluable = get_evaluable_architecture(
        os.path.dirname(root_module_mismatch_project.__file__),
        os.path.dirname(app.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("root_module_mismatch_project.app.red")
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of("root_module_mismatch_project.app.green")
    )

    error_message = (
        '"root_module_mismatch_project.app.red.red" is imported by "root_module_mismatch_project.app.green.green".\n'
        '"root_module_mismatch_project.app.red.red2" is imported by "root_module_mismatch_project.app.green.green".\n'
        '"root_module_mismatch_project.app.red.red3" is imported by "root_module_mismatch_project.app.green.green".'
    )
    with pytest.raises(AssertionError, match=error_message):
        rule.assert_applies(evaluable)


def test_root_module_match_handled_as_expected() -> None:
    evaluable = get_evaluable_architecture(
        os.path.dirname(app.__file__),
        os.path.dirname(app.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    rule = (
        Rule()
        .modules_that()
        .are_named("app.red")
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of("app.green")
    )

    with pytest.raises(
        AssertionError,
        match='"app.red.red" is imported by "app.green.green".\n"app.red.red2" is imported by "app.green.green".\n"app.red.red3" is imported by "app.green.green".',
    ):
        rule.assert_applies(evaluable)


def test_import_from_package_of_submodule_detected_by_rule() -> None:
    evaluable = get_evaluable_architecture(
        os.path.dirname(from_import_app.__file__),
        os.path.dirname(from_import_app.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    rule = (
        Rule()
        .modules_that()
        .are_named("app.web")
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of("app.green")
    )

    with pytest.raises(
        AssertionError,
        match='"app.web" is imported by "app.green.green".',
    ):
        rule.assert_applies(evaluable)


def test_import_from_package_of_attribute_does_not_create_module() -> None:
    evaluable = get_evaluable_architecture(
        os.path.dirname(from_import_app.__file__),
        os.path.dirname(from_import_app.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
        exclude_external_libraries=False,
    )

    assert isinstance(evaluable, EvaluableArchitectureGraph)
    assert "app.helper" not in evaluable.modules


def test_relative_import_from_package_of_submodule_detected_by_rule() -> None:
    evaluable = get_evaluable_architecture(
        os.path.dirname(from_import_app.__file__),
        os.path.dirname(from_import_app.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    rule = (
        Rule()
        .modules_that()
        .are_named("app.maroon")
        .should_not()
        .import_modules_that()
        .are_named("app.indigo.util")
    )

    with pytest.raises(
        AssertionError,
        match='"app.maroon" imports "app.indigo.util".',
    ):
        rule.assert_applies(evaluable)


def test_relative_import_from_module_of_attribute_does_not_create_module() -> None:
    evaluable = get_evaluable_architecture(
        os.path.dirname(from_import_app.__file__),
        os.path.dirname(from_import_app.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
        exclude_external_libraries=False,
    )

    assert isinstance(evaluable, EvaluableArchitectureGraph)
    assert "app.web.helper" not in evaluable.modules


def test_nested_root_module_mismatch_handled_as_expected() -> None:
    evaluable = get_evaluable_architecture(
        os.path.dirname(nested_root_module_mismatch_project.__file__),
        os.path.dirname(nested_app.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of(
            "nested_root_module_mismatch_project.dir1.dir2.nested_app.red"
        )
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(
            "nested_root_module_mismatch_project.dir1.dir2.nested_app.green"
        )
    )

    error_message = (
        '"nested_root_module_mismatch_project.dir1.dir2.nested_app.red.red" is imported by "nested_root_module_mismatch_project.dir1.dir2.nested_app.green.green".\n'
        '"nested_root_module_mismatch_project.dir1.dir2.nested_app.red.red2" is imported by "nested_root_module_mismatch_project.dir1.dir2.nested_app.green.green".\n'
        '"nested_root_module_mismatch_project.dir1.dir2.nested_app.red.red3" is imported by "nested_root_module_mismatch_project.dir1.dir2.nested_app.green.green".'
    )
    with pytest.raises(AssertionError, match=error_message):
        rule.assert_applies(evaluable)


def test_nested_root_module_match_handled_as_expected() -> None:
    evaluable = get_evaluable_architecture(
        os.path.dirname(nested_app.__file__),
        os.path.dirname(nested_app.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    rule = (
        Rule()
        .modules_that()
        .are_named("nested_app.red")
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of("nested_app.green")
    )

    with pytest.raises(
        AssertionError,
        match='"nested_app.red.red" is imported by "nested_app.green.green".\n"nested_app.red.red2" is imported by "nested_app.green.green".\n"nested_app.red.red3" is imported by "nested_app.green.green".',
    ):
        rule.assert_applies(evaluable)


def test_same_submodule_as_importer_shows_same_behavior(
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    rule_without_submodule = (
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(A)
    )
    rule_with_submodule = (
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named(A)
    )

    with pytest.raises(AssertionError) as e1:
        rule_without_submodule.assert_applies(graph_based_on_string_module_names)

    with pytest.raises(AssertionError) as e2:
        rule_with_submodule.assert_applies(graph_based_on_string_module_names)

    assert str(e1.value) == str(e2.value)


_SUBMODULE_1 = f"{MODULE_1}.1"
_SUBMODULE_2 = f"{MODULE_1}.2"

same_importer_importee_test_cases = [
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_1, _SUBMODULE_2),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should()
        .import_modules_that()
        .are_sub_modules_of(MODULE_1),
        None,
        id="should_import_true",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_1, MODULE_2),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should()
        .import_modules_that()
        .are_sub_modules_of(MODULE_1),
        'Sub modules of "1" do not import a sub module of "1".',
        id="should_import_false",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_1, MODULE_2),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of(MODULE_1),
        None,
        id="should_not_import_true",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_1, _SUBMODULE_2),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of(MODULE_1),
        '"1.1" imports "1.2"',
        id="should_not_import_false",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_1, _SUBMODULE_2),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of(MODULE_1),
        None,
        id="should_only_import_true",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_1, _SUBMODULE_2),
            AbsoluteImport(_SUBMODULE_1, MODULE_3),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of(MODULE_1),
        '"1.1" imports "3"',
        id="should_only_import_false",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_2, _SUBMODULE_1),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of(MODULE_1),
        None,
        id="should_be_imported_true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, _SUBMODULE_1),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of(MODULE_1),
        'Sub modules of "1" are not imported by a sub module of "1"',
        id="should_be_imported_false",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, _SUBMODULE_1),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(MODULE_1),
        None,
        id="should_not_be_imported_true",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_2, _SUBMODULE_1),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(MODULE_1),
        '"1.1" is imported by "1.2"',
        id="should_not_be_imported_false",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_1, _SUBMODULE_2),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of(MODULE_1),
        None,
        id="should_only_be_imported_true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_3, _SUBMODULE_2),
            AbsoluteImport(_SUBMODULE_2, _SUBMODULE_1),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of(MODULE_1),
        '"1.2" is imported by "3',
        id="should_only_be_imported_false",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, _SUBMODULE_2),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(MODULE_1),
        None,
        id="should_be_imported_except_true",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_1, _SUBMODULE_1),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(MODULE_1),
        'Sub modules of "1" are not imported by any module that is not a sub module of "1".',
        id="should_be_imported_except_false",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_2, _SUBMODULE_1),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(MODULE_1),
        None,
        id="should_not_be_imported_except_true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, _SUBMODULE_1),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(MODULE_1),
        '"1.1" is imported by "2".',
        id="should_not_be_imported_except_false",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_3, _SUBMODULE_2),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(MODULE_1),
        None,
        id="should_only_be_imported_except_true",
    ),
    pytest.param(
        [
            AbsoluteImport(_SUBMODULE_2, _SUBMODULE_1),
            AbsoluteImport(MODULE_2, _SUBMODULE_2),
        ],
        Rule()
        .modules_that()
        .are_sub_modules_of(MODULE_1)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(MODULE_1),
        '"1.1" is imported by "1.2".',
        id="should_only_be_imported_except_false",
    ),
]


@pytest.mark.parametrize(
    "imports, rule, expected_error",
    same_importer_importee_test_cases,
)
def test_same_importer_same_importee_handled_correctly(
    imports: list[AbsoluteImport],
    rule: Rule,
    expected_error: str | None,
) -> None:
    evaluable = EvaluableArchitectureGraph(
        NetworkxGraph(ALL_MODULES + [_SUBMODULE_1, _SUBMODULE_2], imports)
    )

    if expected_error is None:
        rule.assert_applies(evaluable)
    else:
        with pytest.raises(AssertionError, match=expected_error):
            rule.assert_applies(evaluable)


def test_importee_module_calculator_does_not_add_internal_modules_as_external() -> None:
    """With exclude_external_libraries=False, modules that belong to the scanned
    root module must NOT appear as spurious extra nodes in the graph.

    See https://github.com/zyskarch/pytestarch/issues/144."""
    level_2_graph = get_evaluable_architecture(
        os.path.dirname(src.__file__),
        os.path.dirname(moduleA.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
        exclude_external_libraries=False,
    )

    nodes = set(level_2_graph._graph._graph.nodes)  # type: ignore
    # 'src.moduleB' and 'src.moduleC' are imported by files inside moduleA,
    # but they start with the root module name 'src', so they must not be
    # added as external dependency nodes to the graph.
    assert "src.moduleB" not in nodes
    assert "src.moduleC" not in nodes


def test_import_of_root_package_not_treated_as_internal_by_default(
    tmp_path: Path,
) -> None:
    """Regression test for the #144 review: an importee equal to the scanned module
    name is internal even with exclude_external_libraries=True (default) - previously
    only its submodules counted as internal (with False the edge exists as well: the
    root node is in the graph via the parser's root-dir naming)."""
    app = tmp_path / "app"
    app.mkdir()
    (app / "__init__.py").write_text("")
    (app / "mod.py").write_text("import app")

    arch = get_evaluable_architecture(str(app), str(app))

    assert set(arch.modules) == {"app", "app.__init__", "app.mod"}

    actual_edges = set(arch._graph._graph.edges)  # type: ignore
    assert ("app", "app.__init__") in actual_edges
    assert ("app", "app.mod") in actual_edges
    assert ("app.mod", "app") in actual_edges

    arch_with_external = get_evaluable_architecture(
        str(app),
        str(app),
        exclude_external_libraries=False,
    )

    actual_edges_with_external = set(arch_with_external._graph._graph.edges)  # type: ignore
    assert ("app.mod", "app") in actual_edges_with_external


def test_container_root_level_relative_import_raises_explanatory_error(
    tmp_path: Path,
) -> None:
    """A top level file of a container root (a scanned directory without __init__.py)
    has no parent package, so a relative import within it cannot be resolved.
    This must raise an explanatory ImportException instead of an IndexError."""
    (tmp_path / "helper.py").write_text("x = 1")
    (tmp_path / "top.py").write_text("from . import helper")

    with pytest.raises(ImportException, match="relative import"):
        get_evaluable_architecture(
            str(tmp_path), str(tmp_path), module_naming="relative"
        )


def test_container_root_top_level_relative_import_resolved_in_default_naming(
    tmp_path: Path,
) -> None:
    """With the default naming, module names carry the root directory's name as prefix,
    so a top level file of a container root has that name as its parent module and its
    relative import resolves against the root (i.e. it is an internal dependency)."""
    (tmp_path / "helper.py").write_text("x = 1")
    (tmp_path / "top.py").write_text("from . import helper")

    arch = get_evaluable_architecture(str(tmp_path), str(tmp_path))

    assert set(arch.modules) == {
        tmp_path.name,
        f"{tmp_path.name}.helper",
        f"{tmp_path.name}.top",
    }

    actual_edges = set(arch._graph._graph.edges)  # type: ignore
    assert (f"{tmp_path.name}.top", f"{tmp_path.name}.helper") in actual_edges


def test_invalid_module_naming_raises(tmp_path: Path) -> None:
    """An unknown module_naming value must be rejected with ImproperlyConfigured."""
    (tmp_path / "pkg.py").write_text("")

    with pytest.raises(ImproperlyConfigured, match="module_naming"):
        get_evaluable_architecture(
            str(tmp_path),
            str(tmp_path),
            module_naming="bogus",  # type: ignore[arg-type]
        )

    with pytest.raises(ImproperlyConfigured, match="module_naming"):
        get_evaluable_architecture_for_module_objects(
            src,
            src,
            module_naming="bogus",  # type: ignore[arg-type]
        )


def test_package_root_ignores_relative_module_naming(tmp_path: Path) -> None:
    """module_naming is only relevant for container roots (no __init__.py): if the root
    path is a Python package itself, its name always prefixes the module names and the
    option is ignored."""
    app = tmp_path / "app"
    app.mkdir()
    (app / "__init__.py").write_text("")
    (app / "mod.py").write_text("import app")

    arch = get_evaluable_architecture(str(app), str(app), module_naming="relative")

    assert set(arch.modules) == {"app", "app.__init__", "app.mod"}

    actual_edges = set(arch._graph._graph.edges)  # type: ignore
    assert ("app", "app.__init__") in actual_edges
    assert ("app", "app.mod") in actual_edges


def test_module_objects_pass_module_naming_through(tmp_path: Path) -> None:
    """get_evaluable_architecture_for_module_objects forwards module_naming: for a
    package root the option is ignored (same prefixed names), ensuring the parameter is
    accepted and wired through."""
    evaluable = get_evaluable_architecture_for_module_objects(
        src, src, module_naming="relative"
    )

    assert "src.moduleA" in set(evaluable.modules)
