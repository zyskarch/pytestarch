from __future__ import annotations

import pytest
from integration.interesting_rules_for_tests import (
    FILE_A11,
    B,
    C,
    additional_multiple_rule_subjects_multiple_rule_objects_error_message_test_cases,
    multiple_rule_subjects_multiple_rule_objects_error_message_test_cases,
)

from pytestarch import Rule
from pytestarch.eval_structure.evaluable_architecture import (
    Dependency,
    EvaluableArchitecture,
    Module,
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

ORIGINAL_SUBJECT_MODULE = Module(identifier=ORIGINAL_SUBJECT)
ORIGINAL_OBJECT_MODULE_1 = Module(identifier=ORIGINAL_OBJECT_1)
ORIGINAL_OBJECT_MODULE_2 = Module(identifier=ORIGINAL_OBJECT_2)
OTHER_OBJECT_MODULE_1 = Module(identifier=OTHER_OBJECT_1)
OTHER_OBJECT_MODULE_2 = Module(identifier=OTHER_OBJECT_2)

single_object_import_generator = RuleViolationMessageGenerator(
    True,
)
single_object_be_imported_generator = RuleViolationMessageGenerator(
    False,
)

multiple_object_import_generator = RuleViolationMessageGenerator(
    True,
)
multiple_object_be_imported_generator = RuleViolationMessageGenerator(
    False,
)


message_content_test_cases = [
    pytest.param(
        single_object_import_generator,
        {"should_violations": [(ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)]},
        f'"{ORIGINAL_SUBJECT}" does not import "{ORIGINAL_OBJECT_1}".',
        id="should import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_violations": [(ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)]},
        f'"{ORIGINAL_SUBJECT}" is not imported by "{ORIGINAL_OBJECT_1}".',
        id="should be imported",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_only_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
        id="should only import -- forbidden",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_only_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" does not import "{ORIGINAL_OBJECT_1}".',
        id="should only import -- no import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {
            "should_only_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
        id="should only be imported -- forbidden",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {
            "should_only_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" is not imported by "{ORIGINAL_OBJECT_1}".',
        id="should only be imported -- no import",
    ),
    pytest.param(
        single_object_import_generator,
        {"should_not_violations": [(ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)]},
        f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
        id="should not import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_not_violations": [(ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)]},
        f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
        id="should not be imported",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_except_violations": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" does not import any module that is not "{ORIGINAL_OBJECT_1}".',
        id="should except import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {
            "should_except_violations": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" is not imported by any module that is not "{ORIGINAL_OBJECT_1}".',
        id="should except be imported",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_not_except_violations": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
        id="should not except import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {
            "should_not_except_violations": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
        id="should not except be imported",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_only_except_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" imports "{ORIGINAL_OBJECT_1}".',
        id="should only import except -- forbidden",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_only_except_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" does not import any module that is not "{ORIGINAL_OBJECT_1}".',
        id="should only import except -- no import",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {
            "should_only_except_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" is imported by "{ORIGINAL_OBJECT_1}".',
        id="should only be imported except -- forbidden",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {
            "should_only_except_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        f'"{ORIGINAL_SUBJECT}" is not imported by any module that is not "{ORIGINAL_OBJECT_1}".',
        id="should only be imported except -- no import",
    ),
]


@pytest.mark.parametrize(
    "generator, violation, expected_message",
    message_content_test_cases,
)
def test_rule_violation_message_content(
    generator: RuleViolationMessageGenerator,
    violation: dict[str, list[Dependency]],
    expected_message: str,
) -> None:
    kwargs = _get_rule_violations_initialisation_dict(violation)
    violations = RuleViolations(**kwargs)  # type: ignore
    messages = generator.create_rule_violation_messages(violations)

    assert len(messages) == 1
    assert messages[0] == expected_message


def _get_rule_violations_initialisation_dict(
    violation: dict[str, list[Dependency]]
) -> dict[str, list[Dependency]]:
    kwargs: dict[str, list[Dependency]] = {
        "should_violations": [],
        "should_only_violations_by_forbidden_import": [],
        "should_only_violations_by_no_import": [],
        "should_not_violations": [],
        "should_except_violations": [],
        "should_only_except_violations_by_forbidden_import": [],
        "should_only_except_violations_by_no_import": [],
        "should_not_except_violations": [],
    }
    kwargs.update(violation)
    return kwargs


message_only_present_if_rule_violated_test_cases = [
    pytest.param(
        single_object_import_generator,
        {"should_violations": [(ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)]},
        id="should import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_violations": []},
        id="should import not present",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_only_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        id="should only import -- forbidden present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_violations_by_forbidden_import": []},
        id="should only import -- forbidden not present",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_only_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        id="should only import -- no import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_violations_by_no_import": []},
        id="should only import -- no import not present",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_not_violations": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        id="should not import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_not_violations": []},
        id="should not import not present",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_except_violations": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        id="should except import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_except_violations": []},
        id="should except import not present",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_not_except_violations": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        id="should not except import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_not_except_violations": []},
        id="should not except import not present",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_only_except_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        id="should only import -- forbidden present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_except_violations_by_forbidden_import": []},
        id="should only import -- forbidden not present",
    ),
    pytest.param(
        single_object_import_generator,
        {
            "should_only_except_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ]
        },
        id="should only import except -- no import present",
    ),
    pytest.param(
        single_object_be_imported_generator,
        {"should_only_except_violations_by_no_import": []},
        id="should only import except -- no import not present",
    ),
]


