import os
from pathlib import Path
from typing import List

from pytestarch.importer.import_types import Import


class ImportPathPadder:
    """Ensures that paths to imported internal modules match path structure of importing internal modules."""

    @classmethod
    def pad(cls, imports: List[Import], root_path: Path, module_path: Path) -> str:
        """
        Appends a prefix to all internal import module paths to ensure that importing and imported modules have the
        same module prefix. This becomes necessary if the root and module path are not identical.

        Args:
            imports: list of Imports to update
            root_path: Path to the root module
            module_path: Path to the top level module to scan

        Returns:
            appended prefix based on the difference between root and module path
        """
        short_prefix = str(module_path.relative_to(root_path)).replace(os.sep, ".")
        # drop name of module_path module itself, as this is already part of the import paths
        full_prefix = ".".join(short_prefix.split(".")[:-1])

        for imp in imports:
            if not imp.importer().startswith(full_prefix):
                imp.update_import_prefixes(full_prefix, module_path.name)

        return full_prefix
