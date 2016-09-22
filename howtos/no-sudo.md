# Run Tasks without sudo

If you don't have root access on a machine you can tell `fabsetup` to not
to use the `sudo` command:

  ```sh
  fab  --set nosudo  <task_name>  -H localhost
  ```

While not all tasks could be executed without `sudo`, this tasks work:
  ```sh
  cd ~/repos/fabsetup

  fab  --set nosudo  setup.i3
  fab  --set nosudo  setup.irssi
  fab  --set nosudo  setup.nvm
  fab  --set nosudo  setup.pencil
  fab  --set nosudo  setup.powerline_shell
  fab  --set nosudo  setup.pyenv
  fab  --set nosudo  setup.ripping_of_cds
  fab  --set nosudo  setup.regex_repl
  fab  --set nosudo  setup.solarized
  fab  --set nosudo  setup.telegram
  fab  --set nosudo  setup.tmux
  fab  --set nosudo  setup.vim
  ```

If executed together with `-H localhost` they can be used to setup a local
environment on a machine maintained by others where you cannot execute `sudo`,
e.g. at your uni or at work.
