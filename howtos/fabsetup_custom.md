# fabsetup_custom

For custom tasks, files, templates and configurations you can use the git
repository `fabsetup_custom`.

Initialize git repository `fabsetup_custom`:
  ```sh
  cd  ~/repos/fabsetup

  fab INIT
  ```

Structure of git repo `fabsetup_custom`:

  ```sh
  tree ~/repos/fabsetup/fabsetup_custom/
  
  ~/repos/fabsetup/fabsetup_custom/
  ├── config.py          # <-- configurations are made here
  ├── fabfile_additions
  │   ├── custom.py      # <--- custom tasks, e.g. for 'fab custom.latex'
  │   └── __init__.py    # <-- custom tasks, eg. for 'fab setup_webserver'
  └── files                                       (without 'custom.' prefix)
      └── ...            # <--- custom files and templates
  ```

Every time you change something in your `fabsetup_custom` repo you should
commit the changes and create a backup.  Note: the `fabsetup_custom` repo
should not be made public, e.g. on github.

Tasks which use data from the `fabsetup_custom` are decorated by the decorator
function `needs_repo_fabsetup_custom()` which is defined in
[`fabutils.py`](../fabfile/fabutils.py).
