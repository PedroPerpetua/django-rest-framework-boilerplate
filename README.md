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
  - This custom user model can be easily setup with mixins to change the username field, set up required email or username, etc.
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


## Makefile
A convenience `Makefile` is available for use. It has the following commands:

### `build`
The build command will build all services (`db`, `app` and `test`). This is usually a required step when files not in the /app folder are changed (for example, requirements files).

### `run`
Runs the `app` service, starting the Django server.

### `test`
Runs the `test` service; this will run all linting tools in the following order:
- `isort`
- `autoflake`
- `black`
  - All commands above are done _in place_, meaning they will change the files in /app as they see fit.
- `mypy`
  - If `mypy` fails, execution will be stopped (before tests are ran). **This will still leave the _in place_ changes of the linting tools** (they will not be reverted).

Afterwards, runs the test suite trough Django, wrapped in the `coverage` module to generate a coverage report in the `/coverage` folder IF the tests are successful.

### `clean`
This command will clear all cache files from Python and `mypy`, clear all logs and clear the coverage report.


### `command`
This is a shortcut command to run Django management commands. This command should be used as follows: `make command <commands to be passed>`. Under the hood, the `app` service will start and run `python manage.py <commands passed>`.

Examples:
- `make command makemigrations` will run the Django `makemigrations` command;
- `make command test appname.tests.Testclass.test_name` will run a specific test by itself as given by the "Python import statement" (see [Django's documentation](https://docs.djangoproject.com/en/4.1/topics/testing/overview/#running-tests) about it);
- `make command "test -v2"` (notice the `"`; this is because we're using a command with a `-` flag) will run the test suit with `verbosity=2`.

It's also worth nothing that once this command is used, Makefile will show an `ignore_this_error` error. This is because of the way we're passing arguments to the command, and it's just a safety mechanism that can be ignored. See the `Makefile` for more information.
