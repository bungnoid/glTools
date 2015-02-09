import maya.mel as mm
import maya.cmds as mc

import glTools.utils.attribute
import glTools.utils.base
import glTools.utils.layer
import glTools.utils.reference
import glTools.utils.shader
import glTools.utils.shape
import glTools.utils.transform

import re

# ===========
# - Cleanup -
# ===========

def toggleCons(state):
	'''
	Toggle the display state of all joint buffers ('Con') in the scene
	@param state: The display state to set the joint buffers to
	@type state: bool
	'''
	# Get List of Con Joints
	conList = mc.ls('*Con*_jnt',type='joint')
	
	for conJnt in conList:
		
		# Toggle State
		if state:
			glTools.utils.base.displayOverride(conJnt,overrideEnable=1,overrideLOD=0)
			mc.setAttr(conJnt+'.drawStyle',0) # Bone
		else:
			glTools.utils.base.displayOverride(conJnt,overrideEnable=1,overrideLOD=1)
			mc.setAttr(conJnt+'.drawStyle',2) # None
		
		# Set Joint Radius
		if mc.getAttr(conJnt+'.radius',se=True):
			mc.setAttr(conJnt+'.radius',0.0)
			mc.setAttr(conJnt+'.radius',cb=False)
		
		# Hide Rotate Order
		if mc.getAttr(conJnt+'.ro',se=True):
			mc.setAttr(conJnt+'.ro',cb=False)
	
	# Return Result
	return conList

def toggleEnds(state):
	'''
	Toggle the display state of all joint buffers ('Con') in the scene
	@param state: The display state to set the joint buffers to
	@type state: bool
	'''
	# Get list of End joints
	endList = mc.ls('*End_jnt',type='joint')
	
	for endJnt in endList:
		
		# Toggle state
		if state:
			glTools.utils.base.displayOverride(endJnt,overrideEnable=1,overrideLOD=0)
			mc.setAttr(endJnt+'.drawStyle',0) # Bone
		else:
			glTools.utils.base.displayOverride(endJnt,overrideEnable=1,overrideLOD=1)
			mc.setAttr(endJnt+'.drawStyle',2) # None
		
		# Set Joint Radius
		if mc.getAttr(endJnt+'.radius',se=True):
			mc.setAttr(endJnt+'.radius',0.0)
			mc.setAttr(endJnt+'.radius',cb=False)
		
		# Hide Rotate Order
		if mc.getAttr(endJnt+'.ro',se=True):
			mc.setAttr(endJnt+'.ro',cb=False)
	
	# Return Result
	return endList

