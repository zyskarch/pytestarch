"""Abstract types to specify the interface of evaluable objects."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple, Union


@dataclass(frozen=True)
class Module:
    """Represents a python module.
    The module can either be identified by its name or by the name of a parent module.

    Attributes:
        name: full name of the module
        parent_module: full name of the parent module
    """

    name: Optional[str] = None
    parent_module: Optional[str] = None


StrictDependency = Tuple[Module, Module]
# if value is not None, it contains the actual (sub) modules of the key-modules that are connected
StrictDependenciesByBaseModules = Dict[StrictDependency, List[StrictDependency]]
# key: module that either has dependencies or that other are dependent on that were not expected
# value: importer and importee that were not expected
LaxDependenciesByBaseModule = Dict[Module, List[StrictDependency]]


class EvaluableArchitecture(Protocol):
    def get_dependencies(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> StrictDependenciesByBaseModules:
        """Returns tuple of importer and importee per dependent and depending module if the dependent module is indeed
        depending on the dependent_upon module.
        Submodules of dependent towards are taken into account, but submodules of dependent_upon are not.
        If one or both of the modules are defined by their parent module, this parent module is excluded from possible
        matches.

        Args:
            dependent: Module
            dependent_upon: Module

        Returns:
            Importer and importee per pair of dependent and dependent_upon module if there are any that are sub modules of dependent and dependent_upon respectively.
        """
        raise NotImplementedError()

    def any_dependencies_to_modules_other_than(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> LaxDependenciesByBaseModule:
        """Returns list of depending modules per dependent module if the dependent module has any
        dependency to a module other than the dependent_upon modules
        or any of their submodules.
        If a dependent module is defined via a parent module, this parent module is not taken into account.
        If a dependent upon module is defined via a parent module, this parent module counts as an 'other' dependency.

        Args:
            dependent: Module
            dependent_upon: Module

        Returns:
            All modules other than dependent_upon on which dependent module as any dependency per dependent module
        """
        raise NotImplementedError()

    def any_other_dependencies_to_modules_than(
        self,
        dependents: Union[Module, List[Module]],
        dependent_upons: Union[Module, List[Module]],
    ) -> LaxDependenciesByBaseModule:
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
