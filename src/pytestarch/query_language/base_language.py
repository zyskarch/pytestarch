from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar, Union

from pytestarch import EvaluableArchitecture
from pytestarch.utils.decorators import deprecated


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


U = TypeVar("U", bound="RelationshipSpecification")


class BehaviorBaseSpecification(Generic[U], ABC):
    """Offers functionality to specify whether dependencies are expected or not."""

    @abstractmethod
    def should(self) -> U:
        pass

    @abstractmethod
    def should_only(self) -> U:
        pass

    @abstractmethod
    def should_not(self) -> U:
        pass


class BehaviorSpecification(BehaviorBaseSpecification["DependencySpecification"], ABC):
    pass


ModuleSpecificationSuccessor = TypeVar(
    "ModuleSpecificationSuccessor", BehaviorSpecification, RuleApplier
)


class ModuleSpecification(Generic[ModuleSpecificationSuccessor], ABC):
    """Offers functionality to specify detail information about Rule
    Subjects or Objects."""

    @abstractmethod
    def are_sub_modules_of(
        self, modules: str | list[str]
    ) -> ModuleSpecificationSuccessor:
        """If multiple rule subjects are specified, this has the same effect as defining a rule per rule subject."""
        pass

    @abstractmethod
    def are_named(self, names: str | list[str]) -> ModuleSpecificationSuccessor:
        """If multiple rule subjects are specified, this has the same effect as defining a rule per rule subject."""
        pass

    @deprecated
    @abstractmethod
    def have_name_containing(
        self, partial_name: str | list[str]
    ) -> ModuleSpecificationSuccessor:
        """
        [DEPRECATED] Use have_name_matching instead; method will be removed in upcoming releases.
        If multiple rule subjects are specified, this has the same effect as defining a rule per rule subject.
        """
        pass

    @abstractmethod
    def have_name_matching(
        self,
        regex: str,
    ) -> ModuleSpecificationSuccessor:
        """Note that regex expressions can have unexpected results if predicates apply to modules, but not their submodules.
        This is often the case for regex expressions with negations. Refer to the documentation of the module import feature for more details.
        If multiple rule subjects are specified, this has the same effect as defining a rule per rule subject.
        """
        pass


class RuleObject(ModuleSpecification[RuleApplier], ABC):
    pass


class RuleSubject(ModuleSpecification[BehaviorSpecification], ABC):
    pass


class RelationshipSpecification(ABC):
    """Base class for different types of relationships between modules, layers, etc."""

    pass


class DependencySpecification(RelationshipSpecification, ABC):
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


class LayerDefinition(ABC):
    """Offers functionality to define which modules a layer contains. Can either be a single
    or multiple modules."""

    @abstractmethod
    def containing_modules(self, modules: str | list[str]) -> BaseLayeredArchitecture:
        """If a module is defined as belonging to layer X, then its submodules are also assumed to be part of layer X."""
        pass

    @abstractmethod
    def have_modules_with_names_matching(
        self,
        regex: str,
    ) -> BaseLayeredArchitecture:
        """If a module is defined as belonging to layer X, then its submodules are also assumed to be part of layer X.
        Note that no attempt will be made to ensure that the regex patterns for different layers are mutually exclusive.
        Also note that regex expressions can have unexpected results if predicates apply to modules, but not their submodules.
        This is often the case for regex expressions with negations. Refer to the documentation of the module import feature for more details.
        """
        pass


class LayerName(ABC):
    """Offers functionality to specify the name of a yet to be defined layer."""

    @abstractmethod
    def layer(self, name: str) -> LayerDefinition:
        pass


class BaseLayeredArchitecture(ABC):

    @abstractmethod
    def with_layer(self) -> LayerName:
        """This is simply a convenience method to achieve proper typing. It can be omitted."""
        pass


class AccessSpecification(RelationshipSpecification, ABC):
    """Offers functionality to specify which kind of imports between layers in a layer architecture are expected.
    Access is defined as the layer equivalent of import between modules, e.g. if layer L consists of module X, and
    layer M of module Y, layer L accesses layer M if module X import module Y."""

    @abstractmethod
    def access_layers_that(self) -> LayerRuleObject:
        pass

    @abstractmethod
    def be_accessed_by_layers_that(self) -> LayerRuleObject:
        pass

    @abstractmethod
    def access_layers_except_layers_that(self) -> LayerRuleObject:
        pass

    @abstractmethod
    def be_accessed_by_layers_except_layers_that(self) -> LayerRuleObject:
        pass

    @abstractmethod
    def access_any_layer(self) -> RuleApplier:
        pass

    @abstractmethod
    def be_accessed_by_any_layer(self) -> RuleApplier:
        pass


class LayerBehaviorSpecification(BehaviorBaseSpecification["AccessSpecification"], ABC):
    pass


LayerSpecificationSuccessor = TypeVar(
    "LayerSpecificationSuccessor", LayerBehaviorSpecification, RuleApplier
)

InputTypes = TypeVar("InputTypes", str, Union[str, list[str]])


class LayerSpecification(Generic[LayerSpecificationSuccessor, InputTypes], ABC):
    """Offers functionality to specify detail information about Layer Rule Subjects or Objects."""

    @abstractmethod
    def are_named(self, names: InputTypes) -> LayerSpecificationSuccessor:
        pass


class LayerRuleObject(LayerSpecification[RuleApplier, Union[str, list[str]]], ABC):
    pass


class LayerRuleSubject(LayerSpecification[LayerBehaviorSpecification, str], ABC):
    pass


class LayerBase(ABC):
    """Offers an entry point to specifying detailed information about Layer Rule
    Subjects."""

    @abstractmethod
    def layers_that(self) -> LayerRuleSubject:
        pass


X = TypeVar("X", bound=BaseLayeredArchitecture)


class LayerRuleBase(Generic[X]):
    """Entry point to defining a rule based on a layered architecture."""

    @abstractmethod
    def based_on(self, architecture: X) -> LayerBase:
        pass
