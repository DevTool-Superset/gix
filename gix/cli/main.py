import importlib.metadata
import os
import subprocess
from pathlib import Path

import click
import typer
from gix.cli.commands.alias_management import alias_subcommand
from gix.cli.util import build_engine_from_parent_gix_repo, console
from gix.exceptions import GixException, AliasNotFoundError
from gix.manager.init import init_gix_list
from typer.core import TyperGroup


class AliasCommand(click.Command):
    def __init__(self):
        super().__init__(
            name="<alias>",
            callback=self.run_alias,
        )

    def run_alias(self, **kwargs):
        ctx = click.get_current_context()
        alias = ctx.obj["alias"]
        git_args = ctx.obj["git_args"]

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
            raise typer.Exit()


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


app = typer.Typer(
    help="Manage multiple git subrepositories from a single parent repository",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    add_completion=False,
    cls=GixGroup,
    context_settings={"obj": {}},
)
app.add_typer(alias_subcommand, name="alias")


def version_callback(value: bool):
    if value:
        typer.echo(f"Current gix version is {importlib.metadata.version('gix')}")
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
        alias = ctx.obj["alias"]
        git_args = ctx.obj["git_args"]
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
            raise typer.Exit()


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
        raise typer.Exit()
    else:
        console.print(f"Initialized gix list in {cwd}", style="green")
