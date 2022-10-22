from pytestarch.diagram_import.parsed_dependencies import ParsedDependencies
from pytestarch.query_language.diagrams.dependency_to_rule_converter import (
    DependencyToRuleConverter,
)

M1 = "M1"
M2 = "M2"
M3 = "M3"


def test_empty_dependencies_still_empty() -> None:
    dependencies = ParsedDependencies(set(), {})
    rules = DependencyToRuleConverter.convert(dependencies)
    assert not rules


def test_should_rules_with_single_rule_object() -> None:
    dependencies = ParsedDependencies({M1, M2}, {M1: {M2}})
    rules = DependencyToRuleConverter._convert_should_rules(dependencies)

    assert len(rules) == 1
    assert '"M1" should only import modules that are named "M2".' == str(rules[0])


def test_should_rules_with_multiple_rule_objects() -> None:
    dependencies = ParsedDependencies({M1, M2, M3}, {M1: {M2, M3}})
    rules = DependencyToRuleConverter._convert_should_rules(dependencies)

    assert len(rules) == 1
    assert '"M1" should only import modules that are named "M2, M3".' == str(rules[0])


def test_multiple_should_rules() -> None:
    dependencies = ParsedDependencies({M1, M2}, {M1: {M2}, M2: {M1}})
    rules = DependencyToRuleConverter._convert_should_rules(dependencies)

    assert len(rules) == 2
    assert '"M1" should only import modules that are named "M2".' == str(rules[0])
    assert '"M2" should only import modules that are named "M1".' == str(rules[1])


def test_should_not_rules_with_single_rule_object() -> None:
    dependencies = ParsedDependencies({M1, M2}, {M2: {M1}})
    rules = DependencyToRuleConverter._convert_should_not_rules(dependencies)

    assert len(rules) == 1
    assert '"M1" should not import modules that are named "M2".' == str(rules[0])


def test_should_not_rules_with_multiple_rule_objects() -> None:
    dependencies = ParsedDependencies({M1, M2, M3}, {M2: {M1, M3}, M3: {M1, M2}})
    rules = DependencyToRuleConverter._convert_should_not_rules(dependencies)

    assert len(rules) == 1
    assert '"M1" should not import modules that are named "M2, M3".' == str(rules[0])


def test_multiple_should_not_rules() -> None:
    dependencies = ParsedDependencies({M1, M2, M3}, {M1: {M3}, M2: {M3}, M3: {M1, M2}})
    rules = DependencyToRuleConverter._convert_should_not_rules(dependencies)

    assert len(rules) == 2
    assert '"M1" should not import modules that are named "M2".' == str(rules[0])
    assert '"M2" should not import modules that are named "M1".' == str(rules[1])


def test_should_and_should_not_rules_generated() -> None:
    dependencies = ParsedDependencies({M1, M2}, {M2: {M1}})
    rules = DependencyToRuleConverter.convert(dependencies)

    assert len(rules) == 2
    assert '"M2" should only import modules that are named "M1".' == str(rules[0])
    assert '"M1" should not import modules that are named "M2".' == str(rules[1])
