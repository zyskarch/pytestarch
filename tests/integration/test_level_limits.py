from __future__ import annotations

import os

import pytest

from integration.interesting_rules_for_tests import (
    A,
    rules_for_level_limit_1,
    rules_for_no_level_limits,
)
from pytestarch import EvaluableArchitecture, Rule, get_evaluable_architecture
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from resources.test_project import src
from resources.test_project.src import moduleA
from resources.test_project.src.moduleA import submoduleA1


@pytest.mark.parametrize(
    "rule, expected_result, skip_with_level_limit", rules_for_no_level_limits
)
def test_architecture_based_on_string_modules(
    rule: Rule,
    expected_result: bool,
    skip_with_level_limit: bool,
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    if expected_result:
        rule.assert_applies(graph_based_on_string_module_names)
    else:
        with pytest.raises(AssertionError):
            rule.assert_applies(graph_based_on_string_module_names)


@pytest.mark.parametrize(
    "rule_without_submodule, rule_with_submodule",
    [
        (
            Rule()
            .modules_that()
            .are_sub_modules_of(A)
            .should_not()
            .be_imported_by_modules_except_modules_that()
            .are_sub_modules_of(A),
            Rule()
            .modules_that()
            .are_sub_modules_of(A)
            .should_not()
            .be_imported_by_modules_except_modules_that()
            .are_named(A),
        )
    ],
)
def test_same_submodule(
    rule_without_submodule: Rule,
    rule_with_submodule: Rule,
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    # todo: try all other verbs etc if this works
    with pytest.raises(AssertionError) as e1:
        rule_without_submodule.assert_applies(graph_based_on_string_module_names)

    with pytest.raises(AssertionError) as e2:
        rule_with_submodule.assert_applies(graph_based_on_string_module_names)

    assert str(e1.value) == str(e2.value)


@pytest.mark.parametrize(
    "rule, expected_result, skip_with_level_limit", rules_for_no_level_limits
)
def test_architecture_based_on_module_objects(
    rule: Rule,
    expected_result: bool,
    skip_with_level_limit: bool,
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    if expected_result:
        rule.assert_applies(graph_based_on_string_module_names)
    else:
        with pytest.raises(AssertionError):
            rule.assert_applies(graph_based_on_string_module_names)


def test_depending_on_module_does_not_imply_depending_on_submodule(
    graph_including_tests: EvaluableArchitecture,
) -> None:
    rule_1 = (
        Rule()
        .modules_that()
        .are_named("src.moduleC.cTest")
        .should()
        .import_modules_that()
        .are_named("src.moduleB")
    )
    rule_2 = (
        Rule()
        .modules_that()
        .are_named("src.moduleC.cTest")
        .should_not()
        .import_modules_that()
        .are_named("src.moduleB.submoduleB1.fileB3")
    )

    rule_1.assert_applies(graph_including_tests)
    rule_2.assert_applies(graph_including_tests)


@pytest.mark.parametrize(
    "rule, expected_result, skip_with_level_limit", rules_for_no_level_limits
)
def test_identical_source_and_module_path_do_not_lead_to_errors(
    rule: Rule,
    expected_result: bool,
    skip_with_level_limit: bool,
    graph_with_identical_source_and_module_path: EvaluableArchitecture,
) -> None:
    if expected_result:
        rule.assert_applies(graph_with_identical_source_and_module_path)
    else:
        with pytest.raises(AssertionError):
            rule.assert_applies(graph_with_identical_source_and_module_path)


@pytest.mark.parametrize(
    "rule, expected_result, skip_with_level_limit", rules_for_level_limit_1
)
def test_level_limit_flattens_dependencies_correctly(
    rule: Rule,
    expected_result: bool,
    skip_with_level_limit: bool,
    graph_with_level_limit_1: EvaluableArchitecture,
) -> None:
    if skip_with_level_limit:
        return

    if expected_result:
        rule.assert_applies(graph_with_level_limit_1)
    else:
        with pytest.raises(AssertionError):
            rule.assert_applies(graph_with_level_limit_1)


def test_edges_correctly_calculated_for_level_2_module_path() -> None:
    level_2_graph = get_evaluable_architecture(
        os.path.dirname(src.__file__),
        os.path.dirname(moduleA.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    assert (
        len(
            list(
                filter(
                    lambda e: _not_inheritance_edge(e, level_2_graph._graph),  # type: ignore
                    level_2_graph._graph._graph.edges,  # type: ignore
                )
            )
        )
        == 0
    )  # no internal dependencies left

    assert (
        len(level_2_graph._graph._graph.edges) == 9  # type: ignore
    )  # only parent-submodule edges # type: ignore


def _not_inheritance_edge(edge: tuple[str, str], graph: NetworkxGraph) -> bool:
    return not graph.parent_child_relationship(*edge)


def test_edges_correctly_calculated_for_level_2_module_path_no_external_dependencies_modified() -> (
    None
):
    level_2_graph = get_evaluable_architecture(
        os.path.dirname(src.__file__),
        os.path.dirname(moduleA.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
        exclude_external_libraries=False,
    )

    assert len(level_2_graph._graph._graph.edges) == 23  # type: ignore

    for edge in [
        ("src", "src.moduleA"),
        ("src", "src.moduleB"),  # must not be src.moduleA.src.moduleB
        ("src", "src.moduleC"),
        ("src.moduleA", "src.moduleA.fileA"),
        ("src.moduleA", "src.moduleA.submoduleA1"),
        ("src.moduleA", "src.moduleA.submoduleA2"),
        ("src.moduleA.fileA", "src.moduleC.fileC"),
        ("src.moduleA.submoduleA1", "src.moduleA.submoduleA1.submoduleA11"),
        (
            "src.moduleA.submoduleA1.submoduleA11",
            "src.moduleA.submoduleA1.submoduleA11.fileA11",
        ),
        (
            "src.moduleA.submoduleA1.submoduleA11.fileA11",
            "os",
        ),  # must not be src.moduleA.os!
        (
            "src.moduleA.submoduleA1.submoduleA11.fileA11",
            "src.moduleB.submoduleB1.fileB1",
        ),
        ("src.moduleA.submoduleA2", "src.moduleA.submoduleA2.fileA2"),
        ("src.moduleA.submoduleA2.fileA2", "src.moduleC.fileC"),
        ("src.moduleB", "src.moduleB.submoduleB1"),
        ("src.moduleB.submoduleB1", "src.moduleB.submoduleB1.fileB1"),
        ("src.moduleC", "src.moduleC.fileC"),
    ]:
        assert edge in level_2_graph._graph  # type: ignore


def test_edges_correctly_calculated_for_level_3_module_path() -> None:
    level_3_graph = get_evaluable_architecture(
        os.path.dirname(src.__file__),
        os.path.dirname(submoduleA1.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    assert (
        len(
            list(
                filter(
                    lambda e: _not_inheritance_edge(e, level_3_graph._graph),  # type: ignore
                    level_3_graph._graph._graph.edges,  # type: ignore
                )
            )
        )
        == 0
    )  # no internal dependencies left
    assert len(level_3_graph._graph._graph.edges) == 6  # type: ignore


def test_edges_correctly_calculated_for_level_3_module_path_no_external_dependencies_modified() -> (
    None
):
    level_3_graph = get_evaluable_architecture(
        os.path.dirname(src.__file__),
        os.path.dirname(submoduleA1.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
        exclude_external_libraries=False,
    )

    assert len(level_3_graph._graph._graph.edges) == 14  # type: ignore

    for edge in [
        ("src", "src.moduleB"),
        ("src.moduleA.submoduleA1", "src.moduleA.submoduleA1.submoduleA11"),
        (
            "src.moduleA.submoduleA1.submoduleA11",
            "src.moduleA.submoduleA1.submoduleA11.fileA11",
        ),
        ("src.moduleA.submoduleA1.submoduleA11.fileA11", "os"),
        (
            "src.moduleA.submoduleA1.submoduleA11.fileA11",
            "src.moduleB.submoduleB1.fileB1",
        ),
        ("src.moduleB", "src.moduleB.submoduleB1"),
        ("src.moduleB.submoduleB1", "src.moduleB.submoduleB1.fileB1"),
    ]:
        assert edge in level_3_graph._graph  # type: ignore
