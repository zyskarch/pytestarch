import ast
import os
from pathlib import Path
from typing import List, Optional, Tuple

from pytestarch.importer.file_filter import FileFilter
from pytestarch.importer.import_types import NamedModule

PYTHON_FILE_SUFFIX = ".py"


class Parser:
    """Parses all files that match given criteria starting at a source path."""

    def __init__(self, filter: FileFilter, source_root: Path) -> None:
        self._filter = filter
        self._source_root = source_root

    def parse(self, path: Path) -> Tuple[List[str], List[NamedModule]]:
        """Reads all python files in the given path and returns list of ast
        modules with names.

        Args:
            path: either to a file or to a directory
        Returns:
            list of python modules, one per python file
        """
        self._all_modules = []

        paths = [path]
        modules = []

        while paths:
            path = paths.pop()

            if path.is_dir():
                if not self._filter.is_excluded(path):
                    module_name = self._get_module_name(path)
                    if module_name:
                        self._all_modules.append(module_name)
                    paths.extend(path.iterdir())
            else:
                new_module = self._parse_file(path)
                if new_module:
                    modules.append(new_module)

        return self._all_modules, modules

    def _parse_file(self, path: Path) -> Optional[NamedModule]:
        """Converts a given python file to an ast module and its name."""
        absolute_path = path.resolve()
        if self._file_should_be_parsed(absolute_path):
            with open(absolute_path, "r") as file:
                code = file.read()

            module_name = self._get_module_name(path)
            self._all_modules.append(module_name)

            return NamedModule(
                ast.parse(code),
                module_name,
            )

    def _get_module_name(self, path: Path) -> str:
        """Determine full name of module, such as A.B.C"""
        module_path = path.relative_to(self._source_root)

        if str(module_path) == ".":
            return self._source_root.name

        module_without_file_suffix = module_path.with_suffix("")
        module_in_dot_notation = str(module_without_file_suffix).replace(os.sep, ".")

        return f"{self._source_root.name}.{module_in_dot_notation}"

    def _file_should_be_parsed(self, path: Path) -> bool:
        """Returns True if path represents a python file that does not match any exclusion filters."""
        correct_file_type = path.suffix == PYTHON_FILE_SUFFIX
        file_excluded = self._filter.is_excluded(path)

        return correct_file_type and not file_excluded
