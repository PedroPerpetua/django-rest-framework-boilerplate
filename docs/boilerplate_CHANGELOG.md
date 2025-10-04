# Boilerplate Changelog

All notable changes to the [django-rest-framework-boilerplate](https://github.com/PedroPerpetua/django-rest-framework-boilerplate) used will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This CHANGELOG was only adopted from v2.6.0 forward, so previous release are **not** documented. Maybe in the future they'll be added.


## [Unreleased]

### Changed
- Removed `CORS_ALLOW_ALL_ORIGINS` setting. Use `CORS_ALLOWED_ORIGINS=*` instead.

### Fixed
- Added missing CORS headers to nginx `/media` location.
- Improved Docker builds.

### Dependencies
- `python`: `3.1.5` -> `3.1.7`.
- `Django`: `5.2.5` -> `5.2.7`.
- `django-cors-headers` `4.7.0` -> `4.9.0`.
- `click`: `8.2.1` -> `8.3.0`.
- `ruff`: `0.12.8` -> `0.13.3`.
- `mypy`: `1.17.1` -> `1.18.2`.
- `django-stubs`: `5.2.2` -> `5.2.5`.
- `djangorestframework-stubs`: `3.16.2` -> `3.16.4`.
- `types-docker`: `7.1.0.20250809` -> `7.1.0.20250916`.
- `pytest`: `8.4.1` -> `8.4.2`.
- `pytest-cov`: `6.2.1` -> `7.0.0`.


## [2.6.0] - 2025-08-16

### Added
- `subTest_patch_and_put` decorator.
- `override_auto_now` context manager.

### Changed
- Major overhaul to the CLI's code organization; should still work more or less the same, but multiple commands / options were improved, as well as messages displayed to the user.

### Fixed
- CLI's `test` command's options `cpus` and `with_stdout` now will properly emit a warning if used together.
- Fixed typo in `regenerate-migrations-order` naming documentation.

### Dependencies
- `Django`: `5.2.3` -> `5.2.5`.
- `djangorestframework`: `3.16.0` -> `3.16.1`.
- `djangorestframework-simplejwt`: `5.5.0` -> `5.5.1`.
  - **[BREAKING CHANGE]** - see [their changelog](https://github.com/jazzband/djangorestframework-simplejwt/releases/tag/v5.5.1).
- `docker`: `-` -> `7.1.0`.
- `ruff`: `0.11.13` -> `0.12.8`.
- `mypy`: `1.16.0` -> `1.17.1`.
- `django-stubs`: `5.2.0` -> `5.2.2`.
- `djangorestframework-stubs`: `3.16.0` -> `3.16.2`.
- `types-docker`: `-` -> `7.1.0.20250809`.
- `pytest`: `8.4.0` -> `8.4.1`.
- `pytest-xdist`: `3.7.0` -> `3.8.0`.
