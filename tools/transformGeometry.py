import maya.cmds as mc

import glTools.utils.shape
import glTools.utils.stringUtils

def create(geo,transform,prefix=None):
	'''
	@param geo: Geometry to transform.
	@type geo: str
	@param transform: Transform node that drives geometry transformation.
	@type transform: str
	@param prefix: Naming prefix. If None, prefix will be derived from geo name.
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(geo):
		raise Exception('Geometry "'+geo+'" does not exist! Unable to transform geometry...')
	if not mc.objExists(transform):
		raise Exception('Transform "'+transform+'" does not exist! Unable to transform geometry...')
	if not prefix:
		prefix = glTools.utils.stringUtils.stripSuffix(geo)
	
	# ======================
	# - Transform Geometry -
	# ======================
	
	# Find Geometry Shapes to Transform
	geoShapes = mc.ls(mc.listRelatives(geo,s=True,ni=True) or [],type=['mesh','nurbsCurve','nurbsSurface']) or []
	if not geoShapes:
		raise Exception('Object "'+geo+'" has no geometry shape! Unable to transform geometry...')
	
	# Transform Geometry Shapes
	transformGeoList = []
	for i in range(len(geoShapes)):
		
		# Create Transform Geometry Node
		ind = glTools.utils.stringUtils.alphaIndex(i)
		transformGeo = mc.createNode('transformGeometry',n=prefix+'_'+ind+'_transformGeometry')
		mc.connectAttr(transform+'.worldMatrix[0]',transformGeo+'.transform',f=True)
		
		# Check Shape Input
		shapeType = mc.objectType(geoShapes[i])
		shapeInputSrc = glTools.utils.shape.shapeInputSrc(geoShapes[i])
		shapeInputAttr = glTools.utils.shape.shapeInputAttr(geoShapes[i])
		shapeOutputAttr = glTools.utils.shape.shapeOutputAttr(geoShapes[i])
		
		# Connect Transform Geometry Node
		if shapeInputSrc:
			
			# -- Existing Input Source
			mc.connectAttr(shapeInputSrc,transformGeo+'.inputGeometry',f=True)
			mc.connectAttr(transformGeo+'.outputGeometry',geoShapes[i]+'.'+shapeInputAttr,f=True)
			
		else:
			
			# -- No Input Source
			geoShapeOrig = mc.rename(geoShapes[i],geoShapes[i]+'Orig')
			geoShape = mc.createNode(shapeType,n=geoShapes[i],p=geo)
			shapeOutputAttr = glTools.utils.shape.shapeOutputAttr(geoShapes[i])
			mc.connectAttr(geoShapeOrig+'.'+shapeOutputAttr,transformGeo+'.inputGeometry',f=True)
			mc.connectAttr(transformGeo+'.outputGeometry',geoShape+'.'+shapeInputAttr,f=True)
			mc.setAttr(geoShapeOrig+'.intermediateObject',True)
			
			# Apply Overrides
			overrideAttrs = [	'template',
								'overrideEnabled',
								'overrideDisplayType',
								'overrideLevelOfDetail',
								'overrideVisibility',
								'overrideColor'	]
			for overrideAttr in overrideAttrs:
				mc.setAttr(geoShape+'.'+overrideAttr,mc.getAttr(geoShapeOrig+'.'+overrideAttr))
			
		
		# Append Output List
		transformGeoList.append(transformGeo)
		
	# =================
	# - Return Result -
	# =================
	
	return transformGeoList
