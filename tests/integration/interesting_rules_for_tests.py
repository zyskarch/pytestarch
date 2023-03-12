from __future__ import annotations

import pytest

from pytestarch import Rule

TEST_PROJECT_EXPORTER = "flat_test_project_1.exporter"
TEST_PROJECT_IMPORTER = "flat_test_project_1.importer"

C = "src.moduleC"
B = "src.moduleB"
A = "src.moduleA"
A2 = f"{A}.submoduleA2"
FILE_A2 = f"{A2}.fileA2"
A1 = f"{A}.submoduleA1"
A11 = f"{A1}.submoduleA11"
FILE_A = f"{A}.fileA"
FILE_A11 = f"{A11}.fileA11"
B1 = f"{B}.submoduleB1"
FILE_B = f"{B}.fileB"
FILE_B1 = f"{B1}.fileB1"
FILE_B11 = f"{B1}.submoduleB11.fileB11"
FILE_B2 = f"{B1}.fileB2"
FILE_C = f"{C}.fileC"


rules_for_level_limits = [
    (
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .import_modules_except_modules_that()
        .are_named(A),
        True,
        False,
    ),
    (
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named(A2),
        False,
        True,
    ),
    # same rule, but adapted for flattened graph
    (
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named(A),
        False,
        False,
    ),
    (
        Rule()
        .modules_that()
        .are_sub_modules_of(A1)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of(B),
        True,
        True,
    ),
    # same rule, but adapted for flattened graph
    (
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .import_modules_that()
        .are_sub_modules_of(B),
        False,  # there are no true sub modules left
        False,
    ),
    (
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(A),
        False,
        False,
    ),
    (
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(A),
        True,
        True,
    ),
    (
        Rule()
        .modules_that()
        .are_named(A11)
        .should_not()
        .import_modules_that()
        .are_named(FILE_B2),
        True,
        True,
    ),
    # same rule, but adapted for flattened graph
    (
        Rule().modules_that().are_named(A).should().import_modules_that().are_named(B),
        True,
        False,
    ),
    (
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of(B),
        False,
        False,  # there are no true sub modules left
    ),
    (
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B),
        True,
        False,
    ),
]

