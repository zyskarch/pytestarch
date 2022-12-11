from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport


def test_empty_graph_allowed() -> None:
    NetworkxGraph([], [])

    assert True


def test_graph_as_expected() -> None:
    imports = [
        AbsoluteImport("A", "B"),
        AbsoluteImport("B", "C"),
        AbsoluteImport("A", "C"),
    ]
    graph = NetworkxGraph(["A", "B", "C"], imports)

    assert "A" in graph
    assert "B" in graph
    assert "C" in graph

    assert ("A", "B") in graph
    assert ("B", "C") in graph
    assert ("A", "C") in graph


def test_duplicate_edges_do_not_raise_error() -> None:
    imports = [AbsoluteImport("A", "B"), AbsoluteImport("A", "B")]
    graph = NetworkxGraph(["A", "B"], imports)

    assert len(graph._graph.nodes) == 2
    assert len(graph._graph.edges) == 1
