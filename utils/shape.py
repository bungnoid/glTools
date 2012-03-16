import maya.cmds as mc

import glTools.utils.base

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

def hasIntermediate(geo):
	'''
	Check if the specified geometry has any intermediate shapes
	@param geo: Transform to check intermediate shapes for
	@type geo: str
	'''
	return bool(len(listIntermediates(geo)))

def listIntermediates(geo):
	'''
	Return a list of intermediate shapes under a transform parent
	@param geo: Transform to list intermediate shapes for
	@type geo: str
	'''
	# Checks
	if not mc.objExists(geo): raise Exception('Object "'+geo+'" does not exist!!')
	# Get non intermediate shapes
	shapes = mc.listRelatives(geo,s=True,ni=True)
	# Get all shapes
	allShapes = mc.listRelatives(geo,s=True)
	# Get difference
	intShapes = list(set(allShapes) - set(shapes))
	# Return result
	return intShapes

def getShapes(geo,nonIntermediates=True,intermediates=True):
	'''
	Return a list of shapes under a transform parent
	@param geo: Transform to list shapes for
	@type geo: str
	'''
	# Checks
	if not mc.objExists(geo):
		raise Exception('Object "'+geo+'" does not exist!!')
	# Get Shapes
	shapes = []
	if nonIntermediates:
		shapes.extend(mc.listRelatives(geo,s=True,ni=True))
	if intermediates:
		shapes.extend(listIntermediates(geo))
	# Return result
	return shapes

def findInputShape(shape):
	'''
	Return the input shape ('...ShapeOrig') for the specified shape node based on deformer data.
	This function assumes that the specified shape is affected by at least one valid deformer.
	@param shape: The shape node to find the corresponding input shape for.
	@type shape: str
	'''
	# Get MObject for shape
	shapeObj = glTools.utils.base.getMObject(shape)
	
	# Get inMesh connection
	inConn = mc.listConnections(shape,s=True,d=False)
	if not inConn: return shape
	
	# Find connected deformer
	deformerHist = mc.ls(mc.listHistory(shape),type='geometryFilter')
	if not deformerHist: raise Exception('Shape node "'+shape+'" is not affected by any valid deformers! Unable to determine input shape')
	deformerObj = glTools.utils.base.getMObject(deformerHist[0])
	
	# Get deformer function set
	deformerFn = OpenMayaAnim.MFnGeometryFilter(deformerObj)
	
	# Get input shape for deformer
	geomIndex = deformerFn.indexForOutputShape(shapeObj)
	inputShapeObj = deformerFn.inputShapeAtIndex(geomIndex)
	
	# Return result
	return OpenMaya.MFnDependencyNode(inputShapeObj).name()

def findInputShape2(shape):
	'''
	Determine the input shape for the speficified geomety based on construction history
	@param shape: The shape node to find the corresponding input shape for.
	@type shape: str
	'''
	# Check shape
	allShapes = mc.listRelatives(shape,s=True)
	if glTools.utils.base.isType(shape,'transform'):
		shapes = mc.listRelatives(shape,s=True,ni=True)
		if not shapes: raise Exception('Unable to determine shape node from transform "'+shape+'"!')
		shape = shapes[0]
	
	# Get shape type
	shapeType = mc.objectType(shape)
	
	# Get shape history
	shapeHist = mc.ls(mc.listHistory(shape),type=shapeType)
	if shapeHist.count(shape): shapeHist.remove(shape)
	if not shapeHist: raise Exception('Unable to determine history nodes for shape "'+shape+'"!')
	
	# Check shape history
	if len(shapeHist) == 1:
		inputShape = shapeHist[0]
	else:
		shapeInput = list(set(shapeHist).intersection(set(allShapes)))
		if shapeInput: inputShape = shapeInput[0]
		else: inputShape = shapeHist[0]
	
	# Return result
	return inputShape

def parent(shape,parent):
	'''
	Parent shape nodes to a destination parent
	@param shape: Shape or transform to parent
	@type shape: str
	@param parent: Shape or transform to parent
	@type parent: Destination parent transform
	'''
	# Checks
	if not mc.objExists(shape):
		raise Exception('Object "'+shape+'" does not exist!!')
	if not mc.objExists(parent):
		raise Exception('Object "'+parent+'" does not exist!!')
	
	# Get shapes
	if mc.ls(shape,type='transform'):
		transform = shape
		shapes = mc.listRelatives(shape,s=True)
	else:
		transform = mc.listRelatives(shape,p=True)[0]
		shapes = [shape]
	
	# Match parent transform
	mc.parent(transform,parent)
	mc.makeIdentity(transform,apply=True,t=True,r=True,s=True)
	mc.parent(transform,w=True)
	
	# Parent shapes
	for shape in shapes:
		mc.parent(shape,parent,s=True,r=True)

