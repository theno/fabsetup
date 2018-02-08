import os

from fabric.context_managers import quiet
from fabric.api import execute

from fabsetup.fabutils import exists, run, task, print_msg, suggest_localhost
from fabsetup.fabutils import checkup_git_repo, subtask, subsubtask
from fabsetup.fabutils import install_file_legacy
from fabsetup.fabutils import update_or_append_line, needs_repo_fabsetup_custom
from fabsetup.utils import flo, query_input, query_yes_no


_lazy_dict = {}
_lazy_queries = {
    'presi_title': {
        'question': 'Presentation title?',
        'default': None,  # will be derived from basedir
    },
    'presi_subtitle': {
        'question': 'Presentation sub-title?',
        'default': "It's about this and that",
    },
    'presi_description': {
        'question': 'Short description of your presentation?',
        'default': 'This presentation shows this, that and foo bar baz.'
    },
    'github_user': {
        'question': 'github username?',
        'default': None,
    },
    'github_repo': {
        'question': 'github repo?',
        'default': None,
    },
}


def _lazy(key, default=None):
    question = _lazy_queries[key]['question']
    default = default or _lazy_queries[key]['default']
    val = _lazy_dict.get(key, None)
    if not val:
        val = query_input(question, default)
        _lazy_dict[key] = val
    return val


@task
@suggest_localhost
def revealjs(basedir=None, title=None, subtitle=None, description=None,
             github_user=None, github_repo=None):
    '''Set up or update a reveals.js presentation with slides written in markdown.

    Several reveal.js plugins will be set up, too.

    More info:
      Demo: https://theno.github.io/revealjs_template
      http://lab.hakim.se/reveal-js/
      https://github.com/hakimel/reveal.js
      plugins:
        https://github.com/hakimel/reveal.js/wiki/Plugins,-Tools-and-Hardware
        https://github.com/rajgoel/reveal.js-plugins/
        https://github.com/e-gor/Reveal.js-TOC-Progress
        https://github.com/e-gor/Reveal.js-Title-Footer
    '''
    basedir = basedir or query_input('Base dir of the presentation?',
                                     default='~/repos/my_presi')
    revealjs_repo_name = 'reveal.js'
    revealjs_dir = flo('{basedir}/{revealjs_repo_name}')

    _lazy_dict['presi_title'] = title
    _lazy_dict['presi_subtitle'] = subtitle
    _lazy_dict['presi_description'] = description
    _lazy_dict['github_user'] = github_user
    _lazy_dict['github_repo'] = github_repo

    question = flo("Base dir already contains a sub dir '{revealjs_repo_name}'."
                   ' Reset (and re-download) reveal.js codebase?')
    if not exists(revealjs_dir) or query_yes_no(question, default='no'):
        run(flo('mkdir -p {basedir}'))
        set_up_revealjs_codebase(basedir, revealjs_repo_name)
        install_plugins(revealjs_dir)
        apply_customizations(repo_dir=revealjs_dir)
    if exists(revealjs_dir):
        install_files_in_basedir(basedir, repo_dir=revealjs_dir)
        init_git_repo(basedir)
        create_github_remote_repo(basedir)
        setup_npm(revealjs_dir)
    else:
        print('abort')


def export_repo(parent_dir, repo_url, repo_name=None):
    if repo_name:
        repo_dir = flo('{parent_dir}/{repo_name}')
        if exists(repo_dir):
            run(flo('rm -rf {repo_dir}'),
                msg='delete existing repo dir')
    repo_name = checkup_git_repo(repo_url, name=repo_name, base_dir=parent_dir)
    run(flo('cd {parent_dir}/{repo_name} && rm -rf .git/'),
        msg='delete .git dir (the hole presentation becomes a git repository)')


@subtask
def set_up_revealjs_codebase(basedir, repo_name):
    export_repo(basedir, repo_url='https://github.com/hakimel/reveal.js.git',
                repo_name=repo_name)


@subsubtask
def install_plugin_menu(plugin_dir):
    # FIXME: Checkout latest tag, not head
    export_repo(plugin_dir, 'https://github.com/denehyg/reveal.js-menu.git',
                repo_name='menu')


