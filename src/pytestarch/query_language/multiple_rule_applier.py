from __future__ import annotations

from typing import List

from pytestarch import EvaluableArchitecture
from pytestarch.query_language.base_language import RuleApplier


class MultipleRuleApplier(RuleApplier):
    def __init__(self, rule_appliers: List[RuleApplier]) -> None:
        self._rule_appliers = rule_appliers

    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        """Checks a number of rules against the given evaluable and returns an aggregated error message if at least
        one tests fails.

        Args:
            evaluable:

        """
        error_messages = []

        for rule_applier in self._rule_appliers:
            try:
                rule_applier.assert_applies(evaluable)
            except AssertionError as e:
                error_messages.append(e.args[0])

        if error_messages:
            raise AssertionError("\n".join(error_messages))
