from abc import ABC, abstractmethod
from typing import Optional

from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    LaxDependenciesByBaseModule,
    StrictDependenciesByBaseModules,
)
from pytestarch.rule_assessment.error_message.message_generator import (
    RuleViolationMessageGenerator,
)
from pytestarch.rule_assessment.rule_check.behavior_requirement import (
    BehaviorRequirement,
)
from pytestarch.rule_assessment.rule_check.module_requirement import ModuleRequirement
from pytestarch.rule_assessment.rule_check.rule_violations import RuleViolations


class RuleMatcher(ABC):
    """Checks whether given modules fulfill the module and behavior requirements that have been specified for them."""

    def __init__(
        self,
        module_requirement: ModuleRequirement,
        behavior_requirement: BehaviorRequirement,
    ) -> None:
        self._module_requirement = module_requirement
        self._behavior_requirement = behavior_requirement

    @abstractmethod
    def match(self, evaluable: EvaluableArchitecture) -> None:
        """
        Checks whether an expected behavior is exhibited by the EvaluableArchitecture.
        If there are any rule violations, will raise an error detailing the violations.

        Args:
            evaluable: object to check
        Raises:
            AssertionError
        """
        raise NotImplementedError()


class DefaultRuleMatcher(RuleMatcher):
    def match(self, evaluable: EvaluableArchitecture) -> None:
        rule_violations = self._find_rule_violations(evaluable)

        if rule_violations:
            raise AssertionError(self._create_rule_violation_message(rule_violations))

    def _find_rule_violations(self, evaluable: EvaluableArchitecture) -> RuleViolations:
        strict_dependencies = self._get_strict_dependencies(evaluable)
        lax_dependencies = self._get_lax_dependencies(evaluable)

        return self._behavior_requirement.generate_rule_violation(
            strict_dependencies,
            lax_dependencies,
        )

    def _create_rule_violation_message(self, rule_violations: RuleViolations) -> str:
        message_generator = RuleViolationMessageGenerator(  # TODO
            self._module_requirement._left_hand_modules_as_specified_by_user,
            self._module_requirement._right_hand_modules_as_specified_by_user,
            self._module_requirement._right_hand_module_has_specifier,
        )
        single_violation_messages = message_generator.create_rule_violation_messages(
            rule_violations
        )
        return "\n".join(single_violation_messages)

    def _get_lax_dependencies(
        self, evaluable: EvaluableArchitecture
    ) -> Optional[LaxDependenciesByBaseModule]:
        if (
            self._behavior_requirement.lax_dependency_required
            or self._behavior_requirement.lax_dependency_not_allowed
        ):
            if not self._module_requirement.left_hand_module_has_specifier:
                lax_dependency_check_method = (
                    evaluable.any_dependencies_to_modules_other_than
                )
            else:
                lax_dependency_check_method = (
                    evaluable.any_other_dependencies_to_modules_than
                )

            return lax_dependency_check_method(
                self._module_requirement.left_hand_modules,
                self._module_requirement.right_hand_modules,
            )

        return None

    def _get_strict_dependencies(
        self,
        evaluable: EvaluableArchitecture,
    ) -> Optional[StrictDependenciesByBaseModules]:
        if (
            self._behavior_requirement.strict_dependency_required
            or self._behavior_requirement.strict_dependency_not_allowed
        ):
            return evaluable.get_dependencies(
                self._module_requirement.left_hand_modules,
                self._module_requirement.right_hand_modules,
            )

        return None
