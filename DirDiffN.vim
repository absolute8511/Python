command! -nargs=* -complete=dir DirDiffN call <SID>DirDiffN (<f-args>)
command! -nargs=0 DirDiffNOpen call <SID>DirDiffNOpen ()
command! -nargs=0 DirDiffNNext call <SID>DirDiffNNext ()
command! -nargs=0 DirDiffNPrev call <SID>DirDiffNPrev ()
command! -nargs=0 DirDiffNQuit call <SID>DirDiffNQuit ()

if !exists("g:DirDiffWindowSize")
    let g:DirDiffWindowSize = 14
endif

" diffbuffer file's struct is as below:
" =======================================
" DirDiffNum
" <X>=XXXXX 
" ...
" ...
" ...
" (DirDiffNum lines like <X>=XXXXX)
" 
"     File:XXXXX @ <X>,<X>,<X>
"     File:XXXXX @ <X>,<X>
" =======================================
let s:DirDiffNum = 2
let s:DirDiffNFirstDiffLine = s:DirDiffNum + 3    " first line of the difffile list
let s:DirDiffNDifferLine = "File:"
let s:DiffBufferNum = 0  " The num of the opened buffers (in diff mode)

function! <SID>DirDiffN(DiffBuffer)
    silent exe "edit ".a:DiffBuffer
    " go to the beginning of the file
    0
    " read the num of dirs to be diffed.
    let s:DirDiffNum = getline(1) + 0
    let s:DirDiffNFirstDiffLine = s:DirDiffNum + 3
    let b:currentDiff = s:DirDiffNFirstDiffLine - 1
    nnoremap <buffer> q :call <SID>DirDiffNQuit()<CR>
    nnoremap <buffer> <CR>  :call <SID>DirDiffNOpen()<CR>  
    nnoremap <buffer> <2-Leftmouse> :call <SID>DirDiffNOpen()<CR>
    setlocal nomodified
    setlocal nomodifiable
    setlocal buftype=nowrite
    setlocal nowrap
    call <SID>SetupSyntax()

    " Open the first diff
    call <SID>DirDiffNNext()
endfunction

" Set up syntax highlighing for the diff window
function! <SID>SetupSyntax()
  if has("syntax") && exists("g:syntax_on") 
    syn match DirDiffSrcDir             "<.>"
    syn match DirDiffSelected           "^==>.*" contains=DirDiffSrcA,DirDiffSrcB

    hi def link DirDiffSrcDir               Directory
    hi def link DirDiffFiles              String
    hi def link DirDiffSelected           DiffChange
  endif
endfunction

" Quit the DirDiff mode
function! <SID>DirDiffNQuit()
    let in = confirm ("Are you sure you want to quit DirDiffN?", "&Yes\n&No", 2)
    if (in == 1)
        call <SID>CloseDiffWindows()
        bd!
    endif
endfun

" Close the opened diff comparison windows if they exist
function! <SID>CloseDiffWindows()
    if (<SID>AreDiffWinsOpened())
        wincmd k
        " Ask the user to save if buffer is modified
        call <SID>AskIfModified()
        bd!
        " User may just have one window opened, we may not need to close
        " the second diff window
        if (&diff)
            call <SID>AskIfModified()
            for index in range(2,s:DiffBufferNum)
                bd!
            endfor
        endif
    endif
endfunction
" 获取对应序号的文件夹代号 
function! <SID>GetBaseDirSymbol(dirNum)
    let line = getline(a:dirNum+1)
    let dirsym = substitute(line,'\(.*\)=.*$','\1','')
    return dirsym
endfunction
" 获取对应行的需要比较的文件名(不含参与比较的文件夹路径)
function! <SID>GetDiffLineFileName(line)
    let regex = '^.*' . s:DirDiffNDifferLine . '\(.*\) @ .*$'
    let fileToProcess = substitute(a:line, regex, '\1', '')
    let fileToProcess = substitute(fileToProcess,'^ *','','')
    let fileToProcess = substitute(fileToProcess,' *$','','')
    return fileToProcess
endfunction

