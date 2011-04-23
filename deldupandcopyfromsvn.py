#!/usr/bin/env python
# coding:UTF-8
# coding=utf-8

import os,sys,shutil,string,subprocess
from os import path
# 删除重复的修改项,并统计排序
def deldup(srcfile,destfile):
    linesnodup = {}
    linesnodup['Added'] = []
    linesnodup['Modified'] = []
    linesnodup['Deleted'] = []
    linesnodup['Others'] = []
    linesnodup['Revision'] = []
    fp = open(srcfile,'r')
    linelist = fp.readlines()
    for line in linelist:
        # 查找modified开头的行,因为只有这种行才需要去重
        if line.find(r'Modified') == 0 and linesnodup['Modified'].count(line)>0:
            pass
        else:
            isfinded = False
            for key in linesnodup.keys():
                if line.find(key)==0:
                    linesnodup[key] += [line]
                    isfinded = True
                    break
            if not isfinded:
                linesnodup['Others'] += [line]
    fp.close()
    for key,values in linesnodup.iteritems():
        if key == 'Others':
            pass
        else:
            linesnodup[key].sort(key=lambda x:x.lower())

    # 删除前缀
    for key,values in linesnodup.iteritems():
        if key=='Others':
            pass
        elif len(values)>0:
            startpos = values[0].find(': ') + 2
            for i in range(0,len(values)):
                endpos = values[i].find('(Copy from path')
                if endpos == -1:
                    linesnodup[key][i] = linesnodup[key][i][startpos:].strip()
                else:
                    linesnodup[key][i] = linesnodup[key][i][startpos:endpos].strip()
    # 过滤Modified中的在Add中出现过的文件
    linesnodup['Modified'] = [ v for v in linesnodup['Modified'] if linesnodup['Added'].count(v) == 0]
    fp = open(destfile,mode='w')
    tmp = [v for v in linesnodup['Added'] if linesnodup['Deleted'].count(v)>0]
    if len(tmp) > 0:
        fp.write('以下文件同时出现在Added列表和Deleted列表中,清格外注意!\n')
        fp.write('\n'.join(tmp))
        fp.write('\n')
    tmp = [v for v in linesnodup['Modified'] if linesnodup['Deleted'].count(v)>0] 
    if len(tmp) > 0:
        fp.write('以下文件同时出现在Modified列表和Deleted列表中,清格外注意!\n')
        fp.writelines('\n'.join(tmp))
        fp.write('\n')
    #结果输出到文件
    for key,values in linesnodup.iteritems():
        if key == 'Others':
            pass
        else:
            fp.write(key+' : \n')
            fp.writelines('\n'.join(linesnodup[key]))
            fp.write('\n\n')
    fp.writelines(linesnodup['Others'])
    fp.close()
    # 将Revision中的串转成整数重新排序
    for i in range(0,len(linesnodup['Revision'])):
        linesnodup['Revision'][i] = int(linesnodup['Revision'][i])
    linesnodup['Revision'].sort()
    return linesnodup            
# 从svn导出指定版本的文件,filelist为要导出的文件列表,svnbasepath为svn路径,localpath为本地导出根目录
# Revision为要导出的版本, samefold指示是否将导出文件放在同一路径下,还是重建和svn一样的本地目录树
def copyfilesfromsvn(filelist,svnbasepath,localpath,revision,samefold=True):
    shutil.rmtree(localpath,True)
    if not path.lexists(localpath):
        os.makedirs(localpath)
    os.chdir(localpath)
    haserr = False
    for onefile in filelist:
        if samefold:
            cmdstr = 'svn export -r '+ str(revision) + ' ' + svnbasepath + onefile
        else:
            if not path.lexists(path.dirname(localpath+onefile)):
                os.makedirs(path.dirname(localpath+onefile))
            cmdstr = 'svn export -r '+ str(revision) + ' ' + svnbasepath + onefile + ' ' + localpath + onefile
        try:
            retcode = subprocess.call(cmdstr,shell=True)
            if retcode != 0:
                haserr = True
        except OSError,e:
            haserr = True
    return haserr

if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        srcfile = args[1]
        destfile = srcfile + '.nodup'
        result = deldup(srcfile,destfile)
        svnbasepath = 'http://svn.alisoft-inc.com/repos/im'
        if len(args) > 2:
            svnbasepath = args[2];
            localpath = r'D:/test/PYOutput'
            haserr = copyfilesfromsvn(result['Added'] + result['Modified'],svnbasepath,localpath+'/new',result['Revision'][len(result['Revision'])-1])
            haserr = copyfilesfromsvn(result['Modified'],svnbasepath,localpath+'/old',result['Revision'][0]-1)
            if not haserr:
                print "finished success."
            else:
                print "something error."
    else:
        print "Not enough arguments!"
