import nox

locations = "src", "tests", "noxfile.py"


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
def tests(session):
    session.run("poetry", "shell")
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "pytest")
