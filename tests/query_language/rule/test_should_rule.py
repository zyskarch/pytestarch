from __future__ import annotations

from pytestarch import EvaluableArchitecture, Rule
from query_language.rule.conftest import (
    MODULE_1,
    MODULE_2,
    MODULE_3,
    MODULE_4,
    MODULE_6,
    MODULE_7,
    SUB_MODULE_OF_1,
    SUB_MODULE_OF_7,
)
from query_language.rule.test_rule import (
    assert_rule_applies,
    assert_rule_does_not_apply,
)


def test_should_be_imported_except_named_named_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should().be_imported_by_modules_except_modules_that().are_named(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_except_named_submodule_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should().be_imported_by_modules_except_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_except_submodule_named_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should().be_imported_by_modules_except_modules_that().are_named(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_except_submodule_submodule_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should().be_imported_by_modules_except_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_except_named_named_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_4
    ).should().be_imported_by_modules_except_modules_that().are_named(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_except_named_submodule_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_7
    ).should().be_imported_by_modules_except_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_except_submodule_named_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_4
    ).should().be_imported_by_modules_except_modules_that().are_named(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_except_submodule_submodule_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_4
    ).should().be_imported_by_modules_except_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_named_named_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should().be_imported_by_modules_that().are_named(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_named_submodule_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_1
    ).should().be_imported_by_modules_that().are_sub_modules_of(MODULE_7)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_submodule_named_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should().be_imported_by_modules_that().are_named(MODULE_7)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_submodule_submodule_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should().be_imported_by_modules_that().are_sub_modules_of(MODULE_7)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_named_named_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_6
    ).should().be_imported_by_modules_that().are_named(MODULE_1)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_named_submodule_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_6
    ).should().be_imported_by_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_submodule_named_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_6
    ).should().be_imported_by_modules_that().are_named(MODULE_1)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_submodule_submodule_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_6
    ).should().be_imported_by_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_import_except_named_named_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should().import_modules_except_modules_that().are_named(MODULE_4)

    assert_rule_applies(rule, evaluable1)


def test_should_import_except_named_submodule_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should().import_modules_except_modules_that().are_sub_modules_of(MODULE_4)

    assert_rule_applies(rule, evaluable1)


def test_should_import_except_submodule_named_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_7
    ).should().import_modules_except_modules_that().are_named(MODULE_4)

    assert_rule_applies(rule, evaluable1)


def test_should_import_except_submodule_submodule_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_7
    ).should().import_modules_except_modules_that().are_sub_modules_of(MODULE_4)

    assert_rule_applies(rule, evaluable1)


def test_should_import_except_named_named_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_1
    ).should().import_modules_except_modules_that().are_named(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_import_except_named_submodule_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_7
    ).should().import_modules_except_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_import_except_submodule_named_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should().import_modules_except_modules_that().are_named(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_import_except_submodule_submodule_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should().import_modules_except_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_import_named_named_positive(evaluable1: EvaluableArchitecture) -> None:
    rule = Rule()

    rule.modules_that().are_named(MODULE_1).should().import_modules_that().are_named(
        MODULE_2
    )

    assert_rule_applies(rule, evaluable1)


def test_should_import_named_submodule_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        SUB_MODULE_OF_7
    ).should().import_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_import_submodule_named_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_7
    ).should().import_modules_that().are_named(SUB_MODULE_OF_1)

    assert_rule_applies(rule, evaluable1)


def test_should_import_submodule_submodule_positive(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_7
    ).should().import_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_import_named_named_negative(evaluable1: EvaluableArchitecture) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        SUB_MODULE_OF_1
    ).should().import_modules_that().are_named(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_import_named_submodule_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        SUB_MODULE_OF_1
    ).should().import_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_import_submodule_named_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        SUB_MODULE_OF_1
    ).should().import_modules_that().are_named(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)


def test_should_import_submodule_submodule_negative(
    evaluable1: EvaluableArchitecture,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        SUB_MODULE_OF_1
    ).should().import_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_does_not_apply(rule, evaluable1)
