# fabsetup-custom

For custom tasks, files, templates and configurations you can use the git
repository `fabsetup-custom`.

Initialize git repository `fabsetup-custom`:
  ```sh
  cd  ~/repos/fabsetup

  fab INIT
  ```

Structure of git repo `fabsetup-custom`:

  ```sh
  tree ~/.fabsetup-custom/

  ~/.fabsetup-custom/
  ├── config.py          # <-- configurations are made here
  ├── fabfile_
  │   ├── custom.py      # <--- custom tasks, e.g. for 'fab custom.latex'
  │   └── __init__.py    # <-- custom tasks, eg. for 'fab setup_webserver'
  └── files                                   #  (without prefix 'custom.')
      └── ...            # <--- custom files and templates
  ```

Every time you change something in your `fabsetup-custom` repo you should
commit the changes and create a backup.  Note: the `fabsetup-custom` repo
should not be made public, e.g. on github.

Tasks which use data from the `fabsetup-custom` are decorated by the decorator
function `needs_repo_fabsetup-custom()` which is defined in
[`fabutils.py`](../fabsetup/fabutils.py).
