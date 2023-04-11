from __future__ import annotations

import pytest

from pytestarch.eval_structure.evaluable_architecture import Module, ModuleFilter
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport

MODULE_1 = "Module1"
MODULE_FILTER_OBJECT_1 = ModuleFilter(name=MODULE_1)
MODULE_OBJECT_1 = Module(name=MODULE_1)
MODULE_2 = "Module2"
MODULE_FILTER_OBJECT_2 = ModuleFilter(name=MODULE_2)
MODULE_OBJECT_2 = Module(name=MODULE_2)
MODULE_3 = "Module3"
MODULE_FILTER_OBJECT_3 = ModuleFilter(name=MODULE_3)
MODULE_OBJECT_3 = Module(name=MODULE_3)
MODULE_4 = "Module4"
MODULE_FILTER_OBJECT_4 = ModuleFilter(name=MODULE_4)
MODULE_OBJECT_4 = Module(name=MODULE_4)
MODULE_6 = "Module6"
MODULE_FILTER_OBJECT_6 = ModuleFilter(name=MODULE_6)
MODULE_OBJECT_6 = Module(name=MODULE_6)
SUB_MODULE_OF_2 = "Module2.SubModule1"
SUB_MODULE_FILTER_OBJECT_2 = ModuleFilter(name=SUB_MODULE_OF_2)
SUB_MODULE_OBJECT_2 = Module(name=SUB_MODULE_OF_2)
SUB_MODULE_OF_1 = "Module1.SubModule1"
MODULE_A = "E.A"  # submodule of E
MODULE_B = "E.A.B"  # submodule of A
MODULE_C = "C"
MODULE_D = "E.A.B.D"  # submodule of B
MODULE_E = "E"
MODULE_F = "E.F"  # submodule of E


@pytest.fixture(scope="session")
def evaluable() -> EvaluableArchitectureGraph:
    all_modules = [MODULE_1, MODULE_2, MODULE_3, MODULE_4, SUB_MODULE_OF_2, MODULE_6]
    imports = [
        AbsoluteImport(MODULE_1, MODULE_2),
        AbsoluteImport(MODULE_1, MODULE_3),
        AbsoluteImport(MODULE_1, MODULE_4),
        AbsoluteImport(MODULE_3, MODULE_2),
        AbsoluteImport(MODULE_4, SUB_MODULE_OF_2),
        AbsoluteImport(MODULE_3, MODULE_6),
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))


@pytest.fixture(scope="session")
def submodule_evaluable() -> EvaluableArchitectureGraph:
    all_modules = [MODULE_A, MODULE_B, MODULE_C, MODULE_D, MODULE_E, MODULE_F]
    imports = [
        AbsoluteImport(MODULE_F, MODULE_C),
        AbsoluteImport(MODULE_C, MODULE_A),
        AbsoluteImport(MODULE_C, MODULE_B),
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))
