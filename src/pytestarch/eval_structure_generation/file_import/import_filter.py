from __future__ import annotations

from collections.abc import Sequence

from pytestarch.eval_structure.types import Import
from pytestarch.eval_structure_generation.file_import.config import Config
from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter


class ExternalImportFilter:
    """Filters out imports of (some) external modules from the list of all imports.
    External modules are all modules that are not contained in the set of modules
    detected under the scanned root.

    Two possibilities: either all external modules are filtered out, or only those matching given regex patterns.
    """

    def __init__(
        self,
        exclude_external_libraries: bool,
        internal_modules: set[str],
        external_exclusions: tuple[str, ...],
    ) -> None:
        """
        Args:
            exclude_external_libraries: If True, external modules will be filtered out, otherwise this class implements a no-op.
            internal_modules: set of all modules detected under the scanned root.
                Every importee contained in this set is considered internal.
            external_exclusions: regex pattern: all external modules that match it shall be filtered out.
        """
        self._exclude_external_libraries = exclude_external_libraries
        self._internal_modules = internal_modules
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
        """An import is internal if its importee is contained in the set of modules
        detected under the scanned root.
        """
        return i.importee() in self._internal_modules

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
