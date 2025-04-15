import filecmp
import requests
import shutil
import subprocess
import tomllib
import webbrowser
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, Optional, TypedDict, TypeVar
import click


FuncT = TypeVar("FuncT", bound=Callable[..., Any])

BASE_DIR = Path(__file__).parent


# -----------------------------------------------------------------------------
# Auxiliary content for the update functionality ------------------------------
# -----------------------------------------------------------------------------

# Python Diff3 implementation -------------------------------------------------
# https://github.com/schuhschuh/cmake-basis/blob/master/src/utilities/python/diff3.py
# ============================================================================
# Copyright (C) 1988, 1989, 1992, 1993, 1994 Free Software Foundation, Inc.
# Copyright (c) 2011-2012 University of Pennsylvania
# Copyright (c) 2013-2014 Andreas Schuh
# All rights reserved.
# ============================================================================

"""

    @file  diff3.py
    @brief Three-way file comparison algorithm.

    This is a line-by-line translation of the Text::Diff3 Perl module version
    0.10 written by MIZUTANI Tociyuki <tociyuki@gmail.com>.

    The Text::Diff3 Perl module in turn was based on the diff3 program:

    Three way file comparison program (diff3) for Project GNU.
    Copyright (C) 1988, 1989, 1992, 1993, 1994 Free Software Foundation, Inc.
    Written by Randy Smith

    The two-way file comparison procedure was based on the article:
    P. Heckel. ``A technique for isolating differences between files.''
    Communications of the ACM, Vol. 21, No. 4, page 264, April 1978.

"""


from operator import xor


# ----------------------------------------------------------------------------
def diff3(yourtext, origtext, theirtext):
    """Three-way diff based on the GNU diff3.c by R. Smith.

    @param [in] yourtext   Array of lines of your text.
    @param [in] origtext   Array of lines of original text.
    @param [in] theirtext  Array of lines of their text.

    @returns Array of tuples containing diff results. The tuples consist of
             (cmd, loA, hiA, loB, hiB), where cmd is either one of
             '0', '1', '2', or 'A'.

    """
    # diff result => [(cmd, loA, hiA, loB, hiB), ...]
    d2 = (diff(origtext, yourtext), diff(origtext, theirtext))
    d3 = []
    r3 = [None, 0, 0, 0, 0, 0, 0]
    while d2[0] or d2[1]:
        # find a continual range in origtext lo2..hi2
        # changed by yourtext or by theirtext.
        #
        #     d2[0]        222    222222222
        #  origtext     ...L!!!!!!!!!!!!!!!!!!!!H...
        #     d2[1]          222222   22  2222222
        r2 = ([], [])
        if not d2[0]:
            i = 1
        else:
            if not d2[1]:
                i = 0
            else:
                if d2[0][0][1] <= d2[1][0][1]:
                    i = 0
                else:
                    i = 1
        j = i
        k = xor(i, 1)
        hi = d2[j][0][2]
        r2[j].append(d2[j].pop(0))
        while d2[k] and d2[k][0][1] <= hi + 1:
            hi_k = d2[k][0][2]
            r2[k].append(d2[k].pop(0))
            if hi < hi_k:
                hi = hi_k
                j = k
                k = xor(k, 1)
        lo2 = r2[i][0][1]
        hi2 = r2[j][-1][2]
        # take the corresponding ranges in yourtext lo0..hi0
        # and in theirtext lo1..hi1.
        #
        #   yourtext     ..L!!!!!!!!!!!!!!!!!!!!!!!!!!!!H...
        #      d2[0]        222    222222222
        #   origtext     ...00!1111!000!!00!111111...
        #      d2[1]          222222   22  2222222
        #  theirtext          ...L!!!!!!!!!!!!!!!!H...
        if r2[0]:
            lo0 = r2[0][0][3] - r2[0][0][1] + lo2
            hi0 = r2[0][-1][4] - r2[0][-1][2] + hi2
        else:
            lo0 = r3[2] - r3[6] + lo2
            hi0 = r3[2] - r3[6] + hi2
        if r2[1]:
            lo1 = r2[1][0][3] - r2[1][0][1] + lo2
            hi1 = r2[1][-1][4] - r2[1][-1][2] + hi2
        else:
            lo1 = r3[4] - r3[6] + lo2
            hi1 = r3[4] - r3[6] + hi2
        # detect type of changes
        if not r2[0]:
            cmd = "1"
        elif not r2[1]:
            cmd = "0"
        elif hi0 - lo0 != hi1 - lo1:
            cmd = "A"
        else:
            cmd = "2"
            for d in range(0, hi0 - lo0 + 1):
                (i0, i1) = (lo0 + d - 1, lo1 + d - 1)
                ok0 = 0 <= i0 and i0 < len(yourtext)
                ok1 = 0 <= i1 and i1 < len(theirtext)
                if xor(ok0, ok1) or (ok0 and yourtext[i0] != theirtext[i1]):
                    cmd = "A"
                    break
        d3.append((cmd, lo0, hi0, lo1, hi1, lo2, hi2))
    return d3


