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

    module: ast.AST
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
    """Represents a relative import.

    For 'from <module> import <name>', the importee resolves to
    '<importer's level-th parent>.<module>.<name>'. A RelativeImport with
    both module and name None represents the base package at that level
    alone, which Python imports in addition to the imported name; bare
    relative statements emit one such import plus one per alias.
    """

    def __init__(
        self,
        importer: str,
        module_name: str | None,
        import_name: str | None,
        level: int,
    ) -> None:
        super().__init__(importer)
        self._module_name = module_name
        self._import_name = import_name
        self._level = level

        self._importee = self._calculate_importee()

        self._importee_module_hierarchy = get_parent_modules(self._importee)

    def importee(self) -> str:
        return self._importee

    def importee_parent_modules(self) -> list[str]:
        return self._importee_module_hierarchy

    def _calculate_importee(self) -> str:
        if self._level < 1:
            raise ImportException(
                "Relative import needs at least one leading dot: the level must "
                "be at least 1."
            )
        if len(self._importer_module_hierarchy) < self._level:
            requested = self._import_name or self._module_name or "." * self._level
            raise ImportException(
                f"Attempted relative import with no known parent package: cannot "
                f"resolve the level {self._level} relative import of "
                f"'{requested}' in module "
                f"'{self._importer}'. This happens if the module is located directly "
                "at the root of a scanned directory that is not a Python package."
            )
        base = self._importer_module_hierarchy[-self._level]
        name = ".".join(part for part in (self._module_name, self._import_name) if part)
        return f"{base}.{name}" if name else base
