from pytestarch import EvaluableArchitecture
from pytestarch.query_language.base_language import RuleApplier


class MultipleRuleApplier(RuleApplier):
    def __init__(self, rule_appliers: list[RuleApplier]) -> None:
        self._rule_appliers = rule_appliers

    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        error_messages = []

        for rule_applier in self._rule_appliers:
            try:
                rule_applier.assert_applies(evaluable)
            except AssertionError as e:
                error_messages.append(e.args[0])

        if error_messages:
            raise AssertionError("\n".join(error_messages))