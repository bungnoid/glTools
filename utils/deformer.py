import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.utils.attribute
import glTools.utils.base
import glTools.utils.geometry
import glTools.utils.selection

import re

# Create exception class
class UserInputError(Exception): pass

def isDeformer(deformer):
	'''
	Test if node is a valid deformer
	@param deformer: Name of deformer to query
	@type deformer: str
	'''
	# Check deformer exists
	if not mc.objExists(deformer): return False
	# Check deformer type
	nodeType = mc.nodeType(deformer,i=1)
	if not nodeType.count('geometryFilter'): return False
	# Return result
	return True

def getDeformerFn(deformer):
	'''
	Initialize and return an MFnWeightGeometryFilter function set attached to the specified deformer
	@param deformer: Name of deformer to create function set for
	@type deformer: str
	'''
	# Checks
	if not mc.objExists(deformer):
		raise UserInputError('Deformer '+deformer+' does not exist!')
	
	# Get MFnWeightGeometryFilter
	deformerObj = glTools.utils.base.getMObject(deformer)
	deformerFn = OpenMayaAnim.MFnWeightGeometryFilter(deformerObj)
	
	# Return result
	return deformerFn

def getDeformerSet(deformer):
	'''
	Return the deformer set name associated with the specified deformer
	@param deformer: Name of deformer to return the deformer set for
	@type deformer: str
	'''
	# Checks
	if not mc.objExists(deformer):
		raise UserInputError('Deformer '+deformer+' does not exist!')
	
	# Get deformer set
	deformerSet = mc.listConnections(deformer,s=False,d=True,type='objectSet',exactType=True)
	if not deformerSet: raise UserInputError('Unable to determine deformer set!')
	
	# Return result
	return deformerSet[0]

def getDeformerSetFn(deformer):
	'''
	Initialize and return an MFnSet function set attached to the deformer set of the specified deformer
	@param deformer: Name of deformer attached to the deformer set to create function set for
	@type deformer: str
	'''
	# Checks
	if not mc.objExists(deformer):
		raise UserInputError('Deformer '+deformer+' does not exist!')
	
	# Get deformer set
	deformerSet = getDeformerSet(deformer)
	
	# Get MFnWeightGeometryFilter
	deformerSetObj = glTools.utils.base.getMObject(deformerSet)
	deformerSetFn = OpenMaya.MFnSet(deformerSetObj)
	
	# Return result
	return deformerSetFn


def getDeformerSetMembers(deformer,geometry=''):
	'''
	Return the deformer set members of the specified deformer.
	Optionally, you can specify a shape name to query deformer membership on.
	Otherwise, membership for the first affected geometry will be returned.
	Results are returned as a list containing an MDagPath to the affected shape and an MObject for the affected components.
	@param deformer: Deformer to query set membership for
	@type deformer: str
	@param geometry: Geometry to query deformer set membership for. Optional.
	@type geometry: str
	'''
	# Get MFnSet
	deformerSetFn = getDeformerSetFn(deformer)
	
	# Get deformer set members
	deformerSetSel = OpenMaya.MSelectionList()
	deformerSetFn.getMembers(deformerSetSel,1)
	deformerSetPath = OpenMaya.MDagPath()
	deformerSetComp = OpenMaya.MObject()
	
	# Get geometry index
	if geometry:
		# Initialize setSelIndex boolean
		setSelIndexFound = False
		
		# Check geometry
		geo = geometry
		if mc.objectType(geometry) == 'transform':
			try: geometry = mc.listRelatives(geometry,s=True,ni=True,pa=True)[0]
			except:	raise UserInputError('Object "'+geo+'" is not a valid geometry!')
		geomPath = glTools.utils.base.getMDagPath(geometry)
		
		# Check geometry affected by deformer
		if not (geometry in getAffectedGeometry(deformer,returnShapes=True).keys()):
			raise UserInputError('Geometry "'+geometry+'" is not a affected by deformer "'+deformer+'"!')
		
		# Cycle through selection set members
		for i in range(deformerSetSel.length()):
			# Get deformer set members
			deformerSetSel.getDagPath(i,deformerSetPath,deformerSetComp)
			if geomPath == deformerSetPath:
				setSelIndexFound = True
				break
		
		# Check setSelIndex found
		if not setSelIndexFound:
			raise UserInputError('No valid geometryIndex found for "'+geometry+'" in deformer set for "'+deformer+'"!')
	else:
		# Get deformer set members
		deformerSetSel.getDagPath(0,deformerSetPath,deformerSetComp)
	
	# Return result
	return [deformerSetPath,deformerSetComp]

