from __future__ import annotations

from abc import abstractmethod, ABC
from collections import defaultdict
from typing import Optional, Type, Generic, TypeVar

from pytestarch.eval_structure.eval_structure_types import EvaluableArchitecture, Module
from pytestarch.eval_structure.graph import Node
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.query_language.rule_matcher import (
    RuleMatcher,
    DefaultRuleMatcher,
    BehaviorRequirement,
    ModuleRequirement,
    RuleViolations,
)

# (Import, negated, singular)
PREFIX_MAPPING = defaultdict(str)
PREFIX_MAPPING.update(
    {
        (False, False, True): "is ",
        (False, True, True): "is not ",
        (True, True, True): "does not ",
        (False, False, False): "are ",
        (False, True, False): "are not ",
        (True, True, False): "do not ",
    }
)


class RuleApplier(ABC):
    @abstractmethod
    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        """
        Calculates whether it (the rule) applies to a given EvaluableArchitecture.
        This means calculating which behavior is wanted and then
        checking this to the state the Evaluable represents.

        Args:
            evaluable: module dependency structure to compare the rule against

        Raises:
            AssertionError: if the rule does not apply to the evaluable object
        """
        raise NotImplementedError()


class BehaviorSpecification(ABC):
    """Offers functionality to specify whether dependencies are expected or not."""

    @abstractmethod
    def should(self) -> DependencySpecification:
        pass

    @abstractmethod
    def should_only(self) -> DependencySpecification:
        pass

    @abstractmethod
    def should_not(self) -> DependencySpecification:
        pass


ModuleSpecificationSuccessor = TypeVar(
    "ModuleSpecificationSuccessor", BehaviorRequirement, RuleApplier
)


class ModuleSpecification(Generic[ModuleSpecificationSuccessor], ABC):
    """Offers functionality to specify detail information about Rule Subjects or Objects."""

    @abstractmethod
    def are_sub_modules_of(self, modules: Node) -> ModuleSpecificationSuccessor:
        pass

    @abstractmethod
    def are_named(self, name: str) -> ModuleSpecificationSuccessor:
        pass


class RuleObject(ModuleSpecification[RuleApplier], ABC):
    pass


class RuleSubject(ModuleSpecification[BehaviorSpecification], ABC):
    pass


class DependencySpecification(ABC):
    """Offers functionality to specify which kind of dependencies are expected."""

    @abstractmethod
    def import_modules_that(self) -> RuleObject:
        pass

    @abstractmethod
    def be_imported_by_modules_that(self) -> RuleObject:
        pass

    @abstractmethod
    def import_modules_except_modules_that(self) -> RuleObject:
        pass

    @abstractmethod
    def be_imported_by_modules_except_modules_that(self) -> RuleObject:
        pass


class RuleBase(ABC):
    """Entry point to each architectural rule."""

    @abstractmethod
    def modules_that(self) -> RuleSubject:
        pass