@subsubtask
def install_plugin_toc_progress(plugin_dir):
    export_repo(plugin_dir,
                'https://github.com/e-gor/Reveal.js-TOC-Progress.git',
                repo_name='toc-progress_all')
    run(flo('mv {plugin_dir}/toc-progress_all/plugin/toc-progress  '
            '{plugin_dir}/toc-progress'))
    run(flo('rm -rf {plugin_dir}/toc-progress_all'))
    print_msg('correct css path (because reveal.js is placed in a subdir)')
    update_or_append_line(flo('{plugin_dir}/toc-progress/toc-progress.js'),
                          prefix='\tlink.href="plugin/'
                                 'toc-progress/toc-progress.css"',
                          new_line='\tlink.href="reveal.js/plugin/'
                                   'toc-progress/toc-progress.css"')


@subsubtask
def install_plugin_title_footer(plugin_dir):
    export_repo(plugin_dir,
                'https://github.com/e-gor/Reveal.js-Title-Footer.git',
                repo_name='title-footer_all')
    run(flo('mv {plugin_dir}/title-footer_all/plugin/title-footer  '
            '{plugin_dir}/title-footer'))
    run(flo('rm -rf {plugin_dir}/title-footer_all'))
    print_msg('correct css path (because reveal.js is placed in a subdir)')
    update_or_append_line(flo('{plugin_dir}/title-footer/title-footer.js'),
                          prefix='\tlink.href="plugin/'
                                 'title-footer/title-footer.css";',
                          new_line='\tlink.href="reveal.js/plugin/'
                                   'title-footer/title-footer.css";')


@subtask
def install_plugins(revealjs_dir):
    plugin_dir = flo('{revealjs_dir}/plugin')
    install_plugin_menu(plugin_dir)
    install_plugin_toc_progress(plugin_dir)
    install_plugin_title_footer(plugin_dir)


@subsubtask
def custom_index_html(basedir, repo_dir):
    if exists(flo('{repo_dir}/index.html')):
        run(flo('cd {repo_dir} && cp --no-clobber index.html index.html_orig'),
            'save original index.html')
    index_html_path = flo('{basedir}/index.html')
    if exists(index_html_path):
        print_msg('\nalready exists (skip)')
    else:
        presi_title = _lazy('presi_title', os.path.basename(basedir))
        print_msg(flo('\ncustomizations of index.html:\n'
                      " * <title>{presi_title}</title>\n"
                      " * 'solarized' as default theme\n"
                      " * load plugins 'menu', 'solarized', 'toc-progress'\n"
                      " * config for plugins: 'menu', 'math'\n"
                      ""))
        install_file_legacy(path=index_html_path,
                     from_path='~/repos/my_presi/index.html',
                     presi_title_space=presi_title.replace('_', ' '))
        thanks_img_path = flo('{basedir}/img/thanks.jpg')
        if not exists(thanks_img_path):
            install_file_legacy(path=thanks_img_path,
                         from_path='~/repos/my_presi/img/thanks.jpg')


@subsubtask
def tweak_css(repo_dir):
    '''Comment out some css settings.'''
    print_msg("* don't capitalize titles (no uppercase headings)")
    files = [
        'beige.css', 'black.css', 'blood.css', 'league.css', 'moon.css',
        'night.css', 'serif.css', 'simple.css', 'sky.css', 'solarized.css',
        'white.css',
    ]
    line = '  text-transform: uppercase;'
    for file_ in files:
        update_or_append_line(filename=flo('{repo_dir}/css/theme/{file_}'),
                              prefix=line, new_line=flo('/*{line}*/'))

    print_msg('* images without border')
    data = [
        {'file': 'beige.css',     'line': '  border: 4px solid #333;'},
        {'file': 'black.css',     'line': '  border: 4px solid #fff;'},
        {'file': 'blood.css',     'line': '  border: 4px solid #eee;'},
        {'file': 'league.css',    'line': '  border: 4px solid #eee;'},
        {'file': 'moon.css',      'line': '  border: 4px solid #93a1a1;'},
        {'file': 'night.css',     'line': '  border: 4px solid #eee;'},
        {'file': 'serif.css',     'line': '  border: 4px solid #000;'},
        {'file': 'simple.css',    'line': '  border: 4px solid #000;'},
        {'file': 'sky.css',       'line': '  border: 4px solid #333;'},
        {'file': 'solarized.css', 'line': '  border: 4px solid #657b83;'},
        {'file': 'white.css',     'line': '  border: 4px solid #222;'},
    ]
    for item in data:
        file_ = item['file']
        lines = [item['line'], ]
        lines.extend(['  box-shadow: 0 0 10px rgba(0, 0, 0, 0.15); }',
                      '  box-shadow: 0 0 20px rgba(0, 0, 0, 0.55); }'])
        for line in lines:
            update_or_append_line(filename=flo('{repo_dir}/css/theme/{file_}'),
                                  prefix=line, new_line=flo('/*{line}*/'))