# ----------------------------------------------------------------------------
def merge(yourtext, origtext, theirtext):
    res = {"conflict": 0, "body": []}
    d3 = diff3(yourtext, origtext, theirtext)
    text3 = (yourtext, theirtext, origtext)
    i2 = 1
    for r3 in d3:
        for lineno in range(i2, r3[5]):
            res["body"].append(text3[2][lineno - 1])
        if r3[0] == "0":
            for lineno in range(r3[1], r3[2] + 1):
                res["body"].append(text3[0][lineno - 1])
        elif r3[0] != "A":
            for lineno in range(r3[3], r3[4] + 1):
                res["body"].append(text3[1][lineno - 1])
        else:
            res = _conflict_range(text3, r3, res)
        i2 = r3[6] + 1
    for lineno in range(i2, len(text3[2]) + 1):
        res["body"].append(text3[2][lineno - 1])
    return res


# ----------------------------------------------------------------------------
def _conflict_range(text3, r3, res):
    text_a = []  # their text
    for i in range(r3[3], r3[4] + 1):
        text_a.append(text3[1][i - 1])
    text_b = []  # your text
    for i in range(r3[1], r3[2] + 1):
        text_b.append(text3[0][i - 1])
    d = diff(text_a, text_b)
    if _assoc_range(d, "c") and r3[5] <= r3[6]:
        res["conflict"] += 1
        res["body"].append("<<<<<<<")
        for lineno in range(r3[1], r3[2] + 1):
            res["body"].append(text3[0][lineno - 1])
        res["body"].append("|||||||")
        for lineno in range(r3[5], r3[6] + 1):
            res["body"].append(text3[2][lineno - 1])
        res["body"].append("=======")
        for lineno in range(r3[3], r3[4] + 1):
            res["body"].append(text3[1][lineno - 1])
        res["body"].append(">>>>>>>")
        return res
    ia = 1
    for r2 in d:
        for lineno in range(ia, r2[1]):
            res["body"].append(text_a[lineno - 1])
        if r2[0] == "c":
            res["conflict"] += 1
            res["body"].append("<<<<<<<")
            for lineno in range(r2[3], r2[4] + 1):
                res["body"].append(text_b[lineno - 1])
            res["body"].append("=======")
            for lineno in range(r2[1], r2[2] + 1):
                res["body"].append(text_a[lineno - 1])
            res["body"].append(">>>>>>>")
        elif r2[0] == "a":
            for lineno in range(r2[3], r2[4] + 1):
                res["body"].append(text_b[lineno - 1])
        ia = r2[2] + 1
    for lineno in range(ia, len(text_a)):
        res["body"].append(text_a[lineno - 1])
    return res


# ----------------------------------------------------------------------------
def _assoc_range(diff, diff_type):
    for d in diff:
        if d[0] == diff_type:
            return d
    return None


