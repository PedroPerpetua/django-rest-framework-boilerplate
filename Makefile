# https://stackoverflow.com/questions/2214575/passing-arguments-to-make-run
# If the first argument is "command"...
ifeq (command,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "command"
  COMMAND_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  # This will spit an error wich is fine for now
  $(eval $(COMMAND_ARGS):ignore_this_error;@:)
endif

# "-" at the start of lines are so that docker compose stop is always ran.

.PHONY: build run test clear command

build:
	docker compose build

run:
	-docker compose up
	docker compose stop

test:
	-docker compose run --rm test
	docker compose stop

clean:
	pyclean .
	rm -rf ./.mypy_cache
	rm -rf ./app/logs
	rm -rf ./coverage

command:
	-docker compose run --rm app sh -c "python manage.py $(COMMAND_ARGS)"
	docker compose stop
