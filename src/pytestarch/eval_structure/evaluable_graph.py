"""Base class for different graph implementations of an evaluable structure. Delegates direct access to graph nodes
and edges to its subclasses in a template pattern.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from itertools import product
from typing import Any

from pytestarch.eval_structure.breadth_first_searches import (
    any_dependency_to_module_other_than,
    any_other_dependency_to_module_than,
    get_dependency_between_modules,
)
from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    ExplicitlyRequestedDependenciesByBaseModules,
    ModuleFilter,
    NotExplicitlyRequestedDependenciesByBaseModule,
)
from pytestarch.eval_structure.evaluable_structures import AbstractGraph
from pytestarch.eval_structure.utils import filter_to_module


class EvaluableArchitectureGraph(EvaluableArchitecture):
    """Abstract implementation of an evaluable object that is based on a graph structure."""

    def __init__(self, graph: AbstractGraph) -> None:
        self._graph = graph

    def get_dependencies(
        self,
        dependents: Iterable[ModuleFilter],
        dependent_upons: Iterable[ModuleFilter],
    ) -> ExplicitlyRequestedDependenciesByBaseModules:
        result = {}

        # remove any duplicates
        dependents_set = set(dependents)
        dependent_upons_set = set(dependent_upons)

        for dependent, dependent_upon in product(dependents_set, dependent_upons_set):
            dependency = get_dependency_between_modules(
                self._graph, dependent, dependent_upon
            )
            result[(filter_to_module(dependent), filter_to_module(dependent_upon))] = (
                dependency
            )

        return result

    def any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        self,
        dependents: Sequence[ModuleFilter],
        dependent_upons: Sequence[ModuleFilter],
    ) -> NotExplicitlyRequestedDependenciesByBaseModule:
        # remove any duplicates
        dependents_set = set(dependents)
        dependent_upons_set = set(dependent_upons)

        result = {}

        for dependent in dependents_set:
            dependencies = any_dependency_to_module_other_than(
                self._graph, dependent, dependent_upons_set
            )
            result[filter_to_module(dependent)] = dependencies

        return result

    def any_other_dependencies_on_dependent_upons_than_from_dependents(
        self,
        dependents: Sequence[ModuleFilter],
        dependent_upons: Sequence[ModuleFilter],
    ) -> NotExplicitlyRequestedDependenciesByBaseModule:
        # remove any duplicates
        dependents_set = set(dependents)
        dependent_upons_set = set(dependent_upons)

        result = {}

        for dependent_upon in dependent_upons_set:
            dependencies = any_other_dependency_to_module_than(
                self._graph, dependents_set, dependent_upon
            )
            result[filter_to_module(dependent_upon)] = dependencies

        return result

    def visualize(self, **kwargs: Any) -> None:
        self._graph.draw(**kwargs)  # type: ignore

    @property
    def modules(self) -> list[str]:
        return self._graph.nodes
