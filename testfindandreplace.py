#!/usr/bin/env python
# coding:UTF-8

import os,sys
import shutil
import findandreplace

rootdir = 'd:/test/'
testsrcdir = 'testsrc'
testdestdir = 'testdest'
testfile = { 'notexist' : ['001','002','003','004','005'],  # 替换目标不存在的文件
             'onlyone'  : ['101','102','103','104','105'],  # 有唯一对应的文件存在的
             'morethanone':['201','202','203','204','205']} # 多于一个同名存在的
testfileext = '.txt'
# clear old test files
shutil.rmtree(os.path.join(rootdir,testsrcdir),True)
shutil.rmtree(os.path.join(rootdir,testdestdir),True)
# generate src files
os.makedirs(os.path.join(rootdir,testsrcdir))
for key,values in testfile.iteritems():
    for filestr in values:
        srcfile = open(os.path.join(rootdir,testsrcdir,filestr+testfileext),'w')
        srcfile.write(filestr+'srcfile')
        srcfile.close()
# generate dest files
os.makedirs(os.path.join(rootdir,testdestdir))
for key,values in testfile.iteritems():
    if key == 'notexist':
        pass
    elif key == 'onlyone':
        for filestr in values:
            newdir = os.path.join(rootdir,testdestdir,filestr)
            os.makedirs(newdir)
            srcfile = open(os.path.join(newdir,filestr+testfileext),'w')
            srcfile.write(filestr+'destfile')
            srcfile.close()
    elif key=='morethanone':
        for filestr in values:
            newdir = os.path.join(rootdir,testdestdir,filestr)
            os.makedirs(newdir)
            srcfile = open(os.path.join(newdir,filestr+testfileext),'w')
            srcfile.write(filestr+'destfile')
            srcfile.close()
            srcfile = open(os.path.join(rootdir,testdestdir,filestr+testfileext),'w')
            srcfile.write(filestr+'destfile')
            srcfile.close()

findandreplace.findandreplace(os.path.join(rootdir,testsrcdir),os.path.join(rootdir,testdestdir))
