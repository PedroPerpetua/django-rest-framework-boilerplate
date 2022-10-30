# django-rest-framework-boilerplate
This repository contains a boilerplate implementation of a Django Rest Framework + Postgres stack.


## Version
Currently set up for `python 3.11` with `Django 4.1.2` and `Django Rest Framework 3.14.0`.


## Features
- Environment and YAML config files for easy dev and production environments.
- Dockerfile and docker-compose files to dockerize the application.
- A "/ping" endpoint to check server availability.
- Migration to auto setup an ADMIN user (with Django's default User class - can be overridden).
- Base command and a wait_for_db command to ease command development.
- Ready to edit Admin page customization.
- Tests for the implemented features.
- A Makefile to support basic operations.


## Configuration
Two configuration files are set: `config.yaml` and `config.env`. The YAML file is the important one, where all the configs are stored for the application. It uses environment variables on it, so `config.env` is present for convenience; it is not mandatory for execution UNLESS execution is done trough the present `docker-compose.yaml`.

See `config.yaml.example` and `config.env.example` for variables.
