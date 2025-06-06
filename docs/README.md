[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

django-rest-framework-boilerplate
===
This repository contains a boilerplate implementation of a Django Rest Framework + Postgres stack, with extended functionality and utilities.

Provided by [PedroPerpetua](https://github.com/PedroPerpetua).


## Version
Currently set up for `python 3.13.3` with `Django 5.2.1` and `Django Rest Framework 3.16.0`.


## Getting started
After copying this boilerplate, make sure to provide it with it's own `README`, and editing the `pyproject.toml` project name.

Install the requirements with `pip install -r requirements/dev.requirements.txt`.

Run `python make.py test` to ensure everything is working as intended.

Run `python make.py run` to run the dev server.


## Features

### Project
- Configuration trough environment variables.
- Separated requirement file structure for both production and development.
- Dockerized application, both for development and production environments.
- Linting preconfigured with `ruff`, static type checking with `mypy`, and test `coverage` included.
- CI/CD for linting and testing trough Github Actions.
- Tests for the implemented features.
- A `make.py` CLI to support basic operations.

### Django Functionality
- Multiple utility functions and extensions frequently used in Django projects.
- Template app for the `startapp` command that follows the usual restframework patterns.
- Base command to ease command development, with additional `wait_for_db` and `setup` commands.
- Ready to edit custom Admin page.
  - Also features an ordering utility to easily re-order apps and models on the admin page.
- Dynamic configuration through Constance.
- A base for a custom user model with the full JWT authentication flow.
  - This custom user model can be easily setup with mixins to change the username field, set up required email or username, etc.
  - Also includes classes and mixins for views to facilitate working with Users.
  - **NOTE**: The users, by default, have `active=True`. It may be desired to change this behavior.
  - **NOTE**: The simplejwt settings have `UPDATE_LAST_LOGIN: True`. This may hinder performance and may be desired to change this behavior.
  - **NOTE**: By default, registration through REST endpoints is disabled. This can be changed in the Constance configuration.

### REST
- A `/ping` endpoint to check server availability.
- Custom error messages using [DRF Standardized Errors](https://github.com/ghazi-git/drf-standardized-errors).
  - A custom `ExceptionHandler` that will automatically convert Django's `ValidationError`s to DRF's `ValidationError`s.
- Out of the box OpenAPI schema with Swagger support using [DRF Spectacular](https://github.com/tfranzel/drf-spectacular)
  - The schema is made available in the `/schema` endpoint.
  - The Swagger view is made available in the `/schema/swagger` endpoint.
  - **NOTE**: By default, only admin users can access these endpoints. This can be changed in the Constance configuration.


## Configuration

### Dynamic configuration
Settings can be included as dynamic using [Constance](https://github.com/jazzband/django-constance). See their docs for more information.

### Config files
`.env` is the main configuration file. It's recommended to use `extensions.utilities.env` functions to extract variables in multiple formats from here. See `.env.example` for available configurations and more details. This file should be placed in the respective docker folders: `./docker/dev/.env` and / or `./docker/prod/.env`.

Other project specific settings can be changed in Django's `settings.py` file like a regular Django project, to better suit your needs.


## Requirements
Python requirements can be added on the `requirements` folder. Production requirements go on `requirements.txt` and dev-only requirements go on `dev.requirements.txt`. For production, `pip install -r requirements/requirements.txt` will install all needed dependencies. For development, `pip install -r requirements/dev.requirements.txt` will install all needed dependencies (including the dev ones). The `boilerplate.requirements.txt` and `boilerplate.dev.requirements.txt` contain the base requirements that this boilerplate needs, and are automatically installed with the respective production/development requirements files.


## Make
A convenience `make.py` CLI is available for use. Run `python make.py --help` to see all options.


## Auto-updater
This boilerplate comes with an auto-updater since version `2.1.0`, by running `python make.py update`. This will attempt to update the current boilerplate base version to the latest version. `python make.py update --help` for more options.

**It's highly advisable that you have version control set up and are working on a clean tree when you start the update.** Updating the boilerplate will modify files in the project through adding, removing, and merging files; when going through major version updates, it's very likely that some automated changes may be wrong and break things. The recommended process for updating involves creating a new branch, performing the update, fixing any merge conflicts generated by the update, re-building the project, running the test suite again, and then carefully reviewing the pull request from the new branch back to the original branch.

### Before 2.1.0
It's possible to attempt to auto-update projects with versions _before_ `2.1.0`. To do so, create a `pyproject.toml` file INSIDE the `app` folder, with the following content:
```toml
[boilerplate]
version = "<Your current boilerplate version here>"
```

Afterwards, copy the most recent `make.py` script onto the project root renamed (for example, `_make.py`, so it doesn't conflict with the new `make.py`s that may be created) and run `python <make.py renamed> update` as usual.


## Deployment
A production ready compose is available in the `docker/prod` folder. The images here _assume_ the existence of `cert.pem` and `key.pem` files in the same folder, with the certificates to used for production.

The following configs are highly recommended for production:
```env
DEBUG=0
ALLOWED_HOSTS="<not empty>"
LOG_LEVEL=20

CORS_ALLOW_ALL_ORIGINS=0
CORS_ALLOWED_ORIGINS="<not empty>"

CSRF_TRUSTED_ORIGINS="<not empty>"
CSRF_COOKIE_SECURE=1
SESSION_COOKIE_SECURE=1
```
