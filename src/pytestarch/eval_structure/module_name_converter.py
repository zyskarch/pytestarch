from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, List, Tuple

from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure.breadth_first_searches import get_all_submodules_of
from pytestarch.eval_structure.evaluable_architecture import Module
from pytestarch.eval_structure.exceptions import ImpossibleMatch


class ModuleNameConverter:
    """Converts module names specified via regex pattern to module names based on which modules in the architecture
    match the regex pattern."""

    @classmethod
    def convert(
        cls, modules: List[Module], arch: EvaluableArchitecture
    ) -> Tuple[List[Module], Dict[str, List[Module]]]:
        """Converts each regex pattern that serves to identify module names into actual modules that match this pattern.

        Args:
            - modules: list of modules, some of which may need converting since their names are regex patterns
            - arch: architecture that contains actual modules

        Returns:
            - list of modules, now without any regex patterns.
            - mapping between a regex pattern and the actual modules it was replaced by
        """
        (
            modules_that_need_converting,
            other_modules,
        ) = cls._split_modules_by_presence_of_regex_pattern(modules)

        never_matched = {module.name for module in modules_that_need_converting}

        converted_modules = set()
        conversion_mapping = defaultdict(list)
        matching_submodules = set()

        module_names_that_need_to_be_matched = list(
            map(lambda module: module.name, modules_that_need_converting)
        )

        for actually_present_module in arch.modules:
            for module_to_match in module_names_that_need_to_be_matched:
                if cls._name_matches_pattern(module_to_match, actually_present_module):
                    converted_module = Module(name=actually_present_module)

                    converted_modules.add(converted_module)
                    conversion_mapping[module_to_match].append(converted_module)

                    if module_to_match in never_matched:
                        never_matched.remove(module_to_match)

                    submodules_of_match = get_all_submodules_of(
                        arch._graph, converted_module
                    )
                    submodules_of_match.remove(
                        actually_present_module
                    )  # should not count as its own submodule here
                    matching_submodules.update(submodules_of_match)

        if never_matched:
            raise ImpossibleMatch(
                f'No modules found that match: {", ".join(never_matched)}'
            )

        return list(converted_modules) + other_modules, conversion_mapping

    @classmethod
    def _name_matches_pattern(cls, pattern_to_match: str, name: str) -> bool:
        pattern = re.compile(pattern_to_match)
        match = re.match(pattern, name)

        return match is not None

    @classmethod
    def _split_modules_by_presence_of_regex_pattern(
        cls, modules: List[Module]
    ) -> Tuple[List[Module], List[Module]]:
        modules_with_regex_name_pattern = []
        other_modules = []

        for module in modules:
            if module.regex:
                modules_with_regex_name_pattern.append(module)
            else:
                other_modules.append(module)

        return modules_with_regex_name_pattern, other_modules
