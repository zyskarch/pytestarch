from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path

from pytestarch.diagram_import.parsed_dependencies import ParsedDependencies
from pytestarch.exceptions import PumlParsingError


class DiagramParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDependencies:
        pass


PUML_START_TAG = "@startuml"
PUML_END_TAG = "@enduml"
NEW_LINE_CHARACTER = "\n"

ARROW_RIGHT = "-->"
MODULE_START_CHARACTER = "["
MODULE_END_CHARACTER = "]"


class PumlParser(DiagramParser):
    def parse(self, file_path: Path) -> ParsedDependencies:
        with open(file_path) as puml_file:
            lines = puml_file.readlines()
            relevant_lines = self._remove_content_outside_start_and_end_tags(lines)
            modules = self._retrieve_modules(relevant_lines)
            dependencies = self._retrieve_dependencies(relevant_lines)

        return ParsedDependencies(modules, dependencies)

    def _remove_content_outside_start_and_end_tags(self, lines: list[str]) -> list[str]:
        try:
            start_idx = lines.index(PUML_START_TAG + NEW_LINE_CHARACTER)
            end_idx = lines.index(PUML_END_TAG + NEW_LINE_CHARACTER)

        except ValueError as e:
            raise PumlParsingError("PUML file needs a start and an end tag.") from e

        if end_idx <= start_idx + 1:
            return []

        return lines[start_idx + 1 : end_idx]

    def _retrieve_modules(self, lines: list[str]) -> set[str]:
        modules = set()
        for line in lines:
            if line.isspace() or MODULE_START_CHARACTER not in line:
                continue

            arrow_removed = line.split(ARROW_RIGHT)
            modules |= set(self._extract_names(arrow_removed))

        return modules

    def _retrieve_dependencies(self, lines: list[str]) -> dict[str, set[str]]:
        dependencies = defaultdict(set)
        for line in lines:
            if line.isspace() or MODULE_START_CHARACTER not in line:
                continue

            arrow_removed = line.split(ARROW_RIGHT)
            dependor, dependee = self._extract_names(arrow_removed)  # todo: docstring
            dependencies[dependor].add(dependee)

        return dict(dependencies)

    def _extract_names(self, arrow_removed: list[str]) -> tuple[str, str]:
        names = [
            name.strip()
            .replace(MODULE_START_CHARACTER, "")
            .replace(MODULE_END_CHARACTER, "")
            for name in arrow_removed
        ]

        if len(names) != 2:
            raise PumlParsingError(
                "A dependency always needs to have a dependor and a dependee."
            )

        return names[0], names[1]
