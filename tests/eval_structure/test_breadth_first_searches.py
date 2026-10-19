from __future__ import annotations

from eval_structure.conftest import (
    MODULE_A,
    MODULE_B,
    MODULE_C,
    MODULE_D,
    MODULE_E,
    MODULE_F,
)
from pytestarch.eval_structure.breadth_first_searches import get_all_submodules_of
from pytestarch.eval_structure.evaluable_architecture import ModuleNameFilter
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph


def test_submodule_calculation(submodule_evaluable: EvaluableArchitectureGraph) -> None:
    assert get_all_submodules_of(
        submodule_evaluable._graph, ModuleNameFilter(name=MODULE_A)
    ) == {
        MODULE_A,
        MODULE_B,
        MODULE_D,
    }
    assert get_all_submodules_of(
        submodule_evaluable._graph, ModuleNameFilter(name=MODULE_B)
    ) == {
        MODULE_B,
        MODULE_D,
    }
    assert get_all_submodules_of(
        submodule_evaluable._graph, ModuleNameFilter(name=MODULE_C)
    ) == {MODULE_C}
    assert get_all_submodules_of(
        submodule_evaluable._graph, ModuleNameFilter(name=MODULE_D)
    ) == {MODULE_D}
    assert get_all_submodules_of(
        submodule_evaluable._graph, ModuleNameFilter(name=MODULE_E)
    ) == {
        MODULE_E,
        MODULE_A,
        MODULE_B,
        MODULE_F,
        MODULE_D,
    }
    assert get_all_submodules_of(
        submodule_evaluable._graph, ModuleNameFilter(name=MODULE_F)
    ) == {MODULE_F}
