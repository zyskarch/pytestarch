"""
The following two functions are the main entry point to PyTestArch. They can be used to create an evaluable object,
for which the user can then define architectural rules.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Sequence
from pathlib import Path
from types import ModuleType
from typing import Literal

from pytestarch import EvaluableArchitecture
from pytestarch.eval_structure_generation.file_import.import_roots import (
    ImportRoots,
    is_import_root,
)
from pytestarch.eval_structure_generation.graph_generation.graph_generator import (
    generate_graph,
)
from pytestarch.query_language.exceptions import ImproperlyConfigured
from pytestarch.utils.partial_match_to_regex_converter import (
    convert_partial_match_to_regex,
)

DEFAULT_EXCLUSIONS = ("*__pycache__*",)

SCAN_MODES = ("legacy", "multi_module")


def get_evaluable_architecture(
    root_path: str | Path,
    module_path: str | Path | None = None,
    exclusions: tuple[str, ...] = DEFAULT_EXCLUSIONS,
    exclude_external_libraries: bool = True,
    level_limit: int | None = None,
    regex_exclusions: tuple[str, ...] | None = None,
    external_exclusions: tuple[str, ...] | None = None,
    regex_external_exclusions: tuple[str, ...] | None = None,
    *,
    mode: Literal["legacy", "multi_module"] = "legacy",
    import_roots: Sequence[str | Path] | None = None,
) -> EvaluableArchitecture:
    """Constructs an evaluable object based on the given module.

    Args:
        root_path: root directory of the source code. If it contains an __init__.py, it is treated as the top level Python package; otherwise as a container directory. For import-name scans, pass the directory that is on sys.path (e.g. 'src'), not necessarily the repository root. See mode for naming and import resolution.
        module_path: path of the module (directory or .py file) to generate the evaluable for. Must be below root_path. Defaults to root_path, i.e. everything below the root is scanned.
        exclusions: pseudo-regex to exclude files and directories from being integrated into the evaluable, e.g. *Test.py. Can only be specified if regex_exclusions is not specified.
        external_exclusions: pseudo-regex version of 'external_exclusions' to exclude certain external dependencies from being integrated into the evaluable. Can only be specified if exclude_external_libraries is False and regex_external_exclusions is not specified. If a parent module (e.g. 'logging') is excluded, so are its child modules (e.g. 'logging.handlers').
        exclude_external_libraries: if True, external dependencies (defined as all dependencies to module outside the
            module_path, including Python built-in modules) will not be taken into account for the dependency analysis. If a parent module (e.g. 'logging') is excluded, so will be child modules (e.g. 'logging.handlers').
        level_limit: if not None, specifies the depth of the graph. For example, a limit of 1 will result in only the
            modules one level below the module path to be added as nodes. Note that this only applies to the final graph;
            all modules will be parsed, the graph will simply be flattened: if a submodule of X imports Y, this import is
            then assigned to X instead, if Y is above the level limit. With dotted namespace roots, the limit is measured
            below the package; namespace ancestors are always retained.
        regex_exclusions: Proper regex version of 'exclusions'. Can only be specified if exclusions is not specified. Path separators in patterns are forward slashes, independent of the operating system.
        regex_external_exclusions: Proper regex version of 'external_exclusions' to exclude certain external dependencies from being integrated into the evaluable. Can only be specified if exclude_external_libraries is False and external_exclusions is not specified. If a parent module (e.g. 'logging') is excluded, so will be child modules (e.g. 'logging.handlers').
        mode: "legacy" (default) preserves directory-prefixed names and does not resolve imports across
            top-level packages or monorepo projects. "multi_module" derives container-root names relative to
            root_path (e.g. 'packageA', not 'src.packageA') and resolves root-relative imports. It also resolves
            imports against local import roots: every child directory holding packages or Python modules. Cross-project providers
            include conventional 'src' folders directly beneath root_path and projects with a pyproject.toml,
            setup.py or setup.cfg; a child project's own 'src' folder needs a project marker or explicit
            import_roots to provide packages across projects. Project directories remain in
            module names to distinguish same-named packages. Package roots containing an __init__.py retain
            their package-name prefix in either mode.
        import_roots: with mode="multi_module", the directories whose paths define import prefixes and whose
            packages may satisfy imports from other import roots. Paths are relative to root_path (or absolute)
            and must be non-package directories below root_path that directly contain at least one package or .py module.
            Passing this option replaces automatic cross-project discovery; importers still prefer their own
            local import roots. Use it for monorepos without project markers or to exclude directories whose
            packages must not act as providers. Only supported for container roots.
    """
    _validate_mode(mode)
    root_as_path = Path(root_path)
    module_as_path = root_as_path if module_path is None else Path(module_path)
    _validate_scan_paths(root_as_path, module_as_path)
    root_module_name = _path_root_module_name(root_as_path, mode)
    resolved_import_roots = _import_roots_for_scan(
        root_as_path, root_module_name, mode, import_roots
    )

    return _generate_evaluable(
        root_path=root_as_path,
        module_path=module_as_path,
        scan_paths=[module_as_path],
        root_module_name=root_module_name,
        exclusions=exclusions,
        exclude_external_libraries=exclude_external_libraries,
        level_limit=level_limit,
        regex_exclusions=regex_exclusions,
        external_exclusions=external_exclusions,
        regex_external_exclusions=regex_external_exclusions,
        mode=mode,
        import_roots=resolved_import_roots,
    )


def _generate_evaluable(
    *,
    root_path: Path,
    module_path: Path,
    scan_paths: Sequence[Path],
    root_module_name: str,
    exclusions: tuple[str, ...],
    exclude_external_libraries: bool,
    level_limit: int | None,
    regex_exclusions: tuple[str, ...] | None,
    external_exclusions: tuple[str, ...] | None,
    regex_external_exclusions: tuple[str, ...] | None,
    mode: Literal["legacy", "multi_module"],
    import_roots: ImportRoots | None,
) -> EvaluableArchitecture:
    """Shared validation and graph construction for both public entry points."""
    if regex_exclusions and exclusions:
        raise ImproperlyConfigured(
            "Partial match exclusions and regex exclusions cannot both be specified."
        )

    if regex_external_exclusions and external_exclusions:
        raise ImproperlyConfigured(
            "Partial match external_exclusions and regex external_exclusions cannot both be specified."
        )

    if exclude_external_libraries and (
        external_exclusions or regex_external_exclusions
    ):
        raise ImproperlyConfigured(
            "If external libraries are excluded, no exclusion patterns can be defined for them."
        )

    if exclusions:
        regex_exclusions = tuple(
            convert_partial_match_to_regex(pattern) for pattern in exclusions
        )
    elif regex_exclusions is None:
        regex_exclusions = ()

    if external_exclusions:
        regex_external_exclusions = tuple(
            convert_partial_match_to_regex(pattern) for pattern in external_exclusions
        )
    elif regex_external_exclusions is None:
        regex_external_exclusions = ()

    path_diff_between_root_and_module = _path_diff(root_path, module_path)

    if level_limit is not None and root_module_name:
        # A dotted root name (e.g. the namespace parent 'company.product') spans one
        # hierarchy level per segment, so the limit must reach that much deeper.
        level_limit += root_module_name.count(".")

    return generate_graph(
        root_path,
        module_path,
        path_diff_between_root_and_module,
        regex_exclusions,
        exclude_external_libraries,
        level_limit,
        regex_external_exclusions,
        mode,
        scan_paths,
        root_module_name,
        import_roots,
    )


def _absolute_path(path: str | Path) -> Path:
    """Absolute, lexically normalized path; keeps the name a symlink was reached under."""
    return Path(os.path.abspath(path))


def _path_root_module_name(
    root_path: Path, mode: Literal["legacy", "multi_module"]
) -> str:
    if (root_path / "__init__.py").is_file():
        return root_path.name

    return "" if mode == "multi_module" else root_path.name


def _path_diff(root_path: Path, module_path: Path) -> str:
    relative = module_path.relative_to(root_path)
    if module_path.is_file() and relative.suffix == ".py":
        relative = relative.with_suffix("")

    return str(relative).replace(os.sep, ".")


def _validate_scan_paths(root_path: Path, module_path: Path) -> None:
    if root_path.is_absolute() != module_path.is_absolute():
        raise ImproperlyConfigured(
            "root_path and module_path must both be relative or both absolute."
        )
    if not root_path.exists():
        raise ImproperlyConfigured(f"root_path '{root_path}' does not exist.")
    if not root_path.is_dir():
        raise ImproperlyConfigured(f"root_path '{root_path}' is not a directory.")
    if not module_path.exists():
        raise ImproperlyConfigured(f"module_path '{module_path}' does not exist.")
    if not module_path.is_dir() and not (
        module_path.is_file() and module_path.suffix == ".py"
    ):
        raise ImproperlyConfigured(
            f"module_path '{module_path}' must be a directory or a Python file."
        )
    if not _is_lexically_under_root(module_path, root_path):
        raise ImproperlyConfigured(
            f"'{module_path}' is not below the root '{root_path}'."
        )


def _import_roots_for_scan(
    root_path: Path,
    root_module_name: str,
    mode: Literal["legacy", "multi_module"],
    import_roots: Sequence[str | Path] | None,
) -> ImportRoots | None:
    if mode != "multi_module":
        if import_roots is not None:
            raise ImproperlyConfigured(
                'import_roots can only be used with mode="multi_module".'
            )
        return None

    if import_roots is not None and (root_path / "__init__.py").is_file():
        raise ImproperlyConfigured(
            "import_roots is only supported for container roots (directories "
            "without __init__.py). A package root already prefixes all module names."
        )

    explicit = (
        None if import_roots is None else _import_root_paths(root_path, import_roots)
    )
    return ImportRoots.discover(root_path, root_module_name, explicit)


def _import_root_paths(
    root_path: Path,
    import_roots: Sequence[str | Path],
) -> tuple[Path, ...]:
    if isinstance(import_roots, (str, bytes)):
        raise ImproperlyConfigured(
            "import_roots must be a sequence of paths, not a single string."
        )
    try:
        entries = iter(import_roots)
    except TypeError as error:
        raise ImproperlyConfigured(
            "import_roots must be a sequence of paths."
        ) from error

    root_abs = _absolute_path(root_path)
    paths: list[Path] = []
    seen: set[Path] = set()
    for entry in entries:
        candidate = Path(entry)
        path_abs = _absolute_path(
            candidate if candidate.is_absolute() else root_path / candidate
        )

        if not path_abs.exists():
            raise ImproperlyConfigured(f"import_root '{path_abs}' does not exist.")
        if not path_abs.is_dir():
            raise ImproperlyConfigured(f"import_root '{path_abs}' is not a directory.")
        if not _is_under_root(path_abs, root_abs):
            raise ImproperlyConfigured(
                f"import_root '{path_abs}' is not below the root '{root_abs}'."
            )
        if (path_abs / "__init__.py").is_file():
            raise ImproperlyConfigured(
                f"import_root '{path_abs}' is a package. Pass the directory that "
                "contains the package instead."
            )
        if not is_import_root(path_abs):
            raise ImproperlyConfigured(
                f"import_root '{path_abs}' does not directly contain any package or .py module."
            )

        # Validation runs in one absolute form, but entries are stored in the
        # root's path form so that downstream relative_to(root_path) calls
        # (e.g. import root prefixes) keep working with a relative root.
        stored = (
            path_abs
            if root_path.is_absolute()
            else root_path / path_abs.relative_to(root_abs)
        )
        if stored not in seen:
            seen.add(stored)
            paths.append(stored)

    return tuple(paths)


def get_evaluable_architecture_for_module_objects(
    root_module: ModuleType | Iterable[ModuleType],
    module: ModuleType | None = None,
    exclusions: tuple[str, ...] = DEFAULT_EXCLUSIONS,
    exclude_external_libraries: bool = True,
    level_limit: int | None = None,
    regex_exclusions: tuple[str, ...] | None = None,
    external_exclusions: tuple[str, ...] | None = None,
    regex_external_exclusions: tuple[str, ...] | None = None,
    *,
    mode: Literal["legacy", "multi_module"] = "legacy",
) -> EvaluableArchitecture:
    """Constructs an evaluable object from module objects instead of paths.

    The default legacy mode accepts one root and keeps directory-prefixed names.
    With mode="multi_module", a package or any iterable of sibling packages is
    scanned with full import names, including namespace parents. Names do not
    depend on root count. `module` may be omitted to scan all roots.

    Namespace packages and packages spread over several directories are not
    supported as roots.

    Args:
        root_module: package (or plain module) whose directory is the naming root,
            or, with mode="multi_module", an iterable of sibling packages.
        module: package or module to scan. Defaults to all roots. A plain module
            selects its containing directory, matching the path-based API.
        exclusions: see get_evaluable_architecture.
        exclude_external_libraries: see get_evaluable_architecture.
        level_limit: see get_evaluable_architecture.
        regex_exclusions: see get_evaluable_architecture.
        external_exclusions: see get_evaluable_architecture.
        regex_external_exclusions: see get_evaluable_architecture.
        mode: "legacy" (default) keeps the historical single-root directory naming.
            "multi_module" accepts iterable roots and uses their full Python import
            names for both single-root and multi-root scans. Several roots must be
            direct siblings in a container directory, not subpackages of a concrete
            package, and each package name must match its directory name. A plain
            module selects its containing directory in either mode.
    """
    _validate_mode(mode)
    (
        root_path,
        module_path,
        scan_paths,
        root_module_name,
    ) = _layout_for_module_objects(root_module, module, mode)

    return _generate_evaluable(
        root_path=root_path,
        module_path=module_path,
        scan_paths=scan_paths,
        root_module_name=root_module_name,
        exclusions=exclusions,
        exclude_external_libraries=exclude_external_libraries,
        level_limit=level_limit,
        regex_exclusions=regex_exclusions,
        external_exclusions=external_exclusions,
        regex_external_exclusions=regex_external_exclusions,
        mode=mode,
        import_roots=None,
    )


def _layout_for_module_objects(
    root_module: ModuleType | Iterable[ModuleType],
    module: ModuleType | None,
    mode: Literal["legacy", "multi_module"],
) -> tuple[Path, Path, list[Path], str]:
    if mode == "legacy" and not isinstance(root_module, ModuleType):
        raise ImproperlyConfigured(
            'Iterable root modules require mode="multi_module"; '
            "legacy mode accepts one module object."
        )
    root_modules = _as_root_modules(root_module)

    if len(root_modules) == 1:
        single_root = root_modules[0]
        root_path = _module_directory(single_root, is_root=True)
        if mode == "legacy":
            root_module_name = root_path.name
        elif getattr(single_root, "__path__", None) is not None:
            root_module_name = single_root.__name__
        else:
            root_module_name = single_root.__name__.rpartition(".")[0]

        if module is None:
            module_path = root_path
            scan_paths = [root_path]
        else:
            module_path = _module_directory(module, is_root=False)
            if not _is_under_root(module_path, root_path):
                raise ImproperlyConfigured(
                    f"'{module_path}' is not below the root '{root_path}'."
                )
            scan_paths = [module_path]

        return root_path, module_path, scan_paths, root_module_name

    root_paths = [_root_package_path(candidate) for candidate in root_modules]

    for root_module, root_package_path in zip(root_modules, root_paths, strict=True):
        import_name = root_module.__name__.rsplit(".", 1)[-1]
        if import_name != root_package_path.name:
            raise ImproperlyConfigured(
                f"'{root_module.__name__}' is loaded from the directory "
                f"'{root_package_path.name}'. Multi-root scans derive module names "
                "from directory names, so the package name and directory name must "
                "match."
            )

    if len({path.resolve() for path in root_paths}) != len(root_paths):
        raise ImproperlyConfigured("Root modules must be distinct packages.")
    if len({path.parent for path in root_paths}) != 1:
        raise ImproperlyConfigured(
            "All root packages must be direct siblings in one directory."
        )

    root_path = _absolute_path(root_paths[0].parent)
    if (root_path / "__init__.py").is_file():
        raise ImproperlyConfigured(
            "Root packages passed as a sequence must be top-level packages in a "
            "container directory. To scan sibling subpackages of a package, pass "
            "their parent package directly."
        )

    dotted_parents = {
        module.__name__.rsplit(".", 1)[0]
        for module in root_modules
        if "." in module.__name__
    }
    if dotted_parents and (
        len(dotted_parents) != 1
        or any("." not in module.__name__ for module in root_modules)
    ):
        raise ImproperlyConfigured("Root packages must share one parent module name.")
    parent_module_name = next(iter(dotted_parents)) if dotted_parents else None

    root_module_name = parent_module_name or ""

    if module is None:
        module_path = root_path
        scan_paths = sorted(root_paths)
    else:
        module_path = _module_directory(module, is_root=False)
        if not any(_is_under_root(module_path, root) for root in root_paths):
            raise ImproperlyConfigured(
                f"'{module_path}' is not below any of the provided root packages."
            )
        scan_paths = [module_path]

    return root_path, module_path, scan_paths, root_module_name


def _as_root_modules(
    root_module: ModuleType | Iterable[ModuleType],
) -> list[ModuleType]:
    if isinstance(root_module, ModuleType):
        return [root_module]

    if isinstance(root_module, str) or not isinstance(root_module, Iterable):
        raise ImproperlyConfigured(
            "root_module must be a module object or an iterable of module objects."
        )

    root_modules = list(root_module)
    if not root_modules:
        raise ImproperlyConfigured("At least one root module is required.")
    if not all(isinstance(candidate, ModuleType) for candidate in root_modules):
        raise ImproperlyConfigured("All root_module entries must be module objects.")

    return root_modules


def _validate_mode(mode: Literal["legacy", "multi_module"]) -> None:
    if mode not in SCAN_MODES:
        raise ImproperlyConfigured(
            f"mode must be one of {SCAN_MODES}, but was '{mode}'."
        )


def _module_directory(module: ModuleType, *, is_root: bool) -> Path:
    if getattr(module, "__path__", None) is not None:
        return _root_package_path(module) if is_root else _package_path(module)

    file = getattr(module, "__file__", None)
    if file is None:
        raise ImproperlyConfigured(
            f"'{module.__name__}' has neither __path__ nor __file__; "
            "pass a package or a module loaded from a file."
        )
    path = _absolute_path(Path(file).parent)
    if not path.is_dir():
        raise ImproperlyConfigured(
            f"'{module.__name__}' does not point to a readable directory."
        )
    return path


def _root_package_path(module: ModuleType) -> Path:
    if getattr(module, "__path__", None) is None:
        raise ImproperlyConfigured(
            f"'{module.__name__}' is not a package. Root modules passed as a "
            "sequence must be packages."
        )
    if getattr(module, "__file__", None) is None:
        raise ImproperlyConfigured(
            f"'{module.__name__}' is a namespace package. Namespace packages "
            "are not supported as root modules."
        )
    return _package_path(module)


def _package_path(module: ModuleType) -> Path:
    paths = [Path(path) for path in getattr(module, "__path__")]
    try:
        distinct = {path.resolve() for path in paths}
    except (OSError, RuntimeError) as error:
        raise ImproperlyConfigured(
            f"'{module.__name__}' contains an unresolvable package path: {error}"
        )
    if len(distinct) != 1:
        raise ImproperlyConfigured(
            f"'{module.__name__}' is spread over several directories. "
            "Packages with multiple __path__ entries are not supported."
        )
    path = _absolute_path(paths[0])
    if not path.is_dir():
        raise ImproperlyConfigured(
            f"'{module.__name__}' does not point to a readable directory."
        )
    return path


def _is_lexically_under_root(module_path: Path, root_path: Path) -> bool:
    """Path-form containment check for the path-based API: a symlinked module
    path is accepted by its link path, matching the path-diff computation and
    the historical behavior that a link may point outside the root. Both paths
    are normalized lexically first, so '..' segments cannot escape the root;
    symlinks are still not resolved."""
    try:
        Path(os.path.normpath(module_path)).relative_to(
            Path(os.path.normpath(root_path))
        )
    except ValueError:
        return False
    return True


def _is_under_root(module_path: Path, root_path: Path) -> bool:
    try:
        module_path.relative_to(root_path)
        module_path.resolve().relative_to(root_path.resolve())
    except (OSError, RuntimeError, ValueError):
        return False
    return True
