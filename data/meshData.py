import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import data
import glTools.utils.mesh
import glTools.utils.progressBar

class MeshData( data.Data ):
	'''
	MeshData class object.
	Contains functions to save, load and rebuild maya mesh data.
	'''
	def __init__(self,mesh=''):
		'''
		MeshData class initializer.
		'''
		# Execute Super Class Initilizer
		super(MeshData, self).__init__()

		# Initialize Class Defaults
		self.maxDist = 9999999.9
		
		# Initialize Default Class Data Members
		self._data['name'] = ''
		self._data['vertexList'] = []
		self._data['polyCounts'] = []
		self._data['polyConnects'] = []
		
		self._data['uvCounts'] = []
		self._data['uvIds'] = []
		self._data['uArray'] = []
		self._data['vArray'] = []
		
		# Build Data
		if mesh: self.buildData(mesh)

	def buildData(self,mesh):
		'''
		Build meshData class.
		@param mesh: Mesh to initialize data for
		@type mesh: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Check Mesh
		if not glTools.utils.mesh.isMesh(mesh):
			raise Exception('Object "'+mesh+'" is not a vaild Mesh node!')
		
		# ==============
		# - Build Data -
		# ==============
		
		# Start timer
		timer = mc.timerX()
		
		# Get basic mesh info
		self._data['name'] = mesh

		# Get Mesh Function Class
		meshFn = glTools.utils.mesh.getMeshFn(mesh)

		# Get Polygon Data
		polygonCounts = OpenMaya.MIntArray()
		polygonConnects = OpenMaya.MIntArray()
		meshFn.getVertices(polygonCounts,polygonConnects)
		self._data['polyCounts'] = list(polygonCounts)
		self._data['polyConnects'] = list(polygonConnects)

		# Get Vertex Data
		meshPts = meshFn.getRawPoints()
		numVerts = meshFn.numVertices()
		meshPtUtil = OpenMaya.MScriptUtil()
		self._data['vertexList'] = [meshPtUtil.getFloatArrayItem(meshPts,i) for i in xrange(numVerts*3)]
		
		# =======
		# - UVs -
		# =======
		
		# UV Connect Data
		uvCounts = OpenMaya.MIntArray()
		uvIds = OpenMaya.MIntArray()
		meshFn.getAssignedUVs(uvCounts,uvIds)
		self._data['uvCounts'] = list(uvCounts)
		self._data['uvIds'] = list(uvIds)
		
		# Get UVs
		uArray = OpenMaya.MFloatArray()
		vArray = OpenMaya.MFloatArray()
		meshFn.getUVs(uArray,vArray)
		self._data['uArray'] = list(uArray)
		self._data['vArray'] = list(vArray)

		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('MeshData: Data build time for mesh "'+mesh+'": '+str(buildTime))
		
		# =================
		# - Return Result -
		# =================
		
		return self._data['name']

	def rebuild(self):
		'''
		'''
		# Start timer
		timer = mc.timerX()

		# Rebuild Mesh Data
		meshUtil = OpenMaya.MScriptUtil()
		numVertices = len(self._data['vertexList'])/3
		numPolygons = len(self._data['polyCounts'])
		polygonCounts = OpenMaya.MIntArray()
		polygonConnects = OpenMaya.MIntArray()
		meshUtil.createIntArrayFromList(self._data['polyCounts'],polygonCounts)
		meshUtil.createIntArrayFromList(self._data['polyConnects'],polygonConnects)
		
		# Rebuild UV Data
		uvCounts = OpenMaya.MIntArray()
		uvIds = OpenMaya.MIntArray()
		meshUtil.createIntArrayFromList(self._data['uvCounts'],uvCounts)
		meshUtil.createIntArrayFromList(self._data['uvIds'],uvIds)
		uArray = OpenMaya.MFloatArray()
		vArray = OpenMaya.MFloatArray()
		meshUtil.createFloatArrayFromList(self._data['uArray'],uArray)
		meshUtil.createFloatArrayFromList(self._data['vArray'],vArray)

		# Rebuild Vertex Array
		vertexArray = OpenMaya.MFloatPointArray(numVertices,OpenMaya.MFloatPoint.origin)
		vertexList = [vertexArray.set(i,self._data['vertexList'][i*3],self._data['vertexList'][i*3+1],self._data['vertexList'][i*3+2],1.0) for i in xrange(numVertices)]

		# Rebuild Mesh
		meshFn = OpenMaya.MFnMesh()
		meshData = OpenMaya.MFnMeshData().create()
		meshObj = meshFn.create(	numVertices,
									numPolygons,
									vertexArray,
									polygonCounts,
									polygonConnects,
									uArray,
									vArray,
									meshData	)
		
		# Assign UVs
		meshFn.assignUVs(uvCounts,uvIds)
		
		meshObjHandle = OpenMaya.MObjectHandle(meshObj)

		# Print Timed Result
		buildTime = mc.timerX(st=timer)
		print('MeshIntersectData: Data rebuild time for mesh "'+self._data['name']+'": '+str(buildTime))

		# =================
		# - Return Result -
		# =================
		
		return meshObjHandle

	def rebuildMesh(self):
		'''
		'''
		# Start timer
		timer = mc.timerX()

		# Rebuild Mesh Data
		meshData = OpenMaya.MObject()
		meshUtil = OpenMaya.MScriptUtil()
		numVertices = len(self._data['vertexList'])/3
		numPolygons = len(self._data['polyCounts'])
		polygonCounts = OpenMaya.MIntArray()
		polygonConnects = OpenMaya.MIntArray()
		meshUtil.createIntArrayFromList(self._data['polyCounts'],polygonCounts)
		meshUtil.createIntArrayFromList(self._data['polyConnects'],polygonConnects)
		
		# Rebuild UV Data
		uArray = OpenMaya.MFloatArray()
		vArray = OpenMaya.MFloatArray()
		meshUtil.createFloatArrayFromList(self._data['uArray'],uArray)
		meshUtil.createFloatArrayFromList(self._data['vArray'],vArray)
		uvCounts = OpenMaya.MIntArray()
		uvIds = OpenMaya.MIntArray()
		meshUtil.createIntArrayFromList(self._data['uvCounts'],uvCounts)
		meshUtil.createIntArrayFromList(self._data['uvIds'],uvIds)

		# Rebuild Vertex Array
		vertexArray = OpenMaya.MFloatPointArray(numVertices,OpenMaya.MFloatPoint.origin)
		vertexList = [vertexArray.set(i,self._data['vertexList'][i*3],self._data['vertexList'][i*3+1],self._data['vertexList'][i*3+2],1.0) for i in xrange(numVertices)]

		# Rebuild Mesh
		meshFn = OpenMaya.MFnMesh()
		meshObj = meshFn.create(	numVertices,
									numPolygons,
									vertexArray,
									polygonCounts,
									polygonConnects,
									uArray,
									vArray,
									meshData	)
		
		# Assign UVs
		meshFn.assignUVs(uvCounts,uvIds)

		# Rename Mesh
		mesh = OpenMaya.MFnDependencyNode(meshObj).setName(self._data['name'])
		meshShape = mc.listRelatives(mesh,s=True,ni=True,pa=True)[0]

		# Assign Initial Shading Group
		mc.sets(meshShape,fe='initialShadingGroup')

		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('MeshIntersectData: Geometry rebuild time for mesh "'+mesh+'": '+str(buildTime))

		# =================
		# - Return Result -
		# =================
		
		return mesh
