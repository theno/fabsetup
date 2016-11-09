# Howto: Install latest version of Node.js via nvm

More info:
* Node Version Manager (nvm): https://github.com/creationix/nvm
* Node.js: https://nodejs.org/en/

## Install (or upgrade) nvm

  ```sh
  fab setup.nvm  -H localhost
  ```

## Install latest Node.js (and npm)

  ```sh
  nvm install node
  ```

## Use it in a new shell

  ```sh
  nvm use node

  node  # or npm or ...
  ```

Usage of `nvm`:
* https://github.com/creationix/nvm#usage
* run: `nvm --help`
