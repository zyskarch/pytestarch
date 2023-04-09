"""Base class for different graph implementations of an evaluable structure. Delegates direct access to graph nodes
and edges to its subclasses in a template pattern.
"""
from __future__ import annotations

from itertools import product
from typing import Any, List

from pytestarch.eval_structure.breadth_first_searches import (
    any_dependency_to_module_other_than,
    any_other_dependency_to_module_than,
    get_dependency_between_modules,
)
from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    ExplicitlyRequestedDependenciesByBaseModules,
    Module,
    NotExplicitlyRequestedDependenciesByBaseModule,
)
from pytestarch.eval_structure.evaluable_structures import AbstractGraph


class EvaluableArchitectureGraph(EvaluableArchitecture):
    """Abstract implementation of an evaluable object that is based on a graph structure."""

    def __init__(self, graph: AbstractGraph) -> None:
        self._graph = graph

    def get_dependencies(
        self,
        dependents: List[Module],
        dependent_upons: List[Module],
    ) -> ExplicitlyRequestedDependenciesByBaseModules:
        result = {}

        # remove any duplicates
        dependents = set(dependents)
        dependent_upons = set(dependent_upons)

        for dependent, dependent_upon in product(dependents, dependent_upons):
            dependency = get_dependency_between_modules(
                self._graph, dependent, dependent_upon
            )
            result[(dependent, dependent_upon)] = dependency

        return result

    def any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        self,
        dependents: List[Module],
        dependent_upons: List[Module],
    ) -> NotExplicitlyRequestedDependenciesByBaseModule:
        # remove any duplicates
        dependents = set(dependents)
        dependent_upons = set(dependent_upons)

        result = {}

        for dependent in dependents:
            dependencies = any_dependency_to_module_other_than(
                self._graph, dependent, dependent_upons
            )
            result[dependent] = dependencies

        return result

    def any_other_dependencies_on_dependent_upons_than_from_dependents(
        self,
        dependents: List[Module],
        dependent_upons: List[Module],
    ) -> NotExplicitlyRequestedDependenciesByBaseModule:
        # remove any duplicates
        dependents = set(dependents)
        dependent_upons = set(dependent_upons)

        result = {}

        for dependent_upon in dependent_upons:
            dependencies = any_other_dependency_to_module_than(
                self._graph, dependents, dependent_upon
            )
            result[dependent_upon] = dependencies

        return result

    def visualize(self, **kwargs: Any) -> None:
        self._graph.draw(**kwargs)

    @property
    def modules(self) -> List[str]:
        return self._graph.nodes
