# How to release a new version
In order to deploy the newest version of PyTestArch to PyPI, the following steps are required:


### Check out release branch
Create a new release branch based on the current `main` branch.


### Ensure that everything works
Run all tests just to be safe.


### Ensure that changelog is up-to-date
Each PR should come with an update of the [changelog](docs/changelog.md). Make sure that all recent features/bug fixes/...
are mentioned in the changelog. If they are not, update the changelog and open a PR for this first.


### Bump version
In according to what you just specified in the changelog, run
`poetry version [patch/minor/major/prepatch/prerelease/preminor/premajor/prepatch]`
to set the package version.


### Review
Open a PR for the changes you just made.


### Create git tag
Once your PR has been approved and your changes have been merged into main, update your main branch.
Then create a git tag for the release via
`git tag v<insert new version>`

Then share the tag via
`git push origin v<insert new version>`


## Release
Create a release via GitHub. This will trigger the `Release` GitHub Action, which will push the newest version to PyPI.
