from __future__ import annotations

import pytest

from pytestarch import Rule
from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    Module,
)
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.query_language.rule import RuleConfiguration
from query_language.rule.conftest import MODULE_1, MODULE_2


def test_rule_to_str_as_expected() -> None:
    rule = Rule()

    rule.modules_that().are_named(
        "A name"
    ).should().import_modules_that().are_sub_modules_of("Module 1")

    rule_as_str = str(rule)

    assert (
        rule_as_str
        == '"A name" should import modules that are sub modules of "Module 1".'
    )


def test_sub_modules_identification() -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of("A name")

    assert len(rule.rule_subjects) == 1
    assert rule.rule_subjects[0].name is None
    assert rule.rule_subjects[0].parent_module == "A name"


def test_module_name_identification() -> None:
    rule = Rule()

    rule.modules_that().are_named("A name")

    assert len(rule.rule_subjects) == 1
    assert rule.rule_subjects[0].name == "A name"
    assert rule.rule_subjects[0].parent_module is None


def test_partially_configured_rule_raises_error(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a RuleSubject, a BehaviorSpecification, "
        "a DependencySpecification, a RuleObject.",
    ):
        rule.assert_applies(evaluable1)

    x = rule.modules_that()

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a RuleSubject, a BehaviorSpecification, "
        "a DependencySpecification, a RuleObject.",
    ):
        rule.assert_applies(evaluable1)

    y = x.are_named(MODULE_1)

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a BehaviorSpecification, a "
        "DependencySpecification, a RuleObject.",
    ):
        rule.assert_applies(evaluable1)

    z = y.should()

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a DependencySpecification, a RuleObject.",
    ):
        rule.assert_applies(evaluable1)

    a = z.import_modules_that()

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a RuleObject.",
    ):
        rule.assert_applies(evaluable1)

    a.are_named(MODULE_2)

    rule.assert_applies(evaluable1)

    assert True


def assert_rule_applies(rule: Rule, evaluable: EvaluableArchitecture) -> None:
    rule.assert_applies(evaluable)


def assert_rule_does_not_apply(rule: Rule, evaluable: EvaluableArchitecture) -> None:
    with pytest.raises(AssertionError):
        rule.assert_applies(evaluable)


def test_only_submodules_are_filtered_out() -> None:
    module_names = ["X.a", "X.b", "X.a.a", "X.a.b", "Y"]
    modules = [Module(name=name) for name in module_names]

    rule_configuration = RuleConfiguration(modules_to_check=modules)

    modules_without_submodules = (
        Rule._get_modules_to_check_without_parent_and_submodule_combinations(
            rule_configuration
        )
    )

    assert list(map(lambda module: module.name, modules_without_submodules)) == [
        "X.a",
        "X.b",
        "Y",
    ]
