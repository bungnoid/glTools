import maya.mel as mm
import maya.cmds as mc

import glTools.utils.blendShape
import glTools.utils.dnpublish
import glTools.utils.mesh
import glTools.utils.skinCluster

import glTools.tools.shapeExtract
import glTools.tools.measureMeshDistance
import glTools.tools.barycentricPointWeight

def measureAttach(measureList,baseMesh,detachList=[]):
	'''
	Attach each measurement specified in measureList to the baseMesh
	@param measureList: List of measurements to attach
	@type measureList: list
	@param baseMesh: Mesh to attach measurements to
	@type baseMesh: str
	@param detachList: List of attachement points to leave detached
	@type detachList: list
	'''
	# Attach measuremenst
	for measure in measureList:
		
		# Constrain to mesh
		meshConn = glTools.tools.measureMeshDistance.constrainMeasure(measure,baseMesh)
		
		# Add distance attrs
		distAttr = glTools.tools.measureMeshDistance.addDistanceAttrs(measure,baseMesh)
		
	# Delete unused measure attachments
	for obj in detachList:
		
		# Get measure point constraint
		meshCon = mc.listConnections(obj,type='dnMeshConstraint')
		if meshCon: mc.delete(meshCon)


def extractExpressionRegions(char,deleteHistory=True,rebuildDeltas=False):
	'''
	Extract expression delta regions based on imported regions definitions.
	@param char: The character to extract expression deltas for
	@type char: str
	@param deleteHistory: Delete (or keep) blendShape history for region extraction
	@type deleteHistory: bool
	@param rebuildDeltas: Rebuild deltas to retained model history. Deltas regenerated as the difference between the expression rigBase and scult shapes.
	@type rebuildDeltas: bool
	'''
	# ---------------------------
	# - Define constant strings -
	# ---------------------------
	face_mesh_grp = 'face_mesh_group'
	face_mesh = 'face_eyeClosed_mesh'
	face_regionExtract_grp = 'face_regionExtract_grp'
	region_mesh = 'face_regionExtract_mesh'
	null_region = 'null'
	expressionGrp = 'expressions_grp'
	region_blend_mesh = 'face_expressionDelta_mesh'
	region_blendShape = 'face_expressionDelta_blendShape'
	
	# ---------------------
	# - Import Components -
	# ---------------------
	
	# Face Model
	glTools.utils.dnpublish.importFaceModel(char)
	
	# Expression Sculpts
	glTools.utils.dnpublish.importExpressionSculpts(char)
	
	# Region Definitions
	regionPath = '/jobs/JCOM/ldev_'+char.lower()+'/rig/scenes/face/expressionIntegrate/region/'+char.upper()+'_FACE_expressionRegion.mb'
	mc.file(regionPath,i=True,type='mayaBinary',rpr="_",options='v=0',pr=False)
	
	# -----------------------------------
	# - Get expression and region lists -
	# -----------------------------------
	
	# Identify expression list
	expressionList = [i.split('_')[0] for i in mc.listRelatives(expressionGrp,c=True)]
	
	# Identify region list
	regionList = mc.listRelatives(face_regionExtract_grp,c=True,type='joint')
	regionList.remove(null_region)
	
	# --------------------
	# - Reconnect Deltas -
	# --------------------
	
	# Check reconnectDeltas and deleteHistory
	if rebuildDeltas and not deleteHistory:
		
		# Iterate over expressions
		for target in expressionList:
			
			# Reset delata shape
			reset_blendShape = mc.blendShape(face_mesh,target+'_delta',n=target+'_reset_blendShape')[0]
			mc.setAttr(reset_blendShape+'.'+face_mesh,1.0)
			mc.delete(target+'_delta',ch=True)
			
			# Re-apply deltas as result of rigBase and sculpt
			delta_blendShape = mc.blendShape([target+'_rigBase',target+'_sculpt'],target+'_delta',n=target+'_delta_blendShape')[0]
			mc.setAttr(delta_blendShape+'.'+target+'_rigBase',-1.0)
			mc.setAttr(delta_blendShape+'.'+target+'_sculpt',1.0)
	
	# ------------------------------
	# - Extract Expression Regions -
	# ------------------------------
	
	# Get expression region skinCluster
	skinCluster = glTools.utils.skinCluster.findRelatedSkinCluster(region_mesh)
	
	# Perform extraction
	expressionExtractList = []
	for target in expressionList:
		extractList = glTools.tools.shapeExtract.shapeExtract_skinCluster(face_mesh,target+'_delta',skinCluster,regionList,deleteHistory,prefix=target)
		expressionExtractList += extractList
	
	# Group extractin results
	expressionExtractGrp = mc.ls(mc.listRelatives(expressionExtractList,p=True))
	expressionExtractMainGrp = mc.group(expressionExtractGrp,n='expression_extract_grp')
	
	# -------------------------------------
	# - Apply Extracted Expression Deltas -
	# -------------------------------------
	
	region_blendShape = mc.blendShape(expressionExtractList,face_mesh,n=region_blendShape)[0]
	region_blend_mesh = mc.rename(face_mesh,region_blend_mesh)
	mc.parent(region_blend_mesh,w=True)
	
	# ------------
	# - Clean up -
	# ------------
	
	# Delete face mesh group
	mc.delete('*_curveInfo')
	mc.delete('*_detachCurve')
	mc.delete(face_mesh_grp)
	
	# Delete region mesh and joints
	mc.delete(face_regionExtract_grp)
	
	# Check deleteHistory
	if deleteHistory:
	
		# Delete region extract meshes
		mc.delete(expressionExtractMainGrp)
		
		# Delete expression mesh group
		mc.delete(expressionGrp)
	
	# -----------------
	# - Return Result -
	# -----------------
	
	return region_blend_mesh

