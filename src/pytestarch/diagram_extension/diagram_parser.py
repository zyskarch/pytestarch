from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Set, Tuple

from pytestarch.diagram_extension.exceptions import PumlParsingError
from pytestarch.diagram_extension.parsed_dependencies import ParsedDependencies


class DiagramParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDependencies:
        pass


@dataclass(frozen=True)
class Module:
    name: str
    alias: Optional[str] = None


PUML_START_MARKER = "@startuml"
PUML_END_MARKER = "@enduml"
ANYTHING = ".*"
ANY_ARROW_TEXT = "(-?|\w+-)"  # noqa: W605
NON_EMPTY_STRING = ".+"
COMPONENT_MARKER = "component"
NON_EMPTY_WHITESPACE = "\s+"  # noqa: W605
NON_EMPTY_CHAR_OR_DIGIT = "(\w|\d)+"  # noqa: W605
NON_EMPTY_CHAR_OR_DIGIT_OR_WHITESPACE = "(\w|\d|\s)+"  # noqa: W605
START_LINE = "^"
END_LINE = "$"
BRACKET_OPEN = "\["  # noqa: W605
BRACKET_CLOSE = "\]"  # noqa: W605
OPTIONAL_BRACKET_OPEN = "(\[)?"  # noqa: W605
OPTIONAL_BRACKET_CLOSE = "(\])?"  # noqa: W605
ALIAS_MARKER = "as"
ARROW_BODY = "-"
ARROW_HEAD_LEFT = "<"
ARROW_HEAD_RIGHT = ">"


