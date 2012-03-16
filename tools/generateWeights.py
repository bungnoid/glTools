import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.mathUtils
import glTools.utils.curve
import glTools.utils.mesh

def gradientWeights(geometry,pnt1,pnt2,smooth=0):
	'''
	Generate a gradient weight list for a specified geometry.
	The weight gradient is defined between the 2 input points.
	@param geometry: The geometry to generate weights for
	@type geometry: str
	@param pnt1: Start point of the gradient
	@type pnt1: str
	@param pnt2: End point of the gradient
	@type pnt2: str
	@param smooth: Number of smoothStep iterations
	@type smooth: int
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise UserInputError('Object "'+geometry+'" does not exist!')
	
	# Check points
	pnt1 = glTools.utils.base.getMPoint(pnt1)
	pnt2 = glTools.utils.base.getMPoint(pnt2)
	# Calc offset vector
	pntVec = pnt2 - pnt1
	pntVecNorm = pntVec.normal()
	pntLen = pntVec.length()
	
	# Get points to generate weights from
	pointList = glTools.utils.base.getMPointArray(geometry)
	
	# Build weight array
	wtList = []
	for i in range(pointList.length()):
		offsetVec = pointList[i] - pnt1
		wt = ((pntVecNorm*offsetVec)/pntLen)
		if wt < 0.0: wt = 0.0
		if wt > 1.0: wt = 1.0
		for i in range(int(smooth)):
			wt = glTools.utils.mathUtils.smoothStep(wt)
		wtList.append(wt)
	
	# Return result
	return wtList

def gradientWeights3Point(geometry,inner,mid,outer,smooth=0):
	'''
	Generate a gradient weight list for a specified geometry.
	The weight gradient is defined by 3 input points.
	@param geometry: The geometry to generate weights for
	@type geometry: str
	@param inner: Inner end point of the gradient
	@type inner: str
	@param mid: Mid point of the gradient
	@type mid: str
	@param outer: Outer end point of the gradient
	@type outer: str
	@param smooth: Number of smoothStep iterations
	@type smooth: int
	'''
	# Get Inner Weight List
	innerWtList = gradientWeights(geometry,inner,mid,smooth)
	
	# Get Outer Weight List
	outerWtList = gradientWeights(geometry,outer,mid,smooth)
	
	# Calculate Final Weight List
	wtList = [innerWtList[i]*outerWtList[i] for i in range(len(innerWtList))]
	
	# Return result
	return wtList

def radialWeights(geometry,center,radius,innerRadius=0.0,smooth=0):
	'''
	Generate a radial weight list for a specified geometry.
	The weight center and radius are defined by the input arguments.
	@param geometry: The geometry to generate weights for
	@type geometry: str
	@param center: Center of the radial weights
	@type center: str
	@param radius: Maximum radius for the radial weights
	@type radius: str
	@param innerRadius: Minimum radius for the radial weights
	@type innerRadius: str
	@param smooth: Number of smoothStep iterations
	@type smooth: int
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise UserInputError('Object "'+geometry+'" does not exist!')
	
	# Check center point
	pnt = glTools.utils.base.getMPoint(center)
	
	# Get points to generate weights from
	pointList = glTools.utils.base.getMPointArray(geometry)
	
	# Build weight array
	wtList = []
	for i in range(pointList.length()):
		
		# Initialize zero weight value
		wt = 0.0
		
		# Calculate distance to radial center
		dist = (pnt-pointList[i]).length()
		
		# Generate weight value
		if dist < radius:
			wt = (radius-innerRadius-dist)/(radius-innerRadius)
			for i in range(int(smooth)):
				wt = glTools.utils.mathUtils.smoothStep(wt)
		
		# Append weight value to weight list
		wtList.append(wt)
	
	# Return result
	return wtList
	
