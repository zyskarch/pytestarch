from __future__ import annotations

import pytest

from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure.evaluable_architecture import Module
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport

MODULE_1 = "Module1"
MODULE_2 = "Module2"
MODULE_3 = "Module3"
MODULE_4 = "Module4"
MODULE_5 = "Module5"
MODULE_6 = "Module6"
SUB_MODULE_OF_7 = "Module7.SubModule1"
MODULE_7 = "Module7"
SUB_MODULE_OF_1 = "Module1.SubModule1"
SUB_SUB_MODULE_OF_1 = "Module1.SubModule1.SubModule1"
MODULE_A = Module(name="A")


@pytest.fixture(scope="session")
def evaluable1() -> EvaluableArchitecture:
    all_modules = [
        MODULE_1,
        MODULE_2,
        MODULE_3,
        MODULE_4,
        MODULE_5,
        MODULE_6,
        SUB_MODULE_OF_7,
        MODULE_7,
        SUB_MODULE_OF_1,
        SUB_SUB_MODULE_OF_1,
    ]
    imports = [
        AbsoluteImport(MODULE_1, MODULE_2),
        AbsoluteImport(MODULE_2, MODULE_3),
        AbsoluteImport(MODULE_4, MODULE_2),
        AbsoluteImport(MODULE_2, MODULE_4),
        AbsoluteImport(MODULE_3, MODULE_5),
        AbsoluteImport(MODULE_6, MODULE_3),
        AbsoluteImport(SUB_MODULE_OF_7, SUB_MODULE_OF_1),
        AbsoluteImport(MODULE_7, SUB_MODULE_OF_7),
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))
