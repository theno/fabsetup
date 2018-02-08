# fabsetup

Fabric tasks in order to set up and maintain configurations, software
installations and other things on a local or remote linux system
(most functionality for Debian/Ubuntu).

## Installation

```sh
sudo apt-get install  git  fabric
mkdir ~/repos && cd ~/repos
git clone  https://github.com/theno/fabsetup.git
```

## How to use fabsetup

__fabsetup__ is a __[fabric](http://www.fabfile.org/ "www.fabfile.org")__
script, so every command starts with a __`fab`__:

```sh
# go to the fabsetup repository
cd ~/repos/fabsetup


# task infos

## list all tasks: '-l'
fab -l

## show details: '-d'
fab -d setup.vim


# run tasks

fab setup.regex_repl

## on your local host:
fab setup.pencil_v3 -H localhost

## remote host:
fab up -H example.com
```

__[Setup-Howtos](./howtos "cookbook")__:

 * Customize fabsetup: [Initialize git repository
   `fabsetup_custom`](./howtos/fabsetup_custom.md)
 * [Set up an environment without sudo access](./howtos/no-sudo.md)
 * [Webserver Certificates with Letsencrypt](./howtos/letsencrypt.md)
 * [Host an Owncloud Service](./howtos/owncloud.md)
 * [Host an own F-Droid Repository](./howtos/f-droid-repo.md) (Android App Repository)
 * [Host a Selfoss Service](./howtos/selfoss.md) (RSS Reader Web Application)
 * [Install latest Node.js via nvm](./howtos/nodejs.md)
 * [Create or update a reveal.js presentation](./howtos/revealjs.md)
 * __[How to create and write a fabsetup-addon](./howtos/fabsetup-addon.md)__
