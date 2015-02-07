import maya.cmds as mc

import glTools.utils.base

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

def isShape(obj):
	'''
	Check if the specified object is a valid shape node
	@param obj: Object to check as a shape node
	@type obj: str
	'''
	# Check object exists
	if not mc.objExists(obj): return False
	
	# Check Shape
	mObject = glTools.utils.base.getMObject(obj)
	if not mObject.hasFn(OpenMaya.MFn.kShape): return False
	
	# Return Result
	return True

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
	if not mc.objExists(geo):
		raise Exception('Object "'+geo+'" does not exist!!')
	if isShape(geo):
		geo = mc.listRelatives(geo,p=True,pa=True)[0]
	
	# Get Non Intermediate Shapes
	shapes = mc.listRelatives(geo,s=True,ni=True,pa=True)
	
	# Get All Shapes
	allShapes = mc.listRelatives(geo,s=True,pa=True)
	
	# Get Intermediate Shapes
	if not allShapes: return []
	if not shapes: return allShapes
	intShapes = list(set(allShapes) - set(shapes))
	
	# Return Result
	return intShapes

def getShapes(geo,nonIntermediates=True,intermediates=True):
	'''
	Return a list of shapes under a transform parent
	@param geo: Transform to list shapes for
	@type geo: str
	@param nonIntermediates: List non intermediate shapes
	@type nonIntermediates: bool
	@param intermediates: List intermediate shapes
	@type intermediates: bool
	'''
	# Checks
	if not mc.objExists(geo):
		raise Exception('Object "'+geo+'" does not exist!!')
	if isShape(geo):
		geo = mc.listRelatives(geo,p=True,pa=True)[0]
	
	# Get Shapes
	shapes = []
	if nonIntermediates:
		nonIntShapes = mc.listRelatives(geo,s=True,ni=True,pa=True)
		if nonIntShapes: shapes.extend(nonIntShapes)
	if intermediates:
		shapes.extend(listIntermediates(geo))
	
	# Return Result
	return shapes
	
def rename(geo):
	'''
	Rename shape nodes based on the parent transform name
	@param geo: Transform to rename shapes for
	@type geo: str
	'''
	# Get Shapes
	shapes = getShapes(geo)
	
	# Check Shapes
	if not shapes: return []
	
	# Rename Shapes
	for i in range(len(shapes)):
		
		# Get Shape Type
		shapeType = mc.objectType(shapes[i])
		
		# Temporarily rename shapes, so hash index (#) is accurate
		shapes[i] = mc.rename(shapes[i],geo+'ShapeTMP')
		
		# Rename Shape
		if shapeType == 'nurbsCurve':
			shapes[i] = mc.rename(shapes[i],geo+'CrvShape#')
		elif shapeType == 'nurbsSurface':
			shapes[i] = mc.rename(shapes[i],geo+'SrfShape#')
		elif shapeType == 'mesh':
			shapes[i] = mc.rename(shapes[i],geo+'MeshShape#')
		else:
			shapes[i] = mc.rename(shapes[i],geo+'Shape#')
	
	# Return Result
	return shapes

def shapeInputAttr(shape):
	'''
	Return the shape input attribute.
	@param shape: The shape node to find the shape input attribute for.
	@type shape: str
	'''
	# Check Shape
	if not isShape(shape):
		raise Exception('Object "'+shape+'" is not a valid shape node!')
	
	# Determine Shape Input Plug
	shapeInputAttr = ''
	shapeInputType = mc.objectType(shape)
	shapeInputDict = {	'mesh':'inMesh',
						'nurbsCurve':'create',
						'nurbsSurface':'create'	}
	if shapeInputDict.has_key(shapeInputType):
		shapeInputAttr = shapeInputDict[shapeInputType]
	else:
		raise Exception('Unsupported shape type! ('+shapeInputType+')')
	
	# Return Result
	return shapeInputAttr

def shapeOutputAttr(shape,worldSpace=False):
	'''
	Return the shape output attribute.
	@param shape: The shape node to find the shape input attribute for.
	@type shape: str
	@param worldSpace: Return the worldSpace output attribute if available.
	@type worldSpace: bool
	'''
	# Check Shape
	if not isShape(shape):
		raise Exception('Object "'+shape+'" is not a valid shape node!')
	
	# Determine Shape Input Plug
	shapeOutputAttr = ''
	shapeOutputType = mc.objectType(shape)
	shapeOutputDict = {	'mesh':['outMesh','worldMesh'],
						'nurbsCurve':['local','worldSpace'],
						'nurbsSurface':['local','worldSpace']	}
	
	if shapeOutputDict.has_key(shapeOutputType):
		shapeOutputAttr = shapeOutputDict[shapeOutputType][int(worldSpace)]
	else:
		raise Exception('Unsupported shape type! ('+shapeOutputType+')')
	
	# Return Result
	return shapeOutputAttr

