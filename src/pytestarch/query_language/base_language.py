from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, List, TypeVar, Union

from pytestarch import EvaluableArchitecture
from pytestarch.rule_assessment.rule_check.behavior_requirement import (
    BehaviorRequirement,
)


class FileRule(ABC):
    @abstractmethod
    def from_file(self, file_path: Path) -> BaseModuleSpecifier:
        """Set the path to the file containing the rules that should be
        applied to the evaluable."""
        pass


class BaseModuleSpecifier(ABC):
    @abstractmethod
    def with_base_module(self, name_relative_to_root: str) -> RuleApplier:
        """Sets the name of the base module that was turned into an Evaluable.
        This enables the user to not having to include the entire name relative
        to the root module in
        the diagram.
        Example: root module is named 'src'
        Base module: my_project
        diagram generated for modules in src.my_project.components:
            src.my_project.components.A, src.my_project.components.B
            -> components are named 'A', 'B' in diagram
        name_relative_to_root: src.my_project.components
        """
        pass

    @abstractmethod
    def base_module_included_in_module_names(self) -> RuleApplier:
        """If the diagram contains fully qualified module names."""
        pass


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
    """Offers functionality to specify detail information about Rule
    Subjects or Objects."""

    @abstractmethod
    def are_sub_modules_of(
        self, modules: Union[str, List[str]]
    ) -> ModuleSpecificationSuccessor:
        pass

    @abstractmethod
    def are_named(self, names: Union[str, List[str]]) -> ModuleSpecificationSuccessor:
        pass

    @abstractmethod
    def have_name_containing(
        self, partial_name: Union[str, List[str]]
    ) -> ModuleSpecificationSuccessor:
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

    @abstractmethod
    def import_anything(self) -> RuleApplier:
        pass

    @abstractmethod
    def be_imported_by_anything(self) -> RuleApplier:
        pass


class RuleBase(ABC):
    """Entry point to each architectural rule."""

    @abstractmethod
    def modules_that(self) -> RuleSubject:
        pass
