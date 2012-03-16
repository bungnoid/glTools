import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base

def isBurlyDeformer(dnBurlyDeformer):
	'''
	'''
	# Check object exists
	if not mc.objExists(dnBurlyDeformer):
		print('dnBurlyDeformer "'+dnBurlyDeformer+'" does not exists!')
		return False
	# Check object is a valid dnBurlyDeformer
	if mc.objectType(dnBurlyDeformer) != 'dnBurlyDeformer':
		print('Object "'+dnBurlyDeformer+'" is not a vaild dnBurlyDeformer node!')
		return False
	
	# Retrun result
	return True

def getMusclePlug(dnBurlyDeformer):
	'''
	'''
	# Check dnBurlyDeformer
	if not isBurlyDeformer(dnBurlyDeformer):
		raise Exception('Object "'+dnBurlyDeformer+'" is not a valid dnBurlyDeformer!')
	
	# Get dnBurlyDeformer muscle attribute plug
	dnBurlyDeformerObj = glTools.utils.base.getMObject(dnBurlyDeformer)
	dnBurlyDeformerNode = OpenMaya.MFnDependencyNode(dnBurlyDeformerObj)
	musclePlug = dnBurlyDeformerNode.findPlug('muscle')
	
	# Return result
	return musclePlug

def getPointsPlug(dnBurlyDeformer,influence):
	'''
	'''
	# Check dnBurlyDeformer
	if not isBurlyDeformer(dnBurlyDeformer):
		raise Exception('Object "'+dnBurlyDeformer+'" is not a valid dnBurlyDeformer!')
	
	# Get dnBurlyDeformer muscle attribute plug
	musclePlug = getMusclePlug(dnBurlyDeformer)
	
	# Get influence index
	influenceIndex = getInfluenceIndex(dnBurlyDeformer,influence)
	
	# Go to influenceIndex of muscle plug
	musclePlug = musclePlug.elementByLogicalIndex(influenceIndex)
	pointsPlug = musclePlug.child(6) # muscle[i].points
	
	# Return result
	return pointsPlug
	
def getInfluenceIndexList(dnBurlyDeformer):
	'''
	'''
	# Check dnBurlyDeformer
	if not isBurlyDeformer(dnBurlyDeformer):
		raise Exception('Object "'+dnBurlyDeformer+'" is not a valid dnBurlyDeformer!')
	
	# Get dnBurlyDeformer muscle attribute plug
	musclePlug = getMusclePlug(dnBurlyDeformer)
	
	# Get Existing Array Attribute Indices
	indexArray = OpenMaya.MIntArray()
	indexCount = musclePlug.getExistingArrayAttributeIndices(indexArray)
	
	# Retrun result
	return list(indexArray)

def getInfluenceList(dnBurlyDeformer,shape=False):
	'''
	'''
	# Check dnBurlyDeformer
	if not isBurlyDeformer(dnBurlyDeformer):
		raise Exception('Object "'+dnBurlyDeformer+'" is not a valid dnBurlyDeformer!')
	
	# Get influence index list
	indexList = getInfluenceIndexList(dnBurlyDeformer)
	
	# Iterate through indices and build influence list
	influenceList = []
	for i in indexList:
		inf = mc.listConnections(dnBurlyDeformer+'.muscle['+str(i)+'].surface',s=True,d=False,sh=shape)
		if inf: influenceList.append(inf[0])
	
	# Return result
	return influenceList

def getInfluenceIndexData(dnBurlyDeformer,shape=False):
	'''
	'''
	# Check dnBurlyDeformer
	if not isBurlyDeformer(dnBurlyDeformer):
		raise Exception('Object "'+dnBurlyDeformer+'" is not a valid dnBurlyDeformer!')
	
	# Initialize influenceIndexData
	influenceIndexData = {}
	
	# Get dnBurlyDeformer muscle attribute plug and available indices
	musclePlug = getMusclePlug(dnBurlyDeformer)
	muscleIndexArray = OpenMaya.MIntArray()
	muscleIndexCount = musclePlug.getExistingArrayAttributeIndices(muscleIndexArray)
	if not muscleIndexCount: return influenceIndexData
	
	# Get Influence Index Data
	musclePlugConn = OpenMaya.MPlugArray()
	for index in list(muscleIndexArray):
		muscleIndPlug = musclePlug.elementByLogicalIndex(index).child(0)
		if muscleIndPlug.connectedTo(musclePlugConn,True,False):
			muscleSurface = OpenMaya.MFnDependencyNode(musclePlugConn[0].node()).name()
			if not shape: muscleSurface = mc.listRelatives(muscleSurface,p=True)[0]
			influenceIndexData[muscleSurface] = index
	
	# Return result
	return influenceIndexData

