from __future__ import annotations

from abc import ABC, abstractmethod

from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    ExplicitlyRequestedDependenciesByBaseModules,
    Layer,
    LayerMapping,
    Module,
    ModuleGroup,
    NotExplicitlyRequestedDependenciesByBaseModule,
)
from pytestarch.eval_structure.module_name_converter import ModuleNameConverter
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
        self._updated_module_requirements(evaluable)
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

        regex_conversion_mapping = self._create_module_name_regex_conversion_mapping()

        return self._get_rule_violation_detector(
            regex_conversion_mapping
        ).get_rule_violation(
            explicitly_requested_dependencies,
            not_explicitly_requested_dependencies,
        )

    @abstractmethod
    def _get_rule_violation_detector(
        self, module_name_conversion_mapping: dict[str, list[Module]]
    ) -> RuleViolationBaseDetector:
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
    ) -> NotExplicitlyRequestedDependenciesByBaseModule | None:
        if (
            self._behavior_requirement.not_explicitly_requested_dependency_required
            or self._behavior_requirement.not_explicitly_requested_dependency_not_allowed
        ):
            if (
                not self._updated_module_requirement.rule_specified_with_importer_as_rule_object
            ):
                not_explicitly_requested_dependency_check_method = (
                    evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons
                )
            else:
                not_explicitly_requested_dependency_check_method = (
                    evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents
                )

            return not_explicitly_requested_dependency_check_method(
                self._updated_module_requirement.importers,
                self._updated_module_requirement.importees,
            )

        return None

    def _get_explicitly_requested_dependencies(
        self,
        evaluable: EvaluableArchitecture,
    ) -> ExplicitlyRequestedDependenciesByBaseModules | None:
        if (
            self._behavior_requirement.explicitly_requested_dependency_required
            or self._behavior_requirement.explicitly_requested_dependency_not_allowed
        ):
            return evaluable.get_dependencies(
                self._updated_module_requirement.importers,
                self._updated_module_requirement.importees,
            )

        return None

    def _updated_module_requirements(self, evaluable: EvaluableArchitecture) -> None:
        """There may be modules specified via regexes. Before starting the evaluation of the rule, convert these regexes
        to actual module names."""
        (
            converted_importers,
            self._conversion_mapping_importers,
        ) = ModuleNameConverter.convert(
            self._module_requirement.importers_as_specified_by_user, evaluable
        )
        (
            converted_importees,
            self._conversion_mapping_importees,
        ) = ModuleNameConverter.convert(
            self._module_requirement.importees_as_specified_by_user, evaluable
        )

        self._updated_module_requirement = ModuleRequirement(
            converted_importers,
            converted_importees,
            self._module_requirement.rule_specified_with_importer_as_rule_subject,
        )

    def _create_module_name_regex_conversion_mapping(self) -> dict[str, list[Module]]:
        """Maps between a regex and the actual modules it represents."""

        result = {
            key: values for key, values in self._conversion_mapping_importers.items()
        }

        for key, values in self._conversion_mapping_importees.items():
            if key not in result:
                result[key] = values
            else:
                existing_values = set(result[key])
                existing_values.update(set(values))

                result[key] = list(existing_values)

        return result


class DefaultRuleMatcher(RuleMatcher):
    """To be used for rules that operate on modules, such as "module X should not import module Y."""

    def _get_rule_violation_detector(
        self, _: dict[str, list[Module]]
    ) -> RuleViolationBaseDetector:
        return RuleViolationDetector(
            self._updated_module_requirement, self._behavior_requirement
        )

    def _create_rule_violation_message_generator(self) -> RuleViolationMessageGenerator:
        return RuleViolationMessageGenerator(
            self._updated_module_requirement.rule_specified_with_importer_as_rule_subject,
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

    def _get_rule_violation_detector(
        self, module_name_conversion_mapping: dict[str, list[Module]]
    ) -> RuleViolationBaseDetector:
        self._updated_layer_mapping = self._update_layer_mapping(
            self._layer_mapping, module_name_conversion_mapping
        )
        return LayerRuleViolationDetector(
            self._updated_module_requirement,
            self._behavior_requirement,
            self._updated_layer_mapping,
        )

    def _create_rule_violation_message_generator(
        self,
    ) -> LayerRuleViolationMessageGenerator:
        return LayerRuleViolationMessageGenerator(
            self._updated_module_requirement.rule_specified_with_importer_as_rule_subject,
            self._updated_layer_mapping,
        )

    @classmethod
    def _update_layer_mapping(
        cls,
        layer_mapping: LayerMapping,
        module_name_conversion_mapping: dict[str, list[Module]],
    ) -> LayerMapping:
        return LayerMapping(
            {
                layer: LayerRuleMatcher._replace_regex_specified_modules_with_actual_modules(
                    layer, layer_mapping, module_name_conversion_mapping
                )
                for layer in layer_mapping.all_layers
            }
        )

    @classmethod
    def _replace_regex_specified_modules_with_actual_modules(
        cls,
        layer: Layer,
        layer_mapping: LayerMapping,
        module_name_conversion_mapping: dict[str, list[Module]],
    ) -> list[Module]:
        modules_potentially_with_regexes = layer_mapping.get_module_filters(layer)

        result = []
        for module in modules_potentially_with_regexes:
            if not module.identifier_is_regex:
                result.append(
                    ModuleGroup(identifier=module.identifier)
                    if module.identifier_is_parent_module
                    else Module(identifier=module.identifier)
                )

            else:
                result = result + module_name_conversion_mapping[module.identifier]

        return result
