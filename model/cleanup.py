import maya.mel as mm
import maya.cmds as mc

import glTools.utils.attribute
import glTools.utils.mesh
import glTools.ui.utils

def cleanAll():
	'''
	'''
	# Clear Selection
	mc.select(cl=True)
	
	# Initialize Report Message
	msg = '==== Clean Scene Geometry ====\n'
	msg += '------------------------------\n\n'
	
	# -----------------------
	# - Delete Unused Nodes -
	# -----------------------
	
	# Unknown Nodes
	unknownNodes = deleteUnknownNodes()
	msg += 'Delete Unknown Nodes:\n'
	for node in unknownNodes:
		msg += '\t- '+node+'\n'
	msg += 'Done!\n\n'
	
	# History
	deleteSceneHistory()
	msg += 'Deleted Scene History:...\nDone!\n\n'
	
	# Shaders
	assignInitialShadingGroup()
	deleteUnusedShadingNodes()
	msg += 'Assign Default Shader:...\nDone!\n\n'
	msg += 'Deleted Unused Shading Nodes:...\nDone!\n\n'
	
	# Layers
	displayLayers = deleteDisplayLayers()
	msg += 'Delete Display Layers:\n'
	for layer in displayLayers:
		msg += '\t-'+layer+'\n'
	msg += 'Done!\n\n'
	
	renderLayers = deleteRenderLayers()
	msg += 'Delete Render Layers:\n'
	for layer in renderLayers:
		msg += '\t-'+layer+'\n'
	msg += 'Done!\n\n'
	
	# Reference Nodes
	deleteUnusedReferenceNodes()
	msg += 'Deleted Unused Reference Nodes:...\nDone!\n\n'
	
	# Empty Groups
	emptyGrpList = deleteEmptyGroups()
	msg += 'Delete Empty Groups:\n'
	for grp in emptyGrpList:
		msg += '\t-'+grp+'\n'
	msg += 'Done!\n\n'
	
	# Intermediate Shapes
	intermediateShapeList = deleteIntermediateShapes()
	msg += 'Delete Intermediate Shapes:\n'
	for intShape in intermediateShapeList:
		msg += '\t-'+intShape+'\n'
	msg += 'Done!\n\n'
	
	# User Attributes
	deleteUserAttrs()
	msg += 'Deleted Extra Attributes:...\nDone!\n\n'
	
	# Unused Nodes - Defined List
	unusedNodes = deleteUnusedNodes()
	msg += 'Delete Unused Nodes:\n'
	for unusedNode in unusedNodes:
		msg += '\t-'+unusedNode+'\n'
	msg += 'Done!\n\n'
	
	# ----------------------
	# - Get Scene Geometry -
	# ----------------------
	
	# Get geometry list
	shapeList = mc.ls(type=['mesh','nurbsSurface'])
	if not shapeList: shapeList = []
	transformList = list(set([mc.listRelatives(shape,p=True,pa=True)[0] for shape in shapeList]))
	
	for transform in transformList:
		
		# Freeze Transforms
		mc.makeIdentity(transform,apply=True,t=True,r=True,s=True,n=False)
		msg += 'Freeze Transforms:...\nDone!\n\n'
		
		# Set Pivot to Origin
		mc.xform(transform,ws=True,piv=[0,0,0])
		msg += 'Set Transform Pivots to Origin:...\nDone!\n\n'
	
	# Set Render Stats
	for shape in shapeList: renderStats(shape)
	msg += 'Set Render Stats:...\nDone!\n\n'
	
	# Unlock Normals
	unlockNormals()
	msg += 'Unlock Polygon Normals:...\nDone!\n\n'
	
	# ---------------------------
	# - Check User Fixed Issues -
	# ---------------------------
	
	msg += '====== User Fixed Items ======\n'
	msg += '------------------------------\n\n'
	
	# Non-Unique Names
	nonUnique = uniqueNameCheck()
	if nonUnique:
		msg += 'Non-Unique Names:\n'
		for item in nonUnique:
			msg += '\t- '+item+'\n'
		msg += '\n\n'
	
	# Valid Names
	invalidNameList = validNameCheck()
	if invalidNameList:
		msg += 'Invalid Names:\n'
		for item in invalidNameList:
			msg += '\t- '+item+'\n'
		msg += '\n\n'
	
	# Non Quads
	nonQuadList = nonQuads()
	if nonQuadList:
		nonQuadGeo = list(set(mc.ls(nonQuadList,o=True)))
		msg += 'Non-Quad Geometry:\n'
		for item in nonQuadGeo:
			msg += '\t- '+item+'\n'
		msg += '\n\n'
	
	# -----------------------
	# - Restore Scene State -
	# -----------------------
	
	mm.eval('changeSelectMode -object')
	mc.select(cl=True)
	
	# ----------------
	# - Print Report -
	# ----------------
	
	reportWindow(msg,'Clean Scene Geometry')
	
	