def disableDrawingOverrides(grp):
	'''
	Disable drawing overrides for all DAG descendents of the specified transform node.
	@param state: The transform under which all descendent node drawing overrides will be disabled.
	@type state: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(grp):
		raise Exception('Transform "'+grp+'" does not exists!')
	if not glTools.utils.transform.isTransform(grp):
		raise Exception('Object "'+grp+'" is not a valid transform!')
	
	# Get Descendent Node List
	nodeList = mc.ls(mc.listRelatives(grp,ad=True, pa=True) or [],dag=True) or []
	if not nodeList: return []
	
	# =============================
	# - Disable Drawing Overrides -
	# =============================
	
	overrideName = 'overrideEnabled'
	for node in nodeList:
		
		# Check Override Attribute
		overrideAttr = node+'.'+overrideName
		if not mc.attributeQuery(overrideName,n=node,ex=True):
			print('Override attribute "'+overrideAttr+'" does not exist! Skipping...')
			continue
		
		# Check Override Attribute Connections
		overrideConn = mc.listConnections(overrideAttr,s=True,d=False) or []
		if overrideConn:
			print('Found incoming connection for override attribute "'+overrideAttr+'"! ('+overrideConn[0]+')')
			print('Disconnecting attribute and disabling drawing overrides...')
			mc.disconnectAttr(overrideConn[0],overrideAttr)
		
		# Disable Drawing Overrides
		try: mc.setAttr(overrideAttr,0)
		except: pass
	
	# =================
	# - Return Result -
	# =================
	
	return nodeList

# ==========
# - Checks -
# ==========

def uniqueNameCheck(objList=[],transformsOnly=False):
	'''
	Return a list of nodes with non unique names
	@param objList: List of scene objects to check. If empty, use all existing scene nodes.
	@type objList: list
	@param transformsOnly: Check transform names only
	@type transformsOnly: bool
	'''
	# Get list of scene nodes
	if not objList:
		objList = mc.ls()
	if transformsOnly:
		nodeList = mc.ls(objList,transforms=True)
	else:
		nodeList = mc.ls(objList,dag=True)
	
	# Determine non unique names
	nonUniqueList = [i for i in nodeList if i.count('|')]
	
	# Return result
	return nonUniqueList

def validNameCheck(objList=[]):
	'''
	Check for valid names in the specified list of nodes
	@param objList: List of objects to check valid names for. If empty use all scene transforms
	@type objList: list
	'''
	# Check geo list
	if not objList: objList = mc.ls()
	if not objList: return []
	
	# Remove Default Nodes
	defNodes = ['dof1','time1','lambert1','postProcessList1','sequenceManager1','lightLinker1','renderGlobalsList1','dynController1','lightList1','particleCloud1','shaderGlow1']
	objList = [obj for obj in objList if not defNodes.count(obj)]
	objList = [obj for obj in objList if not obj.startswith('default')]
	objList = [obj for obj in objList if not mc.nodeType(obj) == 'objectTypeFilter']
	objList = [obj for obj in objList if not mc.nodeType(obj) == 'objectNameFilter']
	objList = [obj for obj in objList if not mc.nodeType(obj) == 'objectScriptFilter']
	
	# Check valid names
	result = []
	for obj in objList:
		
		# Check prefix
		#if not obj.startswith('cn_') and not obj.startswith('lf_') and not obj.startswith('rt_'):
		#	result.append(obj)
		
		# Check "pasted"
		if obj.count('pasted'): result.append(obj)
		
		# Check "poly"
		if obj.count('poly'): result.append(obj)
		
		# Check double underscore "__"
		if obj.count('__'): result.append(obj)
		
		# Check names ending with a digit (0-9)
		digitSearch = re.search('(\d+)$', obj)
		if digitSearch and glTools.utils.transform.isTransform(obj):
			if digitSearch.group(0):
				result.append(obj)
	
	# Remove Duplicate Entries
	result = list(set(result))
	
	# Return result
	return result

def shapeNameCheck(	objList				= [],
					typeList			= ['mesh','nurbsCurve','nurbsSurface'],
					skipIntermediates	= True,
					skipMultipleShapes	= False,
					strict				= True ):
	'''
	Return a list of incorrectly named geometry shape nodes.
	@param objList: List of objects to check for valid shape names. If empty, get all nodes of the specified type.
	@type objList: list
	@param typeList: List of shape types to check for valid names.
	@type typeList: list
	@param skipIntermediates: Skip intermediate shapes.
	@type skipIntermediates: bool
	@param skipMultipleShapes: Skip objects with multiple shape nodes.
	@type skipMultipleShapes: bool
	@param strict: Shape name must match parent+"Shape" to pass.
	@type strict: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not objList: objList = mc.ls(type=typeList)
	
	# ====================
	# - Build Shape List -
	# ====================
	
	shapeList = []
	for obj in objList:
		
		# Get Shapes from Transform
		if glTools.utils.transform.isTransform(obj):
			
			# Check Multiple Shapes
			objShapes = mc.listRelatives(obj,s=True,pa=True)
			if not objShapes: continue
			if (len(objShapes) > 1) and skipMultipleShapes: continue
			
			# Get Shapes
			tShapeList = mc.listRelatives(obj,s=True,ni=skipIntermediates,pa=True)
			for shape in tShapeList:
				shapeList.append(obj)
			
		elif glTools.utils.shape.isShape(obj):
			shapeList.append(obj)
			
		else:
			print('Unable to determine shape from object "'+obj+'"! Skipping...')
	
	# =====================
	# - Check Shape Names -
	# =====================
	
	invalidShapeNameList = []
	for shape in shapeList:
		
		# Check Type
		if not typeList.count(mc.objectType(shape)): continue
		
		# Check Intermediate Object
		if skipIntermediates and mc.getAttr(shape+'.intermediateObject'): continue
		
		# Get transform parent name
		parent = mc.listRelatives(shape,p=True,pa=True)[0]
		
		# Get Short Names
		shapeSN = mc.ls(shape,sn=True)[0]
		parentSN = mc.ls(parent,sn=True)[0]
		
		# Check Shape Name
		if strict and (shape != parent+'Shape'):
			invalidShapeNameList.append(shape)
		if not shapeSN.startswith(parentSN):
			invalidShapeNameList.append(shape)
		elif not shapeSN.count('Shape'):
			invalidShapeNameList.append(shape)
	
	# =================
	# - Return Result -
	# =================
	
	return invalidShapeNameList

