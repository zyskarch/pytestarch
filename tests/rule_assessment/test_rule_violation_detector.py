from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from pytestarch.eval_structure.evaluable_architecture import (
    Dependency,
    ExplicitlyRequestedDependenciesByBaseModules,
    Module,
    ModuleNameFilter,
    NotExplicitlyRequestedDependenciesByBaseModule,
)
from pytestarch.rule_assessment.rule_check.behavior_requirement import (
    BehaviorRequirement,
)
from pytestarch.rule_assessment.rule_check.module_requirement import ModuleRequirement
from pytestarch.rule_assessment.rule_check.rule_violation_detector import (
    RuleViolationDetector,
)

IMPORTER_SPECIFIED_AS_RULE_SUBJECT = "importer_specified_as_rule_subject"
IMPORTEES = "importees"
IMPORTERS = "importers"

BEHAVIOR_EXCEPTION = "behavior_exception"
SHOULD_ONLY = "should_only"
SHOULD_NOT = "should_not"
SHOULD = "should"

SHOULD_VIOLATIONS = "should_violations"
SHOULD_NOT_VIOLATIONS = "should_not_violations"
SHOULD_ONLY_VIOLATIONS_NO_IMPORT = "should_only_violations_by_no_import"
SHOULD_ONLY_VIOLATIONS_FORBIDDEN_IMPORT = "should_only_violations_by_forbidden_import"
SHOULD_EXCEPT_VIOLATIONS = "should_except_violations"
SHOULD_NOT_EXCEPT_VIOLATIONS = "should_not_except_violations"
SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT = "should_only_except_violations_by_no_import"
SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT = (
    "should_only_except_violations_by_forbidden_import"
)

MODULE_NAME_1 = "M1"
MODULE_NAME_2 = "M2"
MODULE_NAME_3 = "M3"

MODULE_FILTER_1 = ModuleNameFilter(MODULE_NAME_1)
MODULE_FILTER_2 = ModuleNameFilter(MODULE_NAME_2)
MODULE_FILTER_3 = ModuleNameFilter(MODULE_NAME_3)

MODULE_1 = Module(MODULE_NAME_1)
MODULE_2 = Module(MODULE_NAME_2)
MODULE_3 = Module(MODULE_NAME_3)


def get_behavior_requirement(**kwargs) -> BehaviorRequirement:
    if SHOULD not in kwargs:
        kwargs[SHOULD] = False

    if SHOULD_NOT not in kwargs:
        kwargs[SHOULD_NOT] = False

    if SHOULD_ONLY not in kwargs:
        kwargs[SHOULD_ONLY] = False

    if BEHAVIOR_EXCEPTION not in kwargs:
        kwargs[BEHAVIOR_EXCEPTION] = False

    return BehaviorRequirement(**kwargs)


def get_module_requirement(**kwargs) -> ModuleRequirement:
    if IMPORTERS not in kwargs:
        kwargs[IMPORTERS] = [MODULE_FILTER_1]

    if IMPORTEES not in kwargs:
        kwargs[IMPORTEES] = [MODULE_FILTER_2]

    if IMPORTER_SPECIFIED_AS_RULE_SUBJECT not in kwargs:
        kwargs[IMPORTER_SPECIFIED_AS_RULE_SUBJECT] = True

    return ModuleRequirement(**kwargs)


@dataclass
class RuleViolationDetectorTestCase:
    behavior: dict[str, Any]
    expected_violation: str | None
    expected_violating_dependencies: set[Dependency]
    explicitly_requested_dependencies: (
        ExplicitlyRequestedDependenciesByBaseModules | None
    )
    not_explicitly_requested_dependencies: (
        NotExplicitlyRequestedDependenciesByBaseModule | None
    )


