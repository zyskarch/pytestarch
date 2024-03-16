from __future__ import annotations

import os

import pytest
from integration.interesting_rules_for_tests import (
    partial_name_match_test_cases,
    single_rule_subject_multiple_rule_objects_error_message_test_cases,
    single_rule_subject_single_rule_object_error_message_test_cases,
)
from resources import root_module_mismatch_project
from resources.root_module_mismatch_project import app

from pytestarch import EvaluableArchitecture, Rule, get_evaluable_architecture


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
        .are_named("app.red.red")
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of("app.green")
    )

    with pytest.raises(
        AssertionError, match='"app.red.red" is imported by "app.green.green"'
    ):
        rule.assert_applies(evaluable)
