# Webserver Certificates with Letsencrypt

## Define domain names

In your [`fabsetup_custom`](./fabsetup_custom.md) repo in the `config.py` file
set the domain names of your sites.  For example, if your domain is
`example.com` and you have the sites `frdoid`, `owncloud`, `www`, and
`www-staging`:

  ```python
  domain_groups = [
      # SAN-DN entries of the first certificate
      [
	  # the first entry defines the name of the certificate file and must
	  # be the domain name for the tasks 'setup.service.fdroid' and
	  # 'setup.service.owncloud' to work properly
	  'example.com',
          'fdroid.example.com',
	  'owncloud.example.com',
	  'www.example.com',
      ],

      # second certificate
      [
          'www-staging.example.com',
      ],
  ]
  ```

##  Create the certificates

Now create a certificate using task `setup.server_letsencrypt`:
  ```sh
  fab  setup.server_letsencrypt  -H <you_domain>
  ```

Don't forget to save the changes of your custom fabsetup repo, e.g.
  ```sh
  cd  ~/repos/fabsetup/fabsetup_custom
  git  commit  -am 'add domain fdroid.example.com for letsencrypt certificates'
  ```