# ----------------------------------------------------------------------------
def _diff_heckel(text_a, text_b):
    """Two-way diff based on the algorithm by P. Heckel.

    @param [in] text_a Array of lines of first text.
    @param [in] text_b Array of lines of second text.

    @returns TODO

    """
    d = []
    uniq = [(len(text_a), len(text_b))]
    (freq, ap, bp) = ({}, {}, {})
    for i in range(len(text_a)):
        s = text_a[i]
        freq[s] = freq.get(s, 0) + 2
        ap[s] = i
    for i in range(len(text_b)):
        s = text_b[i]
        freq[s] = freq.get(s, 0) + 3
        bp[s] = i
    for s, x in freq.items():
        if x == 5:
            uniq.append((ap[s], bp[s]))
    (freq, ap, bp) = ({}, {}, {})
    uniq.sort(key=lambda x: x[0])
    (a1, b1) = (0, 0)
    while a1 < len(text_a) and b1 < len(text_b):
        if text_a[a1] != text_b[b1]:
            break
        a1 += 1
        b1 += 1
    for a_uniq, b_uniq in uniq:
        if a_uniq < a1 or b_uniq < b1:
            continue
        (a0, b0) = (a1, b1)
        (a1, b1) = (a_uniq - 1, b_uniq - 1)
        while a0 <= a1 and b0 <= b1:
            if text_a[a1] != text_b[b1]:
                break
            a1 -= 1
            b1 -= 1
        if a0 <= a1 and b0 <= b1:
            d.append(("c", a0 + 1, a1 + 1, b0 + 1, b1 + 1))
        elif a0 <= a1:
            d.append(("d", a0 + 1, a1 + 1, b0 + 1, b0))
        elif b0 <= b1:
            d.append(("a", a0 + 1, a0, b0 + 1, b1 + 1))
        (a1, b1) = (a_uniq + 1, b_uniq + 1)
        while a1 < len(text_a) and b1 < len(text_b):
            if text_a[a1] != text_b[b1]:
                break
            a1 += 1
            b1 += 1
    return d


# ----------------------------------------------------------------------------
diff = _diff_heckel  # default two-way diff function used by diff3()

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Auxiliary type definitions for the github API -------------------------------
# -----------------------------------------------------------------------------


class CommitData(TypedDict):
    sha: str
    url: str


class TagData(TypedDict):
    name: str
    zipball_url: str
    tarball_url: str
    commit: CommitData
    node_id: str


FILE_ADDED_CODE = -1
FILE_DELETED_CODE = -2
FILE_MODIFIED_CODE = -3

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Auxiliary functions for printing with color ---------------------------------
# -----------------------------------------------------------------------------


def log(message: str) -> None:
    click.echo(message)


def success(message: str, *, bold: bool = False) -> None:
    click.echo(click.style(message, fg="green", bold=bold))


def warning(message: str, *, bold: bool = False) -> None:
    click.echo(click.style(message, fg="yellow", bold=bold))


def error(message: str, *, bold: bool = False) -> None:
    click.echo(click.style(message, fg="red", bold=bold), err=True)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Auxiliary CLI functions -----------------------------------------------------
# -----------------------------------------------------------------------------


def production_opt(func: FuncT) -> FuncT:
    """Auxiliary common option for multiple commands."""
    return click.option("-p", "--production", is_flag=True, help="Use production compose")(func)


def run_docker_command(command: str, production: bool = False, *, raise_exception: bool = True) -> None:
    """Run a command inside the specified docker container."""
    warning(f"Running command in {'PROD' if production else 'DEV'} mode...")
    folder = BASE_DIR / "docker" / ("prod" if production else "dev")
    try:
        subprocess.run(f"cd {folder.resolve()} && docker compose {command}", shell=True, check=True)
        subprocess.run(f"cd {folder.resolve()} && docker compose stop", shell=True, check=True)
    except:
        if raise_exception:
            raise


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


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
        error("Options skip-lint and lint-only options can't be used together!", bold=True)
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
def open_coverage() -> None:
    """Open the coverage index file on a new tab in your browser."""
    coverage_file = BASE_DIR / "docker" / "dev" / "coverage" / "index.html"
    if not coverage_file.exists():
        error("No coverage file found. Please run the test command first.")
        raise click.Abort()
    webbrowser.open(f"file://{coverage_file.resolve()}", new=2)


