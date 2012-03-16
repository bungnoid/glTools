import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.mesh

def longestEdges(mesh,faceSel=[]):
	'''
	'''
	# Get mesh function sets
	meshFn = glTools.utils.mesh.getMeshFn(mesh)
	edgeIter = glTools.utils.mesh.getMeshEdgeIter(mesh)
	faceIter = glTools.utils.mesh.getMeshFaceIter(mesh)
	
	# Check face selection
	if faceSel:
		faceSel = mc.ls(faceSel,fl=1)
		selList = OpenMaya.MSelectionList()
		for face in faceSel: selList.add(face)
		meshPath = OpenMaya.MDagPath()
		compObj = OpenMaya.MObject()
		selList.getDagPath(0,meshPath,compObj)
		faceIter = OpenMaya.MItMeshPolygon(meshPath,compObj)
	
	# Get edge array wrapper
	faceEdges = OpenMaya.MIntArray()
	
	# Initialize longest edge list
	longEdgeList = []
	
	# Build edge ID pointer
	edgeId = OpenMaya.MScriptUtil()
	edgeId.createFromInt(0)
	edgeIdPtr = edgeId.asIntPtr()
	
	# Iterate through faces
	while not faceIter.isDone():
		# Reset max edge length
		maxEdgeLen = 0
		longEdge = -1
		# Get face edges
		faceIter.getEdges(faceEdges)
		# Iterate through edges
		for i in list(faceEdges):
			edgeIter.setIndex(i,edgeIdPtr)
			edgeLen = (edgeIter.point(0,OpenMaya.MSpace.kObject)-edgeIter.point(1,OpenMaya.MSpace.kObject)).length()
			if edgeLen > maxEdgeLen:
				longEdge = i
				maxEdgeLen = edgeLen
		longEdgeList.append(longEdge)
		faceIter.next()
	
	# Build selection list
	sel = [mesh+'.e['+str(i)+']' for i in longEdgeList]
	
	# Return result
	return sel