def volumeWeights(geometry,volumeCenter,volumeBoundary,volumeInterior='',smoothValue=0):
	'''
	Generate a volume weight list for a specified geometry.
	The volume is defined by the volumeBoundary geometry.
	@param geometry: The geometry to generate weights for
	@type geometry: str
	@param volumeCenter: Volume center for the weights
	@type volumeCenter: str
	@param volumeBoundary: Outer volume boundary primative
	@type volumeBoundary: str
	@param volumeInterior: Inner volume boundary primative
	@type volumeInterior: str
	@param smooth: Number of smoothStep iterations
	@type smooth: int
	'''
	
	# NOT IMPLEMENTED!!
	raise Exception('NOT FULLY IMPLEMENTED!!')
	
	# Check geometry
	if not mc.objExists(geometry):
		raise UserInputError('Object "'+geometry+'" does not exist!')
	
	# Check volumeBoundary
	if not mc.objExists(volumeBoundary):
		raise UserInputError('Volume boundary "'+volumeBoundary+'" does not exist!')
	
	# Check volume center point
	volumeCenterPt = glTools.utils.base.getMPoint(volumeCenter)
	
	# Get volume geometry bounding box
	volumeBBox = glTools.utils.base.getMBoundingBox(volumeBoundary,worldSpace=True)
	
	# Get geometry point array
	geometryPtArray = glTools.utils.base.getMPointArray(geometry)
	
def geometryVolumeWeights(geometry,volumeCenter,volumeBoundary,volumeCenterCurve='',volumeInterior='',smoothValue=0):
	'''
	Generate a volume weight list for a specified geometry.
	The volume is defined by the volumeBoundary geometry.
	@param geometry: The geometry to generate weights for
	@type geometry: str
	@param volumeCenter: Volume center for the weights
	@type volumeCenter: str
	@param volumeBoundary: Outer volume boundary geometry
	@type volumeBoundary: str
	@param volumeInterior: Inner volume boundary geometry
	@type volumeInterior: str
	@param smooth: Number of smoothStep iterations
	@type smooth: int
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise UserInputError('Object "'+geometry+'" does not exist!')
	
	# Check volumeBoundary
	if not mc.objExists(volumeBoundary):
		raise UserInputError('Volume boundary "'+volumeBoundary+'" does not exist!')
	
	# Check volume center point
	volumeCenterPt = glTools.utils.base.getMPoint(volumeCenter)
	
	# Get volume geometry bounding box
	volumeBBox = glTools.utils.base.getMBoundingBox(volumeBoundary,worldSpace=True)
	
	# Check Volume Center Curve
	if volumeCenterCurve:
		if not mc.objExists(volumeCenterCurve):
			raise Exception('Volume center curve "'+volumeCenterCurve+'" does not exist!')
		curveFn = glTools.utils.curve.getCurveFn(volumeCenterCurve)
	
	# Get geometry point array
	geometryPtArray = glTools.utils.base.getMPointArray(geometry)
	
	# Iterate through geometry points
	wtList = []
	for i in range(geometryPtArray.length()):
		
		# Volume Bounding Box test
		if volumeBBox.contains(geometryPtArray[i]):
			
			# Check volume center curve
			if volumeCenterCurve:
				volumeCenterPt = curveFn.closestPoint(geometryPtArray[i])
			
			# Get offset from volume center
			offsetVec = geometryPtArray[i] - volumeCenterPt
			offsetDist = offsetVec.length()
			
			# Get distance to volume boundary
			boundaryPt = glTools.utils.mesh.intersect(volumeBoundary,volumeCenterPt,offsetVec,False)
			boundaryDist = (volumeCenterPt - OpenMaya.MPoint(boundaryPt[0],boundaryPt[1],boundaryPt[2],1.0)).length()
			
			# Get distance to interior volume boundary
			intBoundaryDist = 0.0
			if volumeInterior:
				intBoundaryPt = glTools.utils.mesh.intersect(volumeInterior,volumeCenterPt,offsetVec,False)
				intBoundaryDist = (volumeCenterPt - OpenMaya.MPoint(intBoundaryPt[0],intBoundaryPt[1],intBoundaryPt[2],1.0)).length()
			
			# Caluculate weight
			wt = 1.0
			if offsetDist > intBoundaryDist:
				if offsetDist < boundaryDist:
					wt = 1.0 - (offsetDist - intBoundaryDist)/(boundaryDist - intBoundaryDist)
					for n in range(int(smoothValue)): wt = glTools.utils.mathUtils.smoothStep(wt)
				else:
					wt = 0.0
			
			# Append to weight list
			wtList.append(wt)
			
		else:
			
			# Point is outside volume bounding box. Append zero weight
			wtList.append(0.0)
	
	# Return result
	return wtList

def curveProximityWeights(geometry,curve,maxDistance,minDistance=0.0,smoothValue=0):
	'''
	Generate a curve proximity weight list for a specified geometry.
	@param geometry: The geometry to generate weights for
	@type geometry: str
	@param curve: The curve to compare proximity to
	@type curve: str
	@param maxDistance: Maximum distance from the curve
	@type maxDistance: str
	@param minDistance: Minimum distance from the curve
	@type minDistance: str
	@param smooth: Number of smoothStep iterations
	@type smooth: int
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise UserInputError('Object "'+geometry+'" does not exist!')
	
	# Check curve
	if not glTools.utils.curve.isCurve(curve):
		raise Exception('Curve object "'+curve+'" is not a valid nurbs curve!')
	
	# Get vertex array
	geometryPtList = glTools.utils.base.getMPointArray(geometry)
	geometryPtLen = geometryPtList.length()
	
	# Get curve function set
	curveFn = glTools.utils.curve.getCurveFn(curve)
	
	# Get curve bounding box
	curveBbox = glTools.utils.base.getMBoundingBox(curve,worldSpace=True)
	# Expand bounding box
	curveBbox.expand(curveBbox.min() - OpenMaya.MVector(maxDistance,maxDistance,maxDistance))
	curveBbox.expand(curveBbox.max() + OpenMaya.MVector(maxDistance,maxDistance,maxDistance))
	
	# Build weight list
	wtList = []
	for i in range(geometryPtLen):
		
		# Check bounding box
		if curveBbox.contains(geometryPtList[i]):
			
			# Get distance to curve
			dist = curveFn.distanceToPoint(geometryPtList[i],OpenMaya.MSpace.kWorld)
			
			# Calculate weight value
			if dist <= minDistance: wt = 1.0
			elif dist > maxDistance: wt = 0.0
			else:
				wt = 1.0 - (dist - minDistance)/(maxDistance - minDistance)
				for n in range(int(smoothValue)): wt = glTools.utils.mathUtils.smoothStep(wt)
			
			# Append to weight list
			wtList.append(wt)
			
		else:
			
			# Point is outside volume bounding box. Append zero weight
			wtList.append(0.0)
			
	# Return result
	return wtList

