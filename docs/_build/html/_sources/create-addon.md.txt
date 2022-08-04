# Create a Fabsetup Addon

## In a Nutshell

* [Scaffold](#scaffold): Run `fabsetup new` which scaffolds a new Fabsetup
  addon
* [Code](#code): Implement Your task, use decorators `task`, `subtask`, and
  `subsubtask` of module `fabsetup.fabutils.task`
* [Documentation](#documentation): Set up documentation (sphinx powered page)
* [CI/CD](#ci-cd): Auto-test Your addon and set up shields
* [PyPI](#pypi): Publish Your addon repository on git{hub,lab,...}
  and upload Your addon to PyPI

## En Détail

### Scaffold

```sh
fabsetup new
```

### Code

Implement Your task, use decorators of module `fabsetup.fabutils.task`.

An academic example:

```python
from fabsetup.fabutils.task import task, subtask, subsubtask

@subsubtask
def my_subsubtask_a(c):
    '''subsubtask a'''
    c.run('echo subsubtask a')


@subsubtask
def my_subsubtask_b(c):
    '''subsubtask b'''
    c.run('echo subsubtask b')


@subtask
def my_subtask_1(c):
    '''subtask 1'''
    c.run('echo subtask 1')
    my_subsubtask_a(c)
    my_subsubtask_b(c)


@subsubtask
def my_subsubtask_c(c):
    '''subsubtask c'''
    c.run('echo subsubtask c')


@subsubtask
def my_subsubtask_d(c):
    '''subsubtask d'''
    c.run('echo subsubtask d')


@subtask
def my_subtask_2(c):
    '''subtask 2'''
    c.run('echo subtask 2')
    my_subsubtask_c(c)
    my_subsubtask_d(c)


@task
def my_task(c):
    '''Run my_subtask_1 and my_subtask_2'''
    c.run('echo task')
    my_subtask_1(c)
    my_subtask_2(c)
```

### Documentation

* set up documentation (github page)

### CI/CD

* TODO: auto-test Your addon and use shields

### PyPI

* upload to pypi

## More Details

### Files

Where to put files and templates, used by a fabsetup task.

### Git Repositories

How to manage a git repository used by a fabsetup task.

### Downloads

How to manage a downloaded file used by a fabsetup task.

## Styleguide

_"I whish You all the best four Your Fabsetup addon."_

### Cleanliness

There is [PEP 8](https://www.python.org/dev/peps/pep-0008/). And tools
like [flake8](https://flake8.pycqa.org/) and
[black](https://github.com/psf/black).  Please meet this baseline in
writing [clean code](https://www.informit.com/martinseries).

### Comprehensibility

A Fabsetup user should understand for every single command of a task why it
is executed.  Therefore, please write a docstring for every `task`,
`subtask`, and `subsubtask` and describe what the code is intended to
achieve.

### Traceability

A Fabsetup user should be able to achieve what a task does by manually
executing each command listed on task execution.  Therefore, please use
"all-inclusive" commands (e.g. `cd path/to/somewhere && ./run-something`
instead of [invoke.context.Context.cd](
https://docs.pyinvoke.org/en/stable/api/context.html#invoke.context.Context.cd)
which would not show the current dir where a command is executed from).
Also, consider to avoide the execution of hidden commands in Your task.

### Repetitions

By intuition, a Fabsetup user expects that repeated runs of a Fabsetup
task would not alter the achievements of the first run.  Please take
care to meet this assumption of idempotency for Your task.

### Markdown Output

You probably have noted that the output of the tasks `info` and `new` is
in [markdown](https://daringfireball.net/projects/markdown/).  Please
assure that Your fabsetup addon also creates markdown formatted output.
