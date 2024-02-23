from __future__ import annotations

from typing import List

import pytest
from eval_structure.evaluable_graph.conftest import (
    MODULE_1,
    MODULE_2,
    MODULE_FILTER_OBJECT_1,
    MODULE_FILTER_OBJECT_2,
    MODULE_FILTER_OBJECT_3,
    MODULE_FILTER_OBJECT_4,
    MODULE_FILTER_OBJECT_6,
    MODULE_OBJECT_1,
    MODULE_OBJECT_2,
    MODULE_OBJECT_3,
    MODULE_OBJECT_4,
    MODULE_OBJECT_6,
    SUB_MODULE_FILTER_OBJECT_2,
    SUB_MODULE_OBJECT_2,
    SUB_MODULE_OF_1,
    SUB_MODULE_OF_2,
)

from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure.evaluable_architecture import (
    Module,
    ModuleGroup,
    ModuleNameFilter,
    ParentModuleNameFilter,
)
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport


def test_a_depends_on_non_b(evaluable: EvaluableArchitecture) -> None:
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_2]
    )[
        MODULE_OBJECT_1
    ]
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_3]
    )[
        MODULE_OBJECT_1
    ]
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_4]
    )[
        MODULE_OBJECT_1
    ]
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_1], [SUB_MODULE_FILTER_OBJECT_2]
    )[
        MODULE_OBJECT_1
    ]
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_6]
    )[
        MODULE_OBJECT_1
    ]

    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_1]
    )[
        MODULE_OBJECT_2
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_3]
    )[
        MODULE_OBJECT_2
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_4]
    )[
        MODULE_OBJECT_2
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_2], [SUB_MODULE_FILTER_OBJECT_2]
    )[
        MODULE_OBJECT_2
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_6]
    )[
        MODULE_OBJECT_2
    ]

    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_1]
    )[
        MODULE_OBJECT_3
    ]
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_2]
    )[
        MODULE_OBJECT_3
    ]
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_4]
    )[
        MODULE_OBJECT_3
    ]
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_3], [SUB_MODULE_FILTER_OBJECT_2]
    )[
        MODULE_OBJECT_3
    ]
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_6]
    )[
        MODULE_OBJECT_3
    ]

    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_1]
    )[
        MODULE_OBJECT_4
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_2]
    )[
        MODULE_OBJECT_4
    ]
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_3]
    )[
        MODULE_OBJECT_4
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_4], [SUB_MODULE_FILTER_OBJECT_2]
    )[
        MODULE_OBJECT_4
    ]
    assert evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_6]
    )[
        MODULE_OBJECT_4
    ]

    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_1]
    )[
        SUB_MODULE_OBJECT_2
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_2]
    )[
        SUB_MODULE_OBJECT_2
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_3]
    )[
        SUB_MODULE_OBJECT_2
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_4]
    )[
        SUB_MODULE_OBJECT_2
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_6]
    )[
        SUB_MODULE_OBJECT_2
    ]

    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_1]
    )[
        MODULE_OBJECT_6
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_2]
    )[
        MODULE_OBJECT_6
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_3]
    )[
        MODULE_OBJECT_6
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_4]
    )[
        MODULE_OBJECT_6
    ]
    assert not evaluable.any_dependencies_from_dependents_to_modules_other_than_dependent_upons(
        [MODULE_FILTER_OBJECT_6], [SUB_MODULE_FILTER_OBJECT_2]
    )[
        MODULE_OBJECT_6
    ]


def test_non_a_depends_on_b(evaluable: EvaluableArchitecture) -> None:
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_2]
    )[MODULE_OBJECT_2]
    assert not evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_3]
    )[MODULE_OBJECT_3]
    assert not evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_4]
    )[MODULE_OBJECT_4]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_1], [SUB_MODULE_FILTER_OBJECT_2]
    )[SUB_MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_6]
    )[MODULE_OBJECT_6]

    assert not evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_1]
    )[MODULE_OBJECT_1]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_3]
    )[MODULE_OBJECT_3]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_4]
    )[MODULE_OBJECT_4]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_2], [SUB_MODULE_FILTER_OBJECT_2]
    )[SUB_MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_6]
    )[MODULE_OBJECT_6]

    assert not evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_1]
    )[MODULE_OBJECT_1]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_2]
    )[MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_4]
    )[MODULE_OBJECT_4]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_3], [SUB_MODULE_FILTER_OBJECT_2]
    )[SUB_MODULE_OBJECT_2]
    assert not evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_6]
    )[MODULE_OBJECT_6]

    assert not evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_1]
    )[MODULE_OBJECT_1]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_2]
    )[MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_3]
    )[MODULE_OBJECT_3]
    assert not evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_4], [SUB_MODULE_FILTER_OBJECT_2]
    )[SUB_MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_6]
    )[MODULE_OBJECT_6]

    assert not evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_1]
    )[MODULE_OBJECT_1]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_2]
    )[MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_3]
    )[MODULE_OBJECT_3]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_4]
    )[MODULE_OBJECT_4]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_6]
    )[MODULE_OBJECT_6]

    assert not evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_1]
    )[MODULE_OBJECT_1]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_2]
    )[MODULE_OBJECT_2]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_3]
    )[MODULE_OBJECT_3]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_4]
    )[MODULE_OBJECT_4]
    assert evaluable.any_other_dependencies_on_dependent_upons_than_from_dependents(
        [MODULE_FILTER_OBJECT_6], [SUB_MODULE_FILTER_OBJECT_2]
    )[SUB_MODULE_OBJECT_2]


