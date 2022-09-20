import pytest

from pytestarch.eval_structure.eval_structure_types import Evaluable
from pytestarch.query_language.base_language import Rule

C = "src.moduleC"
B = "src.moduleB"
A = "src.moduleA"
FILE_A2 = f"{A}.submoduleA2.fileA2"
A11 = f"{A}.submoduleA1.submoduleA11"
B2 = f"{B}.submoduleB1.fileB2"

test_cases = [
    pytest.param(
        Rule().modules_that().are_named(C).should().import_modules_that().are_named(A),
        '"src.moduleC" does not import "src.moduleA".',
        id="named should import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should()
        .import_modules_that()
        .are_sub_modules_of(A),
        '"src.moduleC" does not import a sub module of "src.moduleA".',
        id="named should import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should()
        .import_modules_that()
        .are_named(A),
        'Sub modules of "src.moduleC" do not import "src.moduleA".',
        id="submodule should import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should()
        .import_modules_that()
        .are_sub_modules_of(A),
        'Sub modules of "src.moduleC" do not import a sub module of "src.moduleA".',
        id="submodule should import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_that()
        .are_named(B),
        '"src.moduleA" imports "src.moduleC.fileC".',
        id="named should only import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleA" imports a sub module of "src.moduleC.fileC".',
        id="named should only import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .are_named(B),
        'Sub modules of "src.moduleA" import "src.moduleC.fileC".',
        id="submodule should only import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_that()
        .are_sub_modules_of(B),
        'Sub modules of "src.moduleA" import a sub module of "src.moduleC.fileC".',
        id="submodule should only import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .import_modules_that()
        .are_named(A),
        '"src.moduleB" imports "src.moduleA.',
        id="named should not import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of(A),
        '"src.moduleB" imports a sub module of "src.moduleA".',
        id="named should not import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should_not()
        .import_modules_that()
        .are_named(A),
        'Sub modules of "src.moduleB" import "src.moduleA".',
        id="submodule should not import named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should_not()
        .import_modules_that()
        .are_sub_modules_of(A),
        'Sub modules of "src.moduleB" import a sub module of "src.moduleA".',
        id="submodule should not import submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_named(C),
        '"src.moduleA.submoduleA2.fileA2" does not import any module that is not "src.moduleC".',
        id="named should import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        '"src.moduleA.submoduleA2.fileA2" does not import any module that is not a sub module of "src.moduleC".',
        id="named should import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_named(C),
        'Sub modules of "src.moduleA.submoduleA2.fileA2" do not import any module that is not "src.moduleC".',
        id="submodule should import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(FILE_A2)
        .should()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        'Sub modules of "src.moduleA.submoduleA2.fileA2" do not import any module that is not a sub module of "src.moduleC".',
        id="submodule should import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(C),
        '"src.moduleA" imports "src.moduleC".',
        id="named should only import except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        '"src.moduleA" imports a sub module of "src.moduleC".',
        id="named should only import except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(C),
        'Sub modules of "src.moduleA" import "src.moduleC".',
        id="submodule should only import except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(C),
        'Sub modules of "src.moduleA" import a sub module of "src.moduleC".',
        id="submodule should only import except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(B),
        '"src.moduleC" does not import any module that is not "src.moduleB".',
        id="named should only import except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleC" does not import any module that is not a sub module of "src.moduleB".',
        id="named should only import except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_named(B),
        'Sub modules of "src.moduleC" do not import any module that is not "src.moduleB".',
        id="submodule should only import except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        'Sub modules of "src.moduleC" do not import any module that is not a sub module of "src.moduleB".',
        id="submodule should only import except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_named(B),
        '"src.moduleA" imports "src.moduleC.fileC".',
        id="named should not import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleA" imports a sub module of "src.moduleC.fileC".',
        id="named should not import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_named(B),
        'Sub modules of "src.moduleA" import "src.moduleC.fileC".',
        id="submodule should not import except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_not()
        .import_modules_except_modules_that()
        .are_sub_modules_of(B),
        'Sub modules of "src.moduleA" import a sub module of "src.moduleC.fileC".',
        id="submodule should not import except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should()
        .be_imported_by_modules_that()
        .are_named(C),
        '"src.moduleA" is not imported by "src.moduleC".',
        id="named should be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of(C),
        '"src.moduleA" is not imported by a sub module of "src.moduleC".',
        id="named should be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .be_imported_by_modules_that()
        .are_named(C),
        'Sub modules of "src.moduleA" are not imported by "src.moduleC".',
        id="submodule should be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should()
        .be_imported_by_modules_that()
        .are_sub_modules_of(C),
        'Sub modules of "src.moduleA" are not imported by a sub module of "src.moduleC".',
        id="submodule should be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named(B),
        '"src.moduleC" is imported by "src.moduleA.',
        id="named should only be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleC" is imported by a sub module of "src.moduleA',
        id="named should only be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_named(B),
        'Sub modules of "src.moduleC" are imported by "src.moduleA',
        id="submodule should only be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_only()
        .be_imported_by_modules_that()
        .are_sub_modules_of(B),
        'Sub modules of "src.moduleC" are imported by a sub module of "src.moduleA',
        id="submodule should only be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_named(A),
        '"src.moduleC" is imported by "src.moduleA".',
        id="named should not be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(A),
        '"src.moduleC" is imported by a sub module of "src.moduleA".',
        id="named should not be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_named(A),
        'Sub modules of "src.moduleC" are imported by "src.moduleA".',
        id="submodule should not be imported by named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(A),
        'Sub modules of "src.moduleC" are imported by a sub module of "src.moduleA".',
        id="submodule should not be imported by submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named(A),
        '"src.moduleB" is not imported by any module that is not "src.moduleA".',
        id="named should be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(A),
        '"src.moduleB" is not imported by any module that is not a sub module of "src.moduleA".',
        id="named should be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_named(A),
        'Sub modules of "src.moduleB" are not imported by any module that is not "src.moduleA".',
        id="submodule should be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(B)
        .should()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(A),
        'Sub modules of "src.moduleB" are not imported by any module that is not a sub module of "src.moduleA".',
        id="submodule should be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(B2),
        '"src.moduleA.submoduleA1.submoduleA11" is imported by "src.moduleB.submoduleB1.fileB2".',
        id="named should only be imported by except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B2),
        '"src.moduleA.submoduleA1.submoduleA11" is imported by a sub module of "src.moduleB.submoduleB1.fileB2".',
        id="named should only be imported by except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(B2),
        'Sub modules of "src.moduleA.submoduleA1.submoduleA11" are imported by "src.moduleB.submoduleB1.fileB2".',
        id="submodule should only be imported by except named - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A11)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B2),
        'Sub modules of "src.moduleA.submoduleA1.submoduleA11" are imported by a sub module of "src.moduleB.submoduleB1.fileB2".',
        id="submodule should only be imported by except submodule - forbidden import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(B),
        '"src.moduleA" is not imported by any module that is not "src.moduleB".',
        id="named should only be imported by except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B),
        '"src.moduleA" is not imported by any module that is not a sub module of "src.moduleB"',
        id="named should only be imported by except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_named(B),
        'Sub modules of "src.moduleA" are not imported by any module that is not "src.moduleB"',
        id="submodule should only be imported by except named - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(A)
        .should_only()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(B),
        'Sub modules of "src.moduleA" are not imported by any module that is not a sub module of "src.moduleB"',
        id="submodule should only be imported by except submodule - no import",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named(FILE_A2),
        '"src.moduleC" is imported by "src.moduleA.fileA".',
        id="named should not be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_named(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(FILE_A2),
        '"src.moduleC" is imported by a sub module of "src.moduleA.fileA".',
        id="named should not be imported by except submodule",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_named(FILE_A2),
        'Sub modules of "src.moduleC" are imported by "src.moduleA.fileA".',
        id="submodule should not be imported by except named",
    ),
    pytest.param(
        Rule()
        .modules_that()
        .are_sub_modules_of(C)
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .are_sub_modules_of(FILE_A2),
        'Sub modules of "src.moduleC" are imported by a sub module of "src.moduleA.fileA".',
        id="submodule should not be imported by except submodule",
    ),
]


@pytest.mark.parametrize("rule, expected_error_message", test_cases)
def test_rule_violated_raises_proper_error_message(
    rule: Rule,
    expected_error_message: str,
    graph_based_on_string_module_names: Evaluable,
) -> None:
    with pytest.raises(AssertionError, match=expected_error_message):
        rule.applies(graph_based_on_string_module_names)
