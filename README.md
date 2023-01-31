[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

django-rest-framework-boilerplate
===
This repository contains a boilerplate implementation of a Django Rest Framework + Postgres stack, with extended functionality and utilities.

Provided by [PedroPerpetua](https://github.com/PedroPerpetua).


## Version
Currently set up for `python 3.11` with `Django 4.1.5` and `Django Rest Framework 3.14.0`.


## Features

### Project
- Configuration trough environment variables.
- Separated requirement file structure for both production and development.
- Dockerized application.
- Separate dockerfile for linting, testing and coverage using `isort`, `black`, `autoflake`, `mypy` and `coverage`.
- CI/CD for linting and testing trough Github Actions.
- Tests for the implemented features.
- A Makefile to support basic operations.

### Django Functionality
- Multiple utility functions and extensions frequently used in Django projects.
- Template app for the `startapp` command that follows the usual restframework patterns.
- Base command to ease command development, with additional `wait_for_db` and `setup` commands.
- Migration to auto setup a Superuser.
- Ready to edit custom Admin page.
  - Also features an ordering utility to easily re-order apps and models on the admin page.
- A base for a custom user model with the full JWT authentication flow.
  - Also includes classes and mixins for views to facilitate working with Users.
  - **NOTE**: The users, by default, have `active=True`. It may be desired to change this behavior.
  - **NOTE**: The simplejwt settings have `UPDATE_LAST_LOGIN: True`. This may hinder performance and may be desired to change this behavior.
  - **NOTE**: By default, registration trough REST endpoints is disabled. This can be changed in the `config.env` file, or directly in the settings (setting `AUTH_USER_REGISTRATION_ENABLED`).

### REST
- A `/ping` endpoint to check server availability.
- Custom error messages using [DRF Standardized Errors](https://github.com/ghazi-git/drf-standardized-errors)
- Out of the box OpenAPI schema with Swagger support using [DRF Spectacular](https://github.com/tfranzel/drf-spectacular)
  - The schema is made available in the `/schema` endpoint.
  - The Swagger view is made available in the `/schema/swagger` endpoint.
  - **NOTE**: By default, only Superusers can access these endpoints. This can be changed in the `config.env` file, or directly in the settings(setting `SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"]`).


## Configuration

### Config files
`config.env` is the main configuration file. It's recommended to use `core.utilities.env` functions to extract variables in multiple formats from here. See `config.env.example` for available configurations and more details.

Other project specific settings can be changed in Django's `settings.py` file like a regular Django project, to better suit your needs.

## Requirements
Python requirements can be added on the `requirements` folder. Production requirements go on `requirements.txt` and dev-only requirements go on `dev.requirements.txt`. For production, `pip install -r requirements/requirements.txt` will install all needed dependencies. For development, `pip install -r requirements/dev.requirements.txt` will install all needed dependencies (including the dev ones). The `boilerplate.requirements.txt` and `boilerplate.dev.requirements.txt` contain the base requirements that this boilerplate needs, and are automatically installed with the respective production/development requirements files.
