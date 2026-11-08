from __future__ import annotations

from pathlib import Path

import pytest

from pytestarch import EvaluableArchitecture, Rule, get_evaluable_architecture


def _monorepo(tmp_path: Path) -> Path:
    mono = tmp_path / "mono"
    files = {
        "svc_a/pyproject.toml": "",
        "svc_a/svc_a/__init__.py": "",
        "svc_a/svc_a/api.py": (
            "import svc_b.client\n"
            "from shared import util\n"
            "import utils.helpers\n"
            "import os\n"
        ),
        "svc_a/utils/__init__.py": "",
        "svc_a/utils/helpers.py": "",
        "svc_b/pyproject.toml": "",
        "svc_b/svc_b/__init__.py": "",
        "svc_b/svc_b/client.py": "import shared.util\nfrom utils import helpers\n",
        "svc_b/utils/__init__.py": "",
        "svc_b/utils/helpers.py": "",
        "shared/pyproject.toml": "",
        "shared/shared/__init__.py": "",
        "shared/shared/util.py": "",
        "svc_c/pyproject.toml": "",
        "svc_c/svc_c/__init__.py": "",
        "svc_c/svc_c/c.py": "import utils.helpers\n",
        "tools/build.py": "import svc_a.api\n",
    }
    for relative_path, content in files.items():
        path = mono / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    return mono


def _src_monorepo(tmp_path: Path) -> Path:
    mono = tmp_path / "mono"
    files = {
        "svc_a/pyproject.toml": "",
        "svc_a/src/svc_a/__init__.py": "",
        "svc_a/src/svc_a/api.py": (
            "import svc_b.client\nfrom shared import util\nimport utils.helpers\n"
        ),
        "svc_a/src/utils/__init__.py": "",
        "svc_a/src/utils/helpers.py": "",
        "svc_a/tests/test_api.py": "import svc_a.api\nimport utils.helpers\n",
        "svc_b/pyproject.toml": "",
        "svc_b/src/svc_b/__init__.py": "",
        "svc_b/src/svc_b/client.py": "import shared.util\nfrom utils import helpers\n",
        "svc_b/src/utils/__init__.py": "",
        "svc_b/src/utils/helpers.py": "",
        "shared/pyproject.toml": "",
        "shared/shared/__init__.py": "",
        "shared/shared/util.py": "",
    }
    for relative_path, content in files.items():
        path = mono / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    return mono


def _edges(evaluable: EvaluableArchitecture) -> set[tuple[str, str]]:
    return set(evaluable._graph._graph.edges)  # type: ignore[attr-defined]


def test_monorepo_imports_between_projects_are_edges(tmp_path: Path) -> None:
    evaluable = get_evaluable_architecture(_monorepo(tmp_path), mode="multi_module")

    edges = _edges(evaluable)
    assert ("svc_a.svc_a.api", "svc_b.svc_b.client") in edges
    assert ("svc_a.svc_a.api", "shared.shared.util") in edges
    assert ("svc_b.svc_b.client", "shared.shared.util") in edges
    assert ("tools.build", "svc_a.svc_a.api") in edges


def test_monorepo_keeps_same_named_modules_of_projects_apart(tmp_path: Path) -> None:
    evaluable = get_evaluable_architecture(_monorepo(tmp_path), mode="multi_module")

    assert "svc_a.utils.helpers" in evaluable.modules
    assert "svc_b.utils.helpers" in evaluable.modules
    edges = _edges(evaluable)
    assert ("svc_a.svc_a.api", "svc_a.utils.helpers") in edges
    assert ("svc_b.svc_b.client", "svc_b.utils.helpers") in edges
    assert ("svc_a.svc_a.api", "svc_b.utils.helpers") not in edges
    assert ("svc_b.svc_b.client", "svc_a.utils.helpers") not in edges


