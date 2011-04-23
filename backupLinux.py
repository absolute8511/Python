#! /usr/bin/python
# coding:UTF-8

import sys,os,subprocess,time
# backupLog log the last full backup time
backupLog = '/home/backupLog'
fullbackupPrefix = '/home/fullbackupLinux-'
incbackupPrefix = '/home/incbackupLinux-'
timeformat = '%Y-%m-%d %H:%M:%S'
backupDir = '/home'
excludePattern = ['/home/*/Music','/home/*/Pictures','/home/*/Videos','/home/*/vmware','*.vmdk','/home/*/trunk_tb','/home/*/.cache']
excludePattern += [fullbackupPrefix+'*',incbackupPrefix+'*']
excludePatternFile = '/tmp/excludePatternFile'
fp = open(excludePatternFile,'w')
fp.write('\n'.join(excludePattern))
fp.close()

os.chdir('/')

now = time.localtime()
if now.tm_mday == 1 or (not os.path.lexists(backupLog) ):
    # first day of each month or the first time backup will make full backup
    retcode = subprocess.call('tar -zcvf "' + fullbackupPrefix + time.strftime(timeformat,now) + 
            '.tar.gz" --exclude-from=' + excludePatternFile + ' ' + backupDir + ' > /dev/null',shell=True)
    if retcode != 0:
        print 'error during making the full backup.errcode: ' + str(retcode)
    fp = open(backupLog,'w')
    fp.write(time.strftime(timeformat,now))
    fp.close()
else:
    fp = open(backupLog,'r')
    lastbptime = fp.readline().strip()
    fp.close()
    # make the incremental backup
    retcode = subprocess.call('tar -zcvf "' + incbackupPrefix + 
            lastbptime + '.tar.gz" -N "' + lastbptime + 
            '" --exclude-from=' + excludePatternFile + ' ' + backupDir + ' > /dev/null', shell=True)
    if retcode != 0:
        print 'error during making the incremental backup. errcode: ' + str(retcode)
subprocess.Popen('shutdown -h +10',shell=True)
print 'finished. the system will shutdown in 10 mins.'
