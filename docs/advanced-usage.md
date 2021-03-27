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

Example, fabsetup generated output without uncolored, command output with ANSI color codes:

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

## Configuration

Sane defaults

### Defaults

```python
{
    "outfile": {
        "dir": "",
        "basename_formatter": "fabsetup_{now}.md",
        "now_format": "%F_%H-%M-%S",
        "name": "",
        "keep_color": False,
        "pandoc": {
            "command": "pandoc",
            "html": {
                "dir": "",
                "name": "",
                "css": {
                    "disabled": False,
                    "inline": True,
                    "url": "",
                    "auto_remove_markdown_file": True,
                },
            },
            "toc": False,
        },
        "prepend_executed_fabsetup_command": True,
        "fabsetup_command_prefix": "*Executed fabsetup command:*\n\n",
    },
    "output": {
        "color": {
            "cmd_local": "green",
            "cmd_remote": "yellow",
            "docstring": "blue",
            "error": "red",
            "full_name": "no_color",
            "subtask_header": "cyan",
            "task_header": "magenta",
            # "question": "default_color",
        },
        "color_off": False,
        "hide_command_line": False,
        "hide_code_block": False,
        "hide_docstring": False,
        "hide_header": False,
        "hide_print": False,
        "numbered": True,
        "numbered_state": [0],
    },
    "run": {
        "interactive": False,
    },
    "load_invoke_tasks_file": False,
    "load_fabric_fabfile": False,
    # "search_root": None,
}
```

### Customize

Log every fabsetup call as a HTML file with inline CSS.

`~/.fabsetup.yaml` example:

```yaml
outfile:
  dir: ~/.fabsetup-runs
  pandoc:
    html:
      dir: ~/.fabsetup-runs/html
    toc: true
```

* Configuration order
* `--show-config`

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