class Rule(
    DependencySpecification,
    RuleBase,
    BehaviorSpecification,
    RuleObject,
    RuleSubject,
    RuleApplier,
):
    """Represents an architectural rule of the form
    Module1 [verb, such as 'should'] [import type, such as 'import'] Module2
    """

    def __init__(
        self, rule_matcher_class: Type[RuleMatcher] = DefaultRuleMatcher
    ) -> None:
        self._rule_matcher_class = rule_matcher_class

        self._module_to_check: Optional[Module] = None
        self._module_to_check_against: Optional[Module] = None

        self._should = False
        self._should_only = False
        self._should_not = False

        self._except_present = False

        self._import = None

        self._modules_to_check_to_be_specified_next = None

    @property
    def rule_subject(self) -> Optional[Module]:
        return self._module_to_check

    def modules_that(self) -> RuleSubject:
        self._modules_to_check_to_be_specified_next = True
        return self

    def are_sub_modules_of(self, module: Node) -> BehaviorSpecification:
        if self._modules_to_check_to_be_specified_next is None:
            raise ImproperlyConfigured("Specify a RuleSubject or RuleObject first.")

        module = Module(parent_module=module)

        if self._modules_to_check_to_be_specified_next:
            self._module_to_check = module
        else:
            self._module_to_check_against = module

        return self

    def are_named(self, name: str) -> BehaviorSpecification:
        if self._modules_to_check_to_be_specified_next is None:
            raise ImproperlyConfigured("Specify a RuleSubject or RuleObject first.")

        module = Module(name=name)

        if self._modules_to_check_to_be_specified_next:
            self._module_to_check = module
        else:
            self._module_to_check_against = module

        return self

    def should(self) -> DependencySpecification:
        self._should = True
        return self

    def should_only(self) -> DependencySpecification:
        self._should_only = True
        return self

    def should_not(self) -> DependencySpecification:
        self._should_not = True
        return self

    def import_modules_that(self) -> RuleObject:
        self._import = True
        self._modules_to_check_to_be_specified_next = False
        return self

    def be_imported_by_modules_that(self) -> RuleObject:
        self._import = False
        self._modules_to_check_to_be_specified_next = False
        return self

    def import_modules_except_modules_that(self) -> RuleObject:
        self._import = True
        self._except_present = True
        self._modules_to_check_to_be_specified_next = False
        return self

    def be_imported_by_modules_except_modules_that(self) -> RuleObject:
        self._import = False
        self._except_present = True
        self._modules_to_check_to_be_specified_next = False
        return self

    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        self._assert_required_configuration_present()

        module_requirement = ModuleRequirement(
            self._module_to_check, self._module_to_check_against, self._import
        )
        behavior_requirement = BehaviorRequirement(
            self._should,
            self._should_only,
            self._should_not,
            self._except_present,
        )

        rule_violations = self._rule_matcher_class(
            module_requirement, behavior_requirement
        ).match(evaluable)

        if rule_violations:
            raise AssertionError(self._create_rule_violation_message(rule_violations))

    def __str__(self) -> str:
        method_name = f'{"should" if self._should else "should only" if self._should_only else "should not"}'

        return (
            f"{self._add_rule_subject_plural_marker_if_needed(self._get_module_name(self._module_to_check))} "
            f"{method_name} "
            f'{"import" if self._import else "be imported by"} '
            f'{"modules except " if self._except_present else ""}'
            f'modules that are {"named" if self._module_to_check_against.name is not None else "sub modules of"} '
            f'"{self._get_module_name(self._module_to_check_against)}".'
        )

    def _get_module_name(self, module: Module) -> str:
        return module.name if module.name is not None else module.parent_module

    def _assert_required_configuration_present(self) -> None:
        behavior_missing = not any([self._should, self._should_only, self._should_not])
        dependency_missing = self._import is None
        subject_missing = not self._module_to_check
        object_missing = not self._module_to_check_against

        if any([behavior_missing, dependency_missing, subject_missing, object_missing]):
            subject_message = self._name_or_empty(subject_missing, RuleSubject)
            behavior_message = self._name_or_empty(
                behavior_missing, BehaviorSpecification
            )
            dependency_message = self._name_or_empty(
                dependency_missing, DependencySpecification
            )
            object_message = self._name_or_empty(object_missing, RuleObject)

            messages = [
                subject_message,
                behavior_message,
                dependency_message,
                object_message,
            ]

            error_message = (
                f"Specify {', '.join(filter(lambda m: len(m) > 0, messages))}."
            )

            raise ImproperlyConfigured(error_message)

    @classmethod
    def _name_or_empty(cls, empty: bool, clz: type) -> str:
        return f"a {clz.__name__}" if empty else ""

    def _create_rule_violation_message(self, rule_violations: RuleViolations) -> str:
        rule_subject = self._create_rule_subject_for_rule_violation_message(
            rule_violations
        )
        verb = self._create_verb_for_rule_violation_message(rule_violations)
        rule_object = self._create_rule_object_for_rule_violation_message(
            rule_violations
        )
        return f"{rule_subject} {verb}{rule_object}."

    def _create_rule_subject_for_rule_violation_message(
        self, rule_violations: RuleViolations
    ) -> str:
        module_name = self._get_module_name(self._module_to_check)

        if self._forbidden_import(rule_violations):
            if rule_violations.strict_dependency is not None:
                module_name = self._get_subject_of_strict_dependency(rule_violations)

                # no plural marker needed, as module is always singular
                return f'"{module_name}"'

        return self._add_rule_subject_plural_marker_if_needed(module_name)

    def _get_subject_of_strict_dependency(self, rule_violations: RuleViolations) -> str:
        # strict dependency is always reported in format (importer, importee)
        # if rule is of format A ... imports B, the dependency will be (A, B)
        idx = int(not self._import)
        return rule_violations.strict_dependency[idx]

    def _get_object_of_strict_dependency(self, rule_violations: RuleViolations) -> str:
        # strict dependency is always reported in format (importer, importee)
        # if rule is of format A ... be imported by B, the dependency will be (B, A)
        # but in our rule, B is the object
        idx = int(self._import)
        return rule_violations.strict_dependency[idx]

    def _add_rule_subject_plural_marker_if_needed(self, module_name: str) -> str:
        prefix = ""
        if not self._rule_subject_singular:
            prefix = "Sub modules of "
        return f'{prefix}"{module_name}"'

    def _create_verb_for_rule_violation_message(
        self, rule_violations: RuleViolations
    ) -> str:
        base_verb = "import" if self._import else "imported by"

        suffix = " "

        if rule_violations.should_violated:
            negated = True

        elif (
            rule_violations.should_except_violated
            or rule_violations.should_only_except_violated_by_no_import
        ):
            negated = True

        elif (
            rule_violations.should_only_except_violated_by_forbidden_import
            or rule_violations.should_not_violated
            or rule_violations.should_only_violated
            or rule_violations.should_not_except_violated
        ):

            if self._import and (
                self._rule_subject_singular or (self._forbidden_import(rule_violations))
            ):
                suffix = "s "

            negated = False
        else:
            raise Exception("Unknown rule violation detected.")

        prefix = PREFIX_MAPPING[
            (
                self._import,
                negated,
                self._rule_subject_singular
                or (self._forbidden_import(rule_violations)),
            )
        ]

        return f"{prefix}{base_verb}{suffix}"

    def _forbidden_import(self, rule_violations: RuleViolations) -> bool:
        return (
            rule_violations.should_not_violated
            or rule_violations.should_only_except_violated_by_forbidden_import
        )

    @property
    def _rule_subject_singular(self) -> bool:
        return self._module_to_check.name is not None

    @property
    def _rule_object_singular(self) -> bool:
        return self._module_to_check_against.name is not None

    def _create_rule_object_for_rule_violation_message(
        self, rule_violations: RuleViolations
    ) -> str:
        object_name = self._get_module_name(self._module_to_check_against)
        module_qualifier = "" if self._rule_object_singular else "a sub module of "

        if (
            rule_violations.should_except_violated
            or rule_violations.should_only_except_violated_by_no_import
        ):
            module_qualifier = f"any module that is not {'' if self._rule_object_singular else 'a sub module of '}"
        elif self._forbidden_import(rule_violations):
            module_qualifier = ""

            if rule_violations.strict_dependency is not None:
                object_name = self._get_object_of_strict_dependency(rule_violations)

        if (
            rule_violations.should_not_except_violated
            or rule_violations.should_only_violated
        ):
            object_name = ", ".join(
                (module.name for module in rule_violations.lax_dependencies_found)
            )

        return f'{module_qualifier}"{object_name}"'
