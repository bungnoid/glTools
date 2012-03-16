import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.mesh
import glTools.utils.dnBurlyDeformer

import glTools.tools.symmetryTable

def mirrorWeights(dnBurlyDeformer,sourceInfluence,targetInfluence,axis='x',posToNeg=True,symmetrical=True,refMesh=''):
	'''
	'''
	# Check dnBurlyDeformer
	if not glTools.utils.dnBurlyDeformer.isBurlyDeformer(dnBurlyDeformer):
		raise Exception('A valid dnBurlyDeformer must be provided!')
	
	# Get mirror axis
	axis = axis.lower()
	if not ['x','y','z'].count(axis): raise Exception('Invalid axis value!!')
	axisInd = {'x':0,'y':1,'z':2}[axis]
	
	# Get affected geometry
	affectedGeo = glTools.utils.deformer.getAffectedGeometry(dnBurlyDeformer).keys()[0]
	affectedGeoPntNum = mc.polyEvaluate(affectedGeo,v=True)
	
	# Get influence indices
	sourceInfluenceIndex = glTools.utils.dnBurlyDeformer.getInfluenceIndex(dnBurlyDeformer,sourceInfluence)
	targetInfluenceIndex = glTools.utils.dnBurlyDeformer.getInfluenceIndex(dnBurlyDeformer,targetInfluence)
	
	# Get source influence weights
	sourceInfluenceWeights = glTools.utils.dnBurlyDeformer.getInfluenceWeights(dnBurlyDeformer,sourceInfluence)
	sourceInfluenceWeightsNum = len(sourceInfluenceWeights)
	if sourceInfluenceWeightsNum < affectedGeoPntNum:
		[sourceInfluenceWeights.append(0.0) for i in range(sourceInfluenceWeightsNum,affectedGeoPntNum)]
	
	# Initialize target influence weights
	targetInfluenceWeights = [0 for i in range(affectedGeoPntNum)]
	
	# Check refMesh
	if not refMesh: refMesh = affectedGeo
	
	# Check symmetrical
	if symmetrical:
		
		# Build symmetry table
		sTable = glTools.tools.symmetryTable.SymmetryTable()
		symTable = sTable.buildSymTable(refMesh)
		
		posIndexList = sTable.positiveIndexList
		negIndexList = sTable.negativeIndexList
		
		# Build target influence weights
		for i in range(len(sourceInfluenceWeights)):
			
			# Check self mirror
			if sourceInfluenceIndex == targetInfluenceIndex:
				if (posToNeg and negIndexList.count(i)) or (not posToNeg and posIndexList.count(i)):
					# Mirror weight
					targetInfluenceWeights[symTable[i]] = sourceInfluenceWeights[i]
				else:
					# Copy Weight
					targetInfluenceWeights[i] = sourceInfluenceWeights[i]
			else:
				# Mirror weight
				targetInfluenceWeights[symTable[i]] = sourceInfluenceWeights[i]
	
	else:
		
		# Build asymmetry table
		asymTable = []
		for i in range(affectedGeoPntNum):
			
			# Get source vertex position
			pos = glTools.utils.base.getPosition(refMesh+'.vtx['+str(i)+']')
			
			# Check self mirror
			if sourceInfluenceIndex == targetInfluenceIndex:
				if (posToNeg and pos[axisInd] < 0.0) or (not posToNeg and pos[axisInd] > 0.0):
					asymTable.append(i)
					continue
			
			# Get mirror position
			mPos = pos
			mPos[axisInd] *= -1.0
			
			# Get closest vertex to mirror position
			mVtx = glTools.utils.mesh.closestVertex(refMesh,mPos)
			asymTable.append(mVtx)
			
		# Build target influence weights
		for i in range(len(sourceInfluenceWeights)):
			targetInfluenceWeights[asymTable[i]] = sourceInfluenceWeights[i]
		
	# Set influence weights
	glTools.utils.dnBurlyDeformer.setInfluenceWeights(dnBurlyDeformer,targetInfluence,targetInfluenceWeights)
	
	# Rebind influence
	mm.eval('dnBurlyDeformer -rebindMuscle "'+dnBurlyDeformer+'" "'+targetInfluence+'"')

