from __future__ import annotations

from typing import Dict, List

import pytest

from integration.interesting_rules_for_tests import (
    multiple_rule_subjects_multiple_rule_objects_error_message_test_cases,
)
from pytestarch import Rule
from pytestarch.eval_structure.evaluable_architecture import (
    EvaluableArchitecture,
    ExplicitlyRequestedDependenciesByBaseModules,
    Module,
    NotExplicitlyRequestedDependenciesByBaseModule,
)
from pytestarch.rule_assessment.error_message.message_generator import (
    RuleViolationMessageGenerator,
)
from pytestarch.rule_assessment.rule_check.rule_violations import RuleViolations

ORIGINAL_SUBJECT = "A"
ORIGINAL_OBJECT_1 = "B"
ORIGINAL_OBJECT_2 = "C"
OTHER_OBJECT_1 = "Y"
OTHER_OBJECT_2 = "Z"

ORIGINAL_SUBJECT_MODULE = Module(name=ORIGINAL_SUBJECT)
ORIGINAL_OBJECT_MODULE_1 = Module(name=ORIGINAL_OBJECT_1)
ORIGINAL_OBJECT_MODULE_2 = Module(name=ORIGINAL_OBJECT_2)
OTHER_OBJECT_MODULE_1 = Module(name=OTHER_OBJECT_1)
OTHER_OBJECT_MODULE_2 = Module(name=OTHER_OBJECT_2)

single_object_import_generator = RuleViolationMessageGenerator(
    [ORIGINAL_SUBJECT_MODULE],
    [ORIGINAL_OBJECT_MODULE_1],
    True,
)
single_object_be_imported_generator = RuleViolationMessageGenerator(
    [ORIGINAL_SUBJECT_MODULE],
    [ORIGINAL_OBJECT_MODULE_1],
    False,
)

multiple_object_import_generator = RuleViolationMessageGenerator(
    [ORIGINAL_SUBJECT_MODULE],
    [ORIGINAL_OBJECT_MODULE_1, ORIGINAL_OBJECT_MODULE_2],
    True,
)
multiple_object_be_imported_generator = RuleViolationMessageGenerator(
    [ORIGINAL_SUBJECT_MODULE],
    [ORIGINAL_OBJECT_MODULE_1, ORIGINAL_OBJECT_MODULE_2],
    False,
)


message_content_test_cases = [
    pytest.param(
        single_object_import_generator,
        {"should_violated": True},
        f'"{ORIGINAL_SUBJECT}" does not import "{ORIGINAL_OBJECT_1}".',
        None,
        None,
        id="should import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_violated": True},
        f'"{ORIGINAL_SUBJECT}" is not imported by "{ORIGINAL_OBJECT_1}".',
        None,
        None,
        id="should be imported",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_only_violated_by_forbidden_import": True},
        f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
        None,
        {ORIGINAL_SUBJECT_MODULE: [(ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)]},
        id="should only import -- forbidden",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_only_violated_by_no_import": True},
        f'"{ORIGINAL_SUBJECT}" does not import "{ORIGINAL_OBJECT_1}".',
        None,
        None,
        id="should only import -- no import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_violated_by_forbidden_import": True},
        f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
        None,
        {ORIGINAL_SUBJECT_MODULE: [(OTHER_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE)]},
        id="should only be imported -- forbidden",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_violated_by_no_import": True},
        f'"{ORIGINAL_SUBJECT}" is not imported by "{ORIGINAL_OBJECT_1}".',
        None,
        None,
        id="should only be imported -- no import",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_not_violated": True},
        f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
        {
            (ORIGINAL_SUBJECT, ORIGINAL_OBJECT_1): [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)
            ]
        },
        None,
        id="should not import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_not_violated": True},
        f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
        {
            (ORIGINAL_SUBJECT, ORIGINAL_OBJECT_1): [
                (OTHER_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE)
            ]
        },
        None,
        id="should not be imported",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_except_violated": True},
        f'"{ORIGINAL_SUBJECT}" does not import any module that is not "{ORIGINAL_OBJECT_1}".',
        None,
        None,
        id="should except import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_except_violated": True},
        f'"{ORIGINAL_SUBJECT}" is not imported by any module that is not "{ORIGINAL_OBJECT_1}".',
        None,
        None,
        id="should except be imported",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_not_except_violated": True},
        f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
        None,
        {(ORIGINAL_SUBJECT): [(ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)]},
        id="should not except import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_not_except_violated": True},
        f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
        None,
        {(ORIGINAL_SUBJECT): [(OTHER_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE)]},
        id="should not except be imported",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_only_except_violated_by_forbidden_import": True},
        f'"{ORIGINAL_SUBJECT}" imports "{ORIGINAL_OBJECT_1}".',
        {ORIGINAL_SUBJECT: [(ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)]},
        None,
        id="should only import except -- forbidden",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_only_except_violated_by_no_import": True},
        f'"{ORIGINAL_SUBJECT}" does not import any module that is not "{ORIGINAL_OBJECT_1}".',
        None,
        None,
        id="should only import except -- no import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_except_violated_by_forbidden_import": True},
        f'"{ORIGINAL_SUBJECT}" is imported by "{ORIGINAL_OBJECT_1}".',
        {ORIGINAL_SUBJECT: [(ORIGINAL_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE)]},
        None,
        id="should only be imported except -- forbidden",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_except_violated_by_no_import": True},
        f'"{ORIGINAL_SUBJECT}" is not imported by any module that is not "{ORIGINAL_OBJECT_1}".',
        None,
        None,
        id="should only be imported except -- no import",
    ),
]


