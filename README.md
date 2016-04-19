# fabsetup

Thermomix for linux setup recipies.


## Let's bubble

fabsetup is a fabric script, so every command starts with a `fab`.  Let's page
through the cookbook and rustle up some snack:

    cd ~/repos/fabsetup # go to the fabsetup repository

    fab -l
    fab -d setup.pencil
    fab setup.pencil -H localhost

Okay, that was just an appetizer. Now we should satisfy the very hunger:

    fab INIT
    fab -d setup_webserver
    fab setup_webserver -H <your_server_on_the_internet>


## Installation

    sudo apt-get install  git  fabric
    mkdir ~/repos && cd ~/repos
    git clone  https://github.com/theno/fabsetup.git
