import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base

def volumeComponentSelectionList(mesh,volume):
	'''
	'''
	# Check mesh
	if not mc.objExists(mesh):
		raise Exception('Mesh object "'+mesh+'" does not exist!!')
		
	# Check volume
	if not mc.objExists(volume):
		raise Exception('Volume object "'+volume+'" does not exist!!')
	
	# Get volume type
	volumeShape = volume
	if mc.objectType(volumeShape) == 'transform':
		volumeShape = mc.listRelatives(volume,s=True,ni=True)
		if not volumeShape: raise Exception('Volume object "'+mesh+'" does not exist!!')
		else: volumeShape = volumeShape[0]
	volumeType = mc.objectType(volumeShape)
	# Convert to polygon volume if necessary
	nurbsToPolyConvert = []
	if volumeType == 'nurbsSurface':
		nurbsToPolyConvert = mc.nurbsToPoly(volumeShape,ch=0,f=1,pt=1,ft=0.01,mel=0.001,d=0.1)
		nurbsToPolyShape = mc.listRelatives(nurbsToPolyConvert,s=True,ni=True)
		volumeShape = nurbsToPolyShape[0]
	
	# Create funtion set for volume object
	volumeObj = glTools.utils.base.getMDagPath(volumeShape)
	volumeFn = OpenMaya.MFnMesh(volumeObj)
	
	# Get bounding box
	volumeBBox = OpenMaya.MFnDagNode(volumeObj).boundingBox()
	volumeBBox.transformUsing(volumeObj.inclusiveMatrix())
	
	# Get mesh vertices
	pntList = glTools.utils.base.getMPointArray(mesh)
	
	# Build selection list
	sel = []
	point = OpenMaya.MPoint()
	normal = OpenMaya.MVector()
	for i in range(pntList.length()):
		if not volumeBBox.contains(pntList[i]): continue
		volumeFn.getClosestPointAndNormal(pntList[i],point,normal)
		dotVal = normal * (point-pntList[i]).normal()
		if dotVal > 0.0: sel.append(mesh+'.vtx['+str(i)+']')
	
	# Clean up
	if nurbsToPolyConvert: mc.delete(nurbsToPolyConvert)
	
	# Return result
	return sel
