import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import mathUtils
import math

class Exception(Exception): pass
class MissingPluginError(Exception): pass

def getMatrix(transform,local=False,time=None):
	'''
	@param transform: Transform object to get world matrix from
	@type transform: str
	@param local: Get local space matrix instead of the world space matrix
	@type local: bool
	@param time: The frame to get the transforms world matrix for. If left at default, will use the current frame.
	@type time: int or float
	'''
	# Check transform
	if not mc.objExists(transform):
		raise Exception('Object "'+transform+'" does not exist!!')
	
	# Define Matrix attribute
	matAttr = 'worldMatrix[0]'
	if local: matAttr = 'matrix'
	
	# Get time
	mat = OpenMaya.MMatrix()
	if time != None: mat = mc.getAttr(transform+'.'+matAttr,t=frame)
	else: mat = mc.getAttr(transform+'.'+matAttr)
	
	# Build Matrix
	matrix = buildMatrix(translate=(mat[12],mat[13],mat[14]),xAxis=(mat[0],mat[1],mat[2]),yAxis=(mat[4],mat[5],mat[6]),zAxis=(mat[8],mat[9],mat[10]))
	
	# Return result
	return matrix

def buildMatrix(translate=(0,0,0),xAxis=(1,0,0),yAxis=(0,1,0),zAxis=(0,0,1)):
	'''
	Build a transformation matrix based on the input vectors
	@param translate: Translate values for the matrix
	@type translate: tuple/list
	@param xAxis: xAxis of the matrix
	@type xAxis: tuple/list
	@param yAxis: yAxis of the matrix
	@type yAxis: tuple/list
	@param zAxis: zAxis of the matrix
	@type zAxis: tuple/list
	'''
	# Create transformation matrix from input vectors
	matrix = OpenMaya.MMatrix()
	OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 0, xAxis[0])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 1, xAxis[1])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 2, xAxis[2])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 0, yAxis[0])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 1, yAxis[1])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 2, yAxis[2])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 0, zAxis[0])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 1, zAxis[1])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 2, zAxis[2])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 0, translate[0])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 1, translate[1])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 2, translate[2])
	return matrix

def vectorMatrixMultiply(vector,matrix,transformAsPoint=False,invertMatrix=False):
	'''
	Transform a vector (or point) by a given transformation matrix.
	@param vector: Vector or point to be transformed
	@type vector: tuple/list
	@param matrix: MMatrix object to provide the transformation
	@type matrix: OpenMaya.MMatrix
	@param transformAsPoint: Transform the vector as a point
	@type transformAsPoint: bool
	@param invertMatrix: Use the matrix inverse to transform the vector
	@type invertMatrix: bool
	'''
	# Create MPoint/MVector object for transformation
	if transformAsPoint: vector = OpenMaya.MPoint(vector[0],vector[1],vector[2],1.0)
	else: vector = OpenMaya.MVector(vector[0],vector[1],vector[2])
	
	# Check input is of type MMatrix
	if type(matrix) != OpenMaya.MMatrix:
		raise Exception('Matrix input variable is not of expected type! Expecting MMatrix, received '+str(type(matrix))+'!!')
	
	# Transform vector
	if matrix != OpenMaya.MMatrix.identity:
		if invertMatrix: matrix = matrix.inverse()
		vector *= matrix
	
	# Return new vector
	return (vector.x,vector.y,vector.z)

def getRotation(matrix,rotationOrder='xyz'):
	'''
	Return the rotation component of a matrix as euler (XYZ) values.
	@param matrix: Matrix to extract rotation from
	@type matrix: maya.OpenMaya.MMatrix
	@param rotationOrder: Rotation order of the matrix
	@type rotationOrder: str or int
	'''
	# Calculate radian constant
	radian = 180.0/math.pi
	
	# Check rotation order
	if type(rotationOrder) == str:
		rotationOrder = rotationOrder.lower()
		rotateOrder = {'xyz':0,'yzx':1,'zxy':2,'xzy':3,'yxz':4,'zyx':5}
		if not rotateOrder.has_key(rotationOrder):
			raise Exception('Invalid rotation order supplied!')
		rotationOrder = rotateOrder[rotationOrder]
	else:
		rotationOrder = int(rotationOrder)
	
	# Get transformation matrix
	transformMatrix = OpenMaya.MTransformationMatrix(matrix)
	
	# Get Euler rotation from matrix
	eulerRot = transformMatrix.eulerRotation()
	
	# Reorder rotation
	eulerRot.reorderIt(rotationOrder)
	
	# Return XYZ rotation values
	return (eulerRot.x*radian,eulerRot.y*radian,eulerRot.z*radian)

