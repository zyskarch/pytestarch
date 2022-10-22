from typing import List

import pytest

from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    Module,
)
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure_impl.networkxgraph import NetworkxGraph
from pytestarch.importer.import_types import AbsoluteImport

MODULE_1 = "Module1"
MODULE_OBJECT_1 = Module(name=MODULE_1)
MODULE_2 = "Module2"
MODULE_OBJECT_2 = Module(name=MODULE_2)
MODULE_3 = "Module3"
MODULE_OBJECT_3 = Module(name=MODULE_3)
MODULE_4 = "Module4"
MODULE_OBJECT_4 = Module(name=MODULE_4)
MODULE_6 = "Module6"
MODULE_OBJECT_6 = Module(name=MODULE_6)
SUB_MODULE_OF_2 = "Module2.SubModule1"
SUB_MODULE_OBJECT_2 = Module(name=SUB_MODULE_OF_2)
SUB_MODULE_OF_1 = "Module1.SubModule1"

MODULE_A = "E.A"  # submodule of E
MODULE_B = "E.A.B"  # submodule of A
MODULE_C = "C"
MODULE_D = "E.A.B.D"  # submodule of B
MODULE_E = "E"
MODULE_F = "E.F"  # submodule of E


@pytest.fixture(scope="module")
def evaluable() -> EvaluableArchitecture:
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


@pytest.fixture(scope="module")
def submodule_evaluable() -> EvaluableArchitecture:
    all_modules = [MODULE_A, MODULE_B, MODULE_C, MODULE_D, MODULE_E, MODULE_F]
    imports = [
        AbsoluteImport(MODULE_F, MODULE_C),
        AbsoluteImport(MODULE_C, MODULE_A),
        AbsoluteImport(MODULE_C, MODULE_B),
    ]

    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))


def test_a_depends_on_non_b(evaluable: EvaluableArchitecture) -> None:
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_1, MODULE_OBJECT_2
    )[MODULE_OBJECT_1]
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_1, MODULE_OBJECT_3
    )[MODULE_OBJECT_1]
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_1, MODULE_OBJECT_4
    )[MODULE_OBJECT_1]
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_1, SUB_MODULE_OBJECT_2
    )[MODULE_OBJECT_1]
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_1, MODULE_OBJECT_6
    )[MODULE_OBJECT_1]

    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_2, MODULE_OBJECT_1
    )[MODULE_OBJECT_2]
    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_2, MODULE_OBJECT_3
    )[MODULE_OBJECT_2]
    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_2, MODULE_OBJECT_4
    )[MODULE_OBJECT_2]
    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_2, SUB_MODULE_OBJECT_2
    )[MODULE_OBJECT_2]
    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_2, MODULE_OBJECT_6
    )[MODULE_OBJECT_2]

    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_3, MODULE_OBJECT_1
    )[MODULE_OBJECT_3]
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_3, MODULE_OBJECT_2
    )[MODULE_OBJECT_3]
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_3, MODULE_OBJECT_4
    )[MODULE_OBJECT_3]
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_3, SUB_MODULE_OBJECT_2
    )[MODULE_OBJECT_3]
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_3, MODULE_OBJECT_6
    )[MODULE_OBJECT_3]

    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_4, MODULE_OBJECT_1
    )[MODULE_OBJECT_4]
    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_4, MODULE_OBJECT_2
    )[MODULE_OBJECT_4]
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_4, MODULE_OBJECT_3
    )[MODULE_OBJECT_4]
    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_4, SUB_MODULE_OBJECT_2
    )[MODULE_OBJECT_4]
    assert evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_4, MODULE_OBJECT_6
    )[MODULE_OBJECT_4]

    assert not evaluable.any_dependencies_to_modules_other_than(
        SUB_MODULE_OBJECT_2, MODULE_OBJECT_1
    )[SUB_MODULE_OBJECT_2]
    assert not evaluable.any_dependencies_to_modules_other_than(
        SUB_MODULE_OBJECT_2, MODULE_OBJECT_2
    )[SUB_MODULE_OBJECT_2]
    assert not evaluable.any_dependencies_to_modules_other_than(
        SUB_MODULE_OBJECT_2, MODULE_OBJECT_3
    )[SUB_MODULE_OBJECT_2]
    assert not evaluable.any_dependencies_to_modules_other_than(
        SUB_MODULE_OBJECT_2, MODULE_OBJECT_4
    )[SUB_MODULE_OBJECT_2]
    assert not evaluable.any_dependencies_to_modules_other_than(
        SUB_MODULE_OBJECT_2, MODULE_OBJECT_6
    )[SUB_MODULE_OBJECT_2]

    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_6, MODULE_OBJECT_1
    )[MODULE_OBJECT_6]
    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_6, MODULE_OBJECT_2
    )[MODULE_OBJECT_6]
    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_6, MODULE_OBJECT_3
    )[MODULE_OBJECT_6]
    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_6, MODULE_OBJECT_4
    )[MODULE_OBJECT_6]
    assert not evaluable.any_dependencies_to_modules_other_than(
        MODULE_OBJECT_6, SUB_MODULE_OBJECT_2
    )[MODULE_OBJECT_6]


