from __future__ import annotations

from pytestarch.eval_structure_generation.file_import.import_types import (
    AbsoluteImport,
    RelativeImport,
)
from pytestarch.eval_structure_generation.file_import.importee_module_calculator import (
    ImporteeModuleCalculator,
)

ROOT_MODULE_NAME = "src"


def calculate(imports, all_modules):
    return set(
        ImporteeModuleCalculator(ROOT_MODULE_NAME).calculate_importee_modules(
            imports, all_modules
        )
    )


def calculate_relative_naming(imports, parsed_modules):
    """ImporteeModuleCalculator with module names carrying no prefix (relative module
    naming for a container root, i.e. root_module_name is empty)."""
    return set(
        ImporteeModuleCalculator("").calculate_importee_modules(imports, parsed_modules)
    )


def test_external_importee_and_its_parents_are_added() -> None:
    result = calculate(
        [AbsoluteImport("src.moduleA.fileA", "os.path")],
        ["src.moduleA.fileA"],
    )

    assert result == {"src.moduleA.fileA", "os.path", "os"}


def test_internal_importee_is_not_added_as_external_module() -> None:
    """Importees belonging to the scanned root module must not be treated as
    external dependencies (regression test for
    https://github.com/zyskarch/pytestarch/issues/144)."""
    result = calculate(
        [AbsoluteImport("src.moduleA.fileA", "src.moduleB.fileB")],
        ["src.moduleA.fileA"],
    )

    assert result == {"src.moduleA.fileA"}


def test_importee_equal_to_root_module_name_is_not_added() -> None:
    result = calculate(
        [AbsoluteImport("src.moduleA.fileA", "src")],
        ["src.moduleA.fileA"],
    )

    assert result == {"src.moduleA.fileA"}


def test_external_importee_sharing_root_module_prefix_is_added() -> None:
    """An external module that only shares the root module's name prefix must
    not be mistaken for an internal module (e.g. 'apprise' with root 'app')."""
    result = set(
        ImporteeModuleCalculator("app").calculate_importee_modules(
            [AbsoluteImport("app.moduleA.fileA", "apprise.core")],
            ["app.moduleA.fileA"],
        )
    )

    assert result == {"app.moduleA.fileA", "apprise.core", "apprise"}


def test_relative_naming_parsed_importee_is_not_added() -> None:
    """A parsed module (package in a container root, relative naming) is internal."""
    result = calculate_relative_naming(
        [AbsoluteImport("X", "pkg_a.mod")],
        ["pkg_a", "pkg_a.mod"],
    )

    assert result == {"pkg_a", "pkg_a.mod"}


def test_relative_naming_top_level_module_file_importee_is_not_added() -> None:
    """Top level module files (e.g. 'top.py' next to packages in the container root)
    are parsed modules as well, so their imports are internal."""
    result = calculate_relative_naming(
        [AbsoluteImport("X", "top")],
        ["pkg_a", "pkg_a.mod", "top"],
    )

    assert result == {"pkg_a", "pkg_a.mod", "top"}


def test_relative_naming_external_importee_and_parents_are_added() -> None:
    result = calculate_relative_naming(
        [AbsoluteImport("X", "os.path")],
        ["pkg_a", "pkg_a.mod"],
    )

    assert result == {"pkg_a", "pkg_a.mod", "os.path", "os"}


def test_relative_naming_out_of_scan_sibling_is_added() -> None:
    """An importee whose top level module was not parsed is external, regardless of
    whether it exists under the root: sibling packages outside the scanned
    module_path are listed as external dependencies, consistent with the default
    naming's treatment of the same scenario."""
    result = calculate_relative_naming(
        [AbsoluteImport("X", "pkg_b.mod")],
        ["pkg_a", "pkg_a.mod"],
    )

    assert result == {"pkg_a", "pkg_a.mod", "pkg_b", "pkg_b.mod"}


def test_relative_naming_unparsed_submodule_importee_is_not_added() -> None:
    """A relatively resolved importee ('from .sub import thing' in 'pkg_a.mod'
    resolves to 'pkg_a.sub') lies under the parsed top level module 'pkg_a'; like a
    submodule of a parsed package that was not itself parsed (e.g. excluded), it is
    internal and must not be re-added as an external module."""
    result = calculate_relative_naming(
        [RelativeImport("pkg_a.mod", "sub", None, 1)],
        ["pkg_a", "pkg_a.mod"],
    )

    assert result == {"pkg_a", "pkg_a.mod"}


def test_default_naming_container_root_importee_without_prefix_is_external() -> None:
    """With the default naming, container root module names are prefixed with the root
    directory's name, so an importee without that prefix is a genuine external module."""
    root_module_name = "project"

    result = set(
        ImporteeModuleCalculator(root_module_name).calculate_importee_modules(
            [AbsoluteImport(f"{root_module_name}.pkg_a.mod", "pkg_b.mod")],
            [],
        )
    )

    assert result == {"pkg_b.mod", "pkg_b"}


def test_default_naming_container_root_prefixed_importee_is_internal() -> None:
    root_module_name = "project"

    result = set(
        ImporteeModuleCalculator(root_module_name).calculate_importee_modules(
            [
                AbsoluteImport(
                    f"{root_module_name}.pkg_a.mod", f"{root_module_name}.top"
                )
            ],
            [],
        )
    )

    assert result == set()