def buildExpressionRig(char):
	'''
	Build main generic expression driver rig from imported components.
	@param char: The character to build expression rig for
	@type char: str
	'''
	# ---------------------------
	# - Define constant strings -
	# ---------------------------
	
	face_mesh = 'face_mesh'
	face_expressionDelta_mesh = 'face_expressionDelta_mesh'
	shapeAdd_blendShape = 'shapeAdd_blendShape'
	targetToSwitchOff = 'shapes_face_mesh'
	
	base_prefs_null = 'base_prefs_null'
	base_prefs_attr = 'expressionShape'
	
	# ---------------------
	# - Import Components -
	# ---------------------
	
	# Expression Sculpts
	glTools.utils.dnpublish.importExpressionSculpts(char)
	
	# Expression Regions Deltas
	print('IMPORTING: '+char.upper()+' Expression Deltas')
	expressionDeltaPath = '/jobs/JCOM/ldev_'+char.lower()+'/rig/scenes/face/expressionIntegrate/expression/'+char.upper()+'_FACE_expressionDelta.mb'
	mc.file(expressionDeltaPath,i=True,type='mayaBinary',rpr="_",options='v=0',pr=False)
	
	# Measurements
	print('IMPORTING: '+char.upper()+' Face Measurements')
	measurementPath = '/jobs/JCOM/ldev_'+char.lower()+'/rig/scenes/face/expressionIntegrate/measure/'+char.upper()+'_FACE_measure.mb'
	mc.file(measurementPath,i=True,type='mayaBinary',rpr="_",options='v=0',pr=False)
	
	# ------------------------------------------
	# - Connect To Expression Delta BlendShape -
	# ------------------------------------------
	
	nextTargetIndex = glTools.utils.blendShape.nextAvailableTargetIndex(shapeAdd_blendShape)
	mc.blendShape(shapeAdd_blendShape,e=True,t=(face_mesh,nextTargetIndex,face_expressionDelta_mesh,1.0))
	mc.setAttr(shapeAdd_blendShape+'.face_expressionDelta_mesh',1)
	if mc.objExists(shapeAdd_blendShape+'.'+targetToSwitchOff):
		mc.setAttr(shapeAdd_blendShape+'.'+targetToSwitchOff,0)
	
	face_mesh_grp = mc.listRelatives(face_mesh,p=True)[0]
	mc.parent(face_expressionDelta_mesh,face_mesh_grp)
	mc.setAttr(face_expressionDelta_mesh+'.v',0)
	
	# ----------------------------
	# - Add Detail Switch to Rig -
	# ----------------------------
	
	mc.addAttr(base_prefs_null,ln=base_prefs_attr,dv=1.0,min=0.0,max=1.0)
	mc.setAttr(base_prefs_null+'.'+base_prefs_attr,1,e=True,cb=True)
	mc.connectAttr(base_prefs_null+'.'+base_prefs_attr,shapeAdd_blendShape+'.'+face_expressionDelta_mesh,f=True)

	