def test_non_a_depends_on_b(evaluable: EvaluableArchitecture) -> None:
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_1, MODULE_OBJECT_2
    )[MODULE_OBJECT_2]
    assert not evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_1, MODULE_OBJECT_3
    )[MODULE_OBJECT_3]
    assert not evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_1, MODULE_OBJECT_4
    )[MODULE_OBJECT_4]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_1, SUB_MODULE_OBJECT_2
    )[SUB_MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_1, MODULE_OBJECT_6
    )[MODULE_OBJECT_6]

    assert not evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_2, MODULE_OBJECT_1
    )[MODULE_OBJECT_1]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_2, MODULE_OBJECT_3
    )[MODULE_OBJECT_3]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_2, MODULE_OBJECT_4
    )[MODULE_OBJECT_4]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_2, SUB_MODULE_OBJECT_2
    )[SUB_MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_2, MODULE_OBJECT_6
    )[MODULE_OBJECT_6]

    assert not evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_3, MODULE_OBJECT_1
    )[MODULE_OBJECT_1]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_3, MODULE_OBJECT_2
    )[MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_3, MODULE_OBJECT_4
    )[MODULE_OBJECT_4]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_3, SUB_MODULE_OBJECT_2
    )[SUB_MODULE_OBJECT_2]
    assert not evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_3, MODULE_OBJECT_6
    )[MODULE_OBJECT_6]

    assert not evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_4, MODULE_OBJECT_1
    )[MODULE_OBJECT_1]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_4, MODULE_OBJECT_2
    )[MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_4, MODULE_OBJECT_3
    )[MODULE_OBJECT_3]
    assert not evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_4, SUB_MODULE_OBJECT_2
    )[SUB_MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_4, MODULE_OBJECT_6
    )[MODULE_OBJECT_6]

    assert not evaluable.any_other_dependencies_to_modules_than(
        SUB_MODULE_OBJECT_2, MODULE_OBJECT_1
    )[MODULE_OBJECT_1]
    assert evaluable.any_other_dependencies_to_modules_than(
        SUB_MODULE_OBJECT_2, MODULE_OBJECT_2
    )[MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_to_modules_than(
        SUB_MODULE_OBJECT_2, MODULE_OBJECT_3
    )[MODULE_OBJECT_3]
    assert evaluable.any_other_dependencies_to_modules_than(
        SUB_MODULE_OBJECT_2, MODULE_OBJECT_4
    )[MODULE_OBJECT_4]
    assert evaluable.any_other_dependencies_to_modules_than(
        SUB_MODULE_OBJECT_2, MODULE_OBJECT_6
    )[MODULE_OBJECT_6]

    assert not evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_6, MODULE_OBJECT_1
    )[MODULE_OBJECT_1]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_6, MODULE_OBJECT_2
    )[MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_6, MODULE_OBJECT_3
    )[MODULE_OBJECT_3]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_6, MODULE_OBJECT_4
    )[MODULE_OBJECT_4]
    assert evaluable.any_other_dependencies_to_modules_than(
        MODULE_OBJECT_6, SUB_MODULE_OBJECT_2
    )[SUB_MODULE_OBJECT_2]


