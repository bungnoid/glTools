import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import math

class Ray(object):
	def __init__(self,p,v):
		self.p = p
		self.v = v

class Cylinder(object):
	def __init__(self,rX,rY,lZ,m=None):
		self.rX = rX
		self.rY = rY
		self.lZ = lZ
		self.m = OpenMaya.MMatrix
		if m: self.m = m
	def matrix(self):
		x = OpenMaya.MVector.xAxis*self.rX
		y = OpenMaya.MVector.yAxis*self.rY
		z = OpenMaya.MVector.zAxis*self.lZ
		matrix = OpenMaya.MMatrix()
		OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 0, x[0])
		OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 1, x[1])
		OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 2, x[2])
		OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 0, y[0])
		OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 1, y[1])
		OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 2, y[2])
		OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 0, z[0])
		OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 1, z[1])
		OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 2, z[2])
		OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 0, 0.0)
		OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 1, 0.0)
		OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 2, 0.0)
		return matrix * self.m

def intersect(c,r):
	'''
	'''
	result = 0
	
	# Matrix and Inverse
	T = c.matrix()
	iT = T.inverse()
	
	# Point and Ray
	p = r.p*iT
	v = r.v*iT
	
	# Solve the 2D Equation for X and Y radii
	AapBb = (p.x*v.x) + (p.y*v.y)
	A2pB2 = (v.x*v.x) + (v.y*v.y)
	disc = (AapBb*AapBb) - A2pB2*(p.x*p.x+p.y*p.y-1)
	if disc < 0:
		print('No intersection with the infinite cylinder!')
		return result
	
	s = math.sqrt(disc)
	inv_A2pB2 = 1.0/A2pB2
	t1 = (-AapBb-s)*inv_A2pB2
	t2 = (-AapBb+s)*inv_A2pB2
	pt1 = p+v*t1
	pt2 = p+v*t2
	
	# Check Cylinder Bounds
	pt1v = (pt1.z>0) and (pt1.z<1) and (((pt1-p)*v)>0)
	pt2v = (pt2.z>0) and (pt2.z<1) and (((pt2-p)*v)>0)
	if not pt1v and not pt2v:
		print('No intersection with the finite cylinder!')
		return result
	
	# To World Space
	pt1 *= T
	pt2 *= T
	if pt1v:
		mc.spaceLocator(p=[pt1.x,pt1.y,pt1.z])
		result += 1
	if pt2v:
		mc.spaceLocator(p=[pt2.x,pt2.y,pt2.z])
		result += 1
	
	return result
