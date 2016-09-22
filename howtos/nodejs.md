# Howto: Install latest version of Node.JS via Node Version Manager (nvm)

More info:
* Node Version Manager (nvm): https://github.com/creationix/nvm
* Node.js: https://nodejs.org/en/

## Install (or upgrade) Node Version Mangaer (nvm)

  ```sh
  fab setup.nvm  -H localhost
  ```

## Install latest NodeJS (and npm)

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
