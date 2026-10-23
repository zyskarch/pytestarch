from __future__ import annotations

import ast
from collections.abc import Callable, Sequence

from pytestarch.eval_structure.types import Import
from pytestarch.eval_structure_generation.file_import.import_types import (
    AbsoluteImport,
    NamedModule,
    RelativeImport,
)


class ImportConverter:
    """Converts all ast imports to custom import types."""

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
                    [NamedModule(m, module_name) for m in child_nodes]  # type: ignore
                )
            else:
                new_imports = self._convert(
                    module.module,
                    module.name,
                    absolute_import_prefix,
                    internal_modules,
                )

                if new_imports:
                    imports.extend(new_imports)

        return imports

    def _convert(
        self,
        module: ast.Module,
        module_name: str,
        absolute_import_prefix: str,
        all_internal_modules: set[str],
    ) -> Sequence[Import] | None:
        """Calculates all imports of the given ast module.

        Args:
            module: module to convert
            module_name: name of the module
            absolute_import_prefix: prefix for modules imported via absolute import
            internal_modules: set of all internal modules

        Returns:
            list of calculated import objects
        """
        new_imports: Sequence[Import] | None = None

        if isinstance(module, ast.Import):
            new_imports = []
            for alias in module.names:
                new_imports.append(
                    AbsoluteImport(
                        module_name,
                        self._adjust_with_root_prefix(
                            alias.name, absolute_import_prefix, all_internal_modules
                        ),
                    )
                )
        elif isinstance(module, ast.ImportFrom):
            if module.level == 0:
                new_imports = [
                    AbsoluteImport(
                        module_name,
                        self._adjust_with_root_prefix(
                            module.module,  # type: ignore
                            absolute_import_prefix,
                            all_internal_modules,
                        ),
                    )
                ]
                for alias in module.names:
                    submodule_import = self._import_of_internal_submodule(
                        alias.name,
                        all_internal_modules,
                        lambda name: AbsoluteImport(
                            module_name,
                            self._adjust_with_root_prefix(
                                f"{module.module}.{name}",
                                absolute_import_prefix,
                                all_internal_modules,
                            ),
                        ),
                    )
                    if submodule_import is not None:
                        new_imports.append(submodule_import)
            else:
                new_imports = []
                # Bare relative forms import the base package at that level as
                # well; a RelativeImport with module None records exactly that
                # (see RelativeImport's docstring).
                new_imports.append(
                    RelativeImport(module_name, module.module, None, module.level)
                )
                for alias in module.names:
                    relative_submodule_import = self._import_of_internal_submodule(
                        alias.name,
                        all_internal_modules,
                        lambda name: RelativeImport(
                            module_name, module.module, name, module.level
                        ),
                    )
                    if relative_submodule_import is not None:
                        new_imports.append(relative_submodule_import)

        return new_imports

    @classmethod
    def _import_of_internal_submodule(
        cls,
        imported_name: str,
        all_internal_modules: set[str],
        create_import: Callable[[str], Import],
    ) -> Import | None:
        """Handles imports of the form "from <module> import <name>": <name> may
        refer to a submodule of <module> instead of an attribute. In this case,
        the import is also an import of <module>.<name>.

        Only names that are known internal modules are taken into account, so
        that imported functions, classes and constants do not end up as imports
        of non-existent modules. "from <module> import *" cannot be resolved
        statically and is therefore skipped.

        Args:
            imported_name: name of the imported submodule or attribute
            all_internal_modules: set of all internal modules
            create_import: builds the import of the submodule for a given name

        Returns: import of the submodule, or None if the imported name is not a known internal module
        """
        if imported_name == "*":
            return None

        candidate = create_import(imported_name)

        if candidate.importee() not in all_internal_modules:
            return None

        return candidate

    @classmethod
    def _adjust_with_root_prefix(
        cls,
        module_name: str,
        absolute_import_prefix: str,
        all_internal_modules: set[str],
    ) -> str:
        """If the user specifies a module import start point that is not the root path, the ast module names will not contain
        the root path. Hence, they will later be flagged as external modules.
        To avoid this, we prepend the root path and check whether this gives a module that we have detected as an internal module earlier.
        If so, we optimistically assume that this prepended module name is the correct module name.

        Only absolute imports are affected by this, as the relative imports are resolved internally anyway.
        """
        potential_full_name = f"{absolute_import_prefix}.{module_name}"

        if potential_full_name in all_internal_modules:
            return potential_full_name

        return module_name
