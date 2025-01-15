#!/bin/bash

RUNNING_MODE="DEVELOPMENT"
DOCKER_COMMAND="docker compose -f ./docker/dev/compose.yml"

log() {
    local NORMAL="\e[0m"
    local BOLD_COLOR="\e[1;32m"
    echo -e "${BOLD_COLOR}$1${NORMAL}"
}

# Define some functions for different commands

build() {
    log "[$RUNNING_MODE] building..."
    # Add your build commands using $DOCKER_COMMAND here
    $DOCKER_COMMAND build
    if [ "$RUNNING_MODE" == "DEVELOPMENT" ]; then
        $DOCKER_COMMAND --profile test build
    fi
    # Code to execute when the variable equals the string
    $DOCKER_COMMAND pull
}

run() {
    log "[$RUNNING_MODE] running..."
    # Because the "up" command sometimes hangs
    # Bind docker stop to SIGINT
    stop_docker() {
        log "[$RUNNING_MODE] stopping..."
        $DOCKER_COMMAND stop
    }

    trap stop_docker SIGINT
    $DOCKER_COMMAND up
    trap - SIGINT
}

test() {
    if [ -z "$1" ]; then
        log "[$RUNNING_MODE] testing..."
        $DOCKER_COMMAND run --rm test
    else
        log "[$RUNNING_MODE] testing '$1'..."
        $DOCKER_COMMAND run --rm -e TEST_TARGET=$1 test
    fi
    $DOCKER_COMMAND stop
}

command() {
    log "[$RUNNING_MODE] Running command \"$@\"..."
    $DOCKER_COMMAND run --rm app sh -c "python manage.py $@"
    $DOCKER_COMMAND stop
}

admin() {
    log "[$RUNNING_MODE] Creating admin user..."
    $DOCKER_COMMAND run --rm app sh -c "python manage.py createsuperuser"
    $DOCKER_COMMAND stop
}

schema() {
    log "[$RUNNING_MODE] Generating schmea..."
    $DOCKER_COMMAND run --rm app sh -c "python manage.py spectacular --color --file schema.yml"
    $DOCKER_COMMAND stop
    mv ./app/schema.yml schema.yml
}

clean() {
    local ALL_FLAG=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -a|--all)
                ALL_FLAG=1
                shift
                ;;
            *)
                echo "Invalid option: $1"
                exit 1
                ;;
        esac
    done

    if [ "$ALL_FLAG" -eq 1 ]; then
        log "Cleaning... (ALL)"
    else
        log "Cleaning..."
    fi
    # Clear pycache https://stackoverflow.com/questions/28991015/
    python -Bc "import pathlib; \
                [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]; \
                [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')];"
    if [ "$ALL_FLAG" -eq 1 ]; then
        # Clear the environments files
        if [ "$RUNNING_MODE" == "DEVELOPMENT" ]; then
            rm -rf ./docker/dev/db ./docker/dev/logs ./docker/dev/media ./docker/dev/coverage
        else
            rm -rf ./docker/prod/db ./docker/prod/logs ./docker/prod/media
        fi
    fi
}

usage() {
    echo "Usage: $0 [-p|--production] {build|run|test|command|admin|clean}"
    echo "Commands:"
    echo "  build              Build and pull all images"
    echo "  run                Run the project"
    echo "  test [module]      Run tests (optionally specify module)"
    echo "  command <args>     Shortcut for running any Django manage.py command"
    echo "  admin              Shortcut for Django createsuperuser"
    echo "  schema             Generate the OpenAPI schema using DRF Spectacular"
    echo "  clean [-a|--all]   Clean project files (use -a to clean all)"
    exit 1
}

# Main script

while [[ "$1" =~ ^- ]]; do
    case "$1" in
        -p|--production)
            RUNNING_MODE="PRODUCTION"
            DOCKER_COMMAND="docker compose -f ./docker/prod/compose.yml"
            shift
            ;;
        *)
            echo "Invalid option: $1"
            exit 1
            ;;
    esac
done

COMMAND=$1
shift

case "$COMMAND" in
    build)
        build
        ;;
    run)
        run
        ;;
    test)
        test "$@"
        ;;
    command)
        command "$@"
        ;;
    admin)
        admin
        ;;
    schema)
        schema
        ;;
    clean)
        clean "$@"
        ;;
    *)
        usage
        ;;
esac

exit 0
