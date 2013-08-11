import maya.cmds as mc

import glTools.surfaceSkin.utilities
import glTools.utils.component
import glTools.utils.curve
import glTools.utils.surface

def setTargetCoord(surfaceSkin,controlPoint,surfacePoint):
	'''
	Set the target surface coordinate for the specified control point
	@param surfaceSkin: surfaceSkin node to apply the coordinates to
	@type surfaceSkin: str
	@param controlPoint: Control point set the target coordinate for
	@type controlPoint: str
	@param surfacePoint: Target UV surface coordiniate
	@type surfacePoint: tuple or list
	'''
	# Get surfacSkin utility object
	ssUtil = glTools.surfaceSkin.utils.SurfaceSkinUtilities()
	
	# Check surfaceSkin
	if not ssUtil.verifyNode(surfaceSkin):
		raise Exception('Object "'+surfaceSkin+'" is not a valid surfaceSkin node!')
	
	# Get influence surface
	influence = surfacePoint.split('.')[0]
	influenceIndex = ssUtil.getInfluenceIndex(influence,surfaceSkin)
	uv = surfacePoint.split('[')
	u = float(uv[1].split(']')[0])
	v = float(uv[2].split(']')[0])
	
	# Get controlPoint index
	geometry = controlPoint.split('.')[0]
	if mc.objectType(geometry) == 'transform': geometry = mc.listRelatives(geometry,s=True,ni=True)[0]
	index = glTools.utils.component.getSingleIndexComponentList([controlPoint])[geometry][0]
	
	# Get influence data
	indexArray = ssUtil.getIndexArray(geometry,influence,surfaceSkin)
	uCoordArray = ssUtil.getCoordUArray(geometry,influence,surfaceSkin)
	vCoordArray = ssUtil.getCoordVArray(geometry,influence,surfaceSkin)
	
	# Set target coord vaules
	indexId = indexArray.index(index)
	uCoordArray[indexId] = u
	vCoordArray[indexId] = v
	
	# Apply target coord values
	ssUtil.setCoordArray(geometry,influence,surfaceSkin,uCoordArray,vCoordArray)

def setTargetCoordSel(surfaceSkin):
	'''
	Selection based wrapper for setTargetCoord
	@param surfaceSkin: surfaceSkin node to apply the coordinates to
	@type surfaceSkin: str
	'''
	# Get surfacePoint selection
	surfacePoint = mc.filterExpand(sm=41)[0]
	
	# Get controlPoint
	controlPoints = mc.filterExpand(sm=31)
	if not controlPoints: controlPoints = mc.filterExpand(sm=28)
	if not controlPoints: raise Exception('No components selected to set target coordinates for!!')
	
	# Apply target coord
	for cp in controlPoints: setTargetCoord(surfaceSkin,cp,surfacePoint)

def getCoord(surfaceSkin,influence,controlPoint=''):
	'''
	Get the current target surface coordinate of the specified influence for the given control point
	@param surfaceSkin: surfaceSkin node to get the coordinates for
	@type surfaceSkin: str
	@param influence: Influence surface to query
	@type influence: str
	@param controlPoint: Control point to get the target coordinate for
	@type controlPoint: str
	'''
	# Check controlPointList
	if not controlPoint:
		controlPoint = mc.filterExpand(sm=(28,31))
		if not controlPoint: raise Exception('No components specified for get coordinate operation!!')
		else: controlPoint = controlPoint[0]
	
	# Get surfacSkin utility object
	ssUtil = glTools.surfaceSkin.utils.SurfaceSkinUtilities()
	
	# Check surfaceSkin node
	if not ssUtil.verifyNode(surfaceSkin):
		raise Exception('Object "'+surfaceSkin+'" is not a valid surfaceSkin node!')
	
	# Check influence
	if not ssUtil.isInfluence(influence,surfaceSkin):
		raise Exception('Influence "'+influence+'" does not affect surfaceSkin "'+surfaceSkin+'"!!')
	
	# Get controlPoint info
	controlPt = glTools.utils.component.getSingleIndexComponentList([controlPoint])
	geometry = controlPt.keys()[0]
	index = controlPt[geometry][0]
	
	# Check affected geometry
	if not ssUtil.getAffectedGeometry(surfaceSkin,getShapes=True).keys().count(geometry):
		raise Exception('Geometry "'+geometry+'" is not affected by surfaceSkin "'+surfaceSkin+'"!!')
	
	# Get influence index data
	indexArray = ssUtil.getIndexArray(geometry,influence,surfaceSkin)
	# Check indexArray
	if not indexArray.count(index):
		raise Exception('Control point "'+controlPoint+'" is not a member of surfaceSkin influence "'+influence+'"!!')
	
	# Get influence coordinate data
	uCoordArray = ssUtil.getCoordUArray(geometry,influence,surfaceSkin)
	vCoordArray = ssUtil.getCoordVArray(geometry,influence,surfaceSkin)
	
	# Return result
	indexId = indexArray.index(index)
	return(uCoordArray[indexId],vCoordArray[indexId])

