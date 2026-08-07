import os
from pathlib import Path
from gix.exceptions import NoParentRepoFound


def fetch_deepest_gix_repo(active_dir: Path):
    """
    Walks through all parent directories and finds the bottom-most active gix parent repo to be used in the current cwd context.
    """
    active_dir = active_dir.resolve()
    for directory in (active_dir, *active_dir.parents):
        config = directory / "gix.toml"
        if config.exists():
            return config
    raise NoParentRepoFound(active_dir)