@cli.command
@production_opt
@click.argument("commands", nargs=-1)
def command(production: bool, commands: tuple[str, ...]) -> None:
    """Pass a command to Django's `manage.py`."""
    if len(commands) == 0:
        error("No command passed!")
        raise click.Abort()
    run_docker_command(f'run --rm app sh -c "python manage.py {" ".join(commands)}"', production)


@cli.command
@production_opt
@click.option("-a", "--all", is_flag=True, help="Clear ALL data")
@click.option("-y", "--yes", is_flag=True, help="Confirm cleaning ALL data without prompt.")
def clean(production: bool, all: bool, yes: bool) -> None:
    """Clear pycache folders; optionally, clear all data (database, logs, media, coverage)."""
    if yes and not all:
        warning("Passing --yes without --all does nothing.")
    # Clear pycache
    [shutil.rmtree(pycache_dir.resolve()) for pycache_dir in BASE_DIR.rglob("__pycache__")]
    success("Pycache cleared.", bold=True)
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
        success("All data cleared.", bold=True)


@cli.command
@click.pass_context
def schema(ctx: click.Context) -> None:
    """Generate an OpenAPI schema using `drf_spectacular`."""
    ctx.invoke(command, production=False, commands=("spectacular --color --file schema.yml",))
    target = BASE_DIR / "schema.yml"
    if target.exists():
        target.unlink()
    (BASE_DIR / "app" / "schema.yml").rename(BASE_DIR / "schema.yml")
    success("Schema generated.", bold=True)


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
    success("Migrations regenerated.")


