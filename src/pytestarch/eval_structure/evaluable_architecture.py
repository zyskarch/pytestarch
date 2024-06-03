"""Abstract interface of evaluable objects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from bisect import bisect
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from pytestarch.eval_structure.exceptions import LayerMismatch

Layer = str
ModuleName = str


class LayerMapping:
    def __init__(
        self,
        layer_mapping_for_module_filters: Mapping[
            Layer, Sequence[ModuleFilter] | Sequence[Module]
        ],
    ) -> None:
        self._layer_mapping_for_module_filters = layer_mapping_for_module_filters
        self._module_filter_mapping: Mapping[ModuleFilter | Module, Layer] = {
            module: layer
            for layer, modules in layer_mapping_for_module_filters.items()
            for module in modules
        }

        self._sorted_module_filter_names = sorted(
            map(lambda module: module.identifier, self._module_filter_mapping.keys())
        )

    def get_module_filters(self, layer: Layer) -> Sequence[ModuleFilter]:
        # assumption: only ModuleFilters present in the layer mapping
        return self._layer_mapping_for_module_filters[layer]  # type: ignore

    def _get_layer(self, module: ModuleNameFilter) -> Layer:
        # assumption: there is exactly one match
        return [
            self._module_filter_mapping[key]
            for key in self._module_filter_mapping
            if key.identifier == module.identifier
        ][0]

    def _get_layer_or_none(self, module_name: str) -> Layer | None:
        layers = [
            self._module_filter_mapping[key]
            for key in self._module_filter_mapping
            if key.identifier == module_name
        ]

        if layers:
            return layers[0]

        return None

    def get_layer_for_module_name(self, module_name: str) -> Layer | None:
        """Attempts to find the layer the given module belongs to. If the module does not appear in the
        layer definition itself, it is checked whether the module is a submodule of one of the modules in the layer
        definition. If so, the layer of the parent module is returned. Otherwise, None is returned.
        This assumes that if a module is in layer X, all of its submodules are as well.
        """
        layer_candidate = self._get_layer_or_none(module_name)

        if layer_candidate is not None:
            return layer_candidate

        idx_of_module = (
            bisect(self._sorted_module_filter_names, module_name) - 1
        )  # -1 since idx is after the insertion point

        candidate_parent_modules = []
        while idx_of_module >= 0:
            parent_module_candidate = self._sorted_module_filter_names[idx_of_module]
            if module_name.startswith(parent_module_candidate):
                candidate_parent_modules.append(
                    ModuleNameFilter(name=parent_module_candidate)
                )
            idx_of_module -= 1

        candidate_layers = set(
            map(
                self._get_layer,
                candidate_parent_modules,
            )
        )

        if len(candidate_layers) > 1:
            raise LayerMismatch(
                f"Multiple possible parent modules found for module {module_name}."
            )

        if not candidate_layers:
            return None
        else:
            return candidate_layers.pop()

    @property
    def all_layers(self) -> Iterable[Layer]:
        return self._layer_mapping_for_module_filters.keys()


class ModuleFilter(ABC):
    """Represents a way to identify a python module in the dependency graph."""

    @property
    @abstractmethod
    def identifier(self) -> str:
        pass

    @property
    @abstractmethod
    def identifier_is_regex(self) -> bool:
        pass

    @property
    @abstractmethod
    def identifier_is_parent_module(self) -> bool:
        pass


@dataclass(frozen=True)
class ModuleNameFilter(ModuleFilter):
    """Represents a way to identify a python module in the dependency graph by its name."""

    name: str

    @property
    def identifier(self) -> str:
        return self.name

    @property
    def identifier_is_regex(self) -> bool:
        return False

    @property
    def identifier_is_parent_module(self) -> bool:
        return False


@dataclass(frozen=True)
class ParentModuleNameFilter(ModuleFilter):
    """Represents a way to identify a python module in the dependency graph by the name of its parent module."""

    parent_module: str

    @property
    def identifier(self) -> str:
        return self.parent_module

    @property
    def identifier_is_regex(self) -> bool:
        return False

    @property
    def identifier_is_parent_module(self) -> bool:
        return True


@dataclass(frozen=True)
class ModuleNameRegexFilter(ModuleFilter):
    """Represents a way to identify a python module in the dependency graph.
    The module is identified by a regex pattern for its name.
    """

    name: str

    @property
    def identifier(self) -> str:
        return self.name

    @property
    def identifier_is_regex(self) -> bool:
        return True

    @property
    def identifier_is_parent_module(self) -> bool:
        return False


@dataclass(frozen=True)
class Module:
    """Represents an actual python module found in the dependency graph."""

    identifier: str

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

    identifier: str

    @property
    def is_single_module(self) -> bool:
        return False


Dependency = tuple[Module, Module]
# key: user-requested dependency
# values: list of exact modules that show this dependency
ExplicitlyRequestedDependenciesByBaseModules = dict[Dependency, list[Dependency]]
# key: module that either has dependencies or that others are dependent on that were not explicitly requested
# via the rule the user has specified
# value: importer and importee that were not found
NotExplicitlyRequestedDependenciesByBaseModule = dict[Module, list[Dependency]]


class EvaluableArchitecture(Protocol):
    def get_dependencies(
        self,
        dependents: Iterable[ModuleFilter],
        dependent_upons: Iterable[ModuleFilter],
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
        dependents: Sequence[ModuleFilter],
        dependent_upons: Sequence[ModuleFilter],
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
        dependents: Sequence[ModuleFilter],
        dependent_upons: Sequence[ModuleFilter],
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
    def modules(self) -> list[str]:
        """Return names of all modules that are present in this architecture."""
        raise NotImplementedError()
