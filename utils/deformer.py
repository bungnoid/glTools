import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.utils.attribute
import glTools.utils.arrayUtils
import glTools.utils.base
import glTools.utils.geometry
import glTools.utils.selection

import re

def isDeformer(deformer):
	'''
	Test if node is a valid deformer
	@param deformer: Name of deformer to query
	@type deformer: str
	'''
	# Check Deformer Exists
	if not mc.objExists(deformer): return False
	
	# Check Deformer Type
	nodeType = mc.nodeType(deformer,i=1)
	if not nodeType.count('geometryFilter'): return False
	
	# Return result
	return True

def getDeformerList(nodeType='geometryFilter',affectedGeometry=[],regexFilter=''):
	'''
	Return a list of deformer that match the input criteria.
	You can list deformers connected to specified geometry, by type and filter the results using regular expressions.
	@param type: Deformer Type as string. Optional arg, only return deformers of specified type.
	@type type: str
	@param affectedGeometry: Affected geometry list. Optional arg that will list deformers connected to the specified geometry.
	@type affectedGeometry: list
	@param regexFilter: Regular Expression as string. Optional arg that will filter results.
	@type regexFilter: str
	'''
	# Get Deformer List
	deformerNodes = mc.ls(type=nodeType)
	
	# ===============================
	# - Filter by Affected Geometry -
	# ===============================
	
	if affectedGeometry:
		if type(affectedGeometry) == str: affectedGeometry = [affectedGeometry]
		historyNodes = mc.listHistory(affectedGeometry,groupLevels=True,pruneDagObjects=True)
		deformerNodes = mc.ls(historyNodes,type=nodeType)
	
	# =========================
	# - Remove Unwanted Nodes -
	# =========================
	
	# Remove Duplicates
	deformerNodes = glTools.utils.arrayUtils.removeDuplicates(deformerNodes)
	
	# Remove Tweak Nodes
	tweakNodes = mc.ls(deformerNodes,type='tweak')
	if tweakNodes: deformerNodes = [x for x in deformerNodes if not x in tweakNodes]
	
	# Remove TransferAttributes Nodes
	transferAttrNodes = mc.ls(deformerNodes,type='transferAttributes')
	if transferAttrNodes: deformerNodes = [x for x in deformerNodes if not x in transferAttrNodes]
	
	# ==================
	# - Filter Results -
	# ==================
	
	if regexFilter:
		reFilter = re.compile(regexFilter)
		deformerNodes = filter(reFilter.search, deformerNodes)	
	
	# =================	
	# - Return Result -
	# =================
	
	return deformerNodes

def getDeformerFn(deformer):
	'''
	Initialize and return an MFnWeightGeometryFilter function set attached to the specified deformer
	@param deformer: Name of deformer to create function set for
	@type deformer: str
	'''
	# Checks
	if not mc.objExists(deformer):
		raise Exception('Deformer '+deformer+' does not exist!')
	
	# Get MFnWeightGeometryFilter
	deformerObj = glTools.utils.base.getMObject(deformer)
	try:
		deformerFn = OpenMayaAnim.MFnWeightGeometryFilter(deformerObj)
	except: # is there a good exception type for this?
		raise Exception('Could not get a geometry filter for deformer "'+deformer+'"!')
	
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
		raise Exception('Deformer '+deformer+' does not exist!')
	if not isDeformer(deformer):
		raise Exception('Object '+deformer+' is not a valid deformer!')
	
	# Get Deformer Set
	deformerObj = glTools.utils.base.getMObject(deformer)
	deformerFn = OpenMayaAnim.MFnGeometryFilter(deformerObj)
	deformerSetObj = deformerFn.deformerSet()
	if deformerSetObj.isNull():
		raise Exception('Unable to determine deformer set for "'+deformer+'"!')
	
	# Return Result
	return OpenMaya.MFnDependencyNode(deformerSetObj).name()

def getDeformerSetFn(deformer):
	'''
	Initialize and return an MFnSet function set attached to the deformer set of the specified deformer
	@param deformer: Name of deformer attached to the deformer set to create function set for
	@type deformer: str
	'''
	# Checks
	if not mc.objExists(deformer):
		raise Exception('Deformer '+deformer+' does not exist!')
	
	# Get deformer set
	deformerSet = getDeformerSet(deformer)
	
	# Get MFnWeightGeometryFilter
	deformerSetObj = glTools.utils.base.getMObject(deformerSet)
	deformerSetFn = OpenMaya.MFnSet(deformerSetObj)
	
	# Return result
	return deformerSetFn

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
			except:	raise Exception('Object "'+geo+'" is not a valid geometry!')
		geomPath = glTools.utils.base.getMDagPath(geometry)
		
		# Check geometry affected by deformer
		if not (geometry in getAffectedGeometry(deformer,returnShapes=True).keys()):
			raise Exception('Geometry "'+geometry+'" is not a affected by deformer "'+deformer+'"!')
		
		# Cycle through selection set members
		for i in range(deformerSetSel.length()):
			# Get deformer set members
			deformerSetSel.getDagPath(i,deformerSetPath,deformerSetComp)
			if geomPath == deformerSetPath:
				setSelIndexFound = True
				break
		
		# Check setSelIndex found
		if not setSelIndexFound:
			raise Exception('No valid geometryIndex found for "'+geometry+'" in deformer set for "'+deformer+'"!')
	else:
		# Get deformer set members
		deformerSetSel.getDagPath(0,deformerSetPath,deformerSetComp)
	
	# Return result
	return [deformerSetPath,deformerSetComp]

