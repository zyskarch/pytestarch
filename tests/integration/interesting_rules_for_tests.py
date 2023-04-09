from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List, Optional

import pytest
from _pytest.mark import ParameterSet

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
        f'"{FILE_A2}" does not import any module that is not a sub module of "{B}", a sub module of "{C}".',
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


@dataclass
class LayerRuleTestCase:
    layers: Dict[str, List[str]]
    rule_setup: LayerRuleSetup
    expected_error_message: Optional[str] = None


@dataclass
class LayerRuleSetup:
    behavior: str
    access_type: str
    importer: str
    importee: List[str]


PROJECT_ROOT = "flat_test_project_1"
EXPORTER = f"{PROJECT_ROOT}.exporter"
IMPORTER = f"{PROJECT_ROOT}.importer"
LOGGING = f"{PROJECT_ROOT}.logging_util"
MODEL = f"{PROJECT_ROOT}.model"
ORCHESTRATION = f"{PROJECT_ROOT}.orchestration"
PERSISTENCE = f"{PROJECT_ROOT}.persistence"
RUNTIME = f"{PROJECT_ROOT}.runtime"
SERVICES = f"{PROJECT_ROOT}.services"
SIMULATION = f"{PROJECT_ROOT}.simulation"
UTIL = f"{PROJECT_ROOT}.util"

LAYER_1 = "L1"
LAYER_2 = "L2"
LAYER_3 = "L3"
LAYER_4 = "L4"

layer_1_should_access_layer_2 = LayerRuleSetup(
    "should", "access_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_access_layer_2_and_3 = LayerRuleSetup(
    "should", "access_layers_that", LAYER_1, [LAYER_2, LAYER_3]
)

layer_1_should_not_access_layer_2 = LayerRuleSetup(
    "should_not", "access_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_not_access_layer_2_and_3 = LayerRuleSetup(
    "should_not", "access_layers_that", LAYER_1, [LAYER_2, LAYER_3]
)
layer_1_should_not_access_anything = LayerRuleSetup(
    "should_not", "access_any_layer", LAYER_1, []
)

layer_1_should_only_access_layer_2 = LayerRuleSetup(
    "should_only", "access_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_only_access_layer_2_and_3 = LayerRuleSetup(
    "should_only", "access_layers_that", LAYER_1, [LAYER_2, LAYER_3]
)

layer_1_should_access_except_layer_2 = LayerRuleSetup(
    "should", "access_layers_except_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_access_except_layer_2_and_3 = LayerRuleSetup(
    "should", "access_layers_except_layers_that", LAYER_1, [LAYER_2, LAYER_3]
)

layer_1_should_not_access_except_layer_2 = LayerRuleSetup(
    "should_not", "access_layers_except_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_not_access_except_layer_2_and_3 = LayerRuleSetup(
    "should_not", "access_layers_except_layers_that", LAYER_1, [LAYER_2, LAYER_3]
)

layer_1_should_only_access_except_layer_2 = LayerRuleSetup(
    "should_only", "access_layers_except_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_only_access_except_layer_2_and_3 = LayerRuleSetup(
    "should_only", "access_layers_except_layers_that", LAYER_1, [LAYER_2, LAYER_3]
)

layer_1_should_be_accessed_by_layer_2 = LayerRuleSetup(
    "should", "be_accessed_by_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_be_accessed_by_layer_2_and_3 = LayerRuleSetup(
    "should", "be_accessed_by_layers_that", LAYER_1, [LAYER_2, LAYER_3]
)

layer_1_should_not_be_accessed_by_layer_2 = LayerRuleSetup(
    "should_not", "be_accessed_by_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_not_be_accessed_by_layer_2_and_3 = LayerRuleSetup(
    "should_not", "be_accessed_by_layers_that", LAYER_1, [LAYER_2, LAYER_3]
)
layer_1_should_not_be_accessed_by_anything = LayerRuleSetup(
    "should_not", "be_accessed_by_any_layer", LAYER_1, []
)

layer_1_should_only_be_accessed_by_layer_2 = LayerRuleSetup(
    "should_only", "be_accessed_by_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_only_be_accessed_by_layer_2_and_3 = LayerRuleSetup(
    "should_only", "be_accessed_by_layers_that", LAYER_1, [LAYER_2, LAYER_3]
)

layer_1_should_be_accessed_except_by_layer_2 = LayerRuleSetup(
    "should", "be_accessed_by_layers_except_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_be_accessed_except_by_layer_2_and_3 = LayerRuleSetup(
    "should", "be_accessed_by_layers_except_layers_that", LAYER_1, [LAYER_2, LAYER_3]
)

layer_1_should_not_be_accessed_except_by_layer_2 = LayerRuleSetup(
    "should_not", "be_accessed_by_layers_except_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_not_be_accessed_except_by_layer_2_and_3 = LayerRuleSetup(
    "should_not",
    "be_accessed_by_layers_except_layers_that",
    LAYER_1,
    [LAYER_2, LAYER_3],
)

