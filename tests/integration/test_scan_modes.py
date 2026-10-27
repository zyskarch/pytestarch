from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from integration.test_module_objects import (
    _graph_edges,
    _multiple_packages_project,
    _nested_namespace_project,
    _package,
)
from integration.test_monorepo import _monorepo
from pytestarch import (
    get_evaluable_architecture,
    get_evaluable_architecture_for_module_objects,
)
from pytestarch.eval_structure_generation.graph_generation.graph_generator import (
    generate_graph,
)
from pytestarch.query_language.exceptions import ImproperlyConfigured


def test_path_multi_module_resolution_requires_opt_in(tmp_path: Path) -> None:
    mono = _monorepo(tmp_path)

    legacy = get_evaluable_architecture(mono)
    explicit_legacy = get_evaluable_architecture(mono, mode="legacy")
    multi_module = get_evaluable_architecture(mono, mode="multi_module")

    assert set(legacy.modules) == set(explicit_legacy.modules)
    assert _graph_edges(legacy) == _graph_edges(explicit_legacy)
    assert "mono.svc_a.svc_a.api" in legacy.modules
    assert ("mono.svc_a.svc_a.api", "mono.svc_b.svc_b.client") not in _graph_edges(
        legacy
    )
    assert ("svc_a.svc_a.api", "svc_b.svc_b.client") in _graph_edges(multi_module)
    assert "mono" not in multi_module.modules


def test_legacy_container_imports_resolve_to_prefixed_module_names(
    tmp_path: Path,
) -> None:
    src, _, _ = _multiple_packages_project(tmp_path)

    legacy = get_evaluable_architecture(src, exclude_external_libraries=False)
    multi_module = get_evaluable_architecture(src, mode="multi_module")

    assert "src.package2" in legacy.modules
    # the root-relative sibling import resolves to the prefixed name - no
    # prefix-less external node for it, even with external libraries included
    assert "package2" not in legacy.modules
    assert ("src.package1.module1", "package2") not in _graph_edges(legacy)
    assert ("src.package1.module1", "src.package2") in _graph_edges(legacy)
    assert ("package1.module1", "package2.module2") in _graph_edges(multi_module)


@pytest.mark.parametrize("mode", [None, "legacy"])
def test_iterable_module_roots_require_opt_in(tmp_path: Path, mode: str | None) -> None:
    _, package_a, _ = _multiple_packages_project(tmp_path)
    roots = [_package("package1", package_a)]

    with pytest.raises(ImproperlyConfigured, match='mode="multi_module"'):
        if mode is None:
            get_evaluable_architecture_for_module_objects(roots)
        else:
            get_evaluable_architecture_for_module_objects(roots, mode=mode)  # type: ignore[arg-type]


@pytest.mark.parametrize("wrapped", [False, True], ids=["single", "iterable"])
def test_namespace_names_do_not_depend_on_root_count(
    tmp_path: Path, wrapped: bool
) -> None:
    a, b = _nested_namespace_project(tmp_path)
    package_a = _package("company.product.a", a)
    package_b = _package("company.product.b", b)

    single = get_evaluable_architecture_for_module_objects(
        [package_a] if wrapped else package_a, mode="multi_module"
    )
    multiple = get_evaluable_architecture_for_module_objects(
        [package_a, package_b], mode="multi_module"
    )
    legacy = get_evaluable_architecture_for_module_objects(package_a, package_a)

    for architecture in (single, multiple):
        assert "company.product.a.x" in architecture.modules
        assert ("company.product.a.x", "company.product.a.z") in _graph_edges(
            architecture
        )
        assert "a.x" not in architecture.modules
    assert "a.x" in legacy.modules
    assert "company.product.a.x" not in legacy.modules


@pytest.mark.parametrize("mode", ["", "relative", "root_dir", "bogus", None])
def test_both_entry_points_reject_unknown_modes(
    tmp_path: Path, mode: str | None
) -> None:
    _, a, _ = _multiple_packages_project(tmp_path)
    package_a = _package("package1", a)

    with pytest.raises(ImproperlyConfigured, match="mode must be"):
        get_evaluable_architecture(a, mode=mode)  # type: ignore[arg-type]
    with pytest.raises(ImproperlyConfigured, match="mode must be"):
        get_evaluable_architecture_for_module_objects(package_a, mode=mode)  # type: ignore[arg-type]


def test_mode_is_keyword_only_and_replaces_the_unreleased_naming_option() -> None:
    for entry_point in (
        get_evaluable_architecture,
        get_evaluable_architecture_for_module_objects,
    ):
        parameters = inspect.signature(entry_point).parameters
        assert parameters["mode"].kind == inspect.Parameter.KEYWORD_ONLY
        assert parameters["mode"].default == "legacy"
        assert "module_naming" not in parameters


def test_single_namespace_root_with_explicit_scan_module(tmp_path: Path) -> None:
    a, _ = _nested_namespace_project(tmp_path)
    root = _package("company.product.a", a)

    architecture = get_evaluable_architecture_for_module_objects(
        root, root, mode="multi_module", level_limit=1
    )

    assert ("company.product.a.x", "company.product.a.z") in _graph_edges(architecture)


def test_exclusions_empty_tuple_disables_default_exclusions(tmp_path: Path) -> None:
    cached = tmp_path / "src" / "pkg" / "__pycache__" / "cached.py"
    cached.parent.mkdir(parents=True)
    cached.write_text("")

    defaulted = get_evaluable_architecture(tmp_path / "src")
    unfiltered = get_evaluable_architecture(tmp_path / "src", exclusions=())

    assert "src.pkg.__pycache__.cached" not in defaulted.modules
    assert "src.pkg.__pycache__.cached" in unfiltered.modules


