from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, List, Optional, Type, Union

from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure.evaluable_architecture import Module
from pytestarch.query_language.base_language import (
    BehaviorSpecification,
    DependencySpecification,
    RuleApplier,
    RuleBase,
    RuleObject,
    RuleSubject,
)
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.rule_assessment.rule_check.behavior_requirement import (
    BehaviorRequirement,
)
from pytestarch.rule_assessment.rule_check.module_requirement import ModuleRequirement
from pytestarch.rule_assessment.rule_check.rule_matcher import (
    DefaultRuleMatcher,
    RuleMatcher,
)


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

    def have_name_containing(
        self, partial_names: Union[str, List[str]]
    ) -> BehaviorSpecification:
        self._set_modules(
            partial_names, lambda name: Module(name=name, partial_match=True)
        )
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

    def import_anything(self) -> RuleApplier:
        self._configuration.rule_object_anything = True
        self.import_modules_that()
        return self

    def be_imported_by_anything(self) -> RuleApplier:
        self._configuration.rule_object_anything = True
        self.be_imported_by_modules_that()
        return self

    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        self._configuration = self._convert_aliases(self._configuration)
        self._assert_required_configuration_present()

        matcher = self._prepare_rule_matcher()
        matcher.match(evaluable)

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
            f'"{", ".join(sorted(map(lambda module: self._get_module_name(module), self._configuration.modules_to_check_against)))}".'
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
