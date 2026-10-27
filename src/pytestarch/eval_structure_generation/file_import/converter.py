from __future__ import annotations

import ast
from collections.abc import Sequence
from typing import cast

from pytestarch.eval_structure.types import Import, get_parent_modules
from pytestarch.eval_structure_generation.file_import.import_roots import ImportRoots
from pytestarch.eval_structure_generation.file_import.import_types import (
    AbsoluteImport,
    NamedModule,
    RelativeImport,
)


class ImportConverter:
    """Converts all ast imports to custom import types."""

    def __init__(self, import_roots: ImportRoots | None = None) -> None:
        """
        Args:
            import_roots: import roots and their package providers. Imports are
                written relative to an import root (e.g. 'import svc_b.client'), so
                they are probed against scanned modules prefixed with an import
                root: the importer's own scope first, then the one eligible other
                root that provides the top-level package. Submodules stay within the
                selected package provider. Empty disables this probing.
        """
        self._import_roots = import_roots

    def convert(
        self,
        asts: list[NamedModule],
        absolute_import_prefix: str,
        internal_modules: set[str],
    ) -> Sequence[Import]:
        """Converts ast modules to custom import modules. Filters out all modules
        that are not imports.

        Args:
            asts: list of ast modules
            absolute_import_prefix: prefix for modules imported via absolute import
            internal_modules: set of all internal modules
        Returns:
            list of import objects
        """
        module_to_search = asts
        imports: list[Import] = []
        # The graph also creates parent nodes that a partial scan did not parse.
        # Matching a top-level name is enough to detect any hierarchy collision.
        internal_top_level_names = (
            {name.split(".", 1)[0] for name in internal_modules}
            if self._import_roots is not None
            else set()
        )

        while module_to_search:
            module = module_to_search.pop()

            ast_module, module_name = module.module, module.name

            child_nodes: list[ast.AST] = (
                getattr(ast_module, "body", [])
                + getattr(ast_module, "orelse", [])
                + getattr(ast_module, "finalbody", [])
                + getattr(ast_module, "handlers", [])
                + getattr(ast_module, "cases", [])
            )

            if child_nodes:
                module_to_search.extend(
                    [NamedModule(m, module_name) for m in child_nodes]
                )
            else:
                new_imports = self._convert(
                    module.module,
                    module.name,
                    absolute_import_prefix,
                    internal_modules,
                    internal_top_level_names,
                )

                if new_imports:
                    imports.extend(new_imports)

        return imports

    def _convert(
        self,
        module: ast.AST,
        module_name: str,
        absolute_import_prefix: str,
        all_internal_modules: set[str],
        internal_top_level_names: set[str],
    ) -> Sequence[Import] | None:
        """Calculates all imports of the given ast module.

        Args:
            module: module to convert
            module_name: name of the module
            absolute_import_prefix: prefix for modules imported via absolute import
            internal_modules: set of all internal modules
            internal_top_level_names: names of the graph's top-level internal nodes

        Returns:
            list of calculated import objects
        """
        new_imports: Sequence[Import] | None = None

        if isinstance(module, ast.Import):
            new_imports = []
            for alias in module.names:
                importee = self._adjust_with_root_prefix(
                    alias.name,
                    module_name,
                    absolute_import_prefix,
                    all_internal_modules,
                    internal_top_level_names,
                )
                if importee is not None:
                    new_imports.append(AbsoluteImport(module_name, importee))
        elif isinstance(module, ast.ImportFrom):
            if module.level == 0:
                importee = self._adjust_with_root_prefix(
                    cast(str, module.module),
                    module_name,
                    absolute_import_prefix,
                    all_internal_modules,
                    internal_top_level_names,
                )
                new_imports = (
                    [AbsoluteImport(module_name, importee)]
                    if importee is not None
                    else []
                )
                for alias in module.names:
                    submodule_importee = _internal_submodule_importee(
                        alias.name,
                        self._adjust_with_root_prefix(
                            f"{module.module}.{alias.name}",
                            module_name,
                            absolute_import_prefix,
                            all_internal_modules,
                            internal_top_level_names,
                        ),
                        all_internal_modules,
                    )
                    if submodule_importee is not None:
                        new_imports.append(
                            AbsoluteImport(module_name, submodule_importee)
                        )
            else:
                new_imports = []
                # Bare relative forms import the base package at that level as
                # well; a RelativeImport with module None records exactly that
                # (see RelativeImport's docstring).
                new_imports.append(
                    RelativeImport(module_name, module.module, None, module.level)
                )
                importer_hierarchy = get_parent_modules(module_name)
                for alias in module.names:
                    # Probe the exact name the RelativeImport resolves to, built
                    # by the same code that will construct the Import (see
                    # RelativeImport.importee_name).
                    relative_submodule_importee = _internal_submodule_importee(
                        alias.name,
                        RelativeImport.importee_name(
                            importer_hierarchy, module.module, alias.name, module.level
                        ),
                        all_internal_modules,
                    )
                    if relative_submodule_importee is not None:
                        new_imports.append(
                            RelativeImport(
                                module_name, module.module, alias.name, module.level
                            )
                        )

        return new_imports

    def _adjust_with_root_prefix(
        self,
        module_name: str,
        importer: str,
        absolute_import_prefix: str,
        all_internal_modules: set[str],
        internal_top_level_names: set[str],
    ) -> str | None:
        """If the user specifies a module import start point that is not the root path, the ast module names will not contain
        the root path. Hence, they will later be flagged as external modules.
        To avoid this, we prepend the root path and check whether this gives a module that we have detected as an internal module earlier.
        If so, we optimistically assume that this prepended module name is the correct module name.

        The import-root registry handles root-relative imports for package roots,
        module-object scans and projects. It selects a provider before the partial
        scan prefix is probed, so a failed provider cannot fall through to another
        matching name.

        Only absolute imports are affected by this, as the relative imports are resolved internally anyway.

        Args:
            module_name: name of the imported module as written in the code
            importer: name of the module containing the import
            absolute_import_prefix: prefix for modules imported via absolute import
            all_internal_modules: set of all internal modules
            internal_top_level_names: names of the graph's top-level internal nodes

        Returns:
            adjusted module name, or None for an unresolved import whose name
            collides with an internal node (including a parent node).
        """
        if self._import_roots is not None:
            resolution = self._import_roots.resolve(
                module_name, importer, all_internal_modules
            )
            if resolution is not None:
                if (
                    not resolution.is_internal
                    and module_name.split(".", 1)[0] in internal_top_level_names
                ):
                    return None
                return resolution.name

        if absolute_import_prefix:
            prefixed_name = f"{absolute_import_prefix}.{module_name}"
            if prefixed_name in all_internal_modules:
                return prefixed_name

        if (
            self._import_roots is not None
            and module_name not in all_internal_modules
            and module_name.split(".", 1)[0] in internal_top_level_names
        ):
            return None

        return module_name


def _internal_submodule_importee(
    imported_name: str,
    importee: str | None,
    internal_modules: set[str],
) -> str | None:
    """Handles imports of the form "from <module> import <name>": <name> may
    refer to a submodule of <module> instead of an attribute. <importee> is
    the name the import of <module>.<name> resolves to.

    Only names that are known internal modules are taken into account, so
    that imported functions, classes and constants do not end up as imports
    of non-existent modules. "from <module> import *" cannot be resolved
    statically and is therefore skipped.

    Args:
        imported_name: name of the imported submodule or attribute
        importee: module name the import of <module>.<name> resolves to
        internal_modules: set of all internal modules

    Returns:
        the given importee name if it is a known internal module, else None
    """
    if imported_name == "*":
        return None

    return importee if importee in internal_modules else None
