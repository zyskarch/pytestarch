import os

import pytest

# from matplotlib import pyplot as plt
# from matplotlib.pyplot import figure

from pytestarch.eval_structure.eval_structure_types import EvaluableArchitecture
from pytestarch.pytestarch import get_evaluable_architecture
from pytestarch.query_language.base_language import Rule
from resources import test_project
from resources.test_project.src import moduleA
from resources.test_project.src.moduleA import submoduleA1

rules_to_test = [
    (
        Rule()
        .modules_that()
        .are_named("src.moduleC")
        .should_not()
        .import_modules_except_modules_that()
        .are_named("src.moduleA"),
        True,
        False,
    ),
    (
        Rule()
        .modules_that()
        .are_named("src.moduleC")
        .should_only()
        .be_imported_by_modules_that()
        .are_named("src.moduleA.submoduleA2"),
        False,
        True,
    ),
    # same rule, but adapted for flattened graph
    (
        Rule()
        .modules_that()
        .are_named("src.moduleC")
        .should_only()
        .be_imported_by_modules_that()
        .are_named("src.moduleA"),
        False,
        False,
    ),
    (
        Rule()
        .modules_that()
        .are_sub_modules_of("src.moduleA.submoduleA1")
        .should_only()
        .import_modules_that()
        .are_sub_modules_of("src.moduleB"),
        True,
        True,
    ),
    # same rule, but adapted for flattened graph
    (
        Rule()
        .modules_that()
        .are_sub_modules_of("src.moduleA")
        .should()
        .import_modules_that()
        .are_sub_modules_of("src.moduleB"),
        False,  # there are no true sub modules left
        False,
    ),
    (
        Rule()
        .modules_that()
        .are_named("src.moduleB")
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of("src.moduleA"),
        False,
        False,
    ),
    (
        Rule()
        .modules_that()
        .are_named("src.moduleB")
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of("src.moduleA"),
        True,
        True,
    ),
    (
        Rule()
        .modules_that()
        .are_named("src.moduleA.submoduleA1.submoduleA11")
        .should_not()
        .import_modules_that()
        .are_named("src.moduleB.submoduleB1.fileB2"),
        True,
        True,
    ),
    # same rule, but adapted for flattened graph
    (
        Rule()
        .modules_that()
        .are_named("src.moduleA")
        .should()
        .import_modules_that()
        .are_named("src.moduleB"),
        True,
        False,
    ),
    (
        Rule()
        .modules_that()
        .are_sub_modules_of("src.moduleA")
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of("src.moduleB"),
        False,
        False,  # there are no true sub modules left
    ),
    (
        Rule()
        .modules_that()
        .are_sub_modules_of("src.moduleA")
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of("src.moduleB"),
        True,
        False,
    ),
]


@pytest.mark.parametrize("rule, expected_result, skip_with_level_limit", rules_to_test)
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
            assert rule.assert_applies(graph_based_on_string_module_names)


@pytest.mark.parametrize("rule, expected_result, skip_with_level_limit", rules_to_test)
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
            assert rule.assert_applies(graph_based_on_string_module_names)


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


@pytest.mark.parametrize("rule, expected_result, skip_with_level_limit", rules_to_test)
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
            assert rule.assert_applies(graph_with_identical_source_and_module_path)


@pytest.mark.parametrize("rule, expected_result, skip_with_level_limit", rules_to_test)
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
            assert rule.assert_applies(graph_with_level_limit_1)


# def test_exporting_as_image_does_not_raise_error(
#     graph_based_on_string_module_names: EvaluableArchitecture,
# ) -> None:
#     figure(figsize=(12, 6), dpi=80)
#
#     graph_based_on_string_module_names.visualize(
#         spacing=0.35,
#         node_size=800,
#         arrowsize=30,
#         labels={
#             "src": "src",
#             "src.moduleA": "A",
#             "src.moduleB": "B",
#             "src.moduleC": "C",
#             "src.moduleA.submoduleA1": "A1",
#             "src.moduleA.submoduleA2": "A2",
#             "src.moduleA.fileA": "fileA",
#             "src.moduleA.submoduleA1.submoduleA11": "A11",
#             "src.moduleA.submoduleA1.fileA1": "fileA1",
#             "src.moduleA.submoduleA1.fileA1_b": "fileA1b",
#             "src.moduleA.submoduleA1.submoduleA11.fileA11": "fileA11",
#             "src.moduleA.submoduleA2.fileA2": "fileA2",
#             "src.moduleB.submoduleB1": "B1",
#             "src.moduleB.fileB": "fileB",
#             "src.moduleB.submoduleB1.fileB1": "fileB1",
#             "src.moduleB.submoduleB1.fileB2": "fileB2",
#             "src.moduleC.fileC": "fileC",
#         },
#     )
#     plt.savefig("test.png")


def test_edges_correctly_calculated_for_level_2_module_path() -> None:
    level_2_graph = get_evaluable_architecture(
        os.path.dirname(test_project.__file__),
        os.path.dirname(moduleA.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    assert len(level_2_graph._graph._graph.edges) == 0  # no internal dependencies left


def test_edges_correctly_calculated_for_level_2_module_path_no_external_dependencies_modified() -> None:
    level_2_graph = get_evaluable_architecture(
        os.path.dirname(test_project.__file__),
        os.path.dirname(moduleA.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
        exclude_external_libraries=False,
    )

    assert len(level_2_graph._graph._graph.edges) == 16

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
        assert edge in level_2_graph._graph


def test_edges_correctly_calculated_for_level_3_module_path() -> None:
    level_3_graph = get_evaluable_architecture(
        os.path.dirname(test_project.__file__),
        os.path.dirname(submoduleA1.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    assert len(level_3_graph._graph._graph.edges) == 0  # no internal dependencies left


def test_edges_correctly_calculated_for_level_3_module_path_no_external_dependencies_modified() -> None:
    level_3_graph = get_evaluable_architecture(
        os.path.dirname(test_project.__file__),
        os.path.dirname(submoduleA1.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
        exclude_external_libraries=False,
    )

    assert len(level_3_graph._graph._graph.edges) == 7

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
        assert edge in level_3_graph._graph
