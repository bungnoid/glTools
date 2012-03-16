import maya.cmds as mc
import maya.OpenMaya as OpenMaya

def mag(vector=(0,0,0)):
	'''
	Returns the magnitude (length) of a specified vector.
	@param vector: Vector or return the length of
	@type vector: tuple
	'''
	return OpenMaya.MVector(vector[0],vector[1],vector[2]).length()

def normalizeVector(vector=(0,0,0)):
	'''
	Returns normalized version of the input vector vector.
	@param vector: Vector to normalize
	@type vector: tuple
	'''
	normal = OpenMaya.MVector(vector[0],vector[1],vector[2]).normal()
	return (normal.x,normal.y,normal.z)

def dotProduct(vector1=(0.0,0.0,0.0),vector2=(0.0,0.0,0.0)):
	'''
	Returns the dot product (inner product) of 2 vectors
	@param vector1: First vector for the dot product operation
	@type vector1: tuple
	@param vector2: Second vector for the dot product operation
	@type vector2: tuple
	'''
	vec1 = OpenMaya.MVector(vector1[0],vector1[1],vector1[2])
	vec2 = OpenMaya.MVector(vector2[0],vector2[1],vector2[2])
	return vec1 * vec2

def distanceBetween(point1=[0.0,0.0,0.0],point2=[0.0,0.0,0.0]):
	'''
	Returns the dot product (inner product) of 2 vectors
	@param point1: Start point of the distance calculation
	@type point1: tuple
	@param point2: End point of the distance calculation
	@type point1: tuple
	'''
	pnt1 = OpenMaya.MPoint(point1[0],point1[1],point1[2],1.0)
	pnt2 = OpenMaya.MPoint(point2[0],point2[1],point2[2],1.0)
	return OpenMaya.MVector(pnt1-pnt2).length()

def offsetVector(point1=(0.0,0.0,0.0),point2=(0.0,0.0,0.0)):
	'''
	Return the offset vector between point1 and point2
	@param point1: Start point of the offset calculation
	@type point1: tuple
	@param point2: End point of the offset calculation
	@type point1: tuple
	'''
	pnt1 = OpenMaya.MPoint(point1[0],point1[1],point1[2],1.0)
	pnt2 = OpenMaya.MPoint(point2[0],point2[1],point2[2],1.0)
	vec = pnt2 - pnt1
	return (vec.x,vec.y,vec.z)

def crossProduct(vector1=(0.0,0.0,0.0),vector2=(0.0,0.0,0.0)):
	'''
	Returns the cross product of 2 vectors
	@param vector1: First vector for the cross product operation
	@type vector1: tuple
	@param vector2: Second vector for the cross product operation
	@type vector2: tuple
	'''
	vec1 = OpenMaya.MVector(vector1[0],vector1[1],vector1[2])
	vec2 = OpenMaya.MVector(vector2[0],vector2[1],vector2[2])
	crossProduct = vec1 ^ vec2
	return (crossProduct.x,crossProduct.y,crossProduct.z)

def averagePosition(pos1=(0.0,0.0,0.0),pos2=(0.0,0.0,0.0),weight=0.5):
	'''
	Return the average of the 2 input positions. You can weight the result between zero and one.
	A weight of 0.0 will favour the first input position, a weight of 1.0 will favour the second input position
	@param pos1: First input position
	@type pos1: tuple
	@param pos2: Second input position
	@type pos2: tuple
	@param weight: The amount to weight between the 2 input positions
	@type weight: float
	'''
	return (pos1[0]+((pos2[0]-pos1[0])*weight),pos1[1]+((pos2[1]-pos1[1])*weight),pos1[2]+((pos2[2]-pos1[2])*weight))

