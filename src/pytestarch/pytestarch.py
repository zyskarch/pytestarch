"""
The following two functions are the main entry point to PyTestArch. They can be used to create an evaluable object,
for which the user can then define architectural rules.
"""

from __future__ import annotations

import os
from pathlib import Path
from types import ModuleType

from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure_generation.graph_generation.graph_generator import (
    generate_graph,
)
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)

DEFAULT_EXCLUSIONS = ("*__pycache__*",)


def get_evaluable_architecture(
    root_path: str,
    module_path: str,
    exclusions: tuple[str, ...] = DEFAULT_EXCLUSIONS,
    exclude_external_libraries: bool = True,
    level_limit: int | None = None,
    regex_exclusions: tuple[str, ...] | None = None,
) -> EvaluableArchitecture:
    """Constructs an evaluable object based on the given module.

    Args:
        root_path: root directory of the source code. Should not be set to a submodule of the top level module.
        module_path: path of module to generate the evaluable for. Must be a submodule of the root_path module.
        exclusions: pseudo-regex to exclude files and directories from being integrated into the evaluable, e.g. *Test.py
        exclude_external_libraries: if True, external dependencies (defined as all dependencies to module outside the
            module_path, including Python built-in modules) will not be taken into account for the dependency analysis.
            Can only be specified if regex_exclusions is not specified.
        level_limit: if not None, specifies the depth of the graph. For example, a limit of 1 will result in only the
            modules one level below the module path to be added as nodes. Note that this only applies to the final graph;
            all modules will be parsed, the graph will simply be flattened: if a submodule of X imports Y, this import is
            then assigned to X instead, if Y is above the level limit.
        regex_exclusions: Proper regex version of 'exclusions'. Can only be specified if regex_exclusions is not specified.
    """
    if regex_exclusions and exclusions:
        raise ImproperlyConfigured(
            "Partial match exclusions and regex exclusions cannot both be specified."
        )

    if exclusions:
        regex_exclusions = tuple(
            convert_partial_match_to_regex(pattern) for pattern in exclusions
        )

    root_as_path = Path(root_path)
    module_as_path = Path(module_path)

    path_diff_between_root_and_module = str(
        module_as_path.relative_to(root_as_path)
    ).replace(os.sep, ".")

    return generate_graph(
        root_as_path,
        module_as_path,
        path_diff_between_root_and_module,
        regex_exclusions,  # type: ignore
        exclude_external_libraries,
        level_limit,
    )


def get_evaluable_architecture_for_module_objects(
    root_module: ModuleType,
    module: ModuleType,
    exclusions: tuple[str, ...] = DEFAULT_EXCLUSIONS,
    exclude_external_libraries: bool = True,
    level_limit: int | None = None,
    regex_exclusions: tuple[str, ...] | None = None,
) -> EvaluableArchitecture:
    """Same functionality as get_evaluable_architecture, but root module and module to evaluate are passed in as module objects
    instead of the absolute paths to them.
    """
    root_path: str = os.path.dirname(root_module.__file__)  # type: ignore
    module_path: str = os.path.dirname(module.__file__)  # type: ignore

    return get_evaluable_architecture(
        root_path,
        module_path,
        exclusions,
        exclude_external_libraries,
        level_limit,
        regex_exclusions,
    )
