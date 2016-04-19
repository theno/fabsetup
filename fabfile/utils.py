import inspect
import sys
from functools import wraps


# inspired by: http://stackoverflow.com/a/6618825
def flo(string):
    '''Return the string given by param formatted with the callers locals.'''
    callers_locals = {}
    frame = inspect.currentframe()
    try:
        outerframe = frame.f_back
        callers_locals = outerframe.f_locals
    finally:
        del frame
    return string.format(**callers_locals)


# does not work if called from another package (with other globals)
def doc1():
    '''Return the first line of the (callers) docstring.'''
    return globals()[inspect.stack()[1][3]].__doc__.splitlines()[0]


def _wrap_with(color_code):
    '''Color wrapper.
    
    Example:
        >>> blue = _wrap_with('34')
        >>> print(blue('text'))
        \033[34mtext\033[0m
    '''
    def inner(text, bold=False):
        '''Inner color function.'''
        code = color_code
        if bold:
            code = flo("1;{code}")
        return flo('\033[{code}m{text}\033[0m')
    return inner


black = _wrap_with('30')
red = _wrap_with('31')
green = _wrap_with('32')
yellow = _wrap_with('33')
blue = _wrap_with('34')
magenta = _wrap_with('35')
cyan = _wrap_with('36')
white = _wrap_with('37')
default_color = _wrap_with('0')


def print_doc1(*args, **kwargs):
    '''Decorator, print the first line of the decorated functions docstring.

    May be invoked as a simple, argument-less decorator (i.e. ``@print_doc1``)
    or with named arguments ``color`` or ``bold`` (eg.
    ``@print_doc1(color=utils.red, bold=True)``).

    Example:
        >>> @print_doc1
        ... def foo():
        ...     """First line of docstring.
        ... 
        ...     another line.
        ...     """ 
        ...     pass
        ... 
        >>> foo()
        \033[34mFirst line of docstring.\033[0m
    '''
    color = kwargs.get('color', blue)
    bold = kwargs.get('bold', False)

    # for decorator with arguments see: http://stackoverflow.com/a/5929165
    def real_decorator(func):
        '''real decorator function'''
        @wraps(func)
        def wrapper(*args, **kwargs):
            '''the wrapper function'''
            try:
                print(color(func.__doc__.splitlines()[0], bold))
            except AttributeError as error:
                name = func.__name__
                print(red(flo('{name}() has no docstring')))
                raise(error)
            return func(*args, **kwargs)
        return wrapper

    invoked = bool(not args or kwargs)
    if not invoked:
        # invoke decorator function which returns the wrapper function
        return real_decorator(func=args[0])
    return real_decorator


def print_full_name(*args, **kwargs):
    '''Decorator, print the full name of the decorated function.

    May be invoked as a simple, argument-less decorator (i.e. ``@print_doc1``)
    or with named arguments ``color``, ``bold``, or ``prefix``
    (eg. ``@print_doc1(color=utils.red, bold=True, prefix=' ')``).
    '''
    color = kwargs.get('color', default_color)
    bold = kwargs.get('bold', False)
    prefix = kwargs.get('prefix', '')

    def real_decorator(func):
        '''real decorator function'''
        @wraps(func)
        def wrapper(*args, **kwargs):
            '''the wrapper function'''
            first_line = ''
            try:
                first_line = func.__module__ + '.' + func.__qualname__
            except AttributeError as exc:
                first_line = func.__name__
            print(color(prefix + first_line, bold))
            return func(*args, **kwargs)
        return wrapper

    invoked = bool(not args or kwargs)
    if not invoked:
        # invoke decorator function which returns the wrapper function
        return real_decorator(func=args[0])

    return real_decorator


# taken from: http://stackoverflow.com/a/3041990
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
    It must be "yes" (the default), "no" or None (which means an answer
    of the user is required).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, '1': True,
             "no": False, "n": False, '0': False,}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def query_input(question, default=None, color=default_color):
    """Ask a question for input via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.

    The "answer" return value is a str.
    """
    if default is None or default == '':
        prompt = ' '
    elif type(default) == str:
        prompt = flo(' [{default}] ')
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(color(question + prompt))
        choice = raw_input()
        if default is not None and choice == '':
            return default
        if choice != '':
            return choice


def filled_out_template_str(template, **substitutions):
    '''Return str template with applied substitutions.

    Example:
        >>> template = 'Asyl for {{name}} {{surname}}!'
        >>> filled_out_template_str(template, name='Edward', surname='Snowden')
        'Asyl for Edward Snowden!'

        >>> template = '[[[foo]]] was substituted by {{foo}}'
        >>> filled_out_template_str(template, foo='bar')
        '{{foo}} was substituted by bar'

        >>> template = 'names wrapped by {single} {curly} {braces} {{curly}}'
        >>> filled_out_template_str(template, curly='remains unchanged')
        'names wrapped by {single} {curly} {braces} remains unchanged'
    '''
    template = template.replace('{', '{{')
    template = template.replace('}', '}}')
    template = template.replace('{{{{', '{')
    template = template.replace('}}}}', '}')
    template = template.format(**substitutions)
    template = template.replace('{{', '{')
    template = template.replace('}}', '}')
    template = template.replace('[[[', '{{')
    template = template.replace(']]]', '}}')
    return template


def filled_out_template(filename, **substitutions):
    '''Return content of file filename with applied substitutions.'''
    res = None
    with open(filename, 'r') as fp:
        template = fp.read()
        res = filled_out_template_str(template, **substitutions)
    return res


if __name__ == '__main__':
    import doctest
    doctest.testmod()