def averageCoord(surfaceSkin,influence,controlPointList=[]):
	'''
	Get the averaged target surface coordinate of the specified influence for the given control points
	@param surfaceSkin: surfaceSkin node to get the coordinates for
	@type surfaceSkin: str
	@param influence: Influence surface to query
	@type influence: str
	@param controlPointList: List of control points to get the target coordinate for
	@type controlPointList: str
	'''
	# Check controlPointList
	if not controlPointList: controlPointList = mc.filterExpand(sm=(28,31))
	if not controlPointList: raise Exception('No components specified for average coordinate operation!!')
	
	# Get surfacSkin utility object
	ssUtil = glTools.surfaceSkin.utils.SurfaceSkinUtilities()
	
	# Get coord average
	uv = [0,0]
	controlPointCnt = len(controlPointList)
	# Iterate over control point list
	for controlPoint in controlPointList:
		# Get control point target coordinate
		cpUV = getCoord(surfaceSkin,influence,controlPoint)
		uv[0] += cpUV[0]
		uv[1] += cpUV[1]
	# Average coordinates
	uv[0] /= controlPointCnt
	uv[1] /= controlPointCnt
	
	# Return result
	return (uv[0],uv[1])

def applyCoord(surfaceSkin,influence,controlPoint='',uvCoord=[]):
	'''
	Apply a given surface coordinate to the specified surfaceSkin influence and control point
	@param surfaceSkin: surfaceSkin node to apply the coordinates to
	@type surfaceSkin: str
	@param influence: surfaceSkin influence to get coordinate for
	@type influence: str
	@param controlPoint: Control point set the target coordinate for
	@type controlPoint: str
	@param uvCoord: Target UV surface coordiniate
	@type uvCoord: tuple or list
	'''
	# Check controlPointList
	if not controlPoint:
		controlPoint = mc.filterExpand(sm=(28,31))
		if not controlPoint: raise Exception('No component specified for apply coordinate operation!!')
		else: controlPoint = controlPoint[0]
	
	# Get surfacSkin utility object
	ssUtil = glTools.surfaceSkin.utils.SurfaceSkinUtilities()
	
	# Check surfaceSkin node
	if not ssUtil.verifyNode(surfaceSkin):
		raise Exception('Object "'+surfaceSkin+'" is not a valid surfaceSkin node!')
	
	# Check influence
	if not ssUtil.isInfluence(influence,surfaceSkin):
		raise Exception('Influence "'+influence+'" does not affect surfaceSkin "'+surfaceSkin+'"!!')
	
	# Get controlPoint info
	controlPt = glTools.utils.component.getSingleIndexComponentList([controlPoint])
	geometry = controlPt.keys()[0]
	index = controlPt[geometry][0]
	
	# Check affected geometry
	if not ssUtil.getAffectedGeometry(surfaceSkin,getShapes=True).keys().count(geometry):
		raise Exception('Geometry "'+geometry+'" is not affected by surfaceSkin "'+surfaceSkin+'"!!')
	
	# Get influence index data
	indexArray = ssUtil.getIndexArray(geometry,influence,surfaceSkin)
	# Check indexArray
	if not indexArray.count(index):
		raise Exception('Control point "'+controlPoint+'" is not a member of surfaceSkin influence "'+influence+'"!!')
	# Get influence coordinate data
	uCoordArray = ssUtil.getCoordUArray(geometry,influence,surfaceSkin)
	vCoordArray = ssUtil.getCoordVArray(geometry,influence,surfaceSkin)
	
	# Determine target coord
	indexId = indexArray.index(index)
	uCoordArray[indexId] = uvCoord[0]
	vCoordArray[indexId] = uvCoord[1]

	# Apply target coord values
	ssUtil.setCoordArray(geometry,influence,surfaceSkin,uCoordArray,vCoordArray)

