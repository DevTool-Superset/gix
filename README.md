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

## A few words on autocompletion
gix exposes its own commands as well as aliases where appropriate via
```
gix --install-completion
```
Make sure your terminal is compatible with autocompletion that goes beyond file system references.

Where it get's more complicated is with exposing native git autocompletion through gix, to stay branch-aware for example.

The native [git-completion.bash](https://github.com/git/git/blob/master/contrib/completion/git-completion.bash) is over 4000 lines long and doesn't expose the completion for external use. \
After long debates the decision was made to emulate a native terminal running git in the working directory, simulating a [TAB] press and exposing the result through gix. \
This comes with performance and latency problems but at least in bashed based environments it's practical and feasible. \
The absolute pain of 1970s development decisions when it comes to terminals is thankfully handled by [pexpect](https://github.com/pexpect/pexpect) and the windows equivalent [winpty](https://github.com/rprichard/winpty).

1. Verify git autocompletion works on your machine:
   - Windows: PowerShell with posh-git installed.
   - Linux/macOS: Bash with bash-completion and Git completion enabled.
   - This step is unique to your system, we expect you to already have this setup.
2. Try it out
- ```gix backend checko<TAB>``` should be replaced to ```gix backend checkout```
- This process might be very slow on Windows because PowerShell starup time and dialogue can sometimes take over 1 second. 

> Currently looking for alternatives to this / caching while still staying aware to git branches