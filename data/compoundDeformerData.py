import maya.cmds as mc

import glTools.data.utils
import glTools.utils.deformer

class CompoundDeformerData( data.Data ):
	'''
	CompoundDeformerData class object.
	Contains functions to save, load and rebuild ordered deformer data from a specified geometry.
	'''
	
	TYPES = ['mesh','nurbsSurface','nurbsCurve','lattice','particle']
	
	def __init__(self,geo=None):
		'''
		CompoundDeformerData class initializer.
		'''
		# ==================================
		# - Execute Super Class Initilizer -
		# ==================================
		
		super(CompoundDeformerData, self).__init__()
		
		# =========================================
		# - Initialize Default Class Data Members -
		# =========================================
		
		self._data['geo'] = None
		self._data['geoType'] = None
		self._data['deformerData'] = []
		
		# ==============
		# - Build Data -
		# ==============
		
		if geo: self.buildData(geo)
	
	def buildData(self,geo):
		'''
		Build Compound Deformer Data.
		@param geo: Geometry to build Compound Deformer data for
		@type geo: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Geometry
		if not mc.objExists(geo):
			raise Exception('Geometry "'+geo+'" does not exist!')
		geoShapes = mc.ls(mc.listRelatives(geo,s=True,ni=True) or [],type=self.TYPES)
		if not geoShapes:
			raise Exception('Object "'+geo+'" has no valid geometry shapes!')
		
		self._data['geo'] = geo
		self._data['geoType'] = mc.objectType(geoShapes[0])
		
		# ==============
		# - Build Data -
		# ==============
		
		# Start timer
		timer = mc.timerX()
		
		# Get Ordered Deformer List
		deformerList = glTools.utils.deformer.getDeformerList(affectedGeometry=[geo],nodeType='geometryFilter')
		deformerList.reverse()
		
		# Build Deformer Data List
		for deformer in deformerList:
			
			# Check Deformer
			if not glTools.utils.deformer.isDeformer(deformer): continue
			
			# Build Deformer Data
			try:
				deformerData = glTools.data.utils.buildDeformerData(deformer)
				self._data['deformerData'].append(deformerData)
			except Exception, e:
				print('CompoundDeformerData: Error building deformerData for "'+deformer+'"! Skipping...')
				print(str(e))
				continue
		
		# Get Timer Val
		buildTime = mc.timerX(st=timer)
		print('CompoundDeformerData: Data build time for "'+geo+'": '+str(buildTime))
		
		# =================
		# - Return Result -
		# =================
		
		return deformerList
	
	def rebuild(self,deformList=None,overrides={}):
		'''
		Rebuild deformers from the stored deformerData
		@param deformList: LIst of deformer to rebuild. In None, rebuild all.
		@type deformList: list or None
		@param overrides: Dictionary of data overrides to apply.
		@type overrides: dict
		'''
		# Apply Overrides
		self._data.update(overrides)
		
		# ==========
		# - Checks -
		# ==========
		
		# Check Geometry
		geo = self._data['geo']
		if not mc.objExists(geo):
			raise Exception('CompoundDeformerData: Geometry "'+geo+'" does not exist!')
		
		# Check Deformer Data
		if not self._data['deformerData']:
			raise Exception('CompoundDeformerData: No deformerData stored!')
		
		# =====================
		# - Rebuild Deformers -
		# =====================
		
		deformerList = []
		for deformerData in self._data['deformerData']:
			deformer = None
			try: deformer = deformerData.rebuild()
			except Exception, e:
				print(str(e))
				print('CompoundDeformerData: Error loading deformer data for "'+deformerData._data['name']+'"!')
			deformerList.append(deformer)
		
		# =================
		# - Return Result -
		# =================
		
		return deformerList
	
	def deformerList(self):
		'''
		Return the list of deformers stored in the CompoundDeformerData object.
		'''
		deformerList = []
		for deformerData in self._data['deformerData']:
			deformerList.append(deformerData._data['name'])
		return deformerList