"""
def getDeformerSetMembers(deformer,geometry=''):
	'''
	Return the deformer set members of the specified deformer.
	Optionally, you can specify a shape name to query deformer membership on.
	Otherwise, membership for the first affected geometry will be returned.
	Results are returned as a list containing an MDagPath to the affected shape and an MObject for the affected components.
	@param deformer: Deformer to query set membership for
	@type deformer: str
	@param geometry: Geometry to query deformer set membership for. Optional.
	@type geometry: str
	'''
	# Get deformer function sets
	deformerSetFn = getDeformerSetFn(deformer)
	
	# Get deformer set members
	deformerSetSel = OpenMaya.MSelectionList()
	deformerSetFn.getMembers(deformerSetSel,1)
	deformerSetPath = OpenMaya.MDagPath()
	deformerSetComp = OpenMaya.MObject()
	
	# Get geometry index
	if geometry: geomIndex = getGeomIndex(geometry,deformer)
	else: geomIndex = 0
	
	# Get deformer set members
	deformerSetSel.getDagPath(geomIndex,deformerSetPath,deformerSetComp)
	
	# Return result
	return [deformerSetPath,deformerSetComp]
"""

def getDeformerSetMemberIndices(deformer,geometry=''):
	'''
	Return a list of deformer set member vertex indices
	@param deformer: Deformer to set member indices for
	@type deformer: str
	@param geometry: Geometry to query deformer set membership for.
	@type geometry: str
	'''
	# Check geometry
	geo = geometry
	if mc.objectType(geometry) == 'transform':
		try: geometry = mc.listRelatives(geometry,s=True,ni=True,pa=True)[0]
		except:	raise UserInputError('Object "'+geo+'" is not a valid geometry!')
	
	# Get deformer set members
	deformerSetMem = getDeformerSetMembers(deformer,geometry)
	
	# Get set member indices
	memberIndices = OpenMaya.MIntArray()
	singleIndexCompFn = OpenMaya.MFnSingleIndexedComponent(deformerSetMem[1])
	singleIndexCompFn.getElements(memberIndices)
	
	# Return result
	return list(memberIndices)

def getAffectedGeometry(deformer,returnShapes=False,fullPathNames=False):
	'''
	Return a dictionary containing information about geometry affected by
	a specified deformer. Dictionary keys correspond to affected geometry names,
	values indicate geometry index to deformer.
	@param deformer: Name of deformer to query
	@type deformer: str
	@param returnShapes: Return shape instead of parent transform name
	@type returnShapes: bool
	@param fullPathNames: Return full path names of affected objects
	@type fullPathNames: bool
	'''
	# Verify input
	if not isDeformer(deformer):
		raise UserInputError('Object "'+deformer+'" is not a valid deformer!')
	
	# Clear return array (dict)
	affectedObjects = {}
	
	# Get MFnGeometryFilter
	deformerObj = glTools.utils.base.getMObject(deformer)
	geoFilterFn = OpenMayaAnim.MFnGeometryFilter(deformerObj)
	# Get output geometry
	outputObjectArray = OpenMaya.MObjectArray()
	geoFilterFn.getOutputGeometry(outputObjectArray)
	# Iterate through affected geometry
	for i in range(outputObjectArray.length()):
		outputIndex = geoFilterFn.indexForOutputShape(outputObjectArray[i])
		outputNode = OpenMaya.MFnDagNode(outputObjectArray[i])
		# Check return shapes
		if not returnShapes: outputNode = OpenMaya.MFnDagNode(outputNode.parent(0))
		# Check full path
		if fullPathNames: affectedObjects[outputNode.fullPathName()] = outputIndex
		else: affectedObjects[outputNode.partialPathName()] = outputIndex
	
	# Return result
	return affectedObjects

def getGeomIndex(geometry,deformer):
	'''
	Returns the geometry index of a shape to a specified deformer.
	@param geometry: Name of shape or parent transform to query
	@type geometry: str
	@param deformer: Name of deformer to query
	@type deformer: str
	'''
	# Verify input
	if not isDeformer(deformer):
		raise UserInputError('Object "'+deformer+'" is not a valid deformer!')
	
	# Check geometry
	geo = geometry
	if mc.objectType(geometry) == 'transform':
		try: geometry = mc.listRelatives(geometry,s=True,ni=True,pa=True)[0]
		except:	raise UserInputError('Object "'+geo+'" is not a valid geometry!')
	geomObj = glTools.utils.base.getMObject(geometry)
	
	# Get geometry index
	deformerObj = glTools.utils.base.getMObject(deformer)
	deformerFn = OpenMayaAnim.MFnGeometryFilter(deformerObj)
	try: geomIndex = deformerFn.indexForOutputShape(geomObj)
	except: raise UserInputError('Object "'+geometry+'" is not affected by deformer "'+deformer+'"!')
	
	# Retrun result
	return geomIndex