@pytest.mark.parametrize("src_layout", [False, True], ids=["flat", "src"])
@pytest.mark.parametrize(
    "source", ["import utils.helpers", "from utils import helpers"]
)
def test_monorepo_keeps_submodule_resolution_within_selected_package(
    tmp_path: Path,
    src_layout: bool,
    source: str,
) -> None:
    mono = _src_monorepo(tmp_path) if src_layout else _monorepo(tmp_path)
    import_root = mono / "svc_a" / "src" if src_layout else mono / "svc_a"
    (import_root / "utils" / "helpers.py").unlink()
    (import_root / "svc_a" / "api.py").write_text(source)

    evaluable = get_evaluable_architecture(mono, mode="multi_module")

    root_name = "svc_a.src" if src_layout else "svc_a"
    importer = f"{root_name}.svc_a.api"
    importee = f"{root_name}.utils"
    expected_edges = {(importer, importee)} if source.startswith("from") else set()
    assert {edge for edge in _edges(evaluable) if edge[0] == importer} == expected_edges


def test_monorepo_does_not_guess_between_projects_providing_the_same_name(
    tmp_path: Path,
) -> None:
    mono = _monorepo(tmp_path)

    evaluable = get_evaluable_architecture(
        mono, exclude_external_libraries=False, mode="multi_module"
    )

    edges = _edges(evaluable)
    assert ("svc_c.svc_c.c", "utils.helpers") in edges
    assert ("svc_c.svc_c.c", "svc_a.utils.helpers") not in edges
    assert ("svc_c.svc_c.c", "svc_b.utils.helpers") not in edges


def test_monorepo_rules_see_dependencies_between_projects(tmp_path: Path) -> None:
    evaluable = get_evaluable_architecture(_monorepo(tmp_path), mode="multi_module")

    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("svc_a")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("svc_b")
    )

    with pytest.raises(AssertionError):
        rule.assert_applies(evaluable)


@pytest.mark.parametrize("src_layout", [False, True], ids=["flat", "src"])
def test_excluding_other_projects_keeps_dependencies_within_retained_project(
    tmp_path: Path, src_layout: bool
) -> None:
    mono = _src_monorepo(tmp_path) if src_layout else _monorepo(tmp_path)
    evaluable = get_evaluable_architecture(
        mono,
        exclusions=("*svc_b*", "*svc_c*", "*shared*"),
        mode="multi_module",
    )
    import_root = "svc_a.src" if src_layout else "svc_a"
    importer = f"{import_root}.svc_a.api"
    importee = f"{import_root}.utils.helpers"

    assert (importer, importee) in _edges(evaluable)
    assert not any(
        module.startswith(project)
        for module in evaluable.modules
        for project in ("svc_b", "svc_c", "shared")
    )
    rule = (
        Rule()
        .modules_that()
        .are_named(importer)
        .should_not()
        .import_modules_that()
        .are_named(importee)
    )
    with pytest.raises(AssertionError):
        rule.assert_applies(evaluable)


def test_monorepo_partial_scan_resolves_imports_within_the_project(
    tmp_path: Path,
) -> None:
    mono = _monorepo(tmp_path)

    evaluable = get_evaluable_architecture(mono, mono / "svc_b", mode="multi_module")

    edges = _edges(evaluable)
    assert ("svc_b.svc_b.client", "svc_b.utils.helpers") in edges
    assert not any(importee.startswith("shared") for _, importee in edges)


def test_single_project_directory_resolves_imports_against_its_local_root(
    tmp_path: Path,
) -> None:
    solo = tmp_path / "solo"
    package = solo / "app" / "app"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "a.py").write_text("import app.b")
    (package / "b.py").write_text("")

    evaluable = get_evaluable_architecture(solo, mode="multi_module")

    edges = _edges(evaluable)
    assert "app.app.a" in evaluable.modules
    assert ("app.app.a", "app.app.b") in edges