def buildRotation(aimVector,upVector=(0,1,0),aimAxis='x',upAxis='y'):
	'''
	Build rotation matrix from the specified inputs
	@param aimVector: Aim vector for construction of rotation matrix (worldSpace)
	@type aimVector: tuple or list
	@param upVector: Up vector for construction of rotation matrix (worldSpace)
	@type upVector: tuple or list
	@param aimAxis: Aim vector for construction of rotation matrix
	@type aimAxis: str
	@param upAxis: Up vector for construction of rotation matrix
	@type upAxis: str
	'''
	# Check negative axis
	negAim = False
	negUp = False
	if aimAxis[0] == '-':
		aimAxis = aimAxis[1]
		negAim = True
	if upAxis[0] == '-':
		upAxis = upAxis[1]
		negUp = True
	
	# Check valid axis
	axisList = ['x','y','z']
	if not axisList.count(aimAxis): raise Exception('Aim axis is not valid!')
	if not axisList.count(upAxis): raise Exception('Up axis is not valid!')
	if aimAxis == upAxis: raise Exception('Aim and Up axis must be unique!')
	
	# Determine cross axis
	axisList.remove(aimAxis)
	axisList.remove(upAxis)
	crossAxis = axisList[0]
	
	# Normaize aimVector
	aimVector = mathUtils.normalizeVector(aimVector)
	if negAim: aimVector = (-aimVector[0],-aimVector[1],-aimVector[2])
	# Normaize upVector
	upVector = mathUtils.normalizeVector(upVector)
	if negUp: upVector = (-upVector[0],-upVector[1],-upVector[2])
	
	# Get cross product vector
	crossVector = (0,0,0)
	if (aimAxis == 'x' and upAxis == 'z') or (aimAxis == 'z' and upAxis == 'y'):
		crossVector = mathUtils.crossProduct(upVector,aimVector)
	else:
		crossVector = mathUtils.crossProduct(aimVector,upVector)
	# Recalculate upVector (orthogonalize)
	if (aimAxis == 'x' and upAxis == 'z') or (aimAxis == 'z' and upAxis == 'y'):
		upVector = mathUtils.crossProduct(aimVector,crossVector)
	else:
		upVector = mathUtils.crossProduct(crossVector,aimVector)
	
	# Build axis dictionary
	axisDict={aimAxis: aimVector,upAxis: upVector,crossAxis: crossVector}
	# Build rotation matrix
	mat = buildMatrix(xAxis=axisDict['x'],yAxis=axisDict['y'],zAxis=axisDict['z'])
	
	# Return rotation matrix
	return mat

def inverseTransform(source,destination,translate=True,rotate=True,scale=True):
	'''
	Apply the inverse of a specified transform to another target transform.
	@param source: The source transform that will supply the transformation
	@type source: str
	@param destination: The destination transform that will receive the inverse transformation
	@type destination: str
	@param translate: Apply inverse translate to destination transform
	@type translate: bool
	@param rotate: Apply inverse rotation to destination transform
	@type rotate: bool
	@param scale: Apply inverse scale to destination transform
	@type scale: bool
	'''
	# Check source / destination transforms
	if not mc.objExists(source): raise Exception('Transform "'+source+'" does not exist!!')
	if not mc.objExists(destination): raise Exception('Transform "'+destination+'" does not exist!!')
	
	# Load decomposeMatrix plugin
	if not mc.pluginInfo('decomposeMatrix',q=True,l=True):
		try: mc.loadPlugin('decomposeMatrix')
		except: raise MissingPluginError('Unable to load "decomposeMatrix" plugin!!')
	
	# Apply inverse transformations
	# -
	# Create and name decomposeMatrix node
	dcm = mc.createNode('decomposeMatrix',n=source+'_decomposeMatrix')
	
	# Make connections
	mc.connectAttr(source+'.inverseMatrix',dcm+'.inputMatrix',f=True)
	if translate:
		mc.connectAttr(dcm+'.outputTranslate',destination+'.translate',f=True)
	if rotate:
		mc.connectAttr(dcm+'.outputRotate',destination+'.rotate',f=True)
	if scale:
		mc.connectAttr(dcm+'.outputScale',destination+'.scale',f=True)
	
	# Return result
	return dcm
