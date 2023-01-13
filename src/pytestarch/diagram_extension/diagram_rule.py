from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pytestarch import EvaluableArchitecture
from pytestarch.diagram_extension.dependency_to_rule_converter import (
    DependencyToRuleConverter,
)
from pytestarch.diagram_extension.diagram_parser import PumlParser
from pytestarch.diagram_extension.parsed_dependencies import ParsedDependencies
from pytestarch.query_language.base_language import (
    BaseModuleSpecifier,
    FileRule,
    RuleApplier,
)
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.query_language.multiple_rule_applier import MultipleRuleApplier


class ModulePrefixer:
    @classmethod
    def prefix(
        cls, parsed_dependencies: ParsedDependencies, prefix: Optional[str]
    ) -> ParsedDependencies:
        modules = parsed_dependencies.all_modules
        dependencies = parsed_dependencies.dependencies

        return ParsedDependencies(
            all_modules={cls._add_prefix_to_module(m, prefix) for m in modules},
            dependencies={
                cls._add_prefix_to_module(key, prefix): {
                    cls._add_prefix_to_module(value, prefix) for value in values
                }
                for key, values in dependencies.items()
            },
        )

    @classmethod
    def _add_prefix_to_module(cls, module_name: str, prefix: Optional[str]) -> str:
        if prefix is None:
            return module_name

        return f"{prefix}.{module_name}"


class DiagramRule(FileRule, BaseModuleSpecifier, RuleApplier):
    """Represents a set of architectural rules as defined in a diagram file.
    Reads the specified file, generates architectural rules, and returns an aggregated test result.

    By default, "should only import" rules will be generated for modules that the diagram shows as connected.
    "Should not import" rules will be generated for modules that are not connected in the diagram.
    """

    def __init__(self, should_only_rule: bool = True) -> None:
        """

        Args:
             should_only_rule: if True, edges between components will be converted into 'should only import' rules.
             If False, 'should import' rules will be generated instead.
        """
        self._file_path: Optional[Path] = None
        self._name_relative_to_root: Optional[str] = None
        self._should_only_rule = should_only_rule

    def from_file(self, file_path: Path) -> BaseModuleSpecifier:
        self._file_path = file_path
        return self

    def with_base_module(self, name_relative_to_root: str) -> RuleApplier:
        self._name_relative_to_root = name_relative_to_root
        return self

    def base_module_included_in_module_names(self) -> RuleApplier:
        return self

    def assert_applies(self, evaluable: EvaluableArchitecture) -> None:
        self._assert_required_configuration_present()
        dependencies: ParsedDependencies = PumlParser().parse(self._file_path)
        dependencies_with_fully_qualified_names = self._add_base_module_path(
            dependencies
        )
        rules = self._convert_to_rules(dependencies_with_fully_qualified_names)
        self._apply_rules(rules, evaluable)

    def _assert_required_configuration_present(self):
        if self._file_path is None:
            raise ImproperlyConfigured(
                "A file path pointing to the diagram has to be specified."
            )

    def _add_base_module_path(
        self, parsed_dependencies: ParsedDependencies
    ) -> ParsedDependencies:
        return ModulePrefixer.prefix(parsed_dependencies, self._name_relative_to_root)

    def _convert_to_rules(self, dependencies: ParsedDependencies) -> List[RuleApplier]:
        return DependencyToRuleConverter(self._should_only_rule).convert(dependencies)

    @classmethod
    def _apply_rules(
        cls, rule_appliers: List[RuleApplier], evaluable: EvaluableArchitecture
    ) -> None:
        MultipleRuleApplier(rule_appliers).assert_applies(evaluable)