def test_root_level_package_does_not_disable_project_resolution(
    tmp_path: Path,
) -> None:
    mono = _monorepo(tmp_path)
    (mono / "top").mkdir()
    (mono / "top" / "__init__.py").write_text("")

    evaluable = get_evaluable_architecture(mono, mode="multi_module")

    assert ("svc_a.svc_a.api", "svc_b.svc_b.client") in _edges(evaluable)


def test_src_layout_monorepo_imports_between_projects_are_edges(
    tmp_path: Path,
) -> None:
    evaluable = get_evaluable_architecture(_src_monorepo(tmp_path), mode="multi_module")

    edges = _edges(evaluable)
    assert ("svc_a.src.svc_a.api", "svc_b.src.svc_b.client") in edges
    assert ("svc_a.src.svc_a.api", "shared.shared.util") in edges
    assert ("svc_b.src.svc_b.client", "shared.shared.util") in edges


def test_src_layout_monorepo_keeps_same_named_modules_of_projects_apart(
    tmp_path: Path,
) -> None:
    evaluable = get_evaluable_architecture(_src_monorepo(tmp_path), mode="multi_module")

    edges = _edges(evaluable)
    assert ("svc_a.src.svc_a.api", "svc_a.src.utils.helpers") in edges
    assert ("svc_b.src.svc_b.client", "svc_b.src.utils.helpers") in edges
    assert ("svc_a.src.svc_a.api", "svc_b.src.utils.helpers") not in edges


def test_src_layout_tests_folder_belongs_to_its_own_project(tmp_path: Path) -> None:
    evaluable = get_evaluable_architecture(_src_monorepo(tmp_path), mode="multi_module")

    edges = _edges(evaluable)
    assert ("svc_a.tests.test_api", "svc_a.src.svc_a.api") in edges
    assert ("svc_a.tests.test_api", "svc_a.src.utils.helpers") in edges
    assert ("svc_a.tests.test_api", "svc_b.src.utils.helpers") not in edges


def test_src_layout_monorepo_rules_see_dependencies_between_projects(
    tmp_path: Path,
) -> None:
    evaluable = get_evaluable_architecture(_src_monorepo(tmp_path), mode="multi_module")

    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("svc_a.src")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("svc_b.src")
    )

    with pytest.raises(AssertionError):
        rule.assert_applies(evaluable)


def test_single_src_layout_project_resolves_imports(tmp_path: Path) -> None:
    solo = tmp_path / "solo"
    package = solo / "src" / "app"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "a.py").write_text("import app.b")
    (package / "b.py").write_text("")

    evaluable = get_evaluable_architecture(solo, mode="multi_module")

    edges = _edges(evaluable)
    assert ("src.app.a", "src.app.b") in edges
    assert ("src.app.a", "app.b") not in edges


def test_src_folder_that_is_a_package_is_no_import_root(tmp_path: Path) -> None:
    mono = tmp_path / "mono"
    for project in ("a", "b"):
        package = mono / project / "src" / "pkg"
        package.mkdir(parents=True)
        (mono / project / "src" / "__init__.py").write_text("")
        (package / "__init__.py").write_text("")
    (mono / "a" / "src" / "pkg" / "x.py").write_text("import pkg.y")
    (mono / "b" / "src" / "pkg" / "y.py").write_text("")

    evaluable = get_evaluable_architecture(
        mono, exclude_external_libraries=False, mode="multi_module"
    )

    assert ("a.src.pkg.x", "pkg.y") in _edges(evaluable)


def test_excluding_a_provider_does_not_rebind_its_imports(tmp_path: Path) -> None:
    evaluable = get_evaluable_architecture(
        _monorepo(tmp_path),
        exclusions=("*__pycache__*", "*svc_a/utils*"),
        mode="multi_module",
    )

    importer = "svc_a.svc_a.api"
    assert (importer, "svc_b.utils.helpers") not in _edges(evaluable)
    assert (importer, "svc_b.svc_b.client") in _edges(evaluable)