single_rule_subject_single_rule_object_error_message_test_cases = [
    pytest.param(
        Rule().modules_that().are_named(C).should().import_modules_that().are_named(A),
        f'"{C}" does not import "{A}".',
        id="named should import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should()
        .import_modules_that()
        .are_sub_modules_of(A),
        f'"{C}" does not import a sub module of "{A}".',
        id="named should import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should()
        .import_modules_that()
        .are_named(A),
        f'Sub modules of "{C}" do not import "{A}".',
        id="submodule should import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should()
        .import_modules_that()
        .are_sub_modules_of(A),
        f'Sub modules of "{C}" do not import a sub module of "{A}".',
        id="submodule should import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_that()
        .are_named(B),
        f'"{FILE_A}" imports "{FILE_C}".',
        id="named should only import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of(B),
        f'"{FILE_A}" imports "{FILE_C}".' + "\n" + f'"{FILE_A2}" imports "{FILE_C}".',
        id="named should only import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .are_named(B),
        f'"{FILE_A}" imports "{FILE_C}".',
        id="submodule should only import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of(B),
        f'"{FILE_A}" imports "{FILE_C}".' + "\n" + f'"{FILE_A2}" imports "{FILE_C}".',
        id="submodule should only import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .import_modules_that()
        .are_named(A),
        f'"{FILE_B11}" imports "src.moduleA.submoduleA1.submoduleA11.fileA11',
        id="named should not import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of(A),
        f'"{FILE_B11}" imports "{FILE_A11}".',
        id="named should not import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should_not()
        .import_modules_that()
        .are_named(A),
        f'"{FILE_B11}" imports "{FILE_A11}".',
        id="submodule should not import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of(A),
        f'"{FILE_B11}" imports "{FILE_A11}".',
        id="submodule should not import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_named(C),
        f'"{FILE_A2}" does not import any module that is not "{C}".',
        id="named should import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        f'"{FILE_A2}" does not import any module that is not a sub module of "{C}".',
        id="named should import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_named(C),
        f'Sub modules of "{FILE_A2}" do not import any module that is not "{C}".',
        id="submodule should import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        f'Sub modules of "{FILE_A2}" do not import any module that is not a sub module of "{C}".',
        id="submodule should import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(C),
        f'"{FILE_A2}" imports "{FILE_C}".',
        id="named should only import except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        f'"{FILE_A2}" imports "{FILE_C}".',
        id="named should only import except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(C),
        f'"{FILE_A2}" imports "{FILE_C}".',
        id="submodule should only import except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        f'"{FILE_A2}" imports "{FILE_C}".',
        id="submodule should only import except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(B),
        f'"{C}" does not import any module that is not "{B}".',
        id="named should only import except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        f'"{C}" does not import any module that is not a sub module of "{B}".',
        id="named should only import except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(B),
        f'Sub modules of "{C}" do not import any module that is not "{B}".',
        id="submodule should only import except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        f'Sub modules of "{C}" do not import any module that is not a sub module of "{B}".',
        id="submodule should only import except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_named(B),
        f'"{FILE_A}" imports "{FILE_C}".',
        id="named should not import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        f'"{FILE_A}" imports "{FILE_C}".' + "\n" + f'"{FILE_A2}" imports "{FILE_C}"',
        id="named should not import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_named(B),
        f'"{FILE_A}" imports "{FILE_C}".',
        id="submodule should not import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        f'"{FILE_A}" imports "{FILE_C}".' + "\n" + f'"{FILE_A2}" imports "{FILE_C}".',
        id="submodule should not import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should()
        .be_imported_by_modules_that()
        .are_named(C),
        f'"{A}" is not imported by "{C}".',
        id="named should be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of(C),
        f'"{A}" is not imported by a sub module of "{C}".',
        id="named should be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .be_imported_by_modules_that()
        .are_named(C),
        f'Sub modules of "{A}" are not imported by "{C}".',
        id="submodule should be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of(C),
        f'Sub modules of "{A}" are not imported by a sub module of "{C}".',
        id="submodule should be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named(B),
        f'"{C}" is not imported by "{B}".',
        id="named should only be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of(B),
        f'"{C}" is not imported by a sub module of "{B}"',
        id="named should only be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named(B),
        f'Sub modules of "{C}" are not imported by "{B}".',
        id="submodule should only be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of(B),
        f'Sub modules of "{C}" are not imported by a sub module of "{B}".',
        id="submodule should only be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_named(A),
        f'"{FILE_C}" is imported by "{FILE_A}".\n"{FILE_C}" is imported by "{FILE_A2}"',
        id="named should not be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(A),
        f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="named should not be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_named(A),
        f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="submodule should not be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(A),
        f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="submodule should not be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named(A),
        f'"{B}" is not imported by any module that is not "{A}".',
        id="named should be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(A),
        f'"{B}" is not imported by any module that is not a sub module of "{A}".',
        id="named should be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named(A),
        f'Sub modules of "{B}" are not imported by any module that is not "{A}".',
        id="submodule should be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(A),
        f'Sub modules of "{B}" are not imported by any module that is not a sub module of "{A}".',
        id="submodule should be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(FILE_B2),
        f'"{FILE_A11}" is imported by "{FILE_B2}".',
        id="named should only be imported by except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B1),
        f'"{FILE_A11}" is imported by "{FILE_B11}".',
        id="named should only be imported by except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(FILE_B2),
        f'"{FILE_A11}" is imported by "{FILE_B2}".',
        id="submodule should only be imported by except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A1)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B1),
        f'"{FILE_A11}" is imported by "{FILE_B11}".',
        id="submodule should only be imported by except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(B),
        f'"{A}" is not imported by any module that is not "{B}".',
        id="named should only be imported by except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B),
        f'"{A}" is not imported by any module that is not a sub module of "{B}"',
        id="named should only be imported by except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(B),
        f'Sub modules of "{A}" are not imported by any module that is not "{B}"',
        id="submodule should only be imported by except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B),
        f'Sub modules of "{A}" are not imported by any module that is not a sub module of "{B}"',
        id="submodule should only be imported by except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named(FILE_A2),
        f'"{FILE_C}" is imported by "{FILE_A}".',
        id="named should not be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(A2),
        f'"{FILE_C}" is imported by "{FILE_A}".',
        id="named should not be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named(A2),
        f'"{FILE_C}" is imported by "{FILE_A}".',
        id="submodule should not be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(FILE_A2),
        f'"{FILE_C}" is imported by "{FILE_A}".'
        + "\n"
        + f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="submodule should not be imported by except submodule",
    ),
    pytest.param(
        Rule().modules_that().are_named(C).should_not().be_imported_by_anything(),
        f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="not be imported by anything",
    ),
    pytest.param(
        Rule().modules_that().are_named(A).should_not().import_anything(),
        f'"{FILE_A}" imports "{FILE_C}".',
        id="not import anything",
    ),
]