@pytest.mark.parametrize(
    "generator, violation, expected_message, explicitly_requested_dependencies, not_explicitly_requested_dependencies",
    message_content_test_cases,
)
def test_rule_violation_message_content(
    generator: RuleViolationMessageGenerator,
    violation: Dict[str, bool],
    expected_message: str,
    explicitly_requested_dependencies: ExplicitlyRequestedDependenciesByBaseModules,
    not_explicitly_requested_dependencies: NotExplicitlyRequestedDependenciesByBaseModule,
) -> None:
    violations = RuleViolations(
        explicitly_requested_dependencies=explicitly_requested_dependencies,
        not_explicitly_requested_dependencies=not_explicitly_requested_dependencies,
        **violation,
    )
    messages = generator.create_rule_violation_messages(violations)

    assert len(messages) == 1
    assert messages[0] == expected_message


message_only_present_if_rule_violated_test_cases = [
    pytest.param(
        single_object_import_generator,
        {"should_violated": True},
        None,
        None,
        id="should import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_violated": False},
        None,
        None,
        id="should import not present",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_only_violated_by_forbidden_import": True},
        None,
        {
            (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1): [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)
            ]
        },
        id="should only import -- forbidden present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_violated_by_forbidden_import": False},
        None,
        {
            (ORIGINAL_SUBJECT_MODULE, ORIGINAL_SUBJECT_MODULE): [
                (OTHER_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE)
            ]
        },
        id="should only import -- forbidden not present",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_only_violated_by_no_import": True},
        {
            (ORIGINAL_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE): [
                (OTHER_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE)
            ]
        },
        None,
        id="should only import -- no import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_violated_by_no_import": False},
        None,
        None,
        id="should only import -- no import not present",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_not_violated": True},
        {
            (ORIGINAL_SUBJECT, ORIGINAL_OBJECT_1): [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)
            ]
        },
        None,
        id="should not import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_not_violated": False},
        {
            (ORIGINAL_SUBJECT, ORIGINAL_OBJECT_1): [
                (OTHER_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE)
            ]
        },
        None,
        id="should not import not present",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_except_violated": True},
        None,
        None,
        id="should except import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_except_violated": False},
        None,
        None,
        id="should except import not present",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_not_except_violated": True},
        None,
        {
            (ORIGINAL_SUBJECT): [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        id="should not except import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_not_except_violated": False},
        None,
        {
            (ORIGINAL_SUBJECT): [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        id="should not except import not present",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_only_except_violated_by_forbidden_import": True},
        {
            (ORIGINAL_SUBJECT, ORIGINAL_OBJECT_1): [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        None,
        id="should only import -- forbidden present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_except_violated_by_forbidden_import": False},
        {
            (ORIGINAL_SUBJECT, ORIGINAL_OBJECT_1): [
                (ORIGINAL_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE)
            ]
        },
        None,
        id="should only import -- forbidden not present",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_only_except_violated_by_no_import": True},
        None,
        None,
        id="should only import except -- no import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_except_violated_by_no_import": False},
        None,
        None,
        id="should only import except -- no import not present",
    ),
]


@pytest.mark.parametrize(
    "generator, violation, explicitly_requested_dependencies, not_explicitly_requested_dependencies",
    message_only_present_if_rule_violated_test_cases,
)
def test_violated_message_only_present_if_rule_actually_violated(
    generator: RuleViolationMessageGenerator,
    violation: Dict[str, bool],
    explicitly_requested_dependencies: ExplicitlyRequestedDependenciesByBaseModules,
    not_explicitly_requested_dependencies: NotExplicitlyRequestedDependenciesByBaseModule,
) -> None:
    violations = RuleViolations(
        explicitly_requested_dependencies=explicitly_requested_dependencies,
        not_explicitly_requested_dependencies=not_explicitly_requested_dependencies,
        **violation,
    )
    messages = generator.create_rule_violation_messages(violations)

    assert bool(messages) is (True in violation.values())


multiple_objects_in_one_message_test_cases = [
    pytest.param(
        multiple_object_import_generator,
        {"should_violated": True},
        f'"{ORIGINAL_SUBJECT}" does not import "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        None,
        None,
        id="should import",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {"should_violated": True},
        f'"{ORIGINAL_SUBJECT}" is not imported by "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        None,
        None,
        id="should be imported",
    ),
    pytest.param(
        multiple_object_import_generator,
        {"should_only_violated_by_no_import": True},
        f'"{ORIGINAL_SUBJECT}" does not import "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        None,
        None,
        id="should only import -- no import",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {"should_only_violated_by_no_import": True},
        f'"{ORIGINAL_SUBJECT}" is not imported by "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        None,
        None,
        id="should only be imported -- no import",
    ),
    pytest.param(
        multiple_object_import_generator,
        {"should_except_violated": True},
        f'"{ORIGINAL_SUBJECT}" does not import any module that is not "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        None,
        None,
        id="should except import",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {"should_except_violated": True},
        f'"{ORIGINAL_SUBJECT}" is not imported by any module that is not "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        None,
        None,
        id="should except be imported",
    ),
    pytest.param(
        multiple_object_import_generator,
        {"should_only_except_violated_by_no_import": True},
        f'"{ORIGINAL_SUBJECT}" does not import any module that is not "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        None,
        None,
        id="should only import except -- no import",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {"should_only_except_violated_by_no_import": True},
        f'"{ORIGINAL_SUBJECT}" is not imported by any module that is not "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        None,
        None,
        id="should only be imported except -- no import",
    ),
]


@pytest.mark.parametrize(
    "generator, violation, expected_message, explicitly_requested_dependencies, not_explicitly_requested_dependencies",
    multiple_objects_in_one_message_test_cases,
)
def test_multiple_rule_objects_combined_in_one_message(
    generator: RuleViolationMessageGenerator,
    violation: Dict[str, bool],
    expected_message: str,
    explicitly_requested_dependencies: ExplicitlyRequestedDependenciesByBaseModules,
    not_explicitly_requested_dependencies: NotExplicitlyRequestedDependenciesByBaseModule,
) -> None:
    violations = RuleViolations(
        explicitly_requested_dependencies=explicitly_requested_dependencies,
        not_explicitly_requested_dependencies=not_explicitly_requested_dependencies,
        **violation,
    )
    messages = generator.create_rule_violation_messages(violations)

    assert len(messages) == 1
    assert messages[0] == expected_message


multiple_objects_in_multiple_messages_test_cases = [
    pytest.param(
        multiple_object_import_generator,
        {"should_only_violated_by_forbidden_import": True},
        2,
        [
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_2}".',
        ],
        None,
        {
            ORIGINAL_SUBJECT_MODULE: [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        id="should only import -- forbidden",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {"should_only_violated_by_forbidden_import": True},
        2,
        [
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_2}".',
        ],
        None,
        {
            ORIGINAL_SUBJECT_MODULE: [
                (OTHER_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE),
                (OTHER_OBJECT_MODULE_2, ORIGINAL_SUBJECT_MODULE),
            ]
        },
        id="should only be imported -- forbidden",
    ),
    pytest.param(
        multiple_object_import_generator,
        {"should_not_violated": True},
        2,
        [
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_2}".',
        ],
        {
            (ORIGINAL_SUBJECT, ORIGINAL_OBJECT_1): [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        None,
        id="should not import",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {"should_not_violated": True},
        2,
        [
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_2}".',
        ],
        {
            (ORIGINAL_SUBJECT, ORIGINAL_OBJECT_1): [
                (OTHER_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE),
                (OTHER_OBJECT_MODULE_2, ORIGINAL_SUBJECT_MODULE),
            ]
        },
        None,
        id="should not be imported",
    ),
    pytest.param(
        multiple_object_import_generator,
        {"should_not_except_violated": True},
        2,
        [
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_2}".',
        ],
        None,
        {
            (ORIGINAL_SUBJECT): [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        id="should not import except",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {"should_not_except_violated": True},
        2,
        [
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_2}".',
        ],
        None,
        {
            (ORIGINAL_SUBJECT): [
                (OTHER_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE),
                (OTHER_OBJECT_MODULE_2, ORIGINAL_SUBJECT_MODULE),
            ]
        },
        id="should not be imported except",
    ),
    pytest.param(
        multiple_object_import_generator,
        {"should_only_except_violated_by_forbidden_import": True},
        2,
        [
            f'"{ORIGINAL_SUBJECT}" imports "{ORIGINAL_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{ORIGINAL_OBJECT_2}".',
        ],
        {
            (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1): [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
            ],
            (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_2): [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ],
        },
        None,
        id="should only import -- forbidden",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {"should_only_except_violated_by_forbidden_import": True},
        2,
        [
            f'"{ORIGINAL_SUBJECT}" is imported by "{ORIGINAL_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" is imported by "{ORIGINAL_OBJECT_2}".',
        ],
        {
            (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1): [
                (ORIGINAL_OBJECT_MODULE_1, ORIGINAL_SUBJECT_MODULE),
            ],
            (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_2): [
                (ORIGINAL_OBJECT_MODULE_2, ORIGINAL_SUBJECT_MODULE),
            ],
        },
        None,
        id="should only be imported -- forbidden",
    ),
]


@pytest.mark.parametrize(
    "generator, violation, expected_message_count, expected_messages, explicitly_requested_dependencies, not_explicitly_requested_dependencies",
    multiple_objects_in_multiple_messages_test_cases,
)
def test_multiple_rule_objects_in_multiple_message(
    generator: RuleViolationMessageGenerator,
    violation: Dict[str, bool],
    expected_message_count: int,
    expected_messages: List[str],
    explicitly_requested_dependencies: ExplicitlyRequestedDependenciesByBaseModules,
    not_explicitly_requested_dependencies: NotExplicitlyRequestedDependenciesByBaseModule,
) -> None:
    violations = RuleViolations(
        explicitly_requested_dependencies=explicitly_requested_dependencies,
        not_explicitly_requested_dependencies=not_explicitly_requested_dependencies,
        **violation,
    )
    messages = generator.create_rule_violation_messages(violations)

    assert len(messages) == expected_message_count
    assert messages == expected_messages


forbidden_and_no_import_test_cases = [
    pytest.param(
        {
            "should_only_violated_by_forbidden_import": True,
            "should_only_violated_by_no_import": True,
        },
        [
            f'"{ORIGINAL_SUBJECT}" does not import "{ORIGINAL_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
        ],
        None,
        {ORIGINAL_SUBJECT: [(ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)]},
        id="should only",
    ),
    pytest.param(
        {
            "should_only_except_violated_by_forbidden_import": True,
            "should_only_except_violated_by_no_import": True,
        },
        [
            f'"{ORIGINAL_SUBJECT}" does not import any module that is not "{ORIGINAL_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{ORIGINAL_OBJECT_1}".',
        ],
        {ORIGINAL_SUBJECT: [(ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)]},
        {ORIGINAL_SUBJECT_MODULE: []},
        id="should only except",
    ),
]


@pytest.mark.parametrize(
    "violation, expected_messages, explicitly_requested_dependencies, not_explicitly_requested_dependencies",
    forbidden_and_no_import_test_cases,
)
def test_multiple_messages_if_forbidden_and_no_import_both_present(
    violation: Dict[str, bool],
    expected_messages: List[str],
    explicitly_requested_dependencies: ExplicitlyRequestedDependenciesByBaseModules,
    not_explicitly_requested_dependencies: NotExplicitlyRequestedDependenciesByBaseModule,
) -> None:
    violations = RuleViolations(
        explicitly_requested_dependencies=explicitly_requested_dependencies,
        not_explicitly_requested_dependencies=not_explicitly_requested_dependencies,
        **violation,
    )
    messages = single_object_import_generator.create_rule_violation_messages(violations)

    assert len(messages) == 2
    assert messages == expected_messages


def test_only_offending_rule_object_listed(
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    rule = (
        Rule()
        .modules_that()
        .are_named("src.moduleA.submoduleA1.submoduleA11.fileA11")
        .should_only()
        .import_modules_that()
        .are_named(["src.moduleB", "src.moduleC"])
    )
    with pytest.raises(
        AssertionError,
        match='"src.moduleA.submoduleA1.submoduleA11.fileA11" does not import "src.moduleC".',
    ):
        rule.assert_applies(graph_based_on_string_module_names)


@pytest.mark.parametrize(
    "rule, expected_error_message",
    multiple_rule_subjects_multiple_rule_objects_error_message_test_cases,
)
def test_multiple_rule_subjects(
    rule: Rule,
    expected_error_message: str,
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    with pytest.raises(AssertionError, match=expected_error_message):
        rule.assert_applies(graph_based_on_string_module_names)
