from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from types import ModuleType

import pytest

from pytestarch import (
    EvaluableArchitecture,
    Rule,
    get_evaluable_architecture,
    get_evaluable_architecture_for_module_objects,
)
from pytestarch.query_language.exceptions import ImproperlyConfigured


def _package(name: str, path: Path) -> ModuleType:
    module = ModuleType(name)
    module.__path__ = [str(path)]
    module.__file__ = str(path / "__init__.py")
    return module


def _module(name: str, path: Path) -> ModuleType:
    module = ModuleType(name)
    module.__file__ = str(path)
    return module


def _multiple_packages_project(tmp_path: Path) -> tuple[Path, Path, Path]:
    src = tmp_path / "src"
    package_1 = src / "package1"
    package_2 = src / "package2"
    for package in (package_1, package_2):
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")

    (package_1 / "module1.py").write_text("from package2 import module2")
    (package_2 / "module2.py").write_text("")

    return src, package_1, package_2


def _nested_namespace_project(tmp_path: Path) -> tuple[Path, Path]:
    namespace = tmp_path / "company" / "product"
    package_a = namespace / "a"
    package_b = namespace / "b"
    for package in (package_a, package_b):
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")

    (package_a / "x.py").write_text(
        "from company.product.b import y\nfrom company.product.a import z"
    )
    (package_a / "z.py").write_text("")
    (package_b / "y.py").write_text("")

    return package_a, package_b


def _graph_edges(evaluable: EvaluableArchitecture) -> set[tuple[str, str]]:
    return set(evaluable._graph._graph.edges)  # type: ignore[attr-defined]


def test_module_objects_scan_multiple_packages_with_import_names(
    tmp_path: Path,
) -> None:
    _, package_1, package_2 = _multiple_packages_project(tmp_path)

    evaluable = get_evaluable_architecture_for_module_objects(
        [_package("package1", package_1), _package("package2", package_2)],
        mode="multi_module",
    )

    assert set(evaluable.modules) == {
        "package1",
        "package1.__init__",
        "package1.module1",
        "package2",
        "package2.__init__",
        "package2.module2",
    }
    assert ("package1.module1", "package2.module2") in _graph_edges(evaluable)


def test_module_objects_partial_scan_of_multiple_packages(tmp_path: Path) -> None:
    _, package_1, package_2 = _multiple_packages_project(tmp_path)

    evaluable = get_evaluable_architecture_for_module_objects(
        [_package("package1", package_1), _package("package2", package_2)],
        _package("package1", package_1),
        mode="multi_module",
    )

    assert set(evaluable.modules) == {
        "package1",
        "package1.__init__",
        "package1.module1",
    }


def test_module_objects_multiple_packages_with_level_limit(tmp_path: Path) -> None:
    _, package_1, package_2 = _multiple_packages_project(tmp_path)

    evaluable = get_evaluable_architecture_for_module_objects(
        [_package("package1", package_1), _package("package2", package_2)],
        level_limit=1,
        mode="multi_module",
    )

    assert set(evaluable.modules) == {"package1", "package2"}


def test_module_objects_scan_namespace_parent_packages(tmp_path: Path) -> None:
    namespace = tmp_path / "ns"
    package_1 = namespace / "n1"
    package_2 = namespace / "n2"
    for package in (package_1, package_2):
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
    (package_1 / "a.py").write_text("from ns.n2 import b")
    (package_2 / "b.py").write_text("")

    evaluable = get_evaluable_architecture_for_module_objects(
        [_package("ns.n1", package_1), _package("ns.n2", package_2)],
        mode="multi_module",
    )

    assert set(evaluable.modules) == {
        "ns",
        "ns.n1",
        "ns.n1.__init__",
        "ns.n1.a",
        "ns.n2",
        "ns.n2.__init__",
        "ns.n2.b",
    }
    assert ("ns.n1.a", "ns.n2.b") in _graph_edges(evaluable)


