from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from pytestarch.eval_structure.evaluable_architecture import (
    Dependency,
    ExplicitlyRequestedDependenciesByBaseModules,
    LayerMapping,
    Module,
    ModuleNameFilter,
    NotExplicitlyRequestedDependenciesByBaseModule,
)
from pytestarch.rule_assessment.rule_check.layer_rule_violation_detector import (
    LayerRuleViolationDetector,
)
from rule_assessment.test_rule_violation_detector import (
    BEHAVIOR_EXCEPTION,
    IMPORTEES,
    IMPORTERS,
    SHOULD,
    SHOULD_EXCEPT_VIOLATIONS,
    SHOULD_NOT,
    SHOULD_NOT_EXCEPT_VIOLATIONS,
    SHOULD_NOT_VIOLATIONS,
    SHOULD_ONLY,
    SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
    SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
    SHOULD_ONLY_VIOLATIONS_FORBIDDEN_IMPORT,
    SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
    SHOULD_VIOLATIONS,
    get_behavior_requirement,
    get_module_requirement,
)

# layer 1
MODULE_NAME_1 = "M1"
MODULE_NAME_2 = "M2"
MODULE_NAME_3 = "M3"

# layer 2
MODULE_NAME_4 = "M4"
MODULE_NAME_5 = "M5"
MODULE_NAME_6 = "M6"

# layer 3
MODULE_NAME_7 = "M7"

# layer 4
MODULE_NAME_8 = "M8"
MODULE_NAME_9 = "M9"

# layer 5
MODULE_NAME_10 = "M10"

MODULE_FILTER_1 = ModuleNameFilter(MODULE_NAME_1)
MODULE_FILTER_2 = ModuleNameFilter(MODULE_NAME_2)
MODULE_FILTER_3 = ModuleNameFilter(MODULE_NAME_3)

MODULE_FILTER_4 = ModuleNameFilter(MODULE_NAME_4)
MODULE_FILTER_5 = ModuleNameFilter(MODULE_NAME_5)
MODULE_FILTER_6 = ModuleNameFilter(MODULE_NAME_6)

MODULE_FILTER_7 = ModuleNameFilter(MODULE_NAME_7)

MODULE_FILTER_8 = ModuleNameFilter(MODULE_NAME_8)
MODULE_FILTER_9 = ModuleNameFilter(MODULE_NAME_9)


MODULE_1 = Module(MODULE_NAME_1)
MODULE_2 = Module(MODULE_NAME_2)
MODULE_3 = Module(MODULE_NAME_3)
MODULE_4 = Module(MODULE_NAME_4)
MODULE_5 = Module(MODULE_NAME_5)
MODULE_6 = Module(MODULE_NAME_6)
MODULE_7 = Module(MODULE_NAME_7)
MODULE_8 = Module(MODULE_NAME_8)
MODULE_9 = Module(MODULE_NAME_9)


LAYER_1 = "L1"
LAYER_2 = "L2"
LAYER_3 = "L3"
LAYER_4 = "L4"

LAYER_MAPPING = LayerMapping(
    {
        LAYER_1: [MODULE_FILTER_1, MODULE_FILTER_2, MODULE_FILTER_3],
        LAYER_2: [MODULE_FILTER_4, MODULE_FILTER_5, MODULE_FILTER_6],
        LAYER_3: [MODULE_FILTER_7],
        LAYER_4: [MODULE_FILTER_8, MODULE_FILTER_9],
    }
)


@dataclass
class RuleViolationDetectorTestCase:
    behavior: dict[str, Any]
    expected_violation: str | None
    expected_violating_dependencies: list[Dependency]
    explicitly_requested_dependencies: (
        ExplicitlyRequestedDependenciesByBaseModules | None
    )
    not_explicitly_requested_dependencies: (
        NotExplicitlyRequestedDependenciesByBaseModule | None
    )
    multiple_rule_objects: bool = False


