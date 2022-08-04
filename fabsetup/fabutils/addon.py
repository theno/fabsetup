"""Create and write local files in the context of a Fabsetup Addon."""

import contextlib
import os
import os.path
import tempfile


FABSETUP_DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), ".fabsetup-downloads")


def filled_out_template_str(template, **substitutions):
    """Return str template with applied substitutions.

    Example:
        >>> template = '{{key}} = {{val}}'
        >>> filled_out_template_str(template, key='foo', val=42)
        'foo = 42'

        >>> template = '[[[foo]]] was substituted by {{foo}}'
        >>> filled_out_template_str(template, foo='bar')
        '{{foo}} was substituted by bar'

        >>> template = 'names wrapped by {single} {curly} {braces} {{curly}}'
        >>> filled_out_template_str(template, curly='remain unchanged')
        'names wrapped by {single} {curly} {braces} remain unchanged'

    """
    template = template.replace("{", "{{")
    template = template.replace("}", "}}")
    template = template.replace("{{{{", "{")
    template = template.replace("}}}}", "}")
    template = template.format(**substitutions)
    template = template.replace("{{", "{")
    template = template.replace("}}", "}")
    template = template.replace("[[[", "{{")
    template = template.replace("]]]", "}}")
    return template


def filled_out_template(filename, **substitutions):
    """Return content of file filename with applied substitutions."""
    res = None
    with open(filename, "r") as fp:
        template = fp.read()
        res = filled_out_template_str(template, **substitutions)
    return res


@contextlib.contextmanager
def template_context(from_path, package_name, substitutions):

    if from_path.endswith(".template"):

        from_str = filled_out_template(from_path, **substitutions)

        with tempfile.NamedTemporaryFile(prefix=package_name) as tmp_file:

            print("\n* template: `{from_path}`".format(from_path=from_path))
            print(
                "\n* filled out template: `{tmp_file.name}`".format(tmp_file=tmp_file)
            )

            with open(tmp_file.name, "w") as fp:
                fp.write(from_str)

            yield tmp_file.name
    else:
        yield from_path


