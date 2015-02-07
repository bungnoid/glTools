import maya.cmds as mc

import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.component
import glTools.utils.mesh
import glTools.utils.stringUtils
import glTools.utils.surface

def autoRivet(createRivetTransform=True,suffix='rvt'):
	'''
	'''
	# Get User Selection
	sel = mc.ls(sl=1)
	# Check Selection
	if not len(sel) == 2:
		raise Exception('Select object to rivet and then the target mesh!')
	
	# Determine rivet object and mesh
	rvtObj = sel[0]
	mesh = sel[1]
	prefix = glTools.utils.stringUtils.stripSuffix(rvtObj)
	
	# Get rivet object position
	pos = glTools.utils.base.getPosition(rvtObj)
	pt = OpenMaya.MPoint(pos[0],pos[1],pos[2],1.0)
	
	# Get closest face on mesh
	faceId = glTools.utils.mesh.closestFace(mesh,pos)
	
	# =========================
	# - Determine Rivet Edges -
	# =========================
	
	edgeId1 = -1
	edgeId2 = -1
	
	# Create MItMeshEdge
	edgeIter = glTools.utils.mesh.getMeshEdgeIter(mesh)
	
	# Create edgeId MScriptUtil
	edgeIdUtil = OpenMaya.MScriptUtil()
	edgeIdUtil.createFromInt(0)
	edgeIdPtr = edgeIdUtil.asIntPtr()
	
	# Get face edges
	faceEdges = glTools.utils.mesh.getFaceEdgeIndices(mesh,faceId)
	
	# Get closest edge
	maxDist = 9999.0
	for edgeId in faceEdges:
		edgeIter.setIndex(edgeId,edgeIdPtr)
		edgePt = edgeIter.center(OpenMaya.MSpace.kWorld)
		edgeDist = (edgePt - pt).length()
		if edgeDist < maxDist:
			edgeId1 = edgeId
			maxDist = edgeDist
	
	# Set current edge
	edgeIter.setIndex(edgeId1,edgeIdPtr)
	
	# Get opposing edge
	faceEdges.remove(edgeId1)
	for edgeId in faceEdges:
		edgeId2 = edgeId
		# Check edge connectivity
		if not edgeIter.connectedToEdge(edgeId): break
	
	# ========================
	# - Create Utility Nodes -
	# ========================
	
	# Rivet Edge 1
	edgeCrv1 = prefix+'_edge'+str(edgeId1)+'_rivet_curveFromMeshEdge'
	if not mc.objExists(edgeCrv1):
		edgeCrv1 = mc.createNode('curveFromMeshEdge',n=edgeCrv1)
		mc.setAttr(edgeCrv1+'.edgeIndex[0]',edgeId1)
		mc.connectAttr(mesh+'.worldMesh[0]',edgeCrv1+'.inputMesh',f=True)
	
	# Rivet Edge 2
	edgeCrv2 = prefix+'_edge'+str(edgeId2)+'_rivet_curveFromMeshEdge'
	if not mc.objExists(edgeCrv2):
		edgeCrv2 = mc.createNode('curveFromMeshEdge',n=edgeCrv2)
		mc.setAttr(edgeCrv2+'.edgeIndex[0]',edgeId2)
		mc.connectAttr(mesh+'.worldMesh[0]',edgeCrv2+'.inputMesh',f=True)
		
	# Rivet Loft
	rivetLoft = prefix+'_face'+str(faceId)+'_rivet_loft'
	if not mc.objExists(rivetLoft):
		rivetLoft = mc.createNode('loft',n=rivetLoft)
		mc.connectAttr(edgeCrv1+'.outputCurve',rivetLoft+'.inputCurve[0]',f=True)
		mc.connectAttr(edgeCrv2+'.outputCurve',rivetLoft+'.inputCurve[1]',f=True)
	
	# Rivet Point on Surface Info
	rivetPosi = prefix+'_face'+str(faceId)+'_rivet_pointOnSurfaceInfo'
	rivetPosi = mc.createNode('pointOnSurfaceInfo',n=rivetPosi)
	mc.connectAttr(rivetLoft+'.outputSurface',rivetPosi+'.inputSurface')
	
	# ===========================
	# -  Get Rivet UV Parameter -
	# ===========================
	
	# Build Temp Surface
	tmpSrfShape = mc.createNode('nurbsSurface')
	tmpSrf = mc.listRelatives(tmpSrfShape,p=True,pa=True)[0]
	mc.connectAttr(rivetLoft+'.outputSurface',tmpSrfShape+'.create',f=True)
	
	# Get closest point on surface
	uv = glTools.utils.surface.closestPoint(tmpSrf,pos)
	
	# Set rivet parameter
	mc.setAttr(rivetPosi+'.parameterU',uv[0])
	mc.setAttr(rivetPosi+'.parameterV',uv[1])
	
	# Delete Temp Surface
	mc.delete(tmpSrf)
	
	# ==========================
	# - Attach Rivet Transform -
	# ==========================
	
	# Determine rivet transform
	rvtTransform = rvtObj
	if createRivetTransform: rvtTransform = mc.group(em=True,n=prefix+'_rvt')
	
	# Connect rivet transform
	mc.connectAttr(rivetPosi+'.position',rvtTransform+'.t',f=True)
	
	# Parent to rivet transform
	if createRivetTransform: mc.parent(rvtObj,rvtTransform)
	
	# =================
	# - Return Result -
	# =================
	
	return rvtTransform

