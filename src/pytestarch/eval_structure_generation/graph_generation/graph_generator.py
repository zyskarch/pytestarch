from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure.networkxgraph import NetworkxGraph, Node
from pytestarch.eval_structure.types import Import
from pytestarch.eval_structure_generation.file_import.config import Config
from pytestarch.eval_structure_generation.file_import.converter import ImportConverter
from pytestarch.eval_structure_generation.file_import.file_filter import FileFilter
from pytestarch.eval_structure_generation.file_import.import_filter import ImportFilter
from pytestarch.eval_structure_generation.file_import.import_types import NamedModule
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
) -> EvaluableArchitectureGraph:
    level_limit = _add_extra_levels_to_limit_if_root_and_module_path_differ(
        level_limit,
        path_diff_between_root_and_module,
    )

    all_modules, ast = _get_all_ast_modules(module_path, root_path, exclusions)

    internal_module_prefix = _get_internal_module_prefix(
        path_diff_between_root_and_module, root_path
    )

    imports = _get_imports_from_ast(
        ast,
        _get_absolute_import_prefix(
            path_diff_between_root_and_module, root_path, module_path
        ),
        _get_all_internal_modules(all_modules, internal_module_prefix),
    )

    imports = _remove_excluded_imports(
        exclude_external_libraries, imports, internal_module_prefix
    )

    all_modules = _append_external_modules_to_module_list(
        all_modules, exclude_external_libraries, imports, root_path
    )
    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports, level_limit))


def _append_external_modules_to_module_list(
    all_modules: list[Node],
    exclude_external_libraries: bool,
    imports: Sequence[Import],
    root_path: Path,
) -> list[Node]:
    """External modules are not detected as modules when importing the source folder - but they will of course show up
    in the imports. To ensure that all edges in the graph have nodes attached, the external modules need to be added to
    the list of modules/nodes."""
    if not exclude_external_libraries:
        all_modules = ImporteeModuleCalculator(root_path).calculate_importee_modules(
            imports,
            all_modules,
        )
    return all_modules


def _remove_excluded_imports(
    exclude_external_libraries: bool,
    imports: Sequence[Import],
    internal_module_prefix: str,
) -> Sequence[Import]:
    import_filter = ImportFilter(exclude_external_libraries, internal_module_prefix)
    return import_filter.filter(imports)


def _get_internal_module_prefix(
    path_diff_between_root_and_module: str, root_path: Path
) -> str:
    """In general, all internal modules should start with the root module name to be able to differentiate between
    internal and external modules. If the root and base module differ, the modules between them also need to be taken
    into account, as not-root.a.b-modules are external, but root.a.b.base-modules are internal.
    """
    internal_module_prefix = root_path.name + "."

    if _actual_difference_between_root_and_module(path_diff_between_root_and_module):
        internal_module_prefix += path_diff_between_root_and_module

    return internal_module_prefix


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
) -> Sequence[Import]:
    converter = ImportConverter()
    return converter.convert(ast, absolute_import_prefix, all_internal_modules)


def _get_all_ast_modules(
    module_path: Path, root_path: Path, exclusions: tuple[str, ...]
) -> tuple[list[str], list[NamedModule]]:
    config = Config(exclusions)
    file_filter = FileFilter(config)

    parser = Parser(file_filter, root_path)
    all_modules, ast = parser.parse(module_path)
    return all_modules, ast


def _get_all_internal_modules(
    modules: list[str], internal_module_prefix: str
) -> set[str]:
    return {m for m in modules if m.startswith(internal_module_prefix)}
