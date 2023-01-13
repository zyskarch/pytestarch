from __future__ import annotations

from typing import Optional

from pytestarch.eval_structure.evaluable_architecture import (
    DependenciesByBaseModules,
    UnexpectedDependenciesByBaseModule,
)
from pytestarch.rule_assessment.exceptions import RuleInconsistency
from pytestarch.rule_assessment.rule_check.rule_violations import RuleViolations


class BehaviorRequirement:
    """Stores information about which import behavior the checked module is supposed to exhibit."""

    def __init__(
        self,
        positive_behavior_lax: bool,
        positive_behavior_strict: bool,
        negative_behavior: bool,
        behavior_exception: bool,
    ) -> None:
        self._should = positive_behavior_lax
        self._should_only = positive_behavior_strict
        self._should_not = negative_behavior

        self._behavior_exception = behavior_exception

        self._validate()

    @property
    def strict_dependency_required(self) -> bool:
        """Returns True if a dependency between two specific modules is required."""
        return (self._should or self._should_only) and not self._behavior_exception

    @property
    def lax_dependency_required(self) -> bool:
        """Returns True if a dependency between a specific module and
        any other modules is required. Which other modules are required
        is specified by the module requirement."""
        return self._behavior_exception and (self._should or self._should_only)

    @property
    def strict_dependency_not_allowed(self) -> bool:
        """Returns True if a dependency between two specific modules is not allowed."""
        return (self._should_not and not self._behavior_exception) or (
            self._should_only and self._behavior_exception
        )

    @property
    def lax_dependency_not_allowed(self) -> bool:
        """Returns True if no dependency between a specific module
        and a set of other modules is not allowed. Which other modules
        are not allowed is specified by the module requirement."""
        return (self._should_not and self._behavior_exception) or (
            self._should_only and not self._behavior_exception
        )

    def _validate(self) -> None:
        if self.strict_dependency_required and self.strict_dependency_not_allowed:
            raise RuleInconsistency("Strict dependency both required and not allowed.")

        if self.lax_dependency_required and self.lax_dependency_not_allowed:
            raise RuleInconsistency("Lax dependency both required and not allowed.")

    def generate_rule_violation(
        self,
        strict_dependencies: Optional[DependenciesByBaseModules],
        lax_dependencies: Optional[UnexpectedDependenciesByBaseModule],
    ) -> RuleViolations:
        """Translate from the detected types of dependencies back to which behavior and dependency requirements are violated by them.
        Args:
            strict_dependencies: dependency between the two specified modules found, grouped by requested modules
            lax_dependencies: other dependencies found beside the two specified modules
        Returns:
            overview of all rule violations
        """
        should_not_except_expected = self._should_not and self._behavior_exception
        should_only_except_violated_by_forbidden_expected = (
            self._should_only and self._behavior_exception
        )
        should_not_expected = self._should_not and not self._behavior_exception
        should_only_expected = self._should_only and not self._behavior_exception
        should_only_except_violated_by_no_expected = (
            self._should_only and self._behavior_exception
        )
        should_except_expected = self._should and self._behavior_exception
        should_expected = self._should and not self._behavior_exception

        lax_dependencies_present = lax_dependencies is not None and any(
            lax_dependency for lax_dependency in lax_dependencies.values()
        )
        strict_dependency_present = strict_dependencies is not None and any(
            strict_dependency for strict_dependency in strict_dependencies.values()
        )

        return RuleViolations(
            should_not_except_violated=should_not_except_expected
            and lax_dependencies_present,
            should_only_except_violated_by_forbidden_import=should_only_except_violated_by_forbidden_expected
            and strict_dependency_present,
            should_not_violated=should_not_expected and strict_dependency_present,
            should_only_violated_by_no_import=should_only_expected
            and any(dependency == [] for dependency in strict_dependencies.values()),
            should_only_violated_by_forbidden_import=should_only_expected
            and lax_dependencies_present,
            should_only_except_violated_by_no_import=should_only_except_violated_by_no_expected
            and not lax_dependencies_present,
            should_except_violated=should_except_expected
            and not lax_dependencies_present,
            should_violated=should_expected and not strict_dependency_present,
            unexpected_dependencies=lax_dependencies,
            dependencies=strict_dependencies,
        )