def getInfluenceIndex(dnBurlyDeformer,influence):
	'''
	'''
	# Check dnBurlyDeformer
	if not isBurlyDeformer(dnBurlyDeformer):
		raise Exception('Object "'+dnBurlyDeformer+'" is not a valid dnBurlyDeformer!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence "'+influence+'" does not exist!!')
	
	# Get influence transform
	influnceObj = glTools.utils.base.getMObject(influence)
	if not influnceObj.hasFn(OpenMaya.MFn.kTransform):
		influence = mc.listRelatives(influence,p=True)[0]
	
	# Get deformer influence list
	influenceData = getInfluenceIndexData(dnBurlyDeformer)
	
	# Get influence index
	if not influence in influenceData.keys():
		raise Exception('Influence "'+influence+'" does not affect dnBurlyDeformer "'+dnBurlyDeformer+'"!!')
	influenceIndex = influenceData[influence]
	
	# Return result
	return influenceIndex

def getInfluenceWeights(dnBurlyDeformer,influence):
	'''
	'''
	# Check dnBurlyDeformer
	if not isBurlyDeformer(dnBurlyDeformer):
		raise Exception('Object "'+dnBurlyDeformer+'" is not a valid dnBurlyDeformer!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence "'+influence+'" does not exist!!')
	
	# Get influence index
	influenceIndex = getInfluenceIndex(dnBurlyDeformer,influence)
	
	# Get inluence points plug
	pointsPlug = getPointsPlug(dnBurlyDeformer,influence)
	indexArray = OpenMaya.MIntArray()
	pointsPlug.getExistingArrayAttributeIndices(indexArray)
	indexArray = list(indexArray)
	
	# Get influence weights
	influenceWeights = []
	for i in indexArray:
		wt = mc.getAttr(dnBurlyDeformer+'.muscle['+str(influenceIndex)+'].points['+str(i)+'].pointWeight')
		influenceWeights.append(wt)
	
	# Return result
	return influenceWeights

def setInfluenceWeights(dnBurlyDeformer,influence,influenceWeights):
	'''
	'''
	# Check dnBurlyDeformer
	if not isBurlyDeformer(dnBurlyDeformer):
		raise Exception('Object "'+dnBurlyDeformer+'" is not a valid dnBurlyDeformer!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence "'+influence+'" does not exist!!')
	
	# Get influence index
	influenceIndex = getInfluenceIndex(dnBurlyDeformer,influence)
	
	# Set influence weights
	for i in range(len(influenceWeights)):
		mc.setAttr(dnBurlyDeformer+'.muscle['+str(influenceIndex)+'].points['+str(i)+'].pointWeight',influenceWeights[i])
	
def getPointsAffectedByInfluence(dnBurlyDeformer,influence,indicesOnly=False):
	'''
	'''
	# Check dnBurlyDeformer
	if not isBurlyDeformer(dnBurlyDeformer):
		raise Exception('Object "'+dnBurlyDeformer+'" is not a valid dnBurlyDeformer!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence "'+influence+'" does not exist!!')
	
	# Get influence weights
	influenceWeights = getInfluenceWeights(dnBurlyDeformer,influence)
	
	# Get affected mesh
	affectedGeo = glTools.utils.deformer.getAffectedGeometry(dnBurlyDeformer).keys()[0]
	
	# Get affected points
	if indicesOnly:
		affectedPoints = [i for i in range(len(influenceWeights)) if influenceWeights[i] > 0.0]
	else:
		affectedPoints = [affectedGeo+'.vtx['+str(i)+']' for i in range(len(influenceWeights)) if influenceWeights[i] > 0.0]
	
	# Return result
	return affectedPoints
