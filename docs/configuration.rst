=============
Configuration
=============

The configuration of Fabsetup is based on the same mechanics as used in
`Fabric <https://docs.fabfile.org/en/latest/concepts/configuration.html>`_ and
`Invoke <https://docs.pyinvoke.org/en/latest/concepts/configuration.html>`_.

The prefix for environment variables is ``FABSETUP_``, see `here
<https://docs.pyinvoke.org/en/latest/concepts/configuration.html#environment-variables>`_
for the rules.

In order to verify which configuration is currently effective run: ``fabsetup
--show-config``.  This prints out the merged configuration before task
execution.

Defaults
========

Fabsetup uses sane defaults and is usable "out of the box":

.. exec::
    import pprint
    import black
    import fabsetup.main
    defaults = fabsetup.main.Defaults()
    print(".. code-block:: python\n")
    lines = black.format_str(
        str(defaults.as_dict()),
        # pprint.pformat(defaults.as_dict()),  # sorts keys
        mode=black.FileMode()
    )
    for line in lines.split("\n"):
        print(f"    {line}")

Customization Examples
======================

Log every fabsetup call as an HTML file with inline CSS, add in Your
``~/.fabsetup.yaml``:

.. code-block:: yaml

    outfile:
      dir: ~/.fabsetup-runs
      pandoc:
        html:
          dir: ~/.fabsetup-runs/html
        toc: true
