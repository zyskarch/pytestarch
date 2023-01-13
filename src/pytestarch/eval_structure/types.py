from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class Import(ABC):
    def __init__(self, importer: str) -> None:
        self._importer = importer

        self._importer_module_hierarchy = self._get_parent_modules(self._importer)

    def importer(self) -> str:
        """Returns name of the module that imports something.

        Returns:
            module name
        """
        return self._importer

    def importer_parent_modules(self) -> List[str]:
        """Returns names of all parent modules of the importing module.

        Returns:
            list of module names
        """
        return self._importer_module_hierarchy

    @abstractmethod
    def importee(self) -> str:
        """Returns name of a module that is being imported.

        Returns:
            module name
        """
        raise NotImplementedError()

    @abstractmethod
    def importee_parent_modules(self) -> List[str]:
        """Returns names of all parent modules of the imported module.

        Returns:
            list of module names
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        return f"{self.importer()} imports {self.importee()}"

    def _get_parent_modules(self, module: str) -> List[str]:
        """Calculates all parent modules of a given module.

        Example: source root is a
        module: a.b.c
        returned: [a, a.b]

        Args:
            module: module to calculate parent modules for

        Returns:
            List of all parent modules, containing their full names up to the source code root.
        """
        parent_modules = []

        parent: List[str] = []

        for char in module:
            if char == ".":
                parent_modules.append("".join(parent))

            parent.append(char)

        return parent_modules

    def _append_prefix(self, value: str, prefix: str) -> str:
        return f"{prefix}.{value}"
