from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Callable

from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure.evaluable_architecture import (
    ModuleFilter,
    ModuleNameFilter,
    ModuleNameRegexFilter,
    ParentModuleNameFilter,
)
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
from pytestarch.utils.decorators import deprecated
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)


@dataclass
class RuleConfiguration:
    modules_to_check: Sequence[ModuleFilter] | None = None
    modules_to_check_against: Sequence[ModuleFilter] | None = None
    should: bool = False
    should_only: bool = False
    should_not: bool = False
    except_present: bool = False
    import_: bool | None = None
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
        self,
        rule_matcher_class: Callable[
            [ModuleRequirement, BehaviorRequirement], RuleMatcher
        ] = DefaultRuleMatcher,
    ) -> None:
        self._rule_matcher_class = rule_matcher_class
        self._modules_to_check_to_be_specified_next: bool | None = None
        self._configuration = RuleConfiguration()

    @property
    def rule_subjects(self) -> Sequence[ModuleFilter] | None:
        return self._configuration.modules_to_check

    def modules_that(self) -> RuleSubject:
        self._modules_to_check_to_be_specified_next = True
        return self

    def are_sub_modules_of(  # type: ignore
        self, modules: str | list[str]
    ) -> BehaviorSpecification:
        self._set_modules(
            modules, lambda name: ParentModuleNameFilter(parent_module=name)
        )
        return self

    def are_named(self, names: str | list[str]) -> BehaviorSpecification:  # type: ignore
        self._set_modules(names, lambda name: ModuleNameFilter(name=name))
        return self

    @deprecated
    def have_name_containing(
        self, partial_names: str | list[str]
    ) -> BehaviorSpecification:
        self._set_modules(
            partial_names,
            lambda name: ModuleNameRegexFilter(
                name=convert_partial_match_to_regex(name)
            ),
        )
        return self

    def have_name_matching(  # type: ignore
        self,
        regex: str,
    ) -> BehaviorSpecification:
        self._set_modules(regex, lambda name: ModuleNameRegexFilter(name=name))
        return self

    def _set_modules(
        self,
        module_names: str | list[str],
        create_module_fn: Callable[[str], ModuleFilter],
    ) -> None:
        if self._modules_to_check_to_be_specified_next is None:
            raise ImproperlyConfigured("Specify a RuleSubject or RuleObject first.")

        if isinstance(module_names, str):
            module_names = [module_names]

        modules = [create_module_fn(n) for n in module_names]
        if self._modules_to_check_to_be_specified_next:
            self._configuration.modules_to_check = modules
        else:
            self._configuration.modules_to_check_against = modules

    def _add_modules(self, modules: list[tuple[str, bool]]) -> BehaviorSpecification:
        module_names = []
        module_creation_fn = []

        for module, name_is_regex in modules:
            module_names.append(module)
            module_creation_fn.append(
                lambda name: (
                    ModuleNameFilter(name=name)
                    if not name_is_regex
                    else ModuleNameRegexFilter(name=name)
                )
            )

        self._append_modules(module_names, module_creation_fn)
        return self

    def _append_modules(
        self,
        module_names: list[str],
        create_module_fns: list[Callable[[str], ModuleFilter]],
    ) -> None:
        modules = [fn(n) for n, fn in zip(module_names, create_module_fns)]
        if self._modules_to_check_to_be_specified_next:
            if self._configuration.modules_to_check is None:
                self._configuration.modules_to_check = []

            self._configuration.modules_to_check.extend(modules)  # type: ignore
        else:
            if self._configuration.modules_to_check_against is None:
                self._configuration.modules_to_check_against = []

            self._configuration.modules_to_check_against.extend(modules)  # type: ignore

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
            self._configuration.modules_to_check,  # type: ignore
            self._configuration.modules_to_check_against,  # type: ignore
            self._configuration.import_,  # type: ignore
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
            if self._configuration.modules_to_check[0].identifier_is_parent_module  # type: ignore
            else ""
        )
        if self._configuration.rule_object_anything:
            object_message = "anything "
        else:
            object_message = f'modules that are {"sub modules of" if self._configuration.modules_to_check_against[0].identifier_is_parent_module else "named"} '  # type: ignore

        combined_rule_subjects = self._combine_names(
            self._configuration.modules_to_check  # type: ignore
        )
        combined_rule_objects = self._combine_names(
            self._configuration.modules_to_check_against  # type: ignore
        )
        return (
            f'{subject_prefix}"{combined_rule_subjects}" '
            f"{method_name} "
            f'{"import" if self._configuration.import_ else "be imported by"} '
            f'{"modules except " if self._configuration.except_present else ""}'
            f"{object_message}"
            f'"{combined_rule_objects}".'
        )

    def _combine_names(self, modules: Sequence[ModuleFilter]) -> str:
        return ", ".join(sorted(map(lambda module: module.identifier, modules)))

    def _assert_required_configuration_present(self) -> None:
        behavior_missing = not any(
            [
                self._configuration.should,
                self._configuration.should_only,
                self._configuration.should_not,
            ]
        )
        dependency_missing = self._configuration.import_ is None
        subject_missing = not self._configuration.modules_to_check
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

        modules_to_check_without_parent_and_submodule_combinations = (
            cls._get_modules_to_check_without_parent_and_submodule_combinations(
                configuration,
            )
        )

        return replace(
            configuration,
            rule_object_anything=False,
            modules_to_check=modules_to_check_without_parent_and_submodule_combinations,
            modules_to_check_against=modules_to_check_without_parent_and_submodule_combinations,
            except_present=True,
        )

    @classmethod
    def _get_modules_to_check_without_parent_and_submodule_combinations(
        cls, configuration: RuleConfiguration
    ) -> Sequence[ModuleFilter] | None:
        # if modules_to_check contain a module and its submodule, this can throw off the breadth first search conducted
        # on the dependency graph - and also, this setup does not really make sense
        if configuration.modules_to_check is None:
            return None

        module_names = sorted(
            map(lambda m: m.identifier, configuration.modules_to_check)
        )

        result = []
        for module in configuration.modules_to_check:
            parent_module_found = False
            for module_name in module_names:
                if (
                    module_name in module.identifier
                    and module.identifier != module_name
                ):
                    parent_module_found = True

            if not parent_module_found:
                result.append(module)

        return result
