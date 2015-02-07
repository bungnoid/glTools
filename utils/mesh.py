import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.component
import glTools.utils.mathUtils
import glTools.utils.matrix

import math

class UserInterupted(Exception): pass

def isMesh(mesh):
	'''
	Check if the specified object is a polygon mesh or transform parent of a mesh
	@param mesh: Object to query
	@type mesh: str
	'''
	# Check Object Exists
	if not mc.objExists(mesh): return False
	
	# Check Shape
	if 'transform' in mc.nodeType(mesh,i=True):
		meshShape = mc.ls(mc.listRelatives(mesh,s=True,ni=True,pa=True) or [],type='mesh')
		if not meshShape: return False
		mesh = meshShape[0]
	
	# Check Mesh
	if mc.objectType(mesh) != 'mesh': return False
	
	# Return Result
	return True

def isOpen(mesh):
	'''
	Check if mesh is a closed surface or has boundary components
	@param mesh: Mesh to check for boundary conditions
	@type mesh: str
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# Get User Selection
	sel = mc.ls(sl=1)
	
	# Select Mesh
	mc.select(mesh)
	mc.polySelectConstraint(mode=3,type=1,where=1)
	boundarySel = mc.ls(sl=1,fl=1)
	
	# Restore User Selection
	if sel: mc.select(sel)
	
	# Return Result
	return bool(boundarySel)
	
def getMeshFn(mesh):
	'''
	Create an MFnMesh class object from the specified polygon mesh
	@param mesh: Mesh to create function class for
	@type mesh: str
	'''
	# Checks
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get shape
	if mc.objectType(mesh) == 'transform':
		mesh = mc.listRelatives(mesh,s=True,ni=True,pa=True)[0]
		
	# Get MFnMesh
	meshPath = glTools.utils.base.getMDagPath(mesh)
	meshFn = OpenMaya.MFnMesh(meshPath)
	
	# Return result
	return meshFn

def getMeshVertexIter(mesh,vtxId=None):
	'''
	Create an MItMeshVertex class object from the specified polygon mesh
	@param mesh: Mesh to create function class for
	@type mesh: str
	'''
	# Checks
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get shape
	if mc.objectType(mesh) == 'transform':
		mesh = mc.listRelatives(mesh,s=True,ni=True,pa=True)[0]
	
	# Get MFnMesh
	meshPath = glTools.utils.base.getMDagPath(mesh)
	meshVertIt = OpenMaya.MItMeshVertex(meshPath)
	
	# Initialize faceId
	if vtxId != None:
		meshVertUtil = OpenMaya.MScriptUtil(0)
		meshVertPtr = meshVertUtil.asIntPtr()
		meshVertIt.setIndex(vtxId,meshVertPtr)
	
	# Return result
	return meshVertIt

def getMeshFaceIter(mesh,faceId=None):
	'''
	Create an MItMeshPolygon class object from the specified polygon mesh
	@param mesh: Mesh to create function class for
	@type mesh: str
	@param faceId: Face ID to initialize iterator to
	@type faceId: int or None
	'''
	# Checks
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get shape
	if mc.objectType(mesh) == 'transform':
		mesh = mc.listRelatives(mesh,s=True,ni=True,pa=True)[0]
	
	# Get MFnMesh
	meshPath = glTools.utils.base.getMDagPath(mesh)
	meshFaceIt = OpenMaya.MItMeshPolygon(meshPath)
	
	# Initialize faceId
	if faceId != None:
		meshFaceUtil = OpenMaya.MScriptUtil(0)
		meshFacePtr = meshFaceUtil.asIntPtr()
		meshFaceIt.setIndex(faceId,meshFacePtr)
	
	# Return result
	return meshFaceIt

def getMeshEdgeIter(mesh,edgeId=None):
	'''
	Create an MItMeshEdge class object from the specified polygon mesh
	@param mesh: Mesh to create function class for
	@type mesh: str
	@param edgeId: Edge ID to initialize iterator to
	@type edgeId: int or None
	'''
	# Checks
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get shape
	if mc.objectType(mesh) == 'transform':
		mesh = mc.listRelatives(mesh,s=True,ni=True,pa=True)[0]
	
	# Get MFnMesh
	meshPath = glTools.utils.base.getMDagPath(mesh)
	meshEdgeIt = OpenMaya.MItMeshEdge(meshPath)
	
	# Initialize faceId
	if edgeId != None:
		meshEdgeUtil = OpenMaya.MScriptUtil(0)
		meshEdgePtr = meshEdgeUtil.asIntPtr()
		meshEdgeIt.setIndex(edgeId,meshEdgePtr)
	
	# Return result
	return meshEdgeIt

def getRawPoints(mesh):
	'''
	Get mesh vertex positions via the MFnMesh.getRawPoints() method.
	@param mesh: Mesh to get vertex positions for
	@type mesh: str
	'''
	# Checks
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get Mesh Points
	meshFn = getMeshFn(mesh)
	meshPts = meshFn.getRawPoints()
	meshVtx = meshFn.numVertices()
	
	# Convert Mesh Points (MPointArray)
	#meshPtUtil = OpenMaya.MScriptUtil()
	#meshPtArray = OpenMaya.MPointArray(meshVtx,OpenMaya.MPoint.origin)
	#for i in range(meshVtx):
	#	meshPtArray[i] = OpenMaya.MPoint(	meshPtUtil.getFloatArrayItem(meshPts,(i*3)+0),
	#										meshPtUtil.getFloatArrayItem(meshPts,(i*3)+1),
	#										meshPtUtil.getFloatArrayItem(meshPts,(i*3)+2)	)
	
	# Return Result
	return meshPts

def getPoints(mesh):
	'''
	Get mesh vertex positions via the MFnMesh.getRawPoints() method.
	@param mesh: Mesh to get vertex positions for
	@type mesh: str
	'''
	# Checks
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get Mesh Points
	meshFn = getMeshFn(mesh)
	meshPts = meshFn.getRawPoints()
	meshVtx = meshFn.numVertices()
	
	# Convert Mesh Points (MPointArray)
	meshPtArray = []
	meshPtUtil = OpenMaya.MScriptUtil()
	for i in range(meshVtx):
		meshPtArray.append(	[	meshPtUtil.getFloatArrayItem(meshPts,(i*3)+0),
								meshPtUtil.getFloatArrayItem(meshPts,(i*3)+1),
								meshPtUtil.getFloatArrayItem(meshPts,(i*3)+2)	]	)
	
	# Return Result
	return meshPtArray

def getNormal(mesh,vtxId,worldSpace=False):
	'''
	Return the vertex normal for the specified vertex of a given mesh
	@param mesh: Mesh to query normal from
	@type mesh: str
	@param vtxId: Vertice index to query normal from
	@type vtxId: int
	@param worldSpace: Sample the normal direction in world space
	@type worldSpace: bool
	'''
	# Check mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get MFnMesh
	meshFn = getMeshFn(mesh)
	
	# Determine sample space
	if worldSpace:
		sampleSpace = OpenMaya.MSpace.kWorld
	else:
		sampleSpace = OpenMaya.MSpace.kObject
	
	# Get Normals
	normal = OpenMaya.MVector()
	meshFn.getVertexNormal(vtxId,normal,sampleSpace)
	
	# Return result
	return normal

def getNormals(mesh,worldSpace=False):
	'''
	Return all vertex normals for the specified mesh
	@param mesh: Mesh to get vertex normals for
	@type mesh: str
	@param worldSpace: Return the normals in world or object space
	@type worldSpace: bool
	'''
	# Check Mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get MFnMesh
	meshFn = getMeshFn(mesh)
	
	# Determine sample space
	if worldSpace:
		sampleSpace = OpenMaya.MSpace.kWorld
	else:
		sampleSpace = OpenMaya.MSpace.kObject
	
	# Get Normals
	normalArray = OpenMaya.MFloatVectorArray()
	meshFn.getVertexNormals(False,normalArray,sampleSpace)
	
	# Return result
	return normalArray

def getUVs(mesh,UVset=None):
	'''
	Get mesh UV coordinates for the specified mesh
	@param mesh: Mesh to get UV from.
	@type mesh: str
	@param UVset: Mesh UV set to get UVs from. If None, use current UV set.
	@type UVset: str or None
	'''
	# Check Mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	# Check UV Set
	if UVset and not UVset in mc.polyUVSet(mesh,allUVSets=True):
		raise Exception('Mesh "'+mesh+'" has not UV set "'+UVset+'"!')
	
	# Get MeshFn
	meshFn = getMeshFn(mesh)
	
	# Get UVs
	uArray = OpenMaya.MFloatArray()
	vArray = OpenMaya.MFloatArray()
	meshFn.getUVs(uArray,vArray,UVset)
	u = list(uArray)
	v = list(vArray)
	
	# Return Result
	return u, v

def resetVertices(mesh):
	'''
	Reset vertex transforms for the specified mesh.
	@param mesh: Mesh to freeze vertex transforms on.
	@type mesh: str
	'''
	# Check Mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Reset Vertices
	vtx = mc.polyEvaluate(mesh,v=True)
	for i in range(vtx):
		mc.setAttr(mesh+'.pnts['+str(i)+'].pntx',0)
		mc.setAttr(mesh+'.pnts['+str(i)+'].pnty',0)
		mc.setAttr(mesh+'.pnts['+str(i)+'].pntz',0)
	
	# Return Result
	return mesh

def freezeVertices(mesh):
	'''
	Freeze vertex transforms for the specified mesh.
	Warning: All construction history will be deleted!!
	@param mesh: Mesh to freeze vertex transforms on.
	@type mesh: str
	'''
	# Check Mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Freeze Vertices
	mc.polyMoveVertex(mesh)
	mc.delete(mesh,ch=True)
	
	# Return Result
	return mesh

def reassignUVs(mesh,precision=4):
	'''
	Reassign stored UVs to specified mesh.
	Forces mesh UV refresh.
	@param mesh: Mesh to reassign UVs for.
	@type mesh: str
	@param precision: UV float precision to reapply.
	@type precision: int
	'''
	# Check Mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get MeshFn
	meshFn = getMeshFn(mesh)
	
	# Get UV Ids
	uvCount = OpenMaya.MIntArray()
	uvIds = OpenMaya.MIntArray()
	meshFn.getAssignedUVs(uvCount,uvIds)
	
	# Get UVs
	uArray = OpenMaya.MFloatArray()
	vArray = OpenMaya.MFloatArray()
	meshFn.getUVs(uArray,vArray)
	u = list(uArray)
	v = list(vArray)
	
	# Set UVs
	uArrayNew = OpenMaya.MFloatArray()
	vArrayNew = OpenMaya.MFloatArray()
	for i in u: uArrayNew.append(round(i,precision))
	for i in v: vArrayNew.append(round(i,precision))
	meshFn.setUVs(uArrayNew,vArrayNew)
	
	# Reassign UVs
	meshFn.assignUVs(uvCount,uvIds)
	
def getEdgeVertexIndices(mesh,edgeId):
	'''
	Return the vertex indices connected to the specified mesh edge.
	@param mesh: Mesh to query edge vertex indices for
	@type mesh: str
	@param edgeId: Edge index to get vertex indices for
	@type edgeId: str
	'''
	# Check mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get MItMeshEdge
	edgeIter = getMeshEdgeIter(mesh)
	
	# Create edgeId MScriptUtil
	edgeIdUtil = OpenMaya.MScriptUtil()
	edgeIdUtil.createFromInt(0)
	edgeIdPtr = edgeIdUtil.asIntPtr()
	
	# Set current edge index
	edgeIter.setIndex(edgeId,edgeIdPtr)
	
	# Get edge vertex indices
	vtx0 = edgeIter.index(0)
	vtx1 = edgeIter.index(1)
	
	# Return result
	return [vtx0,vtx1]

def getFaceVertexIndices(mesh,faceId):
	'''
	Return the vertex indices connected to the specified mesh face.
	@param mesh: Mesh to query face vertex indices for
	@type mesh: str
	@param faceId: Face index to get vertex indices for
	@type faceId: str
	'''
	# Check mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
		
	# Get MItMeshPolygon
	faceIter = getMeshFaceIter(mesh)
	
	# Create faceId MScriptUtil
	faceIdUtil = OpenMaya.MScriptUtil()
	faceIdUtil.createFromInt(0)
	faceIdPtr = faceIdUtil.asIntPtr()
	
	# Get face vertex indices
	faceVtxArray = OpenMaya.MIntArray()
	faceIter.setIndex(faceId,faceIdPtr)
	faceIter.getVertices(faceVtxArray)
	
	# Return result
	return list(faceVtxArray)

def getFaceEdgeIndices(mesh,faceId):
	'''
	Return the edge indices connected to the specified mesh face.
	@param mesh: Mesh to query face edge indices for
	@type mesh: str
	@param faceId: Face index to get edge indices for
	@type faceId: int
	'''
	# Check mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
		
	# Get MItMeshPolygon
	faceIter = getMeshFaceIter(mesh)
	
	# Create faceId MScriptUtil
	faceIdUtil = OpenMaya.MScriptUtil()
	faceIdUtil.createFromInt(0)
	faceIdPtr = faceIdUtil.asIntPtr()
	
	# Get face vertex indices
	faceEdgeArray = OpenMaya.MIntArray()
	faceIter.setIndex(faceId,faceIdPtr)
	faceIter.getEdges(faceEdgeArray)
	
	# Return result
	return list(faceEdgeArray)

def numUvShells(mesh,uvSet=''):
	'''
	Return the number of separate UV shells exist for the specified mesh and UV set.
	@param mesh: Mesh to query UV shells for
	@type mesh: str
	@param uvSet: Mesh UV set to query UV shells for
	@type uvSet: str
	'''
	# Check Mesh
	if not isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check UV Set
	uvSets = mc.polyUVSet(mesh,q=True,allUVSets=True)
	if not uvSets:
		raise Exception('Mesh object "'+mesh+'" has no UVsets!')
	if not uvSet: uvSet = uvSets[0]
	if not uvSets.count(uvSet):
		raise Exception('Mesh object "'+mesh+'" has no UVset "'+uvSet+'"!')
	
	# Initialize Function Sets
	uvShellArray = OpenMaya.MIntArray()
	meshFn = getMeshFn(mesh)
	
	# Build Pointer
	shells = OpenMaya.MScriptUtil()
	shells.createFromInt(0)
	shellsPtr = shells.asUintPtr()
	
	# Get UV Shell IDs
	meshFn.getUvShellsIds(uvShellArray, shellsPtr, uvSet)
	
	# Return Result
	return shells.getUint(shellsPtr)
	
def getVertexUV(mesh,vtxId,uvSet=None,average=False):
	'''
	Return the UV value of the specified mesh vertex
	@param mesh: Mesh to query vertex UV value from
	@type mesh: str
	@param vtxId: Face index to get edge indices for
	@type vtxId: int
	@param uvSet: Mesh uvSet to query. If empty, use current uvSet.
	@type uvSet: str
	@param average: Average shared UV values. If False, use first value.
	@type average: bool
	'''
	# Check mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Check uvSet
	if not uvSet:
		uvSet = mc.polyUVSet(mesh,q=True,cuv=True)
	
	# Get Mesh Vertex Function Set
	vtxIdUtil = OpenMaya.MScriptUtil()
	vtxIdUtil.createFromInt(0)
	vtxIdPtr = vtxIdUtil.asIntPtr()
	vtxIt = glTools.utils.mesh.getMeshVertexIter(mesh)
	vtxIt.setIndex(vtxId,vtxIdPtr)
	
	# Get UV value
	uArray = OpenMaya.MFloatArray()
	vArray = OpenMaya.MFloatArray()
	faceArray = OpenMaya.MIntArray()
	vtxIt.getUVs(uArray,vArray,faceArray)
	#vtxIt.getUVs(uArray,vArray,faceArray,uvSet)
	uArray = list(uArray)
	vArray = list(vArray)
	u = uArray[0]
	v = vArray[0]
	
	# Average shared vertex UVs
	if average:
		u=0.0
		v=0.0
		uvCount = len(uArray)
		for i in range(uvCount):
			u += uArray[i]/uvCount
			v += vArray[i]/uvCount
	
	# Return Result
	return [u,v]
	
def closestPoint(mesh,point=(0,0,0)):
	'''
	Get the closest point on the specified mesh to a given point
	Values expected and returned in world space.
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest point to THIS point
	@type point: tuple
	'''
	# Check mesh
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get MPoint
	pos = glTools.utils.base.getMPoint(point)
	cpos = OpenMaya.MPoint()
	
	# Get MFnMesh
	meshFn = getMeshFn(mesh)
	
	# Get closestPoint
	meshFn.getClosestPoint(pos,cpos,OpenMaya.MSpace.kWorld)
	
	# Return result
	return (cpos.x,cpos.y,cpos.z)

def closestNormal(mesh,point=(0,0,0)):
	'''
	Get the closest face normal from the specified mesh to a given point.
	Values expected and returned in world space.
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest normal to THIS point
	@type point: tuple
	'''
	# Check mesh
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get MPoint
	pos = glTools.utils.base.getMPoint(point)
	norm = OpenMaya.MVector()
	
	# Get MFnMesh
	meshFn = getMeshFn(mesh)
	
	# Get closestPoint
	meshFn.getClosestNormal(pos,norm,OpenMaya.MSpace.kWorld)
	
	# Return result
	return (norm.x,norm.y,norm.z)

def closestFace(mesh,point=(0,0,0)):
	'''
	Get the closest point on the specified mesh to a given point
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest point to THIS point
	@type point: tuple
	'''
	# Check mesh
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get MPoint
	pos = glTools.utils.base.getMPoint(point)
	cpos = OpenMaya.MPoint()
	
	# Create faceId MScriptUtil
	faceId = OpenMaya.MScriptUtil()
	faceId.createFromInt(0)
	faceIdPtr = faceId.asIntPtr()
	
	# Get MFnMesh
	meshFn = getMeshFn(mesh)
	
	# Get closestPoint
	meshFn.getClosestPoint(pos,cpos,OpenMaya.MSpace.kWorld,faceIdPtr)
	
	# Return result
	return OpenMaya.MScriptUtil(faceIdPtr).asInt()

def closestVertex(mesh,point=(0,0,0)):
	'''
	Get the closest vertex on the specified mesh to a given point
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest vertex to THIS point
	@type point: tuple
	'''
	# Check mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get MPoint
	pos = glTools.utils.base.getMPoint(point)
	
	# Get closest face
	faceId = closestFace(mesh,point)
	
	# Create prevIndex MScriptUtil
	indexUtil = OpenMaya.MScriptUtil()
	indexUtil.createFromInt(0)
	indexUtilPtr = indexUtil.asIntPtr()
	
	# Get face vertices
	faceVtxArray = OpenMaya.MIntArray()
	faceIter = getMeshFaceIter(mesh)
	faceIter.setIndex(faceId,indexUtilPtr)
	faceIter.getVertices(faceVtxArray)
	
	# Get closest vertex
	vtxId = -1
	minDist = 99999
	for i in list(faceVtxArray):
		vPos = glTools.utils.base.getMPoint(mesh+'.vtx['+str(i)+']')
		dist = (pos-vPos).length()
		if dist < minDist:
			vtxId = i
			minDist = dist
	
	# Return result
	return vtxId

def closestEdge(mesh,point=(0,0,0)):
	'''
	Get the closest edge on the specified mesh to a given point
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest edge to THIS point
	@type point: tuple
	'''
	# Check mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get closest face
	faceId = closestFace(mesh,point)
	
	# Create prevIndex MScriptUtil
	indexUtil = OpenMaya.MScriptUtil()
	indexUtil.createFromInt(0)
	indexUtilPtr = indexUtil.asIntPtr()
	
	# Get face vertices
	faceEdgeArray = OpenMaya.MIntArray()
	faceIter = getMeshFaceIter(mesh)
	faceIter.setIndex(faceId,indexUtilPtr)
	faceIter.getEdges(faceEdgeArray)
	
	# Get Closest Edge
	edgeId = -1
	minDist = 99999
	for i in list(faceEdgeArray):
		ePos = edgeCenter(mesh,i)
		dist = glTools.utils.mathUtils.distanceBetween(point,ePos)
		if dist < minDist:
			edgeId = i
			minDist = dist
	
	# Return result
	return edgeId

def closestPointWeightedAverage(mesh,point=(0,0,0)):
	'''
	Get the weighted average of the vertices of the closest face on the specified mesh to a given point
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest vertex to THIS point
	@type point: tuple
	'''
	# Check mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get MPoint
	pos = glTools.utils.base.getMPoint(point)
	
	# Get closest face
	faceId = closestFace(mesh,point)
	
	# Create prevIndex MScriptUtil
	indexUtil = OpenMaya.MScriptUtil()
	indexUtil.createFromInt(0)
	indexUtilPtr = indexUtil.asIntPtr()
	
	# Get face vertices
	faceVtxArray = OpenMaya.MIntArray()
	faceIter = getMeshFaceIter(mesh)
	faceIter.setIndex(faceId,indexUtilPtr)
	faceIter.getVertices(faceVtxArray)
	faceVtxArray = list(faceVtxArray)
	
	# Calculate weighted average
	wt = {}
	distArray = []
	totalInvDist = 0.0
	for i in faceVtxArray:
		vPos = glTools.utils.base.getMPoint(mesh+'.vtx['+str(i)+']')
		dist = (pos-vPos).length()
		if dist < 0.00001: dist = 0.00001
		distArray.append(dist)
		totalInvDist += 1.0/dist
	
	for v in range(len(faceVtxArray)):
		wt[faceVtxArray[v]] = (1.0/distArray[v])/totalInvDist
	
	# Return result
	return wt

def closestNormal(mesh,point=(0,0,0)):
	'''
	Get the normal of the closest face on the specified mesh to a given point
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest point to THIS point
	@type point: tuple
	'''
	# Check mesh
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get closest face 
	cFace = closestFace(mesh,point)
	
	# Get MItMeshPolygon
	meshSel = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(mesh,meshSel)
	meshPath = OpenMaya.MDagPath()
	meshSel.getDagPath(0,meshPath)
	faceIter = OpenMaya.MItMeshPolygon(meshPath)
	
	# Get face normal
	faceNorm = OpenMaya.MVector()
	# Setup int pointer for setIndex()
	indexUtil = OpenMaya.MScriptUtil()
	indexUtil.createFromInt(0)
	indexUtilPtr = indexUtil.asIntPtr()
	faceIter.setIndex(cFace,indexUtilPtr)
	# Get normal
	faceIter.getNormal(faceNorm,OpenMaya.MSpace.kWorld)
	
	# Return result
	return (faceNorm.x,faceNorm.y,faceNorm.z)

def closestUV(mesh,point=(0,0,0),uvSet=''):
	'''
	Get the UV of the closest point on a mesh to a specified point
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest point to THIS point
	@type point: tuple
	'''
	# Check mesh
	if not isMesh(mesh): raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check uvSet
	if not uvSet:
		currentUvSet = mc.polyUVSet(mesh,q=True,cuv=True)
		if not currentUvSet: raise Exception('Mesh "'+mesh+'" has no valid uvSet!')
		uvSet = currentUvSet[0]
	if not mc.polyUVSet(mesh,q=True,auv=True).count(uvSet):
		raise Exception('Invalid UV set "'+uvSet+'" specified!"')
	
	# Get mesh function set
	meshFn = getMeshFn(mesh)
	
	# Get closest UV
	pnt = glTools.utils.base.getMPoint(point)
	uv = OpenMaya.MScriptUtil()
	uv.createFromList([0.0,0.0],2)
	uvPtr = uv.asFloat2Ptr()
	meshFn.getUVAtPoint(pnt,uvPtr,OpenMaya.MSpace.kWorld,uvSet)
	
	# Return result
	return (uv.getFloat2ArrayItem(uvPtr,0,0),uv.getFloat2ArrayItem(uvPtr,0,1))

def getPointFromUV(mesh,uv=(-1,-1),uvSet=None,tolerance=0.01):
	'''
	Get the UV of the closest point on a mesh to a specified point
	@param mesh: Mesh to query
	@type mesh: str
	@param uvSet: UV set to query
	@type uvSet: str or None
	@param uv: uv coordinates
	@type uv: tuple
	@param tolerance: tolerance ge
	@type uv: tuple
	'''
	
	# Check mesh
	if not isMesh(mesh): raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	if not uvSet:
		currentUvSet = mc.polyUVSet(mesh,q=True,cuv=True)
		if not currentUvSet: raise Exception('Mesh "'+mesh+'" has no valid uvSet!')
		uvSet = currentUvSet[0]
	if not mc.polyUVSet(mesh,q=True,auv=True).count(uvSet):
		raise Exception('Invalid UV set "'+uvSet+'" specified!"')
	
	# Get mesh function set
	meshFn = getMeshFn(mesh)
	faceCount = mc.polyEvaluate(mesh, face=True)
	
	# convert uv to ptr
	util = OpenMaya.MScriptUtil()   
	util.createFromList ((uv[0], uv[1]),2)   
	uvPtr = util.asFloat2Ptr()
	
	positionMPoint = OpenMaya.MPoint()
	
	# check each face for uv
	#worldPos = {'face#': [x,y,z]}
	worldPos = {}
	for faceIndex in range(faceCount):
	
		try:  
			meshFn.getPointAtUV( 	faceIndex ,
								positionMPoint,
								uvPtr,
								OpenMaya.MSpace.kWorld,
								uvSet,
								tolerance )
			
			worldPos[faceIndex] = (positionMPoint.x, positionMPoint.y, positionMPoint.z)
		except:
			pass
	
	return worldPos
    
def faceCenter(mesh,faceId):
	'''
	Return the center position of the specified mesh face
	@param mesh: Mesh to query
	@type mesh: str
	@param faceId: Face ID to get center position from
	@type faceId: int
	'''
	# Get Face Center
	faceIter = getMeshFaceIter(mesh,faceId)
	pt = faceIter.center(OpenMaya.MSpace.kObject)
	
	# Return Result
	return [pt[0],pt[1],pt[2]]

def edgeCenter(mesh,edgeId):
	'''
	Return the center position of the specified mesh face
	@param mesh: Mesh to query
	@type mesh: str
	@param edgeId: Edge ID to get center position from
	@type edgeId: int
	'''
	# Get Face Center
	edgeIter = getMeshEdgeIter(mesh,edgeId)
	pt = edgeIter.center(OpenMaya.MSpace.kObject)
	
	# Return Result
	return [pt[0],pt[1],pt[2]]

def distToClosestVertex(mesh,point=(0,0,0)):
	'''
	Return the distance to the closest mesh vertex to the specified world position
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest vertex to THIS point
	@type point: tuple or list
	'''
	# Get Closest Vertex
	index = closestVertex(mesh,point)
	# Get Distance to Closest Vertex
	meshPt = mc.pointPosition(mesh+'.vtx['+str(index)+']',w=True)
	dist = glTools.utils.mathUtils.distanceBetween(point,meshPt)
	# Return Result
	return dist

def distToClosestEdge(mesh,point=(0,0,0)):
	'''
	Return the distance to the closest mesh edge to the specified world position
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest vertex to THIS point
	@type point: tuple or list
	'''
	# Get Closest Edge
	index = closestEdge(mesh,point)
	# Get Distance to Closest Edge
	meshPt = edgeCenter(mesh,index)
	dist = glTools.utils.mathUtils.distanceBetween(point,meshPt)
	# Return Result
	return dist

def distToClosestFace(mesh,point=(0,0,0)):
	'''
	Return the distance to the closest mesh face to the specified world position
	@param mesh: Mesh to query
	@type mesh: str
	@param point: Find the closest vertex to THIS point
	@type point: tuple or list
	'''
	# Get Closest Face
	index = closestFace(mesh,point)
	# Get Distance to Closest Face
	meshPt = faceCenter(mesh,index)
	dist = glTools.utils.mathUtils.distanceBetween(point,meshPt)
	# Return Result
	return dist

def snapToMesh(mesh,transform,snapPivot=False):
	'''
	Snap a transform the the closest point on a specified mesh
	@param mesh: Mesh to snap to
	@type mesh: str
	@param transform: Transform to snap to mesh
	@type transform: str
	@param snapPivot: Move only the objects pivot to the mesh point
	@type snapPivot: bool
	'''
	# Check mesh
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a valid mesh!')
	
	# Get transform position
	pos = mc.xform(transform,q=True,ws=True,rp=True)
	
	# Get mesh point position
	meshPt = closestPoint(mesh,pos)
	
	# Snap to Mesh
	if snapPivot: mc.xform(obj,piv=meshPt,ws=True)
	else: mc.move(meshPt[0]-pos[0],meshPt[1]-pos[1],meshPt[2]-pos[2],transform,r=True,ws=True)

def orientToMesh(mesh,transform,upVector=(0,1,0),upVectorObject='',normalAxis='x',upAxis='y'):
	'''
	Orient a transform to the closest point on a specified mesh
	@param mesh: Mesh to orient to
	@type mesh: str
	@param transform: Transform to orient to mesh
	@type transform: str
	@param upVector: UpVector for rotation calculation
	@type upVector: tuple
	@param upVectorObject: UpVector will be calculated in the local space of this object
	@type upVectorObject: str
	@param normalAxis: Transform axis that will be aligned to the mesh normal
	@type normalAxis: str
	@param upAxis: Transform axis that will be aligned to the upVector
	@type upAxis: str
	'''
	# Check mesh
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a valid mesh!')
	# Get transform position
	pos = mc.xform(transform,q=True,ws=True,rp=True)
	# Get closest point on mesh
	mPos = closestPoint(mesh,pos)
	# Get closest normal
	norm = closestNormal(mesh,pos)
	
	# Check upVector object
	if upVectorObject:
		if not mc.objExists(upVectorObject): raise Exception('UpVector object "'+upVectorObject+'" does not exist!!')
		upVectorMat = glTools.utils.matrix.buildMatrix(transform=upVectorObject)
		upVector = glTools.utils.matrix.vectorMatrixMultiply(upVector,upVectorMat,transformAsPoint=False,invertMatrix=False)
	
	# Build rotation matrix
	rotateOrder = mc.getAttr(transform+'.ro')
	mat = glTools.utils.matrix.buildRotation(norm,upVector,normalAxis,upAxis)
	rot = glTools.utils.matrix.getRotation(mat,rotateOrder)
	
	# Orient object to mesh
	mc.rotate(rot[0],rot[1],rot[2],transform,a=True,ws=True)

def snapToVertex(mesh,transform,vtxId=-1,snapPivot=False):
	'''
	Snap a transform the the closest point on a specified mesh
	@param mesh: Mesh to snap to
	@type mesh: str
	@param transform: Transform to snap to mesh
	@type transform: str
	@param vtxId: Integer vertex id to snap to. If -1, snap to closest vertex.
	@type vtxId: int
	@param snapPivot: Move only the objects pivot to the vertex
	@type snapPivot: bool
	'''
	# Check mesh
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a valid mesh!')
	
	# Get transform position
	pos = glTools.utils.base.getPosition(transform)
	
	# Get mesh vertex to snap to
	if vtxId < 0: vtxId = closestVertex(mesh,pos)
	
	# Get vertex position
	vtxPt = mc.pointPosition(mesh+'.vtx['+str(vtxId)+']')
	
	# Snap to Vertex
	if snapPivot:
		mc.xform(obj,piv=vtxPt,ws=True)
	else:
		mc.move(vtxPt[0]-pos[0],vtxPt[1]-pos[1],vtxPt[2]-pos[2],transform,r=True,ws=True)
	
	# Retrun result
	return vtxPt

def snapPtsToMesh_old(mesh,pointList,amount=1.0):
	'''
	Snap a list of points to the closest point on a specified mesh
	@param mesh: Polygon to snap points to
	@type mesh: str
	@param pointList: Point to snap to the specified mesh
	@type pointList: list
	@param amount: Percentage of offset to apply to each point
	@type amount: float
	'''
	# Check mesh
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a valid mesh!')
	
	# Check points
	pointList = mc.ls(pointList,fl=True)
	if not pointList: pointList = mc.ls(sl=True,fl=True)
	
	# Transform types
	transform = ['transform','joint','ikHandle','effector']
	
	# Snap points
	for pt in pointList:
		
		# Check Transform
		if transform.count(mc.objectType(pt)):
			snapToMesh(mesh,pt,snapPivot=False)
			continue
		# Move Point
		pos = mc.pointPosition(pt)
		meshPt = closestPoint(mesh,pos)
		mc.move(meshPt[0],meshPt[1],meshPt[2],pt,ws=True,a=True)

def snapPtsToMesh(mesh,pointList,amount=1.0):
	'''
	Snap a list of points to the closest point on a specified mesh
	@param mesh: Polygon to snap points to
	@type mesh: str
	@param pointList: Point to snap to the specified mesh
	@type pointList: list
	@param amount: Percentage of offset to apply to each point
	@type amount: float
	'''
	# Check mesh
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a valid mesh!')
	
	# Check points
	pointList = mc.ls(pointList,fl=True)
	if not pointList: pointList = mc.ls(sl=True,fl=True)
	
	# Get MFnMesh
	meshFn = getMeshFn(mesh)
	
	# Snap points
	pos = OpenMaya.MPoint()
	for pt in pointList:
		pnt = glTools.utils.base.getMPoint(pt)
		meshFn.getClosestPoint(pnt,pos,OpenMaya.MSpace.kWorld)
		offset = (pos - pnt) * amount
		mc.move(offset[0],offset[1],offset[2],pt,ws=True,r=True)

def closestVertexAttr(obj,mesh,attr='vtx'):
	'''
	Store the id of the closest vertex on the specified mesh as an integer attribute.
	@param obj: The transform object to store closest vertex information on
	@type obj: str
	@param mesh: The mesh to get the closest vertex of
	@type mesh: str
	@param attr: The attribute name that will store the integer index value
	@type attr: str
	'''
	# Checks
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!!')
	if not mc.objExists(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!!')
	if not isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# Get Closest Vertex
	pos = mc.xform(obj,q=True,ws=True,rp=True)
	vtx = closestVertex(mesh,pos)
	
	# Add Vertex Attribute
	if not mc.objExists(obj+'.'+attr):
		mc.addAttr(obj,ln=attr,at='long',dv=0,k=False)
		mc.setAttr(obj+'.'+attr,cb=True)
	mc.setAttr(obj+'.'+attr,vtx)
	
	# Return Result
	return (obj+'.'+attr)

def intersect(mesh,source,direction,testBothDirections=False,maxDist=9999):
	'''
	Return the intersection point on a specified mesh given a source point and direction
	@param mesh: Polygon mesh to perform intersection on
	@type mesh: str
	@param source: Source point for the intersection ray
	@type source: list or tuple or str
	@param direction: Direction of the intersection ray intersection
	@type direction: list or tuple
	@param testBothDirections: Test both directions for intersection
	@type testBothDirections: bool
	'''
	# Get meshFn
	meshFn = getMeshFn(mesh)
	# Get source point
	sourcePt = OpenMaya.MFloatPoint(source[0],source[1],source[2])
	# Get direction vector
	directionVec = OpenMaya.MFloatVector(direction[0],direction[1],direction[2])
	
	# Calculate intersection
	hitPt = OpenMaya.MFloatPoint()
	meshFn.closestIntersection(sourcePt,directionVec,None,None,False,OpenMaya.MSpace.kWorld,maxDist,testBothDirections,None,hitPt,None,None,None,None,None,0.0001)
	
	# Return intersection hit point
	return [hitPt[0],hitPt[1],hitPt[2]]

def allIntersections(mesh,source,direction,testBothDirections=False,maxDist=9999,sort=False):
	'''
	Return all intersection points on a specified mesh given a source point and direction
	@param mesh: Polygon mesh to perform intersection on
	@type mesh: str
	@param source: Source point for the intersection ray
	@type source: list or tuple or str
	@param direction: Direction of the intersection ray intersection
	@type direction: list or tuple
	@param testBothDirections: Test both directions for intersection
	@type testBothDirections: bool
	@param maxDist: Maximum search distance for intersection
	@type maxDist: float
	@param sort: Sort intersections by distance
	@type sort: bool
	'''
	# Get meshFn
	meshFn = getMeshFn(mesh)
	# Get source point
	sourcePt = OpenMaya.MFloatPoint(source[0],source[1],source[2])
	# Get direction vector
	directionVec = OpenMaya.MFloatVector(direction[0],direction[1],direction[2])
	
	# Calculate intersection
	hitPtArray = OpenMaya.MFloatPointArray()
	meshFn.allIntersections(sourcePt,directionVec,None,None,False,OpenMaya.MSpace.kWorld,maxDist,testBothDirections,None,True,hitPtArray,None,None,None,None,None,0.0001)
	
	# Sort
	intersectionList = []
	if sort:
		# Get total intersection count
		hitCount = hitPtArray.length()
		for n in range(hitCount):
			# Initialize Sort Variables
			ind = -1
			minDist = maxDist
			# Test Distance
			for i in range(hitPtArray.length()):
				dist = (sourcePt - hitPtArray[i]).length()
				if dist < minDist:
					minDist = dist
					ind = i
			# Append Sorted Intersection List 
			intersectionList.append((hitPtArray[ind][0],hitPtArray[ind][1],hitPtArray[ind][2]))
			# Remove Sorted Intersection
			hitPtArray.remove(ind)
			
	else:
		# Pass Unsorted Intersection List
		intersectionList = [(hitPtArray[i][0],hitPtArray[i][1],hitPtArray[i][2])]
	
	# Return intersection hit point
	return intersectionList

def closestInersection(mesh,source,direction,testBothDirections=False,maxDist=9999):
	'''
	Return the closest intersection point on a specified mesh given a source point and direction
	@param mesh: Polygon mesh to perform intersection on
	@type mesh: str
	@param source: Source point for the intersection ray
	@type source: list or tuple or str
	@param direction: Direction of the intersection ray intersection
	@type direction: list or tuple
	@param testBothDirections: Test both directions for intersection
	@type testBothDirections: bool
	@param maxDist: Maximum search distance for intersection
	@type maxDist: float
	'''
	# Get All Intersections
	allIntersects = allIntersections(mesh,source,direction,testBothDirections,maxDist,True)
	# Return Result
	return closestIntersection[0]

def furthestInersection(mesh,source,direction,testBothDirections=False,maxDist=9999):
	'''
	Return the furthest intersection point on a specified mesh given a source point and direction
	@param mesh: Polygon mesh to perform intersection on
	@type mesh: str
	@param source: Source point for the intersection ray
	@type source: list or tuple or str
	@param direction: Direction of the intersection ray intersection
	@type direction: list or tuple
	@param testBothDirections: Test both directions for intersection
	@type testBothDirections: bool
	@param maxDist: Maximum search distance for intersection
	@type maxDist: float
	'''
	# Get All Intersections
	allIntersects = allIntersections(mesh,source,direction,testBothDirections,maxDist,True)
	# Return Result
	return furthestIntersection[-1]

def intersectDist(mesh,source,direction,testBothDirections=False,maxDist=9999):
	'''
	Return the distance to the closest intersection point on a specified mesh given a source point and direction
	@param mesh: Polygon mesh to perform intersection on
	@type mesh: str
	@param source: Source point for the intersection ray
	@type source: list or tuple or str
	@param direction: Direction of the intersection ray intersection
	@type direction: list or tuple
	@param testBothDirections: Test both directions for intersection
	@type testBothDirections: bool
	'''
	# Get meshFn
	meshFn = getMeshFn(mesh)
	# Get source point
	sourcePt = OpenMaya.MFloatPoint(source[0],source[1],source[2])
	# Get direction vector
	directionVec = OpenMaya.MFloatVector(direction[0],direction[1],direction[2])
	
	# Create hit distance utils
	hitDistUtil = OpenMaya.MScriptUtil()
	hitDistUtil.createFromDouble(-1.0)
	hitDistPtr = hitDistUtil.asFloatPtr()
	
	# Calculate intersection
	hitPt = OpenMaya.MFloatPoint()
	meshFn.closestIntersection(sourcePt,directionVec,None,None,False,OpenMaya.MSpace.kWorld,maxDist,testBothDirections,None,hitPt,hitDistPtr,None,None,None,None,0.0001)
	
	# Return intersection hit point
	return OpenMaya.MScriptUtil(hitDistPtr).asFloat()

def intersectFace(mesh,source,direction,testBothDirections=False,maxDist=9999):
	'''
	Return the intersected face ID on a specified mesh given a source point and direction
	@param mesh: Polygon mesh to perform intersection on
	@type mesh: str
	@param source: Source point for the intersection ray
	@type source: list or tuple or str
	@param direction: Direction of the intersection ray intersection
	@type direction: list or tuple
	@param testBothDirections: Test both directions for intersection
	@type testBothDirections: bool
	'''
	# Get meshFn
	meshFn = getMeshFn(mesh)
	# Get source point
	sourcePt = OpenMaya.MFloatPoint(source[0],source[1],source[2])
	# Get direction vector
	directionVec = OpenMaya.MFloatVector(direction[0],direction[1],direction[2])
	
	# Create hit face utils
	hitFaceUtil = OpenMaya.MScriptUtil()
	hitFaceUtil.createFromInt(0)
	hitFacePtr = hitDistUtil.asIntPtr()
	
	# Calculate intersection
	hitPt = OpenMaya.MFloatPoint()
	meshFn.closestIntersection(sourcePt,directionVec,None,None,False,OpenMaya.MSpace.kWorld,maxDist,testBothDirections,None,None,None,hitFacePtr,None,None,None,0.0001)
	
	# Return intersection hit point
	return OpenMaya.MScriptUtil(hitFacePtr).asInt()

def intersectAllFaces(mesh,source,direction,testBothDirections=False,maxDist=9999):
	'''
	Return all intersected faces on a specified mesh given a source point and direction
	@param mesh: Polygon mesh to perform intersection on
	@type mesh: str
	@param source: Source point for the intersection ray
	@type source: list or tuple or str
	@param direction: Direction of the intersection ray intersection
	@type direction: list or tuple
	@param testBothDirections: Test both directions for intersection
	@type testBothDirections: bool
	'''
	# Get meshFn
	meshFn = getMeshFn(mesh)
	# Get source point
	sourcePt = OpenMaya.MFloatPoint(source[0],source[1],source[2])
	# Get direction vector
	directionVec = OpenMaya.MFloatVector(direction[0],direction[1],direction[2])
	
	# Calculate intersection
	hitFaceArray = OpenMaya.MIntArray()
	meshFn.allIntersections(sourcePt,directionVec,None,None,False,OpenMaya.MSpace.kWorld,maxDist,testBothDirections,None,True,None,None,hitFaceArray,None,None,None,0.0001)
	
	# Return intersection hit point
	return list(hitFaceArray)

def faceArea(mesh,faceId):
	'''
	Return the surface area of a specified mesh polygon face.
	@param mesh: Polygon mesh to get face area for
	@type mesh: str
	@param faceId: Face index of the polygon to get the area for
	@type faceId: int
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	# Check faceId
	if faceId > mc.polyEvaluate(mesh,f=True):
		raise Exception('Face ID ('+str(faceId)+') out of range for for mesh "'+mesh+'"!')
	
	# Get Mesh Face Fn
	faceIt = getMeshFaceIter(mesh,faceId)
	
	# Get Area
	areaUtil = OpenMaya.MScriptUtil()
	areaUtil.createFromDouble(0.0)
	areaPtr = areaUtil.asDoublePtr()
	faceIt.getArea(areaPtr)
	
	# Return Result
	return OpenMaya.MScriptUtil(areaPtr).asDouble()

