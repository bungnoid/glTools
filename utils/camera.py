import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.mathUtils
import glTools.utils.transform

def isCamera(obj):
	'''
	Check if specified object is a valid camera
	@param obj: The object to check as camera.
	@type obj: str
	'''
	# Check object exists
	if not mc.objExists(obj): return False
	
	# Get Shapes
	objShapes = [obj]
	if glTools.utils.transform.isTransform(obj):
		objShapes = mc.listRelatives(obj,s=True,pa=True)
		if not objShapes: return False
	
	# Check Shapes
	for shape in objShapes:
		if mc.objectType(shape) == 'camera':
			return True
	
	# Return Result
	return False

def getActiveCam():
	'''
	Return the active camera for the current viewport.
	'''
	return mc.lookThru(q=True)

def getEyePoint(camera):
	'''
	Get the camera
	'''
	# Check Camera
	if not isCamera(camera):
		raise Exception('Object "'+camera+'" is not a valid camera!')
	
	# Get Eye Point
	cameraShape = mc.ls(mc.listRelatives(camera,s=True,pa=True),type='camera')[0]
	cameraDagPath = glTools.utils.base.getMDagPath(cameraShape)
	cameraFn = OpenMaya.MFnCamera(cameraDagPath)
	cameraPt = cameraFn.eyePoint(OpenMaya.MSpace.kWorld)
	
	# Return Result
	return [cameraPt.x,cameraPt.y,cameraPt.z]

def distToCam(node,cam):
	'''
	Calculate distance between a specified node (transform) and a camera.
	@param node: Transform node to calculate distance to camera from.
	@type node: str
	@param cam: Camera to calculate distance from.
	@type cam: str
	'''
	# Checks
	if not mc.objExists(node):
		raise Exception('Object "'+node+'" does not exist!')
	if not glTools.utils.transform.isTransform(node):
		raise Exception('Object "'+node+'" is not a valid transform!')
	if not mc.objExists(cam):
		raise Exception('Camera "'+cam+'" does not exist!')
	if not isCamera(cam):
		raise Exception('Object "'+cam+'" is not a valid camera!')
	
	# Get Dist to Camera
	camPt = getEyePoint(cam)
	nodePt = mc.xform(node,q=True,ws=True,rp=True)
	dist = glTools.utils.mathUtils.distanceBetween(camPt,nodePt)
	
	# Return Result
	return dist
