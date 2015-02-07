import maya.cmds as mc

import glTools.utils.attribute
import glTools.utils.base
import glTools.utils.joint
import glTools.utils.mathUtils
import glTools.utils.matrix
import glTools.utils.transform

import types

def objectsAreAligned(obj1,obj2,axis,tol=0.00001):
	'''
	Check if 2 objects are aligned along a specified world axis.
	@param obj1: Object 1 to check alignment of.
	@type obj1: str
	@param obj2: Object 2 to check alignment of.
	@type obj2: str
	@param axis: World space axis to compare object alignment with.
	@type axis: str or list or tuple
	@param tol: Axis to alignment dot product tolerance.
	@type tol: float
	'''
	# Check Objects
	if not mc.objExists(obj1):
		print('Object "'+obj1+'" does not exist! Returning False...')
		return False
	if not mc.objExists(obj2):
		print('Object "'+obj2+'" does not exist! Returning False...')
		return False
	
	# Get World Axis
	if isinstance(axis,types.StringTypes):
		if str(axis).lower() == 'x': axis = (1,0,0)
		elif str(axis).lower() == 'y': axis = (0,1,0)
		elif str(axis).lower() == 'z': axis = (0,0,1)
		else:
			print('Invalid axis value! Returning False...')
			return False
	# Normalize Axis Vector
	axis = glTools.utils.mathUtils.normalizeVector(axis)
	
	# Get Object World Positions
	pos1 = glTools.utils.base.getPosition(obj1)
	pos2 = glTools.utils.base.getPosition(obj2)
	
	# Check Align Axis
	alignAxis = glTools.utils.mathUtils.offsetVector(pos1,pos2)
	alignAxis = glTools.utils.mathUtils.normalizeVector(alignAxis)
	alignDot = abs(glTools.utils.mathUtils.dotProduct(axis,alignAxis))
	
	# Return Result
	if (1.0-alignDot) > abs(tol): return False
	else: return True

def axisIsAligned(obj,objAxis,axis,tol=0.00001):
	'''
	Check if a specified object axis is aligned with a given world axis within a tolerance.
	@param obj: Transform object to check axis alignment for.
	@type obj: str
	@param objAxis: Transform axis to check alignment of.
	@type objAxis: str or list or tuple
	@param axis: World axis to compare against.
	@type axis: str or list or tuple
	@param tol: Axis alignment dot product tolerance.
	@type tol: float
	'''
	# Check Object
	if not mc.objExists(obj):
		print('Object "'+obj+'" does not exist! Returning False...')
		return False
	if not glTools.utils.transform.isTransform(obj):
		print('Object "'+obj+'" is not a valid transform! Returning False...')
		return False
	
	# Get World Axis
	if isinstance(axis,types.StringTypes):
		if str(axis).lower() == 'x': axis = (1,0,0)
		elif str(axis).lower() == 'y': axis = (0,1,0)
		elif str(axis).lower() == 'z': axis = (0,0,1)
		elif str(axis).lower() == '-x': axis = (-1,0,0)
		elif str(axis).lower() == '-y': axis = (0,-1,0)
		elif str(axis).lower() == '-z': axis = (0,0,-1)
		else:
			print('Invalid axis value! Returning False...')
			return False
	# Normalize World Axis Vector
	axis = glTools.utils.mathUtils.normalizeVector(axis)
	
	# Get Transform Axis
	if isinstance(objAxis,types.StringTypes):
		if str(objAxis).lower() == 'x': objAxis = (1,0,0)
		elif str(objAxis).lower() == 'y': objAxis = (0,1,0)
		elif str(objAxis).lower() == 'z': objAxis = (0,0,1)
		elif str(objAxis).lower() == '-x': objAxis = (-1,0,0)
		elif str(objAxis).lower() == '-y': objAxis = (0,-1,0)
		elif str(objAxis).lower() == '-z': objAxis = (0,0,-1)
		else:
			print('Invalid axis value! Returning False...')
			return False
	
	# Transform Axis to World Space
	objMatrix = glTools.utils.matrix.getMatrix(obj)
	objAxis = glTools.utils.matrix.vectorMatrixMultiply(objAxis,objMatrix)
	
	# Normalize Transform Axis Vector
	objAxis = glTools.utils.mathUtils.normalizeVector(objAxis)
	
	# Check Axis Alignment
	alignDot = glTools.utils.mathUtils.dotProduct(axis,objAxis)
	
	# Return Result
	if (1.0-alignDot) > abs(tol): return False
	else: return True

def inverseScaleConnected(joint,connectedTo=None):
	'''
	Check the inverse scale attr for incoming connections for the specified joint.
	@param joint: Joint to check inverse scale connections on.
	@type joint: str
	@param connectedTo: Check if inverse scale is connected to a specific object or object attribute. If None, return True for any existing connection.
	@type connectedTo: str or None
	'''
	# Check Joint
	if not mc.objExists(joint):
		print('Joint "'+joint+'" does not exist! Returning False...')
		return False
	if not glTools.utils.joint.isJoint(joint):
		print('Object "'+joint+'" is not a valid joint! Returning False...')
		return False
	
	# Check Inv Scale Connection
	invScaleConn = mc.listConnections(joint+'.inverseScale',s=True,d=False,p=True) or []
	if not invScaleConn: return False
	invScaleConn = mc.ls(invScaleConn[0])[0]
	invScaleObj = mc.ls(invScaleConn[0],o=True)[0]
	
	# Check Connection Source
	if connectedTo:
		if not mc.objExists(connectedTo):
			print('Specified connection source "'+connectedTo+'" does not exsit! Returning False...')
			return False
		if glTools.utils.attribute.isAttr(connectedTo):
			# Check As Attribute
			if not connectedTo == invScaleConn: return False
		else:
			# Check As Object
			if not connectedTo == invScaleObj: return False
	
	# Return Result
	return True

def attrsAtDefault(obj,attrList=None,tol=0.000001):
	'''
	Check object attributes are at default values.
	@param obj: Object to check default attribute values on.
	@type obj: str
	@param attrList: List of attributes to check.
	@type attrList: list or None
	'''
	# Check Object
	if not mc.objExists(obj):
		print('Object "'+obj+'" does not exist! Returning False...')
		return False
	
	# Check Attribute List
	if not attrList:
		attrList = []
		attrList += mc.listAttr(obj,k=True) or []
		attrList += mc.listAttr(obj,cb=True) or []
	
	# Get List of User Defined Attributes
	udAttrList = [mc.attributeName(obj+'.'+at,s=True) for at in mc.listAttr(obj,ud=True) or []]
	
	# Check Attribute Values
	for at in attrList:
		
		# Check Attribute Exists
		if not mc.attributeQuery(at,n=obj,ex=True):
			print('Object attribute "'+obj+'.'+at+'" not found!')
			continue
		
		# Check Value
		attr = mc.attributeName(obj+'.'+at,s=True)
		if attr in ['tx','ty','tz','rx','ry','rz']:
			# Translate / Rotate
			if abs(mc.getAttr(obj+'.'+attr)) > tol:
				return False
		elif attr in ['sx','sy','sz']:
			# Scale
			if abs(1.0 - mc.getAttr(obj+'.'+attr)) > tol:
				return False
		else:
			# User Defined
			if attr in udAttrList:
				defVal = mc.addAttr(obj+'.'+attr,q=True,dv=True)
				if abs(defVal - mc.getAttr(obj+'.'+attr)) > tol:
					return False
	
	# =================
	# - Return Result -
	# =================
	
	return True

def childJointOffset():
	'''
	'''
	pass