def _get_no_explicitly_requested_dependencies(
    multiple_rule_objects: bool = False,
) -> ExplicitlyRequestedDependenciesByBaseModules:
    result: dict[tuple[Module, Module], list] = {
        (MODULE_1, MODULE_4): [],
        (MODULE_1, MODULE_5): [],
        (MODULE_1, MODULE_6): [],
        (MODULE_2, MODULE_4): [],
        (MODULE_2, MODULE_5): [],
        (MODULE_2, MODULE_6): [],
        (MODULE_3, MODULE_4): [],
        (MODULE_3, MODULE_5): [],
        (MODULE_3, MODULE_6): [],
    }

    if multiple_rule_objects:
        result.update(
            {
                (MODULE_1, MODULE_8): [],
                (MODULE_1, MODULE_9): [],
                (MODULE_2, MODULE_8): [],
                (MODULE_2, MODULE_9): [],
                (MODULE_3, MODULE_8): [],
                (MODULE_3, MODULE_9): [],
            }
        )

    return result


def _get_explicitly_requested_dependencies(
    dependencies: list[Dependency], multiple_rule_objects: bool = False
) -> ExplicitlyRequestedDependenciesByBaseModules:
    no_dependencies = _get_no_explicitly_requested_dependencies(multiple_rule_objects)

    for dependency in dependencies:
        no_dependencies[dependency] = [dependency]

    return no_dependencies


def _get_all_violating_dependencies(
    objects: tuple[str, ...] = (LAYER_2,),
) -> list[Dependency]:
    return [
        (Module(identifier=single_subject.name), Module(identifier=single_object.name))  # type: ignore
        for o in objects
        for single_subject in LAYER_MAPPING.get_module_filters(LAYER_1)
        for single_object in LAYER_MAPPING.get_module_filters(o)
    ]


def _get_no_not_explicitly_requested_dependencies() -> (
    NotExplicitlyRequestedDependenciesByBaseModule
):
    return {MODULE_1: [], MODULE_2: [], MODULE_3: []}


def _get_not_explicitly_requested_dependencies(
    dependencies: list[Dependency],
) -> NotExplicitlyRequestedDependenciesByBaseModule:
    no_dependencies = _get_no_not_explicitly_requested_dependencies()

    for dependency in dependencies:
        no_dependencies[dependency[0]] = [dependency]

    return no_dependencies