def smoothStep(value,rangeStart=0.0,rangeEnd=1.0,smooth=1.0):
	'''
	Interpolate between 2 float values using hermite interpolation.
	@param value: Value to smooth
	@type value: float
	@param rangeStart: Minimum value of interpolation range
	@type rangeStart: float
	@param rangeEnd: Maximum value of interpolation range
	@type rangeEnd: float
	@param smooth: Strength of the smooth applied to the value
	@type smooth: float
	'''
	# Get range
	rangeVal = rangeEnd - rangeStart
	# Normalize value
	nValue = value / rangeVal
	# Get smooth value
	sValue = pow(nValue,2) * (3-(nValue*2))
	sValue = nValue + ((sValue-nValue)*smooth)
	value = rangeStart + (rangeVal * sValue)
	# Return result
	return value

def distributeValue(samples,spacing=1.0,rangeStart=0.0,rangeEnd=1.0):
	'''
	Returns a list of values distributed between a start and end range
	@param samples: Number of values to sample across the value range
	@type samples: int
	@param spacing: Incremental scale for each sample distance
	@type spacing: float
	@param rangeStart: Minimum value in the sample range
	@type rangeStart: float
	@param rangeEnd: Maximum value in the sample range
	@type rangeEnd: float
	'''
	# Get value range
	vList = [rangeStart]
	vDist = abs(rangeEnd - rangeStart)
	unit = 1.0
	# Find the unit distance
	factor = 1.0
	for i in range(samples-2):
		unit += factor * spacing
		factor *= spacing
	unit = vDist/unit
	totalUnit = unit
        # Build sample list
	for i in range(samples-2):
		multFactor = totalUnit/vDist
		vList.append(rangeStart-((rangeStart - rangeEnd) * multFactor))
		unit *= spacing
		totalUnit += unit
	# Append final sample value
	vList.append(rangeEnd)
	# Return result
	return vList

def inverseDistanceWeight1D(valueArray,sampleValue,valueDomain=(0,1),cycleValue=False):
	'''
	Return the inverse distance weight for a specified sample point given an array of scalar values.
	@param valueArray: Value array to calculate weights from
	@type valueArray: list
	@param sampleValue: The sample point to calculate weights for
	@type sampleValue: float
	@param valueDomain: The minimum and maximum range of the value array
	@type valueDomain: tuple or list
	@param cycleValue: Calculate distance based on a closed loop of values
	@type cycleValue: bool
	'''
	# Initialize method varialbles
	distArray = []
	totalInvDist = 0.0
	
	# Initialize weightArray
	wtArray = []
	
	# Calculate inverse distance weight
	for v in range(len(valueArray)):
		# Calculate distance
		dist = abs(sampleValue - valueArray[v])
		
		# Check cycle value
		if cycleValue:
			valueDomainLen = valueDomain[1]-valueDomain[0]
			fCycDist = abs(sampleValue - (valueArray[v] + valueDomainLen))
			rCycDist = abs(sampleValue - (valueArray[v] - valueDomainLen))
			if fCycDist < dist: dist = fCycDist
			if rCycDist < dist: dist = rCycDist
		
		# Check zero distance
		if dist < 0.00001: dist = 0.00001
		
		# Append distance
		distArray.append(dist)
		totalInvDist += 1.0/dist
	
	# Normalize value weights
	wtArray = [(1.0/d)/totalInvDist for d in distArray]
	
	# Return result
	return wtArray

def inverseDistanceWeight3D(pointArray,samplePoint):
	'''
	Return the inverse distance weight for a specified sample point given an array of scalar values.
	@param pointArray: Point array to calculate weights from
	@type pointArray: list of tuples or lists
	@param samplePoint: The sample point to calculate weights for
	@type samplePoint: tuple or list
	'''
	# Initialize method varialbles
	distArray = []
	totalInvDist = 0.0
	
	# Initialize weightArray
	wtArray = []
	
	# Calculate inverse distance weight
	for i in range(len(pointArray)):
		# Calculate distance
		dist = distanceBetween(samplePoint - pointArray[v])
		
		# Check zero distance
		if dist < 0.00001: dist = 0.00001
		
		# Append distance
		distArray.append(dist)
		totalInvDist += 1.0/dist
	
	# Normalize value weights
	wtArray = [(1.0/d)/totalInvDist for d in distArray]
	
	# Return result
	return wtArray
