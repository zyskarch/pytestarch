from __future__ import annotations

from typing import List

import pytest
from eval_structure.evaluable_graph.conftest import (
    MODULE_1,
    MODULE_2,
    MODULE_3,
    SUB_MODULE_OF_1,
    SUB_MODULE_OF_2,
)

from pytestarch.eval_structure.evaluable_architecture import Module
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport


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
    assert architecture.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [module_1], [module_2]
    )[
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
    assert architecture.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [module_1], [module_2]
    )[
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
    assert architecture.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [module_1], [module_2]
    )[
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
    assert architecture.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [module_1], [module_2]
    )[
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
    assert not architecture.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [module_1], [module_2]
    )[
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
    assert not architecture.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [module_1], [module_2]
    )[
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
    assert not architecture.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [module_1], [module_2]
    )[
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
    assert not architecture.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [module_1], [module_2]
    )[
        module_1
    ]
