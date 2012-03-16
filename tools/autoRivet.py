import maya.cmds as mc

import maya.OpenMaya as OpenMaya

import glTools.utils.base
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
