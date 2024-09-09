from __future__ import annotations

from collections.abc import Sequence

from pytestarch.eval_structure.types import Import
from pytestarch.eval_structure_generation.file_import.config import Config
from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter


class ExternalImportFilter:
    """Filters out imports of (some) external modules from the list of all imports.
    External modules are all modules that are not submodules of the configured module to search for imports.

    Two possibilities: either all external modules are filtered out, or only those matching given regex patterns.
    """

    def __init__(
        self,
        exclude_external_libraries: bool,
        root_module_name: str,
        external_exclusions: tuple[str, ...],
    ) -> None:
        """
        Args:
            exclude_external_libraries: If True, external modules will be filtered out, otherwise this class implements a no-op.
            root_module_name: name of the module that determines which modules are considered external. If a module
                is a submodule of this module, it is considered internal.
            external_exclusions: regex pattern: all external modules that match it shall be filtered out.
        """
        self._exclude_external_libraries = exclude_external_libraries
        self._root_module_name = root_module_name
        self._external_exclusion_filter = FileFilter(Config(external_exclusions))

    def filter(self, imports: Sequence[Import]) -> Sequence[Import]:
        """According to the configuration, imports will be filtered.

        Args:
            imports: list of imports to be filtered
        Returns:
            filtered list of imports
        """
        if (
            not self._exclude_external_libraries
            and not self._external_exclusion_filter.has_filter()
        ):
            return imports

        # is this is set, then _exclude_external_libraries is False, as asserted by previously executed code
        if self._external_exclusion_filter.has_filter():
            return [
                i for i in imports if self._is_internal_or_retained_external_import(i)
            ]

        return [i for i in imports if self._is_internal_import(i)]

    def _is_internal_import(self, i: Import) -> bool:
        importee = i.importee()

        return importee.startswith(self._root_module_name)

    def _is_internal_or_retained_external_import(self, i: Import) -> bool:
        if self._is_internal_import(i):
            return True

        importee = i.importee()

        excluded = self._external_exclusion_filter.is_excluded(importee)
        any_parent_excluded = any(
            self._external_exclusion_filter.is_excluded(parent)
            for parent in i.importee_parent_modules()
        )
        return not (excluded or any_parent_excluded)
