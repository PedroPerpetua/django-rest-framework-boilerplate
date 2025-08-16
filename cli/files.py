from pathlib import Path


PROJECT_DIR = Path(__file__).parent.parent

APP_DIR = PROJECT_DIR / "app"

PYPROJECT_FILE = APP_DIR / "pyproject.toml"

DOCKER_DIR = PROJECT_DIR / "docker"

CACHE_DIR = Path(__file__).parent / ".cache"


def get_cache() -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    with open(CACHE_DIR / ".gitignore", "w+") as gitignore_file:
        gitignore_file.write("*")
    return CACHE_DIR
