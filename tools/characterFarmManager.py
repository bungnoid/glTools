#!/bin/env python
import sys
import os
import subprocess
from optparse import OptionParser

import ika.context.util

#import glTools.nrig.utils

class CharacterFarmManager(object):

	def __init__(self):
		
		self.origPath = os.getcwd()
	
		self.start          = 'start'
		self.mayaVers       = 'maya_2014.ext2p05'
		self.optionsFlag    = '-o'
		self.vfxCodeRoot    = 'VFX_CODE_ROOT:'
		self.executableFlag = '-x'
		self.executable     = 'mayapy'
		self.argsFlag       = '-a'
		self.pythonFile     = None
		
		self.mayaProcess    = []
		
		# self.report = {'pass' : ['<CharName> finished.'], 'fail': ['<CharName> errored, <message>']}
		self.report = {'pass':[], 'fail':[]}

	def main(self):
	
		self.parseArguments()
		
		if self.options.verbose:
			print self.options
		
		self.prepareMayaCmd()
		
		self.executeMaya()
		os.chdir(self.origPath)
		
		self.printReport()
		
	def parseArguments(self):
		'''
			parse args from cmd line
		'''
		usage = "This module is designed to be a high level method to send a set of characters and subtasks to the farm with a python file to execute."
		
		parser = OptionParser(usage=usage)
		
		parser.add_option("-f", "--file", dest="pythonFile",
				  help="Python file to execute", metavar="FILE")
		
		parser.add_option("-r", "--codeRoot", dest="codeRoot",
				  help="Set the VFX Code Root", metavar="DIRECTORY")
		
		parser.add_option("-c", "--chars", dest="chars",
				  help='A string encoded list of characters. eg "[\'jack\', \'scott\']"', metavar="String")
		
		parser.add_option("-v", action="store_true", dest="verbose", default=False)
		
		parser.add_option("-s", "--subtasks", dest="subtasks",
				  help='A string encoded list of subtasks. eg "[\'face\', \'face_wip\']"', metavar="String")
		
		(self.options, args) = parser.parse_args(sys.argv)
		self.options.chars = eval(self.options.chars)
		self.options.subtasks = eval(self.options.subtasks)
        
	def printReport(self):
		
		print "\n\n##############################"
		print "Report for Character Farm Manager"
		print "##############################\n\n"
		
		if len(self.report['pass']):
			print '\nCollection of "Pass" messages'
			for item in self.report['pass']:
				print item

		if len(self.report['fail']):
			print '\nCollection of "Fail" messages'
			for item in self.report['fail']:
				print item
				
	def setupEnv(self, char=None, subtask=None):
		'''
			prepare the env to execute maya
		'''
		if not char: raise Exception('No char passed into the setupEnv def')
		if not subtask: raise Exception('No subtask passed into the setupEnv def')
		
		ctx_dict = {'task': 'rig',
		            'extension': 'mb',
		            'assetTypeDir': 'crowd',
		            'subtask': subtask,
		            'asset': char,
		            'deptDir': 'vfx',
		            'assetDir': 'asset'}
		
		ctx = ika.context.util.getContext(overrides=ctx_dict)
		
		if not ctx:
			self.report['fail'].append('%s errored, %s' % (char, 'Could not create a context.'))
			return False
		
		latestCtx = ika.context.util.getLatestVersion(ctx)
		
		if not latestCtx:
			self.report['fail'].append('%s errored, %s' % (char, 'Could not get the latest workfile.'))
			return False
			
		workFilePath = latestCtx.getFullPath()
		
		if not os.path.isfile(workFilePath):
			self.report['fail'].append('%s errored, %s, is not a valid path' % (char, workFilePath))
			return False
			
		os.chdir(os.path.split(workFilePath)[0])
		
		return workFilePath
		
	def prepareMayaCmd(self):
		'''
			prepare the command to execute maya
		'''
		self.mayaProcess.append(self.start)
		self.mayaProcess.append(self.mayaVers)
		self.mayaProcess.append(self.optionsFlag)
		self.mayaProcess.append('%s%s' % (self.vfxCodeRoot, self.options.codeRoot))
		self.mayaProcess.append(self.executableFlag)
		self.mayaProcess.append(self.executable)
		self.mayaProcess.append(self.argsFlag)
		self.mayaProcess.append(self.options.pythonFile)
		
		#if self.options.verbose: print self.mayaProcess
		# arguments for python file !!!
	
	'''
	potential method using a dynamic python path !!!
	def jobSubmit(self, workfile, pythonStringPath, name):
		
		pythonStringPath='glTools.show.kbo.fixes.eyebrowClampFix.addEyebrowWrinkleClamp'
		
		funcObj = glTools.nrig.utils.getPyObject( pythonStringPath )
		
		print 'funcObj :: %s' % funcObj
		
		print 'workfile :: %s' % workFile
		
		if workFile.count('wip'):
			args = {'save':True, 'snapshot':False, 'publish':False}
		else:
			args = {'save':True, 'snapshot':True, 'publish':True}
			
		print args
		#glTools.tools.farmSubmit.submit(workFile,'eyebrowClampFix',clampFunc,args)
		print "glTools.tools.farmSubmit.submit(%s, %s, %s, %s)" % (workFile, name, funcObj, args)
		print "submitted job"
	'''
		
		
	def executeMaya(self):
		'''
			execute maya command
		'''
		for char in self.options.chars:
			for subtask in self.options.subtasks:
				
				if self.options.verbose:
					print "Setting env for %s in subtask %s " % (char, subtask)
				
				fullPath = self.setupEnv(char=char, subtask=subtask)
				if not fullPath:
					self.report['fail'].append('%s errored, the environment could not be properly configured. ' % char)
					return False
					
				
				newProcess = self.mayaProcess + [fullPath] 
				if self.options.verbose: print newProcess
				
				'''
				# potential method using a dynamic python path
				self.jobSubmit(workfile=fullPath,
							   pythonStringPath='glTools.show.kbo.fixes.eyebrowClampFix.addEyebrowWrinkleClamp',
							   name='eyeBrowFixTest')
				'''
				subprocess.call(newProcess)
				self.report['pass'].append('%s, Passed, %s process started. ' % (char, subtask) )
					


# execute the main function if called directly
if __name__ == "__main__":
	charFarmManager = CharacterFarmManager()
	charFarmManager.main()
