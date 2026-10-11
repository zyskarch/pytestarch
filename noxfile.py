from __future__ import annotations

import nox

locations = "src", "tests", "noxfile.py"


@nox.session(python=["3.11", "3.12", "3.13", "3.14", "3.15"])
def tests(session):
    session.run(
        "uv",
        "sync",
        "--python",
        session.python,
        "--extra",
        "visualization",
        external=True,
    )
    session.run(
        "uv", "run", "--python", session.python, "--no-sync", "pytest", external=True
    )
