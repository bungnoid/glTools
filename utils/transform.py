import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.mathUtils
import glTools.utils.matrix

def isTransform(object):
	'''
	Check if the specified object is a valid transform node
	@param object: Object to query type
	@type object: str
	'''
	# Check object exists
	if not mc.objExists(object): return False
	
	# Check transform
	mObject = glTools.utils.base.getMObject(object)
	if not mObject.hasFn(OpenMaya.MFn.kTransform): return False
	
	# Return result
	return True

def getMatrix(transform,local=False,time=None):
	'''
	Get transform local or world space matrix.
	@param transform: Transform object to get world matrix from
	@type transform: str
	@param local: Get local space matrix instead of the world space matrix
	@type local: bool
	@param time: The frame to get the transforms world matrix for. If left at default, will use the current frame.
	@type time: int or float
	'''
	return glTools.utils.matrix.getMatrix(transform,local=False,time=None)

def axisVector(transform,axis,normalize=False):
	'''
	Return the specified transform worldSpace axis vector
	@param transform: Transform object to get worldSpace axis vector
	@type transform: str
	@param axis: The axis to return as world space vector
	@type axis: str
	'''
	# Define axis dictionary
	axis = axis.lower()
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	# Checks
	if not mc.objExists(transform):
		raise Exception('Transform "'+transform+'" does not exist!')
	if not axisDict.has_key(axis):
		raise Exception('Invalid axis "'+axis+'"!')
	
	# Get transform matrix
	tMatrix = getMatrix(transform)
	
	# Get worldSpace axis vector
	axisVector = glTools.utils.matrix.vectorMatrixMultiply(axisDict[axis],tMatrix)
	
	# Normalize
	if normalize: axisVector = glTools.utils.mathUtils.normalizeVector(axisVector)
	
	# Return Result
	return axisVector

def match(transform,target):
	'''
	Match the specified transform to a target transform
	@param transform: Transform to set
	@type transform: str
	@param target: Target transform to match to
	@type target: str
	'''
	# Checks
	if not mc.objExists(transform):
		raise Exception('Transform "'+transform+'" does not exist!')
	if not mc.objExists(target):
		raise Exception('Target transform "'+target+'" does not exist!')
		
	# Get target matrix
	targetMat = mc.xform(target,q=True,ws=True,matrix=True)
	
	# Set source matrix
	mc.xform(transform,ws=True,matrix=targetMat)
