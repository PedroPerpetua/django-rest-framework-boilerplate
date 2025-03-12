import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, TypeVar
import click


FuncT = TypeVar("FuncT", bound=Callable[..., Any])

BASE_DIR = Path(__file__).parent


def production_opt(func: FuncT) -> FuncT:
    return click.option("-p", "--production", is_flag=True, help="Use production compose")(func)


def run_docker_command(command: str, production: bool = False, *, raise_exception: bool = True) -> None:
    click.echo(click.style(f"Running command in {'PROD' if production else 'DEV'} mode...", fg="green", bold=True))
    folder = BASE_DIR / "docker" / ("prod" if production else "dev")
    try:
        subprocess.run(f"cd {folder.resolve()} && docker compose {command}", shell=True, check=True)
        subprocess.run(f"cd {folder.resolve()} && docker compose stop", shell=True, check=True)
    except:
        if raise_exception:
            raise


@click.group
def cli() -> None:
    pass


@cli.command
@production_opt
def run(production: bool) -> None:
    """Run docker compose up to start the server."""
    run_docker_command("up", production)


@cli.command
@production_opt
def build(production: bool) -> None:
    """Build the docker containers."""
    run_docker_command("build", production)


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

    test_commands = ["coverage run manage.py test", "coverage html"]
    if test_suite:
        test_commands[0] += " " + test_suite

    lint_commands = ["ruff check . --fix --unsafe-fixes", "ruff format .", "mypy"]

    if lint_only:
        commands = lint_commands
    elif skip_lint:
        commands = test_commands
    else:
        commands = lint_commands + test_commands
    run_docker_command(f'run --rm app sh -c "{" && ".join(commands)}"', production=False, raise_exception=False)


@cli.command
@production_opt
@click.argument("commands", nargs=-1)
def command(production: bool, commands: tuple[str, ...]) -> None:
    """Pass a command to Django's `manage.py`."""
    run_docker_command(f'run --rm app sh -c "python manage.py {" ".join(commands)}"', production)


@cli.command
@production_opt
@click.option("-a", "--all", is_flag=True, help="Clear ALL data")
@click.option("-y", "--yes", is_flag=True, help="Confirm cleaning ALL data without prompt.")
def clean(production: bool, all: bool, yes: bool) -> None:
    """Clear pycache folders; optionally, clear all data (database, logs, media, coverage)."""
    if yes and not all:
        click.echo(click.style("Passing --yes without --all does nothing.", fg="yellow"))
    # Clear pycache
    [shutil.rmtree(p.resolve()) for p in BASE_DIR.rglob("__pycache__")]
    click.echo(click.style("Pycache cleared.", fg="green"))
    # If all, clear the folders
    if all:
        if not yes:
            click.confirm(
                f"This will delete all data (database, logs, media and coverage) for the {'PROD' if production else 'DEV'} environment. Are you sure?",
                abort=True,
            )
        base_path = BASE_DIR / "docker" / ("prod" if production else "dev")
        for folder_name in ("db", "logs", "media", "coverage"):
            path = base_path / folder_name
            if path.exists():
                shutil.rmtree(path.resolve())


@cli.command
@click.pass_context
def schema(ctx: click.Context) -> None:
    """Generate an OpenAPI schema using `drf_spectacular`."""
    ctx.invoke(command, production=False, commands=("spectacular --color --file schema.yml",))
    target = BASE_DIR / "schema.yml"
    if target.exists():
        target.unlink()
    (BASE_DIR / "app" / "schema.yml").rename(BASE_DIR / "schema.yml")
    click.echo(click.style("Schema generated.", fg="green"))


@cli.command
@click.option("-y", "--yes", is_flag=True, help="Confirm deleting current migrations without prompt.")
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
    click.echo(click.style("Migrations regenerated.", fg="green"))


if __name__ == "__main__":
    cli()