def getDeformerList(geo='',regexFilter='',type='geometryFilter'):
	'''
	Return a list of deformer that match the input criteria.
	You can list deformers connected to a geo specified geometry, by type and filter the result with a regex.
	@param geo: Geometry name as string. Optional arg that will list deformers connected to geo.
	@type geo: str
	@param regexFilter: Regular Expression as string. Optional arg that will filter results
	@type regexFilter: str
	@param type: Deformer Type as string. Optional arg, only return deformers of specified type.
	@type type: str
	'''
	deformers = []
	# Check Geo
	if geo:
		inputShapes = []
		# Get shapes
		shapes = mc.listRelatives(geo, shapes=True, ni=True)
		# Get input shapes
		for shape in shapes: inputShapes.append( findInputShape(shape) )
		# Get deformers by listing all future on input shapes
		deformers = mc.ls(mc.listHistory(inputShapes, future=True, allFuture=True), type=type)
	else:
		deformers = mc.ls(type=type)
	
	# Remove duplicate entries
	deformers = list(set(deformers))
	
	# Filter result if regexFilter
	if regexFilter:
		reFilter = re.compile(regexFilter)
		return filter(reFilter.search, deformers)	
		
	# Return result
	return deformers

def findInputShape(shape):
	'''
	Return the input shape ('...ShapeOrig') for the specified shape node.
	This function assumes that the specified shape is affected by at least one valid deformer.
	@param shape: The shape node to find the corresponding input shape for.
	@type shape: str
	'''
	# Checks
	if not mc.objExists(shape):
		raise Exception('Shape node "'+shape+'" does not exist!')
	
	# Get inMesh connection
	inMeshConn = mc.listConnections(shape+'.inMesh',source=True,destination=False,shapes=True)
	if not inMeshConn:
		return shape
	
	# Check direct mesh (outMesh -> inMesh) connection
	if str(mc.objectType(inMeshConn[0])) == 'mesh':
		return inMeshConn[0]
		
	# Find connected deformer
	deformerObj = glTools.utils.base.getMObject(inMeshConn[0])
	if not deformerObj.hasFn(OpenMaya.MFn.kGeometryFilt):
		deformerHist = mc.ls(mc.listHistory(shape),type='geometryFilter')
		if not deformerHist:
			print('findInputShape.py: Shape node "'+shape+'" has incoming inMesh connections but is not affected by any valid deformers! Returning "'+shape+'"!')
			return shape
			#raise Exception('Shape node "'+shape+'" is not affected by any valid deformers!')
		else:
			deformerObj = glTools.utils.base.getMObject(deformerHist[0])
	
	# Get deformer function set
	deformerFn = OpenMayaAnim.MFnGeometryFilter(deformerObj)
	
	# Get input shape for deformer
	shapeObj = glTools.utils.base.getMObject(shape)
	geomIndex = deformerFn.indexForOutputShape(shapeObj)
	inputShapeObj = deformerFn.inputShapeAtIndex(geomIndex)
	
	# Return result
	return OpenMaya.MFnDependencyNode(inputShapeObj).name()

def renameDeformerSet(deformer,deformerSetName=''):
	'''
	Rename the deformer set connected to the specified deformer
	@param deformer: Name of the deformer whose deformer set you want to rename
	@type deformer: str
	@param deformerSetName: New name for the deformer set. If left as default, new name will be (deformer+"Set")
	@type deformerSetName: str
	'''
	# Verify input
	if not isDeformer(deformer):
		raise UserInputError('Object "'+deformer+'" is not a valid deformer!')
	
	# Check deformer set name
	if not deformerSetName: deformerSetName = deformer+'Set'
	
	# Rename deformer set
	deformerSet = mc.listConnections(deformer+'.message',type='objectSet')[0]
	if deformerSet != deformerSetName: deformerSetName = mc.rename(deformerSet,deformerSetName)
	
	# Retrun result
	return deformerSetName

