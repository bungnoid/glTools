import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.matrix

def bestFitPlane(ptList,upVector=(0,1,0)):
	'''
	'''
	# Initialize plane normal
	norm = OpenMaya.MVector()
	pt = OpenMaya.MVector()
	
	# Calculate plane
	for i in range(len(ptList)):
		
		prev = OpenMaya.MVector(ptList[i-1][0],ptList[i-1][1],ptList[i-1][2])
		curr = OpenMaya.MVector(ptList[i][0],ptList[i][1],ptList[i][2])
		norm += OpenMaya.MVector((prev.z + curr.z) * (prev.y - curr.y), (prev.x + curr.x) * (prev.z - curr.z), (prev.y + curr.y) *  (prev.x - curr.x))
		pt += curr
	
	# Normalize result
	norm.normalize()
	pt /= len(ptList)
	
	# Build rotation matrix
	mat = glTools.utils.matrix.buildRotation(norm,upVector,'y','x')
	rot = glTools.utils.matrix.getRotation(mat,'xyz')
	
	# Create Plane
	plane = mc.polyPlane(w=1,h=1,sx=1,sy=1,ax=[0,1,0],cuv=2,ch=False)[0]
	
	# Position Plane
	mc.rotate(rot[0],rot[1],rot[2],plane,os=True,a=True)
	mc.move(pt[0],pt[1],pt[2],plane,ws=True,a=True)
	
	# Return result
	return plane
