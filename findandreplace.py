#!/usr/bin/env python
# coding:UTF-8

import os,sys,shutil
from os import path

def findandreplace(src,dest):
    srcfiles = os.listdir(src)
    destfilesdict = {}
    #处理目标路径下(含子目录下)的所有文件
    for root,dirs,files in os.walk(dest):
        # 记录每个文件名所在的路径,多个同名文件则会有多个不同路径.
        # 这样就生成了文件名到文件所在路径的一个倒排索引
        for onefile in files:
            # 若该文件名的键值还未创建则先创建
            if onefile not in destfilesdict:
                destfilesdict[onefile] = []
            destfilesdict[onefile] += [root]
    multisamename = []; # 存储目标目录及其子目录下有多个同名文件的文件名
    for srcfile in srcfiles:
        fullsrcfile = os.path.join(src,srcfile)
        if os.path.isfile(fullsrcfile):
            if srcfile in destfilesdict:
                if len(destfilesdict[srcfile])>1:
                    multisamename += [srcfile]
                else:
                    # 有且只有唯一的一个同名文件,那么肯定是要替换的那个
                    shutil.copy(fullsrcfile,destfilesdict[srcfile][0]+'/'+srcfile)
                    print srcfile + ' replace success.'
    print 'following files has more than one in dest directory, replace skipped.'
    print '\n'.join(multisamename);
        
if __name__ == "__main__":
    args = sys.argv
    if len(args) > 2:
        src = args[1]
        dest = args[2]
        print "all files under the "+dest+\
              "(including the subdirectory) will be replaced by the files under " +\
              src+" where they have the same name."
        if raw_input('Sure(y/n?): ') == 'y':
            findandreplace(src,dest)
    else:
        print "Not enough arguments!"