layer_1_should_only_be_accessed_except_by_layer_2 = LayerRuleSetup(
    "should_only", "be_accessed_by_layers_except_layers_that", LAYER_1, [LAYER_2]
)
layer_1_should_only_be_accessed_except_by_layer_2_and_3 = LayerRuleSetup(
    "should_only",
    "be_accessed_by_layers_except_layers_that",
    LAYER_1,
    [LAYER_2, LAYER_3],
)


fulfilled_layer_rule_test_cases_access = [
    # access
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [EXPORTER], LAYER_2: [LOGGING]}, layer_1_should_access_layer_2
        ),
        id="should_fulfilled_one_import",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [EXPORTER, MODEL], LAYER_2: [LOGGING]},
            layer_1_should_access_layer_2,
        ),
        id="should_fulfilled_one_import_by_one_module",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [EXPORTER, ORCHESTRATION], LAYER_2: [LOGGING]},
            layer_1_should_access_layer_2,
        ),
        id="should_fulfilled_one_import_by_all_modules_in_layer",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [EXPORTER], LAYER_2: [LOGGING, MODEL]},
            layer_1_should_access_layer_2,
        ),
        id="should_fulfilled_multiple_imports_by_one_module_two_layers",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [EXPORTER, ORCHESTRATION], LAYER_2: [LOGGING, SIMULATION]},
            layer_1_should_access_layer_2,
        ),
        id="should_fulfilled_multiple_imports_by_different_modules_two_layers",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [EXPORTER], LAYER_2: [LOGGING], LAYER_3: [MODEL]},
            layer_1_should_access_layer_2_and_3,
        ),
        id="should_fulfilled_multiple_imports_by_one_module_three_layers",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [EXPORTER, ORCHESTRATION],
                LAYER_2: [LOGGING],
                LAYER_3: [SIMULATION],
            },
            layer_1_should_access_layer_2_and_3,
        ),
        id="should_fulfilled_multiple_imports_by_different_modules_three_layers",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [UTIL], LAYER_2: [MODEL]}, layer_1_should_not_access_layer_2
        ),
        id="should_not_fulfilled_no_imports",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [UTIL], LAYER_2: [MODEL, SIMULATION]},
            layer_1_should_not_access_layer_2,
        ),
        id="should_not_fulfilled_no_imports_multiple_modules_in_layer",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [UTIL], LAYER_2: [MODEL], LAYER_3: [SIMULATION]},
            layer_1_should_not_access_layer_2_and_3,
        ),
        id="should_not_fulfilled_no_imports_multiple_rule_objects",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [SIMULATION]},
            layer_1_should_not_access_layer_2,
        ),
        id="should_not_fulfilled_import_of_other_layer",
    ),
    pytest.param(
        LayerRuleTestCase({LAYER_1: [MODEL]}, layer_1_should_not_access_anything),
        id="should_not_fulfilled_import_anything",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [RUNTIME],
                LAYER_2: [PERSISTENCE, LOGGING, UTIL, ORCHESTRATION, SERVICES],
            },
            layer_1_should_only_access_layer_2,
        ),
        id="should_only_fulfilled_one_import",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [RUNTIME],
                LAYER_2: [PERSISTENCE, LOGGING, UTIL, ORCHESTRATION],
                LAYER_3: [SERVICES],
            },
            layer_1_should_only_access_layer_2_and_3,
        ),
        id="should_only_fulfilled_one_import_multiple_rule_objects",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [RUNTIME, ORCHESTRATION],
                LAYER_2: [
                    PERSISTENCE,
                    LOGGING,
                    UTIL,
                    SERVICES,
                    EXPORTER,
                    MODEL,
                    SIMULATION,
                    IMPORTER,
                ],
            },
            layer_1_should_only_access_layer_2,
        ),
        id="should_only_fulfilled_multiple_imports_by_different_modules",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [RUNTIME],
                LAYER_2: [LOGGING, PERSISTENCE, UTIL, MODEL, ORCHESTRATION],
            },
            layer_1_should_access_except_layer_2,
        ),
        id="should_except_fulfilled_one_other_import",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [RUNTIME],
                LAYER_2: [LOGGING, PERSISTENCE, UTIL],
                LAYER_3: [ORCHESTRATION],
            },
            layer_1_should_access_except_layer_2_and_3,
        ),
        id="should_except_fulfilled_one_other_import_multiple_rule_objects",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [RUNTIME, IMPORTER],
                LAYER_2: [LOGGING, UTIL],
                LAYER_3: [ORCHESTRATION],
            },
            layer_1_should_access_except_layer_2,
        ),
        id="should_except_fulfilled_multiple_other_imports_by_one_module",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [UTIL], LAYER_2: [MODEL]},
            layer_1_should_not_access_except_layer_2,
        ),
        id="should_not_except_fulfilled_no_other_imports",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SIMULATION, UTIL, MODEL], LAYER_2: [LOGGING]},
            layer_1_should_not_access_except_layer_2,
        ),
        id="should_not_except_fulfilled_one_import",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [SIMULATION, UTIL, MODEL],
                LAYER_2: [LOGGING],
                LAYER_3: [SERVICES],
            },
            layer_1_should_not_access_except_layer_2_and_3,
        ),
        id="should_not_except_fulfilled_one_import_multiple_rule_objects",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [EXPORTER, IMPORTER, LOGGING], LAYER_2: [MODEL, UTIL]},
            layer_1_should_not_access_except_layer_2,
        ),
        id="should_not_except_fulfilled_multiple_imports",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [IMPORTER], LAYER_2: [LOGGING]},
            layer_1_should_only_access_except_layer_2,
        ),
        id="should_only_except_fulfilled_one_other_import",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [IMPORTER], LAYER_2: [LOGGING], LAYER_3: [SIMULATION]},
            layer_1_should_only_access_except_layer_2_and_3,
        ),
        id="should_only_except_fulfilled_one_other_import_multiple_rule_objects",
    ),
]