def shapeInputSrc(shape):
	'''
	Return the shape input source plug. If not input exists, return an empty string
	@param shape: The shape node to find the shape input source for.
	@type shape: str
	'''
	# Check Shape
	if not isShape(shape):
		raise Exception('Object "'+shape+'" is not a valid shape node!')
	
	# Determine Shape Input Plug
	shapeInAttr = shapeInputAttr(shape)
	
	# Determine Shape Input Source Plug
	shapeInputPlug = ''
	shapeInputSrc = mc.listConnections(shape+'.'+shapeInAttr,s=True,d=False,p=True)
	if shapeInputSrc: shapeInputPlug = shapeInputSrc[0]
	
	# Return Result
	return shapeInputPlug

def findInputShape(shape,recursive=False,printExceptions=False):
	'''
	Return the input shape for the specified shape node or transform.
	@param shape: The shape node to find the corresponding input shape for.
	@type shape: str
	'''
	# Initialize Default Value
	inputShape = None
	
	# Try inputShape methods
	if not inputShape:
		try: inputShape = glTools.utils.shape.findInputShape1(shape)
		except Exception, e:
			if printExceptions:
				print('Caught Exception: '+str(e))
	if not inputShape:
		try: inputShape = glTools.utils.shape.findInputShape2(shape)
		except Exception, e:
			if printExceptions:
				print('Caught Exception: '+str(e))
	
	# Check Result
	if not inputShape:
		raise Exception('Unable to determine input shape for "'+shape+'"!')
	
	# Recursive Check
	if recursive:
		while(inputShape!=findInputShape(inputShape)):
			inputShape = findInputShape(inputShape)
	
	# Return Result
	return inputShape

def findInputShape1(shape):
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
	return OpenMaya.MFnDagNode(inputShapeObj).partialPathName()

def findInputShape2(shape):
	'''
	Determine the input shape for the speficified geomety based on construction history
	@param shape: The shape node to find the corresponding input shape for.
	@type shape: str
	'''
	# Initialize Transform
	transform = mc.listRelatives(shape,p=True,pa=True) or []
	
	# Check shape
	if glTools.utils.base.isType(shape,'transform'):
		transform = [shape]
		shapes = mc.listRelatives(shape,s=True,ni=True,pa=True)
		if not shapes: raise Exception('Unable to determine shape node from transform "'+shape+'"!')
		shape = shapes[0]
	
	# Get All Shapes
	allShapes = mc.listRelatives(transform[0],s=True,pa=True)
	
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

