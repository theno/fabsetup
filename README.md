# Welcome to Fabsetup!

**Set up and maintain configurations, software installations and other
things on a local or remote linux system.**

Source: <https://github.com/theno/fabsetup>

Documentation: <https://fabsetup.readthedocs.io>

Features:

* Fabsetup's **tasks** do the things:

  * tasks execute commands commented and comprehensible
  * tasks produce output formatted in Markdown or HTML
  * run a task local or on a remote host

* **Addons**:

  * only install the tasks you need
  * create Your own addon with Your task

* The Command **`fabsetup`**, based on [Fabric](https://www.fabfile.org/),
  is a pimped [`fab` command](
  https://docs.fabfile.org/en/latest/getting-started.html#addendum-the-fab-command-line-tool)
  with the same [options and
  arguments](https://docs.fabfile.org/en/latest/cli.html). And some more:

  * Control markdown formatted output:

    * `--hide-code-block`
    * `--hide-command-line`
    * `--hide-command-output`
    * `--hide-docstring`
    * `--hide-header`
    * `--hide-print`
    * `--unnumbered`
    * `--pandoc-add-toc`

  * Write output to file:

    * `--outfile`
    * `--pandoc-html-file`

  * Control ANSI color codes:

    * `--color-off`
    * `--color-keep`

  * Control execution of commands:

    * `--interactive`

  * Load fabfiles and invoke tasks:

    * `--load-fab`
    * `--load-inv`

  * Show effective config:

    * `--show-config`

  * List known Fabsetup addons:

    * `--known-addons`

* **API**:

  * for Your own Fabsetup addon
  * use Fabsetup in Your own [Fabric tasks](
    https://docs.fabfile.org/en/2.5/api/tasks.html#fabric.tasks.task)
    and [Invoke tasks](
    http://docs.pyinvoke.org/en/latest/getting-started.html#defining-and-running-task-functions)

## Installation

Install fabsetup the same way like
[fabric](https://www.fabfile.org/installing.html), best via
[pip](https://pip.pypa.io/):

```sh
pip install fabsetup
```

## Usage

Run task `info`:

```sh
fabsetup info
```

Important options:

```sh
# Show versions
fabsetup --version

# Help
fabsetup -h

# List tasks
fabsetup -l

# Show task help
fabsetup info --help
fabsetup new --help
```

## Tab Completion

Invokes [shell tab completion](
https://docs.pyinvoke.org/en/stable/invoke.html#tab-completion) also works
with fabsetup:

```sh
fabsetup -h | grep -A1 "completion"
```

Apply this simple setup of tab completion in bash:

```sh
echo 'source <(fabsetup --print-completion-script bash)' >> ~/.bashrc
source ~/.bashrc
```

Now You are able to "tab" through the available fabsetup tasks and options:

```sh
fabsetup --h<TAB><TAB>  ->  --help  --hide  --hosts
fabsetup --he<TAB>      ->  fabsetup --help
fabsetup --help i<TAB>  ->  fabsetup --help info
```

More features:
[Advanced Usage](https://fabsetup.readthedocs.io/en/latest/advanced-usage.html)

## Addons

Fabsetup itself only comes with two tasks, `info` and `new`.  The tasks
that "really do things" reside in separate fabsetup addons.

They will be installed the same way like fabsetup and fabric, best via pip.
For example:

```sh
pip install fabsetup-theno-termdown
```

Now You are able to run the task `theno.termdown`.  This task sets up
[termdown](https://github.com/trehn/termdown), locally or on a remote
host:

```sh
# local
fabsetup theno.termdown

# remote
fabsetup -H user@host theno.termdown
```

More infos:
[Fabsetup Addons](https://fabsetup.readthedocs.io/en/latest/addons.html)

## Your Addon

Create Your own fabsetup addon doing great things! Start now:

```sh
fabsetup new
```

More infos:
[Create a Fabsetup Addon](https://fabsetup.readthedocs.io/en/latest/create-addon.html)
