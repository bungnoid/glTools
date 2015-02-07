import maya.cmds as mc

from glTools.utils.weightList import WeightList

import glTools.tools.generateWeights
import glTools.utils.deformer
import glTools.utils.skinCluster


class VolumeWeights(object):
	
	def __init__(self):
	
		self._operationAttrName = 'weightOperation'
		self._operationAttrModes = 'add:subtract:multiply'
		self.radiusAttrName = 'influenceRadius'
		self.affectAttrName = 'affect'
		self.weightTransforms = []
		self.geometry = []
		self.smooth = True
		self.weights = {}
		self.results = {}
		
	        
    #=============================
	# Create Input Transforms
	#=============================
	def createRadiusLocator(self, prefix='', operationMode=0):
			
		falloffLoc = mc.spaceLocator(n='%s_falloffLoc' % prefix)[0]
		influenceVolume = mc.createNode('renderSphere',n='%s_templateFalloffShape' % prefix, p=falloffLoc)
		
		# add attr
		self.addOperationAttr(transform=falloffLoc, operationMode=operationMode)
		
		# Add Radius Control
		locAttrName = '%s.%s' % (falloffLoc, self.radiusAttrName)
		mc.connectAttr(locAttrName, influenceVolume+'.radius',f=True)
		mc.connectAttr(locAttrName, falloffLoc+'.localScaleX',f=True)
		mc.connectAttr(locAttrName, falloffLoc+'.localScaleY',f=True)
		mc.connectAttr(locAttrName, falloffLoc+'.localScaleZ',f=True)
		
		self.weightTransforms.append(falloffLoc)
		
	
	
	        
    #=============================
	# Utilities
	#=============================
	def addOperationAttr(self, transform, operationMode=0):
		
		# radius attr
		if not mc.objExists('%s.%s' % (transform,self.radiusAttrName)):
			mc.addAttr(transform,ln=self.radiusAttrName,min=0.0001,dv=0.5,k=True)
		
		# operation attr
		if not mc.objExists('%s.%s' % (transform,self._operationAttrName)):
			mc.addAttr(transform,ln=self._operationAttrName, attributeType='enum', enumName=self._operationAttrModes,dv=operationMode, keyable=True)
		
		# affect attr
		if not mc.objExists('%s.%s' % (transform,self.affectAttrName)):
			mc.addAttr(transform,ln=self.affectAttrName, attributeType='float', dv=1, keyable=True)
		
	def addGeometry(self, geometry):
		# geometry checks
		self.geometry.append(geometry)
		
	def addTransform(self, transform):
		# transform checks
		self.weightTransforms.append(transform)
		
	def getOperation(self, transform ):
		# attr check
		return mc.getAttr('%s.%s' % (transform, self._operationAttrName))
		
	def getKeyNames(self, geometry):
		return self.weights[geometry].keys()
		
	def normalize(self, geometry, normalizeMin=0, normalizeMax=1):
		if geometry:
			self.weights[geometry].normalize()
		else:
			for geometry in self.geometry: self.weights[geometry].normalize()
		
		
		
		
	        
    #=============================
	# Weights
	#=============================
	def getWeights(self):
		
		for geometry in self.geometry:
			
			self.weights[geometry] = {}
			
			for transform in self.weightTransforms:
				
				self.weights[geometry][transform] =  WeightList(glTools.tools.generateWeights.radialWeights(	geometry = geometry,
																									center	 = transform,
																									radius	 = mc.getAttr('%s.%s' % (transform, self.radiusAttrName)),
																									smooth	 = self.smooth ))
				
				affect = mc.getAttr('%s.%s' % (transform, self.affectAttrName))
				self.weights[geometry][transform] *= affect
				
	def calculateWeights(self, normalize=False, clamp=True):
		
		addWeights = WeightList([])
		subWeights = WeightList([])
		mulWeights = WeightList([])
		for geometry in self.weights.keys():
			
			for transform in self.weights[geometry].keys():
				opNum = self.getOperation(transform)
				if   opNum == 0: addWeights += self.weights[geometry][transform]
				elif opNum == 1: subWeights += self.weights[geometry][transform] 
				elif opNum == 2: mulWeights += self.weights[geometry][transform] 
				
			self.results[geometry] = ( addWeights - subWeights ) * mulWeights
			
			if normalize: self.results[geometry] = self.results[geometry].normalize()
			if clamp:     self.results[geometry] = self.results[geometry].clamp()
	
								
	def apply(self, deformer, influence):
		
		deformType='deformer'
		if mc.nodeType(deformer) == 'skinCluster':
			deformType='skinCluster'
			
		for geometry in self.geometry:
			
			if deformType == 'skinCluster':
				glTools.utils.skinCluster.setInfluenceWeights(skinCluster=deformer,
															influence  =influence,
															weightList = self.results[geometry],
															normalize=True,
															componentList=[])
			else:
				glTools.utils.deformer.setWeights(	deformer	= deformer,
													weights		= self.results[geometry],
													geometry	= geometry)
				
			
	        
    #=============================
	# High Level Methods
	#=============================
	
	def getCalculateAndApply(self, deformer, influence=None, normalize=False, clamp=True):
		
		self.getWeights()
		self.calculateWeights(normalize=normalize, clamp=clamp)
		self.apply(deformer=deformer, influence=influence)
		
		
	
