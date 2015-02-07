import maya.mel as mm
import maya.cmds as mc

import glTools.utils.attribute
import glTools.utils.cleanup
import glTools.utils.mesh
import glTools.ui.utils

class RecursiveBreak( Exception ): pass

def getGeoList(geoList=[]):
	'''
	Return a list of geometry transform objects to be used for model checks
	@param meshList: List of meshes to return as list. If empty, use all non intermediate meshes in the scene
	@type meshList: list
	'''
	# Check Geo List
	if not geoList:
		geoList = [mc.listRelatives(i,p=True,pa=True)[0] for i in mc.ls(geometry=True,ni=True) or []]
	else:
		geoList = [geo for geo in geoList if glTools.utils.geometry.isGeometry(geo)]
	if not geoList: return []
	
	# Remove Duplicates
	geoList = list(set(geoList))
	
	# Return Result
	return geoList

def getMeshList(meshList=[]):
	'''
	Return a list of mesh objects to be used in the poly check scripts
	@param meshList: List of meshes to return as list. If empty, use all non intermediate meshes in the scene
	@type meshList: list
	'''
	# Check Mesh List
	if not meshList:
		meshList = [mc.listRelatives(i,p=True,pa=True)[0] for i in mc.ls(type='mesh',ni=True) or []]
	else:
		meshList = [mesh for mesh in meshList if glTools.utils.mesh.isMesh(mesh)]
	if not meshList: return []
	
	# Remove Duplicates
	meshList = list(set(meshList))
	
	# Return Result
	return meshList

# ==========
# - Checks -
# ==========
	
def triangles(meshList=[]):
	'''
	Return a list of all 3-sided polygon faces in a specified mesh list.
	@param meshList: List of meshes to check for triangles
	@type meshList: list
	'''
	# Check Mesh List
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Find Triangles
	mc.select(meshList)
	mc.polySelectConstraint(mode=3,type=0x0008,size=1)
	mc.polySelectConstraint(disable=True)
	tris = mc.filterExpand(ex=True,sm=34) or []
	mc.select(meshList)
	
	# Return Result
	return tris

def nGons(meshList=[]):
	'''
	Return a list of all polygon faces with more than 4 sides in a specified list of meshes.
	@param meshList: List of meshes to check for triangles
	@type meshList: list
	'''
	# Check Mesh List
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Find N-Gons
	mc.select(meshList)
	mc.polySelectConstraint(mode=3,type=0x0008,size=3)
	mc.polySelectConstraint(disable=True)
	ngon = mc.filterExpand(ex=True,sm=34) or []
	mc.select(meshList)
	
	# Return Result
	return ngon

def nonQuads(meshList=[]):
	'''
	Return a list of all non 4-sided polygon faces in a specified list of meshes.
	@param meshList: List of meshes to check for non quads
	@type meshList: list
	'''
	# Return Result
	return triangles(meshList) + nGons(meshList)

def nonManifold(meshList=[]):
	'''
	Check for non manifold geometry in a specified list of meshes.
	@param meshList: List of meshes to check for non manifold topology. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Check Mesh List
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Check Non Manifold
	mc.select(meshList)
	mc.polySelectConstraint(mode=3,type=0x0001,nm=1)
	mc.polySelectConstraint(disable=True)
	nonManifoldList = mc.filterExpand(ex=True,sm=31) or []
	mc.select(meshList)
	
	# Return result
	return nonManifoldList

def lamina(meshList=[]):
	'''
	Check for lamina faces
	@param meshList: List of meshes to check for lamina faces. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Check Mesh List
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Check Lamina
	mc.select(meshList)
	mc.polySelectConstraint(mode=3,type=0x0008,topology=2)
	mc.polySelectConstraint(disable=True)
	laminaList = mc.filterExpand(ex=True,sm=34) or []
	mc.select(meshList)
	
	# Return result
	return laminaList
	
def checkLockedVertexNormals(meshList=[]):
	'''
	Check for locked vertex normals
	@param meshList: List of meshes to check for locked normals. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Check meshList
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Check Locked Normals
	lockedNormalList = []
	for mesh in meshList:
		
		# Shapes
		meshShapes = mc.listRelatives(mesh,s=True,ni=True,pa=True)
		if not meshShapes: continue
		for meshShape in meshShapes:
			
			# Check Normals
			if True in mc.polyNormalPerVertex(meshShape+'.vtx[*]',q=True,fn=True):
				lockedNormalList.append(mesh)
				continue
	
	# Return Result
	return lockedNormalList

def checkVertexTransforms(meshList=[]):
	'''
	Check for mesh vertex transforms (tweaks)
	@param meshList: List of meshes to check for vertex transforms. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Check meshList
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Check Vertex Transforms
	vtxTransformList = []
	for mesh in meshList:
		
		# Shapes
		meshShapes = mc.listRelatives(mesh,s=True,ni=True,pa=True) or []
		for meshShape in meshShapes:
			
			# Avoid Redundant Checks
			if vtxTransformList.count(mesh): break
			
			# Check Shape Type
			if mc.objectType(meshShape) != 'mesh': continue
			
			# Check NonZero Values
			#if [i for sublist in mc.getAttr(meshShape+'.pnts[*]') for i in sublist if abs(i) > 0.0000000001]:
			try:
				for tweak in mc.getAttr(meshShape+'.pnts[*]'):
					for i in tweak:
						if abs(i) > 0.0000000001:
				
							# Append Result
							vtxTransformList.append(mesh)
							raise RecursiveBreak
				
			except RecursiveBreak:
				pass
			
	# Return Result
	return  vtxTransformList

