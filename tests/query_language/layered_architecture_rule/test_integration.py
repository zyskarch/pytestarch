from __future__ import annotations

import re
from typing import Dict, List

import pytest

from integration.interesting_rules_for_tests import (
    LayerRuleSetup,
    LayerRuleTestCase,
    fulfilled_layer_rule_test_cases,
    layer_rule_error_messages_test_cases,
)
from pytestarch import EvaluableArchitecture, LayeredArchitecture, LayerRule


def _get_layered_architecture(layers: Dict[str, List[str]]) -> LayeredArchitecture:
    arch = LayeredArchitecture()

    for layer, modules in layers.items():
        arch.layer(layer).containing_modules(modules)

    return arch


def _get_layer_rule(rule_setup: LayerRuleSetup, arch: LayeredArchitecture) -> LayerRule:
    rule = LayerRule().based_on(arch)
    rule = rule.layers_that().are_named(rule_setup.importer)

    behavior_fn = getattr(rule, rule_setup.behavior)
    rule = behavior_fn()

    access_type_fn = getattr(rule, rule_setup.access_type)
    rule = access_type_fn()

    if rule_setup.importee:
        rule = rule.are_named(rule_setup.importee)

    return rule


@pytest.mark.parametrize(
    "test_case",
    fulfilled_layer_rule_test_cases,
)
def test_fulfilled_rules_as_excepted(
    test_case: LayerRuleTestCase,
    flat_project_1: EvaluableArchitecture,
) -> None:
    arch = _get_layered_architecture(test_case.layers)
    rule = _get_layer_rule(test_case.rule_setup, arch)

    rule.assert_applies(flat_project_1)


@pytest.mark.parametrize(
    "test_case",
    layer_rule_error_messages_test_cases,
)
def test_rule_violated_raises_proper_error_message(
    test_case: LayerRuleTestCase,
    flat_project_1: EvaluableArchitecture,
) -> None:
    arch = _get_layered_architecture(test_case.layers)
    rule = _get_layer_rule(test_case.rule_setup, arch)

    with pytest.raises(
        AssertionError, match=re.escape(test_case.expected_error_message)
    ):
        rule.assert_applies(flat_project_1)
