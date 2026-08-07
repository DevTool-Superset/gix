class GixException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class AlreadyInitializedException(GixException):
    def __init__(self, cwd):
        super().__init__(f"Already initialized gix list at {cwd} parent directory.")


class GitNotInstalledException(GixException):
    def __init__(self):
        super().__init__(
            "Git is not installed or is not available in the system environment"
        )


class CorruptedGixList(GixException):
    def __init__(self):
        super().__init__(
            "The parent's dir gix.toml is corrupted or got deleted. Recreate using gix init at parent directory."
        )


class AliasAlreadyExists(GixException):
    def __init__(self, alias):
        super().__init__(f"The alias {alias} already exists.")


class AliasNotFoundError(GixException):
    def __init__(self, alias):
        super().__init__(f"The alias {alias} wasn't found inside this gix list.")


class NoParentRepoFound(GixException):
    def __init__(self, sub_dir):
        super().__init__(
            f"No gix.toml was found in any parent directory of {sub_dir}. Use gix init to create one in a parent directory."
        )


class NoGitRepoFoundException(GixException):
    def __init__(self, directory):
        super().__init__(
            f"No git directory found at {directory} so it cant be used as an gix alias."
        )
