# Howto: Host an Owncloud Service

## Install and setup owncloud

Scenario: You have a shell with sudo access on an internet hosting machine
(`<your_domain>`) running (ubuntu) linux.

This will happen on your server:
* Install and enable nginx service
  * Therefore, deinstall and disable apache service
* Install owncloud
* Set up owncloud as a web service
* Host owncloud as a site via nginx

On a local shell, go to the fabsetup dir and run the task
`setup.service.owncloud`:

  ```sh
  cd  ~/repos/fabsetup
  fab  setup.service.owncloud  -H <your_domain>
  ```

## Webserver certificate via letsencrypt

Add an `owncloud.<your_domain>` entry within of the `domain_groups` and create
a webserver certificate as described in the howto [Webserver Certificates with
Letsencrypt](./letsencrypt.md).

Your owncloud service is now available at this URL:
`https://owncloud.<your_domain>`

## Update

  ```sh
  cd  ~/repos/fabsetup
  fab  up  -H <your_domain>
  ```