def mirrorWeightsAll(dnBurlyDeformer,search='L_',replace='R_',axis='x',posToNeg=True,symmetrical=True,refMesh=''):
	'''
	'''
	# Check dnBurlyDeformer
	if not glTools.utils.dnBurlyDeformer.isBurlyDeformer(dnBurlyDeformer):
		raise Exception('A valid dnBurlyDeformer must be provided!')
	
	# Get mirror axis
	axis = axis.lower()
	if not ['x','y','z'].count(axis): raise Exception('Invalid axis value!!')
	axisInd = {'x':0,'y':1,'z':2}[axis]
	
	# Get influence list
	influenceList = glTools.utils.dnBurlyDeformer.getInfluenceList(dnBurlyDeformer)
	
	# Get influence pivot list
	if not search and not replace:
		influencePivList = []
		for influence in influenceList:
			influencePivList.append(mc.xform(influence,q=True,ws=True,rp=True))
	
	# Get mirrored influence list
	mInfluenceList = {}
	sourceInfluenceList = []
	for i in range(len(influenceList)):
		if search and replace:
			# Search and replace names to find mirror influence
			if influenceList[i].startswith(search): mInf = influenceList[i].replace(search,replace)
			elif influenceList[i].startswith(replace): continue
			else: mInf = influenceList[i]
			mInfluenceList[influenceList[i]] = mInf
			sourceInfluenceList.append(influenceList[i])
		else:
			# Determine mirror influence based on pivot position
			piv = influencePivList[i]
			piv[axisInd] *= -1
			mPiv = glTools.utils.base.getMPoint(piv)
			minDist = 999999.0
			mInf = influenceList[i]
			for n in range(len(influenceList)):
				infPiv = glTools.utils.base.getMPoint(influencePivList[n])
				dist = (mPiv - infPiv).length()
				if dist - minDist:
					mInf = influenceList[n]
					minDist = dist
			mInfluenceList[influenceList[i]] = mInf
	
	# Iterate over influence list
	for influence in sourceInfluenceList:
		print('dnBurlyDeformer.mirrorWeightsAll: "'+influence+'" -> "'+mInfluenceList[influence]+'"')
		mirrorWeights(dnBurlyDeformer,influence,mInfluenceList[influence],axis,posToNeg,symmetrical,refMesh)


def flipWeights(sourceDeformer,targetDeformer,sourceInfluence,targetInfluence,axis='x'):
	'''
	'''
	# Check dnBurlyDeformer
	if not glTools.utils.dnBurlyDeformer.isBurlyDeformer(sourceDeformer):
		raise Exception('A valid source dnBurlyDeformer must be provided!')
	
	if not isBurlyDeformer(targetDeformer):
		raise Exception('A valid target dnBurlyDeformer must be provided!')
	
	# Get influence indices
	sourceInfluenceIndex = glTools.utils.dnBurlyDeformer.getInfluenceIndex(sourceDeformer,sourceInfluence)
	targetInfluenceIndex = glTools.utils.dnBurlyDeformer.getInfluenceIndex(targetDeformer,targetInfluence)
	
	# Get affected geometry
	sourceGeo = glTools.utils.deformer.getAffectedGeometry(sourceDeformer).keys()[0]
	targetGeo = glTools.utils.deformer.getAffectedGeometry(targetDeformer).keys()[0]
	sourceGeoPntNum = mc.polyEvaluate(sourceGeo,v=True)
	targetGeoPntNum = mc.polyEvaluate(targetGeo,v=True)
	
	# Get source influence weights
	sourceInfluenceWeights = glTools.utils.dnBurlyDeformer.getInfluenceWeights(dnBurlyDeformer,sourceInfluence)
	
	# Get affected geometry
	targetInfluenceWeights = [0.0 for i in range(targetGeoPntNum)]
	
	# Build vertex correspondence table
	vtxTable = []
	for i in range(sourceGeoPntNum):
		# Get source vertex position
		pos = glTools.utils.base.getPosition(sourceGeo+'.vtx['+str(i)+']')
		
		# Get mirror position
		mPos = pos
		mPos[axisInd] *= -1.0
		
		# Get closest vertex to mirror position
		mVtx = glTools.utils.mesh.closestVertex(targetGeo,mPos)
		vtxTable.append(mVtx)
		
	# Build target influence weights
	for i in range(len(sourceInfluenceWeights)):
		targetInfluenceWeights[vtxTable[i]] = sourceInfluenceWeights[i]
	
	# Set influence weights
	glTools.utils.dnBurlyDeformer.setInfluenceWeights(targetDeformer,targetInfluence,targetInfluenceWeights)
	
	# Rebind influence
	mm.eval('dnBurlyDeformer -rebindMuscle "'+targetDeformer+'" "'+targetInfluence+'"')