def intermediateShapesCheck(objList=[]):
	'''
	Return a list of intermediate shapes.
	@param objList: List of objects to check for intermediate shapes.
	@type objList: list
	'''
	# Check nodeList
	if not objList: objList = mc.ls(transforms=True)
	else: objList = mc.ls(objList,transforms=True)
	
	# For each node
	result = []
	for obj in objList:
		
		# Get All Shapes
		shapes = mc.listRelatives(obj,s=True,pa=True)
		if not shapes: shapes = []
		for shape in shapes:
			
			# Check Intermediate Shapes
			if mc.objExists(shape+'.intermediateObject'):
				if mc.getAttr(shape+'.intermediateObject'):
					result.append(shape)
	
	# Return Result
	return result
	
def multipleShapeCheck(objList=[]):
	'''
	Return a list of transforms with multiple shape nodes
	@param objList: List of objects to check for multiple shapes.
	@type objList: list
	'''
	# Get scene transforms
	if not objList: objList = mc.ls(transforms=True)
	else: objList = mc.ls(objList,dag=True)
	
	# Iterate over scene transforms
	result = []
	for transform in objList:
		
		# Check Transform
		if not glTools.utils.transform.isTransform(transform):
			transform = mc.listRelatives(transform,p=True)[0]
		
		# Get transform shape list
		shapeList = mc.listRelatives(transform,s=True)
		
		# Check shape list
		if not shapeList: continue
		shapeList = mc.ls(shapeList,type=['mesh','nurbsSurface','nurbsCurve'])
		
		# Check number of shapes
		if len(shapeList) > 1: result.append(transform)
	
	# Return result
	return result

def constructionHistoryCheck(geoList=[]):
	'''
	Return a list of nodes that contain construction history
	@param objList: List of objects to check for construction history.
	@type objList: list
	'''
	# Get Scene Geometry
	if not geoList:
		geoList = mc.ls(geometry=True)
	else:
		geoList = mc.listRelatives(geoList,s=True,pa=True)
	
	# For each node
	result = []
	for geo in geoList:
		
		# Check Construction History
		hist = mc.listHistory(geo)
		
		# Remove Self
		if hist.count(geo): hist.remove(geo)
		
		# Ignore Node Types
		ignore = mc.ls(hist,type=['groupId','shadingEngine','transform'])
		hist = list(set(hist)-set(ignore))
		
		# Check History
		if hist:
			obj = mc.listRelatives(geo,p=True,pa=True)
			result.extend(obj)
	
	# Remove Duplicate Names
	if result: result = list(set(result))
	
	# Return Result
	return result

def userAttrCheck(objList=[],includeShapes=False):
	'''
	Return a list of user defined attributes for a specified list of nodes (and shapes).
	@param objList: List of objects to check for user defined attributes.
	@type objList: list
	@param includeShapes: Also check shapes for user defined attributes.
	@type includeShapes: bool
	'''
	# Initialize Return List
	result = []
	
	# Check objList
	if not objList: objList = mc.ls()
	
	# For each node
	for obj in objList:
		
		userAttrs = mc.listAttr(obj,ud=True)
		if not userAttrs: userAttrs = []
		for attr in userAttrs:
			result.append(obj+'.'+attr)
		
		# Check Shapes
		if includeShapes:
			
			shapes = mc.listRelatives(obj,s=True)
			if not shapes: shapes = []
			for shape in shapes:
				userAttrs = mc.listAttr(shape,ud=True)
				if not userAttrs: userAttrs = []
				for attr in userAttrs:
					result.append(shape+'.'+attr)
	
	# Return Result
	return result

