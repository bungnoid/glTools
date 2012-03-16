import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.common.arrayUtilities
import glTools.common.componentUtilities
import glTools.common.connectionUtilities
import glTools.utils.skinCluster

import multiInfluenceDeformerData

class SkinClusterData( multiInfluenceDeformerData.MultiInfluenceDeformerData ):
	
	def __init__(self,skinCluster=''):
		'''
		SkinClusterData class initilizer.
		'''
		
		# Execute super class initilizer
		#super(SkinClusterData, self).__init__(skinCluster)
		
		# Array Utility Class
		self.arrayUtils = glTools.common.arrayUtilities.ArrayUtilities()
		# Component Utility Class
		self.componentUtils = glTools.common.componentUtilities.ComponentUtilities()
		# Connection Utility Class
		self.connectionUtils = glTools.common.connectionUtilities.ConnectionUtilities()
		
		# Clear influenceData dictionary
		self.influenceData = {}
		
		# Verify node
		if not mc.objExists(skinCluster):
			raise UserInputError('SkinCluster '+skinCluster+' does not exists! No influence data recorded!!')
		if mc.objectType(skinCluster) != 'skinCluster':
			raise UserInputError('Object '+skinCluster+' Is not a vaild skinCluster node! Incorrect class for node type '+self.type+'!!')
			
		# Get skinCluster node
		skinClusterFn = glTools.utils.skinCluster.getSkinClusterFn(skinCluster)
		
		# Get influence array
		influencePathArray = OpenMaya.MDagPathArray()
		numInfluence = skinClusterFn.influenceObjects(influencePathArray)
		
		# Get Affected Geometry
		geomObj = skinClusterFn.outputShapeAtIndex(0)
		geomPath = OpenMaya.MDagPath()
		OpenMaya.MDagPath().getAPathTo(geomObj,geomPath)
		geo = geomPath.partialPathName()
		
		# Get Deformer Membership
		defSet = skinClusterFn.deformerSet()
		deformerSet = OpenMaya.MFnDependencyNode(defSet).name()
		memberIndexList = self.componentUtils.getSingleIndexComponentList(mc.sets(deformerSet,q=True))[geo]
		
		#-------------------#
		# Get Deformer Data #
		#-------------------#
		
		self.deformerName = skinCluster
		self.deformerType = 'skinCluster'
		self.deformerData = {}
		self.deformerData[geo] = {}
		self.deformerData[geo]['index'] = 0
		self.deformerData[geo]['geometryType'] = str(mc.objectType(geo))
		self.deformerData[geo]['membership'] = memberIndexList
		self.deformerData[geo]['weights'] = [1.0 for i in memberIndexList]
		
		#--------------------#
		# Get Influence Data #
		#--------------------#
		
		# Record influence data
		compSel = OpenMaya.MSelectionList()
		compList = OpenMaya.MObject()
		weightArray = OpenMaya.MDoubleArray()
		affectedObjPath = OpenMaya.MDagPath()
		for i in range(numInfluence):
			# Get Influence Name
			inf = influencePathArray[i].partialPathName()
			# Build influence data dictionary
			self.influenceData[inf] = {}
			# Get influence index
			self.influenceData[inf]['index'] = skinClusterFn.indexForInfluenceObject(influencePathArray[i])
			# Get influence weights
			compList = []
			weightArray.clear()
			skinClusterFn.getPointsAffectedByInfluence(influencePathArray[i],compSel,weightArray)
			compSel.getSelectionStrings(compList)
			if compList: compList = mc.ls(compList,fl=True)
			memberIndexList = []
			if compList: memberIndexList = self.componentUtils.getSingleIndexComponentList(compList)[geo]
			# Add influence weight data to influenceData dictionary
			self.influenceData[inf]['membership'] = list(memberIndexList)
			self.influenceData[inf]['weights'] = list(weightArray)
		
		# Influence Base Data
		self.influenceBaseData = self.connectionUtils.connectionListToAttr(skinCluster,'bindPreMatrix')
		
		# Get geomMatrix connections
		self.geomMatrix = mc.listConnections(skinCluster+'.geomMatrix',s=True,d=False,p=True)
		
		# Get additional skinCluster node data
		self.maxInfluences = mc.getAttr(skinCluster+'.maxInfluences')
		self.useMaxInfluences = mc.getAttr(skinCluster+'.maintainMaxInfluences')
	
	def rebuild(self):
		'''
		Rebuild skinCluster deformer from saved deformer data
		'''
		#=========
		# CHECKS
		
		# Check skinCluster
		skinCluster = self.deformerName
		if mc.objExists(skinCluster): raise UserInputError('SkinCluster '+skinCluster+' already exists!')
		# Check geometry
		geometry = self.deformerData.keys()[0]
		if not mc.objExists(geometry): raise UserInputError('Target geometry '+geometry+' does not exist!')
		# Check influences
		for inf in self.influenceData.iterkeys():
			if not mc.objExists(inf): raise UserInputError('Influence transform '+inf+' does not exist!')
		# Check influence bases
		for infBase in self.influenceBaseData.iterkeys():
			if not mc.objExists(infBase): raise UserInputError('Influence base '+infBase+' does not exist!')
		
		#=====================
		# Rebuild skinCluster
		
		# Get Ordered Influence List
		influenceList = self.influenceList()
		# Create skinCluster deformer
		skinCluster = mc.skinCluster(self.getMemberList(),influenceList,tsb=True,dr=1.0,mi=self.maxInfluences,omi=self.useMaxInfluences,n=skinCluster)[0]
		
		# Connect Influence Bases
		for infBase in self.influenceBaseData.iterkeys():
			if mc.objExists(infBase):
				mc.connectAttr(infBase+'.'+self.influenceBaseData[infBase][0],cluster+'.bindPreMatrix['+str(self.influenceBaseData[infBase][1])+']')
		# Connect geomMatrix
		if self.geomMatrix:
			if mc.objExists(self.geomMatrix[0]):
				mc.connectAttr(self.geomMatrix[0],cluster+'.geomMatrix')
		# Load Weights
		self.loadWeights()
	
	def loadWeights(self):
		'''
		Load skinCluster weight values
		'''
		# Check skinCluster
		skinCluster = self.deformerName
		if not mc.objExists(skinCluster): raise UserInputError('SkinCluster '+skinCluster+' does not exist!')
		
		# Check influences
		for inf in self.influenceData.iterkeys():
			if not mc.objExists(inf): raise UserInputError('Influence transform '+inf+' does not exist!')
		
		# Get skinCluster node
		skinClusterFn = glTools.utils.skinCluster.getSkinClusterFn(skinCluster)
		
		# Get skinCluster influence information
		for inf in self.influenceData.iterkeys():
			
			# Build Influence Index Array
			indexList = OpenMaya.MIntArray(1,glTools.utils.skinCluster.getInfluenceIndex(skinCluster,inf))
			# Build Weight Array
			weightList = OpenMaya.MDoubleArray()
			[weightList.append(i) for i in self.influenceData[inf]['weights']]
			
			# Get Geometry and Component objects
			geoPath = OpenMaya.MDagPath()
			compObj = OpenMaya.MObject()
			memberSel = OpenMaya.MSelectionList()
			memberList = self.getInfluenceMemberList(inf)
			if memberList:
				mc.select(self.getInfluenceMemberList(inf))
				OpenMaya.MGlobal.getActiveSelectionList(memberSel)
				memberSel.getDagPath(0,geoPath,compObj)
				# Set Weights
				skinClusterFn.setWeights(geoPath,compObj,indexList,weightList,False)
		
		# Clear Selection
		mc.select(cl=True)
	
	def getInfluenceMemberList(self,influence):
		'''
		Return a list of component member names that can be passed to other functions/methods.
		
		@param influence: Influence of the skinCluster to query
		@type influence: str
		'''
		# Get affected geometry
		geo = self.deformerData.keys()[0]
		# Build member string list
		memberList = []
		pt = 'cv'
		if self.deformerData[geo]['geometryType'] == 'mesh': pt = 'vtx'
		for i in self.influenceData[influence]['membership']:
			memberList.append(geo+'.'+pt+'['+str(i)+']')
		return memberList
	
	def influenceList(self):
		'''
		Return and ordered list of skinCluster influences
		'''
		influenceDict = {}
		for inf in self.influenceData.iterkeys():
			influenceDict[self.influenceData[inf]['index']] = inf
		return self.arrayUtils.dict_orderedValueListFromKeys(influenceDict)
