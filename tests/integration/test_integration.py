from __future__ import annotations

import os

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
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport
from resources import nested_root_module_mismatch_project, root_module_mismatch_project
from resources.nested_root_module_mismatch_project.dir1.dir2 import nested_app
from resources.root_module_mismatch_project import app


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
