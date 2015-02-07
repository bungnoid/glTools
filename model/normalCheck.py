import maya.mel as mm
import maya.cmds as mc

import cleanup

def normalCheck(meshList=[]):
	'''
	Setup normal check properties for a specified list of meshes.
	@param meshList: List of meshes to setup normal check for
	@type meshList: list
	'''
	# Check Mesh List
	meshList = cleanup.getMeshList(meshList)
	if not meshList: return []
	
	# Check Normal Shader
	normalSG = 'normalCheckSG'
	normalShader = 'normalCheckShader'
	if not mc.objExists(normalShader):
		# Create Shader
		normalShader = mc.shadingNode('lambert',asShader=True,n=normalShader)
		normalSG = mc.sets(renderable=True,noSurfaceShader=True,empty=True,name=normalSG)
		mc.connectAttr(normalShader+'.outColor',normalSG+'.surfaceShader',f=True)
		mc.setAttr(normalShader+'.color',0,0,0)
		mc.setAttr(normalShader+'.incandescence',1,0,0)
	
	# Setup Normal Check
	for mesh in meshList:
		
		# Clear selection
		mc.select(cl=True)
		
		# Turn on double sided
		mc.setAttr(mesh+'.doubleSided',1)
		
		# Extrude face
		numFace = mc.polyEvaluate(mesh,f=True)
		polyExtrude = mc.polyExtrudeFacet(mesh+'.f[0:'+str(numFace)+']',ch=1,kft=True,pvt=(0,0,0),divisions=2,twist=0,taper=1,off=0,smoothingAngle=30)
		mm.eval('PolySelectTraverse 1')
		extrudeFaceList = mc.filterExpand(ex=True,sm=34)
		mc.setAttr(polyExtrude[0]+'.localTranslateZ',-0.001)
		
		# Apply shader
		mc.sets(extrudeFaceList,fe=normalSG)
	
	# Set selection
	mc.select(meshList)
	
	# Retrun result
	return meshList

def normalCheckRemove(meshList=[]):
	'''
	Remove normal check properties for a specified list of meshes.
	@param meshList: List of meshes to removes normal check from
	@type meshList: list
	'''
	# Check Mesh List
	meshList = cleanup.getMeshList(meshList)
	if not meshList: return []
	
	# Remove Normal Check
	for mesh in meshList:
		
		# Clear Selection
		mc.select(cl=True)
		
		# Turn Off Double Sided
		mc.setAttr(mesh+'.doubleSided',0)
		
		# Remove Extrude Face
		polyExtrude = mc.ls(mc.listHistory(mesh),type='polyExtrudeFace')
		if polyExtrude: mc.delete(polyExtrude)
		
		# Delete History
		mc.delete(mesh,ch=True)
		
		# Apply Initial Shading Group
		mc.sets(mesh,fe='initialShadingGroup')
		
	# Check normalShader members
	normalSG = 'normalCheckSG'
	normalShader = 'normalCheckShader'
	if not mc.sets(normalSG,q=True): mc.delete(normalShader,normalSG)
	
	# Set Selection
	mc.select(meshList)
	
	# Retrun Result
	return meshList