single_rule_subject_multiple_rule_objects_error_message_test_cases = [
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should()
        .import_modules_that()
        .are_named([A, B]),
        f'"{C}" does not import "{A}", "{B}".',
        id="named should import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should()
        .import_modules_that()
        .are_sub_modules_of([A, B]),
        f'"{C}" does not import a sub module of "{A}", a sub module of "{B}".',
        id="named should import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should()
        .import_modules_that()
        .are_named([A]),
        f'Sub modules of "{C}" do not import "{A}".',
        id="submodule should import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should()
        .import_modules_that()
        .are_sub_modules_of([A]),
        f'Sub modules of "{C}" do not import a sub module of "{A}".',
        id="submodule should import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_that()
        .are_named([B, FILE_B2]),
        f'"{FILE_A}" imports "{FILE_C}".',
        id="named should only import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of([B, FILE_B2]),
        f'"{FILE_A}" imports "{FILE_C}".' + "\n" + f'"{FILE_A2}" imports "{FILE_C}".',
        id="named should only import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .are_named([B]),
        f'"{FILE_A}" imports "{FILE_C}".',
        id="submodule should only import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of([B]),
        f'"{FILE_A}" imports "{FILE_C}".' + "\n" + f'"{FILE_A2}" imports "{FILE_C}".',
        id="submodule should only import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .import_modules_that()
        .are_named([A, C]),
        f'"{FILE_B11}" imports "{FILE_A11}".',
        id="named should not import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of([A, C]),
        f'"{FILE_B11}" imports "{FILE_A11}".',
        id="named should not import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should_not()
        .import_modules_that()
        .are_named([A]),
        f'"{FILE_B11}" imports "{FILE_A11}".',
        id="submodule should not import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of([A]),
        f'"{FILE_B11}" imports "{FILE_A11}".',
        id="submodule should not import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_named([C, FILE_C]),
        f'"{FILE_A2}" does not import any module that is not "{C}".',
        id="named should import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_sub_modules_of([C, B]),
        f'"{FILE_A2}" does not import any module that is not a sub module of "{C}", a sub module of "{B}".',
        id="named should import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_named([C]),
        f'Sub modules of "{FILE_A2}" do not import any module that is not "{C}".',
        id="submodule should import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_sub_modules_of([C]),
        f'Sub modules of "{FILE_A2}" do not import any module that is not a sub module of "{C}".',
        id="submodule should import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([C, B]),
        f'"{FILE_A2}" imports "{FILE_C}".',
        id="named should only import except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of([C, B]),
        f'"{FILE_A2}" imports "{FILE_C}".',
        id="named should only import except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([C]),
        f'"{FILE_A2}" imports "{FILE_C}".',
        id="submodule should only import except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of([C]),
        f'"{FILE_A2}" imports "{FILE_C}".',
        id="submodule should only import except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([B, FILE_B2]),
        f'"{C}" does not import any module that is not "{B}".',
        id="named should only import except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of([B, FILE_B2]),
        f'"{C}" does not import any module that is not a sub module of "{B}".',
        id="named should only import except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_named([B]),
        f'Sub modules of "{C}" do not import any module that is not "{B}".',
        id="submodule should only import except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of([B]),
        f'Sub modules of "{C}" do not import any module that is not a sub module of "{B}".',
        id="submodule should only import except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_named([B, FILE_B2]),
        f'"{FILE_A}" imports "{FILE_C}".',
        id="named should not import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_sub_modules_of([B, FILE_B2]),
        f'"{FILE_A}" imports "{FILE_C}".' + "\n" + f'"{FILE_A2}" imports "{FILE_C}"',
        id="named should not import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_named([B]),
        f'"{FILE_A}" imports "{FILE_C}".',
        id="submodule should not import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_sub_modules_of([B]),
        f'"{FILE_A}" imports "{FILE_C}".' + "\n" + f'"{FILE_A2}" imports "{FILE_C}".',
        id="submodule should not import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should()
        .be_imported_by_modules_that()
        .are_named([C, FILE_C]),
        f'"{A}" is not imported by "{C}", "{FILE_C}".',
        id="named should be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of([C, FILE_C]),
        f'"{A}" is not imported by a sub module of "{C}", a sub module of "{FILE_C}".',
        id="named should be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .be_imported_by_modules_that()
        .are_named([C]),
        f'Sub modules of "{A}" are not imported by "{C}".',
        id="submodule should be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of([C]),
        f'Sub modules of "{A}" are not imported by a sub module of "{C}".',
        id="submodule should be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named([B, FILE_B2]),
        f'"{C}" is not imported by "{B}", "{FILE_B2}".',
        id="named should only be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of([B]),
        f'"{C}" is not imported by a sub module of "src.moduleB',
        id="named should only be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named([B]),
        f'Sub modules of "{C}" are not imported by "{B}".',
        id="submodule should only be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of([B]),
        f'Sub modules of "{C}" are not imported by a sub module of "{B}".',
        id="submodule should only be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_named([A, FILE_A2]),
        f'"{FILE_C}" is imported by "{FILE_A}".'
        + "\n"
        + f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="named should not be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of([A]),
        f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="named should not be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_named([A]),
        f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="submodule should not be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of([A]),
        f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="submodule should not be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named([A, A2]),
        f'"{B}" is not imported by any module that is not "{A}", "{A2}".',
        id="named should be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([A]),
        f'"{B}" is not imported by any module that is not a sub module of "{A}".',
        id="named should be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named([A]),
        f'Sub modules of "{B}" are not imported by any module that is not "{A}".',
        id="submodule should be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([A]),
        f'Sub modules of "{B}" are not imported by any module that is not a sub module of "{A}".',
        id="submodule should be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([FILE_B2, B]),
        f'"{FILE_A11}" is imported by "{FILE_B2}".',
        id="named should only be imported by except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([B1, B]),
        f'"{FILE_A11}" is imported by "{FILE_B11}".',
        id="named should only be imported by except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([FILE_B2]),
        f'"{FILE_A11}" is imported by "{FILE_B2}".',
        id="submodule should only be imported by except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A1)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([B1]),
        f'"{FILE_A11}" is imported by "{FILE_B11}".',
        id="submodule should only be imported by except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([B, FILE_B2]),
        f'"{A}" is not imported by any module that is not "{B}", "{FILE_B2}".',
        id="named should only be imported by except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([B]),
        f'"{A}" is not imported by any module that is not a sub module of "{B}"',
        id="named should only be imported by except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([B]),
        f'Sub modules of "{A}" are not imported by any module that is not "{B}"',
        id="submodule should only be imported by except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([B]),
        f'Sub modules of "{A}" are not imported by any module that is not a sub module of "{B}"',
        id="submodule should only be imported by except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named([FILE_A2, B]),
        f'"{FILE_C}" is imported by "{FILE_A}".',
        id="named should not be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([A2]),
        f'"{FILE_C}" is imported by "{FILE_A}".',
        id="named should not be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named([A2]),
        f'"{FILE_C}" is imported by "{FILE_A}".',
        id="submodule should not be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of([FILE_A2]),
        f'"{FILE_C}" is imported by "{FILE_A}".'
        + "\n"
        + f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="submodule should not be imported by except submodule",
    ),
]


