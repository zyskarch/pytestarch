# Changelog

This project uses semantic versioning and follows [keep a changelog](https://keepachangelog.com).

## [1.5.0] -- 2023-04-12
## Added
- More extensive documentation for the regex matching features.

## [1.4.1] -- 2023-04-09
## Fixed 
- Import paths in documentation.

## [1.4.0] -- 2023-04-09
### Added
- Option to specify module names and file exclusions via regex.
- Support for layer architecture.
- Batch support for rule subjects.

### Changed
- Complete module hierarchy present in graph, instead of only for modules that are part of an import dependency.
- Error message only lists violated rule objects when multiple rule objects are defined.

## [1.3.1] -- 2023-01-27
### Changed
- Internal module structure to improve coupling, cohesion.

### Fixed
- Support for python3.8.

## [1.3.0] -- 2022-11-28
### Added
- Reference to modules only by part of their names
- Aliases for plot labels
- Test generation from PUML component diagrams

## [1.2.1] -- 2022-10-21
### Fixed
- Queries with "except itself" excluded too many modules from consideration


## [1.2.0] -- 2022-10-08
### Fixed
- Line separator for rule violation messages


## [1.1.1] -- 2022-10-04
### Fixed
- Line separator for rule violation messages

## [1.1.0] -- 2022-10-02
### Added
- Rule objects can be passed in as a list

### Fixed
- All violations not always returned

## [1.0.3] -- 2022-09-28
### Changed
- Simplified calculation of whether imports are within the project

### Fixed
- Excluded directories no longer searched for parseable files

## [1.0.2] -- 2022-09-28
### Fixed
- All internal modules filtered out if module and root path are not identical and are a sub module of the actual root module.

## [1.0.1] -- 2022-09-27
### Fixed
- Module no longer considered if rule asked only for submodules of a given module

## [1.0.0] -- 2022-09-27
### Changed
- Rename entry point methods for clarity

### Fixed
- Reference to outdated code in documentation

## [0.1.0] -- 2022-09-23
### Added
- More detailed error message for violations of rules checking for absence of imports
- Versioning of documentation

## [0.1.0-alpha.4] -- 2022-09-23
### Added
- Documentation for release of PyTestArch
- More detailed project description

### Changed
- Computation of dependencies between modules on graph

## [0.1.0-alpha.3] -- 2022-09-20
### Fixed
- Different construction of graph node names between OS

## [0.1.0-alpha.1] -- 2022-09-20
### Added
- Documentation
- library MVP
