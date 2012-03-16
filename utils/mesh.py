import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.component
import glTools.utils.matrix

def isMesh(mesh):
	'''
	Check if the specified object is a polygon mesh or transform parent of a mesh
	@param mesh: Object to query
	@type mesh: str
	'''
	# Check object exists
	if not mc.objExists(mesh): return False
	# Check shape
	if mc.objectType(mesh) == 'transform': mesh = mc.listRelatives(mesh,s=True,ni=True,pa=True)
	if not mesh: return False
	if mc.objectType(mesh[0]) != 'mesh': return False
	
	# Return result
	return True
	
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

def getMeshVertexIter(mesh):
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
	# Return result
	return meshVertIt

def getMeshFaceIter(mesh):
	'''
	Create an MItMeshPolygon class object from the specified polygon mesh
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
	meshFaceIt = OpenMaya.MItMeshPolygon(meshPath)
	# Return result
	return meshFaceIt

def getMeshEdgeIter(mesh):
	'''
	Create an MItMeshEdge class object from the specified polygon mesh
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
	meshEdgeIt = OpenMaya.MItMeshEdge(meshPath)
	# Return result
	return meshEdgeIt

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
	normalArray = OpenMaya.MFloatVectorArray()
	meshFn.getVertexNormals(False,normalArray,sampleSpace)
	
	# Return result
	return normalArray
	
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
	faceEdgeArray = OpenMaya.MIntArray()
	faceIter.setIndex(faceId,faceIdPtr)
	faceIter.getEdges(faceEdgeArray)
	
	# Return result
	return list(faceEdgeArray)
	
def closestPoint(mesh,point=(0,0,0)):
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
	pos = OpenMaya.MPoint(point[0],point[1],point[2],1.0)
	cpos = OpenMaya.MPoint()
	
	# Get MFnMesh
	meshFn = getMeshFn(mesh)
	
	# Get closestPoint
	meshFn.getClosestPoint(pos,cpos,OpenMaya.MSpace.kWorld)
	
	# Return result
	return (cpos.x,cpos.y,cpos.z)

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
	pos = OpenMaya.MPoint(point[0],point[1],point[2],1.0)
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
	pos = OpenMaya.MPoint(point[0],point[1],point[2],1.0)
	
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
	pos = OpenMaya.MPoint(point[0],point[1],point[2],1.0)
	
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
	pnt = OpenMaya.MPoint(point[0],point[1],point[2],1.0)
	uv = OpenMaya.MScriptUtil()
	uv.createFromList([0.0,0.0],2)
	uvPtr = uv.asFloat2Ptr()
	meshFn.getUVAtPoint(pnt,uvPtr,OpenMaya.MSpace.kWorld,uvSet)
	
	# Return result
	return (uv.getFloat2ArrayItem(uvPtr,0,0),uv.getFloat2ArrayItem(uvPtr,0,1))

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
	if not isMesh(mesh): raise Exception('Object '+mesh+' is not a valid mesh!')
	
	# Get transform position
	pos = mc.xform(transform,q=True,ws=True,rp=True)
	
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
	
	# Get closest vertex
	pos = mc.xform(obj,q=True,ws=True,rp=True)
	vtx = closestVertex(mesh,pos)
	
	# Add vertex attribute
	if not mc.objExists(obj+'.'+attr):
		mc.addAttr(obj,ln=attr,at='long',dv=0,k=True)
	mc.setAttr(obj+'.'+attr,vtx)
	
	# Return result
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

def allIntersections(mesh,source,direction,testBothDirections=False,maxDist=9999):
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
	
	# Return intersection hit point
	return [(hitPtArray[i][0],hitPtArray[i][1],hitPtArray[i][2]) for i in range(hitPtArray.length())]

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
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# Check prefix
	if not prefix: prefix = mesh
	
	# Get vertices
	componentList = glTools.utils.component.getComponentStrList(mesh)
	
	# Iterate over component list
	locatorList = []
	for i in range(len(componentList)):
		
		# Get componet position
		pos = mc.pointPosition(componentList[i])
		
		# Build vertex locator
		loc = mc.spaceLocator(n=prefix+'_vtx'+str(i)+'_loc')[0]
		mc.move(pos[0],pos[1],pos[2],loc,a=True,ws=True)
		mc.setAttr(loc+'.localScale',locatorScale,locatorScale,locatorScale)
		locatorList.append(loc)
		
		# Freeze vertex
		mc.move(0,0,0,componentList[i],a=True,ws=True)
		
	# Freeze mesh
	deformer = mc.deformer(mesh,type='cluster')
	mc.delete(mesh,constructionHistory=True)
	
	# Connect locators
	for i in range(len(locatorList)):
		mc.connectAttr(locatorList[i]+'.worldPosition[0]',mesh+'.controlPoints['+str(i)+']',f=True)
	
	# Return result
	return locatorList

def getCornerVertexIds(mesh):
	'''
	Return a list of vertex Ids for vertices connected to only 2 edges
	@param mesh: Polygon mesh to find corner vertices for
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
	
def vertexConnectivityList(mesh,faceConnectivity=False):
	'''
	Return a vertex connectivity list for the specified mesh
	@param mesh: Polygon mesh to return vertex connectivity list for
	@type mesh: str
	@param faceConnectivity: Use face connectivity instead of edge connectivity
	@type faceConnectivity: str
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# Get MItMeshVertex
	meshVertIt = getMeshVertexIter(mesh)
	if faceConnectivity: meshFaceIt = getMeshFaceIter(mesh)
	
	# Initialize connectivity list
	vertexConnectList = []
	
	# Build vertex connectivity list
	vertexConnectIntArray = OpenMaya.MIntArray()
	if faceConnectivity: faceConnectIntArray = OpenMaya.MIntArray()
	
	# Iterate over vertices
	meshVertIt.reset()
	for i in range(meshVertIt.count()):
		
		# Check connectivity type
		if faceConnectivity:
			
			# Face connectivity
			vertexConnectSet = set([])
			meshVertIt.getConnectedFaces(faceConnectIntArray)
			for f in faceConnectIntArray:
				meshFaceIt.setIndex(f,OpenMaya.MScriptUtil().asIntPtr())
				meshFaceIt.getVertices(vertexConnectIntArray)
				vertexConnectSet = vertexConnectSet.union(set(vertexConnectIntArray))
			vertexConnectSet.remove(i)
			vertexConnectList.append(list(vertexConnectSet))
			
		else:
			
			# Edge connectivity
			meshVertIt.getConnectedVertices(vertexConnectIntArray)
			vertexConnectList.append(list(vertexConnectIntArray))
		
		# Iterate to next vertex
		meshVertIt.next()
	
	# Return result
	return vertexConnectList

def duplicateAndConnect(meshList):
	'''
	polyDuplicateAndConnect wrapper for multiple meshes
	@param meshList: List of polygon mesh objects to run polyDuplicateAndConnect on. 
	@type meshList: list
	'''
	# Initialize return value
	dupList = []
	
	# Duplicate and connect
	for mesh in meshList:
		mc.select(mesh)
		mc.polyDuplicateAndConnect()
		dup = mc.ls(sl=True,l=True)
		dupList.append(dup[0])
	
	# Return duplicate list
	return dupList

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
