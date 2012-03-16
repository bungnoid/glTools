import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import cPickle

import glTools.utils.arrayUtils
import glTools.utils.component
import glTools.utils.connection
import glTools.utils.deformer

class DeformerData( object ):
	'''
	DeformerData class object.
	Contains functions to save, load and rebuild basic deformer data.
	'''
	def __init__(self,deformer=''):
		'''
		DeformerData class initializer.
		@param deformer: Deformer to initialize data for
		@type deformer: str
		'''
		# Check deformer
		if not deformer: return
		
		# Initialize class data members
		self.deformerName = ''
		self.deformerType = ''
		self.deformerData = {}
		
		# Check deformer
		if not glTools.utils.deformer.isDeformer(deformer):
			raise Exception('Object '+deformer+' is not a valid deformer! Unable to instantiate DeformerData() class!!')
		
		# Get basic deformer info
		self.deformerName = deformer
		self.deformerType = mc.objectType(deformer)
		self.envelope = mc.getAttr(deformer+'.envelope')
		
		# Get geometry affected by deformer
		affectedGeo = glTools.utils.deformer.getAffectedGeometry(deformer,returnShapes=1)
		
		# Build data lists for each affected geometry
		for geo in affectedGeo.iterkeys():
			geo = str(geo)
			self.deformerData[geo] = {}
			self.deformerData[geo]['index'] = affectedGeo[geo]
			self.deformerData[geo]['geometryType'] = str(mc.objectType(geo))
			self.deformerData[geo]['membership'] = glTools.utils.deformer.getDeformerSetMemberIndices(deformer,geo)
			self.deformerData[geo]['weights'] = glTools.utils.deformer.getWeights(deformer,geo)
	
	def save(self,filePath):
		'''
		Save deformer data object to file.
		@param filePath: Target file path
		@type filePath: str
		'''
		fileOut = open(filePath,'wb')
		cPickle.dump(self,fileOut)
		fileOut.close()
	
	def load(self,filePath):
		'''
		Load deformer data object from file.
		@param filePath: Target file path
		@type filePath: str
		'''
		fileIn = open(filePath,'rb')
		return cPickle.load(fileIn)
	
	def getMemberList(self,geoList=[]):
		'''
		Return a list of component member names that can be passed to other functions/methods.
		'''
		# Check geoList
		if not geoList: geoList = self.deformerData.keys()
		
		# Build member component list
		memberList = []
		for geo in geoList:
			
			# Determine component type
			pt = 'cv'
			if self.deformerData[geo]['geometryType'] == 'mesh': pt = 'vtx'
			
			for i in self.deformerData[geo]['membership']: memberList.append(geo+'.'+pt+'['+str(i)+']')
		
		# Return Result
		return memberList
	
	def rebuild(self):
		'''
		Rebuild the deformer from the recorded data
		'''
		# Check target geometry
		for obj in self.deformerData.iterkeys():
			if not mc.objExists(obj): raise Exception('Object '+obj+' does not exist!')
		
		# Rebuild deformer
		deformer = self.deformerName
		if not mc.objExists(deformer):
			deformer = mc.deformer(self.getMemberList(),typ=self.deformerType,n=deformer)[0]
		else:
			self.setDeformerMembership()
		
		# Set cluster weights
		self.loadWeights()
		
		# Set envelope value
		if mc.getAttr(self.deformerName+'.envelope',se=True):
			mc.setAttr(self.deformerName+'.envelope',self.envelope)
		
		# Return result
		return deformer
	
	def setDeformerMembership(self,geoList=[]):
		'''
		'''
		# Check geometry list
		if not geoList: geoList = self.deformerData.keys()
		
		# Check deformer
		deformer = self.deformerName
		if not glTools.utils.deformer.isDeformer(deformer):
			raise Exception('Deformer "'+deformer+'" does not exist!')
		
		# Get deformer set
		deformerSet = glTools.utils.deformer.getDeformerSet(deformer)
		
		for geo in geoList:
			
			# Get current and stored membership
			setMembers = self.deformerData[geo]['membership']
			currMembers = glTools.utils.deformer.getDeformerSetMemberIndices(deformer,geo)
			removeMembers = list(set(currMembers)-set(setMembers))
			
			# Determine component type
			pt = 'cv'
			if self.deformerData[geo]['geometryType'] == 'mesh': pt = 'vtx'
			
			# Remove unused
			if removeMembers:
				mc.sets([geo+'.'+pt+'['+str(i)+']' for i in removeMembers],rm=deformerSet)
			
			# Add remaining members
			mc.sets(self.getMemberList([geo]),fe=deformerSet)
	
	def loadWeights(self,geoList=[]):
		'''
		Load deformer weights for all affected geometry
		'''
		# Check geometry list
		if not geoList: geoList = self.deformerData.keys()
		
		# Check deformer
		deformer = self.deformerName
		if not glTools.utils.deformer.isDeformer(deformer):
			raise Exception('Deformer "'+deformer+'" does not exist!')
			
		for geo in geoList:
			
			# Check geometry
			if not mc.objExists(geo): continue
			if not self.deformerData.has_key(geo):
				raise Exception('No data stored for geometry "'+geo+'"!')
			
			# Get stored weight values
			wt = self.deformerData[geo]['weights']
			
			# Apply defomer weights
			glTools.utils.deformer.setWeights(deformer,wt,geo)
