# Howto: Set up or update a reveal.js presentation with slides written in markdown

More info:
* reveal.js template presentation: https://theno.github.io/revealjs_template/
  * source: https://github.com/theno/revealjs_template
* reveal.js: http://lab.hakim.se/reveal-js/
  * source: https://github.com/hakimel/reveal.js

## Create a new presentation by installing the reveal.js template

At first, [install](https://github.com/theno/fabsetup#installation) fabric sript *fabsetup*. Then:

  ```sh
  cd ~/repos/fabsetup  &&  fab setup.revealjs  -H localhost
  ```

Running the task for the first time, a reveal.js template will be installed.
During the installation you will be asked for:
* Directory of the presentation
* Title
* Sub-Title
* Short description

Optionally, the script can create a remote origin repo at github in order to
publicly serve the presentation.

Also, you will be asked for to optionally download JavaScript libs with `npm`
for running the presentation as a local site
([how to install npm](./nodejs.md)).

Finally, start editing the `slides.md` file.

## Update reveal.js codebase

  ```sh
  fab setup.revealjs  -H localhost
  ```

When re-running the task `setup.revealjs`, you will be asked for to optionally
download the latest reveal.js codebase (everything in subdir `reveal.js` will
be replaced; other files in particular `slides.md` and `index.html` will not be
touched).

## Create PDF of the presentation with decktape

Install decktape:

  ```sh
  fab setup.decktape  -H localhost
  ```

Serve the presentation locally:

  ```sh
  cd ~/repos/my_presi/reveal.js
  npm start
  ```

Create the PDF:

  ```sh
  cd ~/bin/decktape/active && \
  ./phantomjs decktape.js --size 1280x800  localhost:8000  ~/repos/my_presi/my_presi.pdf
  ```