@subsubtask
def install_markdown_slides_template(basedir):
    slides_path = flo('{basedir}/slides.md')
    if exists(slides_path):
        print_msg('already exists (skip)')
    else:
        presi_title = _lazy('presi_title', os.path.basename(basedir))
        presi_subtitle = _lazy('presi_subtitle')
        cur_date = run(r'date +%F', capture=True)
        install_file_legacy(path=slides_path,
                     from_path='~/repos/my_presi/slides.md',
                     presi_title_upper=presi_title.replace('_', ' ').upper(),
                     presi_subtitle=presi_subtitle, cur_date=cur_date)


@subsubtask
def symbolic_links(repo_dir):
    print_msg('Create symbolic links in order to be able to start presi '
              'with npm (from the subdir reveal.js as starting point)')
    repo_name = os.path.basename(repo_dir)
    run(flo('ln -snf ../{repo_name}  {repo_dir}/{repo_name}'))
    run(flo('ln -snf ../img  {repo_dir}/img'))
    run(flo('ln -snf ../index.html  {repo_dir}/index.html'))
    run(flo('ln -snf ../slides.md  {repo_dir}/slides.md'))


@subsubtask
def install_readme(basedir):
    readme_path = flo('{basedir}/README.md')
    if exists(readme_path):
        print_msg('already exists (skip)')
    else:
        presi_title = _lazy('presi_title', os.path.basename(basedir))
        presi_subtitle = _lazy('presi_subtitle')
        presi_description = _lazy('presi_description')
        install_file_legacy(path=readme_path, from_path='~/repos/my_presi/README.md',
                     presi_title=presi_title, presi_subtitle=presi_subtitle,
                     presi_description=presi_description, basedir=basedir)


@subtask
def apply_customizations(repo_dir):
    '''Customize reveal.js codebase and installed plugins.'''
    tweak_css(repo_dir)
    symbolic_links(repo_dir)
    return repo_dir


@subtask
def install_files_in_basedir(basedir, repo_dir):
    custom_index_html(basedir, repo_dir)
    install_markdown_slides_template(basedir)
    install_readme(basedir)


@subtask
def init_git_repo(basedir):
    basedir_abs = os.path.expanduser(basedir)
    if os.path.isdir(flo('{basedir_abs}/.git')):
        print_msg('git repo already initialized (skip)')
    else:
        if not exists('{basedir_abs}/.gitignore'):
            install_file_legacy(path=flo('{basedir_abs}/.gitignore'),
                         from_path='~/repos/my_presi/.gitignore')
        run(flo('cd {basedir} && git init'))
        run(flo('cd {basedir} && git add .'))
        run(flo('cd {basedir} && git commit -am "Initial commit"'))


def remote_origin_configured(basedir):
    entry_exists = False
    with quiet():
        entry_exists = run(flo('''grep '\[remote "origin"\]' '''
                           '{basedir}/.git/config')).return_code == 0
    return entry_exists


def _insert_repo_infos_into_readme(basedir, github_user, github_repo):
    print_msg('\nadd github user and repo name into README.md')
    filename = flo('{basedir}/README.md')
    # FIXME: workaround: line starts with space "trick" for github.io link
    #        correct solution would be: create util function update_line()
    #                                   which will not append if prefix not
    #                                   found in file
    update_or_append_line(filename,
                          #prefix=' https://USER.github.io/REPO',
                          prefix=' https://',
                          new_line=flo(' https://{github_user}.github.io/'
                                       '{github_repo}'))
    update_or_append_line(filename,
                          #prefix='https://github.com/USER/REPO/blob/master/'
                          #       'slides.md',
                          prefix='https://github.com/',
                          new_line=flo('https://github.com/{github_user}/'
                                       '{github_repo}/blob/master/slides.md'))