def emptyGroupCheck(objList=[]):
	'''
	List empty groups.
	@param objList: List of transforms to check.
	@type objList: list
	'''
	# Check objList
	if not objList: objList = mc.ls(transforms=True)
	else: objList = mc.ls(objList,transforms=True)
	
	# Find Empty Groups
	result = []
	for grp in objList:
		if not mc.listRelatives(grp,ad=True):
			result.append(grp)
	
	# Return Result
	return result

def emptySetCheck(setList=[]):
	'''
	Return a list of empty sets
	@param setList: List of sets to check.
	@type setList: list
	'''
	# Check setList
	if not setList: setList = mc.ls(sets=True)
	
	# Check empty sets
	result = []
	for setName in setList:
		
		# Check Set
		if not mc.ls(setName,sets=True): continue
		
		# Skip Default Sets
		if setName.startswith('default'): continue
		if setName.startswith('initial'): continue
		
		# Check Set
		if not mc.sets(setName,q=True):
			result.append(setName)
	
	# Return result
	return result

def emptyLayerCheck(layerList=[]):
	'''
	Return a list if empty layers
	@param layerList: List of layers to check. If empty, use all existing layers in current scene.
	@type layerList: list
	'''
	# Check Layer List
	if not layerList: layerList = mc.ls(type=['displayLayer','renderLayer','animLayer'])
	else: layerList = mc.ls(layerList,type=['displayLayer','renderLayer','animLayer'])
	
	# Check Empty Layers
	result = []
	for layer in layerList:
		
		# Check Layer
		if not mc.ls(layer,type=['displayLayer','renderLayer','animLayer']): continue
		
		# Skip Default Layers
		if layer.startswith('default'): continue
		
		# Check Membership
		if not glTools.utils.layer.memberList(layer):
			result.append(layer)
	
	# Return Result
	return result

def animCurveCheck(curveTypeList=['animCurveTL','animCurveTA','animCurveTT','animCurveTU','animCurveUL','animCurveUA','animCurveUT','animCurveUU']):
	'''
	Return a list of all existing animCurves of a specified type.
	@param curveList: List of animCurve types to consider.
	@type curveList: list
	@param curveTypeList: List of animCurve types to consider.
	@type curveTypeList: list
	'''
	# Initialize Return List
	animCurves = []
	
	# List AnimCurve Nodes
	for curveType in curveTypeList:
		curveList = mc.ls(type=curveType)
		if curveList:
			animCurves.extend(curveList)
	
	# Return Result
	return animCurves

def unusedShadingNodeCheck():
	'''
	Return a list of unused shading nodes.
	'''
	return glTools.utils.shader.listUnusedShadingNodes()

def noGeometryShaderCheck(geoList=[]):
	'''
	Return a list of non intermediate geometry shapes with no shader assignment.
	@param geoList: List of geometry to check for shader assignments.
	@type geoList: list
	'''
	# Check Geometry List
	if not geoList:
		geoList = mc.ls(type=['mesh','nurbsSurface'],ni=True)
	else:
		geoList += mc.ls(mc.listRelatives(geoList,ad=True,pa=True) or [],type=['mesh','nurbsSurface'],ni=True) or []
		geoList = mc.ls(geoList,type=['mesh','nurbsSurface'],ni=True)
	
	# Check Shader Assignment
	noShaderList = []
	for geo in geoList:
		SG = glTools.utils.shader.getSG(geo)
		if not SG: noShaderList.append(geo)
	
	# Return Result
	return noShaderList

def unusedReferenceCheck():
	'''
	Return a list of unused reference nodes.
	'''
	# Initialize Return List
	result = []
	
	# Get list of existing references
	refList = glTools.utils.reference.listReferences()
	
	# Check Unused Reference
	for ref in refList:
		try: refFile = glTools.utils.reference.getReferenceFile(ref)
		except: result.append(ref)
	
	# Return Result
	return result

