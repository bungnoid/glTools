import maya.cmds as mc

import glTools.utils.shape

class UserInputError(Exception): pass

def geometryType(geometry):
	'''
	Return the geometry type of the first shape under the specified geometry object
	@param geometry: The geometry object to query
	@type geometry: str
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise UserInputError('Geometry object "'+geometry+'" does not exist!!')
	
	# Get shapes
	shapeList = glTools.utils.shape.getShapes(geometry,intermediates=False)
	if not shapeList:
		shapeList = glTools.utils.shape.getShapes(geometry,intermediates=True)
	if not shapeList:
		raise UserInputError('Geometry object "'+geometry+'" has no shape children!!')
	
	# Get geometry type
	geometryType = mc.objectType(shapeList[0])
	
	# Return result
	return geometryType

def componentType(geometry):
	'''
	Return the geometry component type string, used for building component selection lists.
	@param geometry: The geometry object to query
	@type geometry: str
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise UserInputError('Geometry object "'+geometry+'" does not exist!!')
	
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
		raise UserInputError('Destination geometry "'+destinationGeometry+'" does not exist!!')
	if not mc.objExists(sourceGeometry):
		raise UserInputError('Source geometry "'+sourceGeometry+'" does not exist!!')
	
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
				raise UserInputError('Unknown geometry type "'+sourceGeoType+'" is not supported!!')
		
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
				raise UserInputError('Unknown geometry type "'+destinationGeoType+'" is not supported!!')
		
	# Check geometry types
	if destinationGeoType != sourceGeoType:
		raise UserInputError('Destination and Source geometry types do not match!!')
	
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
		raise UserInputError('Unknown geometry type "'+destinationGeoType+'" is not supported!!')
