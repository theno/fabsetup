import sys
import inspect
from os.path import basename
from io import StringIO

import invoke
from docutils.parsers.rst import Directive
from docutils import nodes, statemachine
from sphinx.ext import autodoc
from sphinx.util.inspect import stringify_signature

import fabsetup

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# note: not required because fabsetup was installed already via
# `pip install .[devel]`
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('../fabsetup/'))

# -- Project information -----------------------------------------------------

project = "Fabsetup"
author = "Theodor Nolte"
copyright = author  # fallback
with open("../LICENSE.txt") as fh:
    prefix = "Copyright (c) "
    for line in fh.readlines():
        if line.startswith(prefix):
            copyright = line.split(prefix)[-1].strip()

# The full version, including alpha/beta/rc tags
release = "fabsetup-{}".format(fabsetup.__version__)


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "recommonmark",
    # TODO DEVEL
    # https://github.com/pyinvoke/invoke/issues/313#issuecomment-387249051
    # 'invocations.autodoc',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# sphinx.ext.autodoc
# https://stackoverflow.com/a/37210251
autodoc_member_order = "bysource"


# Fix autodoc to be able to extract fabric tasks and fabsetup subtasks.
#
# resources:
# https://github.com/pyinvoke/invocations/blob/master/invocations/autodoc.py#L51
# https://github.com/sphinx-doc/sphinx/issues/3783#issuecomment-628738539
# https://github.com/sphinx-doc/sphinx/blob/697dff31ab09625ead62e1a7ec0780126aeb07c6/sphinx/ext/autodoc/__init__.py
# https://github.com/sphinx-doc/sphinx/blob/3.2.x/sphinx/util/inspect.py


class TaskDocumenter(autodoc.DocstringSignatureMixin, autodoc.ModuleLevelDocumenter):
    objtype = "task"
    directivetype = "function"

    @classmethod
    def can_document_member(cls, member, membername, isattr, paren):
        return isinstance(member, invoke.Task)

    def format_signature(self):
        function = self.object.body
        # sig = signature(subject=function, follow_wrapped=True)
        sig = inspect.signature(function, follow_wrapped=True)
        return stringify_signature(sig)

    def document_members(self, all_members=False):
        pass

    def format_name(self):
        nam = super().format_name()
        return "@task\n{nam}".format(nam=nam)  # noqa: E0100

    def get_doc(self, **kwargs):
        result = super().get_doc(**kwargs)
        for arg, descr in self.object.help.items():
            result[0].append("")
            result[0].append(":param {arg}:".format(arg=arg))
            result[0].append("    {descr}".format(descr=descr))
        return result


class SubtaskDocumenter(autodoc.DocstringSignatureMixin, autodoc.ModuleLevelDocumenter):
    objtype = "subtask"
    directivetype = "function"

    @classmethod
    def can_document_member(cls, member, membername, isattr, paren):
        try:
            return inspect.getsourcelines(member)[0][0].startswith("@subtask")
        except Exception:
            pass
        return False

    def format_signature(self):
        function = self.object
        sig = inspect.signature(function, follow_wrapped=True)
        return stringify_signature(sig)

    def document_members(self, all_members=False):
        pass

    def format_name(self):
        nam = super().format_name()
        return "@subtask\n{nam}".format(nam=nam)  # noqa: E0100

    def get_doc(self, **kwargs):
        result = super().get_doc(**kwargs)
        return result


# cf. https://stackoverflow.com/a/18143318
class ExecDirective(Directive):
    """Execute the specified python code and insert the output into the document"""

    has_content = True

    def run(self):
        oldStdout, sys.stdout = sys.stdout, StringIO()

        tab_width = self.options.get(
            "tab-width", self.state.document.settings.tab_width
        )
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1
        )

        try:
            exec("\n".join(self.content))
            text = sys.stdout.getvalue()
            lines = statemachine.string2lines(text, tab_width, convert_whitespace=True)
            self.state_machine.insert_input(lines, source)
            return []
        except Exception:
            return [
                nodes.error(
                    None,
                    nodes.paragraph(
                        text="Unable to execute python code at %s:%d:"
                        % (basename(source), self.lineno)
                    ),
                    nodes.paragraph(text=str(sys.exc_info()[1])),
                )
            ]
        finally:
            sys.stdout = oldStdout


def setup(app):
    app.add_autodocumenter(TaskDocumenter)
    app.add_autodocumenter(SubtaskDocumenter)
    app.add_directive("exec", ExecDirective)
