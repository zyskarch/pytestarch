from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Set, List, Optional, Tuple

from pytestarch.eval_structure.eval_structure_types import Module, EvaluableArchitecture
from pytestarch.query_language.exceptions import ImproperlyConfigured


class ModuleRequirement:
    """Stores information about which module is supposed to be checked against which module."""

    def __init__(
        self, left_hand_module: Module, right_hand_module: Module, import_relation: bool
    ) -> None:
        self._left_hand_module = left_hand_module
        self._right_hand_module = right_hand_module

        self._right_hand_module_has_specifier = import_relation

        if self.left_hand_module_has_specifier:
            self._left_hand_module, self._right_hand_module = (
                self._right_hand_module,
                self._left_hand_module,
            )

    @property
    def left_hand_module(self) -> Module:
        return self._left_hand_module

    @property
    def right_hand_module(self) -> Module:
        return self._right_hand_module

    @property
    def left_hand_module_has_specifier(self) -> bool:
        return not self._right_hand_module_has_specifier


@dataclass
class RuleViolations:
    lax_dependencies_found: List[Module]
    strict_dependency: Optional[Tuple[str, str]]

    should_not_except_violated: bool = False
    should_only_except_violated_by_forbidden_import: bool = False
    should_not_violated: bool = False
    should_only_violated: bool = False
    should_only_except_violated_by_no_import: bool = False
    should_except_violated: bool = False
    should_violated: bool = False

    def __bool__(self) -> bool:
        return any(self.__dict__[a] for a in self._bool_types())

    @classmethod
    def _bool_types(cls) -> List[str]:
        return [field.name for field in fields(cls) if field.type == bool]


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
            raise ImproperlyConfigured(
                "Strict dependency both required and not allowed."
            )

        if self.lax_dependency_required and self.lax_dependency_not_allowed:
            raise ImproperlyConfigured("Lax dependency both required and not allowed.")

    def generate_rule_violation(
        self,
        strict_dependency: Optional[Tuple[str, str]],
        lax_dependencies: Set[Module],
    ) -> RuleViolations:
        """Translate from the detected types of dependencies back to which behavior and dependency requirements are violated by them.
        Args:
            strict_dependency: dependency between the two specified modules found
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

        lax_dependencies_present = (
            lax_dependencies is not None and len(lax_dependencies) > 0
        )
        strict_dependency_present = strict_dependency is not None

        return RuleViolations(
            should_not_except_violated=should_not_except_expected
            and lax_dependencies_present,
            should_only_except_violated_by_forbidden_import=should_only_except_violated_by_forbidden_expected
            and (strict_dependency_present and lax_dependencies_present),
            should_not_violated=should_not_expected and strict_dependency_present,
            should_only_violated=should_only_expected
            and (not strict_dependency_present or lax_dependencies_present),
            should_only_except_violated_by_no_import=should_only_except_violated_by_no_expected
            and not lax_dependencies_present,
            should_except_violated=should_except_expected
            and not lax_dependencies_present,
            should_violated=should_expected and not strict_dependency_present,
            lax_dependencies_found=lax_dependencies,
            strict_dependency=strict_dependency,
        )


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
    def match(self, evaluable: EvaluableArchitecture) -> RuleViolations:
        """
        Checks whether an expected behavior is exhibited by the EvaluableArchitecture.

        Args:
            evaluable: object to check
        Returns:
            overview of rule violations
        """
        raise NotImplementedError()


class DefaultRuleMatcher(RuleMatcher):
    def match(self, evaluable: EvaluableArchitecture) -> RuleViolations:
        strict_dependency_required = (
            self._behavior_requirement.strict_dependency_required
        )
        lax_dependency_required = self._behavior_requirement.lax_dependency_required
        no_strict_dependency_allowed = (
            self._behavior_requirement.strict_dependency_not_allowed
        )
        no_lax_dependency_allowed = (
            self._behavior_requirement.lax_dependency_not_allowed
        )

        left_hand_module = self._module_requirement.left_hand_module
        right_hand_module = self._module_requirement.right_hand_module

        strict_dependency = None
        lax_dependencies = None

        if strict_dependency_required or no_strict_dependency_allowed:
            strict_dependency = evaluable.get_dependency(
                left_hand_module, right_hand_module
            )

        if lax_dependency_required or no_lax_dependency_allowed:
            if not self._module_requirement.left_hand_module_has_specifier:
                dependency_check_method = evaluable.any_dependency_to_module_other_than
            else:
                dependency_check_method = evaluable.any_other_dependency_to_module_than

            lax_dependencies = dependency_check_method(
                left_hand_module,
                right_hand_module,
            )

        return self._behavior_requirement.generate_rule_violation(
            strict_dependency, lax_dependencies
        )
