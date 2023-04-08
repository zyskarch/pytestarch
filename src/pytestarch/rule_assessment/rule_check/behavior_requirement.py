from __future__ import annotations

from pytestarch.rule_assessment.exceptions import RuleInconsistency


class BehaviorRequirement:
    """Stores information about which import behavior the checked module is supposed to exhibit."""

    def __init__(
        self,
        should: bool,
        should_only: bool,
        should_not: bool,
        behavior_exception: bool,
    ) -> None:
        self.should = should
        self.should_only = should_only
        self.should_not = should_not

        self.behavior_exception = behavior_exception

        self._validate()

    @property
    def explicitly_requested_dependency_required(self) -> bool:
        """Returns True if the dependency between two specific modules is required."""
        return (self.should or self.should_only) and not self.behavior_exception

    @property
    def not_explicitly_requested_dependency_required(self) -> bool:
        """Returns True if a dependency between a specific module and
        any other modules is required. Which other modules are required
        is specified by the module requirement."""
        return self.behavior_exception and (self.should or self.should_only)

    @property
    def explicitly_requested_dependency_not_allowed(self) -> bool:
        """Returns True if the dependency between two specific modules is not allowed."""
        return (self.should_not and not self.behavior_exception) or (
            self.should_only and self.behavior_exception
        )

    @property
    def not_explicitly_requested_dependency_not_allowed(self) -> bool:
        """Returns True if no dependency between a specific module
        and a set of other modules is not allowed. Which other modules
        are not allowed is specified by the module requirement."""
        return (self.should_not and self.behavior_exception) or (
            self.should_only and not self.behavior_exception
        )

    def _validate(self) -> None:
        if (
            self.explicitly_requested_dependency_required
            and self.explicitly_requested_dependency_not_allowed
        ):
            raise RuleInconsistency(
                "Explicitly requested dependency both required and not allowed."
            )

        if (
            self.not_explicitly_requested_dependency_required
            and self.not_explicitly_requested_dependency_not_allowed
        ):
            raise RuleInconsistency(
                "Not explicitly requested dependency both required and not allowed."
            )