"""

def getDeformerSetMembers(deformer,geometry=''):
	'''
	Return the deformer set members of the specified deformer.
	You can specify a shape name to query deformer membership for.
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
	deformerSetFn.getMembers(deformerSetSel,True)
	deformerSetPath = OpenMaya.MDagPath()
	deformerSetComp = OpenMaya.MObject()
	
	# Get geometry index
	if geometry: geomIndex = getGeomIndex(geometry,deformer)
	else: geomIndex = 0
	
	# Get number of selection components
	deformerSetLen = deformerSetSel.length()
	if geomIndex >= deformerSetLen:
		raise Exception('Geometry index out of range! (Deformer: "'+deformer+'", Geometry: "'+geometry+'", GeoIndex: '+str(geomIndex)+', MaxIndex: '+str(deformerSetLen)+')')
	
	# Get deformer set members
	deformerSetSel.getDagPath(geomIndex,deformerSetPath,deformerSetComp)
	
	# Return result
	return [deformerSetPath,deformerSetComp]
#"""

def getDeformerSetMemberStrList(deformer,geometry=''):
	'''
	Return the deformer set members of the specified deformer as a list of strings.
	You can specify a shape name to query deformer membership for.
	Otherwise, membership for the first affected geometry will be returned.
	@param deformer: Deformer to query set membership for
	@type deformer: str
	@param geometry: Geometry to query deformer set membership for. Optional.
	@type geometry: str
	'''
	# Get deformer function sets
	deformerSetFn = getDeformerSetFn(deformer)
	
	# Get deformer set members
	deformerSetSel = OpenMaya.MSelectionList()
	deformerSetFn.getMembers(deformerSetSel,True)
	
	# Convert to list of strings
	setMemberStr = []
	deformerSetSel.getSelectionStrings(setMemberStr)
	setMemberStr = mc.ls(setMemberStr,fl=True)
	
	# Return Result
	return setMemberStr

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
		except:	raise Exception('Object "'+geo+'" is not a valid geometry!')
	# Get geometry type
	geometryType = mc.objectType(geometry)
	
	# Get deformer set members
	deformerSetMem = getDeformerSetMembers(deformer,geometry)
	
	# ==========================
	# - Get Set Member Indices -
	# ==========================
	memberIdList = []
	
	# Single Index
	if geometryType == 'mesh' or geometryType == 'nurbsCurve' or geometryType == 'particle':
		memberIndices = OpenMaya.MIntArray()
		singleIndexCompFn = OpenMaya.MFnSingleIndexedComponent(deformerSetMem[1])
		singleIndexCompFn.getElements(memberIndices)
		memberIdList = list(memberIndices)
	
	# Double Index
	if geometryType == 'nurbsSurface':
		memberIndicesU = OpenMaya.MIntArray()
		memberIndicesV = OpenMaya.MIntArray()
		doubleIndexCompFn = OpenMaya.MFnDoubleIndexedComponent(deformerSetMem[1])
		doubleIndexCompFn.getElements(memberIndicesU,memberIndicesV)
		for i in range(memberIndicesU.length()):
			memberIdList.append([memberIndicesU[i],memberIndicesV[i]])
	
	# Triple Index
	if geometryType == 'lattice':
		memberIndicesS = OpenMaya.MIntArray()
		memberIndicesT = OpenMaya.MIntArray()
		memberIndicesU = OpenMaya.MIntArray()
		tripleIndexCompFn = OpenMaya.MFnTripleIndexedComponent(deformerSetMem[1])
		tripleIndexCompFn.getElements(memberIndicesS,memberIndicesT,memberIndicesU)
		for i in range(memberIndicesS.length()):
			memberIdList.append([memberIndicesS[i],memberIndicesT[i],memberIndicesU[i]])
		
	# Return result
	return memberIdList

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
	# Verify Input
	if not isDeformer(deformer):
		raise Exception('Object "'+deformer+'" is not a valid deformer!')
	
	# Initialize Return Array (dict)
	affectedObjects = {}
	
	# Get MFnGeometryFilter
	deformerObj = glTools.utils.base.getMObject(deformer)
	geoFilterFn = OpenMayaAnim.MFnGeometryFilter(deformerObj)
	
	# Get Output Geometry
	outputObjectArray = OpenMaya.MObjectArray()
	geoFilterFn.getOutputGeometry(outputObjectArray)
	
	# Iterate Over Affected Geometry
	for i in range(outputObjectArray.length()):
		
		# Get Output Connection at Index
		outputIndex = geoFilterFn.indexForOutputShape(outputObjectArray[i])
		outputNode = OpenMaya.MFnDagNode(outputObjectArray[i])
		
		# Check Return Shapes
		if not returnShapes: outputNode = OpenMaya.MFnDagNode(outputNode.parent(0))
		
		# Check Full Path
		if fullPathNames: affectedObjects[outputNode.fullPathName()] = outputIndex
		else: affectedObjects[outputNode.partialPathName()] = outputIndex
	
	# Return Result
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
		raise Exception('Object "'+deformer+'" is not a valid deformer!')
	
	# Check geometry
	geo = geometry
	if mc.objectType(geometry) == 'transform':
		try: geometry = mc.listRelatives(geometry,s=True,ni=True,pa=True)[0]
		except:	raise Exception('Object "'+geo+'" is not a valid geometry!')
	geomObj = glTools.utils.base.getMObject(geometry)
	
	# Get geometry index
	deformerObj = glTools.utils.base.getMObject(deformer)
	deformerFn = OpenMayaAnim.MFnGeometryFilter(deformerObj)
	try: geomIndex = deformerFn.indexForOutputShape(geomObj)
	except: raise Exception('Object "'+geometry+'" is not affected by deformer "'+deformer+'"!')
	
	# Retrun result
	return geomIndex

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
		raise Exception('Object "'+deformer+'" is not a valid deformer!')
	
	# Check deformer set name
	if not deformerSetName: deformerSetName = deformer+'Set'
	
	# Rename deformer set
	deformerSet = mc.listConnections(deformer+'.message',type='objectSet')[0]
	if deformerSet != deformerSetName: deformerSetName = mc.rename(deformerSet,deformerSetName)
	
	# Retrun result
	return deformerSetName

