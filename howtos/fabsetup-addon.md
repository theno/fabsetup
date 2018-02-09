# How to create and write a fabsetup-addon

## Prerequisites

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

## Boilerplate / fabsetup-addon structure

Example: https://github.com/theno/fabsetup-theno-termdown

* github username: `theno`
  * addon name: `termdown`  
    └─> full addon name / package name: `fabsetup-theno-termdown`  
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
```

## fabsetup-addon development

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

Edit your task in [`fabsetup_theno_termdown/__init__.py`](https://github.com/theno/fabsetup-theno-termdown/blob/master/fabsetup_theno_termdown/__init__.py). Take a look in the code, it uses this useful functions and decorators:

* [install_file()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L507)
* [install_user_command()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L568)
* execute a shell command: [run()](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L65)
* decorators
  * [@task](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L171)
  * [@subtask](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L193)
  * [@suggest_localhost](https://github.com/theno/fabsetup/blob/ddae2cf810b3db2413cb06abd3ac4dd738d92e07/fabsetup/fabutils.py#L29)

## Execute your task

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
fab theno.termdow
```

## Task Rules

* A task must list in its docstring all changed or created files.

* A task must be able to be executed repeatedly
  * First execution does the initial setup
  * Next exectutions update the setup
    * When there is nothing to update, it must not change anything

* Later:
  The unit tests which test the setup taken by the task must pass.

* Only when this rules are met by all task of a fabsetup-addon, the
  fabsetup-addon will be taken into the list of `known_pip_addons`
  defined in fabsetup/addons.py.
  
If your fabsetup-addon is in the `known_pip_addons` list, you only need to
install the addon via pip to be able to execute the task:

```sh
pip install fabsetup-addon-theno
fabsetup theno.termdown
```