def rebuildExpressionsWithLatestRig(char,rigHighDetail=True):
	'''
	Rebuild expression shapes using the latest published face rig.
	@param char: The character to rebuild expression shapes for
	@type char: str
	@param rigHighDetail: Switch the face rig highDetail attribute on when rebuilding expressions
	@type rigHighDetail: bool
	'''
	
	# Rig info
	fRig_info = glTools.utils.dnpublish.faceRigPubInfo(char)
	fRig_ns = fRig_info['namespace']+'01'
	
	# Constants
	conceptGrp = 'concepts_grp'
	expressionGrp = 'expressions_grp'
	
	faceMesh = fRig_ns+':face_mesh'
	addBlendShape = fRig_ns+':shapeAdd_blendShape'
	basePrefNull = fRig_ns+':base_prefs_null'
	
	# --------------------------
	# - Import Face Components -
	# --------------------------
	
	glTools.utils.dnpublish.importFaceRig(char)
	glTools.utils.dnpublish.importExpressionSculpts(char)
	glTools.utils.dnpublish.importConceptSculpts(char)
		
	# Identify expression list
	expressionList = [i.split('_')[0] for i in mc.listRelatives(expressionGrp,c=True)]
	deltaList = [i+'_delta' for i in expressionList]
	
	# ----------------------
	# - Apply Rig Settings -
	# ----------------------
	
	# Check High detail
	if rigHighDetail:
		highDetailAttr = basePrefNull+'.highDetail'
		if mc.objExists(highDetailAttr):
			mc.setAttr(highDetailAttr,1)
	
	# Turn Off Expression Detail
	expressionDetailAttr = basePrefNull+'.expressionShape'
	if mc.objExists(expressionDetailAttr):
		mc.setAttr(expressionDetailAttr,0)
	
	# -------------------------
	# - Get Mesh Spacing Info -
	# -------------------------
	
	# Get bounding box width
	widthMin = mc.getAttr(faceMesh+'.boundingBoxMinX')
	widthMax = mc.getAttr(faceMesh+'.boundingBoxMaxX')
	width = (widthMax - widthMin) * 1.1
	
	heightMin = mc.getAttr(faceMesh+'.boundingBoxMinY')
	heightMax = mc.getAttr(faceMesh+'.boundingBoxMaxY')
	height = (heightMax - heightMin) * 1.1
	
	# ------------------------
	# - Load Expression Anim -
	# ------------------------
	
	print('LOADING: '+char.upper()+' Expression Animation')
	animPath = '/jobs/JCOM/ldev_'+char+'/rig/scenes/face/expressionIntegrate/anim/'+char.upper()+'_FACE_animExpression.anm'
	mm.eval('dnAnim -read -namespace "'+fRig_ns+':" -keyed 1 -unkeyed 1 -stripNamespaces 1 -matchMode "partialPath" -file "'+animPath+'"')
	
	# -----------------------------
	# - Extract Animation Results -
	# -----------------------------
	
	print('EXTRACTING: '+char.upper()+' Animation Results')
	
	rigBaseList = []
	animResultList = []
	
	# Duplicate and layout expression results
	for i in range(len(expressionList)):
		
		# Go to expression keyframe
		mc.currentTime(20*(i+1))
		
		# Duplicate expression result
		rigBaseNew = mc.duplicate(faceMesh,rr=True,n=expressionList[i]+'_rigBaseNEW')[0]
		
		# Shift expression mesh along the X axis
		mc.move(width*(i+1),0,0,rigBaseNew)
		
		# Get expression rigBase
		rigBase = expressionList[i]+'_rigBase'
		if mc.objExists(rigBase): rigBase = mc.rename(rigBase,rigBase+'OLD') 
		else: raise Exception('Cant find RIGBASE for '+expressionList[i]+' expression!!')
		
		# Move rigBase
		mc.move(width*(i+1),0,0,rigBase)
		
		# Append expression result lists
		rigBaseList.append(rigBase)
		animResultList.append(rigBaseNew)
	
	# Group and position expression mesh results
	rigBaseGrp = mc.group(rigBaseList,n='expression_rigBaseOLD_GRP',w=True)
	rigBaseNewGrp = mc.group(animResultList,n='expression_rigBaseNEW_GRP',w=True)
	
	mc.move(0,-height*4,0,rigBaseNewGrp)
	mc.move(0,-height*3,0,rigBaseGrp)
	
	# -----------------------
	# - Rebuild Expressions -
	# -----------------------
	
	# Add rigBase targets
	targetIndex = glTools.utils.blendShape.nextAvailableTargetIndex(addBlendShape)
	for i in range(len(deltaList)):
		mc.blendShape(addBlendShape,e=True,t=(faceMesh,targetIndex+i,deltaList[i],1.0))
	
	# ----------------------------------
	# - Set Expression Delta Keyframes -
	# ----------------------------------
	
	for i in range(len(deltaList)):
		mc.setKeyframe(addBlendShape,attribute=deltaList[i],t=(20*i),v=0.0)
		mc.setKeyframe(addBlendShape,attribute=deltaList[i],t=(20*(i+1)),v=1.0)
		mc.setKeyframe(addBlendShape,attribute=deltaList[i],t=(20*(i+2)),v=0.0)
	
	# ------------------------------
	# - Extract Expression Results -
	# ------------------------------
	
	print('EXTRACTING: '+char.upper()+' Expression Results')
	
	expressionResultList = []
	expressionSculptList = []
	expressionConceptList = []
	
	# Duplicate and layout expression results
	for i in range(len(deltaList)):
		
		# Go to expression keyframe
		mc.currentTime(20*(i+1))
		
		# Duplicate expression result
		expressionResult = mc.duplicate(faceMesh,rr=True,n=expressionList[i]+'_sculptNEW')[0]
		
		# Shift expression mesh along the X axis
		mc.move(width*(i+1),0,0,expressionResult)
		
		# Layout expression sculpt and concept
		expressionSculpt = expressionList[i]+'_sculpt'
		mc.move(width*(i+1),0,0,expressionSculpt)
		expressionConcept = expressionList[i]+'_concept'
		mc.move(width*(i+1),0,0,expressionConcept)
		
		# Append expression result lists
		expressionResultList.append(expressionResult)
		expressionSculptList.append(expressionSculpt)
		expressionConceptList.append(expressionConcept)
		
	# Group and position expression mesh results
	expressionResultGrp = mc.group(expressionResultList,n='expression_sculptNEW_GRP',w=True)
	expressionSculptGrp = mc.group(expressionSculptList,n='expression_sculptOLD_GRP',w=True)
	expressionConceptGrp = mc.group(expressionConceptList,n='expression_concept_GRP',w=True)
	
	mc.move(0,height,0,expressionConceptGrp)
	mc.move(0,-height,0,expressionSculptGrp)
	
	# ------------------------
	# - Reapply Rig Settings -
	# ------------------------
	
	# Turn On Expression Detail
	expressionDetailAttr = basePrefNull+'.expressionShape'
	if mc.objExists(expressionDetailAttr):
		mc.setAttr(expressionDetailAttr,1)
	
	# -----------
	# - Cleanup -
	# -----------
	
	# Move and hide expression and concept group
	mc.move(-width,0,0,expressionGrp)
	mc.setAttr(expressionGrp+'.v',0)
	mc.move(-width*2,0,0,conceptGrp)
	mc.setAttr(conceptGrp+'.v',0)
	
	print('COMPLETED: '+char.upper()+' Expression Update')