def unknownNodeCheck():
	'''
	Return a list of unknown nodes.
	'''
	result = mc.ls(type='unknown')
	if not result: result = []
	return result

def checkTransforms(objList=[],tol=0.0000000001):
	'''
	Check for non-zero transforms
	@param objList: List of transforms to check.
	@type objList: list
	@param tol: Value tolerance.
	@type tol: float
	'''
	# Check Object List
	if not objList: objList = mc.ls(transforms=True)
	if not objList: return []
	
	# Check Transforms
	transformList = []
	for obj in objList:
		
		# Skip Default Transforms
		if obj == 'persp': continue
		if obj == 'front': continue
		if obj == 'side': continue
		if obj == 'top': continue
		
		# Translate
		if abs(mc.getAttr(obj+'.tx')) > tol:
			transformList.append(obj)
			continue
		if abs(mc.getAttr(obj+'.ty')) > tol:
			transformList.append(obj)
			continue
		if abs(mc.getAttr(obj+'.tz')) > tol:
			transformList.append(obj)
			continue
		
		# Rotate
		if abs(mc.getAttr(obj+'.rx')) > tol:
			transformList.append(obj)
			continue
		if abs(mc.getAttr(obj+'.ry')) > tol:
			transformList.append(obj)
			continue
		if abs(mc.getAttr(obj+'.rz')) > tol:
			transformList.append(obj)
			continue
		
		# Scale
		if abs(mc.getAttr(obj+'.sx') - 1.0) > tol:
			transformList.append(obj)
			continue
		if abs(mc.getAttr(obj+'.sy') - 1.0) > tol:
			transformList.append(obj)
			continue
		if abs(mc.getAttr(obj+'.sz') - 1.0) > tol:
			transformList.append(obj)
			continue
	
	# Return Result
	return transformList

def displayOverridesCheck(objList=[]):
	'''
	Check all/specified objects for display overrides
	@param objList: List of DAG nodes to check. If empty, use all DAG nodes in scene
	@type objList: list
	'''
	# Check Object List
	if not objList: objList = mc.ls(dag=True)
	else: objList = mc.ls(objList,dag=True)
	
	# Check Display Overrides
	displayOverrideList = []
	for obj in objList:
		if mc.getAttr(obj+'.overrideEnabled'):
			displayOverrideList.append(obj)
	
	# Return Result
	return displayOverrideList

# =========
# - Fixes -
# =========

def shapeNameFix(shape):
	'''
	Fix incorrectly named geometry shape node
	@param objList: List of objects to check for valid shape names.
	@type objList: list
	@param typeList: List of shape types to check for valid names.
	@type typeList: list
	@param skipIntermediates: Skip intermediate shapes
	@type skipIntermediates: bool
	'''
	# Get Shape Transform Parent
	parent = mc.listRelatives(shape,p=True)[0]
		
	# Check Shape Name
	shapeName = parent+'Shape'
	if mc.objExists(shapeName):
		raise Exception('Shape "'+shapeName+'" already exists! Unable to rename shape "'+shape+'"!')
		
	# Rename Shape
	newShape = mc.rename(shape,shapeName)
	
	# Return Result
	return newShape

def deleteIntermediateShapes(objList=[]):
	'''
	Delete all intermediate shapes in the scene
	'''
	# Get list of intermediate shapes
	intermediateShapeList = intermediateShapesCheck(objList)
	# Delete intermediate shapes
	if intermediateShapeList: mc.delete(intermediateShapeList)
	# Return result
	return intermediateShapeList

def deleteConstructionHistory(geoList=[]):
	'''
	Delete construction history for specified geometry
	@param geoList: List of objects to delete for construction history from.
	@type geoList: list
	'''
	# Get Scene Geometry
	if not geoList: geoList = mc.ls(geometry=True)
	# Delete History
	for geo in geoList: mc.delete(geo,ch=True)
	# Return Result
	return geoList

