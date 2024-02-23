from __future__ import annotations

import pytest

from pytestarch import EvaluableArchitecture
from pytestarch.query_language.base_language import RuleApplier
from pytestarch.query_language.multiple_rule_applier import MultipleRuleApplier

ERROR_MESSAGE = "Rule violated"


class FulfilledRuleApplier(RuleApplier):
    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        pass


class ViolatedRuleApplier(RuleApplier):
    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        raise AssertionError(ERROR_MESSAGE)


mock_evaluable = None


def test_empty_rules_does_not_raise_error() -> None:
    applier = MultipleRuleApplier([])

    applier.assert_applies(mock_evaluable)  # type: ignore


def test_single_fulfilled_rule_does_not_raise_error() -> None:
    applier = MultipleRuleApplier([FulfilledRuleApplier()])

    applier.assert_applies(mock_evaluable)  # type: ignore


def test_multiple_fulfilled_rules_does_not_raise_error() -> None:
    applier = MultipleRuleApplier([FulfilledRuleApplier(), FulfilledRuleApplier()])

    applier.assert_applies(mock_evaluable)  # type: ignore


def test_single_violated_rule_raises_error() -> None:
    applier = MultipleRuleApplier([ViolatedRuleApplier()])

    with pytest.raises(AssertionError, match=f"{ERROR_MESSAGE}"):
        applier.assert_applies(mock_evaluable)  # type: ignore


def test_multiple_violated_rules_raises_error() -> None:
    applier = MultipleRuleApplier([ViolatedRuleApplier(), ViolatedRuleApplier()])

    with pytest.raises(AssertionError, match=f"{ERROR_MESSAGE}\n{ERROR_MESSAGE}"):
        applier.assert_applies(mock_evaluable)  # type: ignore


def test_fulfilled_and_violated_rules_raises_error() -> None:
    applier = MultipleRuleApplier([FulfilledRuleApplier(), ViolatedRuleApplier()])

    with pytest.raises(AssertionError, match=f"{ERROR_MESSAGE}"):
        applier.assert_applies(mock_evaluable)  # type: ignore