def replaceExpressionDeltaMesh(namespace='TARSFACEa01:'):
	'''
	Override expression delta connection to new input mesh.
	Useful for connecting history bound expression targets to the rig for editing.
	@param namespace: Namespace of the rig to connect new input mesh to
	@type namespace: str
	'''
	# --------------------------
	# - Define variable values -
	# --------------------------
	
	face_mesh = namespace+'face_mesh'
	blendShape = namespace+'shapeAdd_blendShape'
	target = 'face_expressionDelta_mesh'
	target_mesh = 'face_expressionDelta_mesh'
	sourceBlendShape = namespace+'face_expressionDelta_blendShape'
	targetBlendShape = 'face_expressionDelta_blendShape'
	
	# -----------------------------------------
	# - Replace blendShape connection to face -
	# -----------------------------------------
	
	glTools.utils.blendShape.connectToTarget(blendShape,target_mesh,target,face_mesh,1.0,force=True)
	
	# ----------------------------------
	# - Replace blendShape connections -
	# ----------------------------------
	
	connectionList = mc.listConnections(sourceBlendShape+'.w',s=True,p=True,c=True)
	for i in range(0,len(connectionList),2):
		targetPlug = connectionList[i].replace(sourceBlendShape,targetBlendShape)
		mc.connectAttr(connectionList[i+1],targetPlug,f=True)

