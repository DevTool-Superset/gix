# gix

Manage multiple git sub-repos without constantly `cd`-ing into their folder first.
## Installation

Requires Python 3.12+.

```bash
pip install --upgrade gix-cli
gix --install-completion
```

Check your installed version:

```bash
gix --version
```

## Getting started

Run this once in the parent directory that holds your sub-repos:

```bash
gix init
```

This creates a `gix.toml` file in the current folder, which is where all
your registered aliases will be stored.

If you already have git repos sitting in subfolders and want to register
them all at once:

```bash
gix init --fetch
```

To wipe an existing `gix.toml` and start over:

```bash
gix init --overwrite
```

## Managing aliases

Add the repo in your current working directory as an alias:

```bash
cd path/to/some-repo
gix alias add backend
```

List all registered aliases:

```bash
gix alias list
```

Rename an alias:

```bash
gix alias rename backend api
```

Remove an alias (this only removes it from `gix.toml`, the repo itself
is untouched):

```bash
gix alias delete api
```

## Running git commands

Once a repo is registered under an alias, run any git command against it
from anywhere inside the parent tree:

```bash
gix backend status
gix backend pull
gix backend log -5
```

`gix` looks up the alias, finds the matching repo path, and runs `git <your arguments>` there 

## How it works

```python
result = subprocess.run(["git", *git_args], cwd=engine.read()["repos"].get(alias))
```

## Notes

- `gix` doesn't do anything to your actual git repos. Tt only manages the
  alias-to-path mapping.
- If `gix.toml` gets deleted or corrupted, just run `gix init` again.