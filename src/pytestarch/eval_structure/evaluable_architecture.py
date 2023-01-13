"""Abstract types to specify the interface of evaluable objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple, Union


@dataclass(frozen=True)
class Module:
    """Represents a python module.
    The module can either be identified by its name or by the name of a parent module.

    Attributes:
        name: full name of the module
        parent_module: full name of the parent module
        partial_match: if True, the name may only represent a single part of the actual module name
    """

    name: Optional[str] = None
    parent_module: Optional[str] = None
    partial_match: bool = False


StrictDependency = Tuple[Module, Module]
# key: module that has dependencies
# values: modules the key depends on
DependenciesByBaseModules = Dict[StrictDependency, List[StrictDependency]]
# key: module that either has dependencies or that others are dependent on that were not expected
# value: importer and importee that were not expected
UnexpectedDependenciesByBaseModule = Dict[Module, List[StrictDependency]]


class EvaluableArchitecture(Protocol):
    def get_dependencies(
        self,
        dependents: Union[Module, list[Module]],
        dependent_upons: Union[Module, list[Module]],
    ) -> DependenciesByBaseModules:
        """Returns tuple of importer and importee per dependent and depending module if the dependent module is indeed
        depending on the dependent_upon module. In short: find all dependencies between dependent and dependent_upons.

        Submodules of dependent and dependent upon are taken into account.
        If X.A depends on Y, then X also depends on Y, as X.A is part of X.
        If X depends on Y.Z, then it also depends on Y.

        If one or both of the modules are defined by their parent module, this parent module is excluded from possible
        matches.

        Args:
            dependent: Module(s)
            dependent_upon: Module(s)

        Returns:
            Importer and importee per pair of dependent and dependent_upon module if there are any
            that are sub modules of dependent and dependent_upon respectively.
        """
        raise NotImplementedError()

    def any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> UnexpectedDependenciesByBaseModule:
        """Returns list of depending modules per dependent module if the dependent module has any
        dependency to a module other than the dependent_upon modules
        or any of their submodules.

        If a dependent module is defined via a parent module, this parent module is not taken into account.
        If a dependent upon module is defined via a parent module, this parent module counts as an 'other' dependency.
            Reason behind this: If we want to know whether there are any dependencies from X to any non-Y modules,
            Y's parent is such a module, as this parent module can and usually will also contain other modules than Y.

        Args:
            dependent: Module
            dependent_upon: Module

        Returns:
            All modules other than dependent_upon on which dependent module as any dependency per dependent module
        """
        raise NotImplementedError()

    def any_other_dependencies_on_dependent_upons_than_from_dependents(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> UnexpectedDependenciesByBaseModule:
        """Returns list of depending modules per dependent_upon module if any module other than the dependent
        module and its submodules has any dependency to the
        dependent_upon module.
        If the dependent module is defined via a parent module, this parent module is taken into account. This means
        that if the dependent module's parent module has a dependency to the dependent upon module, this will be contained
        in the returned list.
        If the dependent upon module is defined via a parent module, this parent module is not taken into account.

        Args:
            dependent: Module
            dependent_upon: Module

        Returns:
            All modules other than dependent that have any dependency on the dependent upon module per dependent_upon module
        """
        raise NotImplementedError()

    def visualize(self, **kwargs: Any) -> None:
        """Uses matplotlib to draw the underlying dependency structure.

        Args:
            **kwargs: Any formatting options available for networkx' drawing function, as this is currently the only
                available backend.
                Exception: If 'spacing' is set, this will be interpreted as the parameter 'k' of the spring layout (https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html#networkx.drawing.layout.spring_layout).
        """
        raise NotImplementedError()