fulfilled_layer_rule_test_cases_be_accessed = [
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES], LAYER_2: [RUNTIME]},
            layer_1_should_be_accessed_by_layer_2,
        ),
        id="should_fulfilled_one_be_imported",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES, PERSISTENCE], LAYER_2: [RUNTIME]},
            layer_1_should_be_accessed_by_layer_2,
        ),
        id="should_fulfilled_multiple_be_imported_by_one_module",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES, MODEL], LAYER_2: [RUNTIME, IMPORTER]},
            layer_1_should_be_accessed_by_layer_2,
        ),
        id="should_fulfilled_multiple_be_imported_by_different_modules",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES, MODEL], LAYER_2: [RUNTIME], LAYER_3: [IMPORTER]},
            layer_1_should_be_accessed_by_layer_2_and_3,
        ),
        id="should_fulfilled_multiple_be_imported_by_different_modules_per_rule_object",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [MODEL]},
            layer_1_should_not_be_accessed_by_layer_2,
        ),
        id="should_not_fulfilled_no_be_imported",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [MODEL, UTIL]},
            layer_1_should_not_be_accessed_by_layer_2,
        ),
        id="should_not_fulfilled_no_be_imported_multiple_modules_in_layer",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [MODEL], LAYER_3: [UTIL]},
            layer_1_should_not_be_accessed_by_layer_2_and_3,
        ),
        id="should_not_fulfilled_no_be_imported_multiple_rule_objects",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME, SIMULATION], LAYER_2: [MODEL]},
            layer_1_should_not_be_accessed_by_layer_2,
        ),
        id="should_not_fulfilled_be_imported_of_other_layer",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME]}, layer_1_should_not_be_accessed_by_anything
        ),
        id="should_not_fulfilled_be_imported_by_any_layer",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES], LAYER_2: [RUNTIME]},
            layer_1_should_only_be_accessed_by_layer_2,
        ),
        id="should_only_fulfilled_one_be_imported",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [PERSISTENCE, SIMULATION],
                LAYER_2: [RUNTIME, SERVICES],
                LAYER_3: [ORCHESTRATION],
            },
            layer_1_should_only_be_accessed_by_layer_2_and_3,
        ),
        id="should_only_fulfilled_one_be_imported_multiple_rule_objects",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [UTIL], LAYER_2: [SERVICES]},
            layer_1_should_be_accessed_except_by_layer_2,
        ),
        id="should_except_fulfilled_one_other_be_imported",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [UTIL], LAYER_2: [SERVICES], LAYER_3: [LOGGING]},
            layer_1_should_be_accessed_except_by_layer_2_and_3,
        ),
        id="should_except_fulfilled_one_other_be_imported_multiple_rule_objects",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [UTIL], LAYER_2: [SERVICES, LOGGING]},
            layer_1_should_be_accessed_except_by_layer_2,
        ),
        id="should_except_fulfilled_multiple_other_be_imported_by_one_module",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [UTIL, MODEL], LAYER_2: [SERVICES, IMPORTER]},
            layer_1_should_be_accessed_except_by_layer_2,
        ),
        id="should_except_fulfilled_multiple_other_be_imported_by_different_modules",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES], LAYER_2: [RUNTIME, EXPORTER]},
            layer_1_should_not_be_accessed_except_by_layer_2,
        ),
        id="should_not_except_fulfilled_no_other_be_imported",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES, EXPORTER], LAYER_2: [RUNTIME, ORCHESTRATION]},
            layer_1_should_not_be_accessed_except_by_layer_2,
        ),
        id="should_not_except_fulfilled_multiple_be_imported",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [SERVICES, EXPORTER],
                LAYER_2: [RUNTIME],
                LAYER_3: [ORCHESTRATION],
            },
            layer_1_should_not_be_accessed_except_by_layer_2_and_3,
        ),
        id="should_not_except_fulfilled_multiple_be_imported_rule_objects",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES], LAYER_2: [PERSISTENCE]},
            layer_1_should_only_be_accessed_except_by_layer_2,
        ),
        id="should_only_except_fulfilled_one_other_be_imported",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES], LAYER_2: [PERSISTENCE], LAYER_3: [SIMULATION]},
            layer_1_should_only_be_accessed_except_by_layer_2_and_3,
        ),
        id="should_only_except_fulfilled_one_other_be_imported_multiple_rule_objects",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES], LAYER_2: [PERSISTENCE, SIMULATION]},
            layer_1_should_only_be_accessed_except_by_layer_2,
        ),
        id="should_only_except_fulfilled_multiple_other_be_imported",
    ),
]