def _create_github_remote_repo(basedir):
    '''More info:
      https://help.github.com/articles/adding-an-existing-project-to-github-using-the-command-line/
      https://developer.github.com/v3/repos/#create
      https://stackoverflow.com/a/10325316
    '''
    github_user = _lazy('github_user')
    github_repo = _lazy('github_repo', default=os.path.basename(basedir))

    _insert_repo_infos_into_readme(basedir, github_user, github_repo)
    run(flo('cd {basedir} && git add README.md'))
    run(flo('cd {basedir} && git commit -am "Add github repo and user '
            'into README.md"'))

    print_msg('create github repo')
    run(flo("cd {basedir}  &&  "
            "curl -u '{github_user}' https://api.github.com/user/repos "
            "-d '") + '{"name":"' + flo('{github_repo}"') + "}'")
    run(flo('cd {basedir}  &&  '
            'git remote add origin '
            'git@github.com:{github_user}/{github_repo}.git'))
    run(flo('cd {basedir}  &&  git push origin master'))


@subtask
def create_github_remote_repo(basedir):
    '''Create a remote origin repo at github.com if wanted.'''
    if remote_origin_configured(basedir):
        print_msg('remote origin already configured (skip)')
    elif query_yes_no('Create remote repo at github.com?', default='no'):
        _create_github_remote_repo(basedir)


@subtask
def setup_npm(revealjs_dir):
    if query_yes_no('\nSet up npm for serving presentation?',
                    default='no'):
        run(flo('cd {revealjs_dir}  &&  '
                'npm install'))
        print_msg(flo('\nServe presentation locally '
                      '(monitors source files for changes):\n\n'
                      '    cd {revealjs_dir}  &&  npm start\n\n'
                      'View presentation in a browser:\n\n'
                      '    http://localhost:8000'))


@task
@suggest_localhost
def decktape():
    '''Install DeckTape.

    DeckTape is a "high-quality PDF exporter for HTML5 presentation
    frameworks".  It can be used to create PDFs from reveal.js presentations.

    More info:
      https://github.com/astefanutti/decktape
      https://github.com/hakimel/reveal.js/issues/1252#issuecomment-198270915
    '''
    run('mkdir -p ~/bin/decktape')
    if not exists('~/bin/decktape/decktape-1.0.0'):
        print_msg('\n## download decktape 1.0.0\n')
        run('cd ~/bin/decktape && '
            'curl -L https://github.com/astefanutti/decktape/archive/'
            'v1.0.0.tar.gz | tar -xz --exclude phantomjs')
        run('cd ~/bin/decktape/decktape-1.0.0 && '
            'curl -L https://github.com/astefanutti/decktape/releases/'
            'download/v1.0.0/phantomjs-linux-x86-64 -o phantomjs')
        run('cd ~/bin/decktape/decktape-1.0.0 && '
            'chmod +x phantomjs')
    run('ln -snf ~/bin/decktape/decktape-1.0.0 ~/bin/decktape/active',
        msg='\n## link installed decktape version as active')
    print_msg('\nCreate PDF from reveal.js presentation:\n\n    '
              '# serve presentation:\n    '
              'cd ~/repos/my_presi/reveal.js/ && npm start\n\n    '
              '# create pdf in another shell:\n    '
              'cd ~/bin/decktape/active && \\\n    '
              './phantomjs decktape.js --size 1280x800  localhost:8000  '
              '~/repos/my_presi/my_presi.pdf')


@task
@needs_repo_fabsetup_custom  # for import of github_user from config.py
@suggest_localhost
def revealjs_template():
    '''Create or update the template presentation demo using task `revealjs`.
    '''
    from config import basedir, github_user, github_repo

    run(flo('rm -f {basedir}/index.html'))
    run(flo('rm -f {basedir}/slides.md'))
    run(flo('rm -f {basedir}/README.md'))
    run(flo('rm -rf {basedir}/img/'))

    title = 'reveal.js template'
    subtitle = '[reveal.js][3] presentation written ' \
               'in [markdown][4] set up with [fabric][5] & [fabsetup][6]'
    description = '''\
This presentation shows how to create a reveal.js presentation which will be
set up with the fabric task `setup.revealjs` of fabsetup.

Also, you can use this presentation source as a reveal.js template:
* Checkout this repo
* Then set the title in the `index.html` and edit the
  `slides.md`.'''

    execute(revealjs, basedir, title, subtitle, description,
            github_user, github_repo)

    # (README.md was removed, but not the github remote repo)
    print_msg('\n## Re-add github repo infos into README.md')
    basename = os.path.basename(basedir)
    _insert_repo_infos_into_readme(basedir, github_user=_lazy('github_user'),
                                   github_repo=_lazy('github_repo',
                                                     default=basename))

    print_msg('\n## Assure symbolic link not tracked by git exists\n')
    run(flo('ln -snf ../reveal.js  {basedir}/reveal.js/reveal.js'))
