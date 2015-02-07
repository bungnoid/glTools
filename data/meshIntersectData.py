import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import meshData
import glTools.utils.base
import glTools.utils.mesh
import glTools.utils.progressBar

class MeshIntersectData( meshData.MeshData ):
	'''
	MeshIntersectData class object.
	Contains functions to save, load and rebuild maya sets.
	'''
	def __init__(self):
		'''
		MeshIntersectData class initializer.
		'''
		# Execute Super Class Initilizer
		super(MeshIntersectData, self).__init__()

	def getClosestPointList(self,ptList):
		'''
		'''
		# Start timer
		timer = mc.timerX()

		# Display Progress
		glTools.utils.progressBar.init(status=('Building Closest Point Coord Array...'),maxValue=int(len(ptList)*0.1))

		# Rebuild Mesh Data
		meshUtil = OpenMaya.MScriptUtil()
		numVertices = len(self._data['vertexList'])/3
		numPolygons = len(self._data['polyCounts'])
		polygonCounts = OpenMaya.MIntArray()
		polygonConnects = OpenMaya.MIntArray()
		meshUtil.createIntArrayFromList(self._data['polyCounts'],polygonCounts)
		meshUtil.createIntArrayFromList(self._data['polyConnects'],polygonConnects)

		# Rebuild Vertex Array
		vertexArray = OpenMaya.MFloatPointArray(numVertices,OpenMaya.MFloatPoint.origin)
		vertexList = [vertexArray.set(i,self._data['vertexList'][i*3],self._data['vertexList'][i*3+1],self._data['vertexList'][i*3+2],1.0) for i in xrange(numVertices)]

		# Rebuild Mesh
		meshFn = OpenMaya.MFnMesh()
		meshData = OpenMaya.MFnMeshData().create()
		meshObj = meshFn.create(numVertices,numPolygons,vertexArray,polygonCounts,polygonConnects,meshData)

		# Build Mesh Intersector
		meshPt = OpenMaya.MPointOnMesh()
		meshIntersector = OpenMaya.MMeshIntersector()
		meshIntersector.create(meshObj,OpenMaya.MMatrix.identity)

		# Get Closest Point Data
		ptCount = len(ptList)
		pntList = [ (0,0,0) for i in range(ptCount) ]
		for i in range(ptCount):

			# Get Closest Point
			mpt = glTools.utils.base.getMPoint(ptList[i])
			meshIntersector.getClosestPoint(mpt,meshPt,self.maxDist)

			# Get Mesh Point Data
			pt = meshPt.getPoint()
			pntList[i] = (pt[0],pt[1],pt[2])

			# Update Progress Bar (Every 10th Iteration)
			if not i % 10: glTools.utils.progressBar.update(step=1)

		# =================
		# - Return Result -
		# =================
		
		# End Progress
		if showProgress: glTools.utils.progressBar.end()	

		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('MeshIntersectData: Closest Point search time for mesh "'+self._data['name']+'": '+str(buildTime))
		
		return pntList

	def getClosestPointCoords(self,ptList):
		'''
		'''
		# Start timer
		timer = mc.timerX()

		# Display Progress
		glTools.utils.progressBar.init(status=('Building Closest Point Coord Array...'),maxValue=int(len(ptList)*0.1))
		
		# =====================
		# - Rebuild Mesh Data -
		# =====================

		meshUtil = OpenMaya.MScriptUtil()
		numVertices = len(self._data['vertexList'])/3
		numPolygons = len(self._data['polyCounts'])
		polygonCounts = OpenMaya.MIntArray()
		polygonConnects = OpenMaya.MIntArray()
		meshUtil.createIntArrayFromList(self._data['polyCounts'],polygonCounts)
		meshUtil.createIntArrayFromList(self._data['polyConnects'],polygonConnects)

		# Rebuild Vertex Array
		vertexArray = OpenMaya.MFloatPointArray(numVertices,OpenMaya.MFloatPoint.origin)
		vertexList = [vertexArray.set(i,self._data['vertexList'][i*3],self._data['vertexList'][i*3+1],self._data['vertexList'][i*3+2],1.0) for i in xrange(numVertices)]

		# Rebuild Mesh
		meshFn = OpenMaya.MFnMesh()
		meshData = OpenMaya.MFnMeshData().create()
		meshObj = meshFn.create(numVertices,numPolygons,vertexArray,polygonCounts,polygonConnects,meshData)

		# Build Mesh Intersector
		meshPt = OpenMaya.MPointOnMesh()
		meshIntersector = OpenMaya.MMeshIntersector()
		meshIntersector.create(meshObj,OpenMaya.MMatrix.identity)

		# ==========================
		# - Get Closest Point Data -
		# ==========================

		ptCount = len(ptList)
		baryCoords = [ [(0,0),(0,0),(0,0)] for i in range(ptCount) ]
		for i in range(ptCount):

			# Get Closest Point
			mpt = glTools.utils.base.getMPoint(ptList[i])
			meshIntersector.getClosestPoint(mpt,meshPt,self.maxDist)

			# Get Barycentric Coords
			uPtr = OpenMaya.MScriptUtil().asFloatPtr()
			vPtr = OpenMaya.MScriptUtil().asFloatPtr()
			meshPt.getBarycentricCoords(uPtr,vPtr)
			u = OpenMaya.MScriptUtil(uPtr).asFloat()
			v = OpenMaya.MScriptUtil(vPtr).asFloat()
			w = 1.0 - (u+v)
			# Get Triangle Vertex IDs
			idPtr = OpenMaya.MScriptUtil().asIntPtr()
			meshFn.getPolygonTriangleVertices(meshPt.faceIndex(),meshPt.triangleIndex(),idPtr)
			baryCoords[i] = [	(OpenMaya.MScriptUtil().getIntArrayItem(idPtr,0),u),
								(OpenMaya.MScriptUtil().getIntArrayItem(idPtr,1),v),
								(OpenMaya.MScriptUtil().getIntArrayItem(idPtr,2),w)	]

			# Update Progress Bar (Every 10th Iteration)
			if not i % 10: glTools.utils.progressBar.update(step=1)

		# =================
		# - Return Result -
		# =================
		
		# End Progress
		if showProgress: glTools.utils.progressBar.end()	
		
		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('MeshIntersectData: Data search time for mesh "'+self._data['name']+'": '+str(buildTime))
		
		return baryCoords