test_cases = [
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            set(),
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: []},
        ),
        id="should_fulfilled",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: False}, SHOULD_VIOLATIONS, set(), {}, {}
        ),
        id="should_violated_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True},
            SHOULD_VIOLATIONS,
            {(MODULE_1, MODULE_2)},
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: []},
        ),
        id="should_violated",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True},
            SHOULD_NOT_VIOLATIONS,
            set(),
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: []},
        ),
        id="should_not_fulfilled",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: False},
            SHOULD_NOT_VIOLATIONS,
            set(),
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: []},
        ),
        id="should_not_violated_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True},
            SHOULD_NOT_VIOLATIONS,
            {(MODULE_1, MODULE_2)},
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: []},
        ),
        id="should_not_violated",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
            set(),
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: []},
        ),
        id="should_only_fulfilled",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: False},
            SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
            set(),
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: []},
        ),
        id="should_only_no_import_violated_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_NO_IMPORT,
            {(MODULE_1, MODULE_2)},
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: []},
        ),
        id="should_only_no_import_violated",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: False},
            SHOULD_ONLY_VIOLATIONS_FORBIDDEN_IMPORT,
            set(),
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: [(MODULE_1, MODULE_3)]},
        ),
        id="should_only_no_forbidden_import_violated_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True},
            SHOULD_ONLY_VIOLATIONS_FORBIDDEN_IMPORT,
            {(MODULE_1, MODULE_3)},
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: [(MODULE_1, MODULE_3)]},
        ),
        id="should_only_no_forbidden_import_violated",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            set(),
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: [(MODULE_1, MODULE_3)]},
        ),
        id="should_except_fulfilled",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: False, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            set(),
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: []},
        ),
        id="should_except_violated_should_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: False},
            SHOULD_EXCEPT_VIOLATIONS,
            set(),
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: []},
        ),
        id="should_except_violated_except_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_EXCEPT_VIOLATIONS,
            {(MODULE_1, MODULE_2)},
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: []},
        ),
        id="should_except_violated",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            set(),
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: []},
        ),
        id="should_not_except_fulfilled",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: False, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            set(),
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: [(MODULE_1, MODULE_3)]},
        ),
        id="should_not_except_violated_should_not_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: False},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            set(),
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: [(MODULE_1, MODULE_3)]},
        ),
        id="should_not_except_violated_except_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_NOT: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_NOT_EXCEPT_VIOLATIONS,
            {(MODULE_1, MODULE_3)},
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: [(MODULE_1, MODULE_3)]},
        ),
        id="should_not_except_violated",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
            set(),
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: [(MODULE_1, MODULE_3)]},
        ),
        id="should_only_except_fulfilled",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: False, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
            set(),
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: []},
        ),
        id="should_only_except_no_import_violated_should_only_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: False},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
            set(),
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: []},
        ),
        id="should_only_except_no_import_violated_except_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_NO_IMPORT,
            {(MODULE_1, MODULE_2)},
            {(MODULE_1, MODULE_2): []},
            {MODULE_1: []},
        ),
        id="should_only_except_no_import_violated",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: False, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
            set(),
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: [(MODULE_1, MODULE_3)]},
        ),
        id="should_only_except_no_forbidden_import_violated_should_only_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: False},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
            set(),
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: [(MODULE_1, MODULE_3)]},
        ),
        id="should_only_except_no_forbidden_import_violated_except_not_required",
    ),
    pytest.param(
        RuleViolationDetectorTestCase(
            {SHOULD_ONLY: True, BEHAVIOR_EXCEPTION: True},
            SHOULD_ONLY_EXCEPT_VIOLATIONS_FORBIDDEN_IMPORT,
            {(MODULE_1, MODULE_2)},
            {(MODULE_1, MODULE_2): [(MODULE_1, MODULE_2)]},
            {MODULE_1: [(MODULE_1, MODULE_3)]},
        ),
        id="should_only_except_no_forbidden_import_violated",
    ),
]


@pytest.mark.parametrize("test_case", test_cases)
def test_rule_violation_detection_as_expected(
    test_case: RuleViolationDetectorTestCase,
) -> None:
    behavior_requirement = get_behavior_requirement(**test_case.behavior)
    module_requirement = get_module_requirement(
        **{IMPORTERS: [MODULE_FILTER_1], IMPORTEES: [MODULE_FILTER_2]}
    )

    detector = RuleViolationDetector(module_requirement, behavior_requirement)

    violations = detector.get_rule_violation(
        test_case.explicitly_requested_dependencies,
        test_case.not_explicitly_requested_dependencies,
    )

    assert test_case.expected_violation is not None
    assert (
        getattr(violations, test_case.expected_violation)
        == test_case.expected_violating_dependencies
    )
