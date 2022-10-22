from abc import ABC, abstractmethod
from pathlib import Path

from pytestarch.diagram_import.parsed_dependencies import ParsedDependencies


class DiagramParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDependencies:
        pass


class PumlParser(DiagramParser):
    def parse(self, file_path: Path) -> ParsedDependencies:
        pass
