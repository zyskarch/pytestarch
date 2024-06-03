from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from pytestarch.eval_structure.evaluable_architecture import (
    Dependency,
    ExplicitlyRequestedDependenciesByBaseModules,
    NotExplicitlyRequestedDependenciesByBaseModule,
)
from pytestarch.eval_structure.utils import filter_to_module
from pytestarch.rule_assessment.rule_check.behavior_requirement import (
    BehaviorRequirement,
)
from pytestarch.rule_assessment.rule_check.module_requirement import ModuleRequirement
from pytestarch.rule_assessment.rule_check.rule_violations import RuleViolations


@dataclass
class DependencyExpectation:
    not_explicitly_requested_dependencies_should_not_be_present: bool
    explicitly_requested_dependencies_should_not_be_present: bool
    explicitly_requested_dependencies_and_no_other_should_be_present: bool
    explicitly_requested_dependencies_should_not_but_others_should_be_present: bool
    at_least_one_not_explicitly_requested_dependency_should_be_present: bool
    explicitly_requested_dependencies_should_be_present: bool


class RuleViolationBaseDetector(ABC):
    """Base class for all classes that detect inconsistencies between the dependencies found within the evaluable
    architecture and the module and behavior requirements.
    """

    def __init__(
        self,
        module_requirement: ModuleRequirement,
        behavior_requirement: BehaviorRequirement,
    ) -> None:
        self._module_requirement = module_requirement
        self._behavior_requirement = behavior_requirement

    def get_rule_violation(
        self,
        explicitly_requested_dependencies: (
            ExplicitlyRequestedDependenciesByBaseModules | None
        ),
        not_explicitly_requested_dependencies: (
            NotExplicitlyRequestedDependenciesByBaseModule | None
        ),
    ) -> RuleViolations:
        """Translate from the detected types of dependencies back to which behavior and dependency requirements are violated by them.
        Args:
            explicitly_requested_dependencies: dependency between the specified modules found, grouped by requested modules
            not_explicitly_requested_dependencies: other dependencies found beside the specified modules
        Returns:
            overview of all rule violations
        """
        dependency_expectations = self._get_dependency_expectations()

        return RuleViolations(
            should_not_violations=self._should_not_requirement_violations(
                dependency_expectations.explicitly_requested_dependencies_should_not_be_present,
                explicitly_requested_dependencies,
            ),
            should_violations=self._should_requirement_violations(
                dependency_expectations.explicitly_requested_dependencies_should_be_present,
                explicitly_requested_dependencies,
            ),
            should_only_violations_by_no_import=self._should_only_requirement_violations_by_no_import(
                dependency_expectations.explicitly_requested_dependencies_and_no_other_should_be_present,
                explicitly_requested_dependencies,
            ),
            should_only_violations_by_forbidden_import=self._should_only_requirement_violations_by_not_explicitly_requested_dependency(
                dependency_expectations.explicitly_requested_dependencies_and_no_other_should_be_present,
                not_explicitly_requested_dependencies,
            ),
            should_except_violations=self._should_except_requirement_violations(
                dependency_expectations.at_least_one_not_explicitly_requested_dependency_should_be_present,
                not_explicitly_requested_dependencies,
            ),
            should_only_except_violations_by_no_import=self._should_only_except_requirement_violations_due_to_no_other_imports(
                dependency_expectations.explicitly_requested_dependencies_should_not_but_others_should_be_present,
                not_explicitly_requested_dependencies,
            ),
            should_only_except_violations_by_forbidden_import=self._should_only_except_requirement_violations_due_to_explicit_dependency_present(
                dependency_expectations.explicitly_requested_dependencies_should_not_but_others_should_be_present,
                explicitly_requested_dependencies,
            ),
            should_not_except_violations=self._should_not_except_requirement_violations(
                dependency_expectations.not_explicitly_requested_dependencies_should_not_be_present,
                not_explicitly_requested_dependencies,
            ),
        )

    @abstractmethod
    def _should_not_requirement_violations(
        self,
        explicitly_requested_dependencies_should_not_be_present: bool,
        explicitly_requested_dependencies: (
            ExplicitlyRequestedDependenciesByBaseModules | None
        ),
    ) -> set[Dependency]:
        pass

    @abstractmethod
    def _should_requirement_violations(
        self,
        explicitly_requested_dependencies_should_be_present: bool,
        explicitly_requested_dependencies: (
            ExplicitlyRequestedDependenciesByBaseModules | None
        ),
    ) -> set[Dependency]:
        pass

    @abstractmethod
    def _should_only_requirement_violations_by_no_import(
        self,
        explicitly_requested_dependencies_and_no_other_should_be_present: bool,
        explicitly_requested_dependencies: (
            ExplicitlyRequestedDependenciesByBaseModules | None
        ),
    ) -> set[Dependency]:
        pass

    @abstractmethod
    def _should_only_requirement_violations_by_not_explicitly_requested_dependency(
        self,
        explicitly_requested_dependencies_and_no_other_should_be_present: bool,
        not_explicitly_requested_dependencies: (
            NotExplicitlyRequestedDependenciesByBaseModule | None
        ),
    ) -> set[Dependency]:
        pass

    @abstractmethod
    def _should_except_requirement_violations(
        self,
        at_least_one_not_explicitly_requested_dependency_should_be_present: bool,
        not_explicitly_requested_dependencies: (
            NotExplicitlyRequestedDependenciesByBaseModule | None
        ),
    ) -> set[Dependency]:
        pass

    @abstractmethod
    def _should_only_except_requirement_violations_due_to_no_other_imports(
        self,
        explicitly_requested_dependency_should_not_but_others_should_be_present: bool,
        not_explicitly_requested_dependencies: (
            NotExplicitlyRequestedDependenciesByBaseModule | None
        ),
    ) -> set[Dependency]:
        pass

    @abstractmethod
    def _should_only_except_requirement_violations_due_to_explicit_dependency_present(
        self,
        explicitly_requested_dependency_should_not_but_others_should_be_present: bool,
        explicitly_requested_dependencies: (
            ExplicitlyRequestedDependenciesByBaseModules | None
        ),
    ) -> set[Dependency]:
        pass

    @abstractmethod
    def _should_not_except_requirement_violations(
        self,
        not_explicitly_requested_dependencies_should_not_be_present: bool,
        not_explicitly_requested_dependencies: (
            NotExplicitlyRequestedDependenciesByBaseModule | None
        ),
    ) -> set[Dependency]:
        pass

    def _get_realised_dependencies(
        self, explicitly_requested_dependencies: dict[Any, list[Dependency]]
    ) -> set[Dependency]:
        violating_dependencies = explicitly_requested_dependencies.values()

        violating_dependencies_in_user_specified_rule_subject_object_order = set()
        for dependencies in violating_dependencies:
            for dependency in dependencies:
                dependency_in_user_specified_order = (
                    self._get_rule_subject_and_object_in_user_specified_order(
                        dependency
                    )
                )

                violating_dependencies_in_user_specified_rule_subject_object_order.add(
                    dependency_in_user_specified_order
                )

        return violating_dependencies_in_user_specified_rule_subject_object_order

    def _get_rule_subject_and_object_in_user_specified_order(
        self, dependency: Dependency
    ) -> Dependency:
        if self._module_requirement.rule_specified_with_importer_as_rule_subject:
            return dependency

        return dependency[1], dependency[0]

    def _get_dependency_expectations(self) -> DependencyExpectation:
        return DependencyExpectation(
            not_explicitly_requested_dependencies_should_not_be_present=(
                self._behavior_requirement.should_not
                and self._behavior_requirement.behavior_exception
            ),
            explicitly_requested_dependencies_should_not_be_present=(
                self._behavior_requirement.should_not
                and not self._behavior_requirement.behavior_exception
            ),
            explicitly_requested_dependencies_and_no_other_should_be_present=(
                self._behavior_requirement.should_only
                and not self._behavior_requirement.behavior_exception
            ),
            explicitly_requested_dependencies_should_not_but_others_should_be_present=(
                self._behavior_requirement.should_only
                and self._behavior_requirement.behavior_exception
            ),
            at_least_one_not_explicitly_requested_dependency_should_be_present=(
                self._behavior_requirement.should
                and self._behavior_requirement.behavior_exception
            ),
            explicitly_requested_dependencies_should_be_present=(
                self._behavior_requirement.should
                and not self._behavior_requirement.behavior_exception
            ),
        )

    def _get_importee_modules_as_specified_by_user(self):
        return [
            filter_to_module(filter)
            for filter in self._module_requirement.importees_as_specified_by_user
        ]


