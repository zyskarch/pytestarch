from pytestarch import Rule
from pytestarch.diagram_import.parsed_dependencies import ParsedDependencies
from pytestarch.query_language.base_language import RuleApplier


class DependencyToRuleConverter:
    @classmethod
    def convert(cls, dependencies: ParsedDependencies) -> list[RuleApplier]:
        should_rules = cls._convert_should_rules(dependencies)
        should_not_rules = cls._convert_should_not_rules(dependencies)
        return should_rules + should_not_rules

    @classmethod
    def _convert_should_rules(
        cls, dependencies: ParsedDependencies
    ) -> list[RuleApplier]:
        return [
            Rule()
            .modules_that()
            .are_named(importer)
            .should_only()
            .import_modules_that()
            .are_named(list(importees))
            for importer, importees in dependencies.dependencies.items()
        ]

    @classmethod
    def _convert_should_not_rules(
        cls, parsed_dependencies: ParsedDependencies
    ) -> list[RuleApplier]:
        # sorting in this method is necessary to generate a reliable order of returned rules
        # this helps with testing and overall consistency
        rules = []

        for possible_importer in sorted(parsed_dependencies.all_modules):
            imported = parsed_dependencies.dependencies.get(possible_importer, set())
            all_other_modules = parsed_dependencies.all_modules - {possible_importer}
            not_imported = all_other_modules - imported

            if not_imported:
                sorted_not_imported = sorted(not_imported)
                rules.append(
                    Rule()
                    .modules_that()
                    .are_named(possible_importer)
                    .should_not()
                    .import_modules_that()
                    .are_named(sorted_not_imported)
                )

        return rules
