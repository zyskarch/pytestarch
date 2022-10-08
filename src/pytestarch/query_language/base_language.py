from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Callable, Generic, List, Optional, Type, TypeVar, Union

from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    Module,
)
from pytestarch.exceptions import ImproperlyConfigured
from pytestarch.query_language.message_generator import RuleViolationMessageGenerator
from pytestarch.query_language.rule_matcher import (
    BehaviorRequirement,
    DefaultRuleMatcher,
    ModuleRequirement,
    RuleMatcher,
    RuleViolations,
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
    def are_sub_modules_of(
        self, modules: Union[str, List[str]]
    ) -> ModuleSpecificationSuccessor:
        pass

    @abstractmethod
    def are_named(self, names: Union[str, List[str]]) -> ModuleSpecificationSuccessor:
        pass


class RuleObject(ModuleSpecification[RuleApplier], ABC):
    @abstractmethod
    def anything(self) -> ModuleSpecificationSuccessor:
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


@dataclass
class RuleConfiguration:
    module_to_check: Optional[Module] = None
    modules_to_check_against: Optional[List[Module]] = None
    should: bool = False
    should_only: bool = False
    should_not: bool = False
    except_present: bool = False
    import_: bool = None
    rule_object_anything: bool = False


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
        self._modules_to_check_to_be_specified_next = None
        self._configuration = RuleConfiguration()

    @property
    def rule_subject(self) -> Optional[Module]:
        return self._configuration.module_to_check

    def modules_that(self) -> RuleSubject:
        self._modules_to_check_to_be_specified_next = True
        return self

    def are_sub_modules_of(
        self, modules: Union[str, List[str]]
    ) -> BehaviorSpecification:
        self._set_modules(modules, lambda name: Module(parent_module=name))
        return self

    def are_named(self, names: Union[str, List[str]]) -> BehaviorSpecification:
        self._set_modules(names, lambda name: Module(name=name))
        return self

    def anything(self) -> ModuleSpecificationSuccessor:
        if self._modules_to_check_to_be_specified_next:
            raise ImproperlyConfigured('"Anything" can only be used as a rule object.')
        self._configuration.rule_object_anything = True
        return self

    def _set_modules(
        self,
        module_names: Union[str, List[str]],
        create_module_fn: Callable[[str], Module],
    ) -> None:
        if self._modules_to_check_to_be_specified_next is None:
            raise ImproperlyConfigured("Specify a RuleSubject or RuleObject first.")

        if self._modules_to_check_to_be_specified_next and isinstance(
            module_names, list
        ):
            raise ImproperlyConfigured("Only rule subjects can be specified in batch.")

        if not self._modules_to_check_to_be_specified_next and isinstance(
            module_names, str
        ):
            module_names = [module_names]

        if self._modules_to_check_to_be_specified_next:
            self._configuration.module_to_check = create_module_fn(module_names)  # type: ignore
        else:
            self._configuration.modules_to_check_against = [
                create_module_fn(n) for n in module_names
            ]

    def should(self) -> DependencySpecification:
        self._configuration.should = True
        return self

    def should_only(self) -> DependencySpecification:
        self._configuration.should_only = True
        return self

    def should_not(self) -> DependencySpecification:
        self._configuration.should_not = True
        return self

    def import_modules_that(self) -> RuleObject:
        self._configuration.import_ = True
        self._modules_to_check_to_be_specified_next = False
        return self

    def be_imported_by_modules_that(self) -> RuleObject:
        self._configuration.import_ = False
        self._modules_to_check_to_be_specified_next = False
        return self

    def import_modules_except_modules_that(self) -> RuleObject:
        self._configuration.import_ = True
        self._configuration.except_present = True
        self._modules_to_check_to_be_specified_next = False
        return self

    def be_imported_by_modules_except_modules_that(self) -> RuleObject:
        self._configuration.import_ = False
        self._configuration.except_present = True
        self._modules_to_check_to_be_specified_next = False
        return self

    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        self._assert_required_configuration_present()

        self._configuration = self._convert_aliases(self._configuration)
        matcher = self._prepare_rule_matcher()
        rule_violations = matcher.match(evaluable)

        if rule_violations:
            raise AssertionError(self._create_rule_violation_message(rule_violations))

    def _prepare_rule_matcher(self) -> RuleMatcher:
        module_requirement = ModuleRequirement(
            self._configuration.module_to_check,
            self._configuration.modules_to_check_against,
            self._configuration.import_,
        )
        behavior_requirement = BehaviorRequirement(
            self._configuration.should,
            self._configuration.should_only,
            self._configuration.should_not,
            self._configuration.except_present,
        )

        return self._rule_matcher_class(module_requirement, behavior_requirement)

    def __str__(self) -> str:
        self._assert_required_configuration_present()

        method_name = f'{"should" if self._configuration.should else "should only" if self._configuration.should_only else "should not"}'

        subject_prefix = (
            "Sub modules of "
            if self._configuration.module_to_check.parent_module is not None
            else ""
        )
        if self._configuration.rule_object_anything:
            object_message = "anything "
        else:
            object_message = f'modules that are {"named" if self._configuration.modules_to_check_against[0].name is not None else "sub modules of"} '

        return (
            f'{subject_prefix}"{self._get_module_name(self._configuration.module_to_check)}" '
            f"{method_name} "
            f'{"import" if self._configuration.import_ else "be imported by"} '
            f'{"modules except " if self._configuration.except_present else ""}'
            f"{object_message}"
            f'"{", ".join(map(lambda module: self._get_module_name(module), self._configuration.modules_to_check_against))}".'
        )

    def _get_module_name(self, module: Module) -> str:
        return module.name if module.name is not None else module.parent_module

    def _assert_required_configuration_present(self) -> None:
        behavior_missing = not any(
            [
                self._configuration.should,
                self._configuration.should_only,
                self._configuration.should_not,
            ]
        )
        dependency_missing = self._configuration.import_ is None
        subject_missing = not self._configuration.module_to_check
        object_missing = not self._configuration.modules_to_check_against

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

        if (
            self._configuration.rule_object_anything
            and not self._configuration.should_not
        ):
            raise ImproperlyConfigured(
                'The "anything" rule object can only be used with "should not".'
            )

    @classmethod
    def _name_or_empty(cls, empty: bool, clz: type) -> str:
        return f"a {clz.__name__}" if empty else ""

    def _create_rule_violation_message(self, rule_violations: RuleViolations) -> str:
        message_generator = RuleViolationMessageGenerator(
            self._configuration.module_to_check,
            self._configuration.modules_to_check_against,
            self._configuration.import_,
        )
        single_violation_messages = message_generator.create_rule_violation_messages(
            rule_violations
        )
        return "\n".join(single_violation_messages)

    @classmethod
    def _convert_aliases(cls, configuration: RuleConfiguration) -> RuleConfiguration:
        if not configuration.rule_object_anything:
            return configuration

        # should not import anything is equivalent to should not import except itself
        # should not be imported by anything is equivalent to should not be imported by anything except itself
        return replace(
            configuration,
            rule_object_anything=False,
            modules_to_check_against=[configuration.module_to_check],
            except_present=True,
        )
