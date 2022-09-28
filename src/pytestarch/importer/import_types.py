import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List

from pytestarch.query_language.exceptions import ImproperlyConfigured


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

    def update_import_prefixes(self, prefix: str, top_level_module_name: str) -> None:
        """Adds the given prefix to the import modules' path.
        This ensures that importers and importees have the same module path structure. For example, if the importees
        have a structure like src.A.x, but the module path has been restricted to src.A, the importers will all have
        a structure like A.x. This causes no edges in the resulting graph, as no matching nodes are found for the edges.
        The prefix will only be appended to modules that are submodules of the top level module.

        Args:
            prefix: to append to all internal module names
            top_level_module_name: name of the top level module. Used to differentiate between internal and external
                dependencies.
        """
        pass

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

    def update_import_prefixes(self, prefix: str, top_level_module_name: str) -> None:
        if self._module_name.startswith(top_level_module_name):
            self._module_name = self._append_prefix(self._module_name, prefix)
            self._importee_module_hierarchy = [
                self._append_prefix(name, prefix)
                for name in self._importer_module_hierarchy
            ]


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
        self._module_name = module_name
        self._import_name = import_name
        self._level = level

        if module_name is None and import_name is None:
            raise ImproperlyConfigured(
                "Either name of module of of import needs to be specified."
            )

        self._importee = self._calculate_importee()

        self._importee_module_hierarchy = self._get_parent_modules(
            self._module_name or self._import_name
        )

    def importee(self) -> str:
        return self._importee

    def importee_parent_modules(self) -> List[str]:
        return self._importee_module_hierarchy

    def _calculate_importee(self) -> str:
        module_name = self._module_name or self._import_name

        return self._importer_module_hierarchy[-self._level] + "." + module_name

    def update_import_prefixes(self, prefix: str, top_level_module_name: str) -> None:
        if self._module_name.startswith(top_level_module_name):
            self._module_name = self._append_prefix(self._module_name, prefix)
            self._importee_module_hierarchy = [
                self._append_prefix(name, prefix)
                for name in self._importer_module_hierarchy
            ]
