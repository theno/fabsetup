# ~/.fabsetup-downloads

The downloaded git-repositories in this subdirectories will be created or
overridden on fabsetup task execution.

More info: https://github.com/theno/fabsetup

Example structure:

```sh
> tree -L 3 -a ~/.fabsetup-downloads

/home/nolte/.fabsetup-downloads
│
├── README.md
│
├── fabsetup-theno-example1
│   └── ct-utils             <--- git repository
│       ├── ctutlz
│       ├── .editorconfig
│       ├── fabfile.py
│       ├── .git
│       ├── .gitignore
│       ├── LICENSE
│       ├── README.md
│       ├── setup.py
│       ├── tests
│       ├── tox.ini
│       └── .travis.yml
│
└── fabsetup-theno-example2
    ├── ctutlz               <--- git repository
    │   ├── ctutlz
    │   ├── .editorconfig
    │   ├── fabfile.py
    │   ├── .git
    │   ├── .gitignore
    │   ├── LICENSE
    │   ├── README.md
    │   ├── setup.py
    │   ├── tests
    │   ├── tox.ini
    │   └── .travis.yml
    └── utlz                 <--- git repository
        ├── fabfile.py
        ├── .git
        ├── .gitignore
        ├── LICENSE
        ├── README.md
        ├── setup.py
        ├── tests
        ├── tox.ini
        ├── .travis.yml
        └── utlz
```
