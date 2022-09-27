"""Base class for different graph implementations of an evaluable structure. Delegates direct access to graph nodes
and edges to its subclasses in a template pattern.
"""
from typing import Set, Any, Optional, Tuple, List

from pytestarch.eval_structure.eval_structure_types import EvaluableArchitecture, Module
from pytestarch.eval_structure.graph import Graph, Node


class EvaluableArchitectureGraph(EvaluableArchitecture):
    """Abstract implementation of an evaluable object that is based on a graph structure."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    def is_dependent(
        self, dependent: Module, dependent_upon: Module
    ) -> Optional[Tuple[str, str]]:
        dependent_node = self._get_node(dependent)
        dependent_upon_nodes = self._get_all_submodules_of(dependent_upon)

        nodes_to_check = [dependent_node]
        checked_nodes = set()

        while nodes_to_check:
            node = nodes_to_check.pop()

            if node in checked_nodes:
                continue

            checked_nodes.add(node)

            children = self._graph.direct_successor_nodes(node)

            for child in children:
                if self._graph.parent_child_relationship(node, child):
                    nodes_to_check.append(child)

                elif child in dependent_upon_nodes:
                    return node, child

        return None

    def _get_node(self, dependent: Module) -> Node:
        return dependent.name or dependent.parent_module

    def any_dependency_to_module_other_than(
        self, dependent: Module, dependent_upon: Module
    ) -> List[Module]:
        nodes_to_exclude = self._get_all_submodules_of(dependent_upon)

        nodes_fulfilling_criteria = []
        nodes_that_do_not_fulfill_criterion = self._get_all_submodules_of(dependent)

        nodes_to_check = list(nodes_that_do_not_fulfill_criterion)
        checked_nodes = set()

        while nodes_to_check:
            if nodes_fulfilling_criteria:
                break

            node = nodes_to_check.pop()

            if node in checked_nodes:
                continue

            if node in nodes_to_exclude:
                continue

            checked_nodes.add(node)

            children = self._graph.direct_successor_nodes(node)

            for child in children:

                if not self._graph.parent_child_relationship(node, child):
                    if (
                        child not in nodes_to_exclude
                        and child not in nodes_that_do_not_fulfill_criterion
                    ):
                        nodes_fulfilling_criteria.append(child)

                    nodes_to_check.append(child)

        return self._to_modules(nodes_fulfilling_criteria)

    def any_other_dependency_to_module_than(
        self, dependent: Module, dependent_upon: Module
    ) -> List[Module]:
        nodes_to_exclude = self._get_all_submodules_of(dependent)

        nodes_fulfilling_criteria = []
        nodes_that_count_as_not_fulfilling_criterion = self._get_all_submodules_of(
            dependent_upon
        )

        nodes_to_check = list(nodes_that_count_as_not_fulfilling_criterion)
        checked_nodes = set()

        while nodes_to_check:
            node = nodes_to_check.pop()

            if node in checked_nodes:
                continue

            checked_nodes.add(node)

            children = self._graph.direct_predecessor_nodes(node)

            for child in children:

                if not self._graph.parent_child_relationship(child, node):
                    if (
                        child not in nodes_to_exclude
                        and child not in nodes_that_count_as_not_fulfilling_criterion
                    ):
                        nodes_fulfilling_criteria.append(child)

                    if child not in nodes_to_exclude:
                        nodes_to_check.append(child)

        return self._to_modules(nodes_fulfilling_criteria)

    def _to_modules(self, nodes: List[Node]) -> List[Module]:
        return list(map(lambda node: Module(name=node), nodes))

    def _get_all_submodules_of(self, module: Module) -> Set[Node]:
        """Returns all submodules of a given module.

        Args:
            module: module to retrieve submodules of

        Returns:
            all submodules, including the module itself
        """
        start_node = self._get_node(module)

        nodes_to_check = [start_node]
        checked_nodes = set()

        submodules = set()

        while nodes_to_check:
            node = nodes_to_check.pop()

            if node in checked_nodes:
                continue

            checked_nodes.add(node)
            submodules.add(node)

            children = self._graph.direct_successor_nodes(node)

            for child in children:
                if self._graph.parent_child_relationship(node, child):
                    nodes_to_check.append(child)

        return submodules

    def visualize(self, **kwargs: Any) -> None:
        self._graph.draw(**kwargs)
