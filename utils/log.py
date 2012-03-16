import maya.cmds as mc

import os.path
import datetime

def openLog(logDir,logName,mode='a'):
	'''
	'''
	# Check directory
	if not os.path.isdir(logDir): os.makedirs(logDir)
	
	# Open file for writing
	logFile = logDir+'/'+logName
	f = open(logFile,mode)
	
	# Add log header
	file = mc.file(q=True,sn=True)
	dt = datetime.datetime.now()
	f.write('\n\n=========\n')
	f.write('file: '+file+'\n')
	f.write('time: '+str(dt)+'\n')
	f.write('=========\n\n')
	
	# Return log file handle
	return f
	
def printLog(logDir,logName,mode='a',logLines=[]):
	'''
	'''
	# Check directory
	if not os.path.isdir(logDir): os.makedirs(logDir)
	
	# Open file for writing
	logFile = logDir+'/'+logName
	f = open(logFile,mode)
	
	# Print progress
	print('Printing to log file "'+logFile+'"!')
	
	# Add log header
	file = mc.file(q=True,sn=True)
	dt = datetime.datetime.now()
	f.write('\n\n=========\n')
	f.write('file: '+file+'\n')
	f.write('time: '+str(dt)+'\n')
	f.write('=========\n\n')
	
	# Add lines to log
	for line in logLines: f.write(line+'\n')
	
	# Close file handle
	f.close()
	
	# Return log file handle
	return logFile

def clearLog(logDir,logName):
	'''
	'''
	# Check directory
	if not os.path.isdir(logDir):
		raise Exception('Log directory "'+logDir+'" does not exist!')
	
	# Clear log file
	logFile = logDir+'/'+logName
	f = open(logFile,'w')
	f.write('')
	
	# Close file handle
	f.close()
