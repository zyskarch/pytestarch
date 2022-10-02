"""Encapsulation of networkx graph functionality."""
from typing import Any, List, Optional, Tuple

import networkx as nx
from networkx import draw_networkx, has_path, spring_layout

from pytestarch.eval_structure.evaluable_structures import AbstractGraph, AbstractNode
from pytestarch.importer.import_types import Import

EXPECTED_EDGE_AND_NODE_TYPES = "Only str and tuple of two str supported."


Node = AbstractNode


class NetworkxGraph(AbstractGraph):
    """Constructs eval_structure from list of imports.

    Each module passed to this object will be added as a node.
    Importing and imported module are connected via a direct edge.
    Edges are added between each successive level in the module hierarchy.

    E.g.
    Import('A.B', 'C.D.E') results in
    - nodes: ['A', 'A.B', 'C', 'C.D', 'C.D.E']
    - edges: [('A', 'A.B'), ('C', 'C.D'), ('C.D', 'C.D.E'), ('A.B', 'C.D.E')]

    """

    def __init__(
        self,
        all_modules: List[Node],
        imports: List[Import],
        level_limit: Optional[int] = None,
    ) -> None:
        """
        Args:
            all_modules: list of all nodes in the graph, which can be connected by imports.
            imports: all dependencies between the graph's nodes.
            level_limit: if not None, specifies the depth of the graph
        """
        self._all_modules = all_modules
        self._imports = imports
        self._graph = nx.DiGraph()

        self._level_limit = level_limit

        self._initialise()

    def _initialise(self) -> None:
        """Constructs a graph from all modules and their imports."""
        self._add_all_modules_as_nodes()

        for imp in self._imports:
            importer = imp.importer()
            importee = imp.importee()

            self._create_edge(importer, importee)

            self._add_edges_within_module_hierarchy(
                imp.importer_parent_modules(),
                importer,
            )

            all_importee_modules = imp.importee_parent_modules() + [importee]

            for parent, child in zip(
                all_importee_modules[:-1], all_importee_modules[1:]
            ):
                self._create_edge(parent, child, inherits=True)

    def _add_all_modules_as_nodes(self) -> None:
        for module in self._all_modules:
            self._create_node(module)

    def _add_edges_within_module_hierarchy(
        self,
        parent_modules: List[Node],
        child: Node,
    ) -> None:
        """Create edges between a node and its parent recursively until the parent-less parent is reached.

        Args:
            parent_modules: list of all parent modules in order, last element is the direct parent of the child module
            child: lowest element in the module hierarchy
        """
        all_modules = parent_modules + [child]
        for parent, child in zip(all_modules[:-1], all_modules[1:]):
            self._create_edge(parent, child, inherits=True)

    def _create_node(self, node: Node) -> None:
        """Create a node in the dependency graph.
        Args:
            node: to add to the graph
        """
        node = self._flatten_graph_node(node)

        if node not in self._graph:
            self._graph.add_node(node)

    def _create_edge(
        self, node_start: Node, node_end: Node, inherits: bool = False
    ) -> None:
        """Creates an edge in the graph between the two given modules.

        Args:
            node_start: node the edge starts from
            node_end: node the edge points towards
            inherits: if True, edge will be marked as belonging to two nodes that are connected in a parent-child-relationship
        """
        node_start = self._flatten_graph_node(node_start)
        node_end = self._flatten_graph_node(node_end)

        if node_start == node_end:
            return

        # "from foo import bar" - bar could be a function/class in foo
        # or a submodule of foo
        # in order to not add a function/class to the eval_structure, an ende to
        # foo.bar will only be added if both importer
        # and importee are already part of the eval_structure (which they will
        # be if they correspond to modules in the file system
        if (
            self._graph.has_node(node_start)
            and self._graph.has_node(node_end)
            and not self._graph.has_edge(node_start, node_end)
        ):
            self._graph.add_edge(node_start, node_end, inherits=inherits)

    def __contains__(self, item) -> bool:
        if not isinstance(item, (str, tuple)):
            raise TypeError(EXPECTED_EDGE_AND_NODE_TYPES)

        if isinstance(item, str):
            return self._graph.has_node(item)

        if (
            len(item) > 2
            or not isinstance(item[0], str)
            or not isinstance(item[1], str)
        ):
            TypeError(EXPECTED_EDGE_AND_NODE_TYPES)

        return self._graph.has_edge(*item) or has_path(self._graph, *item)

    @property
    def edges_number(self) -> int:
        return self._graph.number_of_edges()

    @property
    def nodes_number(self) -> int:
        return self._graph.number_of_nodes()

    @property
    def nodes(self) -> List[Node]:
        return list(self._graph.nodes)

    @property
    def edges(self) -> List[Tuple[Node, Node]]:
        return list(self._graph.edges)

    def direct_predecessor_nodes(self, node: Node) -> List[Node]:
        """Returns all nodes that have a directed edge towards the given node.

        Args:
            node: node for which to retrieve predecessor nodes

        Returns:
            all predecessor nodes
        """
        return sorted(self._graph.predecessors(node))

    def direct_successor_nodes(self, node: Node) -> List[Node]:
        """Returns all nodes that the given node has a directed edge towards.

        Args:
            node: node for which to retrieve successor nodes

        Returns:
            all successor nodes
        """
        return sorted(self._graph.successors(node))

    def parent_child_relationship(
        self, supposed_parent_node: Node, supposed_child_node: Node
    ) -> bool:
        """Returns True if the given nodes are marked as a parent-child hierarchy.

        Args:
            supposed_parent_node:
            supposed_child_node:

        Returns:
            True if supposed parent is actually parent of supposed child node
        """
        edge_data = self._graph.get_edge_data(supposed_parent_node, supposed_child_node)

        return edge_data["inherits"]

    def draw(self, **kwargs: Any) -> None:
        """Creates a matplotlib plot representing the graph."""
        if "spacing" in kwargs:
            spacing = kwargs.pop("spacing")
            pos = spring_layout(self._graph, k=spacing, iterations=20)
            kwargs["pos"] = pos

        draw_networkx(self._graph, **kwargs)

    def _flatten_graph_node(self, node: Node) -> Node:
        """Limits the depth of the graph by aggregating sub modules above a certain limit.
        Args:
            node: name of node to flatten.

        Returns: flattened name, i.e. only containing at most level limit "." module separators
        """
        if self._level_limit is None:
            return node

        # level 1: include all children of base module:
        # base module: src
        # children: src.A, src.B
        # not to be included: src.A.a, src.A.aa, src.B.b, ...
        # logic: include at most level "." in the node name

        node_parts = node.split(".")
        return ".".join(node_parts[: self._level_limit + 1])
