import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, TypeVar
import click


FuncT = TypeVar("FuncT", bound=Callable[..., Any])

BASE_DIR = Path(__file__).parent

DEV_COMPOSE = "./docker/dev/compose.yml"
PROD_COMPOSE = "./docker/prod/compose.yml"


def production_opt(func: FuncT) -> FuncT:
    return click.option("-p", "--production", is_flag=True, help="Use production compose")(func)


def get_compose_file(production: bool) -> str:
    click.echo(click.style(f"Running command in {'PROD' if production else 'DEV'} mode...", fg="green", bold=True))
    return PROD_COMPOSE if production else DEV_COMPOSE


def run_docker_command(compose_file: str, command: str) -> None:
    subprocess.run(f"docker compose -f {compose_file} {command}", shell=True, check=True)
    subprocess.run(f"docker compose -f {compose_file} stop", shell=True, check=True)


@click.group
def cli() -> None:
    pass


@cli.command
@production_opt
def run(production: bool) -> None:
    """Run docker compose up to start the server."""
    compose = get_compose_file(production)
    run_docker_command(compose, "up")


@cli.command
@production_opt
def build(production: bool) -> None:
    """Build the docker containers."""
    compose = get_compose_file(production)
    run_docker_command(compose, "build")


@cli.command
@click.option("--skip-lint", is_flag=True, help="Skip linting. Can't be used with lint-only.")
@click.option("--lint-only", is_flag=True, help="Run lint tools only. Can't be used with skip-lint.")
@click.argument("test-suite", required=False)
def test(skip_lint: bool, lint_only: bool, test_suite: str) -> None:
    """Runs the linting tools and test suite."""
    if skip_lint and lint_only:
        click.echo(
            click.style("Options skip-lint and lint-only options can't be used together!", fg="red", bold=True),
            err=True,
        )
        raise click.Abort()

    test_commands = ["coverage run manage.py test", "coverage html", "rm -rf .coverage"]
    if test_suite:
        test_commands[0] += " " + test_suite

    lint_commands = ["ruff check . --fix --unsafe-fixes", "ruff format .", "mypy"]

    if lint_only:
        commands = lint_commands
    elif skip_lint:
        commands = test_commands
    else:
        commands = lint_commands + test_commands
    run_docker_command(DEV_COMPOSE, f'run --rm app sh -c "{" && ".join(commands)}"')


@cli.command
@production_opt
@click.option("-a", "--all", is_flag=True, help="Clear ALL data")
def clean(production: bool, all: bool) -> None:
    """Clear pycache folders; optionally, clear all data (database, logs, media, coverage)."""
    get_compose_file(production)  # To echo the mode
    # Clear pycache
    [shutil.rmtree(p.resolve()) for p in BASE_DIR.rglob("__pycache__")]
    # If all, clear the folders
    if all:
        base_path = BASE_DIR / "docker" / ("prod" if production else "dev")
        for folder_name in ("db", "logs", "media", "coverage"):
            path = base_path / folder_name
            if path.exists():
                shutil.rmtree(path.resolve())


@cli.command
@production_opt
@click.argument("commands", nargs=-1)
def command(production: bool, commands: tuple[str, ...]) -> None:
    """Pass a command to Django's `manage.py`."""
    compose = get_compose_file(production)
    run_docker_command(compose, f'run --rm app sh -c "python manage.py {" ".join(commands)}"')


@cli.command
@click.pass_context
def schema(ctx: click.Context) -> None:
    """Generate an OpenAPI schema using `drf_spectacular`."""
    ctx.invoke(command, production=False, commands=("spectacular --color --file schema.yml",))
    target = BASE_DIR / "schema.yml"
    if target.exists():
        target.unlink()
    (BASE_DIR / "app" / "schema.yml").rename(BASE_DIR / "schema.yml")


@cli.command
@click.option("-y", "--yes", is_flag=True, help="Answer yes to the prompt")
@click.pass_context
def regenerate_migrations(ctx: click.Context, yes: bool) -> None:
    """Regenerate all migrations, by deleting them and running `makemigrations` again."""
    if not yes:
        click.confirm(
            "THIS WILL DELETE ALL EXISTING MIGRATIONS before generating new ones. Are you sure you want to proceed?",
            abort=True,
        )
    for migration_folder in (BASE_DIR / "app").rglob("migrations"):
        if not migration_folder.is_dir():
            continue
        # Loop through files in the migrations folder
        for file in migration_folder.iterdir():
            # Skip __init__.py and any non-Python files
            if file.name != "__init__.py" and file.suffix == ".py":
                file.unlink()
    ctx.invoke(command, production=False, commands=("makemigrations",))


if __name__ == "__main__":
    cli()