def getWeights(deformer,geometry=None):
	'''
	Get the weights for the specified deformer. Weights returned as a python list object
	@param deformer: Deformer to get weights for
	@type deformer: str
	@param geometry: Target geometry to get weights from
	@type geometry: str
	'''
	# Check Deformer
	if not isDeformer(deformer):
		raise Exception('Object "'+deformer+'" is not a valid deformer!')
	
	# Check Geometry
	if not geometry:
		geometry = getAffectedGeometry(deformer).keys()[0]
	
	# Get Geometry Shape
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
def setWeights(deformer,weights,geometry=None):
	'''
	Set the weights for the specified deformer using the input value list
	@param deformer: Deformer to set weights for
	@type deformer: str
	@param weights: Input weight value list
	@type weights: list
	@param geometry: Target geometry to apply weights to. If None, use first affected geometry.
	@type geometry: str
	'''
	# Check Deformer
	if not isDeformer(deformer):
		raise Exception('Object "'+deformer+'" is not a valid deformer!')
	
	# Check Geometry
	if not geometry:
		geometry = getAffectedGeometry(deformer).keys()[0]
		
	# Get Geometry Shape
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
		raise Exception('Object "'+deformer+'" is not a valid deformer!')
	if not mc.objExists(deformer+'.bindPreMatrix'):
		raise Exception('Deformer "'+deformer+'" does not accept bindPreMatrix connections!')
	
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
		
		# Get Component Type
		geoType = glTools.utils.geometry.componentType(geo)
	
		# Get Deformer Member Indices
		memberIndexList = getDeformerSetMemberIndices(deformer,geo)
		
		# Get Weights
		weightList = getWeights(deformer,geo)
		
		# Get Prune List
		pruneList = [memberIndexList[i] for i in range(len(memberIndexList)) if weightList[i] <= threshold]
		for i in range(len(pruneList)):
			if type(pruneList[i]) == str or type(pruneList[i]) == unicode or type(pruneList[i]) == int:
				pruneList[i] = '['+str(pruneList[i])+']'
			elif type(pruneList[i]) == list:
				pruneList[i] = [str(p) for p in pruneList[i]]
				pruneList[i] = '['+']['.join(pruneList[i])+']'
			pruneList[i] = geo+'.'+geoType+str(pruneList[i])
		allPruneList.extend(pruneList)
		
		# Prune deformer set membership
		if pruneList: mc.sets(pruneList,rm=deformerSet)
	
	# Return prune list
	return allPruneList

def clean(deformer,threshold=0.001):
	'''
	Clean specified deformer.
	Prune weights under the given tolerance and prune membership.
	@param deformer: The deformer to clean. 
	@type deformer: str
	@param threshold: Weight value tolerance for prune operations.
	@type threshold: float
	'''
	# Print Message
	print('Cleaning deformer: '+deformer+'!')
	
	# Check Deformer
	if not isDeformer(deformer):
		raise Exception('Object "'+deformer+'" is not a valid deformer!')
	
	# Prune Weights
	glTools.utils.deformer.pruneWeights(deformer,threshold=threshold)
	# Prune Membership
	glTools.utils.deformer.pruneMembershipByWeights(deformer,threshold=threshold)

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
		