def _add_submodule_of_layer_1_module(parameter_set: ParameterSet) -> ParameterSet:
    id = parameter_set.id + "_submodule_and_parent_module_in_layer"

    values = deepcopy(parameter_set.values)

    current_modules_in_layer_1 = values[0].layers[LAYER_1]

    module_name_of_first_module = current_modules_in_layer_1[0].split(".")[1]

    values[0].layers[LAYER_1] = current_modules_in_layer_1 + [
        f"{current_modules_in_layer_1[0]}.{module_name_of_first_module}_importer"
    ]

    return ParameterSet.param(*values, id=id)


fulfilled_layer_rule_test_cases_submodule_and_module_in_layer_access = [
    _add_submodule_of_layer_1_module(parameter_set)
    for parameter_set in fulfilled_layer_rule_test_cases_access
]
fulfilled_layer_rule_test_cases_submodule_and_module_in_layer_be_accessed = [
    _add_submodule_of_layer_1_module(parameter_set)
    for parameter_set in fulfilled_layer_rule_test_cases_be_accessed
]

fulfilled_layer_rule_test_cases = (
    fulfilled_layer_rule_test_cases_access
    + fulfilled_layer_rule_test_cases_be_accessed
    + fulfilled_layer_rule_test_cases_submodule_and_module_in_layer_access
    + fulfilled_layer_rule_test_cases_submodule_and_module_in_layer_be_accessed
)


layer_1_does_not_import_layer_2 = (
    f'Layer "{LAYER_1}" does not import layer "{LAYER_2}".'
)
layer_1_does_not_import_layer_3 = (
    f'Layer "{LAYER_1}" does not import layer "{LAYER_3}".'
)
layer_1_does_not_import_any_layer_that_is_not_layer_2 = (
    f'Layer "{LAYER_1}" does not import any layer that is not layer "{LAYER_2}".'
)
layer_1_is_not_imported_by_layer_2 = (
    f'Layer "{LAYER_1}" is not imported by layer "{LAYER_2}".'
)
layer_1_is_not_imported_by_layer_3 = (
    f'Layer "{LAYER_1}" is not imported by layer "{LAYER_3}".'
)
layer_1_is_not_imported_by_any_layer_that_is_not_layer_2 = (
    f'Layer "{LAYER_1}" is not imported by any layer that is not layer "{LAYER_2}".'
)
layer_1_does_not_import_layer_2_3 = (
    f'Layer "{LAYER_1}" does not import layer "{LAYER_2}", layer "{LAYER_3}".'
)
layer_1_does_not_import_any_layer_that_is_not_layer_2_3 = f'Layer "{LAYER_1}" does not import any layer that is not layer "{LAYER_2}", layer "{LAYER_3}".'
layer_1_is_not_imported_by_layer_2_3 = (
    f'Layer "{LAYER_1}" is not imported by layer "{LAYER_2}", layer "{LAYER_3}".'
)
layer_1_is_not_imported_by_any_layer_that_is_not_layer_2_3 = f'Layer "{LAYER_1}" is not imported by any layer that is not layer "{LAYER_2}", layer "{LAYER_3}".'

EXPORTER_IMPORTER = f"{EXPORTER}.exporter_importer"
EXPORTER_IMPORTEE = f"{EXPORTER}.exporter_importee"
RUNTIME_IMPORTER = f"{RUNTIME}.runtime_importer"
SERVICES_IMPORTEE = f"{SERVICES}.services_importee"
UTIL_IMPORTEE = f"{UTIL}.util_importee"
PERSISTENCE_IMPORTEE = f"{PERSISTENCE}.persistence_importee"
PERSISTENCE_IMPORTER = f"{PERSISTENCE}.persistence_importer"
ORCHESTRATION_IMPORTEE = f"{ORCHESTRATION}.orchestration_importee"
ORCHESTRATION_IMPORTER = f"{ORCHESTRATION}.orchestration_importer"
LOGGING_IMPORTEE = f"{LOGGING}.logging_util_importee"
SIMULATION_IMPORTEE = f"{SIMULATION}.simulation_importee"
IMPORTER_IMPORTER = f"{IMPORTER}.importer_importer"
IMPORTER_IMPORTEE = f"{IMPORTER}.importer_importee"
MODEL_IMPORTEE = f"{MODEL}.model_importee"

