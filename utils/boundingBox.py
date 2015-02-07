import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base

def geometryBoundingBox(geometry,worldSpace=True,noIntermediate=True,visibleOnly=True):
	'''
	Get an accurate bounding box from the geometry shapes under the specified geometry (transform or group).
	@param geometry: Geometry to return accurate bounding box for
	@type geometry: str or list
	'''
	# Initialize Object Classes
	geoDagPath = OpenMaya.MDagPath()
	selectionList = OpenMaya.MSelectionList()
	
	# Initialize empty bounding box
	bbox = OpenMaya.MBoundingBox()
	
	# Get Visible Geometry (Shapes)
	geoShapes = mc.ls(mc.listRelatives(geometry,ad=True,pa=True),noIntermediate=noIntermediate,geometry=True,visible=visibleOnly)
	
	# Expand Bounding Box
	for shape in geoShapes:
		selectionList.clear()
		OpenMaya.MGlobal.getSelectionListByName(shape,selectionList)
		selectionList.getDagPath(0,geoDagPath)
		bboxShape = OpenMaya.MFnDagNode(geoDagPath).boundingBox()
		if worldSpace: bboxShape.transformUsing(geoDagPath.inclusiveMatrix())
		bbox.expand(bboxShape)
	
	# Get Bounding Box Min/Max (as MPoint)
	mn = bbox.min()
	mx = bbox.max()

	# Return Formatted Result
	return [mn.x,mn.y,mn.z,mx.x,mx.y,mx.z]

def calcBoundingBox(ptList):
	'''
	Return bounding box that contains the specified list of points.
	@param ptList: Geometry to return bounding box for
	@type ptList: str
	'''
	# Initialize Bounding Box
	bbox = OpenMaya.MBoundingBox()
	
	# Add Points
	for pt in ptList:
		
		# Get MPoint
		mpt = glTools.utils.base.getMPoint(pt)
		
		# Expand BoundingBox
		if not bbox.contains(mpt): bbox.expand(mpt)
	
	# Return Result
	return bbox

def getBoundingBox(geometry,worldSpace=True):
	'''
	Return bounding box for the specified geometry.
	@param geometry: Geometry to return bounding box for
	@type geometry: str
	@param worldSpace: Calculate bounding box in world or local space
	@type worldSpace: bool
	'''
	return glTools.utils.base.getMBoundingBox(geometry,worldSpace=worldSpace)

def getBoundingBoxMin(geometry,worldSpace=True):
	'''
	Return bounding box minimum for the specified geometry.
	@param geometry: Geometry to return bounding box for
	@type geometry: str
	@param worldSpace: Calculate bounding box in world or local space
	@type worldSpace: bool
	'''
	# Get MBoundingBox
	bbox = getBoundingBox(geometry,worldSpace=worldSpace)
	
	# Get Min
	mn = bbox.min()
	
	# Return Result
	return [mn[0],mn[1],mn[2]]

def getBoundingBoxMax(geometry,worldSpace=True):
	'''
	Return bounding box maximum for the specified geometry.
	@param geometry: Geometry to return bounding box for
	@type geometry: str
	@param worldSpace: Calculate bounding box in world or local space
	@type worldSpace: bool
	'''
	# Get MBoundingBox
	bbox = getBoundingBox(geometry,worldSpace=worldSpace)
	
	# Get Max
	mx = bbox.max()
	
	# Return Result
	return [mx[0],mx[1],mx[2]]

def getBoundingBoxCenter(geometry,worldSpace=True):
	'''
	Return bounding box center for the specified geometry.
	@param geometry: Geometry to return bounding box for
	@type geometry: str
	@param worldSpace: Calculate bounding box in world or local space
	@type worldSpace: bool
	'''
	# Get MBoundingBox
	bbox = getBoundingBox(geometry,worldSpace=worldSpace)
	
	# Get Min/Max
	ct = bbox.center()
	
	# Return Result
	return [ct[0],ct[1],ct[2]]

def getBoundingBoxScale(geometry,worldSpace=True):
	'''
	Return bounding box scale for the specified geometry.
	@param geometry: Geometry to return bounding box for
	@type geometry: str
	@param worldSpace: Calculate bounding box in world or local space
	@type worldSpace: bool
	'''
	# Get Bounding Box Min/Max
	minPt = getBoundingBoxMin(geometry,worldSpace=worldSpace)
	maxPt = getBoundingBoxMax(geometry,worldSpace=worldSpace)
	
	# Calculate Scale
	scale = [maxPt[i]-minPt[i] for i in range(3)]
	
	# Return Result
	return scale

def match(geometry,targetGeometry,worldSpace=True):
	'''
	Match one specified geometry object to a target geometry object
	in position and scale based on geometry bounding boxes.
	@param geometry: Geometry to match to target
	@type geometry: str
	@param targetGeometry: Target geometry to match to
	@type targetGeometry: str
	@param worldSpace: Calculate bounding boxes in world or local space
	@type worldSpace: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not geometry: raise Exception('Invalid or empty geometry argument value! (geometry)')
	if not targetGeometry: raise Exception('Invalid or empty target geometry argument value! (targetGeometry)')
	if not mc.objExists(geometry):
		raise Exception('Geometry object "'+geometry+'" does not exist!')
	if not mc.objExists(targetGeometry):
		raise Exception('Target geometry object "'+targetGeometry+'" does not exist!')
	
	# ========================
	# - Match Bounding Boxes -
	# ========================
	
	# Get Current Position and Scale
	sourcePt = getBoundingBoxCenter(geometry)
	sourceSc = getBoundingBoxScale(geometry)
	
	# Get Target Position and Scale
	targetPt = getBoundingBoxCenter(targetGeometry)
	targetSc = getBoundingBoxScale(targetGeometry)
	
	# Calc/Apply New Position and Scale
	mc.scale(targetSc[0]/sourceSc[0],targetSc[1]/sourceSc[1],targetSc[2]/sourceSc[2],geometry,pivot=sourcePt,relative=True)
	mc.move(targetPt[0]-sourcePt[0],targetPt[1]-sourcePt[1],targetPt[2]-sourcePt[2],geometry,relative=True)

