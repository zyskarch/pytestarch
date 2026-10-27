"""Import roots and package providers for multi-module scans.

An import root is a directory that contains top-level packages and is therefore
on the import path (``sys.path``) for the code below it. Module names derived
from a scan root are path-based, so an import written relative to an import root
must be qualified with that root's path prefix before it can be matched against
the scanned modules.

Import roots are discovered from the file system, never from the scanned or
filtered module set, so scan exclusions and partial scans cannot change which
project provides a package.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

PROJECT_MARKERS = ("pyproject.toml", "setup.py", "setup.cfg")

# A directory that contains these is a conventional source root, even without
# project metadata.
CONVENTIONAL_SOURCE_ROOT = "src"


@dataclass(frozen=True)
class ImportRoot:
    """A directory that contains top-level packages.

    Attributes:
        prefix: module name prefix of the directory, e.g. ``svc_a.src``.
        packages: names of the top-level packages and Python modules directly inside
            the directory.
        scope: project the root belongs to; importers below this scope prefer the
            scope's roots over roots of other projects.
        cross_project: whether roots of other scopes may resolve imports against
            this root. Local-only roots (e.g. an unmarked directory of examples)
            still serve importers inside the same scope.
    """

    prefix: str
    packages: frozenset[str]
    scope: str
    cross_project: bool = True


@dataclass(frozen=True)
class ImportResolution:
    """A resolved internal name or an unresolved external import name."""

    name: str
    is_internal: bool


class ImportRoots:
    """Resolves an absolute import against known import roots.

    Resolution order:
    1. Roots of the importer's own scope, in discovery order (e.g. a project's
       flat root before its ``src`` root).
    2. Roots of other scopes, but only if exactly one eligible root provides the
       imported top-level package. Several providers stay ambiguous.

    A selected provider keeps the import unresolved if the requested submodule
    is not part of the scanned modules; another provider is never substituted.
    """

    def __init__(self, roots: Iterable[ImportRoot]) -> None:
        self._roots = tuple(roots)
        self._scopes = tuple(
            sorted({root.scope for root in self._roots}, key=len, reverse=True)
        )

    @classmethod
    def for_named_root(cls, root_path: Path, root_module_name: str) -> ImportRoots:
        """Resolve root-relative imports for package and module-object scans.

        The naming prefix may include namespace parents. Availability comes from
        disk, so a partial scan or exclusion cannot substitute another provider.
        """
        names = _module_names(root_path)
        names.update(directory.name for directory in _sub_directories(root_path))
        # An import of the root itself must not become root.root. Directories
        # also participate here to preserve probing through namespace children.
        names.discard(root_module_name)
        return cls(
            (
                ImportRoot(
                    prefix=root_module_name,
                    packages=frozenset(names),
                    scope=root_module_name,
                ),
            )
        )

    @classmethod
    def discover(
        cls,
        root_path: Path,
        root_module_name: str,
        explicit_roots: Sequence[Path] | None = None,
    ) -> ImportRoots:
        """Discover import roots below a container scan root.

        Every direct child directory that holds packages or .py modules is a local
        root: importers inside its scope can resolve imports against it. Conventional ``src``
        directories directly below the scan root, projects with a project marker
        and explicitly passed roots are eligible to provide packages to other
        scopes. A child project's own ``src`` folder requires a project marker or
        an explicit root to provide packages to other scopes. If ``explicit_roots`` is
        given, it replaces the automatic cross-project roots; local roots remain.

        A package root (a root with ``__init__.py``) supplies one import root with
        its package name as the prefix.
        """
        if (root_path / "__init__.py").is_file():
            return cls.for_named_root(root_path, root_module_name)

        explicit = tuple(explicit_roots or ())
        auto_cross_project = explicit_roots is None

        roots: dict[str, ImportRoot] = {}
        if is_import_root(root_path):
            roots[_prefix(root_module_name, root_path, root_path)] = ImportRoot(
                prefix=_prefix(root_module_name, root_path, root_path),
                packages=frozenset(_module_names(root_path)),
                scope=root_module_name,
                cross_project=auto_cross_project,
            )

        local_roots: dict[str, ImportRoot] = {}
        for directory in _sub_directories(root_path):
            scope = _prefix(root_module_name, root_path, directory)
            marked = _has_project_marker(directory) or _has_project_marker(
                directory / "src"
            )
            conventional = directory.name == CONVENTIONAL_SOURCE_ROOT
            if is_import_root(directory):
                _add_root(
                    local_roots,
                    directory,
                    root_module_name,
                    root_path,
                    scope,
                    cross_project=auto_cross_project and (marked or conventional),
                )
            source_dir = directory / "src"
            if is_import_root(source_dir):
                _add_root(
                    local_roots,
                    source_dir,
                    root_module_name,
                    root_path,
                    scope,
                    cross_project=auto_cross_project and marked,
                )

        if explicit_roots is None:
            roots.update(local_roots)
        else:
            for path in explicit:
                _add_root(
                    roots,
                    path,
                    root_module_name,
                    root_path,
                    _root_scope(path, root_module_name, root_path),
                    cross_project=True,
                )
            for prefix, local_root in local_roots.items():
                roots.setdefault(prefix, local_root)

        return cls(roots.values())

    def resolve(
        self,
        module_name: str,
        importer: str,
        internal_modules: set[str],
    ) -> ImportResolution | None:
        """Resolve an absolute import against the known import roots.

        Returns:
            The qualified internal name or an unresolved external name if the
            provider is ambiguous, disabled or outside the scanned module set.
            None if no root knows the imported top-level package or module.
        """
        package_name = module_name.split(".", 1)[0]
        scope = self._scope_for(importer)

        if scope is not None:
            for root in self._roots:
                if root.scope == scope and package_name in root.packages:
                    return self._qualified(root, module_name, internal_modules)

        candidates = [
            root
            for root in self._roots
            if root.cross_project
            and root.scope != scope
            and package_name in root.packages
        ]

        if not candidates:
            if any(package_name in root.packages for root in self._roots):
                return ImportResolution(module_name, is_internal=False)
            return None
        if len(candidates) != 1:
            return ImportResolution(module_name, is_internal=False)

        return self._qualified(candidates[0], module_name, internal_modules)

    def _scope_for(self, importer: str) -> str | None:
        for scope in self._scopes:
            if scope == "" or importer == scope or importer.startswith(f"{scope}."):
                return scope

        return None

    @staticmethod
    def _qualified(
        root: ImportRoot,
        module_name: str,
        internal_modules: set[str],
    ) -> ImportResolution:
        resolved = f"{root.prefix}.{module_name}" if root.prefix else module_name
        if resolved in internal_modules:
            return ImportResolution(resolved, is_internal=True)
        return ImportResolution(module_name, is_internal=False)


def _add_root(
    roots: dict[str, ImportRoot],
    directory: Path,
    root_module_name: str,
    root_path: Path,
    scope: str,
    cross_project: bool,
) -> None:
    prefix = _prefix(root_module_name, root_path, directory)
    existing = roots.get(prefix)
    roots[prefix] = ImportRoot(
        prefix=prefix,
        packages=frozenset(_module_names(directory)),
        scope=scope,
        cross_project=cross_project or bool(existing and existing.cross_project),
    )


def _prefix(root_module_name: str, root_path: Path, directory: Path) -> str:
    if directory == root_path:
        return root_module_name

    relative = str(directory.relative_to(root_path)).replace(os.sep, ".")
    return f"{root_module_name}.{relative}" if root_module_name else relative


def _root_scope(path: Path, root_module_name: str, root_path: Path) -> str:
    if path == root_path:
        return root_module_name

    project = (
        path.parent
        if path.name == CONVENTIONAL_SOURCE_ROOT and path.parent != root_path
        else path
    )
    return _prefix(root_module_name, root_path, project)


def _module_names(directory: Path) -> set[str]:
    try:
        with os.scandir(directory) as entries:
            return {
                entry.name if entry.is_dir() else Path(entry.name).stem
                for entry in entries
                if (entry.is_dir() and _is_package(directory / entry.name))
                or (entry.is_file() and entry.name.endswith(".py"))
            }
    except OSError:
        return set()


def _has_project_marker(directory: Path) -> bool:
    return any((directory / marker).is_file() for marker in PROJECT_MARKERS)


def is_import_root(directory: Path) -> bool:
    """Whether a non-package directory contains top-level packages or .py modules."""
    return not _is_package(directory) and bool(_module_names(directory))


def _sub_directories(path: Path) -> list[Path]:
    try:
        with os.scandir(path) as entries:
            directories = [path / entry.name for entry in entries if entry.is_dir()]
    except OSError:
        return []

    return sorted(directories)


def _is_package(directory: Path) -> bool:
    return (directory / "__init__.py").is_file()