def unparent(shape):
	'''
	Unparent shape nodes from a source parent
	@param shape: Shape or transform to unparent shapes from
	@type shape: str
	'''
	# Checks
	if not mc.objExists(shape):
		raise Exception('Object "'+shape+'" does not exist!!')
	
	# Get shapes
	if mc.ls(shape,type='transform'):
		transform = shape
		shapes = mc.listRelatives(shape,s=True)
	else:
		transform = mc.listRelatives(shape,p=True)[0]
		shapes = [shape]
	
	# Create shape holder
	shapeHolder = mc.createNode('transform',n=transform+'Shapes')
	targetXform = mc.xform(transform,q=True,ws=True,m=True)
	mc.xform(shapeHolder,ws=True,m=targetXform)
	
	# Unparent shapes
	for shape in shapes:
		mc.parent(shape,shapeHolder,s=True,r=True)

def copyToTransform(shape,transform,relative=True,move=False,overrideColour=None):
	'''
	'''
	# Check shape
	if not mc.objExists(shape):
		raise Exception('Shape "'+shape+'" does not exist!')
	# Check transform
	if not mc.objExists(transform):
		raise Exception('Transform "'+transform+'" does not exist!')
	
	# Duplicate shape
	if not move:
		shapeParent = mc.listRelatives(shape,p=True,pa=True)[0]
		tmpXform = mc.duplicate(shapeParent,rr=True)[0]
		shape = mc.listRelatives(tmpXform,s=True,pa=True)[0]
	
	# Parent shape
	mc.parent(shape,transform,s=True,r=relative,a=not(relative))
	shape = mc.rename(shape,transform+'Shape#')
	
	# Delete temp transform
	if not move: mc.delete(tmpXform)
	
	# Colour Override
	if overrideColour:
		mc.setAttr(shape+'.overrideEnabled',1)
		mc.setAttr(shape+'.overrideColor',overrideColour)
	
	# Return result
	return shape

def createIntermediate(shape):
	'''
	Create and connect an intermediate shape for the specified geoemtry shape
	@param shape: Shape or create intermediate shape for
	@type shape: str
	'''
	# Check Shape
	if not mc.objExists(shape): raise Exception('Object "'+shape+'" does not exist!!')
	
	# Check Geometry Type
	geoType = mc.objectType(shape)
	if geoType == 'transform':
		shapes = getShapes(shape,intermediates=False)
		if not shapes: raise Exception('Object "'+shape+'" has no valid shapes!!')
		shape = shapes[0]
		geoType = mc.objectType(shape)
		
	geoDict = {'mesh':('outMesh','inMesh'),'nurbsSurface':('local','create'),'nurbsCurve':('local','create')}
	if not geoDict.has_key(geoType): raise Exception('Invalid shape type ('+geoType+') for "'+shape+'"!!')
	
	# Get transform
	transform = str(mc.listRelatives(shape,p=True)[0])
	
	# Rename current shape as intermediate
	shapeOrig = mc.rename(shape,shape+'Orig')
	'''
	ind = 1
	shapeOrig = shape.replace('Shape','ShapeOrig')
	while(mc.objExists(shapeOrig)):
		shapeOrig =  shape.replace('Shape','ShapeOrig'+ind)
		ind += 1
	shapeOrig = mc.rename(shape,shape.replace('Shape','ShapeOrig'))
	'''
	# Create new shape
	shape = mc.createNode(geoType,n=shape,p=transform)
	mc.reorder(shape,f=True)
	
	# Connect shapes
	mc.connectAttr(shapeOrig+'.'+geoDict[geoType][0],shape+'.'+geoDict[geoType][1],f=True)
	
	# Set shapeOrig as intermediate
	mc.setAttr(shapeOrig+'.intermediateObject',1)
	
	# Connect to existing shader
	shader = mc.listConnections(shapeOrig,type='shadingEngine')
	if shader:
		mc.sets(shapeOrig,rm=shader[0])
		mc.sets(shape,fe=shader[0])
	
	# Return result
	return shapeOrig
	