@pytest.mark.parametrize(
    "generator, violation",
    message_only_present_if_rule_violated_test_cases,
)
def test_violated_message_only_present_if_rule_actually_violated(
    generator: RuleViolationMessageGenerator,
    violation: dict[str, list[Dependency]],
) -> None:
    kwargs = _get_rule_violations_initialisation_dict(violation)
    violations = RuleViolations(
        **kwargs,  # type: ignore
    )
    messages = generator.create_rule_violation_messages(violations)

    assert bool(messages) is any(
        len(dependency) > 0 for dependency in violation.values()
    )


multiple_objects_in_one_message_test_cases = [
    pytest.param(
        multiple_object_import_generator,
        {
            "should_violations": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ]
        },
        f'"{ORIGINAL_SUBJECT}" does not import "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        id="should import",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {
            "should_violations": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ]
        },
        f'"{ORIGINAL_SUBJECT}" is not imported by "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        id="should be imported",
    ),
    pytest.param(
        multiple_object_import_generator,
        {
            "should_only_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ]
        },
        f'"{ORIGINAL_SUBJECT}" does not import "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        id="should only import -- no import",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {
            "should_only_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ]
        },
        f'"{ORIGINAL_SUBJECT}" is not imported by "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        id="should only be imported -- no import",
    ),
    pytest.param(
        multiple_object_import_generator,
        {
            "should_except_violations": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ]
        },
        f'"{ORIGINAL_SUBJECT}" does not import any module that is not "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        id="should except import",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {
            "should_except_violations": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ]
        },
        f'"{ORIGINAL_SUBJECT}" is not imported by any module that is not "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        id="should except be imported",
    ),
    pytest.param(
        multiple_object_import_generator,
        {
            "should_only_except_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ]
        },
        f'"{ORIGINAL_SUBJECT}" does not import any module that is not "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        id="should only import except -- no import",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {
            "should_only_except_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ]
        },
        f'"{ORIGINAL_SUBJECT}" is not imported by any module that is not "{ORIGINAL_OBJECT_1}", "{ORIGINAL_OBJECT_2}".',
        id="should only be imported except -- no import",
    ),
]


@pytest.mark.parametrize(
    "generator, violation, expected_message",
    multiple_objects_in_one_message_test_cases,
)
def test_multiple_rule_objects_combined_in_one_message(
    generator: RuleViolationMessageGenerator,
    violation: dict[str, list[Dependency]],
    expected_message: str,
) -> None:
    kwargs = _get_rule_violations_initialisation_dict(violation)
    violations = RuleViolations(**kwargs)  # type: ignore
    messages = generator.create_rule_violation_messages(violations)

    assert len(messages) == 1
    assert messages[0] == expected_message