multiple_rule_subjects_multiple_rule_objects_error_message_test_cases = [
    pytest.param(
        Rule()
        .modules_that()
        .are_named([FILE_B2, FILE_B1])
        .should_only()
        .import_modules_that()
        .are_named([A]),
        f'"{FILE_B1}" does not import "{A}".',
        id="one subject violates should only rule -- no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A, A2])
        .should_only()
        .import_modules_that()
        .are_named([C]),
        f'"{FILE_A11}" imports "{FILE_B1}".',
        id="one subject violates should only rule -- forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A, C])
        .should_only()
        .import_modules_that()
        .are_named([B]),
        f'"{FILE_A}" imports "{FILE_C}".\n'
        f'"{FILE_A2}" imports "{FILE_C}".\n'
        f'"{C}" does not import "{B}".',
        id="both subjects violate should only rule -- one forbidden one missing import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A, C])
        .should()
        .import_modules_that()
        .are_named([B]),
        f'"{C}" does not import "{B}".',
        id="one subject violates should rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([FILE_C, C])
        .should()
        .import_modules_that()
        .are_named([B]),
        f'"{C}" does not import "{B}".\n' f'"{FILE_C}" does not import "{B}".',
        id="two subjects violate should rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A, B])
        .should_not()
        .import_modules_that()
        .are_named([C]),
        f'"{FILE_A}" imports "{FILE_C}".\n' f'"{FILE_A2}" imports "{FILE_C}".',
        id="one subject violates should_not rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([B, FILE_B2])
        .should_not()
        .import_modules_that()
        .are_named([A]),
        f'"{FILE_B}" imports "{FILE_A11}".\n'
        f'"{FILE_B2}" imports "{FILE_A11}".\n'
        f'"{FILE_B11}" imports "{FILE_A11}".',
        id="two subjects violate should_not rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A2, C])
        .should_only()
        .import_modules_except_modules_that()
        .are_named([C]),
        f'"{C}" does not import any module that is not "{C}".',
        id="one subject violates should_only except rule -- no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([B, C])
        .should_only()
        .import_modules_except_modules_that()
        .are_named([B]),
        f'"{C}" does not import any module that is not "{B}".',
        id="two subjects violate should_only except rule -- no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([B, C])
        .should_only()
        .import_modules_except_modules_that()
        .are_named([A]),
        f'"{B}" does not import any module that is not "{A}".\n'
        f'"{FILE_B}" imports "{FILE_A11}".\n'
        f'"{FILE_B2}" imports "{FILE_A11}".\n'
        f'"{FILE_B11}" imports "{FILE_A11}".\n'
        f'"{C}" does not import any module that is not "{A}".',
        id="two subjects violate should_only except rule -- no import and forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A11, A2])
        .should()
        .import_modules_except_modules_that()
        .are_named([FILE_B1]),
        f'"{A11}" does not import any module that is not "{FILE_B1}".',
        id="one subject violates should except rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([B, C])
        .should()
        .import_modules_except_modules_that()
        .are_named([A]),
        f'"{B}" does not import any module that is not "{A}".\n'
        f'"{C}" does not import any module that is not "{A}".',
        id="two subjects violate should except rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A2, FILE_B2])
        .should_not()
        .import_modules_except_modules_that()
        .are_named([C]),
        f'"{FILE_B2}" imports "{FILE_A11}".',
        id="one subject violates should_not except rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A, FILE_B2])
        .should_not()
        .import_modules_except_modules_that()
        .are_named([C]),
        f'"{FILE_A11}" imports "{FILE_B1}".\n' f'"{FILE_B2}" imports "{FILE_A11}".',
        id="two subjects violate should_not except rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([FILE_B2, FILE_A11])
        .should_only()
        .be_imported_by_modules_that()
        .are_named([B]),
        f'"{FILE_B2}" is not imported by "{B}".',
        id="one subject violates should only be imported rule -- no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A, C])
        .should()
        .be_imported_by_modules_that()
        .are_named([B]),
        f'"{C}" is not imported by "{B}".',
        id="one subject violates should be imported rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A, B])
        .should()
        .be_imported_by_modules_that()
        .are_named([C]),
        f'"{A}" is not imported by "{C}".\n' f'"{B}" is not imported by "{C}".',
        id="two subjects violate should be imported rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A, C])
        .should_not()
        .be_imported_by_modules_that()
        .are_named([B]),
        f'"{FILE_A11}" is imported by "{FILE_B}".\n'
        f'"{FILE_A11}" is imported by "{FILE_B2}".',
        id="one subject violates should_not be imported rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([B, C])
        .should_not()
        .be_imported_by_modules_that()
        .are_named([A]),
        f'"{FILE_B1}" is imported by "{FILE_A11}".\n'
        f'"{FILE_C}" is imported by "{FILE_A}".\n'
        f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="two subjects violate should_not be imported rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([B, A11])
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named([A]),
        f'"{B}" is not imported by any module that is not "{A}".',
        id="one subject violates should_only except be imported rule -- no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A, FILE_B11])
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named([C]),
        f'"{FILE_B11}" is not imported by any module that is not "{C}".',
        id="one subject violates should except be imported rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A2, B])
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named([C]),
        f'"{A2}" is not imported by any module that is not "{C}".',
        id="two subjects violate should except be imported rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([B, C])
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named([A11]),
        f'"{FILE_C}" is imported by "{FILE_A}".\n'
        f'"{FILE_C}" is imported by "{FILE_A2}".',
        id="one subject violates should_not except be imported rule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([A, B])
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named([C]),
        f'"{FILE_A11}" is imported by "{FILE_B}".\n'
        f'"{FILE_A11}" is imported by "{FILE_B2}".\n'
        f'"{FILE_A11}" is imported by "{FILE_B11}".\n'
        f'"src.moduleB.submoduleB1.fileB1" is imported by "{FILE_A11}".',
        id="two subjects violate should_not except be imported rule",
    ),
]

