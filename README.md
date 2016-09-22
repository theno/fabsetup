# fabsetup

Set up and maintain a local or remote (Ubuntu) linux system.

## Installation

  ```sh
  sudo apt-get install  git  fabric
  mkdir ~/repos && cd ~/repos
  git clone  https://github.com/theno/fabsetup.git
  ```

## Let's bubble: How to use fabsetup

__fabsetup__ is somehow like a Thermomix for linux setup recipies: The tasks
are the programs of the Thermomix and tell it what to do.  The
__[Howtos](./howtos "cookbook")__ are the cookbook, each howto stands for a
recipe.  The recipes are easy and short (cf. [Thermomix-Breirezepte](https://github.com/theno/Breirezepte)).  Sometimes, you don't like a recipe
and want to cook your own meal or you would like to make custom additions.
This works with [`fabsetup_custom`](./howtos/fabsetup_custom.md).

__fabsetup__ is a __[fabric](http://www.fabfile.org/ "www.fabfile.org")__
script, so every command starts with a __`fab`__:

  ```sh
  # go to the fabsetup repository
  cd ~/repos/fabsetup


  # list all tasks: '-l'
  fab -l

  # show details: '-d'
  fab -d setup.vim


  # run tasks
  
  ## on your local host:
  fab setup.pencil -H localhost

  ## remote host:
  fab up -H example.com

  ## when no host specified you would be asked for:
  fab setup.regex_repl
  #<output. here it defaults to 'localhost'>
  #regex_repl
  #Install RegexREPL, a helper tool for building regular expressions.
  #No hosts found. Please specify host string for connection [localhost]:
  ```

Okay, that was just an appetizer. Now we should satisfy the very hunger with
this howtos:

 * Customize fabsetup: [Initialize git repository
   `fabsetup_custom`](./howtos/fabsetup_custom.md)
 * [Set up an environment without sudo access](./howtos/no-sudo.md)
 * [Webserver Certificates with Letsencrypt](./howtos/letsencrypt.md)
 * [Host an Owncloud Service](./howtos/owncloud.md)
 * [Host an own F-Droid Repository](./howtos/f-droid-repo.md)
 * [Install latest Node.js via nvm](./howtos/nodejs.md)