def barycentricPointWeightSetup(samplePt,targetList,calcList=[True,True,True],prefix=''):
	'''
	Create pointSampleWeight setup for driving up to 3 target region shapes
	@param samplePoint: The point to track between target points
	@type samplePoint: str
	@param targetList: List of meshes that define the target vertex positions
	@type targetList: list
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# Checks
	if not mc.objExists(samplePt):
		raise Exception('Sample point "'+samplePt+'" does not exist!!')
	if not mc.objExists(samplePt+'.vtx'):
		raise Exception('Sample point "'+samplePt+'" has not target vertex attribute (".vtx")!!')
	for target in targetList:
		if not mc.objExists(target):
			raise Exception('Target mesh "'+target+'" does not exist!!')
		if not glTools.utils.mesh.isMesh(target):
			raise Exception('Target object "'+target+'" is not a valid mesh!!')
	
	# Generate target points
	vtxId = mc.getAttr(samplePt+'.vtx')
	targetLoc = []
	for target in targetList:
		targetSuffix = target.split('_')[-1]
		targetPos = mc.pointPosition(target+'.vtx['+str(vtxId)+']')
		targetLoc.append(mc.spaceLocator(n=prefix+'_'+targetSuffix+'_pnt')[0])
		mc.setAttr(targetLoc[-1]+'.t',targetPos[0],targetPos[1],targetPos[2])
	
	# Create 3PointSampleWeight setup
	pointSetup = glTools.tools.barycentricPointWeight.create(samplePt,targetLoc,calcList,prefix)
	
	# Cleanup
	mc.delete(targetLoc)
	
	# Return result
	return pointSetup # [locator list, triFace, locator_grp]


def combinationShape(attr1,attr2,invertAttr1,invertAttr2,driveAttr,prefix):
	'''
	Drive a target float attribute value based on the multiplied result of 2 source attribute values.
	@param attr1: Source attribute 1
	@type attr1: str
	@param attr2: Source attribute 2
	@type attr2: str
	@param invertAttr1: Invert source attribute 1 value
	@type invertAttr1: bool
	@param invertAttr2: Invert source attribute 2 value
	@type invertAttr2: bool
	@param driveAttr: Target attribute to connect result to
	@type driveAttr: str
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# Checks
	if not mc.objExists(attr1):
		raise Exception('Input attribute "'+attr1+'" does not exist!!')
	if not mc.objExists(attr2):
		raise Exception('Input attribute "'+attr2+'" does not exist!!')
	
	# Check Invert
	revNode = ''
	if invertAttr1 or invertAttr2:
		revNode = mc.createNode('reverse',n=prefix+'_combine_reverse')
	
	# Create comination multDoubleLinear node
	multNode = mc.createNode('multDoubleLinear',n=prefix+'_combine_multDoubleLinear')
	
	# Connect Attr 1
	if invertAttr1:
		mc.connectAttr(attr1,revNode+'.inputX',f=True)
		mc.connectAttr(revNode+'.outputX',multNode+'.input1',f=True)
	else:
		mc.connectAttr(attr1,multNode+'.input1',f=True)
	
	# Connect Attr 2
	if invertAttr2:
		mc.connectAttr(attr2,revNode+'.inputY',f=True)
		mc.connectAttr(revNode+'.outputY',multNode+'.input2',f=True)
	else:
		mc.connectAttr(attr2,multNode+'.input2',f=True)
	
	# Connect combined value to blendShape target weight
	mc.connectAttr(multNode+'.output',driveAttr,f=True)
	
	# Return result
	return (multNode+'.output')


