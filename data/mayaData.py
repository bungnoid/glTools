import maya.cmds as mc

import os.path

import data

class MayaData( data.Data ):
	'''
	Maya Data Object Class
	Contains functions to save and load standard maya data.
	'''
	
	def __init__(self):
		'''
		Data Object Class Initializer
		'''
		# Execute Super Class Initilizer
		super(MayaData, self).__init__()
		
		# Initialize Data Type
		self.dataType = 'MayaData'
		
		# File Filter
		self.fileFilter = "All Files (*.*)"
	
	def saveAs(self):
		'''
		Save data object to file.
		Opens a file dialog, to allow the user to specify a file path. 
		'''
		# Specify File Path
		filePath = mc.fileDialog2(fileFilter=self.fileFilter,dialogStyle=2,caption='Save As')
		
		# Check Path
		if not filePath: return
		filePath = filePath[0]
		
		# Save Data File
		self.save(filePath,force=True)
		
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
			if not filePath: return
			filePath = filePath[0]
		else:
			if not os.path.isfile(filePath):
				raise Exception('File "'+filePath+'" does not exist!')
		
		# Open File
		dataIn = super(MayaData, self).load(filePath)
		
		# Return Result
		return dataIn
	