TEST_PROJECT_IMPORTER_IMPORTEE = "flat_test_project_1.importer.importer_importee"
TEST_PROJECT_SERVICES = "flat_test_project_1.services"
TEST_PROJECT_SERVICES_IMPORTER = "flat_test_project_1.services.services_importer"
TEST_PROJECT_RUNTIME = "flat_test_project_1.runtime"
TEST_PROJECT_ORCHESTRATION = "flat_test_project_1.orchestration"
additional_multiple_rule_subjects_multiple_rule_objects_error_message_test_cases = [
    pytest.param(
        Rule()
        .modules_that()
        .are_named([TEST_PROJECT_IMPORTER, TEST_PROJECT_EXPORTER])
        .should_only()
        .be_imported_by_modules_that()
        .are_named(f"{TEST_PROJECT_ORCHESTRATION}"),
        f'"{TEST_PROJECT_IMPORTER_IMPORTEE}" is imported by "{TEST_PROJECT_SERVICES_IMPORTER}".',
        id="one subject violates should only be imported rule -- forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([TEST_PROJECT_IMPORTER, TEST_PROJECT_RUNTIME])
        .should_only()
        .be_imported_by_modules_that()
        .are_named(f"{TEST_PROJECT_ORCHESTRATION}"),
        f'"{TEST_PROJECT_IMPORTER_IMPORTEE}" is imported by "{TEST_PROJECT_SERVICES_IMPORTER}".\n'
        f'"{TEST_PROJECT_RUNTIME}" is not imported by "{TEST_PROJECT_ORCHESTRATION}".',
        id="both subjects violate should only be imported rule -- one forbidden one missing import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([TEST_PROJECT_IMPORTER, TEST_PROJECT_EXPORTER])
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(f"{TEST_PROJECT_SERVICES}"),
        f'"{TEST_PROJECT_IMPORTER_IMPORTEE}" is imported by "{TEST_PROJECT_SERVICES_IMPORTER}".',
        id="one subject violates should_only except be imported rule -- forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named([TEST_PROJECT_IMPORTER, TEST_PROJECT_RUNTIME])
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(f"{TEST_PROJECT_SERVICES}"),
        f'"{TEST_PROJECT_IMPORTER_IMPORTEE}" is imported by "{TEST_PROJECT_SERVICES_IMPORTER}".\n'
        f'"{TEST_PROJECT_RUNTIME}" is not imported by any module that is not "{TEST_PROJECT_SERVICES}".',
        id="two subjects violate should_only except be imported rule --- no import and forbidden import",
    ),
]

