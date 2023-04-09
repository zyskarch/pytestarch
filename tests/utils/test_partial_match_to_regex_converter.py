from __future__ import annotations

import re

import pytest

from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)

MODULE = "exporter.importer.module"
OTHER_MODULE = "exporter.orchestration"

test_cases = [
    pytest.param(MODULE, MODULE, MODULE, id="no_markers_match"),
    pytest.param(MODULE, MODULE, OTHER_MODULE, id="no_markers_no_match"),
    pytest.param("*.module", ".*\\.module", MODULE, id="start_markers_match"),
    pytest.param("*.module", ".*\\.module", OTHER_MODULE, id="start_markers_no_match"),
    pytest.param(
        "exporter.importer.*",
        "exporter\\.importer\\..*",
        MODULE,
        id="end_markers_match",
    ),
    pytest.param(
        "exporter.importer.*",
        "exporter\\.importer\\..*",
        OTHER_MODULE,
        id="end_markers_no_match",
    ),
    pytest.param(
        "*.importer.*", ".*\\.importer\\..*", MODULE, id="start_end_markers_match"
    ),
    pytest.param(
        "*.importer.*",
        ".*\\.importer\\..*",
        OTHER_MODULE,
        id="start_end_markers_no_match",
    ),
]


@pytest.mark.parametrize("partial_match, regex, string", test_cases)
def test_partial_match_and_regex_are_equivalent(
    partial_match: str, regex: str, string: str
) -> None:
    converted_match = convert_partial_match_to_regex(partial_match)

    match_result = re.match(re.compile(converted_match), string)
    regex_result = re.match(re.compile(regex), string)

    if match_result is None:
        assert regex_result is None
    else:
        assert match_result.span() == regex_result.span() == (0, 24)
