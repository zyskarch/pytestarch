import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from pytestarch.exceptions import ImproperlyConfigured


@dataclass
class NamedModule:
    """Contains an ast module with its name.

    Attributes:
        module: ast module object
        name: module name
    """

    module: ast.Module
    name: str


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


class AbsoluteImport(Import):
    """Represents an absolute import."""

    def __init__(self, importer: str, module_name: str) -> None:
        super().__init__(importer)
        self._module_name = module_name
        self._importee_module_hierarchy = self._get_parent_modules(self._module_name)

    def importee(self) -> str:
        return self._module_name

    def importee_parent_modules(self) -> List[str]:
        return self._importee_module_hierarchy


class RelativeImport(Import):
    """Represents a relative import."""

    def __init__(
        self,
        importer: str,
        module_name: Optional[str],
        import_name: Optional[str],
        level: int,
    ) -> None:
        super().__init__(importer)
        self._module_name = module_name or import_name
        self._level = level

        if module_name is None and import_name is None:
            raise ImproperlyConfigured(
                "Either name of module of of import needs to be specified."
            )

        self._importee = self._calculate_importee()

        self._importee_module_hierarchy = self._get_parent_modules(self._module_name)

    def importee(self) -> str:
        return self._importee

    def importee_parent_modules(self) -> List[str]:
        return self._importee_module_hierarchy

    def _calculate_importee(self) -> str:
        return self._importer_module_hierarchy[-self._level] + "." + self._module_name
