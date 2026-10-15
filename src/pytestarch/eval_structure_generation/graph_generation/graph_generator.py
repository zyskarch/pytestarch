from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.module_name_boundaries import is_internal_module
from pytestarch.eval_structure.networkxgraph import NetworkxGraph, Node
from pytestarch.eval_structure.types import Import
from pytestarch.eval_structure_generation.file_import.config import Config
from pytestarch.eval_structure_generation.file_import.converter import ImportConverter
from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter
from pytestarch.eval_structure_generation.file_import.import_filter import (
    ExternalImportFilter,
)
from pytestarch.eval_structure_generation.file_import.import_types import NamedModule
from pytestarch.eval_structure_generation.file_import.importee_module_calculator import (
    ImporteeModuleCalculator,
)
from pytestarch.eval_structure_generation.file_import.parser import Parser

MODULE_NAMING = Literal["root_dir", "relative"]
"""Naming of module names relative to the root path:

- 'root_dir' (default): module names are prefixed with the root directory's name,
  whether or not the root itself is a Python module (contains an __init__.py).
- 'relative': only applies if the root is no Python module itself; module names are
  then derived relative to it, without a prefix.
"""


def _get_absolute_import_prefix(
    path_diff_between_root_and_module: str,
    root_path: Path,
    module_path: Path,
    root_module_name: str,
) -> str:
    if not _actual_difference_between_root_and_module(
        path_diff_between_root_and_module
    ):
        return ""

    # If module names carry the root module name as prefix, absolute imports are
    # written relative to the root path's parent directory; for prefix-less module
    # names (relative naming) they are written relative to the root path itself.
    base = root_path.parent if root_module_name else root_path
    prefix = str(module_path.parent.relative_to(base)).replace(os.sep, ".")

    return "" if prefix == "." else prefix


def generate_graph(
    root_path: Path,
    module_path: Path,
    path_diff_between_root_and_module: str,
    exclusions: tuple[str, ...],
    exclude_external_libraries: bool,
    level_limit: int | None,
    external_exclusions: tuple[str, ...] | None,
    module_naming: MODULE_NAMING = "root_dir",
) -> EvaluableArchitectureGraph:
    level_limit = _add_extra_levels_to_limit_if_root_and_module_path_differ(
        level_limit,
        path_diff_between_root_and_module,
    )

    root_is_package = (root_path / "__init__.py").is_file()

    # A Python package root's name is the common prefix of all module names,
    # independently of module_naming; for a container directory (e.g. a 'src' folder)
    # the naming decision below applies.
    if root_is_package:
        root_module_name = root_path.name
    elif module_naming == "relative":
        root_module_name = ""
    else:
        root_module_name = root_path.name

    if level_limit is not None and not root_module_name:
        # With relative naming the root itself is not a module and occupies no
        # hierarchy level, so the same limit covers one level less of module names.
        level_limit -= 1

        if level_limit < 0:
            raise ValueError(
                "level_limit must be at least 1 when module_naming is 'relative' and "
                "the root path is a container directory (no __init__.py): the root "
                "itself is not a module, so a limit of 0 would leave no module."
            )

    all_modules, ast = _get_all_ast_modules(
        module_path, root_path, exclusions, root_module_name
    )

    internal_module_name = _get_internal_module_name(
        path_diff_between_root_and_module, root_module_name
    )

    # Parsed module names include every non-excluded directory, so imports of parent
    # packages (e.g. 'from package2 import module2') are matched by the detected set
    # directly, without a parent closure.
    internal_modules = _get_all_internal_modules(all_modules, internal_module_name)

    imports = _get_imports_from_ast(
        ast,
        _get_absolute_import_prefix(
            path_diff_between_root_and_module, root_path, module_path, root_module_name
        ),
        internal_modules,
        root_module_name,
    )

    if external_exclusions is None:
        external_exclusions = ()

    imports = _remove_excluded_imports(
        exclude_external_libraries,
        imports,
        internal_modules,
        external_exclusions,
    )

    all_modules = _append_external_modules_to_module_list(
        all_modules,
        exclude_external_libraries,
        imports,
        root_module_name,
        external_exclusions,
    )
    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports, level_limit))