multiple_objects_in_multiple_messages_test_cases = [
    pytest.param(
        multiple_object_import_generator,
        {
            "should_only_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        2,
        [
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_2}".',
        ],
        id="should only import -- forbidden",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {
            "should_only_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        2,
        [
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_2}".',
        ],
        id="should only be imported -- forbidden",
    ),
    pytest.param(
        multiple_object_import_generator,
        {
            "should_not_violations": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        2,
        [
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_2}".',
        ],
        id="should not import",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {
            "should_not_violations": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        2,
        [
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_2}".',
        ],
        id="should not be imported",
    ),
    pytest.param(
        multiple_object_import_generator,
        {
            "should_not_except_violations": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        2,
        [
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_2}".',
        ],
        id="should not import except",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {
            "should_not_except_violations": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_2),
            ]
        },
        2,
        [
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" is imported by "{OTHER_OBJECT_2}".',
        ],
        id="should not be imported except",
    ),
    pytest.param(
        multiple_object_import_generator,
        {
            "should_only_except_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ]
        },
        2,
        [
            f'"{ORIGINAL_SUBJECT}" imports "{ORIGINAL_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{ORIGINAL_OBJECT_2}".',
        ],
        id="should only import -- forbidden",
    ),
    pytest.param(
        multiple_object_be_imported_generator,
        {
            "should_only_except_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1),
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_2),
            ]
        },
        2,
        [
            f'"{ORIGINAL_SUBJECT}" is imported by "{ORIGINAL_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" is imported by "{ORIGINAL_OBJECT_2}".',
        ],
        id="should only be imported -- forbidden",
    ),
]


@pytest.mark.parametrize(
    "generator, violation, expected_message_count, expected_messages",
    multiple_objects_in_multiple_messages_test_cases,
)
def test_multiple_rule_objects_in_multiple_message(
    generator: RuleViolationMessageGenerator,
    violation: dict[str, list[Dependency]],
    expected_message_count: int,
    expected_messages: list[str],
) -> None:
    kwargs = _get_rule_violations_initialisation_dict(violation)
    violations = RuleViolations(**kwargs)  # type: ignore
    messages = generator.create_rule_violation_messages(violations)

    assert len(messages) == expected_message_count
    assert messages == expected_messages


forbidden_and_no_import_test_cases = [
    pytest.param(
        {
            "should_only_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, OTHER_OBJECT_MODULE_1)
            ],
            "should_only_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ],
        },
        [
            f'"{ORIGINAL_SUBJECT}" does not import "{ORIGINAL_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{OTHER_OBJECT_1}".',
        ],
        id="should only",
    ),
    pytest.param(
        {
            "should_only_except_violations_by_forbidden_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ],
            "should_only_except_violations_by_no_import": [
                (ORIGINAL_SUBJECT_MODULE, ORIGINAL_OBJECT_MODULE_1)
            ],
        },
        [
            f'"{ORIGINAL_SUBJECT}" does not import any module that is not "{ORIGINAL_OBJECT_1}".',
            f'"{ORIGINAL_SUBJECT}" imports "{ORIGINAL_OBJECT_1}".',
        ],
        id="should only except",
    ),
]


@pytest.mark.parametrize(
    "violation, expected_messages",
    forbidden_and_no_import_test_cases,
)
def test_multiple_messages_if_forbidden_and_no_import_both_present(
    violation: dict[str, list[Dependency]],
    expected_messages: list[str],
) -> None:
    kwargs = _get_rule_violations_initialisation_dict(violation)
    violations = RuleViolations(**kwargs)  # type: ignore
    messages = single_object_import_generator.create_rule_violation_messages(violations)

    assert len(messages) == 2
    assert messages == expected_messages


def test_only_offending_rule_object_listed(
    graph_based_on_string_module_names: EvaluableArchitecture,
) -> None:
    rule = (
        Rule()
        .modules_that()
        .are_named(FILE_A11)
        .should_only()
        .import_modules_that()
        .are_named([B, C])
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


@pytest.mark.parametrize(
    "rule, expected_error_message",
    additional_multiple_rule_subjects_multiple_rule_objects_error_message_test_cases,
)
def test_multiple_rule_subjects_additional_dependencies_only_present_in_other_test_project(
    rule: Rule,
    expected_error_message: str,
    flat_project_1: EvaluableArchitecture,
) -> None:
    with pytest.raises(AssertionError, match=expected_error_message):
        rule.assert_applies(flat_project_1)
