import pytest

from pytestarch.eval_structure.eval_structure_types import Evaluable, Module
from pytestarch.eval_structure.evaluable_graph import EvaluableGraph
from pytestarch.eval_structure.graph import Graph
from pytestarch.importer.import_types import AbsoluteImport


MODULE_1 = "Module1"
MODULE_2 = "Module2"
MODULE_3 = "Module3"
MODULE_4 = "Module4"
MODULE_6 = "Module6"
SUB_MODULE_OF_2 = "Module2.SubModule1"

MODULE_A = "E.A"  # submodule of E
MODULE_B = "E.A.B"  # submodule of A
MODULE_C = "C"
MODULE_D = "E.A.B.D"  # submodule of B
MODULE_E = "E"
MODULE_F = "E.F"  # submodule of E


@pytest.fixture(scope="module")
def evaluable() -> Evaluable:
    all_modules = [MODULE_1, MODULE_2, MODULE_3, MODULE_4, SUB_MODULE_OF_2, MODULE_6]
    imports = [
        AbsoluteImport(MODULE_1, MODULE_2),
        AbsoluteImport(MODULE_1, MODULE_3),
        AbsoluteImport(MODULE_1, MODULE_4),
        AbsoluteImport(MODULE_3, MODULE_2),
        AbsoluteImport(MODULE_4, SUB_MODULE_OF_2),
        AbsoluteImport(MODULE_3, MODULE_6),
    ]

    return EvaluableGraph(Graph(all_modules, imports))


@pytest.fixture(scope="module")
def submodule_evaluable() -> Evaluable:
    all_modules = [MODULE_A, MODULE_B, MODULE_C, MODULE_D, MODULE_E, MODULE_F]
    imports = [
        AbsoluteImport(MODULE_F, MODULE_C),
        AbsoluteImport(MODULE_C, MODULE_A),
        AbsoluteImport(MODULE_C, MODULE_B),
    ]

    return EvaluableGraph(Graph(all_modules, imports))


def test_a_depends_on_non_b(evaluable: Evaluable) -> None:
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_1), Module(name=MODULE_2)
    )
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_1), Module(name=MODULE_3)
    )
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_1), Module(name=MODULE_4)
    )
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_1), Module(name=SUB_MODULE_OF_2)
    )
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_1), Module(name=MODULE_6)
    )

    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_2), Module(name=MODULE_1)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_2), Module(name=MODULE_3)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_2), Module(name=MODULE_4)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_2), Module(name=SUB_MODULE_OF_2)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_2), Module(name=MODULE_6)
    )

    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_3), Module(name=MODULE_1)
    )
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_3), Module(name=MODULE_2)
    )
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_3), Module(name=MODULE_4)
    )
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_3), Module(name=SUB_MODULE_OF_2)
    )
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_3), Module(name=MODULE_6)
    )

    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_4), Module(name=MODULE_1)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_4), Module(name=MODULE_2)
    )
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_4), Module(name=MODULE_3)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_4), Module(name=SUB_MODULE_OF_2)
    )
    assert evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_4), Module(name=MODULE_6)
    )

    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_1)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_2)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_3)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_4)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_6)
    )

    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_6), Module(name=MODULE_1)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_6), Module(name=MODULE_2)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_6), Module(name=MODULE_3)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_6), Module(name=MODULE_4)
    )
    assert not evaluable.any_dependency_to_module_other_than(
        Module(name=MODULE_6), Module(name=SUB_MODULE_OF_2)
    )


def test_non_a_depends_on_b(evaluable: Evaluable) -> None:
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_1), Module(name=MODULE_2)
    )
    assert not evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_1), Module(name=MODULE_3)
    )
    assert not evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_1), Module(name=MODULE_4)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_1), Module(name=SUB_MODULE_OF_2)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_1), Module(name=MODULE_6)
    )

    assert not evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_2), Module(name=MODULE_1)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_2), Module(name=MODULE_3)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_2), Module(name=MODULE_4)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_2), Module(name=SUB_MODULE_OF_2)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_2), Module(name=MODULE_6)
    )

    assert not evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_3), Module(name=MODULE_1)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_3), Module(name=MODULE_2)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_3), Module(name=MODULE_4)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_3), Module(name=SUB_MODULE_OF_2)
    )
    assert not evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_3), Module(name=MODULE_6)
    )

    assert not evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_4), Module(name=MODULE_1)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_4), Module(name=MODULE_2)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_4), Module(name=MODULE_3)
    )
    assert not evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_4), Module(name=SUB_MODULE_OF_2)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_4), Module(name=MODULE_6)
    )

    assert not evaluable.any_other_dependency_to_module_than(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_1)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_2)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_3)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_4)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_6)
    )

    assert not evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_6), Module(name=MODULE_1)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_6), Module(name=MODULE_2)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_6), Module(name=MODULE_3)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_6), Module(name=MODULE_4)
    )
    assert evaluable.any_other_dependency_to_module_than(
        Module(name=MODULE_6), Module(name=SUB_MODULE_OF_2)
    )


