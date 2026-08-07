import os
import subprocess
from pathlib import Path
from gix.exceptions import GitNotInstalledException, AlreadyInitializedException
from gix.manager.CRUD import RepoCRUDEngine
from gix.manager.fetch_existing_repos import fetch_existing_git_repos


def create_config(path, overwrite=False):
    path = str(path)
    if not path.endswith("gix.toml"):
        path = f"{path}/gix.toml"

    exists = os.path.exists(path)
    if not overwrite and exists:
        raise AlreadyInitializedException(path.removesuffix("gix.toml"))
    if overwrite and exists:
        os.remove(path)
    with open(path, "a"):
        os.utime(path, None)


def init_gix_list(
    cwd: Path, overwrite: bool = False, fetch_existing_child_repos: bool = False
):  #
    gix_file = f"{cwd}/gix.toml"
    try:
        subprocess.run(
            ["git", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        raise GitNotInstalledException()
    if os.path.exists(gix_file) and not overwrite:
        raise AlreadyInitializedException(cwd)
    create_config(gix_file, overwrite)
    config = RepoCRUDEngine(gix_file)
    if not fetch_existing_child_repos:
        return {}
    existing_repos = fetch_existing_git_repos(cwd)
    for name in existing_repos:
        config.append(name, existing_repos[name])
    return dict(config.read()["repos"])