def test_module_objects_nested_namespace_parent_keeps_full_import_names(
    tmp_path: Path,
) -> None:
    package_a, package_b = _nested_namespace_project(tmp_path)

    evaluable = get_evaluable_architecture_for_module_objects(
        [
            _package("company.product.a", package_a),
            _package("company.product.b", package_b),
        ],
        mode="multi_module",
    )

    assert set(evaluable.modules) == {
        "company",
        "company.product",
        "company.product.a",
        "company.product.a.__init__",
        "company.product.a.x",
        "company.product.a.z",
        "company.product.b",
        "company.product.b.__init__",
        "company.product.b.y",
    }
    edges = _graph_edges(evaluable)
    assert ("company.product.a.x", "company.product.b.y") in edges
    assert ("company.product.a.x", "company.product.a.z") in edges


def test_module_objects_nested_namespace_parent_imports_are_checked_by_rules(
    tmp_path: Path,
) -> None:
    package_a, package_b = _nested_namespace_project(tmp_path)
    evaluable = get_evaluable_architecture_for_module_objects(
        [
            _package("company.product.a", package_a),
            _package("company.product.b", package_b),
        ],
        mode="multi_module",
    )

    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("company.product.a")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("company.product.b")
    )

    with pytest.raises(AssertionError):
        rule.assert_applies(evaluable)


def test_module_objects_nested_namespace_parent_without_external_noise(
    tmp_path: Path,
) -> None:
    package_a, package_b = _nested_namespace_project(tmp_path)

    evaluable = get_evaluable_architecture_for_module_objects(
        [
            _package("company.product.a", package_a),
            _package("company.product.b", package_b),
        ],
        exclude_external_libraries=False,
        mode="multi_module",
    )

    assert set(evaluable.modules) == {
        "company",
        "company.product",
        "company.product.a",
        "company.product.a.__init__",
        "company.product.a.x",
        "company.product.a.z",
        "company.product.b",
        "company.product.b.__init__",
        "company.product.b.y",
    }


def test_module_objects_nested_namespace_parent_partial_scan(tmp_path: Path) -> None:
    package_a, package_b = _nested_namespace_project(tmp_path)
    package_a_object = _package("company.product.a", package_a)

    evaluable = get_evaluable_architecture_for_module_objects(
        [package_a_object, _package("company.product.b", package_b)],
        package_a_object,
        mode="multi_module",
    )

    assert set(evaluable.modules) == {
        "company",
        "company.product",
        "company.product.a",
        "company.product.a.__init__",
        "company.product.a.x",
        "company.product.a.z",
    }
    assert ("company.product.a.x", "company.product.a.z") in _graph_edges(evaluable)


def test_module_objects_nested_namespace_parent_level_limit(tmp_path: Path) -> None:
    package_a, package_b = _nested_namespace_project(tmp_path)

    evaluable = get_evaluable_architecture_for_module_objects(
        [
            _package("company.product.a", package_a),
            _package("company.product.b", package_b),
        ],
        level_limit=1,
        mode="multi_module",
    )

    assert set(evaluable.modules) == {
        "company",
        "company.product",
        "company.product.a",
        "company.product.b",
    }


def test_module_objects_nested_namespace_parent_partial_scan_with_level_limit(
    tmp_path: Path,
) -> None:
    package_a, package_b = _nested_namespace_project(tmp_path)
    package_a_object = _package("company.product.a", package_a)

    evaluable = get_evaluable_architecture_for_module_objects(
        [package_a_object, _package("company.product.b", package_b)],
        package_a_object,
        level_limit=1,
        mode="multi_module",
    )

    assert set(evaluable.modules) == {
        "company",
        "company.product",
        "company.product.a",
        "company.product.a.__init__",
        "company.product.a.x",
        "company.product.a.z",
    }


