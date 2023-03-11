from __future__ import annotations

from typing import Optional

from pytestarch.eval_structure.evaluable_architecture import (
    ExplicitlyRequestedDependenciesByBaseModules,
    NotExplicitlyRequestedDependenciesByBaseModule,
)
from pytestarch.rule_assessment.rule_check.behavior_requirement import (
    BehaviorRequirement,
)
from pytestarch.rule_assessment.rule_check.rule_violations import RuleViolations


class RuleViolationDetector:
    """Based on the behavior requirement and the dependencies that have actually been (not) found in the graph,
    this class decides whether any of the requirements have been violated.

    ExplicitlyRequestedDependenciesByBaseModules follow this structure:
    {(requested dependency, e.g. from A to B): [list of dependencies found that qualifiy as the requested dependency, e.g. A.a1 imports B, A.a2 imports B]}

    NotExplicitlyRequestedDependenciesByBaseModule on the other hand are structured like this:
    {Module for which not explicitly requested dependencies (either from or to this module) were found: [list of such dependencies]}.
    """

    def __init__(self, behavior_requirement: BehaviorRequirement) -> None:
        self._behavior_requirement = behavior_requirement

    def get_rule_violation(
        self,
        explicitly_requested_dependencies: Optional[
            ExplicitlyRequestedDependenciesByBaseModules
        ],
        not_explicitly_requested_dependencies: Optional[
            NotExplicitlyRequestedDependenciesByBaseModule
        ],
    ) -> RuleViolations:
        """Translate from the detected types of dependencies back to which behavior and dependency requirements are violated by them.
        Args:
            explicitly_requested_dependencies: dependency between the specified modules found, grouped by requested modules
            not_explicitly_requested_dependencies: other dependencies found beside the specified modules
        Returns:
            overview of all rule violations
        """
        not_explicitly_requested_dependencies_should_not_be_present = (
            self._behavior_requirement.should_not
            and self._behavior_requirement._behavior_exception
        )
        explicitly_requested_dependency_should_not_be_present = (
            self._behavior_requirement.should_not
            and not self._behavior_requirement._behavior_exception
        )
        explicitly_requested_dependencies_and_no_other_should_be_present = (
            self._behavior_requirement.should_only
            and not self._behavior_requirement._behavior_exception
        )
        explicitly_requested_dependency_should_not_but_others_should_be_present = (
            self._behavior_requirement.should_only
            and self._behavior_requirement._behavior_exception
        )
        at_least_one_not_explicitly_requested_dependency_should_be_present = (
            self._behavior_requirement.should
            and self._behavior_requirement._behavior_exception
        )
        explicitly_requested_dependency_should_be_present = (
            self._behavior_requirement.should
            and not self._behavior_requirement._behavior_exception
        )

        not_explicitly_requested_dependency_present = (
            not_explicitly_requested_dependencies is not None
            and any(
                lax_dependency
                for lax_dependency in not_explicitly_requested_dependencies.values()
            )
        )
        explicitly_requested_dependency_present = (
            explicitly_requested_dependencies is not None
            and any(
                strict_dependency
                for strict_dependency in explicitly_requested_dependencies.values()
            )
        )

        return RuleViolations(
            should_not_violated=self._should_not_requirement_violated(
                explicitly_requested_dependency_should_not_be_present,
                explicitly_requested_dependency_present,
            ),
            should_violated=self._should_requirement_violated(
                explicitly_requested_dependency_should_be_present,
                explicitly_requested_dependency_present,
            ),
            should_only_violated_by_no_import=self._should_only_requirement_violated_by_no_import(
                explicitly_requested_dependencies_and_no_other_should_be_present,
                explicitly_requested_dependencies,
            ),
            should_only_violated_by_forbidden_import=self._should_only_requirement_violated_by_not_explicitly_requested_dependency(
                explicitly_requested_dependencies_and_no_other_should_be_present,
                not_explicitly_requested_dependency_present,
            ),
            should_except_violated=self._should_except_requirement_violated(
                at_least_one_not_explicitly_requested_dependency_should_be_present,
                not_explicitly_requested_dependency_present,
            ),
            should_only_except_violated_by_no_import=self._should_only_except_requirement_violated_due_to_no_other_imports(
                explicitly_requested_dependency_should_not_but_others_should_be_present,
                not_explicitly_requested_dependency_present,
            ),
            should_only_except_violated_by_forbidden_import=self._should_only_except_requirement_violated_due_to_explicit_dependency_present(
                explicitly_requested_dependency_should_not_but_others_should_be_present,
                explicitly_requested_dependency_present,
            ),
            should_not_except_violated=self._should_not_except_requirement_violated(
                not_explicitly_requested_dependencies_should_not_be_present,
                not_explicitly_requested_dependency_present,
            ),
            not_explicitly_requested_dependencies=not_explicitly_requested_dependencies,
            explicitly_requested_dependencies=explicitly_requested_dependencies,
        )

    def _should_not_requirement_violated(
        self,
        explicitly_requested_dependency_should_not_be_present: bool,
        explicitly_requested_dependency_present: bool,
    ) -> bool:
        return (
            explicitly_requested_dependency_should_not_be_present
            and explicitly_requested_dependency_present
        )

    def _should_requirement_violated(
        self,
        explicitly_requested_dependency_should_be_present: bool,
        explicitly_requested_dependency_present: bool,
    ) -> bool:
        return (
            explicitly_requested_dependency_should_be_present
            and not explicitly_requested_dependency_present
        )

    def _should_only_requirement_violated_by_no_import(
        self,
        explicitly_requested_dependencies_and_no_other_should_be_present: bool,
        explicitly_requested_dependencies: Optional[
            ExplicitlyRequestedDependenciesByBaseModules
        ],
    ) -> bool:
        return (
            explicitly_requested_dependencies_and_no_other_should_be_present
            and self._any_explicitly_requested_dependency_missing(
                explicitly_requested_dependencies
            )
        )

    def _any_explicitly_requested_dependency_missing(
        self,
        explicitly_requested_dependencies: Optional[
            ExplicitlyRequestedDependenciesByBaseModules
        ],
    ) -> bool:
        return any(
            dependency == []
            for dependency in explicitly_requested_dependencies.values()
        )

    def _should_only_requirement_violated_by_not_explicitly_requested_dependency(
        self,
        explicitly_requested_dependencies_and_no_other_should_be_present: bool,
        not_explicitly_requested_dependency_present: bool,
    ) -> bool:
        return (
            explicitly_requested_dependencies_and_no_other_should_be_present
            and not_explicitly_requested_dependency_present
        )

    def _should_except_requirement_violated(
        self,
        at_least_one_not_explicitly_requested_dependency_should_be_present: bool,
        not_explicitly_requested_dependency_present: bool,
    ) -> bool:
        return (
            at_least_one_not_explicitly_requested_dependency_should_be_present
            and not not_explicitly_requested_dependency_present
        )

    def _should_only_except_requirement_violated_due_to_no_other_imports(
        self,
        explicitly_requested_dependency_should_not_but_others_should_be_present: bool,
        not_explicitly_requested_dependency_present: bool,
    ) -> bool:
        return (
            explicitly_requested_dependency_should_not_but_others_should_be_present
            and not not_explicitly_requested_dependency_present
        )

    def _should_only_except_requirement_violated_due_to_explicit_dependency_present(
        self,
        explicitly_requested_dependency_should_not_but_others_should_be_present: bool,
        explicitly_requested_dependency_present: bool,
    ) -> bool:
        return (
            explicitly_requested_dependency_should_not_but_others_should_be_present
            and explicitly_requested_dependency_present
        )

    def _should_not_except_requirement_violated(
        self,
        not_explicitly_requested_dependencies_should_not_be_present: bool,
        not_explicitly_requested_dependency_present: bool,
    ) -> bool:
        return (
            not_explicitly_requested_dependencies_should_not_be_present
            and not_explicitly_requested_dependency_present
        )