def locatorMesh(mesh,locatorScale=0.1,prefix=''):
	'''
	Attach mesh vertices to a list of locators.
	@param mesh: Polygon mesh to attach to locators
	@type mesh: str
	@param locatorScale: Default locator scale
	@type locatorScale: float
	@param prefix: Naming prefix for locators
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# Check Prefix
	if not prefix: prefix = mesh
	
	# =======================
	# - Build Mesh Locators -
	# =======================
	
	# Get Vertices
	componentList = glTools.utils.component.getComponentStrList(mesh)
	
	# Iterate over component list
	locatorList = []
	for i in range(len(componentList)):
		
		# Get componet position
		pos = mc.pointPosition(componentList[i])
		
		# Build Vertex Locator
		loc = mc.spaceLocator(n=prefix+'_vtx'+str(i)+'_loc')[0]
		mc.move(pos[0],pos[1],pos[2],loc,a=True,ws=True)
		mc.setAttr(loc+'.localScale',locatorScale,locatorScale,locatorScale)
		locatorList.append(loc)
		
		# Freeze Vertices
		mc.move(0,0,0,componentList[i],a=True,ws=True)
		
	# Freeze Mesh
	deformer = mc.deformer(mesh,type='cluster')
	mc.delete(mesh,constructionHistory=True)
	
	# Connect Locators
	for i in range(len(locatorList)):
		mc.connectAttr(locatorList[i]+'.worldPosition[0]',mesh+'.controlPoints['+str(i)+']',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return locatorList

def buildMeshFromPoints(pts,ptsInU=None,ptsInV=None,closedInU=False,attach=False,prefix=None):
	'''
	Build a new mesh from a list of points.
	@param pts: List of points to mesh from.
	@type pts: list
	@param ptsInU: Number os mesh vertices in U direction.
	@type ptsInU: int
	@param ptsInV: Number os mesh vertices in V direction.
	@type ptsInV: int
	@param closedInV: Is mesh closed in V direction. (tube or plane)
	@type closedInV: bool
	@param attach: Attach mesh vertices to points. If True, points are assumed to be locators.
	@type attach: bool
	@param prefix: Naming prefix.
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Prefix
	if not prefix: prefix = 'point'
	
	# Check Point Count
	if not ptsInU:
		ptsInU = math.sqrt(len(pts))
		if ptsInU % 1: raise Exception('Invalid point count! Points in U not specified!')
	if not ptsInV:
		ptsInV = math.sqrt(len(pts))
		if ptsInV % 1: raise Exception('Invalid point count! Points in V not specified!')
	if len(pts) != (ptsInU*ptsInV):
		raise Exception('Invalid point count! Does not match ptsInU*ptsInV!')
	
	# ==============
	# - Build Mesh -
	# ==============
	
	# Create Mesh
	mesh = None
	if closedInU:
		mesh = mc.polyCylinder(ch=False,sx=ptsInU,sy=(ptsInV-1),sz=0)[0]
		mc.delete(mesh+'.f['+str(ptsInU*(ptsInV-1))+':'+str(ptsInU*(ptsInV-1)+1)+']')
	else:
		mesh = mc.polyPlane(ch=False,sx=(ptsInU-1),sy=(ptsInV-1))[0]
	
	# Rename Mesh
	mesh = mc.rename(mesh,prefix+'_mesh')
	
	# Get Mesh Vertices
	componentList = glTools.utils.component.getComponentStrList(mesh)
	
	# ==========================
	# - Position Mesh Vertices -
	# ==========================
	
	if attach:
		
		# Freeze Mesh Vertices
		mc.move(0,0,0,componentList,a=True,ws=True)
		freezeVertices(mesh)
		
		# Attach Vertices to Points
		for i in range(len(componentList)):
			mc.connectAttr(pts[i]+'.worldPosition[0]',mesh+'.controlPoints['+str(i)+']',f=True)
	
	else:
		
		# Position Vertices to Points
		for i in range(len(componentList)):
			pt = glTools.utils.base.getPosition(pts[i])
			mc.move(pt[0],pt[1],pt[2],componentList[i],a=True,ws=True)
		
		# Freeze Mesh Vertices
		freezeVertices(mesh)
	
	# =================
	# - Return Result -
	# =================
	
	return mesh
	
