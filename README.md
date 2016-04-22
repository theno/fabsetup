# fabsetup

Set up and maintain a local or remote (Ubuntu) linux system.

## Let's bubble

__fabsetup__ is somehow like a Thermomix for linux setup recipies: The tasks
are the programs of the Thermomix and tell it what to do.  The
__[Howtos](./howtos "cookbook")__ are the cookbook, each howto stands for a
recipe.  The recipes are easy and short.  Sometimes, you don't like a recipe
and want to cook your own meal or you would like to make custom additions.
This works with [`fabsetup_custom`](./howtos/fabsetup_custom.md).

__fabsetup__ is a __[fabric](http://www.fabfile.org/ "www.fabfile.org")__
script, so every command starts with a __`fab`__:

  ```sh
  # go to the fabsetup repository
  cd ~/repos/fabsetup

  # table of content
  fab -l
    
  # show details
  fab -d setup.vim
    
  # run tasks
  fab setup.pencil -H localhost  # local
  fab setup.regex_repl
  fab up -H example.com          # or remote
  ```

Okay, that was just an appetizer. Now we should satisfy the very hunger with
this howtos:

 * Customize fabsetup: [Initialize git repository
   `fabsetup_custom`](./howtos/fabsetup_custom.md)
 * [Set up an environment without sudo access](./howtos/no-sudo.md)
 * [Webserver Certificates with Letsencrypt](./howtos/letsencrypt.md)
 * [Host an Owncloud Service](./howtos/owncloud.md)
 * [Host an own F-Droid Repository](./howtos/f-droid-repo.md)

## Installation

  ```sh
  sudo apt-get install  git  fabric
  mkdir ~/repos && cd ~/repos
  git clone  https://github.com/theno/fabsetup.git
  ```
