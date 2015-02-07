import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.transform

def pointFaceMesh(pointList,scale=0.05,combine=True,prefix='pointFace'):
	'''
	'''
	# Get encoded point list
	ptList = []
	for point in pointList:
		ptList.append(glTools.utils.base.getPosition(point))
	
	# Create face for each point
	faceList = []
	vscale = scale * 0.5
	hscale = scale * 0.866
	for pt in ptList:
		face = mc.polyCreateFacet(p=[(pt[0],pt[1]+scale,pt[2]),(pt[0]+hscale,pt[1]-vscale,pt[2]),(pt[0]-hscale,pt[1]-vscale,pt[2])])[0]
		face = mc.rename(face,prefix+'_mesh')
		faceList.append(face)
	
	# Define return list
	mesh = faceList
	
	# Combine faces to single mesh
	if combine:
		mesh = mc.polyUnite(faceList,ch=False)
		mesh = [mc.rename(mesh[0],prefix+'_mesh')]
	
	# Return result
	return mesh

def transformFaceMesh(transformList,faceAxis='y',scale=0.05,combine=True,prefix='transformFace'):
	'''
	'''
	# Checks
	faceAxis = faceAxis.lower()
	if not ['x','y','z'].count(faceAxis):
		raise Exception('Invalid axis "'+faceAxis+'"! Enter "x", "y" or "z".')
	
	# Define face vertex list
	if faceAxis == 'x':
		vtxList = [OpenMaya.MPoint(0,-scale,scale,1),OpenMaya.MPoint(0,scale,scale,1),OpenMaya.MPoint(0,scale,-scale,1),OpenMaya.MPoint(0,-scale,-scale,1)]
	elif faceAxis == 'y':
		vtxList = [OpenMaya.MPoint(-scale,0,scale,1),OpenMaya.MPoint(scale,0,scale,1),OpenMaya.MPoint(scale,0,-scale,1),OpenMaya.MPoint(-scale,0,-scale,1)]
	elif faceAxis == 'z':
		vtxList = [OpenMaya.MPoint(-scale,scale,0,1),OpenMaya.MPoint(scale,scale,0,1),OpenMaya.MPoint(scale,-scale,0,1),OpenMaya.MPoint(-scale,-scale,0,1)]
	
	# Create face for each transform
	faceList = []
	for i in range(len(transformList)):
		
		# Get world space matrix
		tMatrix = glTools.utils.transform.getMatrix(transformList[i])
		
		# Create face
		vtx = [v*tMatrix for v in vtxList]
		pts = [(vtx[0][0],vtx[0][1],vtx[0][2]),(vtx[1][0],vtx[1][1],vtx[1][2]),(vtx[2][0],vtx[2][1],vtx[2][2]),(vtx[3][0],vtx[3][1],vtx[3][2])]
		face = mc.polyCreateFacet(p=pts)[0]
		face = mc.rename(face,prefix+'_'+str(i)+'_mesh')
		faceList.append(face)
	
	# Define return list
	mesh = faceList
	
	# Combine faces to single mesh
	if combine:
		mesh = mc.polyUnite(faceList,ch=False)
		mesh = [mc.rename(mesh[0],prefix+'_mesh')]
	
	# Return result
	return mesh
