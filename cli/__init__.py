import shutil
import webbrowser
from pathlib import Path
from typing import Literal, Optional
import click
from cli.config import load_config
from cli.docker import production_opt, run_docker_command
from cli.files import APP_DIR, DOCKER_DIR, PROJECT_DIR
from cli.logging import error, log, success, warning
from cli.options import confirm_opt
from cli.update import compare_version, get_tag, get_tags


@click.group
def cli_instance() -> None: ...


@cli_instance.command
@production_opt
def run(production: bool) -> None:
    """Run docker compose up to start the server."""
    run_docker_command("up", production)


@cli_instance.command
@production_opt
def build(production: bool) -> None:
    """Build the docker containers."""
    run_docker_command("build", production)
    run_docker_command("pull", production, show_mode=False)
    success(f"Finished building {'PROD' if production else 'DEV'} docker containers.")


@cli_instance.command
@click.argument("test_path", required=False)
@click.option("--skip-lint", is_flag=True, help="Skip linting. Can't be used with lint-only.")
@click.option("--lint-only", is_flag=True, help="Run lint tools only. Can't be used with skip-lint.")
@click.option("--pattern", "-p", type=str, help="Specify a pattern for pytest to pick tests.")
@click.option(
    "--cpus",
    "-c",
    type=str,
    help='Specify the number of CPUs to use with xdist (positive integer or "auto").',
)
@click.option("--with-stdout", "-s", is_flag=True, help="Include stdout and stderr in the output.")
def test(
    test_path: str,
    skip_lint: bool,
    lint_only: bool,
    pattern: str,
    cpus: int | Literal["auto"],
    with_stdout: bool,
) -> None:
    """Run the linting tools and test suite."""
    if skip_lint and lint_only:
        error("Options skip-lint and lint-only can't be used together!")
        raise click.Abort()

    test_commands = ["pytest"]

    # Check for a specific test
    if test_path:
        if lint_only:
            warning("Test path is ignored with lint-only.")
        else:
            # Make sure it's relative to "app/"
            if test_path.startswith("app/"):
                test_path = test_path[4:]
            test_commands += [test_path]

    # Check for a pattern
    if pattern:
        if lint_only:
            warning("Pattern is ignored with lint-only.")
        else:
            test_commands += ["-k", pattern]

    # Check for xdist cpus
    if cpus:
        if lint_only:
            warning("Cpus is ignored with lint-only.")
        else:
            if cpus != "auto":
                try:
                    cpus = int(cpus)
                    if cpus <= 0:
                        raise ValueError()
                except ValueError as ve:
                    error(f"Invalid cpus value: '{cpus}'.")
                    raise click.Abort() from ve
            test_commands += ["-n", str(cpus)]

    # Check for stdout
    if with_stdout:
        if lint_only:
            warning("With-stdout is ignored with lint-only.")
        if "-n" in test_commands:
            warning("Options cpus and with-stdout don't work together. Ignoring with-stdout.")
        else:
            test_commands += ["-s"]

    # Join all test commands
    test_commands = [" ".join(test_commands)]

    lint_commands = ["ruff check . --fix --unsafe-fixes", "ruff format .", "mypy"]

    if lint_only:
        commands = lint_commands
    elif skip_lint:
        commands = test_commands
    else:
        commands = lint_commands + test_commands
    run_docker_command(
        f'run --rm app sh -c "{" && ".join(commands)}"',
        production=False,
        raise_exception=False,
        show_mode=False,
    )


@cli_instance.command
@production_opt
@click.option(
    "-s",
    "--stop-on-finish",
    is_flag=True,
    help="Stop ALL docker containers once this command finished.",
)
@click.argument("commands", nargs=-1, required=True)
def command(production: bool, stop_on_finish: bool, commands: tuple[str, ...]) -> None:
    """Pass a command to Django's manage.py and execute it."""
    run_docker_command(
        f'run --rm app sh -c "python manage.py {" ".join(commands)}"',
        production,
        stop_on_finish,
    )


@cli_instance.command
def open_coverage() -> None:
    """Open the coverage index file on a new tab in your browser."""
    coverage_file = DOCKER_DIR / "dev" / "coverage" / "index.html"
    if not coverage_file.exists():
        error("No coverage file found. Please run the test command first.")
        raise click.Abort()
    webbrowser.open(f"file://{coverage_file.resolve()}", new=2)


@cli_instance.command
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=True, dir_okay=True, writable=True, path_type=Path),
    default=(PROJECT_DIR / "schema.yml"),
    help="Output destination. Can be a directory, in which case a 'schema.yml' file will be created inside.",
)
def schema(output: Path) -> None:
    """Generate an OpenAPI schema using drf_spectacular."""
    log("Generating schema...")
    run_docker_command(
        'run --rm app sh -c "python manage.py spectacular --color --file schema.yml"',
        production=False,
        stop_on_finish=False,
        show_mode=False,
    )
    if output.is_dir():
        output = output / "schema.yml"
    if output.exists():
        output.unlink()
    (APP_DIR / "schema.yml").rename(output)
    success("Schema generated.")


@cli_instance.command
def clean_cache() -> None:
    """Clean cache folders (__pycache__, .mypy_cache, .ruff_cache, .pytest_cache, .cli_cache)."""
    log("Deleting cache...")
    cache_dirs = ("__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache", ".cli_cache")
    hits: list[Path] = []
    for path in PROJECT_DIR.rglob("*"):
        if "site-packages" in [p.name for p in path.parents]:
            # VENV folder; skip
            continue
        if path.is_dir() and path.name in cache_dirs:
            hits.append(path)
    # Delete them
    [shutil.rmtree(path.resolve()) for path in hits]
    success("Cache successfully deleted.")


