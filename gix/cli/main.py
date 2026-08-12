import importlib.metadata
import os
import subprocess
from pathlib import Path

import click
import typer
from gix.cli.commands.alias_management import alias_subcommand
from gix.cli.util import build_engine_from_parent_gix_repo, console
from gix.exceptions import GixException, AliasNotFoundError
from gix.manager.git_autocompletion import get_git_completion
from gix.manager.init import init_gix_list
from typer.core import TyperGroup


def run_git_for_alias(alias: str, git_args: list[str]) -> None:
    """Resolve an alias to its repo path and run `git <git_args>` there.

    Exits with the underlying git process's return code on success, or
    with a nonzero code and an error message if the alias/config can't
    be resolved.
    """
    try:
        gix_path, engine = build_engine_from_parent_gix_repo(Path.cwd())
        resolved = engine.read()["repos"].get(alias)

        if not resolved:
            raise AliasNotFoundError(alias)

        result = subprocess.run(
            ["git", *git_args],
            cwd=resolved,
        )

        raise typer.Exit(code=result.returncode)

    except GixException as e:
        console.print(e.message, style="bold red")
        raise typer.Exit(code=1)


class AliasCommand(click.Command):
    def __init__(self):
        super().__init__(
            name="<alias>",
            callback=self.run_alias,
        )

    def run_alias(self, **kwargs):
        ctx = click.get_current_context()
        run_git_for_alias(ctx.obj["alias"], ctx.obj["git_args"])

    def shell_complete(self, ctx, incomplete):
        """
        Completes the git subcommand/args for an already-resolved alias,
        e.g. `gix repo1 chec<TAB>` -> `checkout`.

        Click hands completion off to the *leaf* command once an alias has
        been resolved, so this needs to live here rather than on the
        parent group's shell_complete (which is only consulted while
        completing subcommand/alias names themselves).
        """
        try:
            gix_path, engine = build_engine_from_parent_gix_repo(Path.cwd())
        except GixException:
            return []

        alias = ctx.obj.get("alias") if ctx.obj else None
        repos = engine.read().get("repos", {})
        resolved = repos.get(alias) if alias else None

        if not resolved:
            return []

        git_args = (ctx.obj.get("git_args") or []) + [incomplete]
        git_command = "git " + " ".join(git_args)

        completion = get_git_completion(
            cwd=Path(resolved),
            git_command=git_command,
        )

        if completion:
            return [click.shell_completion.CompletionItem(completion)]

        return []


class GixGroup(TyperGroup):
    def resolve_command(self, ctx, args):
        if args:
            first = args[0]

            if first not in self.commands and not first.startswith("-"):
                ctx.ensure_object(dict)
                ctx.obj["alias"] = first
                ctx.obj["git_args"] = args[1:]

                return first, AliasCommand(), []

        return super().resolve_command(ctx, args)

    def shell_complete(self, ctx, incomplete):
        """
        Completes alias names at the group level
        """
        completions = super().shell_complete(ctx, incomplete)

        if not ctx.obj:
            try:
                gix_path, engine = build_engine_from_parent_gix_repo(Path.cwd())
            except GixException:
                return completions

            aliases = engine.fetch_aliases()
            completions.extend(
                click.shell_completion.CompletionItem(alias)
                for alias in aliases
                if alias.startswith(incomplete)
            )

        return completions


app = typer.Typer(
    help="Manage multiple git subrepositories from a single parent repository",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    add_completion=True,
    cls=GixGroup,
    context_settings={"obj": {}},
)
app.add_typer(alias_subcommand, name="alias")


def version_callback(value: bool):
    if value:
        try:
            version = importlib.metadata.version("gix-cli")
        except importlib.metadata.PackageNotFoundError:
            version = "unknown (not installed as a package)"
        typer.echo(f"Current gix version is {version}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
    ),
):
    if ctx.obj.get("alias"):
        run_git_for_alias(ctx.obj["alias"], ctx.obj["git_args"])


@app.command()
def init(
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing gix.toml if already exists."
    ),
    fetch: bool = typer.Option(
        False,
        "--fetch",
        help="Fetch and register all existing git repositories in subdirectories.",
    ),
):
    """
    Initializes a gix list in the current environment
    """
    cwd = os.getcwd()
    try:
        created_repos = init_gix_list(cwd, overwrite, fetch)
        for name in created_repos:
            console.print(
                f"Registered [bold]gix {name}[/bold] alias for {created_repos[name]}"
            )
    except GixException as e:
        console.print(e.message, style="bold red")
        raise typer.Exit(code=1)
    else:
        console.print(f"Initialized gix list in {cwd}", style="green")