def deleteUserAttrs(nodeList=[],includeShapes=False):
	'''
	Delete user defined attributes from the specified list of nodes
	@param nodeList: List of nodes to delete user defined attrs from. If empty, assume all nodes.
	@type nodeList: list
	@param includeShapes: Delete user attributes 
	@type includeShapes: bool
	'''
	# Check nodeList
	if not nodeList: nodeList = mc.ls()
	
	# For each node
	for node in nodeList:
		
		# Delete user attributes
		glTools.utils.attribute.deleteUserAttrs(node)
		
		# Include Shapes
		if includeShapes:
			
			# Delete shape user attributes
			shapes = mc.listRelatives(node,s=True)
			for shape in shapes:
				glTools.utils.attribute.deleteUserAttrs(shape)

def deleteEmptyGroups(objList=[]):
	'''
	Delete empty groups
	'''
	# Get Empty Group List
	emptyGrpList = emptyGroupCheck(objList=objList)
	# Delete Empty Groups
	if emptyGrpList: mc.delete(emptyGrpList)
	# Return Result
	return emptyGrpList

def deleteEmptySets(setList=[]):
	'''
	Delete empty groups
	'''
	# Get Empty Group List
	emptySetList = emptySetCheck(setList=setList)
	# Delete Empty Groups
	if emptySetList: mc.delete(emptySetList)
	# Return Result
	return emptySetList

def deleteEmptyLayers(layerList=[]):
	'''
	Delete empty groups
	'''
	# Get Empty Group List
	emptyLayerList = emptyLayerCheck(layerList=layerList)
	# Delete Empty Groups
	if emptyLayerList: mc.delete(emptyLayerList)
	# Return Result
	return emptyLayerList

def deleteUnknownNodes():
	'''
	Delete all node of type "unknown" in the scene
	'''
	# Get list of unknown nodes
	unknownNodes = unknownNodeCheck() or []
	
	# Delete unknown nodes
	for node in unknownNodes:
		try:
			mc.lockNode(node,l=False)
			mc.delete(node)
		except:
			print('Problem deleting unknown node "'+node+'"!')
	
	# Return Result
	return unknownNodes

def deleteNodesByType(nodeTypeList=[]):
	'''
	Delete nodes of the specified type(s).
	@param nodeTypeList: List of node types to delete.
	@type nodeTypeList: list
	'''
	# Check Node Types
	if not nodeTypeList: return []
	# Get Node List (by type)
	nodeList = mc.ls(type=nodeTypeList)
	# Delete Nodes
	if nodeList: mc.delete(nodeList)
	else: nodeList = []
	# Return Result
	return nodeList

def deleteUnusedReferenceNodes():
	'''
	Delete all unused reference nodes in the scene
	'''
	mm.eval('RNdeleteUnused')

def deleteEmptySets(setList=[]):
	'''
	Delete empty object sets
	@param setList: A list of sets to check. If empty, chack all sets in current scene.
	@type setList: list
	'''
	# Check setList
	if not setList: setList = mc.ls(sets=True)
	
	# Check empty sets
	emptySetList = []
	for set in setList:
		if not mc.sets(set,q=True):
			emptySetList.append(set)
	
	# Delete empty sets
	for emptySet in emptySetList:
		try: mc.delete(emptySet)
		except: pass
	
	# Return result
	return emptySetList

def deleteAllSets(excludeList=[]):
	'''
	Delete unused object sets
	@param excludeList: A list of sets to exclude from the list of unused sets.
	@type excludeList: list
	'''
	# Get set list
	setList = mc.ls(sets=True)
	if excludeList:
		excludeSetList = mc.ls(excludeList,sets=True)
		setList = list(set(setList)-set(excludeSetList))
	
	# Delete unused sets
	for deleteSet in setList:
		try: mc.delete(deleteSet)
		except: pass
	
	# Return result
	return setList
	
def deleteUnusedShadingNodes():
	'''
	Delete all unused shading nodes in the scene
	'''
	#texList = mc.ls(tex=True)
	#if texList: mc.delete(texList)
	mm.eval('MLdeleteUnused')

