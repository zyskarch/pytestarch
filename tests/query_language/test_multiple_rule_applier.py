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


@pytest.mark.parametrize(
    "appliers, expected_error_message",
    [
        pytest.param([FulfilledRuleApplier()], None, id="single_fulfilled"),
        pytest.param(
            [FulfilledRuleApplier(), FulfilledRuleApplier()],
            None,
            id="multiple_fulfilled",
        ),
        pytest.param([ViolatedRuleApplier()], ERROR_MESSAGE, id="single_violated"),
        pytest.param(
            [ViolatedRuleApplier(), ViolatedRuleApplier()],
            f"{ERROR_MESSAGE}\n{ERROR_MESSAGE}",
            id="multiple_violated",
        ),
    ],
)
def test_violated_rules_raise_error_with_all_violations_reported(
    appliers: list[RuleApplier],
    expected_error_message: str | None,
) -> None:
    applier = MultipleRuleApplier(appliers)

    if expected_error_message is None:
        applier.assert_applies(mock_evaluable)  # type: ignore
    else:
        with pytest.raises(AssertionError, match=expected_error_message):
            applier.assert_applies(mock_evaluable)  # type: ignore


def test_fulfilled_and_violated_rules_raises_error() -> None:
    applier = MultipleRuleApplier([FulfilledRuleApplier(), ViolatedRuleApplier()])

    with pytest.raises(AssertionError, match=f"{ERROR_MESSAGE}"):
        applier.assert_applies(mock_evaluable)  # type: ignore
