import os
from pathlib import Path
from typing import Dict


def fetch_existing_git_repos(parent_dir: Path) -> Dict[str, Path]:
    """
    Fetches existing git repos in subdirectories of parent dir and returns {name:Path **without** .git folder}.
    """
    repos = {}

    for path, dirs, _ in os.walk(parent_dir):
        if ".git" in dirs:
            name = Path(path).name
            original_name = name
            uid = 1
            while name in repos.keys():
                name = f"{original_name}{uid}"
                uid += 1
            repos[name] = Path(path)

        dirs[:] = [d for d in dirs if d != ".git"]
    return repos
