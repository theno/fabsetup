# Advanced Usage

## Interactive Runs

```sh
fabsetup --interactive user.task
```

## Output

* control output `--hide-*`
* numbering
* ANSI color codes

## Outfile

```sh
fabsetup --outfile output.md
```

Logging of fabsetup calls: Automatically create a file on each fabsetup
execution: `outfile.dir=~/.fabsetup-runs`

Example, fabsetup generated output without uncolored, command output
with ANSI color codes:

```sh
@task
def task_with_colorful_commands(c):
    """Bla bla"""
    c.run("echo colors")

fabsetup --color-off --color-keep --outfile output.md \
  user.task-with-colorful-commands
```

## Pandoc

### Add Table of Content

```sh
fabsetup --outfile output.md --toc  user.task
```

### HTML File

```sh
fabsetup --pandoc-html-file output.html  user.task
```

## Invoke Task Files and Fabfiles

Fabsetup is also able to load and to invoke invoke task files and
fabfiles.

`--load-inv` and `--load-fab`

```sh
inv -l
inv itask
```

```sh
fabsetup --load-inv -l
fabsetup --config invoke.yaml --load-inv inv.itask
```

```sh
fab -l
fab -H user@host ftask
```

```sh
fabsetup --load-fab -l
fabsetup -H user@host --config fabric.yaml --load-fab inv.ftask
```

```sh
fabsetup --load-inv --load-fab -l
fabsetup -H user@host --config invoke.yaml --load-inv --load-fab inv.itask fab.ftask
```