function! <SID>DirDiffNOpen()
    " First dehighlight the last marked
    call <SID>DeHighlightLine()

    " Mark the current location of the line
    "mark n
    let b:currentDiff = line(".")

    call <SID>CloseDiffWindows()

    let line = getline(".")
    " Parse the line and see whether it's a "Only in" or "Files Differ"
    call <SID>HighlightLine()
    if <SID>IsDiffer(line)
        let fileName = <SID>GetDiffLineFileName(line)
        let fileList = []
        " 获取要参与比较的文件全路径名列表
        for dirnum in range(1,s:DirDiffNum)
            let dirsym = <SID>GetBaseDirSymbol(dirnum)
            if match(line,dirsym)>=0
                let fileList += [<SID>GetBaseDir(dirnum) . fileName]
            endif
        endfor
        split
        wincmd k
        let s:DiffBufferNum = 0
        for onefile in fileList
            if s:DiffBufferNum == 0
                silent exec "edit ".fnameescape(onefile)
                " if only one file,then just make itself as diff mode
                if len(fileList) == 1
                    diffthis
                endif
            else
                silent exec "vert diffsplit ".fnameescape(onefile)
            endif
            let s:DiffBufferNum += 1
        endfor
        " Go back to the diff window
        wincmd j
        " Resize the window
        exe ("resize " . g:DirDiffWindowSize)
        exe (b:currentDiff)
        " Center the line
        exe ("normal z.")
    endif
endfunction

function! <SID>IsDiffer(line)
    return (match(a:line, "^ *" . s:DirDiffNDifferLine . "\\|^==> " . s:DirDiffNDifferLine  ) == 0)
endfunction

" Ask the user to save if the buffer is modified
function! <SID>AskIfModified()
    if (&modified)
        let input = confirm("File " . expand("%:p") . " has been modified.", "&Save\nCa&ncel", 1)
        if (input == 1)
            w!
        endif
    endif
endfunction

function! <SID>HighlightLine()
    let savedLine = line(".")
    exe (b:currentDiff)
    setlocal modifiable
    let line = getline(".")
    if (match(line, "^    ") == 0)
        s/^    /==> /
    endif
    setlocal nomodifiable
    setlocal nomodified
    exe (savedLine)
    redraw
endfunction

function! <SID>DeHighlightLine()
    let savedLine = line(".")
    exe (b:currentDiff)
    let line = getline(".")
    setlocal modifiable
    if (match(line, "^==> ") == 0)
        s/^==> /    /
    endif
    setlocal nomodifiable
    setlocal nomodified
    exe (savedLine)
    redraw
endfunction
" 获取第dirNum个参与比较的文件夹的路径
function! <SID>GetBaseDir(dirNum)
    let regex = '^.*=\(.*\).*$'
    let line = getline(a:dirNum+1)
    let rtn = substitute(line, regex , '\1', '') "取该行中的=后面的字符串,\1即取匹配的第一个()中的内容
    return rtn
endfunction

function! <SID>DirDiffNNext()
    " If the current window is a diff, go down one
    if (&diff == 1)
        wincmd j
    endif
    " if the current line is within the header range, we go to the
    " first diff line open it
    if ((b:currentDiff + 1) < s:DirDiffNFirstDiffLine)
        exe (s:DirDiffNFirstDiffLine - 1)
        let b:currentDiff = line(".")
    endif
    silent! exe (b:currentDiff + 1)
    call <SID>DirDiffNOpen()
endfunction

function! <SID>DirDiffNPrev()
    " If the current window is a diff, go down one
    if (&diff == 1)
        wincmd j
    endif
    if ((b:currentDiff - 1) < s:DirDiffNFirstDiffLine)
        return
    endif
    silent! exe (b:currentDiff - 1)
    call <SID>DirDiffNOpen()
endfunction

function! <SID>AreDiffWinsOpened()
    let currBuff = expand("%:p")
    let currLine = line(".")
    wincmd k
    let abovedBuff = expand("%:p")
    if (&diff)
        let abovedIsDiff = 1
    else
        let abovedIsDiff = 0
    endif
    " Go Back if the aboved buffer is not the same
    if (currBuff != abovedBuff)
        wincmd j
        " Go back to the same line
        exe (currLine)
        if (abovedIsDiff == 1)
            return 1
        else
            " Aboved is just a bogus buffer, not a diff buffer
            return 0
        endif
    else
        exe (currLine)
        return 0
    endif
endfunction
