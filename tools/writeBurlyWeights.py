import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.mesh
import glTools.utils.skinCluster

import os.path

def writeBurlyWeights(mesh,skinCluster,influence,filePath):
	'''
	'''
	# Get basic procedure information
	burly = 'dnBurlyDeformer1'
	vtxCount = mc.polyEvaluate(mesh,v=True)
	inf = mc.ls(influence,l=True)
	
	# Check skinCluster
	if not glTools.utils.skinCluster.isSkinCluster(skinCluster):
		raise Exception('Object "'+skinCluster+'" is not a valid skinCluster!')
	# Get skinCluster Fn
	skinFn = glTools.utils.skinCluster.getSkinClusterFn(skinCluster)
	# Get influence dag path
	influencePath = glTools.utils.base.getMDagPath(influence)
	
	# Get points affected by influence
	infSelectionList = OpenMaya.MSelectionList()
	infWeightList = OpenMaya.MFloatArray()
	skinFn.getPointsAffectedByInfluence(influencePath,infSelectionList,infWeightList)
	infObjectPath = OpenMaya.MDagPath()
	infComponentList = OpenMaya.MObject()
	infSelectionList.getDagPath(0,infObjectPath,infComponentList)
	
	# Get affect point indices
	infComponentIndex = OpenMaya.MIntArray()
	infComponentIndexFn = OpenMaya.MFnSingleIndexedComponent(infComponentList)
	infComponentIndexFn.getElements(infComponentIndex)
	infComponentIndex = list(infComponentIndex)
	
	# Get affect point position and normal arrays
	infComponentPosArray = OpenMaya.MPointArray()
	infComponentNormArray = OpenMaya.MVectorArray()
	infComponentVtxIt = OpenMaya.MItMeshVertex(infObjectPath,infComponentList)
	normal = OpenMaya.MVector()
	while not infComponentVtxIt.isDone():
		infComponentPosArray.append(infComponentVtxIt.position(OpenMaya.MSpace.kWorld))
		infComponentVtxIt.getNormal(normal)
		infComponentNormArray.append(normal)
		infComponentVtxIt.next()
	
	# Open file
	fileId = open(filePath, "w")
	
	# Header
	header = [	'<?xml version="1.0" standalone="no" ?>\n',
				'<dnWeights type="dnBurlyDeformer" version="1.0" name="'+burly+'">\n',
				'\t<Map name="'+inf[0]+'">\n',
				'\t\t<Topology vertexCount="'+str(vtxCount)+'"/>\n'	]
	fileId.writelines(header)
	
	# Weights
	weights = ['\t\t<Weights>\n']
	for i in range(len(infComponentIndex)):
		if not i%5: weights.append('\t\t\t')
		weights.append(str(infWeightList[i]) + ' ')
		if i%5 == 4: weights.append('\n')
	weights.append('\n\t\t</Weights>\n')
	fileId.writelines(weights)
	
	# Indices
	indices = ['\t\t<Indices>\n']
	for i in range(len(infComponentIndex)):
		if not i%10: indices.append('\t\t\t')
		indices.append(str(infComponentIndex[i]) + ' ')
		if i%10 == 9: indices.append('\n')
	indices.append('\n\t\t</Indices>\n')
	fileId.writelines(indices)
	
	# Position
	pos = ['\t\t<Positions>\n']
	for i in range(len(infComponentIndex)):
		if not i%2: pos.append('\t\t\t')
		pos.append(str(infComponentPosArray[i][0])+' '+str(infComponentPosArray[i][1])+' '+str(infComponentPosArray[i][2])+' ')
		if i%2: pos.append('\n')
	pos.append('\n\t\t</Positions>\n')
	fileId.writelines(pos)
	
	# Normals
	norm = ['\t\t<Normals>\n']
	for i in range(len(infComponentIndex)):
		if not i%2: norm.append('\t\t\t')
		norm.append(str(infComponentNormArray[i][0])+' '+str(infComponentNormArray[i][1])+' '+str(infComponentNormArray[i][2])+' ')
		if i%2: norm.append('\n')
	norm.append('\n\t\t</Normals>\n')
	fileId.writelines(norm)
	
	# Radii
	radii = ['\t\t<Radii>\n']
	for i in range(len(infComponentIndex)):
		if not i%6: radii.append('\t\t\t')
		radii.append('0.01 ')
		if i%6 == 5: radii.append('\n')
	radii.append('\n\t\t</Radii>\n')
	fileId.writelines(radii)
	
	# Footer
	footer = ['\t</Map>','\n</dnWeights>']
	fileId.writelines(footer)
	
	# Close file
	fileId.close()
	
def writeBurlyWeights_allInfluences(mesh,skinCluster,directoryPath):
	'''
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" contains no valid polygon mesh!')
	
	# Check skinCluster
	if not glTools.utils.skinCluster.isSkinCluster(skinCluster):
		raise Exception('Object "'+skinCluster+'" is not a valid skinCluster!')
	
	# Check directory
	if not os.path.isdir(directoryPath):
		raise Exception('Directory path "'+directoryPath+'" does not exist!')
	
	# Get skinCluster influences
	influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
	
	# Write weights
	for influence in influenceList:
		writeBurlyWeights(mesh,skinCluster,influence,directoryPath+influence+'.xml')
	
def loadBurlyWeights(burlyDeformer,directoryPath):
	'''
	'''
	# Check burly deformer
	if not mc.objExists(burlyDeformer):
		raise Exception('Burly deformer "'+burlyDeformer+'" does not exist!')
	
	# Check directory path
	if not directoryPath.endswith('/'): directoryPath+='/'
	if not os.path.isdir(directoryPath):
		raise Exception('Directory path "'+directoryPath+'" does not exist!')
	
	# Get directory listing
	fileList = [i for i in os.listdir(directoryPath) if i.endswith('.xml')]
	
	# Load weights
	for filePath in fileList:
		fileId = directoryPath+filePath
		influence = filePath.replace('.xml','')
		mm.eval('dnBurlyDeformer -loadWeights "'+fileId+'" "'+burlyDeformer+'" "'+influence+'"')

def convertToBurly(skinCluster,burlyDeformerName=''):
	'''
	'''
	# Check skinCluster
	if not mc.objExists(skinCluster):
		raise Exception('SkinCluster "'+skinCluster+'" does not exist!')
	if not glTools.utils.skinCluster.isSkinCluster(skinCluster):
		raise Exception('Object "'+skinCluster+'" is not a valid skinCluster deformer!')
	
	# Get affected mesh
	#mesh = 
	
	# Designate temporary path for exported weight files
	dirPath = '/usr/tmp/'
	
	# Export skinCluster weight files
	influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
	writeBurlyWeights_allInfluences(mesh,skinCluster,dirPath)
	
	
	# Create burly deformer
	mm.eval('dnBurlyDeformer_createNamed("'+geo+'","'+burlyDeformerName+'")')


