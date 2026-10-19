from __future__ import annotations

import pytest

from eval_structure.conftest import (
    MODULE_1,
    MODULE_2,
    MODULE_FILTER_OBJECT_1,
    MODULE_FILTER_OBJECT_2,
    MODULE_FILTER_OBJECT_3,
    MODULE_FILTER_OBJECT_4,
    MODULE_FILTER_OBJECT_6,
    SUB_MODULE_FILTER_OBJECT_2,
    SUB_MODULE_OF_1,
    SUB_MODULE_OF_2,
)
from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure.evaluable_architecture import (
    Module,
    ModuleFilter,
    ModuleGroup,
    ModuleNameFilter,
    ParentModuleNameFilter,
)
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure.utils import filter_to_module
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport

# Results of the three dependency queries for (source, target) pairs over the evaluable
# fixture graph (imports: 1 -> 2, 1 -> 3, 1 -> 4, 3 -> 2, 4 -> Module2.SubModule1,
# 3 -> 6), in the order:
# - whether the source imports a module other than the target,
# - whether the target is imported by a module other than the source,
# - whether the source directly imports the target.
dependency_expectations = [
    (MODULE_FILTER_OBJECT_1, MODULE_FILTER_OBJECT_2, True, True, True),
    (MODULE_FILTER_OBJECT_1, MODULE_FILTER_OBJECT_3, True, False, True),
    (MODULE_FILTER_OBJECT_1, MODULE_FILTER_OBJECT_4, True, False, True),
    (MODULE_FILTER_OBJECT_1, SUB_MODULE_FILTER_OBJECT_2, True, True, False),
    (MODULE_FILTER_OBJECT_1, MODULE_FILTER_OBJECT_6, True, True, False),
    (MODULE_FILTER_OBJECT_2, MODULE_FILTER_OBJECT_1, False, False, False),
    (MODULE_FILTER_OBJECT_2, MODULE_FILTER_OBJECT_3, False, True, False),
    (MODULE_FILTER_OBJECT_2, MODULE_FILTER_OBJECT_4, False, True, False),
    (MODULE_FILTER_OBJECT_2, SUB_MODULE_FILTER_OBJECT_2, False, True, False),
    (MODULE_FILTER_OBJECT_2, MODULE_FILTER_OBJECT_6, False, True, False),
    (MODULE_FILTER_OBJECT_3, MODULE_FILTER_OBJECT_1, True, False, False),
    (MODULE_FILTER_OBJECT_3, MODULE_FILTER_OBJECT_2, True, True, True),
    (MODULE_FILTER_OBJECT_3, MODULE_FILTER_OBJECT_4, True, True, False),
    (MODULE_FILTER_OBJECT_3, SUB_MODULE_FILTER_OBJECT_2, True, True, False),
    (MODULE_FILTER_OBJECT_3, MODULE_FILTER_OBJECT_6, True, False, True),
    (MODULE_FILTER_OBJECT_4, MODULE_FILTER_OBJECT_1, True, False, False),
    (MODULE_FILTER_OBJECT_4, MODULE_FILTER_OBJECT_2, False, True, True),
    (MODULE_FILTER_OBJECT_4, MODULE_FILTER_OBJECT_3, True, True, False),
    (MODULE_FILTER_OBJECT_4, SUB_MODULE_FILTER_OBJECT_2, False, False, True),
    (MODULE_FILTER_OBJECT_4, MODULE_FILTER_OBJECT_6, True, True, False),
    (SUB_MODULE_FILTER_OBJECT_2, MODULE_FILTER_OBJECT_1, False, False, False),
    (SUB_MODULE_FILTER_OBJECT_2, MODULE_FILTER_OBJECT_2, False, True, False),
    (SUB_MODULE_FILTER_OBJECT_2, MODULE_FILTER_OBJECT_3, False, True, False),
    (SUB_MODULE_FILTER_OBJECT_2, MODULE_FILTER_OBJECT_4, False, True, False),
    (SUB_MODULE_FILTER_OBJECT_2, MODULE_FILTER_OBJECT_6, False, True, False),
    (MODULE_FILTER_OBJECT_6, MODULE_FILTER_OBJECT_1, False, False, False),
    (MODULE_FILTER_OBJECT_6, MODULE_FILTER_OBJECT_2, False, True, False),
    (MODULE_FILTER_OBJECT_6, MODULE_FILTER_OBJECT_3, False, True, False),
    (MODULE_FILTER_OBJECT_6, MODULE_FILTER_OBJECT_4, False, True, False),
    (MODULE_FILTER_OBJECT_6, SUB_MODULE_FILTER_OBJECT_2, False, True, False),
]

dependency_expectation_ids = [
    f"{source.name} -> {target.name}" for source, target, *_ in dependency_expectations
]


