# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.1]
### Added

Support for NO_COLOR environmental variable (http://no-color.org/)
Support for checking of TERM environmental variable as "dumb"
Type hints for literal values possible to hexdump2 result kwarg.
Development install dependencies

### Fixed

Incorrect package importlib_metadata for Python>3.8
Incorrect link for changelog in setup.cfg metadata

### Changed

Run the black code formatter (https://black.readthedocs.io/en/stable/)

## [1.1.0] - 2022-02-8
### Added
- This changelog and URL for changelog into setup.cfg
- Requirements.txt for funsies

### Changed
- Command line switch `-a` for collapse changed to `-v` to match hexdump(1).
- Updated readme with information on setting color all the time.
- Updated hexdump2 package docstring

### Fixed
- Bug where a newline should be printed after a KeyboardInterrupt when running the CLI. 
