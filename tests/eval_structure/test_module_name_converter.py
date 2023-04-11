from __future__ import annotations

from typing import List

import pytest
from integration.interesting_rules_for_tests import PROJECT_ROOT

from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure.evaluable_architecture import ModuleFilter
from pytestarch.eval_structure.module_name_converter import ModuleNameConverter

test_cases = [
    pytest.param(
        f"{PROJECT_ROOT}\\.ut[ia]l",
        [
            f"{PROJECT_ROOT}.util",
            f"{PROJECT_ROOT}.util.util_importee",
            f"{PROJECT_ROOT}.util.util_importer",
        ],
        id="single_match",
    ),
    pytest.param(
        f"{PROJECT_ROOT}\\.(util|services)",
        [
            f"{PROJECT_ROOT}.services",
            f"{PROJECT_ROOT}.services.services_importee",
            f"{PROJECT_ROOT}.services.services_importer",
            f"{PROJECT_ROOT}.util",
            f"{PROJECT_ROOT}.util.util_importee",
            f"{PROJECT_ROOT}.util.util_importer",
        ],
        id="multiple_matches",
    ),
]


@pytest.mark.parametrize("regex, expected_matches", test_cases)
def test_submodules_are_matched(
    regex: str, expected_matches: List[str], flat_project_1: EvaluableArchitecture
) -> None:
    modules_to_convert = [ModuleFilter(name=regex, regex=True)]

    converted_modules, _ = ModuleNameConverter.convert(
        modules_to_convert, flat_project_1
    )

    assert len(converted_modules) == len(expected_matches)

    converted_modules.sort(key=lambda m: m.name)

    for converted, expected in zip(converted_modules, expected_matches):
        assert converted.name == expected
