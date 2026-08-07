from pathlib import Path
import typer
from gix.cli.util import build_engine_from_parent_gix_repo, console
from gix.exceptions import GixException
from rich.table import Table

alias_subcommand = typer.Typer()


@alias_subcommand.command()
def list():
    """
    List all registered gix repositories.
    """
    try:
        gix_path, engine = build_engine_from_parent_gix_repo(Path.cwd())
        repos = engine.read()["repos"]
    except GixException as e:
        console.print(e.message, style="bold red")
        raise typer.Exit(code=1)

    console.print(f"\n[bold cyan]Parent Repository[/bold cyan]")
    console.print(f"  {Path(gix_path).parent}\n")

    if not repos:
        console.print("[yellow]No repositories registered.[/yellow]")
        return

    table = Table(title="Registered gix Aliases")
    table.add_column("Alias", style="bold green", no_wrap=True)
    table.add_column("Git repository", style="cyan")

    for alias, path in sorted(repos.items()):
        table.add_row(alias, path)

    console.print(table)


@alias_subcommand.command()
def add(alias: str):
    """Add a git repository in the current working directory as a gix alias"""
    try:
        gix_path, engine = build_engine_from_parent_gix_repo(Path.cwd())
        engine.append(alias, Path.cwd())
    except GixException as e:
        console.print(e.message, style="bold red")
        raise typer.Exit(code=1)


@alias_subcommand.command()
def rename(old_alias_name, new_alias_name):
    """Rename a gix alias without changing the destination"""
    try:
        gix_path, engine = build_engine_from_parent_gix_repo(Path.cwd())
        engine.rename_alias(old_alias_name, new_alias_name)
    except GixException as e:
        console.print(e.message, style="bold red")
        raise typer.Exit(code=1)


@alias_subcommand.command()
def delete(alias: str):
    """Delete a gix alias without deleting the git repository"""
    try:
        gix_path, engine = build_engine_from_parent_gix_repo(Path.cwd())
        engine.delete(alias)
    except GixException as e:
        console.print(e.message, style="bold red")
        raise typer.Exit(code=1)


# Don't expose update command right now as it would be a bit confusing to use