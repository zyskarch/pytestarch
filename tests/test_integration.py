import os

import pytest
from resources.test_project import src
from resources.test_project.src import moduleA
from resources.test_project.src.moduleA import submoduleA1

from pytestarch import Rule
from pytestarch.eval_structure.evaluable_architecture import EvaluableArchitecture
from pytestarch.pytestarch import get_evaluable_architecture

# from matplotlib import pyplot as plt
# from matplotlib.pyplot import figure


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
        os.path.dirname(src.__file__),
        os.path.dirname(moduleA.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    assert len(level_2_graph._graph._graph.edges) == 0  # no internal dependencies left


def test_edges_correctly_calculated_for_level_2_module_path_no_external_dependencies_modified() -> None:
    level_2_graph = get_evaluable_architecture(
        os.path.dirname(src.__file__),
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
        os.path.dirname(src.__file__),
        os.path.dirname(submoduleA1.__file__),
        ("*__pycache__", "*__init__.py", "*Test.py"),
    )

    assert len(level_3_graph._graph._graph.edges) == 0  # no internal dependencies left


def test_edges_correctly_calculated_for_level_3_module_path_no_external_dependencies_modified() -> None:
    level_3_graph = get_evaluable_architecture(
        os.path.dirname(src.__file__),
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


C = "src.moduleC"
B = "src.moduleB"
A = "src.moduleA"
FILE_A2 = f"{A}.submoduleA2.fileA2"
FILE_C = f"{C}.fileC"
A2 = f"{A}.submoduleA2"
A1 = f"{A}.submoduleA1"
A11 = f"{A}.submoduleA1.submoduleA11"
B1_MODULE = f"{B}.submoduleB1"
B2 = f"{B}.submoduleB1.fileB2"

test_cases = [
    pytest.param(
        Rule().modules_that().are_named(C).should().import_modules_that().are_named(A),
        '"src.moduleC" does not import "src.moduleA".',
        id="named should import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should()
        .import_modules_that()
        .are_sub_modules_of(A),
        '"src.moduleC" does not import a sub module of "src.moduleA".',
        id="named should import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should()
        .import_modules_that()
        .are_named(A),
        'Sub modules of "src.moduleC" do not import "src.moduleA".',
        id="submodule should import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should()
        .import_modules_that()
        .are_sub_modules_of(A),
        'Sub modules of "src.moduleC" do not import a sub module of "src.moduleA".',
        id="submodule should import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_that()
        .are_named(B),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".',
        id="named should only import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".'
        + "\n"
        + '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="named should only import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .are_named(B),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".',
        id="submodule should only import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".'
        + "\n"
        + '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="submodule should only import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .import_modules_that()
        .are_named(A),
        '"src.moduleB.submoduleB1.submoduleB11.fileB11" imports "src.moduleA.submoduleA1.submoduleA11.fileA11',
        id="named should not import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of(A),
        '"src.moduleB.submoduleB1.submoduleB11.fileB11" imports "src.moduleA.submoduleA1.submoduleA11.fileA11".',
        id="named should not import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should_not()
        .import_modules_that()
        .are_named(A),
        '"src.moduleB.submoduleB1.submoduleB11.fileB11" imports "src.moduleA.submoduleA1.submoduleA11.fileA11".',
        id="submodule should not import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of(A),
        '"src.moduleB.submoduleB1.submoduleB11.fileB11" imports "src.moduleA.submoduleA1.submoduleA11.fileA11".',
        id="submodule should not import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_named(C),
        '"src.moduleA.submoduleA2.fileA2" does not import any module that is not "src.moduleC".',
        id="named should import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        '"src.moduleA.submoduleA2.fileA2" does not import any module that is not a sub module of "src.moduleC".',
        id="named should import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_named(C),
        'Sub modules of "src.moduleA.submoduleA2.fileA2" do not import any module that is not "src.moduleC".',
        id="submodule should import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        'Sub modules of "src.moduleA.submoduleA2.fileA2" do not import any module that is not a sub module of "src.moduleC".',
        id="submodule should import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(C),
        '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="named should only import except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="named should only import except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(C),
        '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="submodule should only import except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="submodule should only import except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(B),
        '"src.moduleC" does not import any module that is not "src.moduleB".',
        id="named should only import except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleC" does not import any module that is not a sub module of "src.moduleB".',
        id="named should only import except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(B),
        'Sub modules of "src.moduleC" do not import any module that is not "src.moduleB".',
        id="submodule should only import except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        'Sub modules of "src.moduleC" do not import any module that is not a sub module of "src.moduleB".',
        id="submodule should only import except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_named(B),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".',
        id="named should not import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".'
        + "\n"
        + '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC"',
        id="named should not import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_named(B),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".',
        id="submodule should not import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".'
        + "\n"
        + '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="submodule should not import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should()
        .be_imported_by_modules_that()
        .are_named(C),
        '"src.moduleA" is not imported by "src.moduleC".',
        id="named should be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of(C),
        '"src.moduleA" is not imported by a sub module of "src.moduleC".',
        id="named should be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .be_imported_by_modules_that()
        .are_named(C),
        'Sub modules of "src.moduleA" are not imported by "src.moduleC".',
        id="submodule should be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of(C),
        'Sub modules of "src.moduleA" are not imported by a sub module of "src.moduleC".',
        id="submodule should be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named(B),
        '"src.moduleC" is not imported by "src.moduleB".',
        id="named should only be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleC" is not imported by a sub module of "src.moduleB',
        id="named should only be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named(B),
        'Sub modules of "src.moduleC" are not imported by "src.moduleB',
        id="submodule should only be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of(B),
        'Sub modules of "src.moduleC" are not imported by a sub module of "src.moduleB',
        id="submodule should only be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_named(A),
        '"src.moduleC.fileC" is imported by "src.moduleA.fileA".\n"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2"',
        id="named should not be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(A),
        '"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2".',
        id="named should not be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_named(A),
        '"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2".',
        id="submodule should not be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(A),
        '"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2".',
        id="submodule should not be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named(A),
        '"src.moduleB" is not imported by any module that is not "src.moduleA".',
        id="named should be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(A),
        '"src.moduleB" is not imported by any module that is not a sub module of "src.moduleA".',
        id="named should be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named(A),
        'Sub modules of "src.moduleB" are not imported by any module that is not "src.moduleA".',
        id="submodule should be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(A),
        'Sub modules of "src.moduleB" are not imported by any module that is not a sub module of "src.moduleA".',
        id="submodule should be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(B2),
        '"src.moduleA.submoduleA1.submoduleA11.fileA11" is imported by "src.moduleB.submoduleB1.fileB2".',
        id="named should only be imported by except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B1_MODULE),
        '"src.moduleA.submoduleA1.submoduleA11.fileA11" is imported by "src.moduleB.submoduleB1.submoduleB11.fileB11".',
        id="named should only be imported by except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(B2),
        '"src.moduleA.submoduleA1.submoduleA11.fileA11" is imported by "src.moduleB.submoduleB1.fileB2".',
        id="submodule should only be imported by except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A1)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B1_MODULE),
        '"src.moduleA.submoduleA1.submoduleA11.fileA11" is imported by "src.moduleB.submoduleB1.submoduleB11.fileB11".',
        id="submodule should only be imported by except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(B),
        '"src.moduleA" is not imported by any module that is not "src.moduleB".',
        id="named should only be imported by except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleA" is not imported by any module that is not a sub module of "src.moduleB"',
        id="named should only be imported by except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(B),
        'Sub modules of "src.moduleA" are not imported by any module that is not "src.moduleB"',
        id="submodule should only be imported by except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B),
        'Sub modules of "src.moduleA" are not imported by any module that is not a sub module of "src.moduleB"',
        id="submodule should only be imported by except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named(FILE_A2),
        '"src.moduleC.fileC" is imported by "src.moduleA.fileA".',
        id="named should not be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(A2),
        '"src.moduleC.fileC" is imported by "src.moduleA.fileA".',
        id="named should not be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named(A2),
        '"src.moduleC.fileC" is imported by "src.moduleA.fileA".',
        id="submodule should not be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(FILE_A2),
        '"src.moduleC.fileC" is imported by "src.moduleA.fileA".'
        + "\n"
        + '"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2".',
        id="submodule should not be imported by except submodule",
    ),
    pytest.param(
        Rule().modules_that().are_named(C).should_not().be_imported_by_anything(),
        '"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2".',
        id="not be imported by anything",
    ),
    pytest.param(
        Rule().modules_that().are_named(A).should_not().import_anything(),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".',
        id="not import anything",
    ),
]


@pytest.mark.parametrize("rule, expected_error_message", test_cases)
def test_rule_violated_raises_proper_error_message(
    rule: Rule,
    expected_error_message: str,
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    with pytest.raises(AssertionError, match=expected_error_message):
        rule.assert_applies(graph_based_on_string_module_names)


multiple_rule_objects_test_cases = [
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should()
        .import_modules_that()
        .are_named([A, B]),
        '"src.moduleC" does not import "src.moduleA", "src.moduleB".',
        id="named should import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should()
        .import_modules_that()
        .are_sub_modules_of([A, B]),
        '"src.moduleC" does not import a sub module of "src.moduleA", a sub module of "src.moduleB".',
        id="named should import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should()
        .import_modules_that()
        .are_named([A]),
        'Sub modules of "src.moduleC" do not import "src.moduleA".',
        id="submodule should import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should()
        .import_modules_that()
        .are_sub_modules_of([A]),
        'Sub modules of "src.moduleC" do not import a sub module of "src.moduleA".',
        id="submodule should import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_that()
        .are_named([B, B2]),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".',
        id="named should only import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of([B, B2]),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".'
        + "\n"
        + '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="named should only import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .are_named([B]),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".',
        id="submodule should only import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of([B]),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".'
        + "\n"
        + '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="submodule should only import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .import_modules_that()
        .are_named([A, C]),
        '"src.moduleB.submoduleB1.submoduleB11.fileB11" imports "src.moduleA.submoduleA1.submoduleA11.fileA11',
        id="named should not import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of([A, C]),
        '"src.moduleB.submoduleB1.submoduleB11.fileB11" imports "src.moduleA.submoduleA1.submoduleA11.fileA11".',
        id="named should not import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should_not()
        .import_modules_that()
        .are_named([A]),
        '"src.moduleB.submoduleB1.submoduleB11.fileB11" imports "src.moduleA.submoduleA1.submoduleA11.fileA11".',
        id="submodule should not import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of([A]),
        '"src.moduleB.submoduleB1.submoduleB11.fileB11" imports "src.moduleA.submoduleA1.submoduleA11.fileA11".',
        id="submodule should not import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_named([C, FILE_C]),
        '"src.moduleA.submoduleA2.fileA2" does not import any module that is not "src.moduleC".',
        id="named should import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_sub_modules_of([C, B]),
        '"src.moduleA.submoduleA2.fileA2" does not import any module that is not a sub module of "src.moduleC", a sub module of "src.moduleB".',
        id="named should import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_named([C]),
        'Sub modules of "src.moduleA.submoduleA2.fileA2" do not import any module that is not "src.moduleC".',
        id="submodule should import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_sub_modules_of([C]),
        'Sub modules of "src.moduleA.submoduleA2.fileA2" do not import any module that is not a sub module of "src.moduleC".',
        id="submodule should import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([C, B]),
        '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="named should only import except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of([C, B]),
        '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="named should only import except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([C]),
        '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="submodule should only import except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of([C]),
        '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="submodule should only import except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([B, B2]),
        '"src.moduleC" does not import any module that is not "src.moduleB".',
        id="named should only import except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of([B, B2]),
        '"src.moduleC" does not import any module that is not a sub module of "src.moduleB".',
        id="named should only import except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([B]),
        'Sub modules of "src.moduleC" do not import any module that is not "src.moduleB".',
        id="submodule should only import except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of([B]),
        'Sub modules of "src.moduleC" do not import any module that is not a sub module of "src.moduleB".',
        id="submodule should only import except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_named([B, B2]),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".',
        id="named should not import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_sub_modules_of([B, B2]),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".'
        + "\n"
        + '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC"',
        id="named should not import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_named([B]),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".',
        id="submodule should not import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_sub_modules_of([B]),
        '"src.moduleA.fileA" imports "src.moduleC.fileC".'
        + "\n"
        + '"src.moduleA.submoduleA2.fileA2" imports "src.moduleC.fileC".',
        id="submodule should not import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should()
        .be_imported_by_modules_that()
        .are_named([C, FILE_C]),
        '"src.moduleA" is not imported by "src.moduleC", "src.moduleC.fileC".',
        id="named should be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of([C, FILE_C]),
        '"src.moduleA" is not imported by a sub module of "src.moduleC", a sub module of "src.moduleC.fileC".',
        id="named should be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .be_imported_by_modules_that()
        .are_named([C]),
        'Sub modules of "src.moduleA" are not imported by "src.moduleC".',
        id="submodule should be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of([C]),
        'Sub modules of "src.moduleA" are not imported by a sub module of "src.moduleC".',
        id="submodule should be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named([B, B2]),
        '"src.moduleC" is not imported by "src.moduleB", "src.moduleB.submoduleB1.fileB2".',
        id="named should only be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of([B]),
        '"src.moduleC" is not imported by a sub module of "src.moduleB',
        id="named should only be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named([B]),
        'Sub modules of "src.moduleC" are not imported by "src.moduleB',
        id="submodule should only be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of([B]),
        'Sub modules of "src.moduleC" are not imported by a sub module of "src.moduleB',
        id="submodule should only be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_named([A, FILE_A2]),
        '"src.moduleC.fileC" is imported by "src.moduleA.fileA".'
        + "\n"
        + '"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2".',
        id="named should not be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of([A]),
        '"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2".',
        id="named should not be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_named([A]),
        '"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2".',
        id="submodule should not be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of([A]),
        '"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2".',
        id="submodule should not be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named([A, A2]),
        '"src.moduleB" is not imported by any module that is not "src.moduleA", "src.moduleA.submoduleA2".',
        id="named should be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([A]),
        '"src.moduleB" is not imported by any module that is not a sub module of "src.moduleA".',
        id="named should be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named([A]),
        'Sub modules of "src.moduleB" are not imported by any module that is not "src.moduleA".',
        id="submodule should be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([A]),
        'Sub modules of "src.moduleB" are not imported by any module that is not a sub module of "src.moduleA".',
        id="submodule should be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([B2, B]),
        '"src.moduleA.submoduleA1.submoduleA11.fileA11" is imported by "src.moduleB.submoduleB1.fileB2".',
        id="named should only be imported by except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([B1_MODULE, B]),
        '"src.moduleA.submoduleA1.submoduleA11.fileA11" is imported by "src.moduleB.submoduleB1.submoduleB11.fileB11".',
        id="named should only be imported by except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([B2]),
        '"src.moduleA.submoduleA1.submoduleA11.fileA11" is imported by "src.moduleB.submoduleB1.fileB2".',
        id="submodule should only be imported by except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A1)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([B1_MODULE]),
        '"src.moduleA.submoduleA1.submoduleA11.fileA11" is imported by "src.moduleB.submoduleB1.submoduleB11.fileB11".',
        id="submodule should only be imported by except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([B, B2]),
        '"src.moduleA" is not imported by any module that is not "src.moduleB", "src.moduleB.submoduleB1.',
        id="named should only be imported by except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([B]),
        '"src.moduleA" is not imported by any module that is not a sub module of "src.moduleB"',
        id="named should only be imported by except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([B]),
        'Sub modules of "src.moduleA" are not imported by any module that is not "src.moduleB"',
        id="submodule should only be imported by except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([B]),
        'Sub modules of "src.moduleA" are not imported by any module that is not a sub module of "src.moduleB"',
        id="submodule should only be imported by except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named([FILE_A2, B]),
        '"src.moduleC.fileC" is imported by "src.moduleA.fileA".',
        id="named should not be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([A2]),
        '"src.moduleC.fileC" is imported by "src.moduleA.fileA".',
        id="named should not be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named([A2]),
        '"src.moduleC.fileC" is imported by "src.moduleA.fileA".',
        id="submodule should not be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([FILE_A2]),
        '"src.moduleC.fileC" is imported by "src.moduleA.fileA".'
        + "\n"
        + '"src.moduleC.fileC" is imported by "src.moduleA.submoduleA2.fileA2".',
        id="submodule should not be imported by except submodule",
    ),
]


@pytest.mark.parametrize(
    "rule, expected_error_message", multiple_rule_objects_test_cases
)
def test_rule_violated_with_multiple_rule_objects_raises_proper_error_message(
    rule: Rule,
    expected_error_message: str,
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    with pytest.raises(AssertionError, match=expected_error_message):
        rule.assert_applies(graph_based_on_string_module_names)


partial_name_match_test_cases = [
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("*moduleC*")
        .should()
        .import_modules_that()
        .are_sub_modules_of([A, B]),
        True,
        id="named should import submodule - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .have_name_containing("*leB*"),
        True,
        id="submodule should only import named - partial name match object",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("*moduleB")
        .should_not()
        .import_modules_that()
        .are_named([A, C]),
        True,
        id="named should not import named - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("src.moduleA*")
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of([C, B]),
        True,
        id="named should only import except submodule - forbidden import - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .have_name_containing("*moduleB*"),
        True,
        id="submodule should only import except named - no import - partial name match object",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("*duleA*")
        .should_not()
        .import_modules_except_modules_that()
        .are_named([B, B2]),
        True,
        id="named should not import except named - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("*moduleA*")
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of([C, FILE_C]),
        True,
        id="named should be imported by submodule - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .have_name_containing(["*leB"]),
        True,
        id="submodule should only be imported by named - partial name match object",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("*moduleC*")
        .should_not()
        .be_imported_by_modules_that()
        .are_named([A, FILE_A2]),
        True,
        id="named should not be imported by named - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .have_name_containing(["*fileB2"]),
        True,
        id="submodule should only be imported by except named - forbidden import - partial name match object",
    ),
]


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
