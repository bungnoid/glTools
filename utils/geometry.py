import maya.cmds as mc

import glTools.utils.shape

def isGeometry(geometry):
	'''
	Check if the specified node is a valid geometry shape node.
	@param geometry: The node object to query as geometry
	@type geometry: str
	'''
	# Check Object Exists
	if not mc.objExists(geometry): return False
	
	# Check Shape
	if 'transform' in mc.nodeType(geometry,i=True):
		geoShape = mc.ls(mc.listRelatives(mesh,s=True,ni=True,pa=True) or [],geometry=True)
		if not geoShape: return False
		geometry = geoShape[0]
	
	# Check Geometry
	if 'geometryShape' in mc.nodeType(geometry,i=True): return True
	
	# Return Result
	return False

def geometryType(geometry):
	'''
	Return the geometry type of the first shape under the specified geometry object
	@param geometry: The geometry object to query
	@type geometry: str
	'''
	# Check Geometry
	if not mc.objExists(geometry):
		raise Exception('Geometry object "'+geometry+'" does not exist!!')
	
	# Get Shapes
	shapeList = glTools.utils.shape.getShapes(geometry,intermediates=False)
	if not shapeList:
		shapeList = glTools.utils.shape.getShapes(geometry,intermediates=True)
	if not shapeList:
		raise Exception('Geometry object "'+geometry+'" has no shape children!!')
	
	# Get Geometry Type
	geometryType = mc.objectType(shapeList[0])
	
	# Return Result
	return geometryType

def componentType(geometry):
	'''
	Return the geometry component type string, used for building component selection lists.
	@param geometry: The geometry object to query
	@type geometry: str
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise Exception('Geometry object "'+geometry+'" does not exist!!')
	
	# Get geometry type
	geoType = geometryType(geometry)
	
	# Define return values
	compType = {'mesh':'vtx','nurbsSurface':'cv','nurbsCurve':'cv','lattice':'pt','particle':'pt'}
	
	# Return result
	return compType[geoType]

def replace(sourceGeometry,destinationGeometry):
	'''
	Replace the geometry of one object with another
	@param sourceGeometry: The object that will provide the replacement geometry 
	@type sourceGeometry: str
	@param destinationGeometry: The object whose geometry will be replaced
	@type destinationGeometry: str
	'''
	# Check destinationGeometry and sourceGeometry
	if not mc.objExists(destinationGeometry):
		raise Exception('Destination geometry "'+destinationGeometry+'" does not exist!!')
	if not mc.objExists(sourceGeometry):
		raise Exception('Source geometry "'+sourceGeometry+'" does not exist!!')
	
	# Determine geometry types
	sourceShape = sourceGeometry
	sourceGeoType = geometryType(sourceGeometry)
	if mc.objectType(sourceShape) == 'transform':
		sourceShapes = glTools.utils.shape.getShapes(sourceGeometry,intermediates=False)
		sourceIntShapes = glTools.utils.shape.getShapes(sourceGeometry,intermediates=True)
		sourceShape = sourceShapes[0]
		if sourceIntShapes:
			if sourceGeoType == 'mesh':
				if mc.listConnections(sourceShapes[0]+'.inMesh',s=True,d=False):
					for intShape in sourceIntShapes:
						if mc.listConnections(intShape+'.outMesh',s=False,d=True):
							sourceShape = intShape
							break
			elif (sourceGeoType == 'nurbsSurface') or (sourceGeoType == 'nurbsCurve'):
				if mc.listConnections(sourceShapes[0]+'.create',s=True,d=False):
					for intShape in sourceIntShapes:
						if mc.listConnections(intShape+'.local',s=False,d=True):
							sourceShape = intShape
							break
			else:
				raise Exception('Unknown geometry type "'+sourceGeoType+'" is not supported!!')
		
	destinationShape = destinationGeometry
	destinationGeoType = geometryType(destinationGeometry)
	if mc.objectType(destinationShape) == 'transform':
		destinationShapes = glTools.utils.shape.getShapes(destinationGeometry,intermediates=False)
		destinationIntShapes = glTools.utils.shape.getShapes(destinationGeometry,intermediates=True)
		if not destinationIntShapes: destinationShape = destinationShapes[0]
		else:
			if destinationGeoType == 'mesh':
				if mc.listConnections(destinationShapes[0]+'.inMesh',s=True,d=False):
					for intShape in destinationIntShapes:
						if mc.listConnections(intShape+'.outMesh',s=False,d=True):
							destinationShape = intShape
							break
			elif (destinationGeoType == 'nurbsSurface') or (destinationGeoType == 'nurbsCurve'):
				if mc.listConnections(destinationShapes[0]+'.create',s=True,d=False):
					for intShape in destinationIntShapes:
						if mc.listConnections(intShape+'.local',s=False,d=True):
							destinationShape = intShape
							break
			else:
				raise Exception('Unknown geometry type "'+destinationGeoType+'" is not supported!!')
		
	# Check geometry types
	if destinationGeoType != sourceGeoType:
		raise Exception('Destination and Source geometry types do not match!!')
	
	# Replace geometry
	#-
	# Mesh
	if destinationGeoType == 'mesh':
		mc.connectAttr(sourceShape+'.outMesh',destinationShape+'.inMesh',force=True)
		mc.evalDeferred('mc.disconnectAttr("'+sourceShape+'.outMesh","'+destinationShape+'.inMesh")')
	# Nurbs Surface/Curve
	elif (destinationGeoType == 'nurbsSurface') or (destinationGeoType == 'nurbsCurve'):
		mc.connectAttr(sourceShape+'.local',destinationShape+'.create',force=True)
		mc.evalDeferred('mc.disconnectAttr("'+sourceShape+'.local","'+destinationShape+'.create")')
	# Unknown geometry type
	else:
		raise Exception('Unknown geometry type "'+destinationGeoType+'" is not supported!!')
