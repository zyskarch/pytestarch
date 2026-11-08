from __future__ import annotations

import nox


def _sync(session):
    # --active targets nox's session env instead of the project's .venv.
    session.run(
        "uv",
        "sync",
        "--active",
        "--extra",
        "visualization",
        external=True,
    )


@nox.session(python=["3.11", "3.12", "3.13", "3.14", "3.15"], allow_parallel=True)
def tests(session):
    _sync(session)
    session.run("uv", "run", "--active", "--no-sync", "pytest", external=True)


@nox.session
def typecheck(session):
    _sync(session)
    session.run("uv", "run", "--active", "--no-sync", "pyrefly", "check", external=True)
