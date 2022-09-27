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

    def get_dependency(
        self, dependent: Module, dependent_upon: Module
    ) -> Optional[Tuple[str, str]]:
        dependent_node = self._get_node(dependent)
        dependent_upon_nodes = self._get_all_submodules_of(dependent_upon)

        nodes_to_exclude = self._get_excluded_nodes([dependent, dependent_upon])

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

                elif (
                    child in dependent_upon_nodes
                    and node not in nodes_to_exclude
                    and child not in nodes_to_exclude
                ):
                    return node, child

        return None

    def _get_node(self, dependent: Module) -> Node:
        return dependent.name or dependent.parent_module

    def any_dependency_to_module_other_than(
        self, dependent: Module, dependent_upon: Module
    ) -> List[Module]:
        # submodules of the dependent upon module do not count as an import that is not the dependent upon module
        nodes_to_exclude = self._get_all_submodules_of(dependent_upon)

        nodes_fulfilling_criteria = []
        # should submodules of the dependent module import each other, this does not count as a dependency
        nodes_that_do_not_fulfill_criterion = self._get_all_submodules_of(dependent)

        if dependent.parent_module is not None:
            # if the parent module is set and has a dependency other than dependent upon, it should not count as only
            # true submodules should be considered
            nodes_to_exclude.add(dependent.parent_module)

        if dependent_upon.parent_module is not None:
            # if there is a dependency to the parent module of dependent upon, this counts, as only dependencies to
            # the true submodules are excluded
            nodes_to_exclude.remove(dependent_upon.parent_module)

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
        # submodules of and including the dependent do not count as allowed imports
        nodes_to_exclude = self._get_all_submodules_of(dependent)

        nodes_fulfilling_criteria = []
        # submodules of the dependent upon do not count as allowed imports if they should import each other
        nodes_that_count_as_not_fulfilling_criterion = self._get_all_submodules_of(
            dependent_upon
        )

        if dependent_upon.parent_module is not None:
            # if the dependent upon module is defined via a parent module, this is not included in the list of modules
            # that do not fulfill the criteria - only its true submodules
            nodes_that_count_as_not_fulfilling_criterion.remove(
                dependent_upon.parent_module
            )

        nodes_to_check = list(nodes_that_count_as_not_fulfilling_criterion)

        if dependent.parent_module is not None:
            # if the dependent module is defined via a parent module, this parent module counts as an allowed import
            nodes_to_exclude.remove(dependent.parent_module)

        checked_nodes = set()

        while nodes_to_check:
            node = nodes_to_check.pop()

            if node in checked_nodes:
                continue

            checked_nodes.add(node)

            parents = self._graph.direct_predecessor_nodes(node)

            for parent in parents:

                if not self._graph.parent_child_relationship(parent, node):
                    if (
                        parent not in nodes_to_exclude
                        and parent not in nodes_that_count_as_not_fulfilling_criterion
                    ):
                        nodes_fulfilling_criteria.append(parent)

                    if parent not in nodes_to_exclude:
                        nodes_to_check.append(parent)

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

    def _get_excluded_nodes(self, modules: List[Module]) -> List[Node]:
        result = [module.parent_module for module in modules]
        return [node for node in result if node is not None]