def parent(shape,parent,deleteShapeTransform=False,force=False):
	'''
	Parent shape nodes to a destination parent
	@param shape: Shape or transform to parent
	@type shape: str
	@param parent: Destination parent transform
	@type parent: str
	@param deleteShapeTransform: Delete shape transform parent, only if transform has no descendants.
	@type deleteShapeTransform: bool
	'''
	# Checks
	if not mc.objExists(shape):
		raise Exception('Object "'+shape+'" does not exist!!')
	if not mc.objExists(parent):
		raise Exception('Object "'+parent+'" does not exist!!')
	
	# Get shapes
	shapes = []
	if mc.ls(shape,type='transform'):
		transform = shape
		shapes = mc.listRelatives(shape,s=True,pa=True)
	else:
		transform = mc.listRelatives(shape,p=True,pa=True)[0]
		shapes = [shape]
	
	# Match parent transform
	mc.parent(transform,parent)
	mc.makeIdentity(transform,apply=True,t=True,r=True,s=True)
	mc.parent(transform,w=True)
	
	# Parent shapes
	for i in range(len(shapes)):
		
		# Parent Shape to Target Transform
		shapeList = mc.parent(shapes[i],parent,s=True,r=True)
		shapes[i] = shapeList[0]
		
		# Get Shape Type
		shapeType = mc.objectType(shapes[i])
		
		# Temporarily rename shapes, so hash index (#) is accurate
		shapes[i] = mc.rename(shapes[i],parent+'ShapeTMP')
		
		# Rename Shapes
		if shapeType == 'nurbsCurve':
			shapes[i] = mc.rename(shapes[i],parent+'CrvShape#')
		elif shapeType == 'nurbsSurface':
			shapes[i] = mc.rename(shapes[i],parent+'SrfShape#')
		elif shapeType == 'mesh':
			shapes[i] = mc.rename(shapes[i],parent+'MeshShape#')
		else:
			shapes[i] = mc.rename(shapes[i],parent+'Shape#')
	
	# Delete Old Shape Transform
	if deleteShapeTransform:
		
		# Check remaining descendants
		if mc.listRelatives(transform,ad=True):
			if not force:
				print('Unable to delete transform "'+transform+'"! Object has remaining descendants. Use force=True to force deletion.')
				deleteShapeTransform = False
			else:
				print('Transform "'+transform+'" has remaining descendants, deleting anyway! (force=True)')
		
		# Check outgoing connections
		if mc.listConnections(transform,s=False,d=True):
			if not force:
				print('Unable to delete transform "'+transform+'"! Object has outgoing connections. Use force=True to force deletion.')
				deleteShapeTransform = False
			else:
				print('Transform "'+transform+'" has outgoing conections, deleting anyway! (force=True)')
		
		# Delete Transform
		if deleteShapeTransform: mc.delete(transform)
	
	# Return Result
	return shapes

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
		shapes = mc.listRelatives(shape,s=True,pa=True)
	else:
		transform = mc.listRelatives(shape,p=True,pa=True)[0]
		shapes = [shape]
	
	# Create shape holder
	shapeHolder = transform+'Shapes'
	if not mc.objExists(shapeHolder): shapeHolder = mc.createNode('transform',n=shapeHolder)
	targetXform = mc.xform(transform,q=True,ws=True,m=True)
	mc.xform(shapeHolder,ws=True,m=targetXform)
	
	# Unparent shapes
	for shape in shapes:
		mc.parent(shape,shapeHolder,s=True,r=True)
	
	# Return Result
	return shapeHolder

def copyToTransform(shape,transform,relative=True,move=False,overrideColour=None):
	'''
	Copy shape to a specified target transform.
	@param shape: Shape or copy to target transform
	@type shape: str
	@param transform: Target transform to copy shape to
	@type transform: str
	@param relative: Copy the shape relative to the original parent transform
	@type relative: str
	@param move: Move shape to target transform instead of copying to the transform.
	@type move: str
	@param overrideColour: Override display colour to assign to the copied shape.
	@type overrideColour: str
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
	# ==========
	# - Checks -
	# ==========
	
	# Check Shape
	if not mc.objExists(shape):
		raise Exception('Object "'+shape+'" does not exist!!')
	
	# Check Geometry Type
	geoType = mc.objectType(shape)
	if geoType == 'transform':
		shapes = getShapes(shape,intermediates=False)
		if not shapes: raise Exception('Object "'+shape+'" has no valid shapes!!')
		shape = shapes[0]
		geoType = mc.objectType(shape)
	
	# Check In/Out Attributes
	geoDict = {'mesh':('outMesh','inMesh'),'nurbsSurface':('local','create'),'nurbsCurve':('local','create')}
	if not geoDict.has_key(geoType): raise Exception('Invalid shape type ('+geoType+') for "'+shape+'"!!')
	
	# =============================
	# - Create Intermediate Shape -
	# =============================
	
	# Get Shape Node from Transform
	transform = str(mc.listRelatives(shape,p=True)[0])
	
	# Rename Current Shape as Intermediate
	shapeOrig = mc.rename(shape,shape+'Orig')
	
	# Create New Shape
	shape = mc.createNode(geoType,n=shape,p=transform)
	mc.connectAttr(shapeOrig+'.'+geoDict[geoType][0],shape+'.'+geoDict[geoType][1],f=True)
	mc.setAttr(shapeOrig+'.intermediateObject',1)
	mc.reorder(shape,f=True)
	
	# Connect Shader
	shader = mc.listConnections(shapeOrig,type='shadingEngine')
	if shader:
		mc.sets(shapeOrig,rm=shader[0])
		mc.sets(shape,fe=shader[0])
	
	# Update Outgoing Connections
	outConn = mc.listConnections(shapeOrig,s=False,d=True,p=True,c=True)
	for i in range(0,len(outConn),2):
		# Check Connection Destination
		dst = outConn[i+1]
		if shape in dst: continue
		# Check Connection Source
		src = outConn[i].replace(shapeOrig,shape)
		if mc.objExists(src):
			print('New source connection: '+src)
		else:
			print('Source connection "'+src+'" does not exist! Skipping...')
			continue
		# Update Connection
		mc.connectAttr(src,dst,f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return shapeOrig
	
