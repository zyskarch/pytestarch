from __future__ import annotations

import nox

locations = "src", "tests", "noxfile.py"


@nox.session(python=["3.9", "3.10", "3.11", "3.12", "3.13"])
def tests(session):
    session.run("poetry", "env", "activate")
    session.run("poetry", "install", "--extras", "visualization", external=True)
    session.run("poetry", "run", "pytest")