def getWeights(deformer,geometry=''):
	'''
	Get the weights for the specified deformer. Weights returned as a python list object
	@param deformer: Deformer to get weights for
	@type deformer: str
	@param geometry: Target geometry to get weights from
	@type geometry: str
	'''
	# Get geoShape
	geoShape = geometry
	if geometry and mc.objectType(geoShape) == 'transform':
		geoShape = mc.listRelatives(geometry,s=True,ni=True)[0]
	
	# Get deformer function set and members
	deformerFn = getDeformerFn(deformer)
	deformerSetMem = getDeformerSetMembers(deformer,geoShape)
	
	# Get weights
	weightList = OpenMaya.MFloatArray()
	deformerFn.getWeights(deformerSetMem[0],deformerSetMem[1],weightList)
	
	# Return result
	return list(weightList)
"""
def getWeights(deformer,geometry='',components=[]):
	'''
	Get the weights for the specified deformer. Weights returned as a python list object
	@param deformer: Deformer to get weights for
	@type deformer: str
	@param geometry: Target geometry to get weights from
	@type geometry: str
	'''
	# Get geoShape
	geoShape = geometry
	if geometry and mc.objectType(geoShape) == 'transform':
		geoShape = mc.listRelatives(geometry,s=True,ni=True)[0]
	
	# Get deformer function set and members
	deformerFn = getDeformerFn(deformer)
	deformerSetMem = []
	if components:
		deformerSetMem = glTools.utils.selection.getSelectionElement(components)
	else:
		deformerSetMem = getDeformerSetMembers(deformer,geoShape)
	
	# Get weights
	weightList = OpenMaya.MFloatArray()
	deformerFn.getWeights(deformerSetMem[0],deformerSetMem[1],weightList)
	
	# Return result
	return list(weightList)
"""
def setWeights(deformer,weights,geometry=''):
	'''
	Set the weights for the specified deformer using the input value list
	@param deformer: Deformer to set weights for
	@type deformer: str
	@param weights: Input weight value list
	@type weights: list
	@param geometry: Target geometry to apply weights to
	@type geometry: str
	'''
	# Get geoShape
	geoShape = geometry
	geoObj = glTools.utils.base.getMObject(geometry)
	if geometry and geoObj.hasFn(OpenMaya.MFn.kTransform):
		geoShape = mc.listRelatives(geometry,s=True,ni=True)[0]
	
	# Get deformer function set and members
	deformerFn = getDeformerFn(deformer)
	deformerSetMem = getDeformerSetMembers(deformer,geoShape)
	
	# Build weight array
	weightList = OpenMaya.MFloatArray()
	[weightList.append(i) for i in weights]
	
	# Set weights
	deformerFn.setWeight(deformerSetMem[0],deformerSetMem[1],weightList)

def bindPreMatrix(deformer,bindPreMatrix='',parent=True):
	'''
	Create a bindPreMatrix transform for the specified deformer.
	@param deformer: Deformer to create bind pre matrix transform for
	@type deformer: str
	@param bindPreMatrix: Specify existing transform for bind pre matrix connection. If empty, create a new transform
	@type bindPreMatrix: str
	@param parent: Parent the deformer handle to the bind pre matrix transform
	@type deformer: bool
	'''
	# Check deformer
	if not isDeformer(deformer):
		raise UserInputError('Object "'+deformer+'" is not a valid deformer!')
	if not mc.objExists(deformer+'.bindPreMatrix'):
		raise UserInputError('Deformer "'+deformer+'" does not accept bindPreMatrix connections!')
	
	# Get deformer handle
	deformerHandle = mc.listConnections(deformer+'.matrix',s=True,d=False)
	if deformerHandle: deformerHandle = deformerHandle[0]
	else:  raise Exception('Unable to find deformer handle!')
	
	# Check bindPreMatrix
	if bindPreMatrix:
		if not mc.objExists(bindPreMatrix):
			bindPreMatrix = mc.createNode('transform',n=bindPreMatrix)
	else:
		# Build bindPreMatrix transform
		prefix = deformerHandle.replace(deformerHandle.split('_')[-1],'')
		bindPreMatrix = mc.createNode('transform',n=prefix+'bindPreMatrix')
	
	# Match transform and pivot
	mc.xform(bindPreMatrix,ws=True,matrix=mc.xform(deformerHandle,q=True,ws=True,matrix=True))
	mc.xform(bindPreMatrix,ws=True,piv=mc.xform(deformerHandle,q=True,ws=True,rp=True))
	
	# Connect inverse matrix to localize cluster
	mc.connectAttr(bindPreMatrix+'.worldInverseMatrix[0]',deformer+'.bindPreMatrix',f=True)
	
	# Parent
	if parent: mc.parent(deformerHandle,bindPreMatrix)
	
	# Return result
	return bindPreMatrix

