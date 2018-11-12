# fabsetup

Fabric tasks in order to set up and maintain configurations, software
installations and other things on a local or remote linux system
(most functionality for Debian/Ubuntu).

> _"dotfiles on steroids"_

## Usage

__fabsetup__ is a __[fabric](http://www.fabfile.org/ "www.fabfile.org")__
script.

```sh
# task infos

## list all tasks: '-l'
fabsetup -l

## show details: '-d'
fabsetup -d new_addon


# run tasks

fabsetup setup.regex_repl

## on your local host:
fabsetup setup.pencil3 -H localhost

## remote host:
fabsetup up -H example.com
```

__[Setup-Howtos](./howtos "cookbook")__:

 * Customize fabsetup: [Initialize git repository
   `fabsetup_custom`](./howtos/fabsetup-custom.md)
 * [Set up an environment without sudo access](./howtos/no-sudo.md)
 * [Webserver Certificates with Letsencrypt](./howtos/letsencrypt.md)
 * [Host an Owncloud Service](./howtos/owncloud.md)
 * [Host an own F-Droid Repository](./howtos/f-droid-repo.md) (Android App Repository)
 * [Host a Selfoss Service](./howtos/selfoss.md) (RSS Reader Web Application)
 * [Install latest Node.js via nvm](./howtos/nodejs.md)
 * [Create or update a reveal.js presentation](./howtos/revealjs.md)
 * __[How to create and write a fabsetup-addon](./howtos/fabsetup-addon.md)__

## Known fabsetup-addons

* [fabsetup-theno-letsencrypt](https://github.com/theno/fabsetup-theno-letsencrypt)
* [fabsetup-theno-powerline-shell](https://github.com/theno/fabsetup-theno-powerline-shell)
* [fabsetup-theno-termdown](https://github.com/theno/fabsetup-theno-termdown)

Please contribute:
[Create your own fabsetup-addon](./howtos/fabsetup-addon.md) and make a
[pull request](https://github.com/theno/fabsetup/pulls) which adds your
 fabsetup-addon to the `known_pip_addons` in `fabsetup/addons.py` and to this
`README.md`.

## Installation

As a [pypi package](https://pypi.python.org/pypi/fabsetup)
with command `pip2` (recommended way):

```sh
pip2 install fabsetup

# install addon, eg. fabsetup-theno-termdown
pip2 install fabsetup-theno-termdown
```

### Raspberry Pi

On a fresh raspbian (Debian) you will need at least the following packages before installing fabsetup with `pip`:

```sh
sudo apt install -y git python python-pip libffi-dev libssl-dev tree curl && sudo pip install fabsetup
```
The whole installation will take about 15 minutes on a Raspi 3 with raspbian stretch, so you can make yourself a tea.
Note: You do not need to type `pip2` as `pip` defaults to the python2-variant of `pip`. If you run `$ pip install fabsetup` as normal usr (without `sudo`) `pip` will install with `--user` setting by default so fabsetup is located under `~/.local/bin`. In this case you need to add `~/.local/bin` to `$PATH` which is located in `/etc/profile`.
 
Update:

```sh
pip2 install --upgrade fabsetup

# update addon (also updates fabsetup)
pip2 install --upgrade fabsetup-theno-termdown
```

Install without superuser privileges:

```sh
pip2 install --user fabsetup
```

When running with `--user` pip installs the command `fabsetup` at
`~/.local/bin`.  [Assure](https://stackoverflow.com/a/14638025) that
`~/.local/bin` is set in your `$PATH` environment variable.

Uninstall:

```sh
pip2 uninstall --yes fabsetup
pip2 uninstall --yes fabsetup-addon-theno
```

You also can clone the [github repository](https://github.com/theno/fabsetup)
instead of using `pip2 install`:

```sh
# install requirements
sudo apt-get install  git  fabric
pip2 install --user utlz

git clone  https://github.com/theno/fabsetup.git  ~/.fabsetup

# from ~/.fabsetup dir use `fab` instead of `fabsetup`
cd ~/.fabsetup
fab -l
```

## Development

Devel commands:

```bash
# save changes
git commit -am 'I describe my changes'

# upload to github
git push origin master

# update version number in fabsetup/_version.py

# create and publish package at pypi
fab -f fabfile-dev.py  pypi

# clean up
fab -f fabfile-dev.py  clean
```