def test_module_objects_reject_sibling_subpackages(tmp_path: Path) -> None:
    root = tmp_path / "package"
    root.mkdir()
    (root / "__init__.py").write_text("")
    sub_1 = root / "sub1"
    sub_2 = root / "sub2"
    for subpackage in (sub_1, sub_2):
        subpackage.mkdir()
        (subpackage / "__init__.py").write_text("")

    with pytest.raises(ImproperlyConfigured, match="top-level packages"):
        get_evaluable_architecture_for_module_objects(
            [
                _package("package.sub1", sub_1),
                _package("package.sub2", sub_2),
            ],
            mode="multi_module",
        )


def test_module_objects_reject_module_outside_declared_roots(
    tmp_path: Path,
) -> None:
    src, package_1, package_2 = _multiple_packages_project(tmp_path)
    package_3 = src / "package3"
    package_3.mkdir()
    (package_3 / "__init__.py").write_text("")

    with pytest.raises(ImproperlyConfigured, match="provided root packages"):
        get_evaluable_architecture_for_module_objects(
            [_package("package1", package_1), _package("package2", package_2)],
            _package("package3", package_3),
            mode="multi_module",
        )


def test_path_api_respects_root_directory_exclusion(tmp_path: Path) -> None:
    package = tmp_path / "package"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "module.py").write_text("")

    evaluable = get_evaluable_architecture(
        package,
        package,
        exclusions=("*package*",),
    )

    assert evaluable.modules == []


def test_path_api_module_path_defaults_to_root_path(tmp_path: Path) -> None:
    src, _, _ = _multiple_packages_project(tmp_path)

    explicit = get_evaluable_architecture(src, src)
    defaulted = get_evaluable_architecture(src)

    assert "src.package1.module1" in defaulted.modules
    assert set(defaulted.modules) == set(explicit.modules)
    assert _graph_edges(defaulted) == _graph_edges(explicit)


def test_path_api_module_path_none_defaults_to_root_path(tmp_path: Path) -> None:
    src, _, _ = _multiple_packages_project(tmp_path)

    assert set(get_evaluable_architecture(src, None).modules) == set(
        get_evaluable_architecture(src, src).modules
    )


def test_path_api_keeps_positional_argument_order(tmp_path: Path) -> None:
    src, _, _ = _multiple_packages_project(tmp_path)

    evaluable = get_evaluable_architecture(src, src, ("*module2.py",))

    assert "src.package2.module2" not in evaluable.modules
    assert "src.package1.module1" in evaluable.modules


def test_module_objects_multi_module_respects_root_exclusion(tmp_path: Path) -> None:
    _, package_1, package_2 = _multiple_packages_project(tmp_path)

    evaluable = get_evaluable_architecture_for_module_objects(
        [_package("package1", package_1), _package("package2", package_2)],
        mode="multi_module",
        exclusions=("*src*",),
    )

    assert evaluable.modules == []


def test_module_objects_single_plain_module_root_still_supported(
    tmp_path: Path,
) -> None:
    package = tmp_path / "package"
    package.mkdir()
    module_file = package / "module.py"
    module_file.write_text("")

    evaluable = get_evaluable_architecture_for_module_objects(
        _module("module", module_file)
    )

    assert set(evaluable.modules) == {"package", "package.module"}


def test_module_objects_reject_empty_sequence() -> None:
    with pytest.raises(ImproperlyConfigured, match="At least one root module"):
        get_evaluable_architecture_for_module_objects([], mode="multi_module")


def test_module_objects_one_element_sequence_equals_single_package(
    tmp_path: Path,
) -> None:
    _, package_1, _ = _multiple_packages_project(tmp_path)
    package = _package("package1", package_1)

    single = get_evaluable_architecture_for_module_objects(package, mode="multi_module")
    wrapped = get_evaluable_architecture_for_module_objects(
        [package], mode="multi_module"
    )

    assert set(wrapped.modules) == set(single.modules)
    assert _graph_edges(wrapped) == _graph_edges(single)