class RuleViolationDetector(RuleViolationBaseDetector):
    """Based on the behavior requirement and the dependencies that have actually been (not) found in the graph,
    this class decides whether any of the requirements have been violated and how.

    ExplicitlyRequestedDependenciesByBaseModules follow this structure:
    {(requested dependency, e.g. from A to B): [list of dependencies found that qualifiy as the requested dependency, e.g. A.a1 imports B, A.a2 imports B]}

    NotExplicitlyRequestedDependenciesByBaseModule on the other hand are structured like this:
    {Module for which not explicitly requested dependencies (either from or to this module) were found: [list of such dependencies]}.

    The output is a rule violation object which for each type of rule contains a list of (rule subject, rule object) modules which violate the rule. These are ordered according
    to the order the user used when specifying the rule, i.e. the rule subject is the original rule subject no matter if the rule is an import
    or be imported rule.

    If multiple rule subjects have been specified, the rule needs to apply to each one of them in order not
    to count as being violated.
    """

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

        return self._get_abstract_dependencies_without_realisations(
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

        return self._get_abstract_dependencies_without_realisations(
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

        return self._get_missing_dependencies_in_user_specified_order(
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

        return self._get_missing_dependencies_in_user_specified_order(
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

    def _get_abstract_dependencies_without_realisations(
        self, explicitly_requested_dependencies: dict[Any, list[Dependency]]
    ) -> set[Dependency]:
        violating_dependencies = [
            abstract_dependency
            for abstract_dependency, concrete_dependency in explicitly_requested_dependencies.items()
            if len(concrete_dependency) == 0
        ]
        return {
            self._get_rule_subject_and_object_in_user_specified_order(dependency)
            for dependency in violating_dependencies
        }

    def _get_missing_dependencies_in_user_specified_order(
        self,
        not_explicitly_requested_dependencies: NotExplicitlyRequestedDependenciesByBaseModule,
    ) -> set[Dependency]:
        dependencies = []

        for (
            module_with_missing_dependencies,
            not_explicitly_requested_dependencies_of_module,
        ) in not_explicitly_requested_dependencies.items():
            if len(not_explicitly_requested_dependencies_of_module) > 0:
                continue

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

        return {
            self._get_rule_subject_and_object_in_user_specified_order(dependency)
            for dependency in dependencies
        }
