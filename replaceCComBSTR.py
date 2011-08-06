#!/usr/bin/env python
# coding:UTF-8
import os,sys
from os import path
import string,re
cppfiletest = re.compile(r'\.cpp$|\.h$|\.hpp$',re.IGNORECASE)
combstrdef = re.compile(r'\s*CComBSTR\s+(?P<bstrdefine>.*?)\s*;')
# 以参数形式传入的CComBSTR, 匹配的可能包括引用形式的参数需要处理
funcparambstr = re.compile(r'.*(.*CComBSTR(?P<bstrdefine>[&a-zA-Z0-9_\s]+).*)')
comment = re.compile(r'^\s*//')
trunk_trader = r'D:\trunk_tb_trader'
srcfiles = []
for root,dirs,files in os.walk(trunk_trader):
    oldlen = len(srcfiles)
    srcfiles += filter(lambda x:cppfiletest.search(x)<>None,files)
    for index in range(oldlen,len(srcfiles)):
        srcfiles[index] = os.path.join(root,srcfiles[index])

oldstdout = sys.stdout
sys.stdout = logfile = open(os.path.join(trunk_trader,'wronguseofCComBSTR.log'),'w')

findnum = 0
for srcfile in srcfiles:
    try:
        fp = open(srcfile,'r')
        # matchingcombstrs记录每个CComBSTR变量的一些信息
        # {
        #    'combstr' : [变量定义所在的行数, 该变量出现取地址(&)的次数, 在它定义之后的嵌套深度(用于记录变量的作用域), 指示是否为函数参数]
        # }
        matchingcombstrs = {}
        linenum = 0
        for line in fp:
            linenum += 1
            # 忽略注释
            if comment.search(line) <> None :
                continue
            if line.strip() == '':
                continue
            
            result = combstrdef.search(line)
            #  查找是否有新的CComBSTR变量定义
            if result <> None and result.group('bstrdefine').strip() != r'' and (result.group('bstrdefine') not in matchingcombstrs):
                matchingcombstrs[result.group('bstrdefine')] = [linenum,0,0,False]
                # 这行是变量定义,可以不用检查后面的了
                continue
            else:
                # 也有可能是函数参数使用了CComBSTR
                result = funcparambstr.search(line)
                if result <> None and result.group('bstrdefine').strip() != r'' and (result.group('bstrdefine') not in matchingcombstrs):
                    matchingcombstrs[result.group('bstrdefine')] = [linenum,0,0,True]
                    # 有可能函数定义的 { 写在同一行 ,处理这种情况
                    matchingcombstrs[result.group('bstrdefine')][2] += line.count('{') - line.count('}') 
                    # 这行是新的函数参数传递, 可以不用检查后面的了
                    continue
            for combstr in matchingcombstrs.keys():
                # 注意对引用变量的查找需要去掉匹配出来的&符号
                matchingcombstrs[combstr][1] += line.count('&'+combstr.replace('&','').strip())
                # 根据括号计算嵌套深度,用于检测变量是否还在作用域
                matchingcombstrs[combstr][2] += line.count('{') - line.count('}') 
                if matchingcombstrs[combstr][1] >= 2:
                    print 'In File: ' + srcfile + ' at line : ' + \
                          str(matchingcombstrs[combstr][0]) + ' CComBSTR: ' + \
                          combstr + ' has used the & operator more than 2 times.'
                    del matchingcombstrs[combstr]  # 删除该变量定义,英文已经找到泄漏位置
                    findnum += 1
                # 检查该CComBSTR变量是否超出作用域
                elif (not matchingcombstrs[combstr][3]) and matchingcombstrs[combstr][2] < 0:
                    del matchingcombstrs[combstr]
                # 检查函数参数是否还在函数范围内
                elif matchingcombstrs[combstr][3] and matchingcombstrs[combstr][2] <= 0:
                    del matchingcombstrs[combstr]
    except:
        print 'error : ' + srcfile
    finally:
        fp.close()

print 'finished. ' + str(findnum) +' results have been found.\n'
sys.stdout = oldstdout
logfile.close()
print 'finished. ' + str(findnum) +' results have been found.\n'+'press any key to continue. '
raw_input()    
