import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.boundingBox
import glTools.utils.mesh
import glTools.utils.surface

def radialComponentSelection(mesh,center,radius=1.0):
	'''
	Build component selection from a point and radial distance.
	@param mesh: Geometry to build component selection from.
	@type mesh: str
	@param center: Radial center to build selection from.
	@type center: str or list
	@param radius: Radial distance to build selection from.
	@type radius: float
	'''
	# ==========
	# - Checks -
	# ==========
		
	# Check Mesh
	if not mc.objExists(mesh):
		raise Exception('Mesh object "'+mesh+'" does not exist!!')
	
	# Get Point
	pt = glTools.utils.base.getMPoint(center)
	
	# ==========================
	# - Build Radial Selection -
	# ==========================
	
	# Get Component List
	ptList = glTools.utils.base.getMPointArray(mesh)
	
	# Build Selection
	sel = []
	for i in range(ptList.length()):
		dist = (pt - ptList[i]).length()
		if dist <= radius: sel.append(mesh+'.vtx['+str(i)+']')
	
	# =================
	# - Return Result -
	# =================
	
	return sel

def volumeComponentSelection(mesh,volume):
	'''
	Build component selection from volume.
	@param mesh: Geometry to build component selection from.
	@type mesh: str
	@param volume: Volume shape to build component selection from.
	@type volume: str
	'''
	# ==========
	# - Checks -
	# ==========
		
	# Check Mesh
	if not mc.objExists(mesh):
		raise Exception('Mesh object "'+mesh+'" does not exist!!')
		
	# Check Volume
	if not mc.objExists(volume):
		raise Exception('Volume object "'+volume+'" does not exist!!')
	
	# Get Volume Type
	volumeShape = volume
	if mc.objectType(volumeShape) == 'transform':
		volumeShape = mc.listRelatives(volume,s=True,ni=True)
		if not volumeShape: raise Exception('Volume object "'+mesh+'" does not exist!!')
		else: volumeShape = volumeShape[0]
	volumeType = mc.objectType(volumeShape)
	
	# Convert to Polygon Volume (if necessary)
	nurbsToPolyConvert = None
	if volumeType == 'nurbsSurface':
		nurbsToPolyConvert = mc.nurbsToPoly(volumeShape,ch=0,f=1,pt=1,ft=0.01,mel=0.001,d=0.1)
		nurbsToPolyShape = mc.listRelatives(nurbsToPolyConvert,s=True,ni=True)
		volumeShape = nurbsToPolyShape[0]
	
	# ==========================
	# - Build Volume Selection -
	# ==========================
	
	# Create Funtion Set for Volume Mesh
	volumeFn = glTools.utils.mesh.getMeshFn(volume)
	
	# Get Bounding Box
	volumeBBox = glTools.utils.base.getMBoundingBox(volume)
	
	# Get Vertices
	pntList = glTools.utils.base.getMPointArray(mesh)
	
	# Build Selection List
	sel = []
	point = OpenMaya.MPoint()
	normal = OpenMaya.MVector()
	for i in range(pntList.length()):
		if not volumeBBox.contains(pntList[i]): continue
		volumeFn.getClosestPointAndNormal(pntList[i],point,normal)
		dotVal = normal * (point-pntList[i]).normal()
		if dotVal > 0.0: sel.append(mesh+'.vtx['+str(i)+']')
	
	# ===========
	# - Cleanup -
	# ===========
	
	if nurbsToPolyConvert: mc.delete(nurbsToPolyConvert)
	
	# =================
	# - Return Result -
	# =================
	
	return sel
