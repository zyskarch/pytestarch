from __future__ import annotations

from collections.abc import Sequence

from pytestarch.eval_structure.module_name_boundaries import is_internal_module
from pytestarch.eval_structure.types import Import


class ImporteeModuleCalculator:
    """Adds all parent modules of imported modules if they are not yet part of the modules list."""

    def __init__(self, root_module_name: str) -> None:
        self._root_module_name = root_module_name

    def calculate_importee_modules(
        self,
        imports: Sequence[Import],
        all_modules: list[str],
    ) -> list[str]:
        """For all imported modules: Calculate parent modules and add them to the list of existing modules if they
        are not already part of this list. This mainly applies to external dependencies.

        Args:
            imports: imports of the scanned source code
            all_modules: all modules parsed in the scanned source code

        Returns:
            all modules extended by parent modules of imported modules
        """
        extended_modules = set(all_modules)

        for imp in imports:
            importee = imp.importee()

            if not self._is_internal_module(importee):
                extended_modules.update(self._calculate_parent_modules(imp))

        return list(extended_modules)

    def _is_internal_module(self, module: str) -> bool:
        """Modules of the scanned root module are internal, even if they lie
        outside the scanned sub path, and must not be added as external nodes."""
        return is_internal_module(module, self._root_module_name)

    def _calculate_parent_modules(self, imp: Import) -> set[str]:
        modules = {imp.importee()}
        modules.update(imp.importee_parent_modules())

        return modules