def borderEdgeList(mesh):
	'''
	Return a list of mesh border edges.
	@param mesh: Polygon mesh to find border edges from.
	@type mesh: str
	'''
	# Initialize edge list
	sel = []
	
	# Initialize mesh edge iterator
	meshIt = getMeshEdgeIter(mesh)
	
	# Iterate over edges
	meshIt.reset()
	while(1):
		
		# Check border edge
		if meshIt.onBoundary():
			sel.append(mesh+'.e['+str(meshIt.index())+']')
		
		# Iterate
		meshIt.next()
		if meshIt.isDone(): break
	
	# Return result
	return sel


def getCornerVertexIds(mesh):
	'''
	Return a list of vertex Ids for vertices connected to only 2 edges
	@param mesh: Polygon mesh to find corner vertices from.
	@type mesh: str
	'''
	# Checks
	if not isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Get MItMeshvertex
	meshIt = getMeshVertexIter(mesh)
	
	# Iterate over vertices
	meshIt.reset()
	cornerVetexList = []
	while not meshIt.isDone():
		
		# Get vertex Id
		vId = meshIt.index()
		
		# Get connected edges
		connEdgeList = OpenMaya.MIntArray()
		meshIt.getConnectedEdges(connEdgeList)
		connEdge = list(connEdgeList)
		
		# Check number of connected edges
		if len(connEdge) == 2: cornerVetexList.append(vId)
		
		# Iterate to next vertex
		meshIt.next()
	
	# Return result
	return cornerVetexList
	