def test_depends_on(evaluable: EvaluableArchitecture) -> None:
    assert evaluable.get_dependencies(MODULE_OBJECT_1, MODULE_OBJECT_2)[
        (MODULE_OBJECT_1, MODULE_OBJECT_2)
    ]
    assert evaluable.get_dependencies(MODULE_OBJECT_1, MODULE_OBJECT_3)[
        (MODULE_OBJECT_1, MODULE_OBJECT_3)
    ]
    assert evaluable.get_dependencies(MODULE_OBJECT_1, MODULE_OBJECT_4)[
        (MODULE_OBJECT_1, MODULE_OBJECT_4)
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_1, SUB_MODULE_OBJECT_2)[
        (MODULE_OBJECT_1, SUB_MODULE_OBJECT_2)
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_1, MODULE_OBJECT_6)[
        (MODULE_OBJECT_1, MODULE_OBJECT_6)
    ]

    assert not evaluable.get_dependencies(MODULE_OBJECT_2, MODULE_OBJECT_1)[
        (MODULE_OBJECT_2, MODULE_OBJECT_1)
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_2, MODULE_OBJECT_3)[
        MODULE_OBJECT_2, MODULE_OBJECT_3
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_2, MODULE_OBJECT_4)[
        MODULE_OBJECT_2, MODULE_OBJECT_4
    ]
    assert not evaluable.get_dependencies(
        MODULE_OBJECT_2, Module(name=SUB_MODULE_OF_2)
    )[MODULE_OBJECT_2, SUB_MODULE_OBJECT_2]
    assert not evaluable.get_dependencies(MODULE_OBJECT_2, MODULE_OBJECT_6)[
        (MODULE_OBJECT_2, MODULE_OBJECT_6)
    ]

    assert not evaluable.get_dependencies(MODULE_OBJECT_3, MODULE_OBJECT_1)[
        (MODULE_OBJECT_3, MODULE_OBJECT_1)
    ]
    assert evaluable.get_dependencies(MODULE_OBJECT_3, MODULE_OBJECT_2)[
        (MODULE_OBJECT_3, MODULE_OBJECT_2)
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_3, MODULE_OBJECT_4)[
        MODULE_OBJECT_3, MODULE_OBJECT_4
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_3, SUB_MODULE_OBJECT_2)[
        (MODULE_OBJECT_3, SUB_MODULE_OBJECT_2)
    ]
    assert evaluable.get_dependencies(MODULE_OBJECT_3, MODULE_OBJECT_6)[
        (MODULE_OBJECT_3, MODULE_OBJECT_6)
    ]

    assert not evaluable.get_dependencies(MODULE_OBJECT_4, MODULE_OBJECT_1)[
        (MODULE_OBJECT_4, MODULE_OBJECT_1)
    ]
    assert evaluable.get_dependencies(MODULE_OBJECT_4, MODULE_OBJECT_2)[
        MODULE_OBJECT_4, MODULE_OBJECT_2
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_4, MODULE_OBJECT_3)[
        MODULE_OBJECT_4, MODULE_OBJECT_3
    ]
    assert evaluable.get_dependencies(MODULE_OBJECT_4, SUB_MODULE_OBJECT_2)[
        (MODULE_OBJECT_4, SUB_MODULE_OBJECT_2)
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_4, MODULE_OBJECT_6)[
        (MODULE_OBJECT_4, MODULE_OBJECT_6)
    ]

    assert not evaluable.get_dependencies(SUB_MODULE_OBJECT_2, MODULE_OBJECT_1)[
        (SUB_MODULE_OBJECT_2, MODULE_OBJECT_1)
    ]
    assert not evaluable.get_dependencies(SUB_MODULE_OBJECT_2, MODULE_OBJECT_2)[
        (SUB_MODULE_OBJECT_2, MODULE_OBJECT_2)
    ]
    assert not evaluable.get_dependencies(SUB_MODULE_OBJECT_2, MODULE_OBJECT_3)[
        (SUB_MODULE_OBJECT_2, MODULE_OBJECT_3)
    ]
    assert not evaluable.get_dependencies(SUB_MODULE_OBJECT_2, MODULE_OBJECT_4)[
        (SUB_MODULE_OBJECT_2, MODULE_OBJECT_4)
    ]
    assert not evaluable.get_dependencies(SUB_MODULE_OBJECT_2, MODULE_OBJECT_6)[
        (SUB_MODULE_OBJECT_2, MODULE_OBJECT_6)
    ]

    assert not evaluable.get_dependencies(MODULE_OBJECT_6, MODULE_OBJECT_1)[
        (MODULE_OBJECT_6, MODULE_OBJECT_1)
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_6, MODULE_OBJECT_2)[
        (MODULE_OBJECT_6, MODULE_OBJECT_2)
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_6, MODULE_OBJECT_3)[
        (MODULE_OBJECT_6, MODULE_OBJECT_3)
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_6, MODULE_OBJECT_4)[
        (MODULE_OBJECT_6, MODULE_OBJECT_4)
    ]
    assert not evaluable.get_dependencies(MODULE_OBJECT_6, SUB_MODULE_OBJECT_2)[
        (MODULE_OBJECT_6, SUB_MODULE_OBJECT_2)
    ]


