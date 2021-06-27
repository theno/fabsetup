import builtins


# print levels: silent < quiet < briefly < default < gassy
# ('quieter than' < 'louder than')


# def print_quiet(*args, **kwargs):
#     if print_quiet.enabled:
#         print_original(*args, **kwargs)
#
#
# def print_briefly(*args, **kwargs):
#     if print_briefly.enabled:
#         print_original(*args, **kwargs)


def print_default(*args, **kwargs):
    if print_default.enabled:
        print_original(*args, **kwargs)


# def print_gassy(*args, **kwargs):
#     if print_gassy.enabled:
#         print_original(*args, **kwargs)


def print_heading(*args, **kwargs):
    if print_heading.enabled:
        print_original(*args, **kwargs)


def print_docstring(*args, **kwargs):
    if print_docstring.enabled:
        print_original(*args, **kwargs)


def print_code_block(*args, **kwargs):
    if print_code_block.enabled:
        print_original(*args, **kwargs)


def print_command_line(*args, **kwargs):
    if print_command_line.enabled:
        print_original(*args, **kwargs)


# def print_command_output(*args, **kwargs):
#     if print_command_output.enabled:
#         print_original(*args, **kwargs)


# defaults
print_default.enabled = True
print_heading.enabled = True
print_docstring.enabled = True
print_code_block.enabled = True
print_command_line.enabled = True
# print_command_output.enabled = True


# def _enable(quiet, briefly, default, gassy):
#     print_quiet.enabled = bool(quiet)
#     print_briefly.enabled = bool(briefly)
#     print_default.enabled = bool(default)
#     print_gassy.enabled = bool(gassy)
#
#
# def set_silent():
#     '''
#     In default print mode will be printed:
#
#     * nothing
#     '''
#     _enable(False, False, False, False)
#
#
# def set_quiet():
#     '''
#     In default print mode will be printed:
#
#     * headings
#     * executed commands
#     * user queries
#
#     * print_quiet()
#     '''
#     _enable(True, False, False, False)
#
#
# def set_briefly():
#     '''
#     In default print mode will be printed:
#
#     * headings
#     * docstrings of tasks, subtasks, subsubtasks
#     * executed commands
#     * output of commands
#     * return code if not 0
#     * user queries
#
#     * print_quiet(), print_briefly()
#     '''
#     _enable(True, True, False, False)
#
#
# def set_default():
#     '''
#     In default print mode will be printed:
#
#     * headings
#     * docstrings of tasks, subtasks, subsubtasks
#     * executed commands
#     * output of commands
#     * return code if not 0
#     * user queries
#
#     * print_quiet(), print_briefly(), print_default()
#     '''
#     _enable(True, True, True, False)
#
#
# def set_gassy():
#     '''
#     In default print mode will be printed:
#
#     * headings
#     * docstrings of tasks, subtasks, subsubtasks
#     * executed commands
#     * output of commands
#     * return code if not 0
#     * user queries
#
#     * print_quiet(), print_briefly(), print_default(), print_gassy()
#     '''
#     _enable(True, True, True, True)


# "redirect" print builtin, cf. https://stackoverflow.com/a/46658735
print_original = builtins.print
builtins.print = print_default

# set_default()
