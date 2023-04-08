from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    ExplicitlyRequestedDependenciesByBaseModules,
    LayerMapping,
    NotExplicitlyRequestedDependenciesByBaseModule,
)
from pytestarch.rule_assessment.error_message.message_generator import (
    LayerRuleViolationMessageGenerator,
    RuleViolationMessageBaseGenerator,
    RuleViolationMessageGenerator,
)
from pytestarch.rule_assessment.rule_check.behavior_requirement import (
    BehaviorRequirement,
)
from pytestarch.rule_assessment.rule_check.layer_rule_violation_detector import (
    LayerRuleViolationDetector,
)
from pytestarch.rule_assessment.rule_check.module_requirement import ModuleRequirement
from pytestarch.rule_assessment.rule_check.rule_violation_detector import (
    RuleViolationBaseDetector,
    RuleViolationDetector,
)
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

    def match(self, evaluable: EvaluableArchitecture) -> None:
        """
        Checks whether an expected behavior is exhibited by the EvaluableArchitecture.
        If there are any rule violations, will raise an error detailing the violations.

        Args:
            evaluable: object to check
        Raises:
            AssertionError
        """
        rule_violations = self._find_rule_violations(evaluable)

        if rule_violations:
            raise AssertionError(self._create_rule_violation_message(rule_violations))

    def _find_rule_violations(self, evaluable: EvaluableArchitecture) -> RuleViolations:
        # dependencies that were explicitly mentioned in the user's rule, be it as they should exist or they should not
        explicitly_requested_dependencies = self._get_explicitly_requested_dependencies(
            evaluable
        )
        # other dependencies that were found
        not_explicitly_requested_dependencies = (
            self._get_not_explicitly_requested_dependencies(evaluable)
        )

        return self._get_rule_violation_detector().get_rule_violation(
            explicitly_requested_dependencies,
            not_explicitly_requested_dependencies,
        )

    @abstractmethod
    def _get_rule_violation_detector(self) -> RuleViolationBaseDetector:
        pass

    def _create_rule_violation_message(self, rule_violations: RuleViolations) -> str:
        message_generator = self._create_rule_violation_message_generator()
        return message_generator.create_rule_violation_message(rule_violations)

    @abstractmethod
    def _create_rule_violation_message_generator(
        self,
    ) -> RuleViolationMessageBaseGenerator:
        pass

    def _get_not_explicitly_requested_dependencies(
        self, evaluable: EvaluableArchitecture
    ) -> Optional[NotExplicitlyRequestedDependenciesByBaseModule]:
        if (
            self._behavior_requirement.not_explicitly_requested_dependency_required
            or self._behavior_requirement.not_explicitly_requested_dependency_not_allowed
        ):
            if not self._module_requirement.rule_specified_with_importer_as_rule_object:
                not_explicitly_requested_dependency_check_method = (
                    evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons
                )
            else:
                not_explicitly_requested_dependency_check_method = (
                    evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents
                )

            return not_explicitly_requested_dependency_check_method(
                self._module_requirement.importers,
                self._module_requirement.importees,
            )

        return None

    def _get_explicitly_requested_dependencies(
        self,
        evaluable: EvaluableArchitecture,
    ) -> Optional[ExplicitlyRequestedDependenciesByBaseModules]:
        if (
            self._behavior_requirement.explicitly_requested_dependency_required
            or self._behavior_requirement.explicitly_requested_dependency_not_allowed
        ):
            return evaluable.get_dependencies(
                self._module_requirement.importers,
                self._module_requirement.importees,
            )

        return None


class DefaultRuleMatcher(RuleMatcher):
    """To be used for rules that operate on modules, such as "module X should not import module Y."""

    def _get_rule_violation_detector(self) -> RuleViolationBaseDetector:
        return RuleViolationDetector(
            self._module_requirement, self._behavior_requirement
        )

    def _create_rule_violation_message_generator(self) -> RuleViolationMessageGenerator:
        return RuleViolationMessageGenerator(
            self._module_requirement.rule_specified_with_importer_as_rule_subject,
        )


class LayerRuleMatcher(RuleMatcher):
    """To be used for rules that operate on layers, such as "layer X should not access layer Y.
    These types of rules differ from the DefaultRuleMatcher in that detected dependencies are interpreted differently.
    Example: Consider the rule 'modules X, Y should import module Z'. In the default case, this means that both X and Y
    have to import Z for the rule to apply to the evaluable.
    For the layer rule 'layer L containing modules X, Y should import layer M containing module Z' it is however
    sufficient for either X or Y to import Z.
    """

    def __init__(
        self,
        module_requirement: ModuleRequirement,
        behavior_requirement: BehaviorRequirement,
        layer_mapping: LayerMapping,
    ) -> None:
        super().__init__(module_requirement, behavior_requirement)
        self._layer_mapping = layer_mapping

    def _get_rule_violation_detector(self) -> RuleViolationBaseDetector:
        return LayerRuleViolationDetector(
            self._module_requirement, self._behavior_requirement, self._layer_mapping
        )

    def _create_rule_violation_message_generator(
        self,
    ) -> LayerRuleViolationMessageGenerator:
        return LayerRuleViolationMessageGenerator(
            self._module_requirement.rule_specified_with_importer_as_rule_subject,
            self._layer_mapping,
        )
