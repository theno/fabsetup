# fabsetup

Set up and maintain a local or remote (Ubuntu) linux system.


## Let's bubble

fabsetup is a fabric script, so every command starts with a `fab`.

It is somehow like a Thermomix for linux setup recipies.  Let's page through
the cookbook and rustle up some snack:

    # go to the fabsetup repository
    cd ~/repos/fabsetup

    # table of content
    fab -l
    
    # show details
    fab -d setup.pencil
    
    # run tasks
    fab setup.pencil -H localhost
    fab setup.regex_repl

Okay, that was just an appetizer. Now we should satisfy the very hunger:

    # initialize a git repository for customizations
    fab INIT
    
    # set up machines by running tasks of tasks
    fab setup_webserver -H <your_server_on_the_internet>
    fab setup_desktop -H localhost


## Installation

    sudo apt-get install  git  fabric
    mkdir ~/repos && cd ~/repos
    git clone  https://github.com/theno/fabsetup.git