def checkMultipleUVsets(meshList=[]):
	'''
	Check multiple UV sets for each specified mesh
	@param meshList: List of meshes to check for UV sets. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Check meshList
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Check Multiple UV Sets
	multipleUVsets = []
	for mesh in meshList:
		UVsets = mc.polyUVSet(mesh,q=True,allUVSets=True)
		if not UVsets: continue
		if len(UVsets) > 1: multipleUVsets.append(mesh)
	
	# Return Result
	return multipleUVsets

def checkMissingUVsets(meshList=[]):
	'''
	Check missing UV sets for each specified mesh
	@param meshList: List of meshes to check for UV sets. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Check meshList
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Check Missing UV Sets
	missingUVsets = []
	for mesh in meshList:
		UVsets = mc.polyUVSet(mesh,q=True,allUVSets=True)
		if not UVsets: missingUVsets.append(mesh)
	
	# Return Result
	return missingUVsets

def checkUvShells(meshList=[],faceCountTol=1):
	'''
	Check number of UV shells compared to the mesh face count.
	Returns a list of mesh objects that have as many UV shells as faces.
	@param meshList: List of meshes to check for UV shells. If empty, check all mesh objects in the scene.
	@type meshList: list
	@param faceCountTol: Only consider mesh objects that have a face count greater this number.
	@type faceCountTol: int
	'''
	# Check meshList
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Check Multiple UV Sets
	meshUVshells = []
	for mesh in meshList:
		
		# Shapes
		meshShapes = mc.listRelatives(mesh,s=True,ni=True,pa=True)
		if not meshShapes: continue
		for meshShape in meshShapes:
		
			# Get Face Count
			faceCount = mc.polyEvaluate(meshShape,f=True)
			if faceCount <= faceCountTol: continue
			
			# Get UV Sets
			uvSets = mc.polyUVSet(meshShape,q=True,allUVSets=True)
			if not uvSets: continue
			
			# For Each UV Set
			for uvSet in uvSets:
			
				# Get Num UV Shells
				UVshells = glTools.utils.mesh.numUvShells(meshShape,uvSet=uvSet)
				if UVshells == faceCount:
					meshUVshells.append(mesh)
					break
	
	# Return Result
	return meshUVshells

def checkCreaseSets():
	'''
	Check mesh edge/vertex crease sets.
	'''
	creaseSets = mc.ls(type='creaseSet') or []
	return creaseSets

# =========
# - Fixes -
# =========

def unlockVertexNormals(meshList=[]):
	'''
	Unlocked vertex normals
	@param meshList: List of meshes to unlocked normals on. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Check meshList
	if not meshList: meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Unlock Normals
	for mesh in meshList: mc.polyNormalPerVertex(mesh,ufn=True)
	
	# Return Result
	return meshList

def freezeVertexTransforms(meshList=[]):
	'''
	Freeze vertex transforms
	@param meshList: List of meshes to freeze transform on. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Check meshList
	if not meshList: meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Freeze Vertex Transforms
	for mesh in meshList: glTools.utils.mesh.freezeVertices(mesh)
	
	# Return Result
	return meshList

def mergeUVs(meshList=[],dist=0.0001):
	'''
	Merge UVs
	@param meshList: List of meshes to merge UVs on. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Check meshList
	if not meshList: meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Merge UVs
	for mesh in meshList:
		mc.polyMergeUV(mesh,d=dist,ch=False)
	
	# Return Result
	return meshList

def assignInitialShadingGroup(geoList=[]):
	'''
	Wrapper function for moved method.
	'''
	# Run Command
	return glTools.utils.cleanup.assignInitialShadingGroup(geoList)

def bakeCreaseSets(creaseSets=[]):
	'''
	'''
	# Check Crease Sets
	if not creaseSets: creaseSets = checkCreaseSets()
	if not creaseSets: return []
	
	# Bake Crease Sets
	