def cleanSceneAll():
	'''
	Run optimize scene with all options enabled
	'''
	mm.eval('cleanUpScene 3')

# ------------------
# - User Interface -
# ------------------

def displayListWindow(itemList,title):
	'''
	'''
	# Check itemList
	if not itemList: return
	
	# Window
	window = 'displayListWindowUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,t=title,s=True)
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	TSL = mc.textScrollList('displayListWindowTSL',allowMultiSelection=True)
	for item in itemList: mc.textScrollList(TSL,e=True,a=item)
	mc.textScrollList(TSL,e=True,sc='glTools.ui.utils.selectFromTSL("'+TSL+'")')
	closeB = mc.button('displayListWindowB',l='Close',c='mc.deleteUI("'+window+'")')
	
	# Form Layout
	mc.formLayout(FL,e=True,af=[(TSL,'top',5),(TSL,'left',5),(TSL,'right',5)])
	mc.formLayout(FL,e=True,af=[(closeB,'bottom',5),(closeB,'left',5),(closeB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(TSL,'bottom',5,closeB)])
	
	# Display Window
	mc.showWindow(window)

def reportWindow(msg,title):
	'''
	'''
	# Check message
	if not msg: return
	
	# Window
	window = 'reportWindowUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,t=title,s=True)
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	reportSF = mc.scrollField('reportWindowSF',editable=False,wordWrap=True,text=msg)
	closeB = mc.button('reportWindowB',l='Close',c='mc.deleteUI("'+window+'")')
	
	# Form Layout
	mc.formLayout(FL,e=True,af=[(reportSF,'top',5),(reportSF,'left',5),(reportSF,'right',5)])
	mc.formLayout(FL,e=True,af=[(closeB,'bottom',5),(closeB,'left',5),(closeB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(reportSF,'bottom',5,closeB)])
	
	# Display Window
	mc.showWindow(window)

# ----------
# - Naming -
# ----------

def shapeNameCheck():
	'''
	Return a list of incorrectly named shapes
	'''
	# Define valid shape list
	typeList = ['mesh','nurbsCurve','nurbsSurface']
	
	# Get scene shape list
	shapeList = mc.ls(type=typeList)
	
	# Check shape names
	invalidShapeNameList = []
	for shape in shapeList:
		
		# Get transform parent name
		parent = mc.listRelatives(shape,p=True)[0]
		
		# Check name
		if shape != parent+'Shape':
			invalidShapeNameList.append(shape)
	
	# Return result
	return invalidShapeNameList

def uniqueNameCheck(transformsOnly=True):
	'''
	Return a list of nodes with non unique names
	@param transformsOnly: Check transform names only
	@type transformsOnly: bool
	'''
	# Get list of scene nodes
	if transformsOnly: nodeList = mc.ls(type='transform')
	else: nodeList = mc.ls(dag=True)
	
	# Determine non unique names
	nonUniqueList = [i for i in nodeList if i.count('|')]
	
	# Return result
	return nonUniqueList

def uniqueNameFix(fixList):
	'''
	'''
	pass

def validNameCheck(objList=[]):
	'''
	Check for valid names in the specified list of nodes
	@param objList: List of objects to check valid names for. If empty use all scene transforms
	@type objList: list
	'''
	# Check geo list
	if not objList:
		#objList = mc.ls(type='transform')
		objList = mc.ls(dag=True,ro=False)
		objList.remove('persp')
		objList.remove('top')
		objList.remove('front')
		objList.remove('side')
		objList.remove('perspShape')
		objList.remove('topShape')
		objList.remove('frontShape')
		objList.remove('sideShape')
	
	# Check empty list
	if not objList: return
	
	# Check valid names
	invalidNameList = []
	for obj in objList:
		
		# Check prefix
		if not obj.startswith('cn_') and not obj.startswith('lf_') and not obj.startswith('rt_'):
			invalidNameList.append(obj)
	
	# Return result
	return invalidNameList
	
# ==============
# - Attributes -
# ==============

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

def renderStats(geo,castShadow=True,receiveShadow=True,motionBlur=True,primaryVis=True,smoothShade=True,reflectVis=True,refractVis=True,doubleSided=False,opposite=False):
	'''
	'''
	# Check geo
	if not mc.objExists(geo): raise Exception('Geometry "'+geo+'" does not exist!!')
	
	# Set render stats
	mc.setAttr(geo+'.castsShadows',int(castShadow))
	mc.setAttr(geo+'.receiveShadows',int(receiveShadow))
	mc.setAttr(geo+'.motionBlur',int(motionBlur))
	mc.setAttr(geo+'.primaryVisibility',int(primaryVis))
	mc.setAttr(geo+'.smoothShading',int(smoothShade))
	mc.setAttr(geo+'.visibleInReflections',int(reflectVis))
	mc.setAttr(geo+'.visibleInRefractions',int(refractVis))
	mc.setAttr(geo+'.doubleSided',int(doubleSided))
	mc.setAttr(geo+'.opposite',int(opposite))
	
def cacheGeoAttr_add():
	'''
	'''
	# Get list of renderable geometry
	geoList = mc.ls(type=['mesh','nurbsSurface'])
	
	# For each geo shape
	for geo in geoList:
		
		# Get shape transform
		geoParent = mc.listRelatives(geo,p=True)[0]
		
		# Add attribute
		if not mc.objExists(geoParent+'.cachegeo'):
			mc.addAttr(geoParent,ln='cachegeo',at='bool',k=True)
		mc.setAttr(geoParent+'.cachegeo',1)
	
def cacheGeoAttr_set():
	'''
	'''
	# Get list of objects with cachegeo attr
	geoAttrList = mc.ls('*.cachegeo',o=True)
	
	# For each object
	for geo in geoAttrList:
		
		# Get long name
		geoLongName = mc.ls(geo,l=True)[0]
		
		# Check blendShape
		if geoLongName.count('blendshapes'):
			mc.setAttr(geo+'.cachegeo',0)
		else:
			mc.setAttr(geo+'.cachegeo',1)

# ================
# - Unused Nodes -
# ================

def deleteUnusedNodes(typeList=[]):
	'''
	'''
	# Check type list
	if not typeList:
		typeList = [	'constraint',
						'pairBlend',
						'locator',
						'expression',
						'groupId',
						'groupParts',
						'animCurve',
						'snapshot',
						'unitConversion',
						'partition',
						'brush'	]
	
	# Get list of unused nodes
	nodeList = mc.ls(type=typeList,ro=False)
	if not nodeList: return []
	
	nodeList.remove('characterPartition')
	nodeList.remove('renderPartition')
	
	# Delete nodes
	delList = []
	for node in nodeList:
		try: mc.delete(node)
		except: continue
		else: delList.append(node)
	
	# Return result
	return delList

def deleteSceneHistory(nodeList=[]):
	'''
	'''
	# Get node list
	if not nodeList: nodeList = mc.ls(dag=True)
	if not nodeList: nodeList = []
	
	# Delete history
	for node in nodeList:
		try: mc.delete(node,ch=True)
		except: pass
	
	# Return result
	return nodeList

def listEmptyGroups():
	'''
	List empty groups
	'''
	mm.eval('source cleanUpScene.mel')
	emptyGrpList = mm.eval('listEmptyGroups ""')
	if not emptyGrpList: emptyGrpList = []
	return emptyGrpList

def deleteEmptyGroups():
	'''
	Delete empty groups
	'''
	emptyGrpList = listEmptyGroups()
	if emptyGrpList: mc.delete(emptyGrpList)
	return emptyGrpList

def deleteUnknownNodes():
	'''
	Delete all node of type "unknown" in the scene
	'''
	# Get list of unknown nodes
	unknownNodeList = mc.ls(type='unknown')
	if not unknownNodeList: unknownNodeList = []
	
	# Delete unknown nodes
	if unknownNodeList:	mc.delete(unknownNodeList)
	
	# Return reult
	return unknownNodeList

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

def deleteUnusedSets(excludeList=['pub_*']):
	'''
	Delete unused object sets
	@param excludeList: A list of sets to exclude from the list of unused sets.
	@type excludeList: list
	'''
	# Get set list
	setList = mc.ls(sets=True)
	excludeSetList = mc.ls(excludeList,sets=True)
	unusedSetList = list(set(setList)-set(excludeSetList))
	
	# Delete unused sets
	for unusedSet in unusedSetList:
		try: mc.delete(unusedSet)
		except: pass
	
	# Return result
	return unusedSetList
	
def checkIntermediateShapes(objList=[]):
	'''
	Return a list of intermediate shapes in the scene
	'''
	# Check object list
	if not objList: objList = mc.ls(transforms=True)
	
	# Find intermediate shapes
	shapeList = mc.listRelatives(objList,s=True,pa=True)
	intermediateShapeList = mc.ls(shapeList,type=['mesh','nurbsSurface','nurbsCurve'],io=True)
	
	# Check intermediate shapes list
	if not intermediateShapeList: intermediateShapeList = []
	
	# Return result
	return intermediateShapeList

def deleteIntermediateShapes(objList=[]):
	'''
	Delete all intermediate shapes in the scene
	'''
	# Get list of intermediate shapes
	intermediateShapeList = checkIntermediateShapes(objList)
	
	# Delete intermediate shapes
	if intermediateShapeList: mc.delete(intermediateShapeList)
	
	# Return result
	return intermediateShapeList
	
def checkMultipleShapes(transformList=[]):
	'''
	Return a list of transforms with multipl shapes
	'''
	# Get scene transforms
	if not transformList:
		transformList = mc.ls(transforms=True)
	
	# Initialize return list
	multiShapeTransformList = []
	
	# Iterate over scene transforms
	for transform in transformList:
		
		# Get transform shape list
		shapeList = mc.listRelatives(transform,s=True)
		
		# Check shape list
		if not shapeList: continue
		shapeList = mc.ls(shapeList,type=['mesh','nurbsSurface','nurbsCurve'])
		
		# Check number of shapes
		if len(shapeList) > 1: multiShapeTransformList.append(transform)
	
	# Return result
	return multiShapeTransformList

# -----------
# - Shaders -
# -----------

def deleteUnusedShadingNodes():
	'''
	Delete all unused shading nodes in the scene
	'''
	texList = mc.ls(tex=True)
	if texList: mc.delete(texList)
	mm.eval('MLdeleteUnused')

def assignInitialShadingGroup(geoList=[]):
	'''
	'''
	# Check geoList
	if not geoList:
		typeList = ['mesh','nurbsSurface']
		geoList = mc.ls(type=typeList)
	if not geoList:
		print 'No valid shapes to assign shader to!!'
		return
	
	# Assign Initial Shading Group
	mc.sets(geoList,fe='initialShadingGroup')
	
	# Return result
	return geoList

# ----------
# - Layers -
# ----------

def deleteDisplayLayers():
	'''
	Delete all render layers
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

# ===============
# - Scale Check -
# ===============

def measureBoundingBox(geo):
	'''
	'''
	# Check geo
	if not mc.objExists(geo): raise Exception('Geometry "'+geo+'" does not exist!!')
	
	# -----------------------------------
	# - Create distance dimension nodes -
	# -----------------------------------
	
	del_locs = []
	
	# Height
	hDimensionShape = mc.distanceDimension(sp=(0,0,0),ep=(1,1,1))
	locs = mc.listConnections(hDimensionShape,s=True,d=False)
	if locs: del_locs.extend(locs)
	hDimension = mc.listRelatives(hDimensionShape,p=True)[0]
	hDimension = mc.rename(hDimension,geo+'_height_measure')
	
	# Width
	wDimensionShape = mc.distanceDimension(sp=(0,0,0),ep=(1,1,1))
	locs = mc.listConnections(wDimensionShape,s=True,d=False)
	if locs: del_locs.extend(locs)
	wDimension = mc.listRelatives(wDimensionShape,p=True)[0]
	wDimension = mc.rename(wDimension,geo+'_width_measure')
	
	# Depth
	dDimensionShape = mc.distanceDimension(sp=(0,0,0),ep=(1,1,1))
	locs = mc.listConnections(dDimensionShape,s=True,d=False)
	if locs: del_locs.extend(locs)
	dDimension = mc.listRelatives(dDimensionShape,p=True)[0]
	dDimension = mc.rename(dDimension,geo+'_depth_measure')
	
	measure_grp = mc.group([hDimension,wDimension,dDimension],n=geo+'_measure_grp')
	
	# ------------------------------------
	# - Connect distance dimension nodes -
	# ------------------------------------
	
	# Height
	mc.connectAttr(geo+'.boundingBoxMin',hDimension+'.startPoint',f=True)
	addHeightNode = mc.createNode('plusMinusAverage',n=geo+'_height_plusMinusAverage')
	mc.connectAttr(geo+'.boundingBoxMin',addHeightNode+'.input3D[0]',f=True)
	mc.connectAttr(geo+'.boundingBoxSizeY',addHeightNode+'.input3D[1].input3Dy',f=True)
	mc.connectAttr(addHeightNode+'.output3D',hDimension+'.endPoint',f=True)
	
	# Width
	mc.connectAttr(geo+'.boundingBoxMin',wDimension+'.startPoint',f=True)
	addWidthNode = mc.createNode('plusMinusAverage',n=geo+'_width_plusMinusAverage')
	mc.connectAttr(geo+'.boundingBoxMin',addWidthNode+'.input3D[0]',f=True)
	mc.connectAttr(geo+'.boundingBoxSizeX',addWidthNode+'.input3D[1].input3Dx',f=True)
	mc.connectAttr(addWidthNode+'.output3D',wDimension+'.endPoint',f=True)
	
	# Depth
	mc.connectAttr(geo+'.boundingBoxMin',dDimension+'.startPoint',f=True)
	addDepthNode = mc.createNode('plusMinusAverage',n=geo+'_depth_plusMinusAverage')
	mc.connectAttr(geo+'.boundingBoxMin',addDepthNode+'.input3D[0]',f=True)
	mc.connectAttr(geo+'.boundingBoxSizeZ',addDepthNode+'.input3D[1].input3Dz',f=True)
	mc.connectAttr(addDepthNode+'.output3D',dDimension+'.endPoint',f=True)
	
	# Delete unused locators
	if del_locs: mc.delete(del_locs)
	
	# Return result
	return measure_grp

# ==================
# - Check Polygons -
# ==================

def getMeshList(meshList=[]):
	'''
	Return a list of mesh objects to be used in the poly check scripts
	'''
	# If meshList is empty, use selection
	if not meshList:
		meshList = [mesh for mesh in mc.ls(sl=True) if glTools.utils.mesh.isMesh(mesh)]
	# If meshList is empty, use all non intermediate meshes in the scene
	if not meshList:
		meshList = [mc.listRelatives(i,p=True)[0] for i in mc.ls(type='mesh',ni=True)]
	# If meshList is empty, return empty list
	if not meshList: meshList = []
	
	# Retrun result
	return meshList

def nonQuads(meshList=[]):
	'''
	Return a list of all non 4-sided polygon faces in a specified list of meshes.
	@param meshList: List of meshes to check for non quads
	@type meshList: list
	'''
	# Check meshList
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Initialize return list
	nonQuadList = []
	
	# Find non quads
	for mesh in meshList:
		
		# Select mesh
		mc.select(mesh)
		# Select quads
		mm.eval('polyCleanupArgList 3 {"0","2","1","1","0","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0"}')
		# Check selection
		if not mc.filterExpand(ex=True,sm=34): continue
		# Invert selection
		mm.eval('InvertSelection')
		# Append return list
		nonQuads = mc.filterExpand(ex=True,sm=34)
		if nonQuads: nonQuadList.extend(nonQuads)
	
	# Set selection
	mc.select(meshList)
	
	# Return result
	if not nonQuadList: nonQuadList = []
	return nonQuadList

def nSidedPolys(meshList=[]):
	'''
	Return a list of all polygon faces with more than 4 sides in a specified list of meshes.
	@param meshList: List of meshes to check for n-sided polys
	@type meshList: list
	'''
	# Check meshList
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Initialize return list
	nSidedList = []
	
	# Find n-sided polys
	for mesh in meshList:
		
		# Select mesh
		mc.select(mesh)
		# Select quads
		mm.eval('polyCleanupArgList 3 {"0","2","1","0","1","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0"}')
		# Check selection
		if not mc.filterExpand(ex=True,sm=34): continue
		# Append return list
		nSided = mc.filterExpand(ex=True,sm=34)
		if nSided: nSidedList.extend(nSided)
	
	# Set selection
	mc.select(meshList)
	
	# Return result
	if not nSidedList: nSidedList = []
	return nSidedList

def unlockNormals(meshList=[]):
	'''
	'''
	# Check meshList
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Unlock Normals
	for mesh in meshList: mc.polyNormalPerVertex(mesh,ufn=True)
	
	# Return result
	return meshList

def checkNonManifold(meshList=[]):
	'''
	Check for non manifold geometry
	@param meshList: List of meshes to check for non manifold topology. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Find non manofold geometry
	nonManifoldList = glTools.utils.mesh.polyCleanup(meshList,nonManifold=True)
	if not nonManifoldList: return []
	
	# Return result
	return nonManifoldList

def checkLamina(meshList=[]):
	'''
	Check for non manifold geometry
	@param meshList: List of meshes to check for lamina faces. If empty, check all mesh objects in the scene.
	@type meshList: list
	'''
	# Find lamina faces
	laminaFaceList = glTools.utils.mesh.polyCleanup(meshList,laminaFace=True)
	if not laminaFaceList: return []
	
	# Return result
	return laminaFaceList
	
# ================
# - Normal Check -
# ================

def normalCheck(meshList=[]):
	'''
	Setup normal check properties for a specified list of meshes.
	@param meshList: List of meshes to setup normal check for
	@type meshList: list
	'''
	# Check meshList
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Check normal shader
	normalSG = 'normalCheckSG'
	normalShader = 'normalCheckShader'
	if not mc.objExists(normalShader):
		# Create Shader
		normalShader = mc.shadingNode('lambert',asShader=True,n=normalShader)
		normalSG = mc.sets(renderable=True,noSurfaceShader=True,empty=True,name=normalSG)
		mc.connectAttr(normalShader+'.outColor',normalSG+'.surfaceShader',f=True)
		mc.setAttr(normalShader+'.color',0,0,0)
		mc.setAttr(normalShader+'.incandescence',1,0,0)
	
	# Setup normal check
	for mesh in meshList:
		
		# Clear selection
		mc.select(cl=True)
		
		# Turn on double sided
		mc.setAttr(mesh+'.doubleSided',1)
		
		# Extrude face
		numFace = mc.polyEvaluate(mesh,f=True)
		polyExtrude = mc.polyExtrudeFacet(mesh+'.f[0:'+str(numFace)+']',ch=1,kft=True,pvt=(0,0,0),divisions=2,twist=0,taper=1,off=0,smoothingAngle=30)
		mm.eval('PolySelectTraverse 1')
		extrudeFaceList = mc.filterExpand(ex=True,sm=34)
		mc.setAttr(polyExtrude[0]+'.localTranslateZ',-0.001)
		
		# Apply shader
		mc.sets(extrudeFaceList,fe=normalSG)
	
	# Set selection
	mc.select(meshList)
	
	# Retrun result
	return meshList

def normalCheckRemove(meshList=[]):
	'''
	Remove normal check properties for a specified list of meshes.
	@param meshList: List of meshes to removes normal check from
	@type meshList: list
	'''
	# Check meshList
	meshList = getMeshList(meshList)
	if not meshList: return []
	
	# Remove normal check
	for mesh in meshList:
		
		# Clear selection
		mc.select(cl=True)
		
		# Turn off double sided
		mc.setAttr(mesh+'.doubleSided',0)
		
		# Remove extrude face
		polyExtrude = mc.ls(mc.listHistory(mesh),type='polyExtrudeFace')
		if polyExtrude: mc.delete(polyExtrude)
		
		# Delete history
		mc.delete(mesh,ch=True)
		
		# Apply initial shading group
		mc.sets(mesh,fe='initialShadingGroup')
		
	# Check normalShader members
	normalSG = 'normalCheckSG'
	normalShader = 'normalCheckShader'
	if not mc.sets(normalSG,q=True): mc.delete(normalShader,normalSG)
	
	# Set selection
	mc.select(meshList)
	
	# Retrun result
	return meshList
