import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

def findInputShape(shape):
	'''
	Return the input shape ('...ShapeOrig') for the specified shape node.
	This function assumes that the specified shape is affected by at least one valid deformer.
	@param shape: The shape node to find the corresponding input shape for.
	@type shape: str
	'''
	# Get MObject for shape
	shapeObj = getMObject(shape)
	
	# Get inMesh connection
	inMeshConn = mc.listConnections(shape+'.inMesh')
	if not inMeshConn:
		raise Exception('Mesh attribute "'+shape+'.inMesh" has no incoming connections!')
	
	# Find connected deformer
	deformerObj = getMObject(inMeshConn[0])
	if not deformerObj.hasFn(OpenMaya.MFn.kGeometryFilt):
		deformerHist = mc.ls(mc.listHistory(shape),type='geometryFilter')
		if not deformerHist:
			raise Exception('Shape node "'+shape+'" is not affected by any valid deformers!')
		else:
			deformerObj = getMObject(deformerHist[0])
	
	# Get deformer function set
	deformerFn = OpenMayaAnim.MFnGeometryFilter(deformerObj)
	
	# Get input shape for deformer
	geomIndex = deformerFn.indexForOutputShape(shapeObj)
	inputShapeObj = deformerFn.inputShapeAtIndex(geomIndex)
	
	# Return result
	return OpenMaya.MFnDependencyNode(inputShapeObj).name()

def getMObject(object):
	'''
	Return an MObject for the input scene object
	@param object: Object to get MObject for
	@type object: str
	'''
	# Check input object
	if not mc.objExists(object):
		raise UserInputError('Object "'+object+'" does not exist!!')
	
	# Get selection list
	selectionList = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(object,selectionList)
	mObject = OpenMaya.MObject()
	selectionList.getDependNode(0,mObject)
	
	# Return result
	return mObject
