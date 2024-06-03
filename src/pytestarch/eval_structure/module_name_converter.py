from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Sequence
from typing import cast

from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure.breadth_first_searches import get_all_submodules_of
from pytestarch.eval_structure.evaluable_architecture import (
    Module,
    ModuleFilter,
    ModuleNameFilter,
    ModuleNameRegexFilter,
)
from pytestarch.eval_structure.exceptions import ImpossibleMatch


class ModuleNameConverter:
    """Converts module names specified via regex pattern to module names based on which modules in the architecture
    match the regex pattern."""

    @classmethod
    def convert(
        cls, modules: Sequence[ModuleFilter], arch: EvaluableArchitecture
    ) -> tuple[Sequence[ModuleFilter], dict[str, list[Module]]]:
        """Converts each regex pattern that serves to identify module names into actual modules that match this pattern.

        Args:
            - modules: list of modules, some of which may need converting since their names are regex patterns
            - arch: architecture that contains actual modules

        Returns:
            - list of module filters, now without any regex patterns. Will be used for later dependency graph queries.
            - mapping between a regex pattern and the actual modules it was replaced by
        """
        (
            modules_that_need_converting,
            other_modules,
        ) = cls._split_modules_by_presence_of_regex_pattern(modules)

        never_matched = {module.identifier for module in modules_that_need_converting}

        converted_module_filters = set()
        conversion_mapping = defaultdict(list)
        matching_submodules = set()

        module_names_that_need_to_be_matched = list(
            map(lambda module: module.identifier, modules_that_need_converting)
        )

        for actually_present_module in arch.modules:
            for module_to_match in module_names_that_need_to_be_matched:
                if cls._name_matches_pattern(module_to_match, actually_present_module):
                    converted_module = Module(identifier=actually_present_module)
                    converted_module_filter = ModuleNameFilter(
                        name=actually_present_module
                    )

                    converted_module_filters.add(converted_module_filter)
                    conversion_mapping[module_to_match].append(converted_module)

                    if module_to_match in never_matched:
                        never_matched.remove(module_to_match)

                    submodules_of_match = get_all_submodules_of(
                        arch._graph, converted_module_filter  # type: ignore
                    )
                    submodules_of_match.remove(
                        actually_present_module
                    )  # should not count as its own submodule here
                    matching_submodules.update(submodules_of_match)

        if never_matched:
            raise ImpossibleMatch(
                f'No modules found that match: {", ".join(never_matched)}'
            )

        all_converted_modules = list(converted_module_filters) + other_modules  # type: ignore
        return all_converted_modules, conversion_mapping

    @classmethod
    def _name_matches_pattern(cls, pattern_to_match: str, name: str) -> bool:
        pattern = re.compile(pattern_to_match)
        match = re.match(pattern, name)

        return match is not None

    @classmethod
    def _split_modules_by_presence_of_regex_pattern(
        cls, modules: Sequence[ModuleFilter]
    ) -> tuple[list[ModuleNameRegexFilter], Sequence[ModuleFilter]]:
        modules_with_regex_name_pattern: list[ModuleNameRegexFilter] = []
        other_modules = []

        for module in modules:
            if module.identifier_is_regex:
                module = cast(ModuleNameRegexFilter, module)
                modules_with_regex_name_pattern.append(module)  # type: ignore
            else:
                other_modules.append(module)

        return modules_with_regex_name_pattern, other_modules