def test_depends_on(evaluable: EvaluableArchitecture) -> None:
    assert evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_2]
    )[(MODULE_OBJECT_1, MODULE_OBJECT_2)]
    assert evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_3]
    )[(MODULE_OBJECT_1, MODULE_OBJECT_3)]
    assert evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_4]
    )[(MODULE_OBJECT_1, MODULE_OBJECT_4)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_1], [SUB_MODULE_FILTER_OBJECT_2]
    )[(MODULE_OBJECT_1, SUB_MODULE_OBJECT_2)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_1], [MODULE_FILTER_OBJECT_6]
    )[(MODULE_OBJECT_1, MODULE_OBJECT_6)]

    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_1]
    )[(MODULE_OBJECT_2, MODULE_OBJECT_1)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_3]
    )[(MODULE_OBJECT_2, MODULE_OBJECT_3)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_4]
    )[(MODULE_OBJECT_2, MODULE_OBJECT_4)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_2], [ModuleNameFilter(name=SUB_MODULE_OF_2)]
    )[(MODULE_OBJECT_2, SUB_MODULE_OBJECT_2)]

    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_6]
    )[(MODULE_OBJECT_2, MODULE_OBJECT_6)]

    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_1]
    )[(MODULE_OBJECT_3, MODULE_OBJECT_1)]
    assert evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_2]
    )[(MODULE_OBJECT_3, MODULE_OBJECT_2)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_4]
    )[(MODULE_OBJECT_3, MODULE_OBJECT_4)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_3], [SUB_MODULE_FILTER_OBJECT_2]
    )[(MODULE_OBJECT_3, SUB_MODULE_OBJECT_2)]
    assert evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_3], [MODULE_FILTER_OBJECT_6]
    )[(MODULE_OBJECT_3, MODULE_OBJECT_6)]

    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_1]
    )[(MODULE_OBJECT_4, MODULE_OBJECT_1)]
    assert evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_2]
    )[(MODULE_OBJECT_4, MODULE_OBJECT_2)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_3]
    )[(MODULE_OBJECT_4, MODULE_OBJECT_3)]
    assert evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_4], [SUB_MODULE_FILTER_OBJECT_2]
    )[(MODULE_OBJECT_4, SUB_MODULE_OBJECT_2)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_4], [MODULE_FILTER_OBJECT_6]
    )[(MODULE_OBJECT_4, MODULE_OBJECT_6)]

    assert not evaluable.get_dependencies(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_1]
    )[(SUB_MODULE_OBJECT_2, MODULE_OBJECT_1)]
    assert not evaluable.get_dependencies(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_2]
    )[(SUB_MODULE_OBJECT_2, MODULE_OBJECT_2)]
    assert not evaluable.get_dependencies(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_3]
    )[(SUB_MODULE_OBJECT_2, MODULE_OBJECT_3)]
    assert not evaluable.get_dependencies(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_4]
    )[(SUB_MODULE_OBJECT_2, MODULE_OBJECT_4)]
    assert not evaluable.get_dependencies(
        [SUB_MODULE_FILTER_OBJECT_2], [MODULE_FILTER_OBJECT_6]
    )[(SUB_MODULE_OBJECT_2, MODULE_OBJECT_6)]

    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_1]
    )[(MODULE_OBJECT_6, MODULE_OBJECT_1)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_2]
    )[(MODULE_OBJECT_6, MODULE_OBJECT_2)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_3]
    )[(MODULE_OBJECT_6, MODULE_OBJECT_3)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_6], [MODULE_FILTER_OBJECT_4]
    )[(MODULE_OBJECT_6, MODULE_OBJECT_4)]
    assert not evaluable.get_dependencies(
        [MODULE_FILTER_OBJECT_6], [SUB_MODULE_FILTER_OBJECT_2]
    )[(MODULE_OBJECT_6, SUB_MODULE_OBJECT_2)]


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
    imports: List[AbsoluteImport],
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
    imports: List[AbsoluteImport],
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
def test_is_dependent_between_submodule_modules(imports: List[AbsoluteImport]) -> None:
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
def test_is_not_dependent_between_named_modules(imports: List[AbsoluteImport]) -> None:
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
    imports: List[AbsoluteImport],
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
    imports: List[AbsoluteImport],
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
    imports: List[AbsoluteImport],
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