def curveCoord(surfaceSkin,influence,controlPoints,curve):
	'''
	Set the target coordinates for the specified control points to lie along a given isoparm
	@param surfaceSkin: surfaceSkin node to apply the coordinates to
	@type surfaceSkin: str
	@param influence: surfaceSkin influence to get coordinate for
	@type influence: str
	@param controlPoints: List of control points to set the target coordinates for
	@type controlPoints: list
	@param curve: Curve to derive coordinates from
	@type curve: str
	'''
	# Check surfaceSkin
	if not ssUtil.verifyNode(surfaceSkin):
		raise Exception('Object "'+surfaceSkin+'" is not a valid surfaceSkin node!')
	
	# Iterate through control point list
	for controlPoint in controlPoints:
		# Get component position
		pos = mc.pointPosition(controlPoint)
		# Get closest point on curve
		cCoord = glTools.utils.curve.closestPoint(curve,pos)
		pos = mc.pointPosition(curve+'.u['+str(cCoord)+']')
		# Get surface coordinate
		uvCoord = glTools.utils.surface.closestPoint(influence,pos)
		# Apply Coord
		applyCoord(surfaceSkin,influence,controlPoint,uvCoord)

def isoparmCoord(surfaceSkin,influence,controlPoints,coord,direction='u'):
	'''
	Set the target coordinates for the specified control points to lie along a given isoparm
	@param surfaceSkin: surfaceSkin node to apply the coordinates to
	@type surfaceSkin: str
	@param influence: surfaceSkin influence to get coordinate for
	@type influence: str
	@param controlPoints: List of control points to set the target coordinates for
	@type controlPoints: list
	@param coord: Coordinate value of the target isoparm
	@type coord: float
	@param direction: Direction of the isoparm
	@type direction: str
	'''
	# Get surface curve
	crv = mc.duplicateCurve(influence+'.'+direction+'['+str(coord)+']',ch=False,rn=0,local=0,n=influence+'TEMP_CRV')[0]
	
	# Iterate through control point list
	for controlPoint in controlPoints:
		# Get component position
		pos = mc.pointPosition(controlPoint)
		# Get closest point on curve
		cCoord = glTools.utils.curve.closestPoint(crv,pos)
		# Apply Coord
		uvCoord = (0,0)
		if direction == 'u': uvCoord = (coord,cCoord)
		else: uvCoord = (cCoord,coord)
		applyCoord(surfaceSkin,influence,controlPoint,uvCoord)
	
	# Delete surface curve
	mc.delete(crv)
	
def isoparmCoordSel(surfaceSkin):
	'''
	Selection based wrapper for isoparmCoord
	@param surfaceSkin: surfaceSkin node to apply the isoparm coordinates to
	@type surfaceSkin: str
	'''
	# Get isoparm selection
	iso = mc.filterExpand(sm=45)
	
	# Get component selection
	controlPoints = mc.filterExpand(sm=31)
	if not controlPoints: controlPoints = mc.filterExpand(sm=28)
	if not controlPoints: raise Exception('No components selected to set target coordinates for!!')
	
	# Get influence
	influence = iso[0].split('.')[0]
	# Get direction
	isoComp = iso[0].split('.')[-1]
	direction = isoComp.split('[')[0]
	coord = isoComp.split('[')[-1]
	coord = float(coord.replace(']',''))
	
	# Apply Coords
	isoparmCoord(surfaceSkin,influence,controlPoints,coord,direction)

