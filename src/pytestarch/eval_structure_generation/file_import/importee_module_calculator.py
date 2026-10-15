from __future__ import annotations

from collections.abc import Sequence

from pytestarch.eval_structure.types import Import
from pytestarch.eval_structure_generation.file_import.internal_module import (
    is_internal_module,
)


class ImporteeModuleCalculator:
    """Adds imported modules that are not internal to the scanned source code, and
    their parent modules, to the modules list."""

    def __init__(self, root_module_name: str) -> None:
        """
        Args:
            root_module_name: prefix of all module names of the scan, e.g. the top
                level package's name. Empty only if module names are derived relative
                to the root without a prefix (module_naming="relative" for a root
                directory without __init__.py).
        """
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
        parsed_top_level_modules = {m.split(".")[0] for m in all_modules}

        for imp in imports:
            importee = imp.importee()

            if not self._is_internal_importee(importee, parsed_top_level_modules):
                extended_modules.update(self._calculate_parent_modules(imp))

        return list(extended_modules)

    def _is_internal_importee(
        self, importee: str, parsed_top_level_modules: set[str]
    ) -> bool:
        """An importee is internal if it belongs to the scanned source code; internal
        importees must not be added to the module list as external dependencies.

        With the default naming, all module names carry the root module name as
        prefix, and root-relative imports are resolved to their prefixed names by the
        converter beforehand, so the prefix decides: an importee without it is
        external.

        With relative naming, module names carry no prefix, so the importee's top
        level module decides: the importee is internal if that module is among the
        top level modules of the parsed source code. A sibling package outside a
        partial scan's module_path is therefore external, just as its bare-name
        import is with the default naming.

        Args:
            importee: name of the imported module
            parsed_top_level_modules: top level modules of all parsed modules

        Returns:
            True if the importee belongs to the scanned source code
        """
        if self._root_module_name:
            return is_internal_module(importee, self._root_module_name)

        return importee.split(".")[0] in parsed_top_level_modules

    def _calculate_parent_modules(self, imp: Import) -> set[str]:
        modules = {imp.importee()}
        modules.update(imp.importee_parent_modules())

        return modules
