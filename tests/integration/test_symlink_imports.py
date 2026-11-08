from __future__ import annotations

from pathlib import Path

import pytest

from pytestarch import get_evaluable_architecture


def _symlink_or_skip(target: Path, link: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError):
        pytest.skip("directory symlinks are not supported on this platform")


def test_symlinked_root_keeps_the_name_it_was_reached_under(tmp_path: Path) -> None:
    real = tmp_path / "realpkg"
    real.mkdir()
    (real / "__init__.py").write_text("")
    (real / "mod.py").write_text("")
    link = tmp_path / "aliaspkg"
    _symlink_or_skip(real, link)

    evaluable = get_evaluable_architecture(link)

    assert "aliaspkg.mod" in set(evaluable.modules)
    assert "realpkg.mod" not in set(evaluable.modules)


def test_symlinked_module_path_keeps_the_name_it_was_reached_under(
    tmp_path: Path,
) -> None:
    package = tmp_path / "package"
    real = package / "real"
    real.mkdir(parents=True)
    (real / "__init__.py").write_text("")
    (real / "mod.py").write_text("")
    link = package / "alias"
    _symlink_or_skip(real, link)

    evaluable = get_evaluable_architecture(package, link)

    assert "package.alias.mod" in set(evaluable.modules)
    assert "package.real.mod" not in set(evaluable.modules)


def test_imports_through_symlinked_directory_are_internal(tmp_path: Path) -> None:
    package = tmp_path / "package"
    real = package / "real"
    real.mkdir(parents=True)
    (real / "mod.py").write_text("x = 1")
    (package / "user.py").write_text("from package.alias import mod")
    _symlink_or_skip(real, package / "alias")

    evaluated = get_evaluable_architecture(package, package)

    assert "package.alias" in set(evaluated.modules)
    assert "package.alias.mod" in set(evaluated.modules)
    assert ("package.user", "package.alias.mod") in set(
        evaluated._graph._graph.edges  # type: ignore[attr-defined]
    )
