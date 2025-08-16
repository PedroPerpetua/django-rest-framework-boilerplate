import subprocess
from typing import Any, Callable
import click
from cli.files import DOCKER_DIR
from cli.logging import error, warning
from docker import DockerClient
from docker.errors import DockerException


def run_docker_command(
    command: str,
    production: bool = False,
    stop_on_finish: bool = False,
    *,
    raise_exception: bool = True,
    show_mode: bool = True,
) -> None:
    """Run a command inside the specified docker container."""
    # Check if docker is operational
    try:
        docker_client = DockerClient.from_env()
        docker_client.ping()
    except DockerException as de:
        error("Failed to reach the docker client. Are you sure it's running?")
        raise click.Abort() from de
    if show_mode:
        warning(f"Running command in {'PROD' if production else 'DEV'} mode...")
    folder = DOCKER_DIR / ("prod" if production else "dev")
    path = str(folder.resolve())
    try:
        # Unfortunately, docker-py does not support compose
        # https://github.com/docker/compose/issues/4542
        subprocess.run(f"cd {path} && docker compose {command}", shell=True, check=True)
        if stop_on_finish:
            subprocess.run(f"cd {path} && docker compose stop", shell=True, check=True)
    except:
        if raise_exception:
            raise


def production_opt[F: Callable[..., Any]](func: F) -> F:
    """Common option to define the execution mode (DEV or PROD)."""
    return click.option("-p", "--production", is_flag=True, help="Use production compose")(func)
