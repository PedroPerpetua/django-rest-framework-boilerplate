# django-rest-framework-boilerplate
This repository contains a boilerplate implementation of a Django Rest Framework + Postgres stack.


## Version
Currently set up for `python 3.11` with `Django 4.1.2` and `Django Rest Framework 3.14.0`.


## Features
- Configuration trough environment variables.
- Dockerized application.
- Separated requirement file structure for both production and development.
- A "/ping" endpoint to check server availability.
- Multiple utility functions and extensions usually applied in Django projects.
- Template app for the startapp command that follows the usual restframework patterns.
- Base command to ease command development, with additional wait_for_db and setup commands.
- Migration to auto setup an ADMIN user (with Django's default User class - can be overridden).
- Ready to edit Admin page customization.
- Tests for the implemented features.
- A Makefile to support basic operations.


## Configuration

### Config files
`config.env` is the main configuration file. It's recommended to use `core.utilities.env` functions to extract variables in multiple formats from here.

## Requirements
Python requirements can be added on the `requirements` folder. Production requirements go on `requirements.txt` and dev-only requirements go on `dev.requirements.txt`. For production, `pip install -r requirements/requirements.txt` will install all needed dependencies. For development, `pip install -r requirements/dev.requirements.txt` will install all needed dependencies (including the dev ones). The `boilerplate.requirements.txt` and `boilerplate.dev.requirements.txt` contain the base requirements that this boilerplate needs, and are automatically installed with the respective production/development requirements files.
