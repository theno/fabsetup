# How to create and write a fabsetup-addon

## Prerequisites

* git is
  [configured](https://help.github.com/articles/setting-your-username-in-git/)
  (email, name of author/user)
* [github](https://github.com) account exists
* [pypi](https://pypi.python.org) account exists
  * best if pypi username is the same as your github username

## Create fabsetup-addon

Scaffold fabsetup-addon boilerplate; follow instructions:

```sh
fabsetup new_addon
```

This is a working fabsetup-addon which setups termdown.  Now, edit the
task to apply for your setup goals.

If you did not create a github remote repo, you can do it later:
https://help.github.com/articles/adding-an-existing-project-to-github-using-the-command-line

## fabsetup-addon development

Assumptions here:
* github username: theno
* addon name: termdown
  * full addon name: fabsetup-theno-termdown
* task name: termdown
  * full task name: theno.termdown

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
