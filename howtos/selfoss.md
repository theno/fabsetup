# Howto: Host an Selfoss Service

Selfoss is a "multipurpose rss reader, live stream, mashup, aggregation web
application".

More infos:
 * http://selfoss.aditu.de/
 * https://github.com/SSilence/selfoss

## Install or update selfoss

Scenario: You have a shell with sudo access on an internet hosting machine
(`<your_domain>`) running (ubuntu) linux.

  ```sh
  cd  ~/repos/fabsetup
  fab  setup.service.selfoss  -H <your_domain>
  ```

## Webserver certificate via letsencrypt

Add a `selfoss.<your_domain>` entry within of the `domain_groups` and create
a webserver certificate as described in the howto [Webserver Certificates with
Letsencrypt](./letsencrypt.md).

Your selfoss service is now available at this URL:
`https://selfoss.<your_domain>`