test_cases = [
    # single rule subject single rule object
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            [],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_5)]),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_fulfilled_one_import_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            [],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_5), (MODULE_2, MODULE_6)]
            ),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_fulfilled_multiple_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            _get_all_violating_dependencies(),
            _get_no_explicitly_requested_dependencies(),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_violated_no_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            _get_all_violating_dependencies(),
            _get_no_explicitly_requested_dependencies(),
            _get_not_explicitly_requested_dependencies([(MODULE_1, MODULE_7)]),
        ),
        id="should_violated_import_of_other_layer_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True}, SHOULD_NOT_VIOLATIONS, [], {}, {}
        ),
        id="should_not_fulfilled_no_import_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True},
            SHOULD_NOT_VIOLATIONS,
            [],
            {},
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_7)]),
        ),
        id="should_not_fulfilled_import_of_other_layer_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True},
            SHOULD_NOT_VIOLATIONS,
            [(MODULE_1, MODULE_6)],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_6)]),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_not_violated_one_import_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True},
            SHOULD_NOT_VIOLATIONS,
            [(MODULE_1, MODULE_6), (MODULE_2, MODULE_5), (MODULE_3, MODULE_6)],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_6), (MODULE_2, MODULE_5), (MODULE_3, MODULE_6)]
            ),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_not_violated_multiple_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
            [],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_4)]),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_only_fulfilled_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
            [],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_4), (MODULE_1, MODULE_5)]
            ),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_only_fulfilled_multiple_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_FORBIDDEN_IMPORT,
            [],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_4)]),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_only_fulfilled_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_FORBIDDEN_IMPORT,
            [],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_4), (MODULE_1, MODULE_5)]
            ),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_only_fulfilled_multiple_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
            _get_all_violating_dependencies(),
            _get_no_explicitly_requested_dependencies(),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_only_violated_no_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_FORBIDDEN_IMPORT,
            [(MODULE_3, MODULE_7)],
            _get_explicitly_requested_dependencies([(MODULE_3, MODULE_4)]),
            _get_not_explicitly_requested_dependencies([(MODULE_3, MODULE_7)]),
        ),
        id="should_only_violated_one_forbidden_import_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_FORBIDDEN_IMPORT,
            [(MODULE_1, MODULE_7), (MODULE_3, MODULE_7)],
            _get_explicitly_requested_dependencies([(MODULE_3, MODULE_4)]),
            _get_not_explicitly_requested_dependencies(
                [(MODULE_3, MODULE_7), (MODULE_1, MODULE_7)]
            ),
        ),
        id="should_only_violated_multiple_forbidden_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            [],
            _get_no_explicitly_requested_dependencies(),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_5)]),
        ),
        id="should_except_fulfilled_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            [],
            _get_no_explicitly_requested_dependencies(),
            _get_not_explicitly_requested_dependencies(
                [(MODULE_2, MODULE_5), (MODULE_3, MODULE_4)]
            ),
        ),
        id="should_except_fulfilled_multiple_other_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            [],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_4)]),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_5)]),
        ),
        id="should_except_fulfilled_import_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            _get_all_violating_dependencies(),
            _get_no_explicitly_requested_dependencies(),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_except_violated_no_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            _get_all_violating_dependencies(),
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_6)]),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_except_violated_no_other_import_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            [],
            _get_no_explicitly_requested_dependencies(),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_not_except_fulfilled_no_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            [],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_6)]),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_not_except_fulfilled_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            [(MODULE_2, MODULE_7)],
            _get_no_explicitly_requested_dependencies(),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_7)]),
        ),
        id="should_not_except_violated_no_allowed_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            [(MODULE_2, MODULE_7)],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_5)]),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_7)]),
        ),
        id="should_not_except_violated_allowed_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
            [],
            _get_no_explicitly_requested_dependencies(),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_7)]),
        ),
        id="should_only_except_fulfilled_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
            [],
            _get_no_explicitly_requested_dependencies(),
            _get_not_explicitly_requested_dependencies(
                [(MODULE_2, MODULE_7), (MODULE_3, MODULE_7)]
            ),
        ),
        id="should_only_except_fulfilled_multiple_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
            [],
            _get_no_explicitly_requested_dependencies(),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_7)]),
        ),
        id="should_only_except_fulfilled_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
            [],
            _get_no_explicitly_requested_dependencies(),
            _get_not_explicitly_requested_dependencies(
                [(MODULE_2, MODULE_7), (MODULE_3, MODULE_7)]
            ),
        ),
        id="should_only_except_fulfilled_multiple_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
            _get_all_violating_dependencies(),
            _get_no_explicitly_requested_dependencies(),
            _get_no_not_explicitly_requested_dependencies(),
        ),
        id="should_only_except_violated_no_imports_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
            [(MODULE_1, MODULE_4)],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_4)]),
            _get_not_explicitly_requested_dependencies([(MODULE_1, MODULE_7)]),
        ),
        id="should_only_except_violated_one_forbidden_import_ssso",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
            [(MODULE_1, MODULE_4), (MODULE_1, MODULE_6)],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_4), (MODULE_1, MODULE_6)]
            ),
            _get_not_explicitly_requested_dependencies([(MODULE_1, MODULE_7)]),
        ),
        id="should_only_except_violated_multiple_forbidden_imports_ssso",
    ),
    # single rule subject multiple rule objects
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            [],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_5), (MODULE_1, MODULE_8)], True
            ),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_fulfilled_one_import_each_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            [],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_5), (MODULE_2, MODULE_6), (MODULE_1, MODULE_8)], True
            ),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_fulfilled_multiple_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            _get_all_violating_dependencies(objects=(LAYER_2, LAYER_4)),
            _get_no_explicitly_requested_dependencies(True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_violated_no_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            _get_all_violating_dependencies(objects=(LAYER_4,)),
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_5)], True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_violated_only_one_rule_object_import_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            _get_all_violating_dependencies(objects=(LAYER_2, LAYER_4)),
            _get_no_explicitly_requested_dependencies(True),
            _get_not_explicitly_requested_dependencies([(MODULE_1, MODULE_7)]),
            True,
        ),
        id="should_violated_import_of_other_layer_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True}, SHOULD_NOT_VIOLATIONS, [], {}, {}
        ),
        id="should_not_fulfilled_no_import_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True},
            SHOULD_NOT_VIOLATIONS,
            [],
            {},
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_7)]),
            True,
        ),
        id="should_not_fulfilled_import_of_other_layer_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True},
            SHOULD_NOT_VIOLATIONS,
            [(MODULE_1, MODULE_6)],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_6)], True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_not_violated_one_import_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True},
            SHOULD_NOT_VIOLATIONS,
            [(MODULE_1, MODULE_6), (MODULE_3, MODULE_9)],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_6), (MODULE_3, MODULE_9)], True
            ),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_not_violated_one_import_each_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True},
            SHOULD_NOT_VIOLATIONS,
            [(MODULE_1, MODULE_6), (MODULE_2, MODULE_5), (MODULE_3, MODULE_6)],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_6), (MODULE_2, MODULE_5), (MODULE_3, MODULE_6)], True
            ),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_not_violated_multiple_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True},
            SHOULD_NOT_VIOLATIONS,
            [
                (MODULE_1, MODULE_6),
                (MODULE_2, MODULE_5),
                (MODULE_3, MODULE_6),
                (MODULE_2, MODULE_8),
            ],
            _get_explicitly_requested_dependencies(
                [
                    (MODULE_1, MODULE_6),
                    (MODULE_2, MODULE_5),
                    (MODULE_3, MODULE_6),
                    (MODULE_2, MODULE_8),
                ],
                True,
            ),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_not_violated_multiple_imports_each_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
            [],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_4), (MODULE_2, MODULE_9)], True
            ),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_only_fulfilled_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
            [],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_4), (MODULE_1, MODULE_5), (MODULE_1, MODULE_8)], True
            ),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_only_fulfilled_multiple_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
            _get_all_violating_dependencies(objects=(LAYER_2, LAYER_4)),
            _get_no_explicitly_requested_dependencies(True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_only_violated_no_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
            _get_all_violating_dependencies(objects=(LAYER_4,)),
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_4)], True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_only_violated_no_imports_of_one_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_FORBIDDEN_IMPORT,
            [(MODULE_3, MODULE_7)],
            _get_explicitly_requested_dependencies(
                [(MODULE_3, MODULE_4), (MODULE_3, MODULE_9)], True
            ),
            _get_not_explicitly_requested_dependencies([(MODULE_3, MODULE_7)]),
            True,
        ),
        id="should_only_violated_one_forbidden_import_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_FORBIDDEN_IMPORT,
            [(MODULE_1, MODULE_7), (MODULE_3, MODULE_7)],
            _get_explicitly_requested_dependencies(
                [(MODULE_3, MODULE_4), (MODULE_3, MODULE_8)], True
            ),
            _get_not_explicitly_requested_dependencies(
                [(MODULE_3, MODULE_7), (MODULE_1, MODULE_7)]
            ),
            True,
        ),
        id="should_only_violated_multiple_forbidden_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            [],
            _get_no_explicitly_requested_dependencies(True),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_5)]),
            True,
        ),
        id="should_except_fulfilled_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            [],
            _get_no_explicitly_requested_dependencies(True),
            _get_not_explicitly_requested_dependencies(
                [(MODULE_2, MODULE_5), (MODULE_3, MODULE_4), (MODULE_3, MODULE_9)]
            ),
            True,
        ),
        id="should_except_fulfilled_multiple_other_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            [],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_4)], True),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_5)]),
            True,
        ),
        id="should_except_fulfilled_import_one_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            [],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_4), (MODULE_1, MODULE_8)], True
            ),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_5)]),
            True,
        ),
        id="should_except_fulfilled_import_both_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            _get_all_violating_dependencies(objects=(LAYER_2, LAYER_4)),
            _get_no_explicitly_requested_dependencies(True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_except_violated_no_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            _get_all_violating_dependencies(objects=(LAYER_2, LAYER_4)),
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_9)], True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_except_violated_import_of_only_one_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            _get_all_violating_dependencies(objects=(LAYER_2, LAYER_4)),
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_6)], True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_except_violated_no_other_import_one_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            _get_all_violating_dependencies(objects=(LAYER_2, LAYER_4)),
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_6), (MODULE_1, MODULE_9)], True
            ),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_except_violated_no_other_import_both_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            [],
            _get_no_explicitly_requested_dependencies(True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_not_except_fulfilled_no_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            [],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_6)], True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_not_except_fulfilled_one_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            [],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_6), (MODULE_2, MODULE_8)], True
            ),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_not_except_fulfilled_both_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            [(MODULE_2, MODULE_7)],
            _get_no_explicitly_requested_dependencies(True),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_7)]),
            True,
        ),
        id="should_not_except_violated_no_allowed_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            [(MODULE_2, MODULE_7)],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_5)], True),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_7)]),
            True,
        ),
        id="should_not_except_violated_one_imported_allowed_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            [(MODULE_2, MODULE_7)],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_5), (MODULE_2, MODULE_8)], True
            ),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_7)]),
            True,
        ),
        id="should_not_except_violated_both_imported_allowed_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
            [],
            _get_no_explicitly_requested_dependencies(True),
            _get_not_explicitly_requested_dependencies([(MODULE_2, MODULE_7)]),
            True,
        ),
        id="should_only_except_fulfilled_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
            [],
            _get_no_explicitly_requested_dependencies(True),
            _get_not_explicitly_requested_dependencies(
                [(MODULE_2, MODULE_7), (MODULE_3, MODULE_7)]
            ),
            True,
        ),
        id="should_only_except_fulfilled_multiple_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
            _get_all_violating_dependencies(objects=(LAYER_2, LAYER_4)),
            _get_no_explicitly_requested_dependencies(True),
            _get_no_not_explicitly_requested_dependencies(),
            True,
        ),
        id="should_only_except_violated_no_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
            [(MODULE_1, MODULE_4)],
            _get_explicitly_requested_dependencies([(MODULE_1, MODULE_4)], True),
            _get_not_explicitly_requested_dependencies([(MODULE_1, MODULE_7)]),
            True,
        ),
        id="should_only_except_violated_one_forbidden_import_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
            [(MODULE_1, MODULE_4), (MODULE_1, MODULE_6)],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_4), (MODULE_1, MODULE_6)], True
            ),
            _get_not_explicitly_requested_dependencies([(MODULE_1, MODULE_7)]),
            True,
        ),
        id="should_only_except_violated_multiple_forbidden_imports_ssmo",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
            [(MODULE_1, MODULE_4), (MODULE_1, MODULE_8)],
            _get_explicitly_requested_dependencies(
                [(MODULE_1, MODULE_4), (MODULE_1, MODULE_8)], True
            ),
            _get_not_explicitly_requested_dependencies([(MODULE_1, MODULE_7)]),
            True,
        ),
        id="should_only_except_violated_multiple_forbidden_imports_in_both_objects_ssmo",
    ),
]


@pytest.mark.parametrize("test_case", test_cases)
def test_rule_violation_detection_as_expected(
    test_case: RuleViolationDetectorTestCase,
) -> None:
    behavior_requirement = get_behavior_requirement(**test_case.behavior)
    importees = [MODULE_FILTER_4, MODULE_FILTER_5, MODULE_FILTER_6]

    if test_case.multiple_rule_objects:
        importees.extend([MODULE_FILTER_8, MODULE_FILTER_9])

    module_requirement = get_module_requirement(
        **{
            IMPORTERS: [MODULE_FILTER_1, MODULE_FILTER_2, MODULE_FILTER_3],
            IMPORTEES: importees,
        }
    )

    detector = LayerRuleViolationDetector(
        module_requirement, behavior_requirement, LAYER_MAPPING
    )

    violations = detector.get_rule_violation(
        test_case.explicitly_requested_dependencies,
        test_case.not_explicitly_requested_dependencies,
    )

    assert set(getattr(violations, test_case.expected_violation)) == set(  # type: ignore
        test_case.expected_violating_dependencies
    )
