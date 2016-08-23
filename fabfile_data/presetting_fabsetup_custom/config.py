# task: setup.powerline_shell

#font = 'Ubuntu Mono derivative Powerline:pixelsize=14,style=regular'
font = 'DejaVu Sans Mono for Powerline:pixelsize=13,style=regular'
#font = 'Source Code Pro for Powerline:pixelsize=14,style=regular'
#font = 'Anonymice Powerline:pixelsize=14,style=regular'


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


# task: custom.github

github_repos = [
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
