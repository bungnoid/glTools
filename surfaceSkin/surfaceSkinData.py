import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.arrayUtils
import glTools.surfaceSkin.utilities

from glTools.data import multiInfluenceDeformerData

class SurfaceSkinData( multiInfluenceDeformerData.MultiInfluenceDeformerData ):
	'''
	SurfaceSkinData class object.
	'''
	# INIT
	def __init__(self,surfaceSkin=''):
		'''
		SurfaceSkinData class initilizer.
		'''
		# Escape
		if not surfaceSkin: return
		
		# Verify node
		if not mc.objExists(surfaceSkin):
			raise UserInputError('SurfaceSkin '+surfaceSkin+' does not exists! No influence data recorded!!')
		objType = mc.objectType(surfaceSkin)
		if objType != 'surfaceSkin':
			raise UserInputError('Object '+surfaceSkin+' Is not a vaild surfaceSkin node! Incorrect class for node type '+objType+'!!')
		
		# Execute super class initilizer
		super(SurfaceSkinData, self).__init__(surfaceSkin)
		
		# SurfaceSkin Utility Class
		self.surfSkinUtils = glTools.surfaceSkin.utils.SurfaceSkinUtilities()
		
		#===================
		# Get Deformer Data
		self.normalizeWeights = mc.getAttr(surfaceSkin+'.normalizeWeights')
		self.useTangentLength = mc.getAttr(surfaceSkin+'.useTangentLength')
		self.offsetScaleFactor = mc.getAttr(surfaceSkin+'.offsetScaleFactor')
		
		#====================
		# Get Influence Data
		self.influenceData = {}
		
		# Get influence list
		influenceList = self.surfSkinUtils.getInfluenceList(surfaceSkin)
		
		# Iterate through influences
		for influence in influenceList.iterkeys():
			
			# Get influence index
			infIndex = influenceList[influence][1]
			# Build Influence Data
			self.influenceData[influence] = {}
			self.influenceData[influence]['index'] = infIndex
			self.influenceData[influence]['samplesU'] = mc.getAttr(influence+'.samplesU')
			self.influenceData[influence]['samplesV'] = mc.getAttr(influence+'.samplesV')
			self.influenceData[influence]['tangentAlign'] = mc.getAttr(influence+'.tangentAlign')
			self.influenceData[influence]['base'] = self.surfSkinUtils.getInfluenceBase(influence)
			self.influenceData[influence]['transformInfluence'] = self.surfSkinUtils.isTransformInfluence(influence,surfaceSkin)
			self.influenceData[influence]['membership'] = {}
			self.influenceData[influence]['weights'] = {}
			self.influenceData[influence]['uCoord'] = {}
			self.influenceData[influence]['vCoord'] = {}
			
			# Iterate through affected geometry
			for geo in self.deformerData.iterkeys():
				
				# Get geometry index
				geoIndex = self.deformerData[geo]['index']
				# Get influence data arrays
				self.influenceData[influence]['membership'][geo] = mc.getAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].index')
				self.influenceData[influence]['weights'][geo] = mc.getAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].influenceWeight')
				self.influenceData[influence]['uCoord'][geo] = mc.getAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].uCoord')
				self.influenceData[influence]['vCoord'][geo] = mc.getAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].vCoord')
	
	def rebuild(self):
		'''
		Rebuild surfaceSkin deformer from saved deformer data
		'''
		#=========
		# CHECKS
		
		# Check surfaceSkin
		surfaceSkin = self.deformerName
		if mc.objExists(surfaceSkin): raise UserInputError('SurfaceSkin '+surfaceSkin+' already exists!')
		# Check geometry
		for geometry in self.deformerData.iterkeys():
			if not mc.objExists(geometry): raise UserInputError('Target geometry '+geometry+' does not exist!')
		# Check influences
		for inf in self.influenceData.iterkeys():
			if not mc.objExists(inf): raise UserInputError('Influence '+inf+' does not exist!')
			# Check influence bases
			infBase = self.influenceData[inf]['base']
			if not mc.objExists(infBase): raise UserInputError('Influence base '+infBase+' does not exist!')
			if self.surfSkinUtils.getInfluenceBase(inf) != infBase:
				self.surfSkinUtils.connectBase(inf,infBase)
		
		#=====================
		# Rebuild surfaceSkin
		
		# Get Ordered Influence List
		influenceList = self.influenceList()
		
		# Create surfaceSkin deformer
		surfaceSkin = self.surfSkinUtils.create(self.getMemberList(),influenceList[0:1],0.0,0.001,name=self.deformerName)
		# Attach influences
		for i in range(len(influenceList)):
			if not i: continue
			if self.influenceData[influenceList[i]]['transformInfluence']:
				self.surfSkinUtils.addTransformInfluence([influenceList[i]],0.0,0.001,surfaceSkin)
			else:
				self.surfSkinUtils.addInfluence([influenceList[i]],0.0,0.001,surfaceSkin)
		
		# Set envelope value
		if mc.getAttr(surfaceSkin+'.envelope',se=True):
			mc.setAttr(surfaceSkin+'.envelope',self.envelope)
		# Set deformer attribute values
		mc.setAttr(surfaceSkin+'.normalizeWeights',self.normalizeWeights)
		mc.setAttr(surfaceSkin+'.useTangentLength',self.useTangentLength)
		mc.setAttr(surfaceSkin+'.offsetScaleFactor',self.offsetScaleFactor)
		
		# Load Weights
		self.loadWeights()
		# Load Influence Data
		self.loadInfluenceData()
	
	def loadInfluenceData(self):
		'''
		Load surfaceSkin influence data values
		'''
		# Check surfaceSkin
		surfaceSkin = self.deformerName
		if not mc.objExists(surfaceSkin): raise UserInputError('SurfaceSkin '+surfaceSkin+' does not exist!')
		
		# Check influences
		for inf in self.influenceData.iterkeys():
			if not mc.objExists(inf): raise UserInputError('Influence transform '+inf+' does not exist!')
		
		# Iterate over influences
		for influence in self.influenceData.iterkeys():
			# Get influence index
			infIndex = self.surfSkinUtils.getInfluenceIndex(influence,surfaceSkin)
			# Apply influence data
			mc.setAttr(influence+'.samplesU',self.influenceData[influence]['samplesU'])
			mc.setAttr(influence+'.samplesV',self.influenceData[influence]['samplesV'])
			mc.setAttr(influence+'.tangentAlign',self.influenceData[influence]['tangentAlign'])
			
			# Iterate over geometry
			for geo in self.deformerData.iterkeys():
				# Get geometry index
				geoIndex = self.deformerData[geo]['index']
				# Apply influence data
				mc.setAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].index',self.influenceData[influence]['membership'][geo],type='Int32Array')
				mc.setAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].influenceWeight',self.influenceData[influence]['weights'][geo],type='doubleArray')
				mc.setAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].uCoord',self.influenceData[influence]['uCoord'][geo],type='doubleArray')
				mc.setAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].vCoord',self.influenceData[influence]['vCoord'][geo],type='doubleArray')
	
	def affectedGeometryList(self):
		'''
		Return an ordered list of the geometry affected by the surfaceSkin deformer
		'''
		geometryDict = {}
		for geo in self.deformerData.iterkeys():
			geometryDict[self.deformerData[geo]['index']] = geo
		return self.arrayUtils.dict_orderedValueListFromKeys(geometryDict)
	
	def influenceList(self):
		'''
		Return an ordered list of surfaceSkin influences
		'''
		influenceDict = {}
		for inf in self.influenceData.iterkeys():
			influenceDict[self.influenceData[inf]['index']] = inf
		return self.arrayUtils.dict_orderedValueListFromKeys(influenceDict)
