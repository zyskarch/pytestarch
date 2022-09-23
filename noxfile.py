import nox


@nox.session(python=["3.8", "3.9", "3.10"])
def tests(session):
    session.run("poetry", "shell")
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "pytest")


locations = "src", "tests", "noxfile.py"


@nox.session(python=["3.8"])
def lint(session):
    session.run("poetry", "shell")
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "flake8", *locations)


@nox.session(python="3.8")
def black(session):
    session.run("poetry", "shell")
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "black", *locations)


@nox.session(python="3.8")
def bandit(session):
    session.run("poetry", "shell")
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "bandit", "-r", "src")
