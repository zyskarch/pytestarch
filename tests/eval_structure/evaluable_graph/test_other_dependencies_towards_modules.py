from __future__ import annotations

import pytest
from eval_structure.evaluable_graph.conftest import (
    MODULE_1,
    MODULE_2,
    MODULE_3,
    SUB_MODULE_OF_1,
    SUB_MODULE_OF_2,
)

from pytestarch.eval_structure.evaluable_architecture import (
    Module,
    ModuleGroup,
    ModuleNameFilter,
    ParentModuleNameFilter,
)
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_3, MODULE_2)],
        [AbsoluteImport(MODULE_3, SUB_MODULE_OF_2)],
    ],
)
def test_other_to_module_than_between_named_modules(
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ModuleNameFilter(name=MODULE_1)
    module_filter_2 = ModuleNameFilter(name=MODULE_2)

    module_2 = Module(identifier=MODULE_2)

    assert architecture.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [module_filter_1], [module_filter_2]
    )[module_2]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_3, SUB_MODULE_OF_2)],
    ],
)
def test_other_to_module_than_between_named_and_submodule_modules(
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ModuleNameFilter(name=MODULE_1)
    module_filter_2 = ParentModuleNameFilter(parent_module=MODULE_2)

    module_2 = ModuleGroup(identifier=MODULE_2)

    assert architecture.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [module_filter_1], [module_filter_2]
    )[module_2]


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
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ParentModuleNameFilter(parent_module=MODULE_1)
    module_filter_2 = ModuleNameFilter(name=MODULE_2)

    module_2 = Module(identifier=MODULE_2)

    assert architecture.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [module_filter_1], [module_filter_2]
    )[module_2]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(MODULE_3, SUB_MODULE_OF_2)],
    ],
)
def test_other_to_module_than_between_submodule_modules(
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ParentModuleNameFilter(parent_module=MODULE_1)
    module_filter_2 = ParentModuleNameFilter(parent_module=MODULE_2)

    module_2 = ModuleGroup(identifier=MODULE_2)

    assert architecture.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [module_filter_1], [module_filter_2]
    )[module_2]


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
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ModuleNameFilter(name=MODULE_1)
    module_filter_2 = ModuleNameFilter(name=MODULE_2)

    module_2 = Module(identifier=MODULE_2)

    assert (
        not architecture.any_other_dependencies_on_dependent_upons_than_from_dependents(
            [module_filter_1], [module_filter_2]
        )[module_2]
    )


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(MODULE_3, MODULE_2)],
    ],
)
def test_not_other_to_module_than_between_named_and_submodule_modules(
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ModuleNameFilter(name=MODULE_1)
    module_filter_2 = ParentModuleNameFilter(parent_module=MODULE_2)

    module_2 = ModuleGroup(identifier=MODULE_2)

    assert (
        not architecture.any_other_dependencies_on_dependent_upons_than_from_dependents(
            [module_filter_1], [module_filter_2]
        )[module_2]
    )


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_not_other_to_module_than_between_submodule_and_named_modules(
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ParentModuleNameFilter(parent_module=MODULE_1)
    module_filter_2 = ModuleNameFilter(name=MODULE_2)

    module_2 = Module(identifier=MODULE_2)

    assert (
        not architecture.any_other_dependencies_on_dependent_upons_than_from_dependents(
            [module_filter_1], [module_filter_2]
        )[module_2]
    )


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
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2, MODULE_3]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ParentModuleNameFilter(parent_module=MODULE_1)
    module_filter_2 = ParentModuleNameFilter(parent_module=MODULE_2)

    module_2 = ModuleGroup(identifier=MODULE_2)

    assert (
        not architecture.any_other_dependencies_on_dependent_upons_than_from_dependents(
            [module_filter_1], [module_filter_2]
        )[module_2]
    )
