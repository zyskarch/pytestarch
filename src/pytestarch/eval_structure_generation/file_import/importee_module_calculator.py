from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pytestarch.eval_structure.types import Import


class ImporteeModuleCalculator:
    """Adds all parent modules of imported modules if they are not yet part of the modules list."""

    def __init__(self, root_path: Path) -> None:
        self._root_path = root_path

    def calculate_importee_modules(
        self,
        imports: Sequence[Import],
        all_modules: list[str],
    ) -> list[str]:
        """For all imported modules: Calculate parent modules and add them to the list of existing modules if they
        are not already part of this list. This mainly applies to external dependencies.

        Args:
            imports:
            all_modules:

        Returns:
            all modules extended by parent modules of imported modules
        """
        extended_modules = set(all_modules)

        for imp in imports:
            importee = imp.importee()

            if str(self._root_path) not in importee:
                extended_modules.update(self._calculate_parent_modules(imp))

        return list(extended_modules)

    def _calculate_parent_modules(self, imp: Import) -> set[str]:
        modules = {imp.importee()}
        modules.update(imp.importee_parent_modules())

        return modules