def meshFaceConstraint(face='',transform='',orient=True,prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not prefix: prefix = 'meshFaceConstraint'
	
	if not face:
		faceList = mc.filterExpand(sm=34)
		if not faceList: raise Exception('No mesh face specified for constraint!')
		face = faceList[0]
	if not transform:
		transformList = mc.ls(sl=True,type='transform')
		if not transformList: transformList = mc.spaceLocator(n=prefix+'_locator')
		transform = transformList[0]
	
	# ======================
	# - Get Face UV Center -
	# ======================
	
	# Get Face Details
	mesh = mc.ls(face,o=True)[0]
	faceId = glTools.utils.component.index(face)
	
	# Get Mesh Face Function Set
	uArray = OpenMaya.MFloatArray()
	vArray = OpenMaya.MFloatArray()
	faceIdUtil = OpenMaya.MScriptUtil()
	faceIdUtil.createFromInt(0)
	faceIdPtr = faceIdUtil.asIntPtr()
	faceIt = glTools.utils.mesh.getMeshFaceIter(mesh)
	faceIt.setIndex(faceId,faceIdPtr)
	
	# Get UV Center
	uvSet = mc.polyUVSet(mesh,q=True,cuv=True)
	faceIt.getUVs(uArray,vArray)
	uArray = list(uArray)
	vArray = list(vArray)
	uvCount = len(uArray)
	u = 0.0
	v = 0.0
	for i in range(uvCount):
		u += (uArray[i] / uvCount)
		v += (vArray[i] / uvCount)
	
	# =====================
	# - Create Constraint -
	# =====================
	
	r = mc.getAttr(transform+'.r')[0]
	
	meshCon = mc.pointOnPolyConstraint(mesh,transform,n=prefix+'_pointOnPolyConstraint')[0]
	wtAlias = mc.pointOnPolyConstraint(meshCon,q=True,wal=True)[0]
	mc.setAttr(meshCon+'.'+wtAlias.replace('W0','U0'),u)
	mc.setAttr(meshCon+'.'+wtAlias.replace('W0','V0'),v)
	
	# Orient
	if not orient:
		rxConn = mc.listConnections(transform+'.rx',s=True,d=False,p=True)[0]
		mc.disconnectAttr(rxConn,transform+'.rx')
		ryConn = mc.listConnections(transform+'.ry',s=True,d=False,p=True)[0]
		mc.disconnectAttr(ryConn,transform+'.ry')
		rzConn = mc.listConnections(transform+'.rz',s=True,d=False,p=True)[0]
		mc.disconnectAttr(rzConn,transform+'.rz')
		mc.setAttr(transform+'.r',*r)
	
	# =================
	# - Return Result -
	# =================
	
	return meshCon
	
def meshVertexConstraint(vertex='',transform='',orient=True,prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not prefix: prefix = 'meshVertexConstraint'
	
	if not vertex:
		vtxList = mc.filterExpand(sm=31)
		if not vtxList: raise Exception('No mesh vertex specified for constraint!')
		vertex = vtxList[0]
	if not transform:
		transformList = mc.ls(sl=True,type='transform')
		if not transformList: transformList = mc.spaceLocator(n=prefix+'_locator')
		transform = transformList[0]
	
	# =================
	# - Get Vertex UV -
	# =================
	
	# Get Vertex Details
	mesh = mc.ls(vertex,o=True)[0]
	vtxId = glTools.utils.component.index(vertex)
	
	# Get Mesh Vertex Function Set
	uArray = OpenMaya.MFloatArray()
	vArray = OpenMaya.MFloatArray()
	faceArray = OpenMaya.MIntArray()
	vtxIdUtil = OpenMaya.MScriptUtil()
	vtxIdUtil.createFromInt(0)
	vtxIdPtr = vtxIdUtil.asIntPtr()
	vtxIt = glTools.utils.mesh.getMeshVertexIter(mesh)
	vtxIt.setIndex(vtxId,vtxIdPtr)
	
	# Get UV Center
	uvSet = mc.polyUVSet(mesh,q=True,cuv=True)
	vtxIt.getUVs(uArray,vArray,faceArray)
	uArray = list(uArray)
	vArray = list(vArray)
	u = uArray[0]
	v = vArray[0]
	
	# =====================
	# - Create Constraint -
	# =====================
	
	r = mc.getAttr(transform+'.r')[0]
	
	meshCon = mc.pointOnPolyConstraint(mesh,transform,n=prefix+'_pointOnPolyConstraint')[0]
	wtAlias = mc.pointOnPolyConstraint(meshCon,q=True,wal=True)[0]
	mc.setAttr(meshCon+'.'+wtAlias.replace('W0','U0'),u)
	mc.setAttr(meshCon+'.'+wtAlias.replace('W0','V0'),v)
	
	# Orient
	if not orient:
		rxConn = mc.listConnections(transform+'.rx',s=True,d=False,p=True)[0]
		mc.disconnectAttr(rxConn,transform+'.rx')
		ryConn = mc.listConnections(transform+'.ry',s=True,d=False,p=True)[0]
		mc.disconnectAttr(ryConn,transform+'.ry')
		rzConn = mc.listConnections(transform+'.rz',s=True,d=False,p=True)[0]
		mc.disconnectAttr(rzConn,transform+'.rz')
		mc.setAttr(transform+'.r',*r)
	
	# =================
	# - Return Result -
	# =================
	
	return meshCon

def meshFaceConstraintList(faceList=[],transformList=[],orient=True,prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Face List
	if not faceList:
		faceList = mc.filterExpand(sm=34)
		if not faceList: raise Exception('No mesh face list specified for constraint!')
	
	# Transform List
	if not transformList:
		transformList = ['' for vtx in vtxList]
	
	# Vertex / Face list length
	if not len(faceList) == len(transformList):
		raise Exception('Face and Transform list length mis-match!')
	
	# ======================
	# - Create Constraints -
	# ======================
	
	constraintList = []
	for i in range(len(faceList)):
		mc.select(cl=True)
		itPrefix = prefix+'_'+str(i)
		constraintList.append(meshFaceConstraint(faceList[i],transformList[i],orient=orient,prefix=itPrefix))
	
	# =================
	# - Return Result -
	# =================
	
	return constraintList

def meshVertexConstraintList(vtxList=[],transformList=[],orient=True,prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Vertex List
	if not vtxList:
		vtxList = mc.filterExpand(sm=31)
		if not vtxList: raise Exception('No mesh vertex list specified for constraint!')
	
	# Transform List
	if not transformList:
		transformList = ['' for vtx in vtxList]
	
	# Vertex / Transform list length
	if not len(vtxList) == len(transformList):
		raise Exception('Vertex and Transform list length mis-match!')
	
	# ======================
	# - Create Constraints -
	# ======================
	
	constraintList = []
	for i in range(len(vtxList)):
		mc.select(cl=True)
		itPrefix = prefix+'_'+str(i)
		constraintList.append(meshVertexConstraint(vtxList[i],transformList[i],orient=orient,prefix=itPrefix))
	
	# =================
	# - Return Result -
	# =================
	
	return constraintList
