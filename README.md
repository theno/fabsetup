# fabsetup

Fabric tasks in order to set up and maintain configurations, software
installations and other things on a local or remote linux system.

## Development

Devel commands.

Install and set up latest python versions with pyenv:

```sh
pyenv update

pys=()  # python versions
for minor in {5..8}; do
  latest=$(pyenv install --list | grep -oP "(?<=^  )3\.$minor\.\d+$" | tail -1)
  pys=("${pys[@]}" $latest)
  pyenv install --skip-existing  $latest
done
pyenv local  ${pys[@]}

pip3.8 install tox
```

Run tox:

```sh
tox

PYTHONPATH= python3.8 -m tox  # long-winded way
```