runtime_imports_services_no_layer = f'"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{SERVICES_IMPORTEE}" (no layer).'
runtime_imports_services_layer_2 = f'"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{SERVICES_IMPORTEE}" (layer "{LAYER_2}").'


layer_rule_error_messages_test_cases_access = [
    # single rule subject single rule object
    # pytest.param(LayerRuleTestCase({LAYER_1: [UTIL], LAYER_2: [MODEL]}, layer_1_should_access_layer_2, layer_1_does_not_import_layer_2), id='should_violated_no_imports_ssso',),
    # pytest.param(LayerRuleTestCase({LAYER_1: [IMPORTER], LAYER_2: [LOGGING]}, layer_1_should_access_layer_2, layer_1_does_not_import_layer_2), id='should_violated_only_other_imports_ssso',),
    #
    # pytest.param(LayerRuleTestCase({LAYER_1: [RUNTIME], LAYER_2: [SERVICES]}, layer_1_should_not_access_layer_2, f'"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{SERVICES_IMPORTEE}" (layer "{LAYER_2}").'), id='should_not_violated_one_import_ssso',),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [
                    RUNTIME,
                    LOGGING,
                    PERSISTENCE,
                    UTIL,
                    ORCHESTRATION,
                    MODEL,
                    SIMULATION,
                    EXPORTER,
                    IMPORTER,
                ],
                LAYER_2: [],
            },
            layer_1_should_not_access_anything,
            f'"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{SERVICES_IMPORTEE}" (no layer).',
        ),
        id="should_not_anything_violated_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [UTIL], LAYER_2: [MODEL]},
            layer_1_should_only_access_layer_2,
            layer_1_does_not_import_layer_2,
        ),
        id="should_only_violated_no_imports_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [EXPORTER]},
            layer_1_should_only_access_layer_2,
            layer_1_does_not_import_layer_2,
        ),
        id="should_only_violated_only_imports_of_other_layers_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [SERVICES]},
            layer_1_should_only_access_layer_2,
            f'"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{LOGGING_IMPORTEE}" (no layer).\n"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{ORCHESTRATION_IMPORTEE}" (no layer).\n"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{PERSISTENCE_IMPORTEE}" (no layer).\n"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{UTIL_IMPORTEE}" (no layer).',
        ),
        id="should_only_violated_also_imports_of_other_layers_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [IMPORTER], LAYER_2: [MODEL, UTIL]},
            layer_1_should_access_except_layer_2,
            layer_1_does_not_import_any_layer_that_is_not_layer_2,
        ),
        id="should_except_violated_no_other_import_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES], LAYER_2: [PERSISTENCE, MODEL, UTIL, IMPORTER]},
            layer_1_should_access_except_layer_2,
            layer_1_does_not_import_any_layer_that_is_not_layer_2,
        ),
        id="should_except_violated_only_import_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [SIMULATION, IMPORTER, LOGGING, PERSISTENCE]},
            layer_1_should_not_access_except_layer_2,
            runtime_imports_services_no_layer,
        ),
        id="should_not_except_violated_other_import_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [SIMULATION, IMPORTER, ORCHESTRATION]},
            layer_1_should_not_access_except_layer_2,
            runtime_imports_services_no_layer,
        ),
        id="should_not_except_violated_import_and_other_import_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [SERVICES, MODEL]},
            layer_1_should_only_access_except_layer_2,
            f'"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{SERVICES_IMPORTEE}" (layer "{LAYER_2}").',
        ),
        id="should_only_except_violated_import_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES], LAYER_2: [MODEL, PERSISTENCE, IMPORTER, UTIL]},
            layer_1_should_only_access_except_layer_2,
            layer_1_does_not_import_any_layer_that_is_not_layer_2,
        ),
        id="should_only_except_violated_no_other_import_ssso",
    ),
    # single rule subject multiple rule objects
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [UTIL], LAYER_2: [MODEL], LAYER_3: [LOGGING]},
            layer_1_should_access_layer_2_and_3,
            layer_1_does_not_import_layer_2_3,
        ),
        id="should_violated_no_imports_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [EXPORTER], LAYER_2: [IMPORTER], LAYER_3: [LOGGING]},
            layer_1_should_access_layer_2_and_3,
            layer_1_does_not_import_layer_2,
        ),
        id="should_violated_one_object_correct_one_object_no_import_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [EXPORTER, MODEL], LAYER_2: [IMPORTER], LAYER_3: [PERSISTENCE]},
            layer_1_should_access_layer_2_and_3,
            layer_1_does_not_import_layer_2_3,
        ),
        id="should_violated_only_other_imports_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [IMPORTER], LAYER_2: [MODEL], LAYER_3: [UTIL]},
            layer_1_should_not_access_layer_2_and_3,
            f'"{IMPORTER_IMPORTER}" (layer "{LAYER_1}") imports "{MODEL_IMPORTEE}" (layer "{LAYER_2}").\n"{IMPORTER_IMPORTER}" (layer "{LAYER_1}") imports "{UTIL_IMPORTEE}" (layer "{LAYER_3}").',
        ),
        id="should_not_violated_both_one_import_sssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [IMPORTER, PERSISTENCE], LAYER_2: [EXPORTER], LAYER_3: [UTIL]},
            layer_1_should_not_access_layer_2_and_3,
            f'"{IMPORTER_IMPORTER}" (layer "{LAYER_1}") imports "{UTIL_IMPORTEE}" (layer "{LAYER_3}").\n"{PERSISTENCE_IMPORTER}" (layer "{LAYER_1}") imports "{UTIL_IMPORTEE}" (layer "{LAYER_3}").',
        ),
        id="should_not_violated_one_object_correct_one_import_sssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [RUNTIME],
                LAYER_2: [SERVICES, PERSISTENCE, UTIL, ORCHESTRATION],
                LAYER_3: [SIMULATION],
            },
            layer_1_should_only_access_layer_2_and_3,
            layer_1_does_not_import_layer_3,
        ),
        id="should_only_violated_only_one_rule_object_imported",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [SERVICES, SIMULATION], LAYER_3: [EXPORTER]},
            layer_1_should_only_access_layer_2_and_3,
            layer_1_does_not_import_layer_3,
        ),
        id="should_only_violated_also_imports_of_other_layers_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME, SERVICES], LAYER_2: [SIMULATION], LAYER_3: [EXPORTER]},
            layer_1_should_only_access_layer_2_and_3,
            layer_1_does_not_import_layer_2_3,
        ),
        id="should_only_violated_only_imports_of_other_layers_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [LOGGING], LAYER_2: [MODEL], LAYER_3: [UTIL]},
            layer_1_should_access_except_layer_2_and_3,
            layer_1_does_not_import_any_layer_that_is_not_layer_2_3,
        ),
        id="should_except_violated_no_imports_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [IMPORTER, EXPORTER], LAYER_2: [MODEL, LOGGING], LAYER_3: [UTIL]},
            layer_1_should_access_except_layer_2_and_3,
            layer_1_does_not_import_any_layer_that_is_not_layer_2_3,
        ),
        id="should_except_violated_only_import_no_other_imports_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [SERVICES, PERSISTENCE], LAYER_3: [UTIL]},
            layer_1_should_not_access_except_layer_2_and_3,
            f'"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{LOGGING_IMPORTEE}" (no layer).\n"{RUNTIME_IMPORTER}" (layer "{LAYER_1}") imports "{ORCHESTRATION_IMPORTEE}" (no layer).',
        ),
        id="should_not_except_violated_other_import_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [IMPORTER, SERVICES], LAYER_2: [MODEL], LAYER_3: [RUNTIME]},
            layer_1_should_only_access_except_layer_2_and_3,
            f'"{IMPORTER_IMPORTER}" (layer "{LAYER_1}") imports "{MODEL_IMPORTEE}" (layer "{LAYER_2}").',
        ),
        id="should_only_except_violated_one_import_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [IMPORTER], LAYER_2: [MODEL, SERVICES], LAYER_3: [UTIL]},
            layer_1_should_only_access_except_layer_2_and_3,
            f'"{IMPORTER_IMPORTER}" (layer "{LAYER_1}") imports "{MODEL_IMPORTEE}" (layer "{LAYER_2}").\n"{IMPORTER_IMPORTER}" (layer "{LAYER_1}") imports "{UTIL_IMPORTEE}" (layer "{LAYER_3}").',
        ),
        id="should_only_except_violated_multiple_imports_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [SERVICES],
                LAYER_2: [MODEL, IMPORTER, PERSISTENCE],
                LAYER_3: [UTIL, RUNTIME],
            },
            layer_1_should_only_access_except_layer_2_and_3,
            layer_1_does_not_import_any_layer_that_is_not_layer_2_3,
        ),
        id="should_only_except_violated_no_other_import_ssmo",
    ),
]

