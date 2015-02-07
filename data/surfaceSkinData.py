import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.surfaceSkin.utilities

import deformerData

class SurfaceSkinData( deformerData.MultiInfluenceDeformerData ):
	'''
	SurfaceSkinData class object.
	'''
	def __init__(self):
		'''
		SurfaceSkinData class initilizer.
		'''
		# ==================================
		# - Execute Super Class Initilizer -
		# ==================================
		
		super(SurfaceSkinData, self).__init__()
		
		# ===============================
		# - Initialize SurfaceSkin Data -
		# ===============================
		
		# SurfaceSkin Utility Class
		self.surfSkinUtils = glTools.surfaceSkin.utilities.SurfaceSkinUtilities()
		
		self._data['attrValueList'].append('normalizeWeights')
		self._data['attrValueList'].append('useTangentLength')
		self._data['attrValueList'].append('offsetScaleFactor')
	
	def buildData(self,surfaceSkin=''):
		'''
		Build surfaceSkin data and store as class object dictionary entries
		@param surfaceSkin: SurfaceSkin deformer to collect data from
		@type surfaceSkin: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		# SurfaceSkin
		if not surfaceSkin: return
		
		# Verify node
		if not mc.objExists(surfaceSkin):
			raise Exception('SurfaceSkin '+surfaceSkin+' does not exists! No influence data recorded!!')
		objType = mc.objectType(surfaceSkin)
		if objType != 'surfaceSkin':
			raise Exception('Object '+surfaceSkin+' Is not a vaild surfaceSkin node! Incorrect class for node type '+objType+'!!')
		
		# =======================
		# - Build Deformer Data -
		# =======================
		
		super(SurfaceSkinData, self).buildData(surfaceSkin)
		
		# ======================
		# - Get Influence Data -
		# ======================
		
		# Get influence list
		influenceList = self.surfSkinUtils.getInfluenceDict(surfaceSkin)
		
		# Iterate through influences
		for influence in influenceList.iterkeys():
			
			# Get influence index
			infIndex = influenceList[influence][1]
			# Build Influence Data
			self._influenceData[influence] = {}
			self._influenceData[influence]['index'] = infIndex
			self._influenceData[influence]['samplesU'] = mc.getAttr(influence+'.samplesU')
			self._influenceData[influence]['samplesV'] = mc.getAttr(influence+'.samplesV')
			self._influenceData[influence]['tangentAlign'] = mc.getAttr(influence+'.tangentAlign')
			self._influenceData[influence]['base'] = self.surfSkinUtils.getInfluenceBase(influence)
			self._influenceData[influence]['transformInfluence'] = self.surfSkinUtils.isTransformInfluence(influence,surfaceSkin)
			self._influenceData[influence]['membership'] = {}
			self._influenceData[influence]['weights'] = {}
			self._influenceData[influence]['uCoord'] = {}
			self._influenceData[influence]['vCoord'] = {}
			
			# Iterate through affected geometry
			for geo in self._data['affectedGeometry']:
				
				# Get geometry index
				geoIndex = self._data[geo]['index']
				# Get influence data arrays
				self._influenceData[influence]['membership'][geo] = mc.getAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].index')
				self._influenceData[influence]['weights'][geo] = mc.getAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].influenceWeight')
				self._influenceData[influence]['uCoord'][geo] = mc.getAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].uCoord')
				self._influenceData[influence]['vCoord'][geo] = mc.getAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].vCoord')
	
	def rebuild(self):
		'''
		Rebuild surfaceSkin deformer from saved deformer data
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Check surfaceSkin
		surfaceSkin = self._data['name']
		if mc.objExists(surfaceSkin): raise Exception('SurfaceSkin '+surfaceSkin+' already exists!')
		
		# Check geometry
		for geometry in self._data['affectedGeometry']:
			if not mc.objExists(geometry): raise Exception('Target geometry '+geometry+' does not exist!')
		
		# Check influences
		for inf in self._influenceData.iterkeys():
			if not mc.objExists(inf): raise Exception('Influence '+inf+' does not exist!')
		
		# =======================
		# - Rebuild surfaceSkin -
		# =======================
		
		# Get Ordered Influence List
		influenceList = self.influenceList()
		
		# Create surfaceSkin deformer
		surfaceSkin = self.surfSkinUtils.create(self.getMemberList(),[influenceList[0]],0.0,0.001,name=surfaceSkin)
		
		# Attach influences
		for i in range(len(influenceList)):
			if not i: continue
			if self._influenceData[influenceList[i]]['transformInfluence']:
				self.surfSkinUtils.addTransformInfluence([influenceList[i]],surfaceSkin,0.0,0.001)
			else:
				self.surfSkinUtils.addInfluence([influenceList[i]],surfaceSkin,0.0,0.001)
		
		# =======================
		# - Load Influence Data -
		# =======================
		
		# Load Weights
		self.loadWeights()
		# Load Influence Data
		self.loadInfluenceData()
		
		# Restore Custom Attribute Values and Connections
		self.setDeformerAttrValues()
		self.setDeformerAttrConnections()
	
	def loadInfluenceData(self):
		'''
		Load surfaceSkin influence data values
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Check surfaceSkin
		surfaceSkin = self._data['name']
		if not mc.objExists(surfaceSkin): raise Exception('SurfaceSkin '+surfaceSkin+' does not exist!')
		
		# Check influences
		for inf in self._influenceData.iterkeys():
			if not mc.objExists(inf): raise Exception('Influence transform '+inf+' does not exist!')
		
		# =======================
		# - Load Influence Data -
		# =======================
		
		# Iterate over influences
		for influence in self._influenceData.iterkeys():
			# Get influence index
			infIndex = self.surfSkinUtils.getInfluenceIndex(influence,surfaceSkin)
			# Apply influence data
			mc.setAttr(influence+'.samplesU',self._influenceData[influence]['samplesU'])
			mc.setAttr(influence+'.samplesV',self._influenceData[influence]['samplesV'])
			mc.setAttr(influence+'.tangentAlign',self._influenceData[influence]['tangentAlign'])
			
			# Iterate over geometry
			for geo in self._data['affectedGeometry']:
				# Get geometry index
				geoIndex = self._data[geo]['index']
				# Apply influence data
				mc.setAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].index',self._influenceData[influence]['membership'][geo],type='Int32Array')
				mc.setAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].influenceWeight',self._influenceData[influence]['weights'][geo],type='doubleArray')
				mc.setAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].uCoord',self._influenceData[influence]['uCoord'][geo],type='doubleArray')
				mc.setAttr(surfaceSkin+'.idl['+str(geoIndex)+'].id['+str(infIndex)+'].vCoord',self._influenceData[influence]['vCoord'][geo],type='doubleArray')
	
	def influenceList(self):
		'''
		Return an ordered list of surfaceSkin influences
		'''
		influenceDict = {}
		for inf in self._influenceData.iterkeys():
			influenceDict[self._influenceData[inf]['index']] = inf
		return [ influenceDict[key] for key in sorted(influenceDict.keys()) ]