@cli_instance.command
@production_opt
@confirm_opt
def clean_data(production: bool, yes: bool) -> None:
    """Clear ALL local data (db, logs, media, coverage) for the respective environment."""
    if not yes:
        click.confirm(
            click.style(
                f"This will delete all data (database, logs, media and coverage) for the {'PROD' if production else 'DEV'} environment. Are you sure?",
                fg="yellow",
                bold=True,
            ),
            abort=True,
        )
    log(f"Deleting all data for the {'PROD' if production else 'DEV'} environment...")
    data_dirs = ("db", "logs", "media", "coverage")
    env_dir = DOCKER_DIR / ("prod" if production else "dev")
    for dir_name in data_dirs:
        path = env_dir / dir_name
        if path.exists() and path.is_dir():
            shutil.rmtree(path.resolve())
    success("Data successfully deleted.")


@cli_instance.command
@confirm_opt
def regenerate_migrations(yes: bool) -> None:
    """
    Regenerate all migrations, by deleting them and running makemigrations again.

    An order for migrations to be generated can be defined in the pyproject.toml file, with the
    boilerplate.regenerate-migrations-order variable. This variable takes a list of strings, and will make this
    command run makemigrations {app} for each app in the list. At the very end, a makemigrations command with no app
    specified will always run to ensure all migrations are generated.
    """
    if not yes:
        click.confirm(
            click.style(
                "This will delete ALL existing migrations before generating new ones. Are you sure you want to proceed?",
                fg="yellow",
                bold=True,
            ),
            abort=True,
        )
    log("Regenerating migrations...")

    # Regenerate them
    config = load_config(raise_exception=False)
    order: list[str] = config["boilerplate"]["regenerate-migrations-order"] or []
    # Concat all determined apps
    app_commands = "".join([f"python manage.py makemigrations {app}; " for app in order])

    # Delete existing migrations
    for migration_folder in APP_DIR.rglob("migrations"):
        if not migration_folder.is_dir():
            continue
        for file in migration_folder.iterdir():
            if file.suffix != ".py" or file.name == "__init__.py":
                continue
            file.unlink()

    # Run the migrations, and run it without arguments at the end to cover any unordered apps
    run_docker_command(
        f'run --rm app sh -c "{app_commands}python manage.py makemigrations"',
        production=False,
        show_mode=False,
    )
    success("Migrations regenerated.")


@cli_instance.command
@click.option("-v", "--target-version", help="Target version to update to.")
@click.option("--ignore-cache", is_flag=True, help="Ignore the cache directory.")
@click.option("--dry", is_flag=True, help="Run without committing the updates; check what would change.")
@confirm_opt
def update(target_version: Optional[str], ignore_cache: bool, dry: bool, yes: bool) -> None:
    """Update the base boilerplate. See the README for more information."""
    # Get the current version
    version = load_config()["boilerplate"]["version"]
    if version is None:
        error("Failed to retrieve version from pyproject.toml.")
        raise click.Abort()
    version = f"v{version}"

    try:
        tags = get_tags()
    except Exception as e:
        error("Failed to get remote versions.")
        raise click.Abort() from e

    current_tag = next((t for t in tags if t["name"] == version), None)
    if current_tag is None:
        error(f"Version {version} not found in git.")
        raise click.Abort()

    if target_version is None:
        target_tag = tags[0]
        if target_tag["name"] == version:
            success(f"Already using the latest ({target_tag['name']}) version!")
            return
    else:
        lookup_tag = next((t for t in tags if t["name"] == target_version), None)
        if lookup_tag is None:
            error(f"Version {target_version} not found in git.")
            raise click.Abort()
        if lookup_tag["name"] == version:
            success(f"Already at version {lookup_tag['name']})!")
            return
        target_tag = lookup_tag

    log(f"Updating from version {current_tag['name']} to {target_tag['name']}...")

    # Get both versions
    try:
        base_dir = get_tag(current_tag, use_cache=(not ignore_cache))
    except Exception as e:
        error(f"Failed to download version {current_tag['name']} from git.")
        raise click.Abort() from e

    try:
        target_dir = get_tag(target_tag, use_cache=(not ignore_cache))
    except Exception as e:
        error(f"Failed to download version {current_tag['name']} from git.")
        raise click.Abort() from e

    # Get the updates
    updates = compare_version(base_dir, target_dir, PROJECT_DIR)
    log("The following updates will be performed:")
    for update in updates:
        click.echo(update.message)

    if dry:
        success("Dry run complete.")
        return

    if not yes:
        log("Do you want to commit these changes?")
        warning(
            "WARNING: doing so will change the files in your project, which may include merge conflicts. Please make sure you have proper backups / version control.",
        )
        if not click.confirm("Proceed?"):
            return

    # Apply the changes
    for update in updates:
        update.perform()

    success("Update complete!")

    conflicts_and_errors = [update for update in updates if update.code in ["ERR", "CFL"]]
    if len(conflicts_and_errors):
        log("Please fix the conflicts on the following files:")
        for conflict in conflicts_and_errors:
            click.echo(conflict.message)
    log("Make sure to run the test battery to potentially fix linting issues and ensure everything went smoothly.")
