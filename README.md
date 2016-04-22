# fabsetup

Set up and maintain a local or remote (Ubuntu) linux system.

## Let's bubble

__fabsetup__ is a __[fabric](http://www.fabfile.org/ "www.fabfile.org")__ script, so every command starts with a __`fab`__.

It is somehow like a Thermomix for linux setup recipies:
The tasks are the programs of the Thermomix and tell it what to do.
The __[Howtos](./howtos "cookbook")__ are the cookbook, each howto
stands for a recipe.

  ```sh
  # go to the fabsetup repository
  cd ~/repos/fabsetup

  # table of content
  fab -l
    
  # show details
  fab -d setup.pencil
    
  # run tasks
  fab setup.pencil -H localhost
  fab setup.regex_repl
  ```

Okay, that was just an appetizer. Now we should satisfy the very hunger with this howtos:
 * [Initialize git repository `fabsetup_custom`](./howtos/fabsetup_custom.md)
 * [Set up an environment without sudo access](./howtos/no-sudo.md)
 * [Webserver Certificates with Letsencrypt](./howtos/letsencrypt.md)
 * [Host an Owncloud Service](./howtos/owncloud.md)
 * [Own F-Droid Repository](./howtos/f-droid-repo.md)

## Installation

  ```sh
  sudo apt-get install  git  fabric
  mkdir ~/repos && cd ~/repos
  git clone  https://github.com/theno/fabsetup.git
  ```