def test_submodule_calculation(submodule_evaluable: EvaluableArchitectureGraph) -> None:
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


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
    ],
)
def test_is_dependent_between_named_modules(imports: List[AbsoluteImport]) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert architecture.get_dependencies(module_1, module_2)[(module_1, module_2)]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_is_dependent_between_named_and_submodule_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert architecture.get_dependencies(module_1, module_2)[(module_1, module_2)]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_is_dependent_between_submodule_and_named_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert architecture.get_dependencies(module_1, module_2)[(module_1, module_2)]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_is_dependent_between_submodule_modules(imports: List[AbsoluteImport]) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert architecture.get_dependencies(module_1, module_2)[(module_1, module_2)]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_1)],
        [AbsoluteImport(SUB_MODULE_OF_2, SUB_MODULE_OF_2)],
    ],
)
def test_is_not_dependent_between_named_modules(imports: List[AbsoluteImport]) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert not architecture.get_dependencies(module_1, module_2)[(module_1, module_2)]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
    ],
)
def test_is_not_dependent_between_named_and_submodule_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert not architecture.get_dependencies(module_1, module_2)[(module_1, module_2)]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
    ],
)
def test_is_not_dependent_between_submodule_and_named_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert not architecture.get_dependencies(module_1, module_2)[(module_1, module_2)]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
    ],
)
def test_is_not_dependent_between_submodule_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert not architecture.get_dependencies(module_1, module_2)[(module_1, module_2)]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_3)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_3)],
    ],
)
def test_any_to_other_between_named_modules(imports: List[AbsoluteImport]) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert architecture.any_dependencies_to_modules_other_than(module_1, module_2)[
        module_1
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_3)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_3)],
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
    ],
)
def test_any_to_other_between_named_and_submodule_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert architecture.any_dependencies_to_modules_other_than(module_1, module_2)[
        module_1
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_3)],
    ],
)
def test_any_to_other_between_submodule_and_named_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert architecture.any_dependencies_to_modules_other_than(module_1, module_2)[
        module_1
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_3)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
    ],
)
def test_any_to_other_between_submodule_modules(imports: List[AbsoluteImport]) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert architecture.any_dependencies_to_modules_other_than(module_1, module_2)[
        module_1
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_not_any_to_other_between_named_modules(imports: List[AbsoluteImport]) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert not architecture.any_dependencies_to_modules_other_than(module_1, module_2)[
        module_1
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_not_any_to_other_between_named_and_submodule_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert not architecture.any_dependencies_to_modules_other_than(module_1, module_2)[
        module_1
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_3)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_not_any_to_other_between_submodule_and_named_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert not architecture.any_dependencies_to_modules_other_than(module_1, module_2)[
        module_1
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_3)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_not_any_to_other_between_submodule_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert not architecture.any_dependencies_to_modules_other_than(module_1, module_2)[
        module_1
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_3, MODULE_2)],
        [AbsoluteImport(MODULE_3, SUB_MODULE_OF_2)],
    ],
)
def test_other_to_module_than_between_named_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert architecture.any_other_dependencies_to_modules_than(module_1, module_2)[
        module_2
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_3, SUB_MODULE_OF_2)],
    ],
)
def test_other_to_module_than_between_named_and_submodule_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert architecture.any_other_dependencies_to_modules_than(module_1, module_2)[
        module_2
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(MODULE_3, MODULE_2)],
        [AbsoluteImport(MODULE_3, SUB_MODULE_OF_2)],
    ],
)
def test_other_to_module_than_between_submodule_and_named_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert architecture.any_other_dependencies_to_modules_than(module_1, module_2)[
        module_2
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(MODULE_3, SUB_MODULE_OF_2)],
    ],
)
def test_other_to_module_than_between_submodule_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert architecture.any_other_dependencies_to_modules_than(module_1, module_2)[
        module_2
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_not_other_to_module_than_between_named_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert not architecture.any_other_dependencies_to_modules_than(module_1, module_2)[
        module_2
    ]


@pytest.mark.parametrize(
    "imports",
    [
        # [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        # [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(MODULE_3, MODULE_2)],
    ],
)
def test_not_other_to_module_than_between_named_and_submodule_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(name=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert not architecture.any_other_dependencies_to_modules_than(module_1, module_2)[
        module_2
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_not_other_to_module_than_between_submodule_and_named_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(name=MODULE_2)
    assert not architecture.any_other_dependencies_to_modules_than(module_1, module_2)[
        module_2
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(MODULE_3, MODULE_2)],
    ],
)
def test_not_other_to_module_than_between_submodule_modules(
    imports: List[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_1 = Module(parent_module=MODULE_1)
    module_2 = Module(parent_module=MODULE_2)
    assert not architecture.any_other_dependencies_to_modules_than(module_1, module_2)[
        module_2
    ]