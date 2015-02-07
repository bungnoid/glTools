import os
import cPickle

import maya.cmds as mc

import glTools.tools.connectionAttrStorage

import data

class GraphConnectionData(data.Data):
	
	def __init__(self, nodeList=[], filePath=None):
		'''
		GraphConnectionData class initializer.
		'''
		# Execute Super Class Initilizer
		super(GraphConnectionData, self).__init__()
		
		self._data['filePath'] = filePath
		self.dataType = 'GraphConnectionData'
		
		self.fileFilter = "All Files (*.*)"

		# Build ChannelData
		if nodeList: self.buildData(nodeList)
		
		self.nodeList = nodeList 
	
	def save(self,filePath,force=False):
		'''
		Save mayaBinary to disk.
		@param filePath: Target file path.
		@type filePath: str
		@param force: Force save if file already exists. (Overwrite).
		@type force: bool
		'''	
		# Check Directory Path
		dirpath = os.path.dirname(filePath)
		if not os.path.isdir(dirpath): os.makedirs(dirpath)
		
		fileWoExtension = filePath.split('.')[0]
		mayaFilePath = '%s.mb' % fileWoExtension
		pklFilePath = '%s.pkl' % fileWoExtension
		
		self._data['filePath'] = mayaFilePath
		
		# Check File Path for .mb file
		if os.path.isfile(mayaFilePath) and not force:
			raise Exception('File "'+mayaFilePath+'" already exists! Use "force=True" to overwrite the existing file.')
		
		# Check File Path for .pkl file
		if os.path.isfile(pklFilePath) and not force:
			raise Exception('File "'+pklFilePath+'" already exists! Use "force=True" to overwrite the existing file.')
		
		# save maya file
		mc.select(cl=True)
		mc.select(self.nodeList)
		mc.file(mayaFilePath, force=force, type="mayaBinary", exportSelected=True, ch=False, channels=False )
		mc.select(cl=True)
		
		# Save pkl File
		fileOut = open(pklFilePath,'wb')
		cPickle.dump(self,fileOut)
		fileOut.close()
		
		# Print Message
		print 'Saved %s : %s' % (self.__class__.__name__, mayaFilePath)
		print 'Saved %s : %s' % (self.__class__.__name__, pklFilePath)
		
	def load(self,filePath=''):
		'''
		Load data mayaBinary from file.
		@param filePath: Target file path
		@type filePath: str
		'''
		# Check File Path
		if not filePath:
			filePath = mc.fileDialog2(fileFilter=self.fileFilter,dialogStyle=2,fileMode=1,caption='Load Graph Connection Maya File',okCaption='Load')
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
		
		self._data = dataIn
		
		# Return Result
		return dataIn
		
	def importFile(self):

		self.mayaFilePath = self._data['filePath']
		print "Loading maya file :: %s" % self.mayaFilePath
		
		# Open File
		try: 
			self.nodeList = mc.file(self.mayaFilePath, type="mayaBinary", i=True, returnNewNodes=True)
		except: 
			raise Exception ("Could not load %s" % self.mayaFilePath)
		
		# Print Message
		print('Loaded "GraphConnectionData" : '+self.mayaFilePath+'"')
		
	def restoreConnections(self):

		if not self.nodeList:
			raise Exception("No nodes specified")
			
		# Start timer
		timer = mc.timerX()
		
		# init ConnectionAttrStorage object
		attrStorage = glTools.tools.connectionAttrStorage.ConnectionAttrStorage()
		
		# Add the nodes from the maya file
		attrStorage.addNodes(self.nodeList)
		
		# get the connection data off the attrs
		attrStorage.getAttrs()
		
		# re-establish connections
		attrStorage.rebuildConnections()
		
		# Print Timer Result
		buildTime = mc.timerX(st=timer)
		print('SetData: Rebuild time : '+str(buildTime))
		
	def rebuild(self):
			
		self.importFile()
		
		self.restoreConnections()
		
		
	def buildData(self,nodeList=None):
		'''
		Build GraphConnectionData class.
		@param nodeList: List of nodes to store connections for.
		@type nodeList: list
		'''		
		# Node List
		if not nodeList:
			print('GraphConnectionData: Empty node list! Unable to build GraphConnectionData!')
			return
			
		# ==============
		# - Build Data -
		# ==============
		
		# Start timer
		timer = mc.timerX()
		
		# Reset Data --- ?
		self.reset()
		
		self.nodeList = nodeList
		
		cas = glTools.tools.connectionAttrStorage.ConnectionAttrStorage()
		
		# set the nodes to operate on
		cas.addNodes(nodeList)
		
		# get the parents
		cas.getParent()
		
		# get connections
		cas.getIncomingConnections()
		cas.getOutgoingConnections()
		
		# Create attributes to store connections
		cas.createAttrs()
		
		# set all the collected data into the attrs
		cas.setAttrs()
		
	
	def reset(self):
		'''
		Reset data object
		'''
		self.__init__()
		