layer_rule_error_messages_test_cases_be_accessed = [
    # single rule subject single rule object
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [SIMULATION]},
            layer_1_should_be_accessed_by_layer_2,
            layer_1_is_not_imported_by_layer_2,
        ),
        id="should_violated_no_be_imported_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [LOGGING, ORCHESTRATION], LAYER_2: [PERSISTENCE, SERVICES]},
            layer_1_should_be_accessed_by_layer_2,
            layer_1_is_not_imported_by_layer_2,
        ),
        id="should_violated_only_other_be_imported_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [PERSISTENCE, UTIL], LAYER_2: [RUNTIME]},
            layer_1_should_not_be_accessed_by_layer_2,
            f'"{PERSISTENCE_IMPORTEE}" (layer "{LAYER_1}") is imported by "{RUNTIME_IMPORTER}" (layer "{LAYER_2}").\n"{UTIL_IMPORTEE}" (layer "{LAYER_1}") is imported by "{RUNTIME_IMPORTER}" (layer "{LAYER_2}").',
        ),
        id="should_not_violated_one_be_imported_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [ORCHESTRATION], LAYER_2: []},
            layer_1_should_not_be_accessed_by_anything,
            f'"{ORCHESTRATION_IMPORTEE}" (layer "{LAYER_1}") is imported by "{RUNTIME_IMPORTER}" (no layer).',
        ),
        id="should_not_be_imported_by_anything_violated_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [EXPORTER]},
            layer_1_should_only_be_accessed_by_layer_2,
            layer_1_is_not_imported_by_layer_2,
        ),
        id="should_only_violated_no_be_imported_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME, SERVICES], LAYER_2: [EXPORTER]},
            layer_1_should_only_be_accessed_by_layer_2,
            layer_1_is_not_imported_by_layer_2,
        ),
        id="should_only_violated_only_be_imported_of_other_layers_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [PERSISTENCE, SIMULATION], LAYER_2: [RUNTIME]},
            layer_1_should_only_be_accessed_by_layer_2,
            f'"{SIMULATION_IMPORTEE}" (layer "{LAYER_1}") is imported by "{ORCHESTRATION_IMPORTER}" (no layer).',
        ),
        id="should_only_violated_also_be_imported_of_other_layers_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [MODEL]},
            layer_1_should_be_accessed_except_by_layer_2,
            layer_1_is_not_imported_by_any_layer_that_is_not_layer_2,
        ),
        id="should_except_violated_no_other_be_imported_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES], LAYER_2: [MODEL, RUNTIME]},
            layer_1_should_be_accessed_except_by_layer_2,
            layer_1_is_not_imported_by_any_layer_that_is_not_layer_2,
        ),
        id="should_except_violated_only_be_imported_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [ORCHESTRATION], LAYER_2: [MODEL, EXPORTER]},
            layer_1_should_not_be_accessed_except_by_layer_2,
            f'"{ORCHESTRATION_IMPORTEE}" (layer "{LAYER_1}") is imported by "{RUNTIME_IMPORTER}" (no layer).',
        ),
        id="should_not_except_violated_other_be_imported_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [LOGGING], LAYER_2: [RUNTIME, SIMULATION, ORCHESTRATION]},
            layer_1_should_not_be_accessed_except_by_layer_2,
            f'"{LOGGING_IMPORTEE}" (layer "{LAYER_1}") is imported by "{EXPORTER_IMPORTER}" (no layer).',
        ),
        id="should_not_except_violated_be_imported_and_other_be_imported_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SIMULATION, LOGGING], LAYER_2: [RUNTIME]},
            layer_1_should_only_be_accessed_except_by_layer_2,
            f'"{LOGGING_IMPORTEE}" (layer "{LAYER_1}") is imported by "{RUNTIME_IMPORTER}" (layer "{LAYER_2}").',
        ),
        id="should_only_except_violated_be_imported_ssso",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [ORCHESTRATION, SIMULATION]},
            layer_1_should_only_be_accessed_except_by_layer_2,
            layer_1_is_not_imported_by_any_layer_that_is_not_layer_2,
        ),
        id="should_only_except_violated_no_other_be_imported_ssso",
    ),
    # single rule subject multiple rule objects
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [SERVICES], LAYER_3: [ORCHESTRATION]},
            layer_1_should_be_accessed_by_layer_2_and_3,
            layer_1_is_not_imported_by_layer_2_3,
        ),
        id="should_violated_no_be_imported_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [IMPORTER, SERVICES],
                LAYER_2: [ORCHESTRATION],
                LAYER_3: [EXPORTER],
            },
            layer_1_should_be_accessed_by_layer_2_and_3,
            layer_1_is_not_imported_by_layer_3,
        ),
        id="should_violated_one_object_correct_one_object_no_import",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [MODEL], LAYER_2: [EXPORTER], LAYER_3: [IMPORTER]},
            layer_1_should_not_be_accessed_by_layer_2_and_3,
            f'"{MODEL_IMPORTEE}" (layer "{LAYER_1}") is imported by "{EXPORTER_IMPORTER}" (layer "{LAYER_2}").\n"{MODEL_IMPORTEE}" (layer "{LAYER_1}") is imported by "{IMPORTER_IMPORTER}" (layer "{LAYER_3}").',
        ),
        id="should_not_violated_both_one_be_imported_sssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [MODEL, UTIL], LAYER_2: [EXPORTER], LAYER_3: [LOGGING]},
            layer_1_should_not_be_accessed_by_layer_2_and_3,
            f'"{MODEL_IMPORTEE}" (layer "{LAYER_1}") is imported by "{EXPORTER_IMPORTER}" (layer "{LAYER_2}").\n"{UTIL_IMPORTEE}" (layer "{LAYER_1}") is imported by "{EXPORTER_IMPORTER}" (layer "{LAYER_2}").',
        ),
        id="should_not_violated_one_object_correct_one_be_imported_sssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [MODEL, UTIL],
                LAYER_2: [SERVICES, LOGGING],
                LAYER_3: [ORCHESTRATION, EXPORTER],
            },
            layer_1_should_only_be_accessed_by_layer_2_and_3,
            "",
        ),
        id="should_only_violated_only_one_rule_object_imported",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [PERSISTENCE], LAYER_2: [EXPORTER], LAYER_3: [IMPORTER]},
            layer_1_should_only_be_accessed_by_layer_2_and_3,
            layer_1_is_not_imported_by_layer_2_3,
        ),
        id="should_only_violated_only_be_imported_of_other_layers_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [RUNTIME], LAYER_2: [MODEL], LAYER_3: [UTIL]},
            layer_1_should_be_accessed_except_by_layer_2_and_3,
            layer_1_is_not_imported_by_any_layer_that_is_not_layer_2_3,
        ),
        id="should_except_violated_no_be_imported_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [ORCHESTRATION], LAYER_2: [RUNTIME, MODEL], LAYER_3: [UTIL]},
            layer_1_should_be_accessed_except_by_layer_2_and_3,
            layer_1_is_not_imported_by_any_layer_that_is_not_layer_2_3,
        ),
        id="should_except_violated_only_be_imported_no_other_be_imported_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [LOGGING],
                LAYER_2: [EXPORTER, MODEL],
                LAYER_3: [RUNTIME, SIMULATION],
            },
            layer_1_should_not_be_accessed_except_by_layer_2_and_3,
            f'"{LOGGING_IMPORTEE}" (layer "{LAYER_1}") is imported by "{ORCHESTRATION_IMPORTER}" (no layer).',
        ),
        id="should_not_except_violated_other_be_imported_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: [IMPORTER, SERVICES],
                LAYER_2: [ORCHESTRATION, MODEL],
                LAYER_3: [UTIL],
            },
            layer_1_should_only_be_accessed_except_by_layer_2_and_3,
            f'"{IMPORTER_IMPORTEE}" (layer "{LAYER_1}") is imported by "{ORCHESTRATION_IMPORTER}" (layer "{LAYER_2}").',
        ),
        id="should_only_except_violated_one_be_imported_ssmo",
    ),
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: [SERVICES], LAYER_2: [RUNTIME], LAYER_3: [MODEL]},
            layer_1_should_only_be_accessed_except_by_layer_2_and_3,
            f'"{SERVICES_IMPORTEE}" (layer "{LAYER_1}") is imported by "{RUNTIME_IMPORTER}" (layer "{LAYER_2}").\n'
            + layer_1_is_not_imported_by_any_layer_that_is_not_layer_2_3,
        ),
        id="should_only_except_violated_no_other_be_imported_ssmo",
    ),
]

