# fabsetup

Set up and maintain a local or remote (Ubuntu) linux system.

## Let's bubble

__fabsetup__ is a __[fabric](http://www.fabfile.org/ "www.fabfile.org")__ script, so every command starts with a __`fab`__.

It is somehow like a Thermomix for linux setup recipies:
The tasks are the programs of the Thermomix and tell it what to do.
The [Howtos](./fabfile/__init__.py "cookbook") are the cookbook, each howto stands for a recipe.

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

Okay, that was just an appetizer. Now we should satisfy the very hunger:

  ```sh
  # initialize a git repository for customizations
  fab INIT
    
  # set up machines by running tasks of tasks
  fab setup_webserver -H <your_server_on_the_internet>
  fab setup_desktop -H localhost
  ```


## Installation

  ```sh
  sudo apt-get install  git  fabric
  mkdir ~/repos && cd ~/repos
  git clone  https://github.com/theno/fabsetup.git
  ```
