"""Base class for different graph implementations of an evaluable structure. Delegates direct access to graph nodes
and edges to its subclasses in a template pattern.
"""
from typing import Callable, Iterable, Optional, Set, Any

from pytestarch.eval_structure.eval_structure_types import Evaluable, Module
from pytestarch.eval_structure.graph import Graph, Node


class EvaluableGraph(Evaluable):
    """Abstract implementation of an evaluable object that is based on a graph structure."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    def is_dependent(self, dependent: Module, dependent_upon: Module) -> bool:
        dependent_node = self._get_node(dependent)
        dependent_upon_node = self._get_node(dependent_upon)

        path_exists = self._path_between_nodes(dependent_node, dependent_upon_node)

        if path_exists:
            return True

        for submodule in self._get_all_submodules_of(dependent_upon):
            if self._path_between_nodes(dependent_node, submodule):
                return True

        return False

    def _get_node(self, dependent: Module) -> Node:
        return dependent.name or dependent.parent_module

    def any_dependency_to_module_other_than(
        self, dependent: Module, dependent_upon: Module
    ) -> Set[Module]:
        dependent_nodes = self._breadth_first_search(
            dependent,
            self._graph.direct_successor_nodes,
            lambda parent, child: not self._graph.parent_child_relationship(
                parent, child
            ),
            nodes_to_exclude=self._get_all_submodules_of(dependent_upon),
            only_consider_children_of_nodes_fulfilling_criterion=False,
            start_node_fulfills_criterion=False,
            early_stop=True,
        )
        return self._to_module_set(dependent_nodes)

    def any_dependency_to_other_module_than(
        self, dependent: Module, dependent_upon: Module
    ) -> Set[Module]:
        dependent_nodes = self._breadth_first_search(
            dependent_upon,
            self._graph.direct_predecessor_nodes,
            lambda parent, child: not self._graph.parent_child_relationship(
                child, parent
            ),
            nodes_to_exclude=self._get_all_submodules_of(dependent),
            only_consider_children_of_nodes_fulfilling_criterion=False,
            start_node_fulfills_criterion=False,
            early_stop=True,
            additional_start_nodes=self._get_all_submodules_of(dependent_upon),
        )
        return self._to_module_set(dependent_nodes)

    def _to_module_set(self, nodes: Set[Node]) -> Set[Module]:
        return set(map(lambda node: Module(name=node), nodes))

    def _get_all_submodules_of(self, module: Module) -> Set[Node]:
        """Returns all submodules of a given module.

        Args:
            module: module to retrieve submodules of

        Returns:
            all submodules
        """
        return self._breadth_first_search(
            module,
            self._graph.direct_successor_nodes,
            self._graph.parent_child_relationship,
        )

    def _breadth_first_search(
        self,
        module: Module,
        get_successors: Callable[[Node], Iterable[Node]],
        criterion_fulfilled: Callable[[Node, Node], bool],
        nodes_to_exclude: Optional[Set[Node]] = None,
        only_consider_children_of_nodes_fulfilling_criterion: bool = True,
        start_node_fulfills_criterion: bool = True,
        early_stop: bool = False,
        additional_start_nodes: Optional[Set[Node]] = None,
    ) -> Set[Node]:
        """Conducts a BFS on the evaluable graph and returns all nodes that match given criteria.

        Attributes:
            module: start module
            get_successors: function to retrieve nodes to consider next after the current node
            criterion_fulfilled: function that returns True if a given node fulfills the criteria to be included in the result
            nodes_to_exclude: set of nodes that should not be included in the result, even if they match the other criteria
            only_consider_children_of_nodes_fulfilling_criterion: if True, child nodes of nodes that do not fulfill the result criteria will not be evaluated
            start_node_fulfills_criterion: True if the start node representing the start module if defined as fulfilling the result criteria
            early_stop: if True, search will be aborted once a node fulfilling the result criteria has been found
            additional_start_nodes: set of nodes that should be searched even if they are not reachable from the start module

        Returns:
            nodes that match all criteria
        """
        nodes_to_exclude = {} if nodes_to_exclude is None else nodes_to_exclude

        start_node = self._get_node(module)
        modules_fulfilling_criteria = (
            {start_node} if start_node_fulfills_criterion else set()
        )

        # successors should not always include parent modules,
        # e.g. when calculating not submodules
        nodes_to_check = {(start_node, node) for node in get_successors(start_node)}
        if additional_start_nodes:
            for additional_start_node in additional_start_nodes:
                nodes_to_check.update(
                    {
                        (additional_start_node, node)
                        for node in get_successors(additional_start_node)
                    }
                )

        checked_nodes = {start_node}

        while nodes_to_check:
            if early_stop and modules_fulfilling_criteria:
                break

            parent, child = nodes_to_check.pop()

            if child in checked_nodes:
                continue

            checked_nodes.add(child)

            if child in nodes_to_exclude:
                continue

            if criterion_fulfilled(parent, child):
                modules_fulfilling_criteria.add(child)

                if only_consider_children_of_nodes_fulfilling_criterion:
                    nodes_to_check.update(
                        {(child, node) for node in get_successors(child)}
                    )

            if not only_consider_children_of_nodes_fulfilling_criterion:
                nodes_to_check.update({(child, node) for node in get_successors(child)})

        return modules_fulfilling_criteria

    def _path_between_nodes(self, start_node: Node, end_node: Node) -> bool:
        all_paths = self._graph.all_paths_between(start_node, end_node)

        # follow path into submodules of start node until the first edge is a non-parent-child edge
        # once this has been found, no further parent-child-edges are allowed.
        # reason: if a submodule of module A depends on module B, module A also depends on it by definition
        # -> follow path into submodules
        # however, if module B has a submodule as well, module A does not automatically depend on this submodule as well
        # -> no further parent-child-edges after the first non-parent-child one allowed
        for path in all_paths:
            non_inheriting_edge_seen = False
            valid_path = True
            for edge in path:
                is_inheriting_edge = self._graph.parent_child_relationship(
                    edge[0], edge[1]
                )
                if is_inheriting_edge and non_inheriting_edge_seen:
                    valid_path = False
                    break
                if not is_inheriting_edge:
                    non_inheriting_edge_seen = True

            if valid_path:
                return True

        return False

    def visualize(self, **kwargs: Any) -> None:
        self._graph.draw(**kwargs)