class PumlParser(DiagramParser):
    """
    Parses .puml files to a dependencies object that can be used to generate architecture rules.
    """

    def parse(self, file_path: Path) -> ParsedDependencies:
        """
        Syntactical requirements for .puml files:
            * start of dependency definition needs to be tagged with @startuml
            * end of dependency definition needs to be tagged with @enduml
            * all text outside these tags is ignored
            * component names must be enclosed in square brackets
            * exception: if a component as been given an alias via `[module name] as alias`, then the alias should not be
                wrapped in square brackets
            * dependencies must be with either -->, ->, <--, <-, -text->, or <-text-. The dependee is to be placed
                on the side of the arrow head, the dependor on the opposite side
        Args:
            file_path: .puml file to parse

        Returns:
            dependencies object that can be used to generate architecture rules.

        """
        with open(file_path) as puml_file:
            content = puml_file.read().strip()

        relevant_content = self._remove_content_outside_start_and_end_tags(content)

        modules = self._retrieve_modules_declared_outside_dependencies(relevant_content)
        dependencies = self._retrieve_dependencies_and_inline_modules(relevant_content)

        modules, dependencies = self._unify(modules, dependencies)

        return ParsedDependencies(modules, dependencies)

    @classmethod
    def _remove_content_outside_start_and_end_tags(cls, content: str) -> str:
        regex = f"{ANYTHING}{PUML_START_MARKER}({NON_EMPTY_STRING}){PUML_END_MARKER}{ANYTHING}"
        # dotall: . also matches newline character
        pattern = re.compile(regex, re.DOTALL)

        match = re.search(pattern, content)

        if match:
            return match.group(1)
        else:
            raise PumlParsingError(
                "No diagram specification found. Check that the file meets the requirements for .puml files."
            )

    @classmethod
    def _named_group(cls, name: str, content: str) -> str:
        return f"(?P<{name}>{content})"

    @classmethod
    def _retrieve_modules_declared_outside_dependencies(
        cls, content: str
    ) -> Set[Module]:
        module_group_1 = "m1"
        module_group_2 = "m2"
        alias_group = "alias"

        component_followed_by_name_no_brackets = f"{COMPONENT_MARKER}{NON_EMPTY_WHITESPACE}{cls._named_group(module_group_1, NON_EMPTY_CHAR_OR_DIGIT)}"

        optional_component = f"({COMPONENT_MARKER}{NON_EMPTY_WHITESPACE})?"
        component_name_in_brackets = f"{BRACKET_OPEN}{cls._named_group(module_group_2, NON_EMPTY_CHAR_OR_DIGIT_OR_WHITESPACE)}{BRACKET_CLOSE}"
        optional_alias = f"({NON_EMPTY_WHITESPACE}{ALIAS_MARKER}{NON_EMPTY_WHITESPACE}{cls._named_group(alias_group, NON_EMPTY_STRING)})?"

        optional_component_followed_by_name_in_brackets_optional_alias = (
            f"{optional_component}{component_name_in_brackets}{optional_alias}"
        )

        module_regex = f"{START_LINE}{component_followed_by_name_no_brackets}|{optional_component_followed_by_name_in_brackets_optional_alias}{END_LINE}"
        pattern = re.compile(module_regex, re.MULTILINE)

        result = set()
        for match in re.finditer(pattern, content):
            module = match.group(module_group_1) or match.group(module_group_2)
            alias = match.group(alias_group)
            result.add(Module(name=module, alias=alias))

        return result

    @classmethod
    def _component_optional_brackets(cls, group_name: str) -> str:
        return f"{OPTIONAL_BRACKET_OPEN}{cls._named_group(group_name, NON_EMPTY_CHAR_OR_DIGIT)}{OPTIONAL_BRACKET_CLOSE}"

    @classmethod
    def _retrieve_dependencies_and_inline_modules(
        cls,
        content: str,
    ) -> Dict[str, Set[str]]:
        dependor_group_1 = "dependor1"
        dependor_group_2 = "dependor2"

        dependee_group_1 = "dependee1"
        dependee_group_2 = "dependee2"

        dependencies = defaultdict(set)

        dependor_left_hand = cls._component_optional_brackets(dependor_group_1)
        dependee_right_hand = cls._component_optional_brackets(dependee_group_1)
        dependor_right_hand = cls._component_optional_brackets(dependor_group_2)
        dependee_left_hand = cls._component_optional_brackets(dependee_group_2)

        arrow_to_right = f"{ARROW_BODY}{ANY_ARROW_TEXT}{ARROW_HEAD_RIGHT}"
        arrow_to_left = f"{ARROW_HEAD_LEFT}{ARROW_BODY}{ANY_ARROW_TEXT}"

        dependor_depends_on_dependee = f"({dependor_left_hand}{NON_EMPTY_WHITESPACE}{arrow_to_right}{NON_EMPTY_WHITESPACE}{dependee_right_hand})"
        dependee_depended_on_by_dependor = f"{dependee_left_hand}{NON_EMPTY_WHITESPACE}{arrow_to_left}{NON_EMPTY_WHITESPACE}{dependor_right_hand}"

        dependency_regex = rf"{START_LINE}{dependor_depends_on_dependee}|{dependee_depended_on_by_dependor}{END_LINE}"
        pattern = re.compile(dependency_regex, re.MULTILINE)

        for match in re.finditer(pattern, content):
            importer = match.group(dependor_group_1) or match.group(dependor_group_2)
            importee = match.group(dependee_group_1) or match.group(dependee_group_2)

            dependencies[importer].add(importee)

        return dict(dependencies)

    def _unify(
        self,
        modules: Set[Module],
        dependencies: Dict[str, Set[str]],
    ) -> Tuple[Set[str], Dict[str, Set[str]]]:
        unified_dependencies = {}

        all_aliases = self._get_modules_by_alias(modules)

        for dependor, dependees in dependencies.items():
            unified_dependor = self._unify_module(dependor, all_aliases)
            unified_dependees = {
                self._unify_module(dependee, all_aliases) for dependee in dependees
            }

            unified_dependencies[unified_dependor] = unified_dependees

        unified_modules = self._get_unified_modules(modules, unified_dependencies)

        return unified_modules, unified_dependencies

    @classmethod
    def _get_unified_modules(
        cls,
        modules: Set[Module],
        unified_dependencies: Dict[str, Set[str]],
    ) -> Set[str]:
        all_modules = {m.name for m in modules}

        all_modules.update(set(unified_dependencies.keys()))

        for dependee_modules in unified_dependencies.values():
            all_modules.update(dependee_modules)

        return all_modules

    @classmethod
    def _get_modules_by_alias(cls, modules: Set[Module]) -> Dict[str, str]:
        return {
            module.alias: module.name for module in modules if module.alias is not None
        }

    @classmethod
    def _unify_module(cls, module: str, all_aliases: Dict[str, str]) -> str:
        return all_aliases.get(module, module)
