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
