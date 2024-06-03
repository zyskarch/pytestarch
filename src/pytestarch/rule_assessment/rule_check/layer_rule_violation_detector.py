from __future__ import annotations

from collections import defaultdict
from typing import Any

from pytestarch.eval_structure.evaluable_architecture import (
    Dependency,
    ExplicitlyRequestedDependenciesByBaseModules,
    Layer,
    LayerMapping,
    Module,
    NotExplicitlyRequestedDependenciesByBaseModule,
)
from pytestarch.rule_assessment.rule_check.behavior_requirement import (
    BehaviorRequirement,
)
from pytestarch.rule_assessment.rule_check.module_requirement import ModuleRequirement
from pytestarch.rule_assessment.rule_check.rule_violation_detector import (
    RuleViolationBaseDetector,
)


class LayerRuleViolationDetector(RuleViolationBaseDetector):
    """Detects violation of a layer rule based on the rule and detected dependencies relevant to this rule.
    Compared to the regular RuleViolationDetector, this detector is more lenient: For example, for a rule in the style
    of "layer X should import layer Y", it is sufficient if only one module from layer X imports something from layer
    Y. The regular detector would instead require all modules from layer X to import something from layer Y.
    """

    def __init__(
        self,
        module_requirement: ModuleRequirement,
        behavior_requirement: BehaviorRequirement,
        layer_mapping: LayerMapping,
    ) -> None:
        super().__init__(module_requirement, behavior_requirement)
        self._layer_to_module_mapping = layer_mapping

    def _should_not_requirement_violations(
        self,
        explicitly_requested_dependencies_should_not_be_present: bool,
        explicitly_requested_dependencies: (
            ExplicitlyRequestedDependenciesByBaseModules | None
        ),
    ) -> set[Dependency]:
        if (
            explicitly_requested_dependencies is None
            or not explicitly_requested_dependencies_should_not_be_present
        ):
            return set()

        return self._get_realised_dependencies(explicitly_requested_dependencies)

    def _should_requirement_violations(
        self,
        explicitly_requested_dependencies_should_be_present: bool,
        explicitly_requested_dependencies: (
            ExplicitlyRequestedDependenciesByBaseModules | None
        ),
    ) -> set[Dependency]:
        if (
            explicitly_requested_dependencies is None
            or not explicitly_requested_dependencies_should_be_present
        ):
            return set()

        return self._get_abstract_dependencies_without_any_realisations(
            explicitly_requested_dependencies
        )

    def _should_only_requirement_violations_by_no_import(
        self,
        explicitly_requested_dependencies_and_no_other_should_be_present: bool,
        explicitly_requested_dependencies: (
            ExplicitlyRequestedDependenciesByBaseModules | None
        ),
    ) -> set[Dependency]:
        if (
            explicitly_requested_dependencies is None
            or not explicitly_requested_dependencies_and_no_other_should_be_present
        ):
            return set()

        return self._get_abstract_dependencies_without_any_realisations(
            explicitly_requested_dependencies
        )

    def _should_only_requirement_violations_by_not_explicitly_requested_dependency(
        self,
        explicitly_requested_dependencies_and_no_other_should_be_present: bool,
        not_explicitly_requested_dependencies: (
            NotExplicitlyRequestedDependenciesByBaseModule | None
        ),
    ) -> set[Dependency]:
        if (
            not_explicitly_requested_dependencies is None
            or not explicitly_requested_dependencies_and_no_other_should_be_present
        ):
            return set()

        return self._get_realised_dependencies(not_explicitly_requested_dependencies)

    def _should_except_requirement_violations(
        self,
        at_least_one_not_explicitly_requested_dependency_should_be_present: bool,
        not_explicitly_requested_dependencies: (
            NotExplicitlyRequestedDependenciesByBaseModule | None
        ),
    ) -> set[Dependency]:
        if (
            not_explicitly_requested_dependencies is None
            or not at_least_one_not_explicitly_requested_dependency_should_be_present
        ):
            return set()

        return self._get_any_missing_dependencies_in_user_specified_order(
            not_explicitly_requested_dependencies
        )

    def _should_only_except_requirement_violations_due_to_no_other_imports(
        self,
        explicitly_requested_dependency_should_not_but_others_should_be_present: bool,
        not_explicitly_requested_dependencies: (
            NotExplicitlyRequestedDependenciesByBaseModule | None
        ),
    ) -> set[Dependency]:
        if (
            not_explicitly_requested_dependencies is None
            or not explicitly_requested_dependency_should_not_but_others_should_be_present
        ):
            return set()

        return self._get_any_missing_dependencies_in_user_specified_order(
            not_explicitly_requested_dependencies
        )

    def _should_only_except_requirement_violations_due_to_explicit_dependency_present(
        self,
        explicitly_requested_dependency_should_not_but_others_should_be_present: bool,
        explicitly_requested_dependencies: (
            ExplicitlyRequestedDependenciesByBaseModules | None
        ),
    ) -> set[Dependency]:
        if (
            explicitly_requested_dependencies is None
            or not explicitly_requested_dependency_should_not_but_others_should_be_present
        ):
            return set()

        return self._get_realised_dependencies(explicitly_requested_dependencies)

    def _should_not_except_requirement_violations(
        self,
        not_explicitly_requested_dependencies_should_not_be_present: bool,
        not_explicitly_requested_dependencies: (
            NotExplicitlyRequestedDependenciesByBaseModule | None
        ),
    ) -> set[Dependency]:
        if (
            not_explicitly_requested_dependencies is None
            or not not_explicitly_requested_dependencies_should_not_be_present
        ):
            return set()

        return self._get_realised_dependencies(not_explicitly_requested_dependencies)

    def _get_abstract_dependencies_without_any_realisations(
        self,
        explicitly_requested_dependencies: dict[Dependency, list[Dependency]],
    ) -> set[Dependency]:
        """If there is any explicitly requested dependency for each rule object, an empty list will be returned. If there is none at all for at least one rule object,
        all dependencies will be returned."""
        explicitly_requested_dependencies_by_layers = (
            self._group_explicitly_requested_dependencies_by_layers(
                explicitly_requested_dependencies
            )
        )

        result: set[tuple[Module, Module]] = set()  # type: ignore

        for layer in self._layer_to_module_mapping.all_layers:
            explicitly_requested_dependencies_for_layer = (
                explicitly_requested_dependencies_by_layers[layer]
            )

            if not explicitly_requested_dependencies_for_layer:
                continue

            if any(
                len(concrete_dependencies) > 0
                for concrete_dependencies in explicitly_requested_dependencies_for_layer.values()
            ):
                continue

            result.update(
                {
                    self._get_rule_subject_and_object_in_user_specified_order(
                        dependency
                    )
                    for dependency in explicitly_requested_dependencies_for_layer.keys()
                }
            )
        return result

    def _get_any_missing_dependencies_in_user_specified_order(
        self,
        not_explicitly_requested_dependencies: NotExplicitlyRequestedDependenciesByBaseModule,
    ) -> set[Dependency]:
        """If no not explicitly requested dependency is present, all possible not present dependencies will be
        returned. If there is one dependency per rule subject, an empty list will be returned.
        """
        if any(
            len(not_explicitly_requested_dependencies_of_module) > 0
            for not_explicitly_requested_dependencies_of_module in not_explicitly_requested_dependencies.values()
        ):
            return set()

        dependencies = self._append_missing_dependencies(
            not_explicitly_requested_dependencies
        )

        return {
            self._get_rule_subject_and_object_in_user_specified_order(dependency)
            for dependency in dependencies
        }

    def _append_missing_dependencies(
        self,
        not_explicitly_requested_dependencies: NotExplicitlyRequestedDependenciesByBaseModule,
    ) -> list[Dependency]:
        dependencies = []

        for (
            module_with_missing_dependencies
        ) in not_explicitly_requested_dependencies.keys():
            if self._module_requirement.rule_specified_with_importer_as_rule_subject:
                for other_module in self._get_importee_modules_as_specified_by_user():
                    dependencies.append(
                        (module_with_missing_dependencies, other_module)
                    )
            else:
                for other_module in self._get_importee_modules_as_specified_by_user():
                    dependencies.append(
                        (other_module, module_with_missing_dependencies)
                    )

        return dependencies

    def _group_explicitly_requested_dependencies_by_layers(
        self,
        explicitly_requested_dependencies: ExplicitlyRequestedDependenciesByBaseModules,
    ) -> defaultdict[Layer, ExplicitlyRequestedDependenciesByBaseModules]:
        result: defaultdict[Layer, ExplicitlyRequestedDependenciesByBaseModules] = (
            defaultdict(dict)
        )

        for (
            abstract_dependency,
            concrete_dependencies,
        ) in explicitly_requested_dependencies.items():
            relevant_module_for_layer = self._get_module_relevant_for_layer(
                abstract_dependency
            )
            layer = self._get_layer_for_module(relevant_module_for_layer)

            result[layer][abstract_dependency] = concrete_dependencies

        return result

    def _get_module_relevant_for_layer(self, dependency: Dependency) -> Module:
        if self._module_requirement.rule_specified_with_importer_as_rule_subject:
            return dependency[1]

        return dependency[0]

    def _get_layer_for_module(self, module: Module) -> Layer:
        return self._layer_to_module_mapping.get_layer_for_module_name(  # type: ignore
            module.identifier
        )

    def _get_realised_dependencies(
        self, explicitly_requested_dependencies: dict[Any, list[Dependency]]
    ) -> set[Dependency]:
        """Removes all dependencies between modules of the same layer, as these are one logical unit."""
        violating_dependencies = super()._get_realised_dependencies(
            explicitly_requested_dependencies
        )

        violating_dependencies_in_different_layers = set()
        for dependency in violating_dependencies:
            rule_subject_layer = (
                self._layer_to_module_mapping.get_layer_for_module_name(
                    dependency[0].identifier
                )
            )
            rule_object_layer = self._layer_to_module_mapping.get_layer_for_module_name(
                dependency[1].identifier
            )

            if rule_subject_layer != rule_object_layer:
                violating_dependencies_in_different_layers.add(dependency)

        return violating_dependencies_in_different_layers