def test_excluding_one_ambiguous_provider_does_not_pick_the_other(
    tmp_path: Path,
) -> None:
    evaluable = get_evaluable_architecture(
        _monorepo(tmp_path),
        exclusions=("*__pycache__*", "*svc_a*"),
        mode="multi_module",
    )

    importer = "svc_c.svc_c.c"
    assert not any(source == importer for source, _ in _edges(evaluable))


@pytest.mark.parametrize("directory", ["docs", "tests", "scripts"])
def test_directory_with_packages_is_not_a_cross_project_provider(
    tmp_path: Path, directory: str
) -> None:
    repo = tmp_path / "repo"
    source = repo / "src"
    (source / "app").mkdir(parents=True)
    (source / "app" / "__init__.py").write_text("")
    (source / "app" / "core.py").write_text("import pkg.mod\n")
    provider = repo / directory / "pkg"
    provider.mkdir(parents=True)
    (provider / "__init__.py").write_text("")
    (provider / "mod.py").write_text("")

    evaluable = get_evaluable_architecture(
        repo, exclude_external_libraries=False, mode="multi_module"
    )

    assert (source.name + ".app.core", f"{directory}.pkg.mod") not in _edges(evaluable)
    assert (source.name + ".app.core", "pkg.mod") in _edges(evaluable)


def test_explicit_import_roots_enable_an_unmarked_monorepo(tmp_path: Path) -> None:
    mono = tmp_path / "mono"
    for project in ("svc_a", "svc_b"):
        package = mono / project / project
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
    (mono / "svc_a" / "svc_a" / "api.py").write_text("import svc_b.client\n")
    (mono / "svc_b" / "svc_b" / "client.py").write_text("")

    automatic = get_evaluable_architecture(mono, mode="multi_module")
    explicit = get_evaluable_architecture(
        mono,
        mode="multi_module",
        import_roots=("svc_a", "svc_b"),
    )

    assert (
        "svc_a.svc_a.api",
        "svc_b.svc_b.client",
    ) not in _edges(automatic)
    assert ("svc_a.svc_a.api", "svc_b.svc_b.client") in _edges(explicit)


def test_explicit_import_roots_for_an_unmarked_src_monorepo(tmp_path: Path) -> None:
    mono = tmp_path / "mono"
    for project in ("svc_a", "svc_b"):
        package = mono / project / "src" / project
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
    (mono / "svc_a" / "src" / "svc_a" / "api.py").write_text("import svc_b.client\n")
    (mono / "svc_b" / "src" / "svc_b" / "client.py").write_text("")

    evaluable = get_evaluable_architecture(
        mono,
        mode="multi_module",
        import_roots=("svc_a/src", "svc_b/src"),
    )

    assert ("svc_a.src.svc_a.api", "svc_b.src.svc_b.client") in _edges(evaluable)


def test_explicit_empty_import_roots_disable_automatic_cross_project_roots(
    tmp_path: Path,
) -> None:
    monorepo = _monorepo(tmp_path)

    evaluable = get_evaluable_architecture(
        monorepo, mode="multi_module", import_roots=()
    )

    assert ("svc_a.svc_a.api", "svc_b.svc_b.client") not in _edges(evaluable)


def test_src_layout_project_next_to_a_tests_project_resolves_test_imports(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / "src" / "app").mkdir(parents=True)
    (repo / "src" / "app" / "__init__.py").write_text("")
    (repo / "src" / "app" / "core.py").write_text("")
    (repo / "tests" / "unit").mkdir(parents=True)
    (repo / "tests" / "unit" / "__init__.py").write_text("")
    (repo / "tests" / "unit" / "test_core.py").write_text("import app.core")

    evaluable = get_evaluable_architecture(repo, mode="multi_module")

    assert ("tests.unit.test_core", "src.app.core") in _edges(evaluable)
