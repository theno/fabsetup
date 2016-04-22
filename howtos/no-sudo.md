# Run Tasks without sudo

If you don't have root access on a machine you can tell `fabsetup` to not
use the `sudo` command:

  ```sh
  fab  --set nosudo  <task_name>
  ```

While not all tasks could be executed without `sudo`, this one could work:
  ```sh
  cd ~/repos/fabsetup

  fab  --set nosudo  setup.pencil
  fab  --set nosudo  setup.regex_repl
  fab  --set nosudo  setup.vim
  ```

If executed together with `-H localhost` they can be used to setup a local
environment on a machine maintained by others where you cannot execute `sudo`,
e.g. at your uni or at work.