def meshOffsetWeights(baseMesh,targetMesh,normalizeWeights=False,normalRayIntersect=False,smoothValue=0):
	'''
	Generate a mesh offset weight list for a specified geometry.
	The weights is defined as the offset distance between 2 mesh objects.
	@param baseMesh: The geometry to generate weights for
	@type baseMesh: str
	@param targetMesh: The offset target mesh
	@type targetMesh: str
	@param normalizeWeights: Normalize weight values to 0-1
	@type normalizeWeights: bool
	@param normalRayIntersect: Calculate offset as a normal ray cast intersection
	@type normalRayIntersect: str
	@param smooth: Number of smoothStep iterations
	@type smooth: int
	'''
	# Check input meshes
	if not glTools.utils.mesh.isMesh(baseMesh):
		raise Exception('BaseMesh object "'+baseMesh+'" is not a valid mesh!')
	if not glTools.utils.mesh.isMesh(targetMesh):
		raise Exception('TargetMesh object "'+targetMesh+'" is not a valid mesh!')
	
	# Get vertex arrays
	basePtList = glTools.utils.base.getMPointArray(baseMesh)
	targetPtList = glTools.utils.base.getMPointArray(targetMesh)
	
	basePtLen = basePtList.length()
	targetPtLen = targetPtList.length()
	
	if basePtLen != targetPtLen:
		raise Exception('Vertex count between the base and target mesh does not match!!')
	
	# Get base normal array
	normalArray = glTools.utils.mesh.getNormals(baseMesh,worldSpace=False)
	
	# Build offset list
	maxDist = 0.0
	distArray = []
	for i in range(basePtLen):
		
		# Determine target distance
		if normalRayIntersect:
			targetPt = glTools.utils.mesh.intersect(targetMesh,basePtList[i],normalArray[i],True)
			targetPt = glTools.utils.base.getMPoint(targetPt)
			dist = OpenMaya.MVector(normalArray[i]) * (targetPt - basePtList[i])
		else:
			offset = targetPtList[i] - basePtList[i]
			dist = OpenMaya.MVector(normalArray[i]) * offset
		
		# Smooth
		if normalizeWeights and smoothValue:
			for n in range(int(smoothValue)):
				dist = glTools.utils.mathUtils.smoothStep(dist)
		
		# Append to target distance array
		distArray.append(dist)
		
		# Check maxDistance
		if abs(dist) > maxDist: maxDist = abs(dist)
	
	# Normalize distance array
	if normalizeWeights:
		distArray = [i/maxDist for i in distArray]
		
	# Return result
	return maxDist, distArray