@pytest.mark.parametrize(
    "container",
    [list, tuple, set, frozenset, iter],
    ids=["list", "tuple", "set", "frozenset", "iterator"],
)
def test_module_objects_accept_any_iterable_of_modules(
    tmp_path: Path, container: Callable[[list[ModuleType]], Iterable[ModuleType]]
) -> None:
    _, package_1, package_2 = _multiple_packages_project(tmp_path)
    packages = [_package("package1", package_1), _package("package2", package_2)]
    expected = get_evaluable_architecture_for_module_objects(
        packages, mode="multi_module"
    )

    evaluable = get_evaluable_architecture_for_module_objects(
        container(packages), mode="multi_module"
    )

    assert set(evaluable.modules) == set(expected.modules)
    assert _graph_edges(evaluable) == _graph_edges(expected)


def test_module_objects_reject_non_module_entries(tmp_path: Path) -> None:
    _, package_1, package_2 = _multiple_packages_project(tmp_path)
    packages = [_package("package1", package_1), _package("package2", package_2)]

    with pytest.raises(ImproperlyConfigured, match="must be module objects"):
        get_evaluable_architecture_for_module_objects(
            [packages[0], "package2"],  # type: ignore[list-item]
            mode="multi_module",
        )

    with pytest.raises(ImproperlyConfigured, match="must be module objects"):
        get_evaluable_architecture_for_module_objects(
            [packages],  # type: ignore[list-item]
            mode="multi_module",
        )


def test_module_objects_reject_duplicate_roots(tmp_path: Path) -> None:
    _, package_1, package_2 = _multiple_packages_project(tmp_path)
    package = _package("package1", package_1)

    with pytest.raises(ImproperlyConfigured, match="distinct packages"):
        get_evaluable_architecture_for_module_objects(
            [package, package], mode="multi_module"
        )


def test_module_objects_reject_non_package_root_in_sequence(tmp_path: Path) -> None:
    _, package_1, package_2 = _multiple_packages_project(tmp_path)

    with pytest.raises(ImproperlyConfigured, match="must be packages"):
        get_evaluable_architecture_for_module_objects(
            [
                _package("package1", package_1),
                _module("package2", package_2 / "module2.py"),
            ],
            mode="multi_module",
        )


def test_module_objects_reject_namespace_root(tmp_path: Path) -> None:
    namespace = ModuleType("namespace")
    namespace.__path__ = [str(tmp_path)]
    namespace.__file__ = None  # type: ignore[assignment]

    with pytest.raises(ImproperlyConfigured, match="namespace package"):
        get_evaluable_architecture_for_module_objects(namespace)


def test_module_objects_reject_split_package_root(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    package = ModuleType("split")
    package.__path__ = [str(first), str(second)]
    package.__file__ = str(first / "__init__.py")

    with pytest.raises(ImproperlyConfigured, match="several directories"):
        get_evaluable_architecture_for_module_objects(package)


def test_module_objects_reject_module_outside_root(tmp_path: Path) -> None:
    _, package_1, _ = _multiple_packages_project(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    (other / "module.py").write_text("")

    with pytest.raises(ImproperlyConfigured, match="not below the root"):
        get_evaluable_architecture_for_module_objects(
            _package("package1", package_1),
            _module("other.module", other / "module.py"),
        )


def test_module_objects_reject_string_as_root(tmp_path: Path) -> None:
    with pytest.raises(ImproperlyConfigured, match="module object or an iterable"):
        get_evaluable_architecture_for_module_objects(
            str(tmp_path),  # type: ignore[arg-type]
            mode="multi_module",
        )


def test_module_objects_reject_multi_root_name_directory_mismatch(
    tmp_path: Path,
) -> None:
    container = tmp_path / "container"
    directory_a = container / "dir_a"
    directory_b = container / "b"
    for directory in (directory_a, directory_b):
        directory.mkdir(parents=True)
        (directory / "__init__.py").write_text("")

    with pytest.raises(ImproperlyConfigured, match="name and directory name must"):
        get_evaluable_architecture_for_module_objects(
            [
                _package("company.product.a", directory_a),
                _package("company.product.b", directory_b),
            ],
            mode="multi_module",
        )