def vertexConnectivityList(mesh,faceConnectivity=False,showProgress=False):
	'''
	Return a vertex connectivity list for the specified mesh
	@param mesh: Polygon mesh to return vertex connectivity list for
	@type mesh: str
	@param faceConnectivity: Use face connectivity instead of edge connectivity
	@type faceConnectivity: str
	@param showProgress: Show operation progress using the main progress bar
	@type showProgress: bool
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# =========================
	# - Iterate Over Vertices -
	# =========================
	
	# Begin Progress Bar
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	if showProgress:
		vtxCount = mc.polyEvaluate(mesh,v=True)
		mc.progressBar( gMainProgressBar,e=True,bp=True,ii=True,status=('Building Vertex Connectivity Array...'),maxValue=vtxCount )
	
	# Initialize Connectivity List
	vtxConnectList = []
	vtxCount = glTools.utils.component.getComponentCount(mesh)
	
	# Iterate over vertices
	for i in range(vtxCount):
		
		# Get Connected Vertex IDs
		connSel = glTools.utils.component.expandVertexSelection(mesh+'.vtx['+str(i)+']',useFace=faceConnectivity)
		connIDs = glTools.utils.component.singleIndexList(connSel)
		connIDs.remove(i)
		
		# Append Return Value
		vtxConnectList.append(connIDs)
		
		# Update Progress Bar
		if showProgress:
			if mc.progressBar(gMainProgressBar,q=True,isCancelled=True):
				mc.progressBar(gMainProgressBar,e=True,endProgress=True)
				raise UserInterupted('Operation cancelled by user!')
			mc.progressBar(gMainProgressBar,e=True,step=1)
	
	# End Current Progress Bar
	if showProgress: mc.progressBar(gMainProgressBar,e=True,endProgress=True)
	
	# Return Result
	return vtxConnectList

def vertexConnectivityDict(mesh,vtxIDs,faceConnectivity=False,showProgress=False):
	'''
	Return a vertex connectivity list for the specified mesh and vertex IDs
	@param mesh: Polygon mesh to return vertex connectivity list for
	@type mesh: str
	@param vtxIDs: Vertex IDs to get connectivity lists for
	@type vtxIDs: list
	@param faceConnectivity: Use face connectivity instead of edge connectivity
	@type faceConnectivity: bool
	@param showProgress: Show operation progress using the main progress bar
	@type showProgress: bool
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# =========================
	# - Iterate Over Vertices -
	# =========================
	
	# Begin Progress Bar
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	if showProgress:
		mc.progressBar( gMainProgressBar,e=True,bp=True,ii=True,status=('Building Vertex Connectivity Array...'),maxValue=len(vtxIDs) )
	
	# Initialize Connectivity List
	vtxConnectDict = {}
	
	for vtxID in vtxIDs:
		
		# Get Connected Vertex IDs
		connSel = glTools.utils.component.expandVertexSelection(mesh+'.vtx['+str(vtxID)+']',useFace=faceConnectivity)
		connIDs = glTools.utils.component.singleIndexList(connSel)
		connIDs.remove(vtxID)
		
		# Append Return Value
		vtxConnectDict[vtxID] = connIDs
		
		# Update Progress Bar
		if showProgress:
			if mc.progressBar(gMainProgressBar,q=True,isCancelled=True):
				mc.progressBar(gMainProgressBar,e=True,endProgress=True)
				raise UserInterupted('Operation cancelled by user!')
			mc.progressBar(gMainProgressBar,e=True,step=1)
	
	# End Current Progress Bar
	if showProgress: mc.progressBar(gMainProgressBar,e=True,endProgress=True)
		
	# Return Result
	return vtxConnectDict

