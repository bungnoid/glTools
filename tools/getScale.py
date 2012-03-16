import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.matrix

import math

def getScale(obj,worldSpace=False,method='max',boundingBoxScale=False):
	'''
	Return a relative scale value for the specified object.
	@param obj: Object to get scale from.
	@type obj: str
	@param worldSpace: Calculate scale in world or local (object) space.
	@type worldSpace: bool
	@param method: The method to determine scale value. Accepted values - "min","max","average","diagonal","x","y","z".
	@type method: str
	@param boundingBoxScale: Use the object bounding box to determine scale rather than the transform.
	@type boundingBoxScale: Bool
	'''
	# Check geometry
	if obj and not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!')
	
	# Check method
	methodList = ['min','max','average','diagonal']
	if not methodList.count(method):
		raise Exception('Invalid method value! ("'+method+'")')
	
	# ===================
	# - Get Scale (XYZ) -
	# ===================
	
	scale = [0,0,0]
	
	# Transform Scale
	if not boundingBoxScale:
		
		mat = glTools.utils.matrix.getMatrix(obj,local=not(worldSpace))
		scalePtr = OpenMaya.MScriptUtil().asDoublePtr()
		OpenMaya.MTransformationMatrix(mat).getScale(scalePtr,OpenMaya.MSpace.kObject)
		scale[0] = OpenMaya.MScriptUtil().getDoubleArrayItem(scalePtr,0)
		scale[1] = OpenMaya.MScriptUtil().getDoubleArrayItem(scalePtr,1)
		scale[2] = OpenMaya.MScriptUtil().getDoubleArrayItem(scalePtr,2)
	
	# Bounding Box Scale
	else:
		
		bBox = glTools.utils.base.getMBoundingBox(obj,worldSpace=worldSpace)
		scale[0] = bBox.width()
		scale[1] = bBox.height()
		scale[2] = bBox.depth()
	
	# ===========================
	# - Determine Overall Scale -
	# ===========================
	
	scaleVal = 0.0
	
	# Minimum
	if method == 'min':
		scaleVal = scale[0]
		if scale[1] < scaleVal: scaleVal = scale[1]
		if scale[2] < scaleVal: scaleVal = scale[2]
	
	# Maximum
	elif method == 'max':
		scaleVal = scale[0]
		if scale[1] > scaleVal: scaleVal = scale[1]
		if scale[2] > scaleVal: scaleVal = scale[2]
	
	# Average
	elif method == 'average':
		scaleVal = (scale[0]+scale[1]+scale[2])/3
	
	# Diagonal
	elif method == 'diagonal':
		scaleVal = math.sqrt((scale[0]*scale[0])+(scale[1]*scale[1])+(scale[2]*scale[2]))
	
	# X
	if method == 'x': scaleVal = scale[0]
	
	# Y
	if method == 'y': scaleVal = scale[1]
	
	# Z
	if method == 'z': scaleVal = scale[2]
	
	# =================
	# - Return Result -
	# =================
	
	return scaleVal
