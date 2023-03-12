from __future__ import annotations

from dataclasses import fields
from typing import List

import pytest

from pytestarch import Rule
from pytestarch.eval_structure.evaluable_architecture import Module, StrictDependency
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph
from pytestarch.eval_structure_generation.file_import.import_types import AbsoluteImport

MODULE_1 = "1"
MODULE_2 = "2"
MODULE_3 = "3"
MODULE_4 = "4"

ALL_MODULES = [MODULE_1, MODULE_2, MODULE_3, MODULE_4]


multiple_violations_test_cases = [
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_2),
            AbsoluteImport(MODULE_1, MODULE_3),
            AbsoluteImport(MODULE_1, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should()
        .import_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should import -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should()
        .import_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_violations"],
        [
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should import -- false",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_1),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should()
        .be_imported_by_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should be imported -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_4, MODULE_1),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should()
        .import_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_violations"],
        [
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should be imported -- false",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_2),
            AbsoluteImport(MODULE_1, MODULE_3),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .import_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should only import -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_2),
            AbsoluteImport(MODULE_1, MODULE_3),
            AbsoluteImport(MODULE_1, MODULE_4),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .import_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_only_violations_by_forbidden_import"],
        [
            [(Module(name=MODULE_1), Module(name=MODULE_4))],
        ],
        id="should only import -- false forbidden",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .import_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_only_violations_by_no_import"],
        [
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should only import -- false no import",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_4),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .import_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [
            "should_only_violations_by_forbidden_import",
            "should_only_violations_by_no_import",
        ],
        [
            [(Module(name=MODULE_1), Module(name=MODULE_4))],
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should only import -- false forbidden and no import",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_3, MODULE_1),
            AbsoluteImport(MODULE_2, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .be_imported_by_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should only be imported -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_1),
            AbsoluteImport(MODULE_4, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .be_imported_by_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_only_violations_by_forbidden_import"],
        [
            [(Module(name=MODULE_1), Module(name=MODULE_4))],
        ],
        id="should only be imported -- false forbidden",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .be_imported_by_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_only_violations_by_no_import"],
        [
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should only be imported -- false no import",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_4, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .be_imported_by_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [
            "should_only_violations_by_forbidden_import",
            "should_only_violations_by_no_import",
        ],
        [
            [(Module(name=MODULE_1), Module(name=MODULE_4))],
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should only be imported  -- false forbidden and no import",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_not()
        .import_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should not import -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_2),
            AbsoluteImport(MODULE_1, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_not()
        .import_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_not_violations"],
        [
            [(Module(name=MODULE_1), Module(name=MODULE_2))],
        ],
        id="should not import -- false",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_4, MODULE_1),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_not()
        .be_imported_by_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should not be imported -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, MODULE_1),
            AbsoluteImport(MODULE_4, MODULE_1),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_not()
        .be_imported_by_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_not_violations"],
        [[(Module(name=MODULE_1), Module(name=MODULE_2))]],
        id="should not be imported -- false",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_2),
            AbsoluteImport(MODULE_1, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should()
        .import_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should import except -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_2),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should()
        .import_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_except_violations"],
        [
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should import except -- false",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, MODULE_1),
            AbsoluteImport(MODULE_4, MODULE_1),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should be imported except -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, MODULE_1),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_except_violations"],
        [
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should be imported except -- false",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_4),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should only import except -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_2),
            AbsoluteImport(MODULE_1, MODULE_4),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_only_except_violations_by_forbidden_import"],
        [
            [(Module(name=MODULE_1), Module(name=MODULE_2))],
        ],
        id="should only import except -- false forbidden",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_only_except_violations_by_no_import"],
        [
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should only import except -- false no import",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_1, MODULE_2),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [
            "should_only_except_violations_by_forbidden_import",
            "should_only_except_violations_by_no_import",
        ],
        [
            [(Module(name=MODULE_1), Module(name=MODULE_2))],
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should only import except  -- false forbidden and no import",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_4, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should only be imported except -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, MODULE_1),
            AbsoluteImport(MODULE_4, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_only_except_violations_by_forbidden_import"],
        [
            [(Module(name=MODULE_1), Module(name=MODULE_2))],
        ],
        id="should only be imported except -- false forbidden",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_only_except_violations_by_no_import"],
        [
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should only be imported except -- false no import",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [
            "should_only_except_violations_by_forbidden_import",
            "should_only_except_violations_by_no_import",
        ],
        [
            [(Module(name=MODULE_1), Module(name=MODULE_2))],
            [
                (Module(name=MODULE_1), Module(name=MODULE_2)),
                (Module(name=MODULE_1), Module(name=MODULE_3)),
            ],
        ],
        id="should only be imported except  -- false forbidden and no import",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        [],
        [],
        id="should not be imported except -- true",
    ),
    pytest.param(
        [
            AbsoluteImport(MODULE_2, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_1),
            AbsoluteImport(MODULE_4, MODULE_1),
            AbsoluteImport(MODULE_3, MODULE_4),
        ],
        Rule()
        .modules_that()
        .are_named(MODULE_1)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named([MODULE_2, MODULE_3]),
        ["should_not_except_violations"],
        [[(Module(name=MODULE_1), Module(name=MODULE_4))]],
        id="should not be imported except -- false",
    ),
]


@pytest.mark.parametrize(
    "imports, rule, expected_violations, expected_violating_dependencies",
    multiple_violations_test_cases,
)
def test_multiple_violations_due_to_multiple_rule_objects(
    imports: List[AbsoluteImport],
    rule: Rule,
    expected_violations: List[str],
    expected_violating_dependencies: List[StrictDependency],
) -> None:
    evaluable = EvaluableArchitectureGraph(NetworkxGraph(ALL_MODULES, imports))
    matcher = rule._prepare_rule_matcher()
    violations = matcher._find_rule_violations(evaluable)

    field_names = [field.name for field in fields(violations)]

    for flag in field_names:
        violated = getattr(violations, flag)
        if flag in expected_violations:
            index = expected_violations.index(flag)
            assert violated == expected_violating_dependencies[index]
        else:
            assert not violated