partial_name_match_test_cases = [
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("*moduleC*")
        .should()
        .import_modules_that()
        .are_sub_modules_of([A, B]),
        True,
        id="named should import submodule - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .have_name_containing("*leB*"),
        True,
        id="submodule should only import named - partial name match object",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("*moduleB")
        .should_not()
        .import_modules_that()
        .are_named([A, C]),
        True,
        id="named should not import named - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("src.moduleA*")
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of([C, B]),
        True,
        id="named should only import except submodule - forbidden import - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .have_name_containing("*moduleB*"),
        True,
        id="submodule should only import except named - no import - partial name match object",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("*duleA*")
        .should_not()
        .import_modules_except_modules_that()
        .are_named([B, FILE_B2]),
        True,
        id="named should not import except named - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("*moduleA*")
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of([C, FILE_C]),
        True,
        id="named should be imported by submodule - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .have_name_containing(["*leB"]),
        True,
        id="submodule should only be imported by named - partial name match object",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .have_name_containing("*moduleC*")
        .should_not()
        .be_imported_by_modules_that()
        .are_named([A, FILE_A2]),
        True,
        id="named should not be imported by named - partial name match subject",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .have_name_containing(["*fileB2"]),
        True,
        id="submodule should only be imported by except named - forbidden import - partial name match object",
    ),
]
