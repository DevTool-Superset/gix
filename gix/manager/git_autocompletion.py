import os
import re
import sys
import time
from pathlib import Path


def strip_ansi(text: str) -> str:
    """Removes ANSI escape sequences."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def intercept_git_auto_complete(
    cwd: Path,
    git_command: str,
) -> str:
    """
    Function gets triggered after gix <alias> has been fulfilled and returns git autocompletion.

    `git_command` is the full `git ...` command line typed so far (e.g.
    "git checko" or "git log -"), already reconstructed by the caller from
    the resolved alias's git args plus the in-progress word.
    """
    cwd = cwd.resolve()
    incomplete_command = git_command.strip()

    if sys.platform == "win32":
        from winpty import PtyProcess

        proc = PtyProcess.spawn(
            [
                "powershell.exe",
                "-NoProfile",
                "-NoExit",
                "-Command",
                "Remove-Module PSReadLine -ErrorAction SilentlyContinue",
            ]
        )

        def wait_for_prompt(timeout=3.0):
            output = ""
            start = time.time()

            while time.time() - start < timeout:
                chunk = proc.read()
                output += chunk

                if ">" in strip_ansi(output):
                    return output

                time.sleep(0.05)

            return output

        wait_for_prompt()

        proc.write("Import-Module posh-git -ErrorAction SilentlyContinue\r\n")
        wait_for_prompt()

        proc.write(f'cd "{cwd.absolute()}"\r\n')
        proc.write(f"{incomplete_command}\t")

        time.sleep(0.5)

        output = proc.read()

        cleaned = strip_ansi(output).replace("\r", "").replace("\n", "").strip()

        if "git " in cleaned:
            parts = cleaned.split(incomplete_command)
        else:
            return ""

    else:
        import pexpect

        env = os.environ.copy()
        env["TERM"] = "xterm-256color"

        child = pexpect.spawn(
            "/bin/bash",
            ["--noprofile", "--norc"],
            env=env,
            encoding="utf-8",
        )

        child.expect(r"\$ |# ")

        child.sendline(f"cd {cwd.absolute()}")
        child.sendline("source /usr/share/bash-completion/bash_completion")

        child.expect(r"\$ |# ")

        child.send(f"{incomplete_command}\t")

        output = ""

        while True:
            try:
                output += child.read_nonblocking(
                    size=1024,
                    timeout=0.05,
                )
            except pexpect.TIMEOUT:
                break

        cleaned = strip_ansi(output).replace("\r", "").replace("\n", "").strip()

        parts = cleaned.split(incomplete_command)

    result = " ".join(parts[1:]).strip()

    return f"{incomplete_command.split(' ')[-1]}{result}"


def get_git_completion(
    cwd: Path,
    git_command: str,
) -> str:
    """
    Runs Git completion synchronously and returns the result.
    """
    try:
        return intercept_git_auto_complete(
            cwd=cwd,
            git_command=git_command,
        )
    except Exception:
        return ""