def faceVertexList(mesh,showProgress=False):
	'''
	Return a list of mesh face vertex IDs for the specified mesh
	@param mesh: Polygon mesh to return face vertex list for
	@type mesh: str
	@param showProgress: Show operation progress using the main progress bar
	@type showProgress: bool
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# ======================
	# - Iterate Over Faces -
	# ======================
	
	# Initialize Face Iterator
	faceIter = getMeshFaceIter(mesh)
	
	# Begin Progress Bar
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	if showProgress:
		mc.progressBar( gMainProgressBar,e=True,bp=True,ii=True,status=('Building Face Vertex Array...'),maxValue=faceIter.count() )
	
	# Initialize Connectivity List
	faceVertexList = []
	faceVertexArray = OpenMaya.MIntArray()
	
	# Face Iterator
	faceIter.reset()
	for i in range(faceIter.count()):
		
		# Get Face Vertices
		faceIter.getVertices(faceVertexArray)
		
		# Append to Face Vertex List
		faceVertexList.append(list(faceVertexArray))
		
		# Increment Iterator
		try:
			faceIter.next()
		except:
			print('end of iter')
			break
		#if not faceIter.next():
		#	print('end of iter')
		#	break
		
		# Update Progress Bar
		if showProgress:
			if mc.progressBar(gMainProgressBar,q=True,isCancelled=True):
				mc.progressBar(gMainProgressBar,e=True,endProgress=True)
				raise UserInterupted('Operation cancelled by user!')
			mc.progressBar(gMainProgressBar,e=True,step=1)
	
	# End Current Progress Bar
	if showProgress: mc.progressBar(gMainProgressBar,e=True,endProgress=True)
	
	# =================
	# - Return Result -
	# =================
	
	return faceVertexList

def faceVertexDict(mesh,faceIDs,showProgress=False):
	'''
	Return a dictionary of mesh face vertex IDs for the specified mesh and face IDs
	@param mesh: Polygon mesh to return face vertex list for
	@type mesh: str
	@param showProgress: Show operation progress using the main progress bar
	@type showProgress: bool
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# ======================
	# - Iterate Over Faces -
	# ======================
	
	# Initialize Face Iterator
	faceIter = getMeshFaceIter(mesh)
	
	# Begin Progress Bar
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	if showProgress:
		mc.progressBar( gMainProgressBar,e=True,bp=True,ii=True,status=('Building Face Vertex Array...'),maxValue=len(faceIDs) )
	
	# Initialize Connectivity List
	faceVertexDict = {}
	faceVertexArray = OpenMaya.MIntArray()
	
	# Face Iterator
	for i in faceIDs:
		
		# Go to Face Index
		faceIter.setIndex(i)
		
		# Get Face Vertices
		faceIter.getVertices(faceVertexArray)
		
		# Append to Face Vertex List
		faceVertexDict[i].append(list(faceVertexArray))
		
		# Update Progress Bar
		if showProgress:
			if mc.progressBar(gMainProgressBar,q=True,isCancelled=True):
				mc.progressBar(gMainProgressBar,e=True,endProgress=True)
				raise UserInterupted('Operation cancelled by user!')
			mc.progressBar(gMainProgressBar,e=True,step=1)
	
	# End Current Progress Bar
	if showProgress: mc.progressBar(gMainProgressBar,e=True,endProgress=True)
	
	# =================
	# - Return Result -
	# =================
	
	return faceVertexDict

