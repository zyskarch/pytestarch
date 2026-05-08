from __future__ import annotations

import pytest

from pytestarch.eval_structure.evaluable_architecture import (
    ModuleNameFilter,
    ParentModuleNameFilter,
)
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.exceptions import ModuleUnknown
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport

INTERNAL = "mypackage.service"
EXTERNAL = "django.db"


@pytest.fixture
def graph() -> EvaluableArchitectureGraph:
    return EvaluableArchitectureGraph(
        NetworkxGraph([INTERNAL], [AbsoluteImport(INTERNAL, INTERNAL)])
    )


def test_direct_successor_nodes_raises_not_in_graph(
    graph: EvaluableArchitectureGraph,
) -> None:
    with pytest.raises(ModuleUnknown):
        graph._graph.direct_successor_nodes(EXTERNAL)


def test_direct_predecessor_nodes_raises_not_in_graph(
    graph: EvaluableArchitectureGraph,
) -> None:
    with pytest.raises(ModuleUnknown):
        graph._graph.direct_predecessor_nodes(EXTERNAL)


def test_message_names_missing_module(graph: EvaluableArchitectureGraph) -> None:
    with pytest.raises(ModuleUnknown, match="'django.db' was not found"):
        graph._graph.direct_successor_nodes(EXTERNAL)


def test_message_mentions_exclude_flag(graph: EvaluableArchitectureGraph) -> None:
    with pytest.raises(ModuleUnknown, match="exclude_external_libraries=False"):
        graph._graph.direct_successor_nodes(EXTERNAL)


def test_message_mentions_import_statement(graph: EvaluableArchitectureGraph) -> None:
    with pytest.raises(ModuleUnknown, match="Python import statement"):
        graph._graph.direct_successor_nodes(EXTERNAL)


def test_get_dependencies_raises_not_in_graph(
    graph: EvaluableArchitectureGraph,
) -> None:
    with pytest.raises(ModuleUnknown, match="'django.db' was not found"):
        graph.get_dependencies(
            [ModuleNameFilter(name=INTERNAL)],
            [ModuleNameFilter(name=EXTERNAL)],
        )


def test_any_other_dependency_raises_not_in_graph(
    graph: EvaluableArchitectureGraph,
) -> None:
    with pytest.raises(ModuleUnknown, match="'django.db' was not found"):
        graph.any_other_dependencies_on_dependent_upons_than_from_dependents(
            [ModuleNameFilter(name=INTERNAL)],
            [ParentModuleNameFilter(parent_module=EXTERNAL)],
        )
