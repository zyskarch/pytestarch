"""
The following two functions are the main entry point to PyTestArch. They can be used to create an evaluable object,
for which the user can then define architectural rules.
"""
import os
from pathlib import Path
from types import ModuleType
from typing import Optional, Tuple

from pytestarch.config.config import Config
from pytestarch.eval_structure.evaluable_architecture import EvaluableArchitecture
from pytestarch.eval_structure.evaluable_graph import EvaluableArchitectureGraph
from pytestarch.eval_structure_impl.networkxgraph import NetworkxGraph
from pytestarch.importer.converter import ImportConverter
from pytestarch.importer.file_filter import FileFilter
from pytestarch.importer.import_filter import ImportFilter
from pytestarch.importer.importee_module_calculator import ImporteeModuleCalculator
from pytestarch.importer.parser import Parser

DEFAULT_EXCLUSIONS = ("*__pycache__",)


def get_evaluable_architecture(
    root_path: str,
    module_path: str,
    exclusions: Tuple[str, ...] = DEFAULT_EXCLUSIONS,
    exclude_external_libraries: bool = True,
    level_limit: Optional[int] = None,
) -> EvaluableArchitecture:
    """Constructs an evaluable object based on the given module.

    Args:
        root_path: root directory of the source code. Should not be set to a submodule of the top level module.
        module_path: path of module to generate the evaluable for. Must be a submodule of the root_path module.
        exclusions: pseudo-regex to exclude files and directories from being integrated into the evaluable, e.g. *Test.py
        exclude_external_libraries: if True, external dependencies (defined as all dependencies to module outside the
            module_path, including Python built-in modules) will not be taken into account for the dependency analysis.
        level_limit: if not None, specifies the depth of the graph. For example, a limit of 1 will result in only the
            modules one level below the module path to be added as nodes. Note that this only applies to the final graph;
            all modules will be parsed, the graph will simply be flattened: if a submodule of X imports Y, this import is
            then assigned to X instead, if Y is above the level limit.
    """
    root_path = Path(root_path)
    module_path = Path(module_path)

    path_diff_between_root_and_module = str(module_path.relative_to(root_path)).replace(
        os.sep, "."
    )

    if level_limit is not None:
        if path_diff_between_root_and_module != ".":
            levels = len(path_diff_between_root_and_module.split("."))
            level_limit += levels

    config = Config(exclusions)
    file_filter = FileFilter(config)

    parser = Parser(file_filter, root_path)
    converter = ImportConverter()

    all_modules, ast = parser.parse(module_path)

    imports = converter.convert(ast)

    internal_module_prefix = root_path.name + "."
    if path_diff_between_root_and_module != ".":
        internal_module_prefix += path_diff_between_root_and_module

    import_filter = ImportFilter(exclude_external_libraries, internal_module_prefix)
    imports = import_filter.filter(imports)

    if not exclude_external_libraries:
        all_modules = ImporteeModuleCalculator(root_path).calculate_importee_modules(
            imports,
            all_modules,
        )
    return EvaluableArchitectureGraph(NetworkxGraph(all_modules, imports, level_limit))


def get_evaluable_architecture_for_module_objects(
    root_module: ModuleType,
    module: ModuleType,
    exclusions: Tuple[str, ...] = DEFAULT_EXCLUSIONS,
    exclude_external_libraries: bool = True,
    level_limit: Optional[int] = None,
) -> EvaluableArchitecture:
    """Same functionality as get_evaluable_architecture, but root module and module to evaluate are passed in as module objects
    instead of the absolute paths to them.
    """
    root_path = os.path.dirname(root_module.__file__)
    module_path = os.path.dirname(module.__file__)

    return get_evaluable_architecture(
        root_path, module_path, exclusions, exclude_external_libraries, level_limit
    )
