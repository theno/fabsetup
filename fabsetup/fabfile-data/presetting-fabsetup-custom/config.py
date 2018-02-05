# task: setup.powerline_shell

fontlist = 'xft:DejaVu\ Sans\ Mono\ for\ Powerline:pixelsize=13:style=Book,' \
           'xft:FreeSerif,xft:Symbola'
#fontlist = 'xft:Ubuntu\ Mono\ derivative\ Powerline:pixelsize=14:style=regular'
#fontlist = 'xft:DejaVu\ Sans\ Mono\ for\ Powerline:pixelsize=13:style=regular'
#fontlist = 'xft:Source\ Code\ Pro\ for\ Powerline:pixelsize=14:style=regular'
#fontlist = 'xft:Anonymice\ Powerline:pixelsize=14:style=regular'


# task: setup.server_letsencrypt

# for each group one certificate will be created
domain_groups = [
    [
#        '{{hostname}}',
#        'fdroid.{{hostname}}',
#        'owncloud.{{hostname}}',
#        'www.{{hostname}}',
    ],
]


# task: setup.service.fdroid

#fdroid_repo_secret = '{{fdroid_repo_secret}}'


# task: custom.repos

git_repos = [
    {
#        'name': 'pyopenssl', # optional, will be derived from url by default
        'url': 'https://github.com/pyca/pyopenssl.git',
    },
    {
        'url': 'https://github.com/pyca/cryptography.git',
    },
]


# task: custom.vim

vim_package_repos = [
]


# task: setup.revealjs_template

basedir = '~/repos/revealjs_template'
#github_user = '{{your_github_username}}'
github_repo = 'revealjs_template'


# task: setup.vim_janus

vim_janus_additional_addons = [
    {
        'name': 'vim-colors-solarized',
        'url': 'git://github.com/altercation/vim-colors-solarized.git',
    },
    {
        'name': 'vim-nerdtree-tabs',
        'url': 'https://github.com/jistr/vim-nerdtree-tabs.git',
    },
    {
        'url': 'https://github.com/klen/python-mode.git',
    },
    {
        'url': 'https://github.com/posva/vim-vue.git',
    },
    {
        'url': 'https://github.com/sukima/xmledit.git',
    },
    {
        'url': 'https://github.com/suan/vim-instant-markdown.git',
    },
    {
        'url': 'https://github.com/editorconfig/editorconfig-vim.git',
    },
    {
        'url': 'https://github.com/christoomey/vim-tmux-navigator.git',
    },
]
