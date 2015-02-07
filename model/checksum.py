import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.mesh

import hashlib
import os.path

def checksum_mesh(mesh):
	'''
	Generate a checksum string based on the vertex connectivity of the specified mesh.
	@param mesh: Polygon mesh to return connectivity checksum for
	@type mesh: str
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object '+mesh+' is not a valid polygon mesh!')
	
	# Get Mesh Face Vertices
	vtxCnt = OpenMaya.MIntArray()
	vtxList = OpenMaya.MIntArray()
	glTools.utils.mesh.getMeshFn(mesh).getVertices(vtxCnt,vtxList)
	
	# Generate Checksum
	m = hashlib.md5()
	m.update(str(list(vtxList)))
	hexVal = m.hexdigest()
	
	# Return Checksum Hash
	return hexVal

def checksum_meshUV(mesh):
	'''
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object '+mesh+' is not a valid polygon mesh!')
	
	# Return Result
	return

def checksum_meshDict(meshList):
	'''
	Create a checksum dictionary from the specified list of meshes.
	@param meshList: List of polygon meshes to return a connectivity checksum dictionary for
	@type meshList: list
	'''
	# Initialize Checksum Dict
	checksum_dict = {}
	
	# Check Mesh List
	if not meshList: return checksum_dict
	
	# For Each Mesh
	for mesh in meshList:
		
		# Check Mesh
		if not glTools.utils.mesh.isMesh(mesh):
			print('Object '+mesh+' is not a valid polygon mesh! Skipping...')
			continue
		
		# Get Transform Parent
		meshTransform = mesh
		if not mc.objectType(mesh) == 'transform':
			meshTransform = mc.listRelatives(mesh,p=True)[0]
		
		# Get Checksum Value
		checksum_dict[meshTransform] = checksum_mesh(mesh)
	
	# Return Result
	return checksum_dict

def checksum_meshDict_fromFile(filePath):
	'''
	Create a checksum dictionary from the specified maya file.
	@param filePath: Path to the maya file to generate the dictionary of mesh checksums from.
	@type filePath: str
	'''
	# Check File
	if not os.path.isfile(filePath):
		raise Exception('No valid file at location "'+filePath+'"!')
	
	# Open File
	mc.file(filePath,o=True,prompt=False,force=True)
	
	# Get List of Mesh Objects
	meshList = mc.ls(type='mesh')
	
	# Get Checksum Dictionary
	checksum_dict = checksum_meshDict(meshList)
	
	# Return Result
	return checksum_dict

def checksum_meshDict_compare(fileList):
	'''
	Create a checksum dictionary from the specified maya file.
	@param fileList: List of file paths to generate and compare checksum dictionaries for.
	@type fileList: list
	'''
	pass