def uncombine(polyUnite):
	'''
	Uncombine a mesh with live polyUnite history
	@param polyUnite: PolyUnite (combine) to break up to indinvidual mesh components
	@type polyUnite: str
	'''
	# Check polyUnite
	if not mc.objExists(polyUnite): raise Exception('PolyUnite "'+polyUnite+'" does not exist!!')
	
	# Get input meshes
	meshInputs = mc.listConnections(polyUnite+'.inputPoly',s=True,d=False,sh=True)
	print meshInputs
	
	# Delete output mesh and polyUnite
	meshOutput = mc.ls(mc.listHistory(polyUnite,f=True),type='mesh')
	meshOutputParent = mc.listRelatives(meshOutput[0],p=True)[0]
	mc.delete(polyUnite)
	mc.delete(meshOutput)
	mc.delete(meshOutputParent)
	
	# Restore input meshes
	meshRestore = []
	for mesh in meshInputs:
		
		# Set input shape as non-intermediate
		mc.setAttr(mesh+'.intermediateObject',0)
		
		# Determine parent transforms
		transform = mc.listRelatives(mesh,p=True)[0]
		newParent = mc.listRelatives(transform,p=True)[0]
		
		# Reparent input shape and delete intermediate transform
		mc.parent(mesh,newParent,s=True,r=True)
		mc.delete(transform)
		
		# Append result
		meshRestore.append(newParent)
	
	# Return result
	return meshRestore