@pytest.mark.parametrize(
    ["source", "target", "towards_other", "other_towards", "dependency"],
    dependency_expectations,
    ids=dependency_expectation_ids,
)
def test_dependencies_between_modules_as_expected(
    source: ModuleFilter,
    target: ModuleFilter,
    towards_other: bool,
    other_towards: bool,
    dependency: bool,
    evaluable: EvaluableArchitecture,
) -> None:
    assert (
        bool(
            evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
                [source], [target]
            )[filter_to_module(source)]
        )
        is towards_other
    )

    assert (
        bool(
            evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
                [source], [target]
            )[filter_to_module(target)]
        )
        is other_towards
    )

    assert (
        bool(
            evaluable.get_dependencies([source], [target])[
                (filter_to_module(source), filter_to_module(target))
            ]
        )
        is dependency
    )


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
    ],
)
def test_is_dependent_between_named_modules(imports: list[AbsoluteImport]) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ModuleNameFilter(name=MODULE_1)
    module_filter_2 = ModuleNameFilter(name=MODULE_2)

    module_1 = Module(identifier=MODULE_1)
    module_2 = Module(identifier=MODULE_2)

    assert architecture.get_dependencies([module_filter_1], [module_filter_2])[
        (module_1, module_2)
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_is_dependent_between_named_and_submodule_modules(
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ModuleNameFilter(name=MODULE_1)
    module_filter_2 = ParentModuleNameFilter(parent_module=MODULE_2)

    module_1 = Module(identifier=MODULE_1)
    module_2 = ModuleGroup(identifier=MODULE_2)

    assert architecture.get_dependencies([module_filter_1], [module_filter_2])[
        (module_1, module_2)
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_is_dependent_between_submodule_and_named_modules(
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ParentModuleNameFilter(parent_module=MODULE_1)
    module_filter_2 = ModuleNameFilter(name=MODULE_2)

    module_1 = ModuleGroup(identifier=MODULE_1)
    module_2 = Module(identifier=MODULE_2)

    assert architecture.get_dependencies([module_filter_1], [module_filter_2])[
        (module_1, module_2)
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(SUB_MODULE_OF_1, SUB_MODULE_OF_2)],
    ],
)
def test_is_dependent_between_submodule_modules(imports: list[AbsoluteImport]) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ParentModuleNameFilter(parent_module=MODULE_1)
    module_filter_2 = ParentModuleNameFilter(parent_module=MODULE_2)

    module_1 = ModuleGroup(identifier=MODULE_1)
    module_2 = ModuleGroup(identifier=MODULE_2)

    assert architecture.get_dependencies([module_filter_1], [module_filter_2])[
        (module_1, module_2)
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_1)],
        [AbsoluteImport(SUB_MODULE_OF_2, SUB_MODULE_OF_2)],
    ],
)
def test_is_not_dependent_between_named_modules(imports: list[AbsoluteImport]) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ModuleNameFilter(name=MODULE_1)
    module_filter_2 = ModuleNameFilter(name=MODULE_2)

    module_1 = Module(identifier=MODULE_1)
    module_2 = Module(identifier=MODULE_2)

    assert not architecture.get_dependencies([module_filter_1], [module_filter_2])[
        (module_1, module_2)
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
    ],
)
def test_is_not_dependent_between_named_and_submodule_modules(
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ModuleNameFilter(name=MODULE_1)
    module_filter_2 = ParentModuleNameFilter(parent_module=MODULE_2)

    module_1 = Module(identifier=MODULE_1)
    module_2 = ModuleGroup(identifier=MODULE_2)
    assert not architecture.get_dependencies([module_filter_1], [module_filter_2])[
        (module_1, module_2)
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
    ],
)
def test_is_not_dependent_between_submodule_and_named_modules(
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ParentModuleNameFilter(parent_module=MODULE_1)
    module_filter_2 = ModuleNameFilter(name=MODULE_2)

    module_1 = ModuleGroup(identifier=MODULE_1)
    module_2 = Module(identifier=MODULE_2)

    assert not architecture.get_dependencies([module_filter_1], [module_filter_2])[
        (module_1, module_2)
    ]


@pytest.mark.parametrize(
    "imports",
    [
        [AbsoluteImport(MODULE_1, MODULE_2)],
        [AbsoluteImport(MODULE_1, SUB_MODULE_OF_2)],
        [AbsoluteImport(SUB_MODULE_OF_1, MODULE_2)],
    ],
)
def test_is_not_dependent_between_submodule_modules(
    imports: list[AbsoluteImport],
) -> None:
    all_modules = [MODULE_1, MODULE_2, SUB_MODULE_OF_1, SUB_MODULE_OF_2]
    architecture = EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports))

    module_filter_1 = ParentModuleNameFilter(parent_module=MODULE_1)
    module_filter_2 = ParentModuleNameFilter(parent_module=MODULE_2)

    module_1 = ModuleGroup(identifier=MODULE_1)
    module_2 = ModuleGroup(identifier=MODULE_2)

    assert not architecture.get_dependencies([module_filter_1], [module_filter_2])[
        (module_1, module_2)
    ]
