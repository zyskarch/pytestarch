import pytest

# from matplotlib import pyplot as plt
# from matplotlib.pyplot import figure

from pytestarch.eval_structure.eval_structure_types import EvaluableArchitecture
from pytestarch.query_language.base_language import Rule

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
        True,
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
        False,
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
        True,
        False,
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