def flipWeightsAll(sourceDeformer,targetDeformer,search='L_',replace='R_',axis='x'):
	'''
	'''
	# Check dnBurlyDeformer
	if not glTools.utils.dnBurlyDeformer.isBurlyDeformer(sourceDeformer):
		raise Exception('A valid source dnBurlyDeformer must be provided!')
	
	if not isBurlyDeformer(targetDeformer):
		raise Exception('A valid target dnBurlyDeformer must be provided!')
	
	# Get mirror axis
	axis = axis.lower()
	if not ['x','y','z'].count(axis): raise Exception('Invalid axis value!!')
	axisInd = {'x':0,'y':1,'z':2}[axis]
	
	# Get influence list
	sourceInfluenceList = glTools.utils.dnBurlyDeformer.getInfluenceList(sourceDeformer)
	targetInfluenceList = glTools.utils.dnBurlyDeformer.getInfluenceList(targetDeformer)
	
	# Get influence pivot lists
	if not search and not replace:
		sourceInfluencePivList = []
		targetInfluencePivList = []
		for sourceInfluence in sourceInfluencePivList:
			sourceInfluencePivList.append(mc.xform(sourceInfluence,q=True,ws=True,rp=True))
		for targetInfluence in targetInfluencePivList:
			targetInfluencePivList.append(mc.xform(targetInfluence,q=True,ws=True,rp=True))
	
	# Get mirrored influence list
	mInfluenceList = {}
	for i in range(len(sourceInfluenceList)):
		if search and replace:
			# Search and replace names to find mirror influence
			if sourceInfluenceList[i].startswith(search):
				mInf = sourceInfluenceList[i].replace(search,replace)
			else:
				mInf = influenceList[i]
			mInfluenceList[influenceList[i]] = mInf
		else:
			# Determine mirror influence based on pivot position
			piv = sourceInfluencePivList[i]
			piv[axisInd] *= -1
			mPiv = glTools.utils.base.getMPoint(piv)
			minDist = 999999.0
			mInf = influenceList[i]
			for t in range(len(targetInfluencePivList)):
				tPiv = glTools.utils.base.getMPoint(targetInfluencePivList[t])
				dist = (mPiv - tPiv).length()
				if dist - minDist:
					mInf = targetInfluenceList[n]
					minDist = dist
			mInfluenceList[sourceInfluenceList[i]] = mInf
	
	# Iterate over influence list
	for sourceInfluence in sourceInfluenceList:
		print('dnBurlyDeformer.flipWeightsAll: "'+influence+'" -> "'+mInfluenceList[influence]+'"')
		flipWeights(sourceDeformer,targetDeformer,sourceInfluence,mInfluenceList[sourceInfluence],axis)

