import maya.cmds as mc

import os.path

import cPickle
#import json

class Data( object ):
	'''
	Base Data Object Class
	Contains functions to save and load standard rig data.
	'''
	
	def __init__(self):
		'''
		Data Object Class Initializer
		'''
		# Initialize Data
		self._data = {}
		
		# Initialize Data Type
		self.dataType = 'Data'
		
		# File Filter
		self.fileFilter = "All Files (*.*)"
	
	def save(self,filePath,force=False):
		'''
		Save data object to file.
		@param filePath: Target file path.
		@type filePath: str
		@param force: Force save if file already exists. (Overwrite).
		@type force: bool
		'''
		# Check Directory Path
		dirpath = os.path.dirname(filePath)
		if not os.path.isdir(dirpath): os.makedirs(dirpath)
		
		# Check File Path
		if os.path.isfile(filePath) and not force:
			raise Exception('File "'+filePath+'" already exists! Use "force=True" to overwrite the existing file.')
		
		# Save File
		fileOut = open(filePath,'wb')
		cPickle.dump(self,fileOut)
		fileOut.close()
		
		# Print Message
		print('Saved '+self.__class__.__name__+': "'+filePath+'"')
		
		# Return Result
		return filePath
	
	def saveAs(self):
		'''
		Save data object to file.
		Opens a file dialog, to allow the user to specify a file path. 
		'''
		# Specify File Path
		filePath = mc.fileDialog2(fileFilter=self.fileFilter,dialogStyle=2,fileMode=0,caption='Save As')
		
		# Check Path
		if not filePath: return
		filePath = filePath[0]
		
		# Save Data File
		filePath = self.save(filePath,force=True)
		
		# Return Result
		return filePath
	
	def load(self,filePath=''):
		'''
		Load data object from file.
		@param filePath: Target file path
		@type filePath: str
		'''
		# Check File Path
		if not filePath:
			filePath = mc.fileDialog2(fileFilter=self.fileFilter,dialogStyle=2,fileMode=1,caption='Load Data File',okCaption='Load')
			if not filePath: return None
			filePath = filePath[0]
		else:
			if not os.path.isfile(filePath):
				raise Exception('File "'+filePath+'" does not exist!')
		
		# Open File
		fileIn = open(filePath,'rb')
		dataIn = cPickle.load(fileIn)
		
		# Print Message
		dataType = dataIn.__class__.__name__
		print('Loaded '+dataType+': "'+filePath+'"')
		
		# Return Result
		return dataIn
	
	def reset(self):
		'''
		Reset data object
		'''
		self.__init__()