@cli.command
@click.option("-c", "--commit", is_flag=True, help="Commit the changes without prompting.")
@click.option("-v", "--target-version", help="Target version to update to.")
@click.option("--ignore-cache", is_flag=True, help="Ignore the cache directory.")
def update(commit: bool, target_version: Optional[str], ignore_cache: bool) -> None:
    """Update the base boilerplate. See the README for more information."""
    # Get the current version
    pyproject_file = BASE_DIR / "app" / "pyproject.toml"
    if not pyproject_file.exists() or not pyproject_file.is_file():
        error("Failed to find pyproject.toml file.", bold=True)
        raise click.Abort()
    with open(pyproject_file, "rb") as pyproject:
        data = tomllib.load(pyproject)
    current_version = data.get("boilerplate", {}).get("version", None)
    if current_version is None:
        error("Failed to find boilerplate version in pyproject.toml file (boilerplate.version).", bold=True)
        raise click.Abort()

    # Get the remote versions
    try:
        tags_res = requests.get("https://api.github.com/repos/PedroPerpetua/django-rest-framework-boilerplate/tags")
        tags_data: list[TagData] = tags_res.json()
    except Exception as e:
        error("Failed to get remote versions.", bold=True)
        raise click.Abort() from e

    if target_version is None:
        target_version = tags_data[0].get("name")[1:]  # Remove the "v."

    if current_version == target_version:
        success(f"Already at the target version! ({target_version})")
        return

    # Check the current version
    current_version_data = next((tag for tag in tags_data if tag.get("name")[1:] == current_version), None)
    if current_version_data is None:
        error("Failed to match current version to remote.", bold=True)
        raise click.Abort()

    # Check the target version
    target_version_data = next((tag for tag in tags_data if tag.get("name")[1:] == target_version), None)
    if target_version_data is None:
        error("Failed to match current version to remote.", bold=True)
        raise click.Abort()

    warning(f"Updating from version {current_version} to {target_version}.")

    # Download both versions
    if ignore_cache:
        temp_dir = TemporaryDirectory(ignore_cleanup_errors=True)
        cache_dir = Path(temp_dir.name)
    else:
        # Create a cache directory with a gitignore
        cache_dir = BASE_DIR / ".boilerplate_cache"
        cache_dir.mkdir(exist_ok=True)
        with open(cache_dir / ".gitignore", "w+") as gitignore_file:
            gitignore_file.write("*")

    def download_and_extract(url: str, version: str) -> None:
        dest = cache_dir / version
        if dest.exists():
            warning(f"Version {version} found in cache.")
            return
        # Download the file
        try:
            res = requests.get(url, stream=True)
            zip_path = cache_dir / f"{version}.zip"
            with open(zip_path, "+wb") as out_file:
                shutil.copyfileobj(res.raw, out_file)
        except Exception as e:
            error(f"Failed to download {version}.", bold=True)
            raise click.Abort() from e
        # Extract the file
        try:
            dest.mkdir()
            with zipfile.ZipFile(zip_path, "r") as zip_file:
                files = zip_file.infolist()
                for file_path in files[1:]:
                    if file_path.is_dir():
                        continue
                    file_path.filename = "/".join(file_path.filename.split("/")[1:])
                    zip_file.extract(file_path, dest)
        except Exception as e:
            error(f"Failed to extract {version}.", bold=True)
            raise click.Abort() from e

    # Download both versions
    download_and_extract(current_version_data.get("zipball_url"), current_version)
    download_and_extract(target_version_data.get("zipball_url"), target_version)

    # Find the files that changed
    current_version_dir = cache_dir / current_version
    target_version_dir = cache_dir / target_version
    diff = filecmp.dircmp(current_version_dir, target_version_dir, shallow=False, ignore=[None])

    def merge_files(ancestor: Path, source: Path, dest: Path) -> tuple[list[str], int]:
        # Our current version was the original but modified - merge
        with open(ancestor, "r") as curr:
            current_file_lines = [line.rstrip() for line in curr.readlines()]
        with open(source, "r") as c:
            target_version_lines = [line.rstrip() for line in c.readlines()]
        with open(dest, "r") as w:
            working_lines = [line.rstrip() for line in w.readlines()]
        merge_result = merge(working_lines, current_file_lines, target_version_lines)
        return merge_result["body"], merge_result["conflict"]

    def compare_files(
        comparison: filecmp.dircmp,
        to_copy: Optional[list[tuple[Path, Path]]] = None,
        to_delete: Optional[list[Path]] = None,
        to_update: Optional[list[tuple[Path, Path]]] = None,
        to_merge: Optional[list[tuple[Path, list[str]]]] = None,
        conflicts: Optional[list[tuple[Path, list[str], int]]] = None,
    ) -> tuple[
        list[tuple[Path, Path]],
        list[Path],
        list[tuple[Path, Path]],
        list[tuple[Path, list[str]]],
        list[tuple[Path, list[str], int]],
    ]:
        """Recursive function that navigates a dircmp object and classifies all files."""
        if to_copy is None:
            to_copy = []
        if to_delete is None:
            to_delete = []
        if to_update is None:
            to_update = []
        if to_merge is None:
            to_merge = []
        if conflicts is None:
            conflicts = []

        for deleted_file in comparison.left_only:
            # File was deleted - check if it matches any of ours
            current_file = Path(comparison.left) / deleted_file
            working_file = BASE_DIR / Path(comparison.left).relative_to(current_version_dir) / deleted_file

            if not working_file.exists():
                # We're good to do nothing
                continue
            if filecmp.cmp(current_file, working_file):
                # Our current version is the same as the original
                to_delete += [working_file]
                continue
            # We changed the file that was deleted
            conflicts += [(working_file, [], FILE_DELETED_CODE)]

        for added_file in comparison.right_only:
            # File was added - check if it matches any of ours
            current_file = Path(comparison.right) / added_file
            working_file = BASE_DIR / Path(comparison.right).relative_to(target_version_dir) / added_file

            if not working_file.exists():
                # We're good to copy
                to_copy += [(current_file, working_file)]
                continue
            if filecmp.cmp(current_file, working_file):
                # Our current version is the same as the original - do nothing
                continue
            # We changed the file that conflicts with the added one - attempt to merge them
            merged_lines, issues = merge_files(current_file, added_file, working_file)
            if issues:
                conflicts += [(working_file, merged_lines, issues)]
            else:
                to_merge += [(working_file, merged_lines)]

        for changed_file in comparison.diff_files:
            current_file = Path(comparison.left) / changed_file
            target_file = Path(comparison.right) / changed_file
            working_file = BASE_DIR / Path(comparison.left).relative_to(current_version_dir) / changed_file

            if not working_file.exists():
                # Our current version was deleted for some reason
                conflicts += [(working_file, [], FILE_ADDED_CODE)]
                continue
            if filecmp.cmp(current_file, working_file):
                # Our current version is the same as the original
                to_update += [(working_file, target_file)]
                continue
            if not filecmp.cmp(working_file, target_file):
                # Our current version was the original but modified - merge
                merged_lines, issues = merge_files(current_file, target_file, working_file)
                if issues:
                    conflicts += [(working_file, merged_lines, issues)]
                else:
                    to_merge += [(working_file, merged_lines)]

        for sub_comparison in comparison.subdirs.values():
            new_copy, new_delete, new_update, new_merge, new_conflict = compare_files(sub_comparison)
            to_copy += new_copy
            to_delete += new_delete
            to_update += new_update
            to_merge += new_merge
            conflicts += new_conflict
        return to_copy, to_delete, to_update, to_merge, conflicts

    to_copy, to_delete, to_update, to_merge, conflicts = compare_files(diff)

    # Print the merges
    if to_copy or to_update or to_delete:
        log("The following files can be updated directly:")
        logs = []
        for old, _ in to_update:
            logs.append(f"(M) {old.relative_to(BASE_DIR)}")
        for _, new in to_copy:
            logs.append(f"(A) {new.relative_to(BASE_DIR)}")
        for file in to_delete:
            logs.append(f"(D) {file.relative_to(BASE_DIR)}")
        logs.sort(key=lambda s: str.lower(s[4:]))  # Sort by filename
        for log_msg in logs:
            success(log_msg)

    if to_merge:
        log("The following files can be merged:")
        for old, _ in to_merge:
            warning(str(old.relative_to(BASE_DIR)))

    if conflicts:
        log("The following files have conflicts:")
        for conflict, _, count in conflicts:
            count_str = str(count)
            if count == FILE_ADDED_CODE:
                count_str = "A"
            if count == FILE_DELETED_CODE:
                count_str = "D"
            if count == FILE_MODIFIED_CODE:
                count_str = "M"
            error(f"({count_str}) {conflict.relative_to(BASE_DIR)}")

    if not commit:
        log("Do you want to commit these changes?")
        warning(
            "WARNING: doing so will change the files in your project, which may include merge conflicts. Please make sure you have proper backups / version control.",
            bold=True,
        )

        if not click.confirm("Proceed?"):
            return

    def copy_path(src: Path, dst: Path) -> None:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)

    # Apply the merges
    for src, dst in to_copy:
        copy_path(src, dst)

    for file in to_delete:
        file.unlink()

    for old_file, new_file in to_update:
        copy_path(new_file, old_file)

    for old_file, new_lines in to_merge:
        with open(old_file, "w") as out:
            out.writelines([f"{line}\n" for line in new_lines])

    for old_file, new_lines, count in conflicts:
        if count in (FILE_ADDED_CODE, FILE_MODIFIED_CODE):
            # (-1) File was changed but didn't exist locally - copy the new file entirely
            # (-3) File was added but ours already existed - replace it
            matching_file = target_version_dir / old_file.relative_to(BASE_DIR)
            old_file.parent.mkdir(parents=True, exist_ok=True)
            copy_path(matching_file, old_file.parent)
        elif count == FILE_DELETED_CODE:
            # File was deleted but ours had changes - leave it
            continue
        else:
            with open(old_file, "w") as out:
                out.writelines([f"{new_line}\n" for new_line in new_lines])

    success("Update complete!", bold=True)
    if conflicts:
        log("Please fix the conflicts on the following files:")
        for conflict, _, count in conflicts:
            if count == FILE_DELETED_CODE:
                continue
            count_str = str(count)
            if count == FILE_DELETED_CODE:
                count_str = "D"
            if count == FILE_MODIFIED_CODE:
                count_str = "M"
            error(f"({count_str}) {conflict.relative_to(BASE_DIR)}")
    log("Make sure to run the test battery to potentially fix linting issues and ensure everything went smoothly.")


if __name__ == "__main__":
    cli()
