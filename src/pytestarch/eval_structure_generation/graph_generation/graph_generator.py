from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

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
from pytestarch.eval_structure_generation.file_import.importee_module_calculator import (
    ImporteeModuleCalculator,
)
from pytestarch.eval_structure_generation.file_import.parser import Parser


def _get_absolute_import_prefix(
    path_diff_between_root_and_module: str, root_path: Path, module_path: Path
) -> str:
    if not _actual_difference_between_root_and_module(
        path_diff_between_root_and_module
    ):
        return ""

    return str(module_path.parent.relative_to(root_path.parent)).replace(os.sep, ".")


def generate_graph(
    root_path: Path,
    module_path: Path,
    path_diff_between_root_and_module: str,
    exclusions: tuple[str, ...],
    exclude_external_libraries: bool,
    level_limit: int | None,
    external_exclusions: tuple[str, ...] | None,
) -> EvaluableArchitectureGraph:
    level_limit = _add_extra_levels_to_limit_if_root_and_module_path_differ(
        level_limit,
        path_diff_between_root_and_module,
    )

    file_filter = FileFilter(Config(exclusions))
    parser = Parser(file_filter, root_path)
    all_modules, ast = parser.parse(module_path)

    internal_module_name = _get_internal_module_name(
        path_diff_between_root_and_module, root_path
    )

    imports = ImportConverter().convert(
        ast,
        _get_absolute_import_prefix(
            path_diff_between_root_and_module, root_path, module_path
        ),
        _get_all_internal_modules(all_modules, internal_module_name),
    )

    if external_exclusions is None:
        external_exclusions = ()

    import_filter = ExternalImportFilter(
        exclude_external_libraries, internal_module_name, external_exclusions
    )
    imports = import_filter.filter(imports)

    all_modules = _append_external_modules_to_module_list(
        all_modules,
        exclude_external_libraries,
        imports,
        root_path.name,
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


def _get_internal_module_name(
    path_diff_between_root_and_module: str, root_path: Path
) -> str:
    """In general, all internal modules should start with the root module name to be able to differentiate between
    internal and external modules. If the root and base module differ, the modules between them also need to be taken
    into account, as not-root.a.b-modules are external, but root.a.b.base-modules are internal.

    The returned name carries no trailing dot: it is matched boundary-safely, so the internal
    module itself ('root', or 'root.a.b' if the scanned module lies below the root) also counts as internal.
    """
    internal_module_name = root_path.name

    if _actual_difference_between_root_and_module(path_diff_between_root_and_module):
        internal_module_name += f".{path_diff_between_root_and_module}"

    return internal_module_name


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


def _get_all_internal_modules(
    modules: list[str], internal_module_name: str
) -> set[str]:
    """All parsed modules that are the internal module itself or its submodules.

    This set backs the converter's exact-name lookups when resolving 'from <module>
    import <name>' statements to submodule imports and when adjusting absolute import
    prefixes. The internal module itself is included, so that imports of the scanned
    module (e.g. 'import app' for a partial scan of module 'src.app') resolve to it
    instead of creating a spurious external node.
    """
    return {m for m in modules if is_internal_module(m, internal_module_name)}