def deleteDisplayLayers():
	'''
	Delete all display layers
	'''
	# Get display layer list
	displayLayers = mc.ls(type='displayLayer')
	displayLayers.remove('defaultLayer')
	
	# Delete display layers
	if displayLayers: mc.delete(displayLayers)
	
	# Return result
	return displayLayers

def deleteRenderLayers():
	'''
	Delete all render layers
	'''
	# Get render layer list
	renderLayers = mc.ls(type='renderLayer')
	renderLayers.remove('defaultRenderLayer')
	
	# Delete render layers
	if renderLayers: mc.delete(renderLayers)
	
	# Return result
	return renderLayers

def assignInitialShadingGroup(geoList=[]):
	'''
	Assign initialShadingGroup (lambert1) to specified geometry.
	@param geoList: List of geometry to apply default shader to. If empty, use all scene geometry
	@type geoList: list
	'''
	# Check geoList
	if not geoList: geoList = mc.ls(geometry=True)
	if not geoList: return []
	
	# Assign Initial Shading Group
	mc.sets(geoList,fe='initialShadingGroup')
	
	# Return result
	return geoList

def zeroTransforms(objList=[]):
	'''
	Reset transform values
	@param objList: List of transforms to zero out.
	@type objList: list
	'''
	# Check Object List
	if not objList: objList = mc.ls(transforms=True)
	if not objList: return []
	
	# Check Transforms
	for obj in objList:
		
		# Translate
		if mc.getAttr(obj+'.tx',se=True): mc.setAttr(obj+'.tx',0)
		if mc.getAttr(obj+'.ty',se=True): mc.setAttr(obj+'.ty',0)
		if mc.getAttr(obj+'.tz',se=True): mc.setAttr(obj+'.tz',0)
		
		# Rotate
		if mc.getAttr(obj+'.rx',se=True): mc.setAttr(obj+'.rx',0)
		if mc.getAttr(obj+'.ry',se=True): mc.setAttr(obj+'.ry',0)
		if mc.getAttr(obj+'.rz',se=True): mc.setAttr(obj+'.rz',0)
		
		# Scale
		if mc.getAttr(obj+'.sx',se=True): mc.setAttr(obj+'.sx',0)
		if mc.getAttr(obj+'.sy',se=True): mc.setAttr(obj+'.sy',0)
		if mc.getAttr(obj+'.sz',se=True): mc.setAttr(obj+'.sz',0)
	
	# Return Result
	return objList

def copyInputShapeAttrs(geoList=[]):
	'''
	Copy user defined attributes from an input shape to the output deforming shape.
	@param geoList: List of geometry to copy atributes for.
	@type geoList: list
	'''
	# Check Geometry List
	if not geoList: geoList = mc.listRelatives(mc.ls(geometry=True) or [],p=True,pa=True) or []
	if not geoList: return []
	
	# Copy Input Shape Attrs
	for geo in geoList:
		
		# Get Output Shape
		geoShape = mc.listRelatives(geo,s=True,ni=True) or []
		if not geoShape:
			print('No shape found for geometry transform "'+geo+'"!')
			continue
		
		# Get Input Shape
		geoInputShape = geoShape[0]
		try: geoInputShape = glTools.utils.shape.findInputShape(geoShape[0])
		except: pass
		
		# Copy User Attributes
		if geoInputShape != geoShape[0]:
			userAttr = mc.listAttr(geoInputShape,ud=True,s=True) or []
			for at in userAttr: glTools.utils.attribute.copyAttr(geoInputShape,geoShape[0],at)

# ========
# - MISC -
# ========

def removeTurtle():
	'''
	Delete nodes and unload plgin related to the Turtle Renderer.
	'''
	# Remove Turtle Nodes
	turtleNode = 'TurtleDefaultBakeLayer'
	if mc.objExists(turtleNode):
		print('Removing Turtle nodes...')
		mc.lockNode(turtleNode,l=False)
		mc.delete(turtleNode)
	
	# Unload Plugin
	if mc.pluginInfo('Turtle',q=True,loaded=True):
		print('Unloading Turtle plugin...')
		try: mc.unloadPlugin('Turtle',f=True)
		except: print('Error unloading Turtle plugin!')
