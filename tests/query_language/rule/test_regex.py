from __future__ import annotations

from pytestarch import EvaluableArchitecture, Rule


def test_import_of_itself_via_regex_works_as_expected(
    regex_project_arch: EvaluableArchitecture,
) -> None:
    rule = (
        Rule()
        .modules_that()
        .have_name_matching(".*dummy$")
        .should_not()
        .be_imported_by_modules_except_modules_that()
        .have_name_matching(".*dummy$")
    )

    rule.assert_applies(regex_project_arch)
