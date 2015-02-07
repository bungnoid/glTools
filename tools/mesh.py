import maya.cmds as mc

import glTools.data.meshData

import glTools.utils.component
import glTools.utils.mesh

# ---
# TODO - Add option to rebuild userdefined attrs and connections on replace
# ---

def reconstructMesh(mesh,replace=False):
	'''
	Reconstruct mesh using meshData data class.
	@param mesh: The mesh object to reconstruct.
	@type mesh: str
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Build Mesh Data
	meshData = glTools.data.meshData.MeshData(mesh)
	
	# Rename Mesh
	meshData._data['name'] = mesh+'_reconstructed'
	
	# Rebuild Mesh
	newMesh = meshData.rebuildMesh()
	
	# Reassign Shader
	meshShape = mc.ls(mc.listRelatives(mesh,s=True,ni=True),type='mesh')[0]
	sg = mc.ls(mc.listConnections(meshShape,s=True,d=True,sh=True) or [],type='shadingEngine')
	if sg: mc.sets(newMesh,fe=sg[0])
	
	# Replace
	if replace:
		
		# Get Current Mesh Parent
		meshParent = mc.listRelatives(mesh,p=True)
		
		# Rename Mesh
		delMesh = mc.rename(mesh,mesh+'_delete')
		newMesh = mc.rename(newMesh,mesh)
		
		# Reparent Mesh
		if meshParent: mc.parent(newMesh,meshParent[0])
		
		# Delete Old Mesh
		mc.delete(delMesh)
	
	# Return Result
	return newMesh

def edgeLoopsToCurve(edgeList,form=2,degree=1):
	'''
	Generate edge loop curves from the specified list of edges.
	@param edgeList: The list of mesh edges to generate edge loop curves from.
	@type edgeList: list
	@param form: NURBS curve form. 0 = Periodic, 1 = Open, 2 = Best Guess.
	@type form: str
	@param degree: NURBS curve degree.
	@type degree: str
	'''
	# Filter/Check Edge List
	edgeList = mc.filterExpand(edgeList,ex=True,sm=32)
	if not edgeList: raise Exception('Invalid edge list!')
	
	# For Each Edge
	edgeCurveList = []
	for edge in edgeList:
		
		# Get Mesh
		edgeId = glTools.utils.component.index(edge)
		meshShape = mc.ls(edge,o=True)[0]
		mesh = mc.listRelatives(meshShape,p=True)[0]
		prefix = mesh.split(':')[-1]
		
		# To Edge Loop
		mc.polySelect(mesh,edgeLoop=edgeId)
		
		# Edge Loop to Curve
		edgeCurve = mc.polyToCurve(ch=False,form=form,degree=degree)[0]
		
		# Append List
		edgeCurveList.append(edgeCurve)
	
	# Return Result
	return edgeCurveList
