# Include the environment file
include config.env
export


# https://stackoverflow.com/questions/2214575/passing-arguments-to-make-run
# If the first argument is "command"...
ifeq (command,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "command"
  COMMAND_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(COMMAND_ARGS):;@:)
endif

# "-" at the start of lines are so that docker compose stop is always ran.

.PHONY: build run test command lint

build:
	docker compose build --no-cache app

run:
	-docker compose up
	docker compose stop

test:
	-docker compose run --rm app sh -c "python manage.py test"
	docker compose stop

command:
	-docker compose run --rm app sh -c "python manage.py $(COMMAND_ARGS)"
	docker compose stop

lint:
	isort ./app
	autoflake ./app
	black ./app
	mypy