class Addon:
    def __init__(self, module_dirname, context):
        self.module_dirname = module_dirname
        self.context = context

    @property
    def module_name(self):
        """
        eg. 'fabsetup_theno_termdown'
        """
        return os.path.basename(self.module_dirname)

    @property
    def package_dirname(self):
        """
        eg. '/home/theno/.fabsetup-addon-repos/fabsetup-theno-termdown'
        """
        return os.path.dirname(self.module_dirname)

    @property
    def package_name(self):
        """
        eg. 'fabsetup-theno-termdown'
        """
        result = os.path.basename(self.package_dirname)
        assert result == self.module_name.replace("_", "-")
        return os.path.basename(self.package_dirname)

    @property
    def files_basedir(self):
        """
        eg.
        '/home/theno/.fabsetup-addon-repos/'
        + 'fabsetup-theno-termdown/fabsetup_theno_termdown/files'
        """
        return os.path.join(self.module_dirname, "fabfile-data", "files")

    @property
    def downloads_basedir(self):
        """
        eg. '/home/theno/.fabsetup-downloads/fabsetup-theno-termdown'
        """
        return os.path.join(FABSETUP_DOWNLOADS_DIR, self.package_name)

    @staticmethod
    def _determine_from_tail(path):

        if path.startswith("~/"):
            path_tail = path[2:]  # path without beginning '~/'
            from_tail = os.path.join("home", "USERNAME", path_tail)
        else:
            # remove beginning '/' (if any), eg '/foo/bar' -> 'foo/bar'
            from_tail = path.lstrip(os.sep)

        return from_tail

    def _determine_from_path(self, path):

        from_tail = Addon._determine_from_tail(path)

        from_path = os.path.join(self.files_basedir, from_tail)
        from_path_template = "{}.template".format(from_path)

        if os.path.isfile(from_path):
            result = from_path
        elif os.path.isfile(from_path_template):
            result = from_path_template
        else:
            raise Exception(
                "Not any file of {} or {} exists".format(from_path, from_path_template)
            )

        return result

    @staticmethod
    def _substituted(string, substitutions):
        substituted = string
        for key, val in substitutions.items():
            if isinstance(val, str):
                substituted = substituted.replace(key, val)
        return substituted

    @staticmethod
    def _execute(cmds, formatters):
        for execute, cmd in cmds:
            execute(cmd.format(**formatters))

    def _install_local(self, from_path, to_path):

        to_path_parent = os.path.dirname(to_path)

        cmds_local = (
            [
                (self.context.local, "cp {from_path}  {to_path}"),
            ]
            if os.path.isdir(os.path.expanduser(to_path_parent))
            else [
                (self.context.local, "mkdir -p {to_path_parent}"),
                (self.context.local, "cp {from_path}  {to_path}"),
            ]
        )

        self._execute(
            cmds_local,
            formatters=dict(
                from_path=from_path,
                to_path=to_path,
                to_path_parent=to_path_parent,
                self=self,
            ),
        )

    def _install_local_sudo(self, from_path, to_path):

        to_path_parent = os.path.dirname(to_path)

        cmds_local_sudo = (
            [
                (self.context.local, "sudo cp {from_path}  {to_path}"),
            ]
            if os.path.isdir(os.path.expanduser(to_path_parent))
            else [
                (self.context.local, "sudo mkdir -p {to_path_parent}"),
                (self.context.local, "sudo cp {from_path}  {to_path}"),
            ]
        )

        self._execute(
            cmds_local_sudo,
            formatters=dict(
                from_path=from_path,
                to_path=to_path,
                to_path_parent=to_path_parent,
                self=self,
            ),
        )

    def _install_remote(self, from_path, to_path):

        to_path_parent = os.path.dirname(to_path)

        cmds_remote = (
            [
                (
                    self.context.local,
                    "scp {from_path}  "
                    "{self.context.host}@{self.context.user}:{to_path}",
                ),
            ]
            if os.path.isdir(os.path.expanduser(to_path_parent))
            else [
                (self.context.run, "mkdir -p {to_path_parent}"),
                (
                    self.context.local,
                    "scp {from_path}  "
                    "{self.context.host}@{self.context.user}:{to_path}",
                ),
            ]
        )

        self._execute(
            cmds_remote,
            formatters=dict(
                from_path=from_path,
                to_path=to_path,
                to_path_parent=to_path_parent,
                self=self,
            ),
        )

    def _install_remote_sudo(self, from_path, to_path):

        to_path_parent = os.path.dirname(to_path)

        temp_filename = os.path.join(
            os.sep, "tmp", self.package_name + "_" + os.path.basename(to_path)
        )

        cmds_remote_sudo = (
            [
                (
                    self.context.local,
                    "scp {from_path}  "
                    "{self.context.user}@{self.context.host}:{temp_filename}",
                ),
                (self.context.run, "sudo mv --force {temp_filename}  {to_path}"),
            ]
            if os.path.isdir(os.path.expanduser(to_path_parent))
            else [
                (
                    self.context.local,
                    "scp {from_path}  "
                    "{self.context.user}@{self.context.host}:{temp_filename}",
                ),
                (self.context.run, "sudo mkdir -p {to_path_parent}"),
                (self.context.run, "sudo mv --force {temp_filename}  {to_path}"),
            ]
        )

        self._execute(
            cmds_remote_sudo,
            formatters=dict(
                from_path=from_path,
                to_path=to_path,
                to_path_parent=to_path_parent,
                temp_filename=temp_filename,
                self=self,
            ),
        )

    def install_file(
        self, path, sudo=False, local=False, from_path=None, **substitutions
    ):
        """Install a file locally or on a remote host."""

        if from_path is None:
            from_path = self._determine_from_path(path)

        to_path = Addon._substituted(path, substitutions)

        with template_context(
            from_path, self.package_name, substitutions
        ) as from_path_:

            if local:
                if sudo:
                    self._install_local_sudo(from_path_, to_path)
                else:
                    self._install_local(from_path_, to_path)
            else:
                if sudo:
                    self._install_remote_sudo(from_path_, to_path)
                else:
                    self._install_remote(from_path_, to_path)
