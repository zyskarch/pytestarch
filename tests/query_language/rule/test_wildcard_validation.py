from __future__ import annotations

import pytest

from pytestarch import Rule
from pytestarch.query_language.exceptions import ImproperlyConfigured


def test_are_named_with_wildcard_single_string_raises_error() -> None:
    """Test that using a wildcard in a single string with are_named raises an error."""
    rule = Rule()

    with pytest.raises(ImproperlyConfigured) as exc_info:
        rule.modules_that().are_named("module_*")

    assert 'Wildcard "*" detected in module name "module_*"' in str(exc_info.value)
    assert 'Use "have_name_matching" with a regex pattern instead' in str(
        exc_info.value
    )


def test_are_named_with_wildcard_in_sequence_raises_error() -> None:
    """Test that using a wildcard in any string within a sequence with are_named raises an error."""
    rule = Rule()

    with pytest.raises(ImproperlyConfigured) as exc_info:
        rule.modules_that().are_named(["module_A", "module_*", "module_B"])

    assert 'Wildcard "*" detected in module name "module_*"' in str(exc_info.value)
    assert 'Use "have_name_matching" with a regex pattern instead' in str(
        exc_info.value
    )


def test_are_named_with_standalone_asterisk_raises_error() -> None:
    """Test that using a standalone asterisk with are_named raises an error."""
    rule = Rule()

    with pytest.raises(ImproperlyConfigured) as exc_info:
        rule.modules_that().are_named("*")

    assert 'Wildcard "*" detected in module name "*"' in str(exc_info.value)
    assert 'Use "have_name_matching" with a regex pattern instead' in str(
        exc_info.value
    )


def test_are_named_without_wildcard_works_normally() -> None:
    """Test that are_named works normally when no wildcards are present."""
    rule = Rule()

    # This should not raise an error
    rule.modules_that().are_named("module_A")
    assert rule.rule_subjects is not None
    assert len(rule.rule_subjects) == 1
    assert rule.rule_subjects[0].identifier == "module_A"


def test_are_named_with_sequence_without_wildcard_works_normally() -> None:
    """Test that are_named works normally with a sequence when no wildcards are present."""
    rule = Rule()

    # This should not raise an error
    rule.modules_that().are_named(["module_A", "module_B"])
    assert rule.rule_subjects is not None
    assert len(rule.rule_subjects) == 2
    assert rule.rule_subjects[0].identifier == "module_A"
    assert rule.rule_subjects[1].identifier == "module_B"


def test_have_name_matching_with_wildcard_works() -> None:
    """Test that have_name_matching works correctly with wildcards (should not raise errors)."""
    rule = Rule()

    # This should work fine - have_name_matching is designed for patterns
    rule.modules_that().have_name_matching("module_.*")
    assert rule.rule_subjects is not None
    assert len(rule.rule_subjects) == 1
    assert rule.rule_subjects[0].identifier == "module_.*"
