import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.utils.mesh
import glTools.utils.skinCluster

def smoothSkinWeights(vtxList,distanceWeighted=False,faceConnectivity=False):
	'''
	'''
	# Flatten point list
	vtxList = mc.ls(vtxList,fl=True)
	
	# Get object selection from point list
	selList = OpenMaya.MSelectionList()
	selPath = OpenMaya.MDagPath()
	selObj = OpenMaya.MObject()
	[selList.add(vtx) for vtx in vtxList]
	objCount = selList.length()
	
	# For each object point selection
	for i in range(objCount):
		
		# Get selection elements
		selList.getDagPath(i,selPath,selObj)
		mesh = selPath.partialPathName()
		
		# =================
		# - Get Mesh Data -
		# =================
		
		# Get vertex connectivity
		vtxConn = glTools.utils.mesh.vertexConnectivityList(mesh,faceConnectivity)
		
		# Get expanded id array
		idArray = OpenMaya.MIntArray() 
		OpenMaya.MFnSingleIndexedComponent(selObj).getElements(idArray)
		exIdArray = set([])
		for ind in idArray: [exIdArray.add(n) for n in vtxConn]
		exIdArray = list(exIdArray)
		
		exVtxSel = OpenMaya.MSelectionList()
		exVtxPath = OpenMaya.MDagPath()
		exVtxObj = OpenMaya.MObject()
		[exVtxSel.add(mesh+'.vtx['+str(exId)+']') for exId in exIdArray]
		exVtxSel.getDagPath(0,exVtxPath,exVtxObj)
		
		ptList = []
		if distanceWeighted: ptList = glTools.utils.mesh.getPointArray(mesh)
		
		# ============================
		# - Get Current Skin Weights -
		# ============================
		
		# Get skinCluster
		skin = glTools.utils.skinCluster.findRelatedSkinCluster(mesh)
		skinFn = glTools.utils.skinCluster.getSkinClusterFn(skin)
		
		# Get influence list
		infArray = OpenMaya.MDagPathArray()
		skinFn.influenceObjects(infList)
		infList = [infArray[i].partialPathName() for i in range(infArray.length())]
		infIndList = [glTools.utils.skinCluster.getInfluencePhysicalIndex(skin,inf) for inf in infList]
		
		# Get weights for vertex selection
		wtList = OpenMaya.MDoubleArray()
		infCountPtr = OpenMaya.MScriptUtil().asIntPtr()
		skinFn.getWeights(exVtxPath,exVtxObj,wtList,infCountPtr)
		
		"""
		# Build influence centric weight dictionary
		wtDict = {}
		for inf in infList: wtDict[inf] = []
		for wt in range(len(wtList)):
			infInd = wt % len(infList)
			wtDict[infInd].append(wtList[wt])
		"""
		
		# =======================
		# - Smooth Skin Weights -
		# =======================
		
		smWtList = []
		
		for vtx in idArray:
			
			wt = 0.0
