from __future__ import annotations

import ast
import os
from operator import itemgetter
from pathlib import Path

from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter
from pytestarch.eval_structure_generation.file_import.import_types import NamedModule

PYTHON_FILE_SUFFIX = ".py"

_DirectoryEntry = tuple[str, Path, bool]  # name, resolved path, is directory


class Parser:
    """Parses all files that match given criteria starting at a source path."""

    def __init__(self, filter: FileFilter, source_root: Path) -> None:
        """
        Args:
            filter: filter for files and directories that shall not be parsed
            source_root: directory the searched files are located in, as reached. It
                is used for module names, so a symlinked root keeps its link name, and
                it keeps the path form it was given in (relative or absolute), so
                exclusions match the form the caller used.
        """
        self._filter = filter
        # As reached: neither resolved nor made absolute. A symlinked root keeps
        # the name it was reached under, which is also the name Python imports
        # it as, and a relative root keeps the walk paths relative so that
        # exclusions written relative to the working directory match. Resolved
        # (symlink-free) paths are only used internally, for reading file
        # content and for cycle and duplicate detection.
        self._source_root = source_root

    def parse(self, path: Path) -> tuple[list[str], list[NamedModule]]:
        """Reads all python files in the given path and returns list of ast
        modules with names.

        Args:
            path: either to a file or to a directory
        Returns:
            list of python modules, one per python file and module name
        """
        self._all_modules: list[str] = []
        self._parsed_asts: dict[Path, ast.Module] = {}
        self._directory_entries: dict[Path, tuple[_DirectoryEntry, ...]] = {}

        naming_start = path
        try:
            resolved = naming_start.resolve()
        except (OSError, RuntimeError):
            return self._all_modules, []
        if not resolved.exists():
            return self._all_modules, []

        stack: list[tuple[Path, Path, bool, frozenset[Path], bool]] = [
            (naming_start, resolved, naming_start.is_dir(), frozenset(), False)
        ]
        modules: list[NamedModule] = []
        visited: set[Path] = set()

        # One walk for real and alias paths alike. Each stack entry is popped
        # exactly once, so each module name is emitted once per path it is
        # reached under: a directory under its real path on the first visit
        # (visited), and again as an alias (is_alias, counted against the
        # alias budget) when reached through another path. Every file is parsed
        # once (cache in _parse_file) and the ancestor set terminates symlink
        # cycles.
        while stack:
            naming_path, resolved_path, is_directory, ancestors, is_alias = stack.pop()

            if is_directory:
                if resolved_path in ancestors:
                    continue
                if self._filter.is_excluded(naming_path):
                    continue
                if not is_alias and resolved_path in visited:
                    # Reached again through another path: emit this subtree
                    # under the alias path, with alias budget accounting.
                    is_alias = True
                if is_alias:
                    self._add_alias_module_name(naming_path)
                else:
                    visited.add(resolved_path)
                    self._add_module_name(naming_path)

                child_ancestors = ancestors | {resolved_path}
                entries = self._entries(naming_path, resolved_path)
                for name, child_resolved, child_is_directory in reversed(entries):
                    stack.append(
                        (
                            naming_path / name,
                            child_resolved,
                            child_is_directory,
                            child_ancestors,
                            is_alias,
                        )
                    )
            else:
                new_module = self._parse_file(naming_path, resolved_path)
                if new_module:
                    modules.append(new_module)

        return self._all_modules, modules

    def _entries(
        self, naming_path: Path, resolved_path: Path
    ) -> tuple[_DirectoryEntry, ...]:
        """Directory entries, cached by their real directory.

        Resolving every entry would reintroduce a per-file syscall. Only symlink
        entries are resolved; for regular entries the resolved child is the
        resolved parent plus the entry name.
        """
        cached = self._directory_entries.get(resolved_path)
        if cached is not None:
            return cached

        entries: list[_DirectoryEntry] = []
        try:
            with os.scandir(naming_path) as directory:
                for entry in directory:
                    entry_path = naming_path / entry.name
                    try:
                        if entry.is_symlink():
                            child_resolved = entry_path.resolve()
                            if not child_resolved.exists():
                                continue
                            child_is_directory = child_resolved.is_dir()
                        else:
                            child_resolved = resolved_path / entry.name
                            child_is_directory = entry.is_dir(follow_symlinks=False)
                    except (OSError, RuntimeError):
                        continue
                    entries.append((entry.name, child_resolved, child_is_directory))
        except OSError:
            pass

        entries.sort(key=itemgetter(0))
        result = tuple(entries)
        self._directory_entries[resolved_path] = result
        return result

    def _parse_file(self, path: Path, resolved_path: Path) -> NamedModule | None:
        """Converts a given python file to an ast module and its name."""
        if not self._file_should_be_parsed(path):
            return None

        parsed = self._parsed_asts.get(resolved_path)
        if parsed is None:
            parsed = ast.parse(resolved_path.read_bytes())
            self._parsed_asts[resolved_path] = parsed

        module_name = self._get_module_name(path)
        self._all_modules.append(module_name)

        return NamedModule(parsed, module_name)

    def _add_module_name(self, path: Path) -> None:
        module_name = self._get_module_name(path)
        if module_name:
            self._all_modules.append(module_name)

    def _add_alias_module_name(self, path: Path) -> None:
        self._add_module_name(path)

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
