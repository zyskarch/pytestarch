from typing import List

from pytestarch.importer.import_types import Import


class ImportFilter:
    """Filters out imports of external modules from the list of all imports.
    External modules are all modules that are not submodules of the configured module to search for imports.
    """

    def __init__(self, exclude_external_libraries: bool, root_module_name: str) -> None:
        """
        Args:
            exclude_external_libraries: If True, external modules will be filtered out, otherwise this class implements a no-op.
            root_module_name: name of the module that determines which modules are considered external. If a module
                is a submodule of this module, it is considered internal.
        """
        self._exclude_external_libraries = exclude_external_libraries
        self._root_module_name = root_module_name

    def filter(self, imports: List[Import]) -> List[Import]:
        """According to the configuration, imports will be filtered.

        Args:
            imports: list of imports to be filtered
        Returns:
            filtered list of imports
        """
        if not self._exclude_external_libraries:
            return imports

        return [i for i in imports if self._is_internal_import(i)]

    def _is_internal_import(self, i: Import) -> bool:
        importee = i.importee()

        return importee.startswith(self._root_module_name)