def _append_external_modules_to_module_list(
    all_modules: list[Node],
    exclude_external_libraries: bool,
    imports: Sequence[Import],
    root_module_name: str,
    external_exclusions: tuple[str, ...],
) -> list[Node]:
    """External modules are not detected as modules when importing the source folder - but they will of course show up
    in the imports. To ensure that all edges in the graph have nodes attached, the external modules need to be added to
    the list of modules/nodes."""
    if exclude_external_libraries:
        return all_modules

    all_modules = ImporteeModuleCalculator(root_module_name).calculate_importee_modules(
        imports,
        all_modules,
    )

    file_filter = FileFilter(Config(external_exclusions))

    if not file_filter.has_filter():
        return all_modules

    return [module for module in all_modules if not file_filter.is_excluded(module)]


def _remove_excluded_imports(
    exclude_external_libraries: bool,
    imports: Sequence[Import],
    internal_modules: set[str],
    external_exclusions: tuple[str, ...],
) -> Sequence[Import]:
    import_filter = ExternalImportFilter(
        exclude_external_libraries, internal_modules, external_exclusions
    )
    return import_filter.filter(imports)


def _get_internal_module_name(
    path_diff_between_root_and_module: str, root_module_name: str
) -> str:
    """In general, all internal modules should start with the root module name to be able to differentiate between
    internal and external modules. If the root and base module differ, the modules between them also need to be taken
    into account, as not-root.a.b-modules are external, but root.a.b.base-modules are internal.

    The returned name carries no trailing dot: it is matched boundary-safely, so the internal
    module itself also counts as internal. If module names carry no prefix at all (relative
    module naming for a container root), it is only the path difference between root and
    module (if any).
    """
    if _actual_difference_between_root_and_module(path_diff_between_root_and_module):
        return (
            f"{root_module_name}.{path_diff_between_root_and_module}"
            if root_module_name
            else path_diff_between_root_and_module
        )

    return root_module_name


def _actual_difference_between_root_and_module(
    path_diff_between_root_and_module: str,
) -> bool:
    return path_diff_between_root_and_module != "."


def _add_extra_levels_to_limit_if_root_and_module_path_differ(
    level_limit: int | None, path_diff_between_root_and_module: str
) -> int | None:
    """If the root and base module are not the same, the level limit needs to be increased by the number of levels
    between these two modules. Otherwise, the actual base module might not even be in the graph, let alone all required
    levels below it."""
    if level_limit is None:
        return None

    if _actual_difference_between_root_and_module(path_diff_between_root_and_module):
        levels = len(path_diff_between_root_and_module.split("."))
        level_limit += levels

    return level_limit


def _get_imports_from_ast(
    ast: list[NamedModule],
    absolute_import_prefix: str,
    all_internal_modules: set[str],
    root_module_name: str,
) -> Sequence[Import]:
    converter = ImportConverter()
    return converter.convert(
        ast, absolute_import_prefix, all_internal_modules, root_module_name
    )


def _get_all_ast_modules(
    module_path: Path,
    root_path: Path,
    exclusions: tuple[str, ...],
    root_module_name: str,
) -> tuple[list[str], list[NamedModule]]:
    config = Config(exclusions)
    file_filter = FileFilter(config)

    parser = Parser(file_filter, root_path, root_module_name)
    all_modules, ast = parser.parse(module_path)
    return all_modules, ast


def _get_all_internal_modules(
    modules: list[str], internal_module_name: str
) -> set[str]:
    """All parsed modules that are the internal module itself or its submodules.

    This set backs the converter's exact-name lookups ('from <module> import <name>'
    resolution, absolute import prefix adjustment) and the import filter. The internal
    module itself is included, so that imports of the scanned module count as internal.
    """
    if not internal_module_name:
        # Relative module naming for a container root: every detected module lies
        # under the scanned root.
        return set(modules)

    return {m for m in modules if is_internal_module(m, internal_module_name)}
