import ast
from _ast import Import
from typing import List, Optional

from pytestarch.importer.import_types import AbsoluteImport, NamedModule, RelativeImport


class ImportConverter:
    """Converts all ast imports to custom import types."""

    def convert(self, asts: List[NamedModule]) -> List[Import]:
        """Converts ast modules to custom import modules. Filters out all modules
        that are not imports.

        Args:
            asts: list of ast modules
        Returns:
            list of import objects
        """
        module_to_search = asts
        imports = []

        while module_to_search:
            module = module_to_search.pop()

            ast_module, module_name = module.module, module.name

            if hasattr(ast_module, "body"):
                module_to_search.extend(
                    [NamedModule(m, module_name) for m in ast_module.body]
                )
            else:
                new_imports = self._convert(module.module, module.name)

                if new_imports:
                    imports.extend(new_imports)

        return imports

    def _convert(self, module: ast.Module, module_name: str) -> Optional[List[Import]]:
        """Calculates all imports of the given ast module.

        Args:
            module: module to convert
            module_name: name of the module

        Returns:
            list of calculated import objects
        """
        new_imports = None

        if isinstance(module, ast.Import):
            new_imports = []
            for alias in module.names:
                new_imports.append(AbsoluteImport(module_name, alias.name))
        elif isinstance(module, ast.ImportFrom):
            if module.level == 0:
                new_imports = [AbsoluteImport(module_name, module.module)]
            else:
                new_imports = []
                for alias in module.names:
                    new_imports.append(
                        RelativeImport(
                            module_name, module.module, alias.name, module.level
                        )
                    )

        return new_imports
