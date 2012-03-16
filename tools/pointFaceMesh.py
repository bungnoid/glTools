import maya.cmds as mc
import maya.mel as mm

import glTools.utils.base

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
		faceList.append(face)
	
	# Combine faces to single mesh
	if combine:
		mesh = mc.polyUnite(faceList,ch=False)
		mesh = mc.rename(mesh[0],prefix+'_mesh')
	
	# Return result
	return mesh
