# How to create and write a fabsetup-addon

## Prerequisites

```sh
fabsetup -d new_addon
```

* git is
  [configured](https://help.github.com/articles/setting-your-username-in-git/)
  (email, name of author/user)
* [github](https://github.com) account exists
* [pypi](https://pypi.python.org) account exists
  * best if pypi username is the same as your github username

## Create fabsetup-addon

Scaffold fabsetup-addon boilerplate, run:

```sh
fabsetup new_addon
```

and follow the instructions.

You will get a working fabsetup-addon which setups termdown.  Now, edit the
task to apply for your own setup goals.

If you did not create a github remote repo, you can
[do it later](https://help.github.com/articles/adding-an-existing-project-to-github-using-the-command-line]).

## Boilerplate / fabsetup-addon Structure

Example: [fabsetup-theno-termdown](https://github.com/theno/fabsetup-theno-termdown)

* github username: `theno`
  * addon name: `termdown`  
    └─> full addon name / package name / repository name: `fabsetup-theno-termdown`  
    └─> module name: `fabsetup_theno_termdown`
  * task name: `termdown`  
    └─> full task name: `theno.termdown`

```sh
~/.fabsetup-addon-repos/fabsetup-theno-termdown     <--- package
                        ├── fabfile-dev.py
                        ├── fabfile.py
                        ├── fabsetup_theno_termdown  <--- module
                        │   ├── fabutils.py
                        │   ├── files
                        │   │   └── home
                        │   │       └── USERNAME
                        │   │           └── bin
                        │   │               └── termdown.template
                        │   ├── __init__.py  <--.
                        │   └── _version.py      `- task definition                                      `
                        ├── .git
                        │   ├── ...
                        │   ├── config
                        │   └── ...
                        ├── .gitignore
                        ├── README.md
                        ├── requirements.txt
                        └── setup.py
                        
~/.fabsetup-custom/fabsetup-theno-termdown
                   ├── config.py     <--- (non-public) configurations
                   └── files
                       └── home
                           └── USERNAME
                               └── bin
                                   └── termdown  <--- custom version (optional)

# when calling checkup_git_repo() in your code
~/.fabsetup-downloads/fabsetup-theno-termdown
                      ├── git-repository-1
                      │   └── ...
                      ├── git-repository-2
                      │   └── ...
                      └── ...
```

## fabsetup-addon Development

Devel commands:

```sh
cd /home/theno/.fabsetup-addon-repos/fabsetup-theno-termdown

# show task info
fab -f fabfile-dev.py -l

# Later: run tests
fab -f fabfile-dev.py test

# commit changes
git commit -am 'my commit message'

# publish at github
git push origin master

# publish pip package at pypi
fab -f fabfile-dev.py pypi
```

Edit your task in [`fabsetup_theno_termdown/__init__.py`](https://github.com/theno/fabsetup-theno-termdown/blob/master/fabsetup_theno_termdown/__init__.py). Take a look in the code, it uses some of this useful functions and decorators
defined in `fabsetup/fabutils.py`:

* [install_file()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L507)
* [install_user_command()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L568)
* wrappers of [fabric operations](http://docs.fabfile.org/en/latest/api/core/operations.html) to be able to call them with `-H localhost`:
  * [run()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L65) a shell command
  * check if a file [exists()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L70)
  * when you know `from` and `to` you also can install a file with [put()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L80)
* manipulate config files and scripts:
  * [update_or_append_line()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L590)
  * [comment_out_line()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L619)
  * [uncomment_or_update_or_append_line()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L629)
* install stuff (.deb packages only):
  * [install_package()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L298)
  * [install_packages()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L253)
* OS detection
  * [is_os()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L671)
  * [is_debian()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L698)
  * [is_ubuntu()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L702)
  * [is_raspbian()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L706)
  * [is_osmc()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L710)
* decorators
  * [@task](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L171)
  * [@subtask](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L193)
  * [@suggest_localhost](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L29)
  * [@needs_packages](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L152) is the decorator version of `install_packages()`

Study [Fabric's API](http://docs.fabfile.org), too.

## Execute Your Task

```sh
# with fabsetup installed as pip package as an fabsetup-addon
fabsetup -d theno.termdown
fabsetup theno.termdown

# with fabsetup from source as an fabsetup-addon
cd .fabsetup
fab -d theno.termdown
fab theno.termdown

# standalone
cd /home/theno/.fabsetup-addon-repos/fabsetup-theno-termdown
pip install -r requirements.txt
fab theno.termdown
```

## Good Tasks

A good task informs the user what it does and behaves as expected.
Therefore:

* A good task lists in its docstring all changed or created files.

* A good task can be executed again and again
  * First run does the initial setup
  * Next runs update the setup
    * When there is nothing to update, nothing changes

* Later: The unit tests pass which test the setup taken by the good task.

## Known fabsetup-addons

A fabsetup-addon with good tasks can be taken into the list of `known_pip_addons`
defined in
[fabsetup/addons.py](https://github.com/theno/fabsetup/blob/master/fabsetup/addons.py#L11).

If your fabsetup-addon is in the `known_pip_addons` list, you only need to
install the addon via pip to be able to execute the task.  For example:

```sh
pip install fabsetup-theno-termdown
fabsetup theno.termdown
```

Please contribute: Create your own fabsetup-addon and make a
[pull request](https://github.com/theno/fabsetup/pulls)
which adds your fabsetup-addon to the `known_pip_addons`
and to the `README.md`.