def test_missing_scan_paths_raise_actionable_errors(tmp_path: Path) -> None:
    with pytest.raises(ImproperlyConfigured, match="root_path .* does not exist"):
        get_evaluable_architecture(tmp_path / "missing")

    root = tmp_path / "root"
    root.mkdir()

    with pytest.raises(ImproperlyConfigured, match="module_path .* does not exist"):
        get_evaluable_architecture(root, root / "missing")


def test_module_path_outside_root_raises_improperly_configured(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    other = tmp_path / "other"
    root.mkdir()
    other.mkdir()

    with pytest.raises(ImproperlyConfigured, match="is not below the root"):
        get_evaluable_architecture(root, other)


def test_mixed_relative_and_absolute_path_forms_are_rejected(tmp_path: Path) -> None:
    """root_path and module_path must share one path form; the containment
    check cannot compare an absolute path against a relative root."""
    root = tmp_path / "src"
    package = root / "pkg_a"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")

    with pytest.raises(
        ImproperlyConfigured, match="must both be relative or both absolute"
    ):
        get_evaluable_architecture("src", package)

    with pytest.raises(
        ImproperlyConfigured, match="must both be relative or both absolute"
    ):
        get_evaluable_architecture(root, "src/pkg_a")


def test_lexical_parent_escape_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """'..' segments are collapsed before the containment check, so a module
    path cannot escape the root lexically while symlinks stay unresolved."""
    src = tmp_path / "src"
    package = src / "pkg_a"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ImproperlyConfigured, match="is not below the root"):
        get_evaluable_architecture("src", "src/../outside")


def test_file_module_path_uses_the_module_name_without_suffix(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "a.py").write_text("from pkg import b\n")
    (package / "b.py").write_text("")

    evaluable = get_evaluable_architecture(
        tmp_path, package / "a.py", mode="multi_module"
    )

    assert "pkg.a" in evaluable.modules
    assert "pkg.a.py" not in evaluable.modules


def test_dotted_root_directory_level_limit_matches_module_objects(
    tmp_path: Path,
) -> None:
    package = tmp_path / "x.v1"
    (package / "pkg").mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "pkg" / "__init__.py").write_text("")
    (package / "pkg" / "mod.py").write_text("")

    from_path = get_evaluable_architecture(package, mode="multi_module", level_limit=1)
    from_objects = get_evaluable_architecture_for_module_objects(
        _package("x.v1", package), mode="multi_module", level_limit=1
    )

    assert set(from_path.modules) == set(from_objects.modules)
    assert "x.v1.pkg" in from_path.modules


@pytest.mark.parametrize(
    "entry, message",
    [
        ("missing", "does not exist"),
        ("empty", "does not directly contain any package"),
        ("package1", "is a package"),
    ],
)
def test_import_roots_reject_invalid_entries(
    tmp_path: Path, entry: str, message: str
) -> None:
    src, _, _ = _multiple_packages_project(tmp_path)
    (src / "empty").mkdir()

    with pytest.raises(ImproperlyConfigured, match=message):
        get_evaluable_architecture(src, mode="multi_module", import_roots=(entry,))


def test_import_roots_must_be_below_root(tmp_path: Path) -> None:
    src, _, _ = _multiple_packages_project(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "package3").mkdir()
    (outside / "package3" / "__init__.py").write_text("")

    with pytest.raises(ImproperlyConfigured, match="is not below the root"):
        get_evaluable_architecture(src, mode="multi_module", import_roots=(outside,))


def test_import_roots_require_multi_module_mode(tmp_path: Path) -> None:
    src, _, _ = _multiple_packages_project(tmp_path)

    with pytest.raises(ImproperlyConfigured, match='mode="multi_module"'):
        get_evaluable_architecture(src, import_roots=("package1",))


def test_import_roots_reject_a_single_string(tmp_path: Path) -> None:
    src, _, _ = _multiple_packages_project(tmp_path)

    with pytest.raises(ImproperlyConfigured, match="sequence of paths"):
        get_evaluable_architecture(
            src,
            mode="multi_module",
            import_roots="package1",  # type: ignore[arg-type]
        )


def test_import_roots_reject_package_roots(tmp_path: Path) -> None:
    _, package_1, _ = _multiple_packages_project(tmp_path)

    with pytest.raises(ImproperlyConfigured, match="container roots"):
        get_evaluable_architecture(
            package_1, mode="multi_module", import_roots=(package_1,)
        )


def test_relative_root_accepts_scan_root_as_explicit_import_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """import_roots are validated against the absolutized root but stored in the
    root's path form, so a relative root_path keeps resolving packages."""
    _multiple_packages_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    evaluable = get_evaluable_architecture(
        "src", mode="multi_module", import_roots=(".",)
    )

    assert ("package1.module1", "package2.module2") in _graph_edges(evaluable)


def test_relative_root_scopes_explicit_import_root_by_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _ = _monorepo(tmp_path)
    monkeypatch.chdir(tmp_path)

    evaluable = get_evaluable_architecture(
        "mono", mode="multi_module", import_roots=("svc_a",)
    )

    assert ("svc_a.svc_a.api", "svc_a.utils.helpers") in _graph_edges(evaluable)


@pytest.mark.parametrize("level_limit", [0, -1])
def test_graph_generation_rejects_empty_container_level_limit(
    tmp_path: Path, level_limit: int
) -> None:
    with pytest.raises(ImproperlyConfigured, match="level_limit must be at least 1"):
        generate_graph(
            tmp_path, tmp_path, ".", (), True, level_limit, (), mode="multi_module"
        )