def normalizeShapes(blendShape,targetList,prefix):
	'''
	Normalize the summed values of a list of blendShape target weights.
	@param blendShape: The blendShape to normalize target weights for
	@type blendShape: str
	@param targetList: List of target weights to normalize
	@type targetList: list
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# Check blendShape
	if not glTools.utils.blendShape.isBlendShape(blendShape):
		raise UserInputError('Object "'+blendShape+'" is not a valid blendShape deformer!')
	
	# Check targetList
	for target in targetList:
		if not mc.objExists(blendShape+'.'+target):
			raise Exception('BlendShape target "'+blendShape+'.'+target+'" does not exist!!')
	
	# Calculate combined value
	combine_pma = mc.createNode('plusMinusAverage',n=prefix+'_combinedValue_plusMinusAverage')
	for i in range(len(targetList)):
		targetConn = mc.listConnections(blendShape+'.'+targetList[i],s=True,d=False,p=True)
		mc.connectAttr(targetConn[0],combine_pma+'.input1D['+str(i)+']',f=True)
	
	# Check combined value
	combine_cond = mc.createNode('condition',n=prefix+'_combinedValue_condition')
	mc.setAttr(combine_cond+'.operation',2) # Greater Than
	mc.setAttr(combine_cond+'.secondTerm',1.0)
	mc.connectAttr(combine_pma+'.output1D',combine_cond+'.firstTerm',f=True)
	# Set Division Factor
	mc.setAttr(combine_cond+'.colorIfFalseR',1.0)
	mc.connectAttr(combine_pma+'.output1D',combine_cond+'.colorIfTrueR',f=True)
	
	# Divide each target value
	for i in range(len(targetList)):
		target_suffix = targetList[i].split('_')[-1]
		targetNorm_mdn = mc.createNode('multiplyDivide',n=prefix+'_'+target_suffix+'Normalize_multiplyDivide')
		targetConn = mc.listConnections(blendShape+'.'+targetList[i],s=True,d=False,p=True)
		mc.connectAttr(targetConn[0],targetNorm_mdn+'.input1X',f=True)
		mc.connectAttr(combine_cond+'.outColorR',targetNorm_mdn+'.input2X',f=True)
		mc.setAttr(targetNorm_mdn+'.operation',2) # Divide
		mc.connectAttr(targetNorm_mdn+'.outputX',blendShape+'.'+targetList[i],f=True)

def cleanBlendShape(blendShape,baseGeometry):
	'''
	Remove unconnected blendShape targets
	@param blendShape: The blendShape deformer to operate on
	@type blendShape: str
	@param baseGeometry: The base geometry connected to the blendShape
	@type baseGeometry: str
	'''
	# Check blendShape
	if not glTools.utils.blendShape.isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape deformer!!')
	
	# Get blendShape target list
	targetList = mc.listAttr(blendShape+'.w',m=True)
	
	# Check blendShape target connections
	deletedTargetList = []
	for target in targetList:
		targetConn = mc.listConnections(blendShape+'.'+target,s=True,d=False)
		
		# If no incoming connnections, delete target
		if not targetConn:
			try:glTools.utils.blendShape.removeTarget(blendShape,target,baseGeometry)
			except: continue
			print('Target "'+target+'" deleted!')
			deletedTargetList.append(target)
	
	# Return result
	return deletedTargetList
