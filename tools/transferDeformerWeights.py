import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.deformer
import glTools.utils.mesh

def transferWeights(sourceMesh,targetMesh,deformer,invDist=False,vertexList=[]):
	'''
	Transfer deformer weights from one mesh to another
	@param sourceMesh: The mesh that you want to transfer weights from
	@type sourceMesh: str
	@param targetMesh: The mesh that you want to transfer weights to
	@type targetMesh: str
	@param deformer: The deformer that you want to transfer weights from
	@type deformer: str
	@param invDist: Use the inverse distance weighted average method for interpolating weights
	@type invDist: bool
	@param vertexList: List of vertices to transfer weights to
	@type vertexList: list
	'''
	# Get mesh points
	tPtArray = glTools.utils.base.getMPointArray(targetMesh)
	
	# Get number of vertices in source mesh
	numSourcePts = mc.polyEvaluate(sourceMesh,v=True)
	
	# Get source weights
	wtArray = glTools.utils.deformer.getWeights(deformer,sourceMesh)
	sWeightInd = glTools.utils.deformer.getDeformerSetMemberIndices(deformer,sourceMesh)
	sWeightArray = [0.0 for i in range(numSourcePts)]
	for i in range(len(sWeightInd)): sWeightArray[sWeightInd[i]] = wtArray[i]
	
	# Cycle through points
	tWeightsArray = []
	if not vertexList: vertexList = range(tPtArray.length())
	for i in vertexList:
		
		# Get target point
		tPt = (tPtArray[i][0],tPtArray[i][1],tPtArray[i][2])
		
		# Calculate averaged weight of source face vertices
		wt = 0.0
		if invDist:
			# Inverse distance weighted average
			vtxWt = glTools.utils.mesh.closestPointWeightedAverage(sourceMesh,tPt)
			for vtx in vtxWt.keys(): wt += sWeightArray[vtx] * vtxWt[vtx]
		else:
			# Standard average
			closestFace = glTools.utils.mesh.closestFace(sourceMesh,tPt)
			faceVtxList = glTools.utils.mesh.getFaceVertexIndices(sourceMesh,closestFace)
			for vtx in faceVtxList: wt += sWeightArray[vtx]
			wt /= len(faceVtxList)
		
		# Append value to target weight array
		tWeightsArray.append(wt)
	
	# Return result
	return tWeightsArray
