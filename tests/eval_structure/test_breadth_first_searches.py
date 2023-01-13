from __future__ import annotations

import pytest
from eval_structure.evaluable_graph.conftest import (
    MODULE_A,
    MODULE_B,
    MODULE_C,
    MODULE_D,
    MODULE_E,
    MODULE_F,
)

from pytestarch.eval_structure.breadth_first_searches import _get_all_submodules_of
from pytestarch.eval_structure.evaluable_architecture import Module
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport


@pytest.fixture(scope="module")
def submodule_evaluable() -> EvaluableArchitectureGraph:
    all_modules = [MODULE_A, MODULE_B, MODULE_C, MODULE_D, MODULE_E, MODULE_F]
    imports = [
        AbsoluteImport(MODULE_F, MODULE_C),
        AbsoluteImport(MODULE_C, MODULE_A),
        AbsoluteImport(MODULE_C, MODULE_B),
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))


def test_submodule_calculation(submodule_evaluable: EvaluableArchitectureGraph) -> None:
    assert _get_all_submodules_of(
        submodule_evaluable._graph, Module(name=MODULE_A)
    ) == {
        MODULE_A,
        MODULE_B,
    }  # D does not show up as it is not connected to any import
    assert _get_all_submodules_of(
        submodule_evaluable._graph, Module(name=MODULE_B)
    ) == {
        MODULE_B
    }  # D does not show up as it is not connected to any import
    assert _get_all_submodules_of(
        submodule_evaluable._graph, Module(name=MODULE_C)
    ) == {MODULE_C}
    assert _get_all_submodules_of(
        submodule_evaluable._graph, Module(name=MODULE_D)
    ) == {MODULE_D}
    assert _get_all_submodules_of(
        submodule_evaluable._graph, Module(name=MODULE_E)
    ) == {
        MODULE_E,
        MODULE_A,
        MODULE_B,
        MODULE_F,
    }  # D does not show up as it is not connected to any import
    assert _get_all_submodules_of(
        submodule_evaluable._graph, Module(name=MODULE_F)
    ) == {MODULE_F}