def polyCleanup(	meshList = 		[],
					quads = 		False,
					nonQuads = 		False,
					concave = 		False,
					holes = 		False,
					nonPlanar = 	False,
					laminaFace = 	False,
					nonManifold = 	False,
					zeroFaceArea =	False,
					zeroEdgeLen = 	False,
					zeroMapArea = 	False,
					faceAreaTol = 	0.001,
					edgeLenTol = 	0.001,
					mapAreaTol = 	0.001,
					keepHistory = 	False,
					fix = 			False,
					printCmd = 		False ):
	'''
	Perform a check for various "bad" polygon geometry.
	@param meshList: List of meshes to operate on. If empty, operate on meshes in the current scene.
	@type meshList: list
	@param quads: Find all faces with 4 sides. Faces will be triangulated if fix=True.
	@type quads: bool
	@param nonQuads: Find all faces with more than 4 sides. Faces will be triangulated if fix=True.
	@type nonQuads: bool
	@param concave: Find all concave faces. Faces will be triangulated if fix=True.
	@type concave: bool
	@param holes: Find all holed faces. Faces will be triangulated if fix=True.
	@type holes: bool
	@param nonPlanar: Find all non-planar faces. Faces will be triangulated if fix=True.
	@type nonPlanar: bool
	@param laminaFace: Find all lamina faces (faces that share the same edges). Faces will be deleted if fix=True.
	@type laminaFace: bool
	@param nonManifold: Find all non-manifold geometry (edges connected to more than 2 faces).
	@type nonManifold: bool
	@param zeroFaceArea: Find polygon faces with zero surface area. Faces will be deleted if fix=True.
	@type zeroFaceArea: bool
	@param zeroLenFace: Find polygon edges with zero length. Edges will be deleted if fix=True.
	@type zeroLenFace: bool
	@param zeroMapArea: Find polygon faces with zero map (UV) area. Faces will be deleted if fix=True.
	@type zeroMapArea: bool
	@param faceAreaTol: Zero face area tolerance.
	@type faceAreaTol: float
	@param edgeLenTol: Zero edge length tolerance.
	@type edgeLenTol: float
	@param mapAreaTol: Zero map area tolerance.
	@type mapAreaTol: float
	@param keepHistory: Maintain cleanup history
	@type keepHistory: bool
	@param fix: Attempt to fix any bad geoemetry found.
	@type fix: bool
	'''
	# Check mesh list
	for mesh in meshList:
		if not mc.objExists(mesh):
			raise Exception('Mesh "'+mesh+'" does not exist!')
	
	if not meshList:
		allMeshes = 1
	else:
		allMeshes = 0
		mc.select(meshList)
	
	# Check fix
	if fix: selectOnly = 0
	else: selectOnly = 2
	
	# Check NonManifold
	if nonManifold:
		if fix: doNonManifold = 1
		else: doNonManifold = 2
	else:
		doNonManifold = -1
	
	# Build Poly Cleanup Command
	polyCleanupCmd = 'polyCleanupArgList 3 {'
	polyCleanupCmd += '"'+str(allMeshes)+'",'			# [0]  - All selectable meshes
	polyCleanupCmd += '"'+str(selectOnly)+'",'			# [1]  - Perform selection only
	polyCleanupCmd += '"'+str(int(keepHistory))+'",'	# [2]  - Keep construction history
	polyCleanupCmd += '"'+str(int(quads))+'",'			# [3]  - Check for 4 sided faces
	polyCleanupCmd += '"'+str(int(nonQuads))+'",'		# [4]  - Check for faces with more than 4 sides
	polyCleanupCmd += '"'+str(int(concave))+'",'		# [5]  - Check for concave faces
	polyCleanupCmd += '"'+str(int(holes))+'",'			# [6]  - Check for holed faces
	polyCleanupCmd += '"'+str(int(nonPlanar))+'",'		# [7]  - Check for non-planar faces
	polyCleanupCmd += '"'+str(int(zeroFaceArea))+'",'	# [8]  - Check for zero area faces
	polyCleanupCmd += '"'+str(faceAreaTol)+'",'			# [9]  - Tolerance for face area
	polyCleanupCmd += '"'+str(int(zeroEdgeLen))+'",'	# [10] - Check for zero length edges
	polyCleanupCmd += '"'+str(edgeLenTol)+'",'			# [11] - Tolerance for edge length
	polyCleanupCmd += '"'+str(int(zeroMapArea))+'",'	# [12] - Check for zero map area faces
	polyCleanupCmd += '"'+str(mapAreaTol)+'",'			# [13] - Tolerance for map area
	polyCleanupCmd += '"0",'							# [14] - Shared UVs (unused)
	polyCleanupCmd += '"'+str(doNonManifold)+'",'		# [15] - Check non-manifold geometry
	polyCleanupCmd += '"'+str(int(laminaFace))+'"'		# [16] - Check lamina faces
	polyCleanupCmd += '};'
	
	# Perform Poly Cleanup
	mm.eval(polyCleanupCmd)
	if printCmd: print polyCleanupCmd
	
	# Generate return value
	result = mc.ls(sl=1)
	
	# Restore selection state
	if meshList: mc.select(meshList)
	else: mc.select(cl=True)
	hiliteList = mc.ls(hilite=True)
	if hiliteList: mc.hilite(hiliteList,tgl=False)
	
	# Return Result
	return result

