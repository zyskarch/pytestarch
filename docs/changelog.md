# Changelog

This project uses semantic versioning and follows [keep a changelog](https://keepachangelog.com).


## [Unreleased]

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