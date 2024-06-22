from __future__ import annotations

import ast
from dataclasses import dataclass

from pytestarch.eval_structure.types import Import, get_parent_modules
from pytestarch.eval_structure_generation.file_import.exceptions import ImportException


@dataclass
class NamedModule:
    """Contains an ast module with its name.

    Attributes:
        module: ast module object
        name: module name
    """

    module: ast.Module
    name: str


class AbsoluteImport(Import):
    """Represents an absolute import."""

    def __init__(self, importer: str, module_name: str) -> None:
        super().__init__(importer)
        self._module_name = module_name
        self._importee_module_hierarchy = get_parent_modules(self._module_name)

    def importee(self) -> str:
        return self._module_name

    def importee_parent_modules(self) -> list[str]:
        return self._importee_module_hierarchy


class RelativeImport(Import):
    """Represents a relative import."""

    def __init__(
        self,
        importer: str,
        module_name: str | None,
        import_name: str | None,
        level: int,
    ) -> None:
        super().__init__(importer)
        if module_name is None and import_name is None:
            raise ImportException(
                "Either name of module of of import needs to be specified."
            )
        self._module_name = module_name or import_name
        self._level = level

        self._importee = self._calculate_importee()

        self._importee_module_hierarchy = get_parent_modules(self._module_name)  # type: ignore

    def importee(self) -> str:
        return self._importee

    def importee_parent_modules(self) -> list[str]:
        return self._importee_module_hierarchy

    def _calculate_importee(self) -> str:
        return self._importer_module_hierarchy[-self._level] + "." + self._module_name  # type: ignore
