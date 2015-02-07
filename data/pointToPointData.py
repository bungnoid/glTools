import maya.cmds as mc

import glTools.utils.deformer
import glTools.utils.pointToPoint

import deformerData

class PointToPointData( deformerData.DeformerData ):
	'''
	PointToPoint DeformerData class object.
	'''
	def __init__(self,deformer=''):
		'''
		PointToPoint DeformerData class initializer.
		'''
		# Execute Super Class Initilizer
		super(PointToPointData, self).__init__()
		
		# Deformer Attribute Connections
		self._data['attrConnectionList'].append('targetMesh')
		self._data['attrConnectionList'].append('targetMatrix')
		
		# Imitialize Point Correspondance List
		self._data['pointCorrespondance'] = {}
		
		# Build Data
		if deformer: self.buildData(deformer)
	
	def buildData(self,deformer):
		'''
		Build Deformer Data.
		@param deformer: Deformer to initialize data for
		@type deformer: str
		'''
		# Check Deformer
		if not mc.objectType(deformer) == 'pointToPoint':
			raise Exception('Object "'+pointToPoint+'" is not a valid pointToPoint deformer!')
		
		# Execute Super Class Initilizer
		super(PointToPointData, self).buildData(deformer=deformer)
		
		# Store Point Correspondance
		self._data['pointCorrespondance'] = {}
		for geo in self._data['affectedGeometry']:
			
			# Get Geometry Index
			geomIndex = self._data[geo]['index']
			# Get Point Correspondance
			ptCorr = mc.getAttr(deformer+'.pointCorrespondance['+str(geomIndex)+']')
			# Append to Deformer Data
			self._data['pointCorrespondance'][geo] = ptCorr
		
		# Return Result
		return deformer
	
	def rebuild(self,overrides={}):
		'''
		'''
		# Execute Super Class Initilizer
		pointToPoint = super(PointToPointData, self).rebuild(overrides=overrides)
		
		# Load Point Correspondance
		self.loadPointCorrespondance()
		
		# Return Result
		return pointToPoint
	
	def loadPointCorrespondance(self,geoList=[]):
		'''
		Load deformer point correspondance data
		@param geoList: List of affected geometries to load deformer data for
		@type geoList: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Check Deformer
		deformer = self._data['name']
		if not mc.objExists(deformer):
			raise Exception('PointToPoint deformer "'+deformer+'" does not exist! Unable to load point correspondance data...')
		if not mc.objectType(deformer) == 'pointToPoint':
			raise Exception('Object "'+deformer+'" is not a valid pointToPoint deformer! Unable to load point correspondance data...')
		
		# Check Geometry List
		if not geoList: geoList = self._data['affectedGeometry']
		if not geoList: raise Exception('No affected geometry for pointToPoint deformer "'+deformer+'"! Unable to load point correspondance data...')
		
		# ==================================
		# - Load Point Correspondance Data -
		# ==================================
		
		# Get Affected Geometry
		affectedGeo = glTools.utils.deformer.getAffectedGeometry(deformer,returnShapes=False)
		
		for geo in geoList:
			
			# Check Geometry
			if not geo in affectedGeo:
				print('Geometry "'+geo+'" is not affected by pointToPoint deformer "'+deformer+'"! Skipping...')
				continue
			
			# Check Point Correspondance Data
			if not self._data['pointCorrespondance'].has_key(geo):
				print('No point correspondance data stored for geo "'+geo+'"! Skipping...')
				continue
			
			# Apply Point Correspondance Data
			glTools.utils.pointToPoint.setPointCorrespondance(deformer,geo,self._data['pointCorrespondance'][geo])
		
		# =================
		# - Return Result -
		# =================
		
		return deformer
