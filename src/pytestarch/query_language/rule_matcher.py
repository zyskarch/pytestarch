from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import List, Optional, Union

from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    LaxDependenciesByBaseModule,
    Module,
    StrictDependenciesByBaseModules,
)
from pytestarch.exceptions import ImproperlyConfigured


class ModuleRequirement:
    """Stores information about which module is supposed to be checked against which module."""

    def __init__(
        self,
        left_hand_module: Module,
        right_hand_modules: List[Module],
        import_relation: bool,
    ) -> None:
        self._left_hand_modules = left_hand_module
        self._right_hand_modules = right_hand_modules

        self._right_hand_module_has_specifier = import_relation

        if self.left_hand_module_has_specifier:
            self._left_hand_modules, self._right_hand_modules = (
                self._right_hand_modules,
                self._left_hand_modules,
            )

    @property
    def left_hand_modules(self) -> Union[Module, List[Module]]:
        return self._left_hand_modules

    @property
    def right_hand_modules(self) -> Union[Module, List[Module]]:
        return self._right_hand_modules

    @property
    def left_hand_module_has_specifier(self) -> bool:
        # True if rule is of format "is imported by"
        return not self._right_hand_module_has_specifier


@dataclass
class RuleViolations:
    lax_dependencies: Optional[LaxDependenciesByBaseModule]
    strict_dependencies: Optional[StrictDependenciesByBaseModules]

    should_violated: bool = False
    should_only_violated_by_forbidden_import: bool = False
    should_only_violated_by_no_import: bool = False
    should_not_violated: bool = False
    should_except_violated: bool = False
    should_only_except_violated_by_forbidden_import: bool = False
    should_only_except_violated_by_no_import: bool = False
    should_not_except_violated: bool = False

    def __bool__(self) -> bool:
        return any(self.__dict__[a] for a in self._bool_field_names())

    @classmethod
    def _bool_field_names(cls) -> List[str]:
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
        strict_dependencies: Optional[StrictDependenciesByBaseModules],
        lax_dependencies: Optional[LaxDependenciesByBaseModule],
        import_rule: bool,
        left_hand_side_module: Union[Module, List[Module]],
        right_hand_side_module: Union[Module, List[Module]],
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
            lax_dependencies=lax_dependencies,
            strict_dependencies=strict_dependencies,
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
        strict_dependencies = self._get_strict_dependencies(evaluable)

        lax_dependencies = self._get_lax_dependencies(evaluable)

        return self._behavior_requirement.generate_rule_violation(
            strict_dependencies,
            lax_dependencies,
            not self._module_requirement.left_hand_module_has_specifier,
            self._module_requirement.left_hand_modules,
            self._module_requirement.right_hand_modules,
        )

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