def test_depends_on(evaluable: Evaluable) -> None:
    assert evaluable.is_dependent(Module(name=MODULE_1), Module(name=MODULE_2))
    assert evaluable.is_dependent(Module(name=MODULE_1), Module(name=MODULE_3))
    assert evaluable.is_dependent(Module(name=MODULE_1), Module(name=MODULE_4))
    assert not evaluable.is_dependent(
        Module(name=MODULE_1), Module(name=SUB_MODULE_OF_2)
    )
    assert not evaluable.is_dependent(Module(name=MODULE_1), Module(name=MODULE_6))

    assert not evaluable.is_dependent(Module(name=MODULE_2), Module(name=MODULE_1))
    assert not evaluable.is_dependent(Module(name=MODULE_2), Module(name=MODULE_3))
    assert not evaluable.is_dependent(Module(name=MODULE_2), Module(name=MODULE_4))
    assert not evaluable.is_dependent(
        Module(name=MODULE_2), Module(name=SUB_MODULE_OF_2)
    )
    assert not evaluable.is_dependent(Module(name=MODULE_2), Module(name=MODULE_6))

    assert not evaluable.is_dependent(Module(name=MODULE_3), Module(name=MODULE_1))
    assert evaluable.is_dependent(Module(name=MODULE_3), Module(name=MODULE_2))
    assert not evaluable.is_dependent(Module(name=MODULE_3), Module(name=MODULE_4))
    assert not evaluable.is_dependent(
        Module(name=MODULE_3), Module(name=SUB_MODULE_OF_2)
    )
    assert evaluable.is_dependent(Module(name=MODULE_3), Module(name=MODULE_6))

    assert not evaluable.is_dependent(Module(name=MODULE_4), Module(name=MODULE_1))
    assert evaluable.is_dependent(Module(name=MODULE_4), Module(name=MODULE_2))
    assert not evaluable.is_dependent(Module(name=MODULE_4), Module(name=MODULE_3))
    assert evaluable.is_dependent(Module(name=MODULE_4), Module(name=SUB_MODULE_OF_2))
    assert not evaluable.is_dependent(Module(name=MODULE_4), Module(name=MODULE_6))

    assert not evaluable.is_dependent(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_1)
    )
    assert not evaluable.is_dependent(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_2)
    )
    assert not evaluable.is_dependent(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_3)
    )
    assert not evaluable.is_dependent(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_4)
    )
    assert not evaluable.is_dependent(
        Module(name=SUB_MODULE_OF_2), Module(name=MODULE_6)
    )

    assert not evaluable.is_dependent(Module(name=MODULE_6), Module(name=MODULE_1))
    assert not evaluable.is_dependent(Module(name=MODULE_6), Module(name=MODULE_2))
    assert not evaluable.is_dependent(Module(name=MODULE_6), Module(name=MODULE_3))
    assert not evaluable.is_dependent(Module(name=MODULE_6), Module(name=MODULE_4))
    assert not evaluable.is_dependent(
        Module(name=MODULE_6), Module(name=SUB_MODULE_OF_2)
    )


def test_submodule_calculation(submodule_evaluable: EvaluableGraph) -> None:
    assert submodule_evaluable._get_all_submodules_of(Module(name=MODULE_A)) == {
        MODULE_A,
        MODULE_B,
    }  # D does not show up as it is not connected to any import
    assert submodule_evaluable._get_all_submodules_of(Module(name=MODULE_B)) == {
        MODULE_B
    }  # D does not show up as it is not connected to any import
    assert submodule_evaluable._get_all_submodules_of(Module(name=MODULE_C)) == {
        MODULE_C
    }
    assert submodule_evaluable._get_all_submodules_of(Module(name=MODULE_D)) == {
        MODULE_D
    }
    assert submodule_evaluable._get_all_submodules_of(Module(name=MODULE_E)) == {
        MODULE_E,
        MODULE_A,
        MODULE_B,
        MODULE_F,
    }  # D does not show up as it is not connected to any import
    assert submodule_evaluable._get_all_submodules_of(Module(name=MODULE_F)) == {
        MODULE_F
    }
