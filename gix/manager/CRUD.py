import os
from functools import wraps
from pathlib import Path

import tomlkit

from gix.exceptions import *


def validate_toml_path(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not os.path.exists(self.toml_path):
            raise CorruptedGixList()

        if not os.access(self.toml_path, os.R_OK | os.W_OK):
            raise CorruptedGixList()

        return func(self, *args, **kwargs)

    return wrapper


class RepoCRUDEngine:
    def __init__(self, toml_path: str):
        self.toml_path = toml_path

    @validate_toml_path
    def read(self):
        try:
            with open(self.toml_path, "r", encoding="utf-8") as f:
                doc = tomlkit.parse(f.read())
            if "repos" not in doc:
                doc["repos"] = tomlkit.table()
            return doc
        except Exception:
            raise CorruptedGixList()

    @validate_toml_path
    def append(self, alias: str, working_dir: Path):
        if working_dir.name == ".git":
            working_dir = working_dir.parent
        doc = self.read()
        repos = doc["repos"]

        if alias in repos:
            raise AliasAlreadyExists(alias)
        if not os.path.exists(f"{working_dir}/.git"):
            raise NoGitRepoFoundException(working_dir)
        repos[alias] = str(working_dir)
        self._write(doc)

    @validate_toml_path
    def delete(self, alias: str = None, working_dir: Path = None):
        if alias is None and working_dir is None:
            raise RuntimeError("Alias or working_dir must be provided")

        doc = self.read()
        repos = doc["repos"]

        if alias is not None:
            if alias in repos:
                del repos[alias]
        else:
            for key, value in list(repos.items()):
                if value == str(working_dir):
                    del repos[key]

        self._write(doc)

    @validate_toml_path
    def rename_alias(self, old: str, new: str):
        doc = self.read()
        repos = doc["repos"]

        if new in repos:
            raise AliasAlreadyExists(new)

        if old not in repos:
            raise AliasNotFoundError(old)

        repos[new] = repos[old]
        del repos[old]
        self._write(doc)

    @validate_toml_path
    def update_working_dir(self, alias: str, new_working_dir: Path):
        doc = self.read()
        repos = doc["repos"]

        if alias not in repos:
            raise AliasNotFoundError(alias)

        repos[alias] = str(new_working_dir)
        self._write(doc)

    def _write(self, data):
        try:
            with open(self.toml_path, "w", encoding="utf-8") as f:
                f.write(tomlkit.dumps(data))
        except Exception:
            raise CorruptedGixList()
