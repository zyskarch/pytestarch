from pathlib import Path
from typing import Optional

from pytestarch import EvaluableArchitecture
from pytestarch.diagram_import.diagram_parser import PumlParser
from pytestarch.diagram_import.parsed_dependencies import ParsedDependencies
from pytestarch.exceptions import ImproperlyConfigured
from pytestarch.query_language.base_language import (
    RuleApplier,
    FileRule,
    BaseModuleSpecifier,
)
from pytestarch.query_language.diagrams.dependency_to_rule_converter import (
    DependencyToRuleConverter,
)
from pytestarch.query_language.multiple_rule_applier import MultipleRuleApplier


class ModulePrefixer:
    def __init__(self, prefix: Optional[str]) -> None:
        self._prefix = prefix

    def prefix(self, parsed_dependencies: ParsedDependencies) -> ParsedDependencies:
        modules = parsed_dependencies.all_modules
        dependencies = parsed_dependencies.dependencies

        return ParsedDependencies(
            all_modules={self._add_prefix_to_module(m) for m in modules},
            dependencies={
                self._add_prefix_to_module(key): {
                    self._add_prefix_to_module(value) for value in values
                }
                for key, values in dependencies.items()
            },
        )

    def _add_prefix_to_module(self, module_name: str) -> str:
        if self._prefix is None:
            return module_name

        return f"{self._prefix}.{module_name}"


class DiagramRule(FileRule, BaseModuleSpecifier, RuleApplier):
    """Represents a set of architectural rules as defined in a diagram file.
    Reads the specified file, generates architectural rules, and returns an aggregated test result.

    By default, "should only" rules will be generated for modules that the diagram shows as connected.
    "Should not" rules will be generated for modules that are not connected in the diagram.
    """

    def __init__(self) -> None:
        self._file_path: Optional[Path] = None
        self._name_relative_to_root: Optional[str] = None

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
        return ModulePrefixer(self._name_relative_to_root).prefix(parsed_dependencies)

    @classmethod
    def _convert_to_rules(cls, dependencies: ParsedDependencies) -> list[RuleApplier]:
        return DependencyToRuleConverter.convert(dependencies)

    @classmethod
    def _apply_rules(
        cls, rule_appliers: list[RuleApplier], evaluable: EvaluableArchitecture
    ) -> None:
        MultipleRuleApplier(rule_appliers).assert_applies(evaluable)