layer_rule_error_messages_test_cases_submodule_and_module_in_layer_access = [
    _add_submodule_of_layer_1_module(parameter_set)
    for parameter_set in layer_rule_error_messages_test_cases_access
]
layer_rule_error_messages_test_cases_submodule_and_module_in_layer_be_accessed = [
    _add_submodule_of_layer_1_module(parameter_set)
    for parameter_set in layer_rule_error_messages_test_cases_be_accessed
]

layer_rule_error_messages_test_cases = (
    layer_rule_error_messages_test_cases_access
    + layer_rule_error_messages_test_cases_be_accessed
    + layer_rule_error_messages_test_cases_submodule_and_module_in_layer_access
    + layer_rule_error_messages_test_cases_submodule_and_module_in_layer_be_accessed
)

layer_rule_error_messages_regex_module_specification_test_cases = [
    pytest.param(
        LayerRuleTestCase(
            {LAYER_1: f"{PROJECT_ROOT}\\.ut[ia]l", LAYER_2: f"{PROJECT_ROOT}\\.model"},
            layer_1_should_only_access_layer_2,
            layer_1_does_not_import_layer_2,
        ),
        id="regex_with_options_in_middle_of_word",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: ".*_1\\.persistence",
                LAYER_2: f"{PROJECT_ROOT}\\.(util|runtime)",
            },
            layer_1_should_not_be_accessed_by_layer_2,
            f'"{PERSISTENCE_IMPORTEE}" (layer "{LAYER_1}") is imported by "{RUNTIME_IMPORTER}" (layer "{LAYER_2}").',
        ),
        id="regex_with_options_at_start_of_word",
    ),
    pytest.param(
        LayerRuleTestCase(
            {
                LAYER_1: f"{PROJECT_ROOT}\\.(imp.*|services)",
                LAYER_2: f"{PROJECT_ROOT}\\.model",
                LAYER_3: f"{PROJECT_ROOT}\\.runtime",
            },
            layer_1_should_only_access_except_layer_2_and_3,
            f'"{IMPORTER_IMPORTER}" (layer "{LAYER_1}") imports "{MODEL_IMPORTEE}" (layer "{LAYER_2}").',
        ),
        id="regex_with_options_at_end_of_word",
    ),
]
