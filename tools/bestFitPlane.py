import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.tools.center

import glTools.utils.base
import glTools.utils.mathUtils
import glTools.utils.matrix

def bestFitPlaneNormal(ptList):
	'''
	Calculate the best fit plane normal from a specified set of points.
	@param ptList: List of points to calculate best fit plane from.
	@type ptList: list
	'''
	# Initialize plane normal
	norm = OpenMaya.MVector()
	
	# Get Point Positions
	ptList = [glTools.utils.base.getPosition(p) for p in ptList]
	
	# Calculate Plane Normal
	for i in range(len(ptList)):
		prev = OpenMaya.MVector(ptList[i-1][0],ptList[i-1][1],ptList[i-1][2])
		curr = OpenMaya.MVector(ptList[i][0],ptList[i][1],ptList[i][2])
		norm += OpenMaya.MVector((prev.z + curr.z) * (prev.y - curr.y), (prev.x + curr.x) * (prev.z - curr.z), (prev.y + curr.y) *  (prev.x - curr.x))
	
	# Normalize result
	norm.normalize()
	
	# Return Result
	return [norm.x,norm.y,norm.z]

def bestFitPlaneCreate(ptList,upVector=(0,1,0)):
	'''
	Create a best fit plane from a specified set of points.
	@param ptList: List of points to calculate best fit plane from.
	@type ptList: list
	@param upVector: Up vector for orientation reference.
	@type upVector: tuple or list
	'''
	
	# Calculate Plane Center and Normal
	p = glTools.tools.center.centerPoint_average(ptList)
	pt = OpenMaya.MVector(p[0],p[1],p[2])
	n = bestFitPlaneNormal(ptList)
	norm = OpenMaya.MVector(n[0],n[1],n[2])
	
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

def bestFitPlaneMatrix(ptList,upVector=(0,1,0)):
	'''
	Calculate the best fit plane matrix from a specified set of points.
	@param ptList: List of points to calculate best fit plane from.
	@type ptList: list
	@param upVector: Up vector for orientation reference.
	@type upVector: tuple or list
	'''
	# Calculate Plane Center and Normal
	p = glTools.tools.center.centerPoint_average(ptList)
	n = bestFitPlaneNormal(ptList)
	
	# Calculate Cross and Up Vectors
	crossVector = glTools.utils.mathUtils.crossProduct(n,upVector)
	upVector = glTools.utils.mathUtils.crossProduct(crossVector,n)
	
	# Build rotation matrix
	mat = glTools.utils.matrix.buildMatrix(translate=p,xAxis=upVector,yAxis=n,zAxis=crossVector)
	
	# Return Result
	return mat
