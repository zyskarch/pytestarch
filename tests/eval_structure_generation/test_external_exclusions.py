from __future__ import annotations

from typing import Any

import pytest

import resources
from pytestarch.pytestarch import get_evaluable_architecture_for_module_objects
from resources import project_with_nested_external_dependencies

external_exclusion_cases = [
    pytest.param({}, True, id="no_exclusions"),
    pytest.param(
        {"regex_external_exclusions": ("logging",)},
        False,
        id="complete_regex_match",
    ),
    pytest.param(
        {"regex_external_exclusions": ("logging$",)},
        False,  # parent is excluded
        id="no_full_regex_match",
    ),
    pytest.param(
        {"regex_external_exclusions": ("logging.*",)},
        False,
        id="partial_regex_match",
    ),
    pytest.param(
        {"external_exclusions": ("logging",)},
        False,  # parent is excluded
        id="complete_pseudo_regex_match",
    ),
    pytest.param(
        {"external_exclusions": ("logging*",)},
        False,
        id="partial_pseudo_regex_match",
    ),
]


@pytest.mark.parametrize("exclusions, expected_present", external_exclusion_cases)
def test_external_dependencies_membership(
    exclusions: dict[str, Any],
    expected_present: bool,
) -> None:
    evaluable = get_evaluable_architecture_for_module_objects(
        resources,
        project_with_nested_external_dependencies,
        exclude_external_libraries=False,
        **exclusions,
    )
    graph = evaluable._graph  # type: ignore[attr-defined]

    if expected_present:
        assert "logging" in graph
        assert "logging.handlers" in graph
    else:
        assert "logging" not in graph
        assert "logging.handlers" not in graph
