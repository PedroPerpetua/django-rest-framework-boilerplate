import filecmp
import requests
import shutil
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Optional, TypedDict
import click
from cli.diff3 import merge
from cli.files import PROJECT_DIR, get_cache
from cli.logging import success, warning


TAGS_URL = "https://api.github.com/repos/PedroPerpetua/django-rest-framework-boilerplate/tags"


class CommitData(TypedDict):
    sha: str
    url: str


class TagData(TypedDict):
    name: str
    node_id: str
    zipball_url: str
    tarball_url: str
    commit: CommitData


def get_tags() -> list[TagData]:
    tags_res = requests.get(TAGS_URL)
    tags_res.raise_for_status()
    return tags_res.json()


def get_tag(tag: TagData, use_cache: bool = True) -> Path:
    version = tag["name"]
    if use_cache:
        download_dir = get_cache() / version
    else:
        temp_dir = TemporaryDirectory(ignore_cleanup_errors=True)
        download_dir = Path(temp_dir.name) / version

    # Check for existing version
    if download_dir.exists():
        warning(f"Version {version} found in cache.", bold=False)
        return download_dir

    # Check for existing zip
    zip_path = download_dir.parent / f"{version}.zip"
    if zip_path.exists():
        warning(f"Zip file for {version} found in cache.", bold=False)
    else:
        res = requests.get(tag["zipball_url"], stream=True)
        with open(zip_path, "+wb") as out_file:
            shutil.copyfileobj(res.raw, out_file)
        success(f"Version {version} successfully downloaded.", bold=False)

    # Extract the file
    download_dir.mkdir()
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        files = zip_file.infolist()
        for file_path in files[1:]:
            if file_path.is_dir():
                continue
            file_path.filename = "/".join(file_path.filename.split("/")[1:])
            zip_file.extract(file_path, download_dir)

    return download_dir


def merge_files(ancestor: Path, source: Path, dest: Path) -> tuple[list[str], int]:
    with open(ancestor, "r") as curr:
        current_file_lines = [line.rstrip() for line in curr.readlines()]
    with open(source, "r") as c:
        target_version_lines = [line.rstrip() for line in c.readlines()]
    with open(dest, "r") as w:
        working_lines = [line.rstrip() for line in w.readlines()]
    merge_result = merge(working_lines, current_file_lines, target_version_lines)
    return merge_result["body"], merge_result["conflict"]


def are_files_equal(f1: Path, f2: Path) -> bool:
    """filecmp has trouble comparing file endings, so we implement our own compare."""
    if filecmp.cmp(f1, f2):
        return True
    with open(f1, "r") as f1_file:
        f1_lines = f1_file.readlines()
    with open(f2, "r") as f2_file:
        f2_lines = f2_file.readlines()
    if len(f1_lines) != len(f2_lines):
        return False
    return all(f1_l == f2_l for f1_l, f2_l in zip(f1_lines, f2_lines, strict=False))


class FileUpdate(ABC):
    """This abstract class represents the operation that should be done for a certain file in order to update it."""

    code: str = "?"
    click_color: Optional[str] = None

    def __init__(self, base_file: Path, updated_file: Path, current_file: Path):
        self.base_file = base_file
        self.updated_file = updated_file
        self.current_file = current_file

    @abstractmethod
    def perform(self) -> None:
        raise NotImplementedError()

    @property
    def relative_path(self) -> str:
        return self.current_file.relative_to(PROJECT_DIR).as_posix()

    @property
    def message(self) -> str:
        return click.style(f"[{self.code}] {self.relative_path}", fg=self.click_color)


class CopyFile(FileUpdate):
    """This represents a file that will be copied over from the update."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Set the code properly
        if not self.current_file.exists():
            self.code = "NEW"
            self.click_color = "green"
        else:
            self.code = "MOD"
            self.click_color = "cyan"

    def perform(self):
        shutil.copy(self.updated_file, self.current_file)


class DeleteFile(FileUpdate):
    """This represents a file that will be deleted from the local project."""

    code = "DEL"
    click_color = "green"

    def perform(self) -> None:
        self.current_file.unlink()


class MergeFile(FileUpdate):
    """This represents a file where the current version will be merged with the update version."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Perform the merge
        self.merged_lines, self.issues = merge_files(self.base_file, self.updated_file, self.current_file)
        # Set the code properly
        if self.issues != 0:
            self.code = "CFL"
            self.click_color = "yellow"
        else:
            self.code = "MGD"
            self.click_color = "magenta"

    def perform(self):
        with open(self.current_file, "w+") as current_file:
            current_file.writelines([f"{line}\n" for line in self.merged_lines])


class ErrorFile(FileUpdate):
    """This represents a conflict that can't be resolved."""

    code = "ERR"
    click_color = "red"

    def perform(self) -> None:
        # Since we can't do anything...
        pass


def compare_version(base_version: Path, updated_version: Path, current_version: Path) -> list[FileUpdate]:
    updates: list[FileUpdate] = []
    diff = filecmp.dircmp(base_version, updated_version, ignore=[])

    def aux(comparison: filecmp.dircmp) -> None:
        deleted_file: str
        for deleted_file in comparison.left_only:
            # File was deleted in the updated_version
            base_file = Path(comparison.left) / deleted_file
            updated_file = updated_version / base_file.relative_to(base_version)
            current_file = current_version / base_file.relative_to(base_version)

            if not current_file.exists():
                # We didn't have the file that was deleted to begin with; we're good
                continue
            if are_files_equal(base_file, current_file):
                # Our current version is the same as the base version; delete it
                updates.append(DeleteFile(base_file, updated_file, current_file))
                continue
            # Otherwise, we've changed a file that was deleted - this is a conflict
            updates.append(ErrorFile(base_file, updated_file, current_file))

        added_file: str
        for added_file in comparison.right_only:
            # File was added in the new version
            updated_file = Path(comparison.right) / added_file
            base_file = updated_version / updated_file.relative_to(updated_version)
            current_file = current_version / updated_file.relative_to(updated_version)

            if not current_file.exists():
                # We don't have the new file; copy it over
                updates.append(CopyFile(base_file, updated_file, current_file))
                continue
            if are_files_equal(updated_file, current_file):
                # Our current version is the same as the updated version; we're good
                continue
            # Otherwise, we've created a file that was added later - merge them
            updates.append(MergeFile(base_file, updated_file, current_file))

        changed_file: str
        for changed_file in comparison.diff_files:
            base_file = Path(comparison.left) / changed_file
            updated_file = Path(comparison.right) / changed_file
            current_file = current_version / base_file.relative_to(base_version)

            if are_files_equal(base_file, updated_file):
                continue

            if not current_file.exists():
                # Our current version was deleted; it's a conflict
                updates.append(ErrorFile(base_file, updated_file, current_file))
                continue
            if are_files_equal(current_file, base_file):
                # Our current version is the same as the base; copy over
                updates.append(CopyFile(base_file, updated_file, current_file))
                continue
            # Otherwise, the file was modified on both current and updated; merge them
            updates.append(MergeFile(base_file, updated_file, current_file))

        # Apply recursively
        for sub_comparison in comparison.subdirs.values():
            aux(sub_comparison)

    # Run it on the root
    aux(diff)
    return updates
