from __future__ import annotations

from pathlib import Path
from shutil import copytree

import pytest

from integration.test_module_objects import _package
from integration.test_monorepo import _edges, _monorepo, _src_monorepo
from pytestarch import (
    get_evaluable_architecture,
    get_evaluable_architecture_for_module_objects,
)


@pytest.mark.parametrize("include_external", [False, True])
@pytest.mark.parametrize(
    "source", ["import utils.helpers", "from utils import helpers"]
)
@pytest.mark.parametrize("reason", ["excluded", "missing-child", "ambiguous"])
def test_unresolved_provider_does_not_bind_to_root_package(
    tmp_path: Path, include_external: bool, source: str, reason: str
) -> None:
    mono = _monorepo(tmp_path)
    copytree(mono / "svc_b" / "utils", mono / "utils")
    importer = "svc_c.svc_c.c" if reason == "ambiguous" else "svc_a.svc_a.api"
    (mono / Path(importer.replace(".", "/")).with_suffix(".py")).write_text(source)
    exclusions: tuple[str, ...] = ("*__pycache__*",)
    if reason == "excluded":
        exclusions += ("*svc_a/utils*",)
    elif reason == "missing-child":
        (mono / "svc_a" / "utils" / "helpers.py").unlink()

    evaluable = get_evaluable_architecture(
        mono,
        mode="multi_module",
        exclusions=exclusions,
        exclude_external_libraries=not include_external,
    )

    targets = {target for origin, target in _edges(evaluable) if origin == importer}
    expected = (
        {"svc_a.utils"}
        if reason == "missing-child" and source.startswith("from")
        else set()
    )
    assert targets == expected
    assert "utils.helpers" in evaluable.modules


def test_unresolved_import_with_colliding_parent_is_omitted(tmp_path: Path) -> None:
    mono = _monorepo(tmp_path)
    copytree(mono / "svc_b" / "utils", mono / "utils")
    (mono / "svc_a" / "svc_a" / "api.py").write_text("import utils.missing\n")

    evaluable = get_evaluable_architecture(
        mono, mode="multi_module", exclude_external_libraries=False
    )

    assert not any(origin == "svc_a.svc_a.api" for origin, _ in _edges(evaluable))


@pytest.mark.parametrize("src_layout", [False, True], ids=["flat", "src"])
@pytest.mark.parametrize("reverse_roots", [False, True])
def test_nested_explicit_roots_keep_their_own_project_scope(
    tmp_path: Path, src_layout: bool, reverse_roots: bool
) -> None:
    mono = _src_monorepo(tmp_path) if src_layout else _monorepo(tmp_path)
    (mono / "libs").mkdir()
    for project in ("svc_a", "svc_b"):
        (mono / project / "pyproject.toml").unlink()
        (mono / project).rename(mono / "libs" / project)
    roots = ["libs/svc_a", "libs/svc_b"]
    if src_layout:
        roots = [f"{root}/src" for root in roots]
    if reverse_roots:
        roots.reverse()

    evaluable = get_evaluable_architecture(
        mono, mode="multi_module", import_roots=roots
    )

    for project, module in (("svc_a", "svc_a.api"), ("svc_b", "svc_b.client")):
        prefix = f"libs.{project}.src" if src_layout else f"libs.{project}"
        assert (f"{prefix}.{module}", f"{prefix}.utils.helpers") in _edges(evaluable)
    if src_layout:
        assert ("libs.svc_a.tests.test_api", "libs.svc_a.src.utils.helpers") in _edges(
            evaluable
        )


@pytest.mark.parametrize("explicit", [False, True])
@pytest.mark.parametrize("package_importer", [False, True])
def test_src_root_provides_standalone_modules(
    tmp_path: Path, explicit: bool, package_importer: bool
) -> None:
    source = tmp_path / "src"
    source.mkdir()
    importer = source / "main.py"
    importer_name = "src.main"
    if package_importer:
        (source / "app").mkdir()
        (source / "app" / "__init__.py").write_text("")
        importer = source / "app" / "main.py"
        importer_name = "src.app.main"
    importer.write_text("import helpers\n")
    (source / "helpers.py").write_text("")

    evaluable = get_evaluable_architecture(
        tmp_path,
        mode="multi_module",
        import_roots=("src",) if explicit else None,
    )

    assert (importer_name, "src.helpers") in _edges(evaluable)


def test_excluding_standalone_provider_does_not_select_another_project(
    tmp_path: Path,
) -> None:
    mono = _src_monorepo(tmp_path)
    for project in ("svc_a", "svc_b"):
        (mono / project / "src" / "helpers.py").write_text("")
    (mono / "svc_a" / "src" / "svc_a" / "api.py").write_text("import helpers\n")

    evaluable = get_evaluable_architecture(
        mono,
        mode="multi_module",
        exclusions=("*svc_a/src/helpers.py",),
        exclude_external_libraries=False,
    )

    assert ("svc_a.src.svc_a.api", "helpers") in _edges(evaluable)
    assert ("svc_a.src.svc_a.api", "svc_b.src.helpers") not in _edges(evaluable)


@pytest.mark.parametrize("include_external", [False, True])
@pytest.mark.parametrize("enable_root", [False, True])
def test_explicit_roots_control_scan_root_cross_project_provider(
    tmp_path: Path, include_external: bool, enable_root: bool
) -> None:
    mono = _monorepo(tmp_path)
    copytree(mono / "svc_b" / "utils", mono / "utils")
    (mono / "main.py").write_text("import utils.helpers\n")

    evaluable = get_evaluable_architecture(
        mono,
        mode="multi_module",
        import_roots=(".",) if enable_root else (),
        exclude_external_libraries=not include_external,
    )

    assert (("svc_c.svc_c.c", "utils.helpers") in _edges(evaluable)) == enable_root
    assert ("main", "utils.helpers") in _edges(evaluable)
    assert ("svc_a.svc_a.api", "svc_a.utils.helpers") in _edges(evaluable)


@pytest.mark.parametrize("module_objects", [False, True])
def test_named_root_registry_preserves_namespace_child_probing(
    tmp_path: Path, module_objects: bool
) -> None:
    root = tmp_path / "app"
    (root / "nested").mkdir(parents=True)
    (root / "__init__.py").write_text("")
    (root / "main.py").write_text("import nested.helpers\n")
    (root / "nested" / "helpers.py").write_text("")

    evaluable = (
        get_evaluable_architecture_for_module_objects(
            _package("app", root), mode="multi_module"
        )
        if module_objects
        else get_evaluable_architecture(root, mode="multi_module")
    )

    assert ("app.main", "app.nested.helpers") in _edges(evaluable)


def test_named_root_registry_does_not_double_prefix_its_own_name(
    tmp_path: Path,
) -> None:
    root = tmp_path / "app"
    root.mkdir()
    (root / "__init__.py").write_text("")
    (root / "app.py").write_text("")
    (root / "main.py").write_text("import app\n")

    evaluable = get_evaluable_architecture(root, mode="multi_module")

    assert ("app.main", "app") in _edges(evaluable)
    assert ("app.main", "app.app") not in _edges(evaluable)
