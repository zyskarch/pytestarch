from __future__ import annotations

import pytest

from pytestarch import Rule
from pytestarch.query_language.rule import RuleConfiguration
from query_language.rule.conftest import MODULE_A

config_alias_test_cases = [
    [
        RuleConfiguration(
            should_not=True,
            import_=True,
            except_present=False,
            modules_to_check=[MODULE_A],
            rule_object_anything=True,
        ),
        RuleConfiguration(
            should_not=True,
            import_=True,
            except_present=True,
            modules_to_check=[MODULE_A],
            modules_to_check_against=[MODULE_A],
            rule_object_anything=False,
        ),
    ],
    [
        RuleConfiguration(
            should_not=True,
            import_=False,
            except_present=False,
            modules_to_check=[MODULE_A],
            rule_object_anything=True,
        ),
        RuleConfiguration(
            should_not=True,
            import_=False,
            except_present=True,
            modules_to_check=[MODULE_A],
            modules_to_check_against=[MODULE_A],
            rule_object_anything=False,
        ),
    ],
    [
        rule := RuleConfiguration(
            should_not=True,
            import_=True,
            except_present=False,
            modules_to_check=[MODULE_A],
            rule_object_anything=False,
        ),
        rule,
    ],
    [
        rule := RuleConfiguration(
            should_not=True,
            import_=False,
            except_present=False,
            modules_to_check=[MODULE_A],
            rule_object_anything=False,
        ),
        rule,
    ],
    [
        rule := RuleConfiguration(
            should_not=True,
            import_=True,
            except_present=False,
            modules_to_check=[MODULE_A],
            rule_object_anything=False,
        ),
        rule,
    ],
    [
        rule := RuleConfiguration(
            should_not=True,
            import_=False,
            except_present=False,
            modules_to_check=[MODULE_A],
            rule_object_anything=False,
        ),
        rule,
    ],
    [
        rule := RuleConfiguration(
            should_only=True,
            import_=True,
            except_present=False,
            modules_to_check=[MODULE_A],
            rule_object_anything=False,
        ),
        rule,
    ],
    [
        rule := RuleConfiguration(
            should_only=True,
            import_=False,
            except_present=False,
            modules_to_check=[MODULE_A],
            rule_object_anything=False,
        ),
        rule,
    ],
    [
        rule := RuleConfiguration(
            should=True,
            import_=True,
            except_present=False,
            modules_to_check=[MODULE_A],
            rule_object_anything=False,
        ),
        rule,
    ],
    [
        rule := RuleConfiguration(
            should=True,
            import_=False,
            except_present=False,
            modules_to_check=[MODULE_A],
            rule_object_anything=False,
        ),
        rule,
    ],
]


@pytest.mark.parametrize("config_with_alias, expected_config", config_alias_test_cases)
def test_aliases_converted(
    config_with_alias: RuleConfiguration,
    expected_config: RuleConfiguration,
) -> None:
    converted_config = Rule._convert_aliases(config_with_alias)
    assert converted_config == expected_config
