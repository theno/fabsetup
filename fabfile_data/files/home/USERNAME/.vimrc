set nocompatible
set t_Co=16
call pathogen#infect()
Helptags
syntax on
set background=dark " light | dark "
colorscheme solarized
filetype plugin on
call togglebg#map("<F5>")

set cursorline
set colorcolumn=80

set textwidth=79
set number

nmap <F8> :NERDTreeToggle<CR>
nmap <F9> :TagbarToggle<CR>

let g:tagbar_autoclose=1
let g:tagbar_autofocus=1
let g:tagbar_sort=0

set smartindent
set autoindent
filetype plugin indent on

au FileType python setlocal formatprg=autopep8\ -

set hlsearch
