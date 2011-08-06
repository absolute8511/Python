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
# 从svn导出指定版本的文件,filelist为要导出的svn文件路径列表,svnbasepath为服务器的svn url,localpath为本地导出根目录
# Revision为要导出的版本, samefold指示是否将导出文件放在同一路径下,还是重建和svn一样的本地目录树
def copyfilesfromsvn(filelist,svnbasepath,localpath,revision,samefold=False):
    shutil.rmtree(localpath,True)
    if not path.lexists(localpath):
        os.makedirs(localpath)
    os.chdir(localpath)
    prefix = r'/IMClient-RV/'
    prefix2 = r'/revolution_min/'
    prefix3 = r'/Private/'
    haserr = False
    for onefile in filelist:
        pos = onefile.find(prefix)
        if pos==-1:
            pos = onefile.find(prefix2)
            if pos == -1:
                pos = onefile.find(prefix3)
                if pos == -1:
                    continue
        if samefold:
            localfilepath = localpath + path.basename(onefile)
            if path.lexists(localfilepath):
                localfilepath = localfilepath + '-dup'
            cmdstr = 'svn export --force -r '+ str(revision) + ' ' + svnbasepath + onefile + ' ' + localfilepath
        else:
            localfilepath = localpath + onefile.replace(onefile[:pos], '', 1)
            if not path.lexists(path.dirname(localfilepath)):
                os.makedirs(path.dirname(localfilepath))
            cmdstr = 'svn export --force -r '+ str(revision) + ' ' + svnbasepath + onefile + ' ' + localfilepath
        try:
            retcode = subprocess.call(cmdstr,shell=True)
            if retcode != 0:
                haserr = True
        except OSError,e:
            haserr = True
    return haserr
# filelist为本地源码库的全路径,localsrcpath为本地源代码库的根路径,localdestpath为要拷贝到的目标根路径,
# samefold表示是否要在目标路径创建和源路径对应的目录树,还是仅拷贝文件到根路径
def copyfilesfromlocal(filelist,localsrcpath,localdestpath,samefold=False):
    shutil.rmtree(localdestpath,True)
    if not path.lexists(localdestpath):
        os.makedirs(localdestpath)
    os.chdir(localdestpath)
    prefix = r'/IMClient-RV/'
    prefix2 = r'/revolution_min/'
    prefix3 = r'/Private/'
    #prefix4 = '/modules/'
    #prefix = '/IMClient/Branches_tb/20110325_Base6.6002C_security'
    #prefix2 = '/IMClient/Branches_tb/20110420_Base6.6003C_security2'
    for onefile in filelist:
        pos = onefile.find(prefix)
        if pos==-1:
            pos = onefile.find(prefix2)
            if pos == -1:
                pos = onefile.find(prefix3)
                if pos == -1:
                    continue
        localfilepath = onefile.replace(onefile[:pos],'',1)
        try:
            if samefold:
                copydest = localdestpath + path.basename(localfilepath)
                if path.lexists(copydest):
                    copydest = copydest + '-dup'
                shutil.copy2(localsrcpath+localfilepath,copydest)
            else:
                copydest = localdestpath+localfilepath
                if not path.lexists(path.dirname(copydest)):
                    os.makedirs(path.dirname(copydest))
                shutil.copy2(localsrcpath+localfilepath,copydest)
        except IOError,e:
            pass

def generatemergefolds(svnlogfile,svnbasepath,localexportpath,localsrcpath):
        nodupfile = svnlogfile + '.nodup'
        result = deldup(svnlogfile,nodupfile)
        haserr1 = copyfilesfromsvn(result['Added'] + result['Modified'],svnbasepath,localexportpath+'/new',result['Revision'][len(result['Revision'])-1])
        haserr2 = copyfilesfromsvn(result['Modified'],svnbasepath,localexportpath+'/old',result['Revision'][0]-1)
        copyfilesfromlocal(result['Modified'],localsrcpath,localexportpath + '/third_merge')
        return (haserr1 or haserr2)
 
if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        srcfile = args[1]
        svnbasepath = 'http://svn.alisoft-inc.com/repos/im'
        if len(args) > 2:
            svnbasepath = args[2]
        localpath = r'D:/test/PYOutput'
        if len(args) > 3:
            localpath = args[3]
        localsrcpath = r'D:/trunk_tb_trader'
        if len(args) > 4:
            localsrcpath = args[4]
        haserr = generatemergefolds(srcfile,svnbasepath,localpath,localsrcpath)
        if not haserr:
            print "finished success."
        else:
            print "something error."
    else:
        print "Interactive Mode,进入交互模式"
        srcfile = raw_input("input the log file:")
        svnbasepath = 'http://svn.alisoft-inc.com/repos/im'
        tmp = raw_input('input svnbasepath:(default-'+svnbasepath+')')
        tmp = tmp.strip()
        if tmp != '':
            svnbasepath = tmp
        localpath = r'F:/PYOutput'
        tmp = raw_input('input localexportpath:(default-'+localpath+')')
        tmp = tmp.strip()
        if tmp != '':
            localpath = tmp
        localsrcpath = r'F:/2011_beta2'
        tmp = raw_input('input localsrcpath:(default-'+localsrcpath+')')
        tmp = tmp.strip()
        if tmp != '':
            localsrcpath = tmp
        haserr = generatemergefolds(srcfile,svnbasepath,localpath,localsrcpath)
        if not haserr:
            print "finished success."
        else:
            print "something error while copyfromsvn."
        raw_input('press any key to exit!')
        
