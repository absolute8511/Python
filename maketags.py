# -*- coding: utf8 -*- 
import os,sys
from os import path
import string,re

#在系统头文件目录下查找系统头文件,可以自行添加头文件路径
def findsysinclude(filename,includepath):
    if filename==None:
        return None
    sysincludepath = ['/usr/include/','/usr/include/c++/4.4/',
            '/usr/lib/gcc/i486-linux-gnu/4.4/include/','/usr/include/c++/4.4/i486-linux-gnu/']   #系统头文件目录
    includepath += sysincludepath
    for onepath in includepath:
        if path.isfile(onepath+filename):
            return onepath+filename
    print 'Not found: '+filename
    return None

#读取用户传入的头文件路径参数
args = sys.argv
print args
retest = re.compile(r'\.cpp$|\.c$|\.h$|\.hpp$|\.cc$',re.IGNORECASE)
cppfiles = []
#查找用户项目路径下的所有源文件
for root,dirs,files in os.walk(os.getcwd()):
    oldlen = len(cppfiles)
    cppfiles += filter(lambda x:retest.search(x)<>None,files)        #过滤非C/C++文件
    for index in range(oldlen,len(cppfiles)):
        cppfiles[index] = root + '/' + cppfiles[index];

oldstdout = sys.stdout
sys.stdout= logfile = open('maketags.log','w')

print 'total cpp files: ' + str(len(cppfiles))
includetest = re.compile(r'\s*#include\s*((<(?P<sysincludefile>.*?)>)|("(?P<userincludefile>.*?)"))')  ## *?代表不贪婪匹配

#对每个C++源文件，查找它包含的头文件以及它的头文件所包含的头文件，以次递归直到全部包含
#由于已经遍历过用户目录了，因次只需要再把系统头文件加近来即可
for cppfile in cppfiles:
    try:
        fp = open(cppfile,'r')
        print 'finding in file: '+cppfile
        for line in fp:
            result = includetest.search(line)   #正则匹配头文件
            if result <> None:
                print 'Matched include line is:'+result.group()
                tmp = findsysinclude(result.group('sysincludefile'),args[1:])
                tmp2 = findsysinclude(result.group('userincludefile'),args[1:]) #用户头文件也去找系统目录
                if tmp<>None and cppfiles.count(tmp)==0:
                    cppfiles += [tmp]
                    print 'Added sys files: '+tmp
                # tmp2 = path.abspath(path.dirname(cppfile)+'/'+result.group('userincludefile'))
                if tmp2<>None and cppfiles.count(tmp2)==0:
                    cppfiles += [tmp2]
                    print 'Added user files: '+tmp2
    finally:
        fp.close()
try:
    filelist = open('python_tags_filelist','w')
    filelist.writelines('\n'.join(cppfiles))
finally:
    filelist.close()

print 'total cpp and include files:'+str(len(cppfiles))
# print 'after delete duplicate files: ' + str(len(set(cppfiles)))
sys.stdout = oldstdout
logfile.close()

os.system('ctags --c++-kinds=+p --fields=+iaS --extra=+q -L python_tags_filelist')
