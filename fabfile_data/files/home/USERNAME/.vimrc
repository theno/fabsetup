set nocompatible
set t_Co=16

" https://github.com/tpope/vim-pathogen
execute pathogen#infect()
syntax on
filetype plugin indent on
Helptags

" https://bbs.archlinux.org/viewtopic.php?id=164108
set background=light " dark | light "
colorscheme solarized
set cursorline
set colorcolumn=80
call togglebg#map("<F5>")


set textwidth=79
set number
set smartindent
set autoindent
" no-outdenting of #-comments in perl files: http://stackoverflow.com/a/191230
set cindent
set cinkeys=0{,0},!^F,o,O,e " default is: 0{,0},0),:,0#,!^F,o,O,e

set expandtab
set shiftwidth=4
set softtabstop=4
set tabstop=4
set tw=0

set ignorecase
set hlsearch

"http://timmurphy.org/2012/04/26/highlighting-tabs-in-vim/
highlight SpecialKey ctermfg=7*
set listchars=tab:\|-,trail:□
set list

set mouse=a

set modeline

nmap <F8> :NERDTreeMirrorToggle<CR>

"Tagbar http://www.vim.org/scripts/script.php?script_id=3465
let g:tagbar_autoclose=1
let g:tagbar_autofocus=1
let g:tagbar_sort=0
nmap <F9> :TagbarToggle<CR>

au FileType python setlocal formatprg=autopep8\ -

" Omni completion
" see: http://vim.wikia.com/wiki/Omni_completion
filetype plugin on
set ofu=syntaxcomplete#Complete
