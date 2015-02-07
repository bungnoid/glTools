import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.utils.arrayUtils
import glTools.utils.deformer
import glTools.utils.mesh
import glTools.utils.progressBar

import data
import meshData

import copy

class DeformerData( data.Data ):
	'''
	DeformerData class object.
	Contains functions to save, load and rebuild basic deformer data.
	'''
	def __init__(self,deformer=''):
		'''
		DeformerData class initializer.
		'''
		# ==================================
		# - Execute Super Class Initilizer -
		# ==================================
		
		super(DeformerData, self).__init__()
		
		# =========================================
		# - Initialize Default Class Data Members -
		# =========================================
		
		# Common Deformer Data
		self._data['name'] = ''
		self._data['type'] = ''
		self._data['affectedGeometry'] = []
		
		# Deformer Attribute - Definition
		self._data['attrValueList'] = ['envelope']
		self._data['attrConnectionList'] = []
		
		# Deformer Attribute - Storage
		self._data['attrValueDict'] = {}
		self._data['attrConnectionDict'] = {}
		
		# Build Data
		if deformer: self.buildData(deformer)
	
	def buildData(self,deformer):
		'''
		Build Deformer Data.
		@param deformer: Deformer to initialize data for
		@type deformer: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Deformer
		if not deformer: return
		if not glTools.utils.deformer.isDeformer(deformer):
			raise Exception('Object '+deformer+' is not a valid deformer! Unable to instantiate DeformerData() class object!')
		
		# ==============
		# - Build Data -
		# ==============
		
		# Start timer
		timer = mc.timerX()
		
		# Reset Data Object - (Maintain Incoming Attribute Lists)
		attrValueList = copy.deepcopy(self._data['attrValueList'])
		attrConnectionList = copy.deepcopy(self._data['attrConnectionList'])
		self.reset()
		self._data['attrValueList'] = copy.deepcopy(attrValueList)
		self._data['attrConnectionList'] = copy.deepcopy(attrConnectionList)
		
		# Get basic deformer info
		self._data['name'] = deformer
		self._data['type'] = mc.objectType(deformer)
		
		# Get geometry affected by deformer
		affectedGeo = glTools.utils.deformer.getAffectedGeometry(deformer,returnShapes=False)
		self._data['affectedGeometry'] = [str(i) for i in glTools.utils.arrayUtils.dict_orderedKeyListFromValues(affectedGeo)]
		
		# Build data lists for each affected geometry
		for geo in self._data['affectedGeometry']:
			geoShape = mc.listRelatives(geo,s=True,ni=True,pa=True)[0]
			self._data[geo] = {}
			self._data[geo]['index'] = affectedGeo[geo]
			self._data[geo]['geometryType'] = str(mc.objectType(geoShape))
			self._data[geo]['membership'] = glTools.utils.deformer.getDeformerSetMemberIndices(deformer,geo)
			self._data[geo]['weights'] = glTools.utils.deformer.getWeights(deformer,geo)
			
			if self._data[geo]['geometryType'] == 'mesh':
				self._data[geo]['mesh'] = meshData.MeshData(geo)
		
		# =========================
		# - Custom Attribute Data -
		# =========================
		
		# Add Pre-Defined Custom Attributes
		self.customDeformerAttributes(self._data['type'])
		self.getDeformerAttrValues()
		self.getDeformerAttrConnections()
		
		# Get Timer Val
		buildTime = mc.timerX(st=timer)
		print('DeformerData: Data build time for "'+deformer+'": '+str(buildTime))
		
		# =================
		# - Return Result -
		# =================
		
		return deformer
	
	def rebuild(self,overrides={}):
		'''
		Rebuild the deformer from the stored deformerData
		@param overrides: Dictionary of data overrides to apply 
		@type overrides: dict
		'''
		# Apply Overrides
		self._data.update(overrides)
		
		# ==========
		# - Checks -
		# ==========
		
		# Check target geometry
		for geo in self._data['affectedGeometry']:
			if not mc.objExists(geo):
				raise Exception('Deformer ('+self._data['name']+') affected geometry "'+geo+'" does not exist!')
		
		# ====================
		# - Rebuild Deformer -
		# ====================
		
		# Start timer
		timer = mc.timerX()
		
		deformer = self._data['name']
		if not mc.objExists(self._data['name']):
			deformer = mc.deformer(self.getMemberList(),typ=self._data['type'],n=deformer)[0]
		else:
			self.setDeformerMembership()
		
		# Set deformer weights
		self.loadWeights()
		
		# ================================
		# - Set Deformer Attribute Values -
		# ================================
		
		self.setDeformerAttrValues()
		self.setDeformerAttrConnections()
		
		# =================
		# - Return Result -
		# =================
		
		# Print Timed Result
		totalTime = mc.timerX(st=timer)
		print(self.__class__.__name__+': Rebuild time for deformer "'+deformer+'": '+str(totalTime))
		
		return deformer
	
	def rename(self,name):
		'''
		Rename deformer
		@param name: New name for deformer 
		@type name: str
		'''
		# Rename Deformer
		self._data['name'] = name
		
		# Return Result
		return self._data['name']
	
	def remapGeometry(self,oldGeometry,newGeometry):
		'''
		Remap the stored deformer data from one geometry to another.
		@param oldGeo: The geometry to remap the deformer data from
		@type oldGeo: str
		@param newGeo: The geometry to remap the deformer data to
		@type newGeo: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		if self._data.has_key(newGeometry):
			raise Exception('Deformer data for "'+newGeometry+'" already exists!!')
		if not self._data.has_key(oldGeometry):
			raise Exception('No deformer data stored for geometry "'+oldGeometry+'"!!')
		
		# ==================
		# - Remap Geometry -
		# ==================
		
		self._data[newGeometry] = self._data[oldGeometry]
		self._data.pop(oldGeometry)
		
		# Update Affected Geometry List
		oldGeometryId = self._data['affectedGeometry'].index(oldGeometry)
		self._data['affectedGeometry'][oldGeometryId] = newGeometry
		
		# =================
		# - Return Result -
		# =================
		
		return newGeometry
	
	def getMemberList(self,geoList=[]):
		'''
		Return a list of component member names that can be passed to other functions/methods.
		@param geoList: List of affected geometries to get membership data for
		@type geoList: str
		'''
		# Check geoList
		if not geoList:
			geoList = self._data['affectedGeometry']
		
		# Build member component list
		memberList = []
		for geo in geoList:
			
			# Mesh
			if self._data[geo]['geometryType'] == 'mesh':
				if not self._data[geo]['membership']:
					memberList.append(geo+'.vtx[*]')
				else:
					for i in self._data[geo]['membership']:
						memberList.append(geo+'.vtx['+str(i)+']')
			
			# Curve
			if self._data[geo]['geometryType'] == 'nurbsCurve':
				if not self._data[geo]['membership']:
					memberList.append(geo+'.cv[*]')
				else:
					for i in self._data[geo]['membership']:
						memberList.append(geo+'.cv['+str(i)+']')
			
			# Particle
			if self._data[geo]['geometryType'] == 'particle':
				if not self._data[geo]['membership']:
					memberList.append(geo+'.pt[*]')
				else:
					for i in self._data[geo]['membership']:
						memberList.append(geo+'.pt['+str(i)+']')
			
			# Surface
			if self._data[geo]['geometryType'] == 'nurbsSurface':
				if not self._data[geo]['membership']:
					memberList.append(geo+'.cv[*][*]')
				else:
					for i in self._data[geo]['membership']:
						memberList.append(geo+'.cv['+str(i[0])+']['+str(i[1])+']')
			
			# Lattice
			if self._data[geo]['geometryType'] == 'lattice':
				if not self._data[geo]['membership']:
					memberList.append(geo+'.pt[*][*][*]')
				else:
					for i in self._data[geo]['membership']:
						memberList.append(geo+'.pt['+str(i[0])+']['+str(i[1])+']['+str(i[2])+']')
		
		# Return Result
		return memberList
	
	def setDeformerMembership(self,geoList=[]):
		'''
		Set deformer membership based on stored deformerData.
		@param geoList: List of affected geometries to set deformer membership for
		@type geoList: str
		'''
		
		# ==========
		# - Checks -
		# ==========
		
		# Check geometry list
		if not geoList: geoList = self._data['affectedGeometry']
		
		# Check deformer
		deformer = self._data['name']
		if not mc.objExists(deformer):
			raise Exception('Deformer "'+deformer+'" does not exist!')
		if not glTools.utils.deformer.isDeformer(deformer):
			raise Exception('Object "'+deformer+'" is not a valid deformer!')
		
		# =========================
		# - Get Deformer Set Data -
		# =========================
		
		deformerSet = glTools.utils.deformer.getDeformerSet(deformer)
		
		for geo in geoList:
			
			# Get Current and Stored Member Data
			setMembers = self._data[geo]['membership']
			currMembers = glTools.utils.deformer.getDeformerSetMemberIndices(deformer,geo)
			removeMembers = [i for i in currMembers if not setMembers.count(i)]
			
			# =========================
			# - Remove Unused Members -
			# =========================
			
			if removeMembers:
				
				# Mesh
				if self._data[geo]['geometryType'] == 'mesh':
					mc.sets([geo+'.vtx['+str(i)+']' for i in removeMembers],rm=deformerSet)
				# Curve
				if self._data[geo]['geometryType'] == 'nurbsCurve':
					mc.sets([geo+'.cv['+str(i)+']' for i in removeMembers],rm=deformerSet)
				# Particle
				if self._data[geo]['geometryType'] == 'particle':
					mc.sets([geo+'.pt['+str(i)+']' for i in removeMembers],rm=deformerSet)
				# Surface
				if self._data[geo]['geometryType'] == 'nurbsSurface':
					mc.sets([geo+'.cv['+str(i[0])+']['+str(i[1])+']' for i in removeMembers],rm=deformerSet)
				# Lattice
				if self._data[geo]['geometryType'] == 'lattice':
					mc.sets([geo+'.pt['+str(i[0])+']['+str(i[1])+']['+str(i[2])+']' for i in removeMembers],rm=deformerSet)
			
			# =========================
			# - Add Remaining Members -
			# =========================
			
			mc.sets(self.getMemberList([geo]),fe=deformerSet)
	
	def loadWeights(self,geoList=[]):
		'''
		Load deformer weights for all affected geometry
		@param geoList: List of affected geometries to load deformer weights for
		@type geoList: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Check Geometry List
		if not geoList: geoList = self._data['affectedGeometry']
		
		# Check Deformer
		deformer = self._data['name']
		if not mc.objExists(deformer):
			raise Exception('Deformer "'+deformer+'" does not exist!')
		if not glTools.utils.deformer.isDeformer(deformer):
			raise Exception('Object "'+deformer+'" is not a valid deformer!')
		
		# =========================
		# - Load Deformer Weights -
		# =========================
			
		for geo in geoList:
			
			# Check Geometry
			if not mc.objExists(geo):
				print('Geometry "'+geo+'" does not exist! Skipping...')
				continue
			if not self._data.has_key(geo):
				print('No data stored for geometry "'+geo+'"! Skipping...')
				continue
			
			# Get stored weight values
			wt = self._data[geo]['weights']
			
			# Apply defomer weights
			glTools.utils.deformer.setWeights(deformer,wt,geo)
	
	def mirrorWeights():
		'''
		'''
		pass
	
	def flipWeights():
		'''
		'''
		pass
	
	def rebuildMeshFromData(self,mesh):
		'''
		Rebuild the specified mesh from the stored deformer data
		@param mesh: Mesh to rebuild geometry from data for. 
		@type mesh: str
		'''
		# Checks Mesh Data
		if not self._data.has_key(mesh):
			raise Exception('No data stored for mesh "'+mesh+'"!')
		
		# Rebuild Mesh
		mesh = self._data[mesh]['mesh'].rebuildMesh()
		
		# Return Result
		return mesh
	
	def rebuildMeshData(self,mesh,sourceMesh=''):
		'''
		Rebuild the mesh data for the specified mesh.
		@param mesh: Mesh to rebuild geometry from data for. 
		@type mesh: str
		@param sourceMesh: The source mesh to rebuild the data from. 
		@type sourceMesh: str
		'''
		# Check Source Mesh
		if not sourceMesh: sourceMesh = mesh
		if not mc.objExists(sourceMesh):
			raise Exception('Source mesh "'+sourceMesh+'" does not exist! Unable to rebuild mesh data...')
		
		# Checks Mesh Data
		if not self._data.has_key(mesh):
			raise Exception('No data stored for mesh "'+mesh+'"!')
		
		# Rebuild Mesh Data
		mesh = self._data[mesh]['mesh'].buildData(sourceMesh)
	
	def rebuildWorldSpaceData(self,sourceGeo,targetGeo='',method='closestPoint'):
		'''
		Rebuild the deformer membership and weight arrays for the specified geometry using the stored world space geometry data.
		@param sourceGeo: Geometry to rebuild world space deformer data from.
		@type sourceGeo: str
		@param targetGeo: Geometry to rebuild world space deformer data for. If empty, use sourceGeo.
		@type targetGeo: str
		@param method: Method for worldSpace transfer. Valid options are "closestPoint" and "normalProject".
		@type method: str
		'''
		# Start timer
		timer = mc.timerX()
		
		# Display Progress
		glTools.utils.progressBar.init(status=('Rebuilding world space deformer data...'),maxValue=100)
		
		# ==========
		# - Checks -
		# ==========
		
		# Target Geometry
		if not targetGeo: targetGeo = sourceGeo
		
		# Check Deformer Data
		if not self._data.has_key(sourceGeo):
			raise Exception('No deformer data stored for geometry "'+sourceGeo+'"!')
		
		# Check Geometry
		if not mc.objExists(targetGeo):
			raise Exception('Geometry "'+targetGeo+'" does not exist!')
		if not glTools.utils.mesh.isMesh(targetGeo):
			raise Exception('Geometry "'+targetGeo+'" is not a valid mesh!')
		
		# Check Mesh Data
		if not self._data[sourceGeo].has_key('mesh'):
			raise Exception('No world space mesh data stored for mesh geometry "'+sourceGeo+'"!')
		
		# =====================
		# - Rebuild Mesh Data -
		# =====================
		
		meshData = self._data[sourceGeo]['mesh']._data
		
		meshUtil = OpenMaya.MScriptUtil()
		numVertices = len(meshData['vertexList'])/3
		numPolygons = len(meshData['polyCounts'])
		polygonCounts = OpenMaya.MIntArray()
		polygonConnects = OpenMaya.MIntArray()
		meshUtil.createIntArrayFromList(meshData['polyCounts'],polygonCounts)
		meshUtil.createIntArrayFromList(meshData['polyConnects'],polygonConnects)
		
		# Rebuild Vertex Array
		vertexArray = OpenMaya.MFloatPointArray(numVertices,OpenMaya.MFloatPoint.origin)
		vertexList = [vertexArray.set(i,meshData['vertexList'][i*3],meshData['vertexList'][i*3+1],meshData['vertexList'][i*3+2],1.0) for i in xrange(numVertices)]
		
		# Rebuild Mesh
		meshFn = OpenMaya.MFnMesh()
		meshDataFn = OpenMaya.MFnMeshData().create()
		meshObj = meshFn.create(numVertices,numPolygons,vertexArray,polygonCounts,polygonConnects,meshDataFn)
		
		# Create Mesh Intersector
		meshPt = OpenMaya.MPointOnMesh()
		meshIntersector = OpenMaya.MMeshIntersector()
		if method == 'closestPoint': meshIntersector.create(meshObj)
		
		# ========================================
		# - Rebuild Weights and Membership List -
		# ========================================
		
		# Initialize Influence Weights and Membership
		new_weights = []
		new_membership = []
		
		# Get Target Mesh Data
		targetMeshFn = glTools.utils.mesh.getMeshFn(targetGeo)
		targetMeshPts = targetMeshFn.getRawPoints()
		numTargetVerts = targetMeshFn.numVertices()
		targetPtUtil = OpenMaya.MScriptUtil()
		
		# Initialize Float Pointers for Barycentric Coords
		uUtil = OpenMaya.MScriptUtil()
		vUtil = OpenMaya.MScriptUtil()
		uPtr = uUtil.asFloatPtr()
		vPtr = vUtil.asFloatPtr()
		
		# Get Progress Step
		progressInd = int(numTargetVerts*0.01)
		
		for i in range(numTargetVerts):
			
			# Get Target Point
			targetPt = OpenMaya.MPoint(	targetPtUtil.getFloatArrayItem(targetMeshPts,(i*3)+0),
										targetPtUtil.getFloatArrayItem(targetMeshPts,(i*3)+1),
										targetPtUtil.getFloatArrayItem(targetMeshPts,(i*3)+2)	)
			
			# Get Closest Point Data
			meshIntersector.getClosestPoint(targetPt,meshPt)
			
			# Get Barycentric Coords
			meshPt.getBarycentricCoords(uPtr,vPtr)
			u = OpenMaya.MScriptUtil(uPtr).asFloat()
			v = OpenMaya.MScriptUtil(vPtr).asFloat()
			baryWt = [u,v,1.0-(u+v)]
			
			# Get Triangle Vertex IDs
			idUtil = OpenMaya.MScriptUtil()
			idPtr = idUtil.asIntPtr()
			meshFn.getPolygonTriangleVertices(meshPt.faceIndex(),meshPt.triangleIndex(),idPtr)
			
			# Calculate Weight and Membership
			wt = 0.0
			isMember = False
			for n in range(3):
				
				# Get Triangle Vertex ID
				triId = OpenMaya.MScriptUtil().getIntArrayItem(idPtr,n)
				
				# Check Against Source Membership
				if self._data[sourceGeo]['membership'].count(triId):
					wtId = self._data[sourceGeo]['membership'].index(triId)
					wt += self._data[sourceGeo]['weights'][wtId] * baryWt[n]
					isMember = True
			
			# Check Weight
			if isMember:
				new_weights.append(wt)
				new_membership.append(i)
				
			# Update Progress Bar
			if not i % progressInd: glTools.utils.progressBar.update(step=1)
		
		# ========================
		# - Update Deformer Data -
		# ========================
		
		self._data[sourceGeo]['membership'] = new_membership
		self._data[sourceGeo]['weights'] = new_weights
		
		# =================
		# - Return Result -
		# =================
		
		# End Progress
		glTools.utils.progressBar.end()	
		
		# Print Timed Result
		buildTime = mc.timerX(st=timer)
		print('DeformerData: Rebuild world space data for deformer "'+self._data['name']+'": '+str(buildTime))
		
		# Return Weights
		return new_weights
	
	def getDeformerAttrValues(self):
		'''
		Get deformer attribute values based on the specified deformer attribute list. 
		'''
		deformer = self._data['name']
		# Get Custom Attribute Values
		for attr in self._data['attrValueList']:
			if not mc.getAttr(deformer+'.'+attr,se=True) and mc.listConnections(deformer+'.'+attr,s=True,d=False):
				self._data['attrConnectionList'].append(attr)
			else:
				self._data['attrValueDict'][attr] = mc.getAttr(deformer+'.'+attr)
	
	def getDeformerAttrConnections(self):
		'''
		Get custom (non-standard) deformer attribute connections based on the specified deformer connection list.
		'''
		deformer = self._data['name']
		# Get Custom Attribute Connections
		for attr in self._data['attrConnectionList']:
			attrConn = mc.listConnections(deformer+'.'+attr,s=True,d=False,p=True,sh=True,skipConversionNodes=True)
			if attrConn: self._data['attrConnectionDict'][attr] = attrConn[0]
	
	def setDeformerAttrValues(self):
		'''
		Set deformer attribute values based on the stored deformer attribute data. 
		'''
		# ===============================
		# - Set Custom Attribute Values -
		# ===============================
		
		for attr in self._data['attrValueDict'].iterkeys():
			
			# Define Deformer Attribute
			deformerAttr = self._data['name']+'.'+attr
			
			# Check attribute exists
			if not mc.objExists(deformerAttr):
				print('Deformer attribute "'+deformerAttr+'" does not exist! Skipping...')
				continue
			
			# Check attribute is settable
			if not mc.getAttr(deformerAttr,se=True):
				print('Deformer attribute "'+deformerAttr+'" is not settable! Skipping...')
				continue
			
			# Set attribute
			attrVal = self._data['attrValueDict'][attr]
			# Check list value (ie. compound or multi value attribute result)
			if type(attrVal) == list: attrVal = attrVal[0]
			# Check list or tuple value (ie. compound or multi value attribute result)
			if type(attrVal) == list or type(attrVal) == tuple:
				mc.setAttr(deformerAttr,*attrVal)
			else:
				mc.setAttr(deformerAttr,attrVal)
	
	def setDeformerAttrConnections(self):
		'''
		Set custom (non-standard) deformer attribute connections based on the stored deformer connection data.
		'''
		# ====================================
		# - Set Custom Attribute Connections -
		# ====================================
		
		for attr in self._data['attrConnectionDict'].iterkeys():
			
			# Define Deformer Attribute
			deformerAttr = self._data['name']+'.'+attr
			
			# Check connection destination
			if not mc.objExists(deformerAttr):
				print('Deformer attribute connection destination "'+deformerAttr+'" does not exist!('+self._data['name']+')')
				continue
			# Check connection destination settable state
			if not mc.getAttr(deformerAttr,se=True):
				print('Deformer attribute connection destination "'+deformerAttr+'" is not settable!('+self._data['name']+')')
				continue
			# Check connection source
			if not mc.objExists(self._data['attrConnectionDict'][attr]):
				print('Deformer attribute connection source "'+self._data['attrConnectionDict'][attr]+'" does not exist!('+self._data['name']+')')
				continue
			# Create Connection
			mc.connectAttr(self._data['attrConnectionDict'][attr],deformerAttr,f=True)
	
	def customDeformerAttributes(self,deformerType):
		'''
		'''
		# Curve Twist
		if deformerType == 'curveTwist':
			
			self._data['attrValueList'].append('twistAngle')
			self._data['attrValueList'].append('twistType')
			self._data['attrValueList'].append('twistAxis')
			self._data['attrValueList'].append('distance')
			self._data['attrValueList'].append('scale')
			
			self._data['attrConnectionList'].append('twistCurve')
		
		# Directional Smooth
		elif deformerType == 'directionalSmooth':
		
			self._data['attrValueList'].append('iterations')
			self._data['attrValueList'].append('smoothFactor')
			self._data['attrValueList'].append('smoothMethod')
			self._data['attrValueList'].append('maintainBoundary')
			self._data['attrValueList'].append('maintainDetail')
			self._data['attrValueList'].append('dentRemoval')
			self._data['attrValueList'].append('averageNormal')
			self._data['attrValueList'].append('weightU')
			self._data['attrValueList'].append('weightV')
			self._data['attrValueList'].append('weightN')
			self._data['attrValueList'].append('useReferenceUVs')
									
			self._data['attrConnectionList'].append('referenceMesh')
		
		# Strain Relaxer
		elif deformerType == 'strainRelaxer':
		
			self._data['attrValueList'].append('iterations')
			self._data['attrValueList'].append('bias')
			
			self._data['attrConnectionList'].append('refMesh')
		
		# Undefined
		else:
			pass

class MultiInfluenceDeformerData( DeformerData ):
	"""
	MultiInfluenceDeformerData class object.
	This class is derived directly from the base class deformerData, and should be
	the parent class for all other multiInfluence deformer data classes.
	"""
	def __init__(self):
		
		# Execute Super Class Initializer
		super(MultiInfluenceDeformerData, self).__init__()
		
		# Initialize Influence Data
		self._influenceData = {}

# =============
# - DEFORMERS -
# =============

class BulgeSkinBasicData( DeformerData ):
	'''
	BulgeSkinBasic DeformerData class object.
	'''
	def __init__(self):
		'''
		BulgeSkinBasic DeformerData class initializer.
		'''
		# Execute Super Class Initilizer
		super(BulgeSkinBasicData, self).__init__()
		
		# Deformer Attribute Values
		self._data['attrValueList'].append('method')
		self._data['attrValueList'].append('projectPoint')
		self._data['attrValueList'].append('shrinkWrap')
		self._data['attrValueList'].append('boundingBoxTest')
		self._data['attrValueList'].append('normalCompare')
		self._data['attrValueList'].append('reverseNormal')
		self._data['attrValueList'].append('averageNormal')
		self._data['attrValueList'].append('maxDistance')
		self._data['attrValueList'].append('collisionOffset')
		
		# Deformer Attribute Connections
		self._data['attrConnectionList'].append('collisionGeometry')
		self._data['attrConnectionList'].append('collisionMatrix')

class BulgeSkinPrimData( DeformerData ):
	'''
	BulgeSkinPrim DeformerData class object.
	'''
	def __init__(self):
		'''
		BulgeSkinPrim DeformerData class initializer.
		'''
		# Execute Super Class Initilizer
		super(BulgeSkinPrimData, self).__init__()
		
		# Deformer Attribute Values
		self._data['attrValueList'].append('projectMethod')
		self._data['attrValueList'].append('projectVector')
		self._data['attrValueList'].append('primitiveType')
		self._data['attrValueList'].append('primitiveSize')
		
		# Deformer Attribute Connections
		self._data['attrConnectionList'].append('primitiveMatrix')

class CurveTwistData( DeformerData ):
	'''
	CurveTwist DeformerData class object.
	'''
	def __init__(self):
		'''
		CurveTwist DeformerData class initializer.
		'''
		# Execute Super Class Initilizer
		super(CurveTwistData, self).__init__()
		
		# Deformer Attribute Values
		self._data['attrValueList'].append('twistAngle')
		self._data['attrValueList'].append('twistType')
		self._data['attrValueList'].append('twistAxis')
		self._data['attrValueList'].append('distance')
		self._data['attrValueList'].append('scale')
		
		# Deformer Attribute Connections
		self._data['attrConnectionList'].append('twistCurve')

class DirectionalSmoothData( DeformerData ):
	'''
	DirectionalSmooth DeformerData class object.
	'''
	def __init__(self):
		'''
		DirectionalSmooth DeformerData class initializer.
		'''
		# Execute Super Class Initilizer
		super(DirectionalSmoothData, self).__init__()
		
		# Deformer Attribute Values
		self._data['attrValueList'].append('iterations')
		self._data['attrValueList'].append('smoothFactor')
		self._data['attrValueList'].append('smoothMethod')
		self._data['attrValueList'].append('maintainBoundary')
		self._data['attrValueList'].append('maintainDetail')
		self._data['attrValueList'].append('dentRemoval')
		self._data['attrValueList'].append('averageNormal')
		self._data['attrValueList'].append('weightU')
		self._data['attrValueList'].append('weightV')
		self._data['attrValueList'].append('weightN')
		self._data['attrValueList'].append('useReferenceUVs')
		
		# Deformer Attribute Connections
		self._data['attrConnectionList'].append('referenceMesh')

class PeakDeformerData( DeformerData ):
	'''
	PeakDeformer DeformerData class object.
	'''
	def __init__(self):
		'''
		PeakDeformer DeformerData class initializer.
		'''
		# Execute Super Class Initilizer
		super(PeakDeformerData, self).__init__()
		
		# Deformer Attribute Values
		self._data['attrValueList'].append('peak')
		self._data['attrValueList'].append('bulge')
		self._data['attrValueList'].append('iterations')
		self._data['attrValueList'].append('averageNormal')

class StrainRelaxerData( DeformerData ):
	'''
	StrainRelaxer DeformerData class object.
	'''
	def __init__(self):
		'''
		StrainRelaxer DeformerData class initializer.
		'''
		# Execute Super Class Initilizer
		super(StrainRelaxerData, self).__init__()
		
		# Deformer Attribute Values
		self._data['attrValueList'].append('iterations')
		self._data['attrValueList'].append('bias')
		
		# Deformer Attribute Connections
		self._data['attrConnectionList'].append('refMesh')
	

