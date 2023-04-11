"""Abstract interface of evaluable objects."""

from __future__ import annotations

from bisect import bisect
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Protocol, Tuple, Union

from pytestarch.eval_structure.exceptions import LayerMismatch

Layer = str
ModuleName = str


class LayerMapping:
    def __init__(
        self, layer_mapping_for_module_filters: Dict[Layer, List[ModuleFilter]]
    ) -> None:
        self._layer_mapping_for_module_filters = layer_mapping_for_module_filters
        self._module_filter_mapping = {
            module: layer
            for layer, modules in layer_mapping_for_module_filters.items()
            for module in modules
        }

        self._sorted_module_filter_names = sorted(
            map(lambda module: module.name, self._module_filter_mapping.keys())
        )

    def get_module_filters(self, layer: Layer) -> List[ModuleFilter]:
        return self._layer_mapping_for_module_filters[layer]

    def get_layer(self, module: Module) -> Optional[Layer]:
        """Attempts to find the layer the given module belongs to. If the module does not appear in the
        layer definition itself, it is checked whether the module is a submodule of one of the modules in the layer
        definition. If so, the layer of the parent module is returned. Otherwise, None is returned.
        This assumes that if a module is in layer X, all of its submodules are as well.
        """
        if not module.name:
            return None

        layer_candidate = self._module_filter_mapping.get(module, None)

        if layer_candidate is not None:
            return layer_candidate

        idx_of_module = (
            bisect(self._sorted_module_filter_names, module.name) - 1
        )  # -1 since idx is after the insertion point

        candidate_parent_modules = []
        while idx_of_module >= 0:
            parent_module_candidate = self._sorted_module_filter_names[idx_of_module]
            if module.name.startswith(parent_module_candidate):
                candidate_parent_modules.append(
                    ModuleFilter(name=parent_module_candidate)
                )
            idx_of_module -= 1

        candidate_layers = set(
            map(
                lambda module: self._module_filter_mapping[module],
                candidate_parent_modules,
            )
        )

        if len(candidate_layers) > 1:
            raise LayerMismatch(
                f"Multiple possible parent modules found for module {module.name}."
            )

        if not candidate_layers:
            return None
        else:
            return candidate_layers.pop()

    def get_layer_for_module_name(self, module_name: str) -> Optional[Layer]:
        return self.get_layer(Module(name=module_name))

    @property
    def all_layers(self) -> Iterable[Layer]:
        return self._layer_mapping_for_module_filters.keys()


@dataclass(frozen=True)
class ModuleFilter:
    """Represents a way to identify a python module in the dependency graph.
    The module can either be identified by its name or by the name of a parent module.

    Attributes:
        name: full name of the module
        parent_module: full name of the parent module
        regex: if True, the name represents a regex pattern that matches potentially multiple modules

    Either name or parent_module can be specified, but not both.
    """

    name: Optional[str] = None
    parent_module: Optional[str] = None
    regex: bool = False


@dataclass(frozen=True)
class Module:
    """Represents an actual python module found in the dependency graph."""

    name: str

    @property
    def is_single_module(self) -> bool:
        return True


@dataclass(frozen=True)
class ModuleGroup(Module):
    """Represents a group of actual python module found in the dependency graph.
    This is only needed if a group of modules is specified via their parent module's name, and only for not explicitly
    requested dependencies. For these, the original module filter is not converted to actual modules, as this would
    clutter the return type and the user output.
    Instead, this filter will be converted to a module group.

    The name is the name of the parent module of all modules in this group.
    """

    name: str

    @property
    def is_single_module(self) -> bool:
        return False


Dependency = Tuple[Module, Module]
# key: user-requested dependency
# values: list of exact modules that show this dependency
ExplicitlyRequestedDependenciesByBaseModules = Dict[Dependency, List[Dependency]]
# key: module that either has dependencies or that others are dependent on that were not explicitly requested
# via the rule the user has specified
# value: importer and importee that were not found
NotExplicitlyRequestedDependenciesByBaseModule = Dict[Module, List[Dependency]]


class EvaluableArchitecture(Protocol):
    def get_dependencies(
        self,
        dependents: Union[ModuleFilter, list[ModuleFilter]],
        dependent_upons: Union[ModuleFilter, list[ModuleFilter]],
    ) -> ExplicitlyRequestedDependenciesByBaseModules:
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
        dependents: List[ModuleFilter],
        dependent_upons: List[ModuleFilter],
    ) -> NotExplicitlyRequestedDependenciesByBaseModule:
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
        dependents: List[ModuleFilter],
        dependent_upons: List[ModuleFilter],
    ) -> NotExplicitlyRequestedDependenciesByBaseModule:
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

    @property
    def modules(self) -> List[str]:
        """Return names of all modules that are present in this architecture."""
        raise NotImplementedError()