def pruneWeights(deformer,geoList=[],threshold=0.001):
	'''
	Set deformer component weights to 0.0 if the original weight value is below the set threshold
	@param deformer: Deformer to removed components from
	@type deformer: str
	@param geoList: The geometry objects whose components are checked for weight pruning
	@type geoList: list
	@param threshold: The weight threshold for removal
	@type threshold: str
	'''
	# Check deformer
	if not mc.objExists(deformer):
		raise Exception('Deformer "'+deformer+'" does not exist!')
	
	# Check geometry
	if type(geoList) == str: geoList = [geoList]
	if not geoList: geoList = mc.deformer(deformer,q=True,g=True)
	if not geoList: raise Exception('No geometry to prune weight for!')
	for geo in geoList:
		if not mc.objExists(geo):
			raise Exception('Geometry "'+geo+'" does not exist!')
	
	# For each geometry
	for geo in geoList:
		
		# Get deformer member indices
		memberIndexList = getDeformerSetMemberIndices(deformer,geo)
		
		# Get weight list
		weightList = getWeights(deformer,geo)
		
		# Prune weights
		pWeightList = [wt if wt > threshold else 0.0 for wt in weightList]
		
		# Apply pruned weight list
		setWeights(deformer,pWeightList,geo)

def pruneMembershipByWeights(deformer,geoList=[],threshold=0.001):
	'''
	Remove components from a specified deformer set if there weight value is below the set threshold
	@param deformer: Deformer to removed components from
	@type deformer: str
	@param geoList: The geometry objects whose components are checked for removal
	@type geoList: list
	@param threshold: The weight threshold for removal
	@type threshold: str
	'''
	# Check deformer
	if not mc.objExists(deformer):
		raise Exception('Deformer "'+deformer+'" does not exist!')
	
	# Check geometry
	if type(geoList) == str: geoList = [geoList]
	if not geoList: geoList = mc.deformer(deformer,q=True,g=True)
	if not geoList: raise Exception('No geometry to prune weight for!')
	for geo in geoList:
		if not mc.objExists(geo):
			raise Exception('Geometry "'+geo+'" does not exist!')
	
	# Get deformer set
	deformerSet = getDeformerSet(deformer)
	
	# For each geometry
	allPruneList = []
	for geo in geoList:
		
		# Get component type
		geoType = glTools.utils.geometry.componentType(geo)
	
		# Get deformer member indices
		memberIndexList = getDeformerSetMemberIndices(deformer,geo)
		
		# Get weights
		weightList = getWeights(deformer,geo)
		
		# Get prune list
		pruneList = [memberIndexList[i] for i in range(len(memberIndexList)) if weightList[i] <= threshold]
		pruneList = [geo+'.'+geoType+'['+str(i)+']' for i in pruneList]
		allPruneList.extend(pruneList)
		
		# Prune deformer set membership
		mc.sets(pruneList,rm=deformerSet)
	
	# Return prune list
	return allPruneList

def checkMultipleOutputs(deformer,printResult=True):
	'''
	Check the specified deformer for multiple ouput connections from a single plug.
	@param deformer: Deformer to check for multiple output connections
	@type deformer: str
	@param printResult: Print results to the script editor
	@type printResult: bool
	'''
	# Check deformer
	if not isDeformer(deformer):
		raise Exception('Deformer "'+deformer+'" is not a valid deformer!')
	
	# Get outputGeometry plug
	outGeomPlug = glTools.utils.attribute.getAttrMPlug(deformer+'.outputGeometry')
	if not outGeomPlug.isArray():
		raise Exception('Attribute "'+deformer+'.outputGeometry" is not an array attribute!')
	
	# Get existing indices
	indexList = OpenMaya.MIntArray()
	numIndex = outGeomPlug.getExistingArrayAttributeIndices(indexList)
	
	# Check output plugs
	returnDict = {}
	for i in range(numIndex):
		plugConn = mc.listConnections(deformer+'.outputGeometry['+str(indexList[i])+']',s=False,d=True,p=True)
		
		# Check multiple outputs
		if len(plugConn) > 1:
			# Append to return value
			returnDict[deformer+'.outputGeometry['+str(indexList[i])+']'] = plugConn
			# Print connection info
			if printResult:
				print('Deformer output "'+deformer+'.outputGeometry['+str(indexList[i])+']" has '+str(len(plugConn))+' outgoing connections:')
				for conn in plugConn: print('\t- '+conn)
	
	# Return result
	return returnDict
		
