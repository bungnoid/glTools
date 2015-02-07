import maya.cmds as mc

import glTools.utils.blendShape
import glTools.utils.stringUtils

def createFromSelection(origin='local',deformOrder=None,prefix=None):
	'''
	Create basic blendShape from selection.
	@param origin: Create a local or world space belndShape deformer. Accepted values - "local" or "world".
	@type origin: str
	@param deformOrder: Deformer order. Accepted values - "after", "before", "parallel", "split" or "foc".
	@type deformOrder: str or None
	@param prefix: Naming prefix
	@type prefix: str or None
	'''
	# Get Selection
	sel = mc.ls(sl=1)
	if not sel:
		print('Empty or invalid selections!')
		return None
	
	# Get Base/Target Geometry
	baseGeo = sel[-1]
	targetGeo = sel[:-1]
	
	# Get Prefix
	if not prefix: prefix = baseGeo # glTools.utils.stringUtils.stripSuffix(baseGeo)
	
	# Create BlendShape
	blendShape = glTools.utils.blendShape.create(baseGeo,targetGeo,origin,deformOrder,prefix)
	
	# Set Default Weight
	if len(targetGeo) == 1: mc.setAttr(blendShape+'.w[0]',1.0)
	
	# Return Result
	return blendShape

def endOfChainBlendShape(geo):
	'''
	Create an End Of Chain override blendShape deformer for the specified geometry.
	The override blendShape will be used to apply custom shot animation (cloth, charFX or shotSculpting) that will override the standard rig deformations.
	@param geo: The geometry to add an override blendShape deformer to.
	@type geo: str
	'''
	# Checks
	if not mc.objExists(geo):
		raise Exception('Geometry object "'+geo+'" does not exist!!')
	
	if not mc.listRelatives(geo,s=True,ni=True):
		raise Exception('Object "'+geo+'" has no valid shape children!')
	
	# Create Override BlendShapes
	blendShape = geo.split(':')[-1]+'_override_blendShape'
	if mc.objExists(blendShape):
		print('Override blendShape "'+blendShape+'" already exists! Skipping...')
	else:
		blendShape = mc.blendShape(geo,n=blendShape)[0]
		
	# Return Result
	return blendShape

def addOverrideTarget(geo,targetGeo,targetWeight=0):
	'''
	Add override blendShape target to the specified geometry.
	@param geo: The geometry to add an override blendShape target to.
	@type geo: str
	@param targetGeo: The override target geometry to add to the blendShape deformer.
	@type targetGeo: str
	@param targetWeight: The override target blend weight to apply.
	@type targetWeight: float
	'''
	# Checks
	if not mc.objExists(geo):
		raise Exception('Base geometry "'+geo+'" does not exist!!')
	if not mc.objExists(targetGeo):
		raise Exception('Target geometry "'+targetGeo+'" does not exist!!')
	
	# Get Override BlendShape
	blendShape = geo.split(':')[-1]+'_override_blendShape'
	if not mc.objExists(blendShape): blendShape = geo+'_override_blendShape'
	if not mc.objExists(blendShape):
		raise Exception('Override blendShape "'+blendShape+'" does not exist!!')
	
	# Add Target
	targetAttr = glTools.utils.blendShape.addTarget(	blendShape=blendShape,
													target=targetGeo,
													base=geo,
													targetWeight=targetWeight,
													topologyCheck=False	)
	
	# Return Result
	return targetAttr

def duplicateAndBlend(obj,parent='',search='',replace='',worldSpace=False):
	'''
	Duplicate a specified deformable object, then blendShape the duplicate to the original.
	@param obj: Object to duplicate
	@type obj: str
	@param parent: Parent transform to place the duplicate object under
	@type parent: str
	@param search: Names search string used to generate the duplicate object name 
	@type search: str
	@param replace: Names replace string used to generate the duplicate object name 
	@type replace: str
	@param worldSpace: Create the blendShape in local or world space 
	@type worldSpace: bool
	'''
	# Check object exists
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!')
	
	# Duplicate object
	dup = mc.duplicate(obj,rr=True,n=obj.replace(search,replace))[0]
	
	# Create blendShape from original to duplicate
	origin = 'local'
	if worldSpace: origin = 'world'
	blendShape = mc.blendShape(obj,dup,o=origin)[0]
	
	# Set blendShape weight
	blendAlias = mc.listAttr(blendShape+'.w',m=True)[0]
	mc.setAttr(blendShape+'.'+blendAlias,1.0)
	
	# Parent
	if parent and mc.objExists(parent):
		mc.parent(dup,parent)
	else:
		mc.parent(dup,w=True)
	
	# Return result
	return blendShape

def regenerateTarget(blendShape,target,base='',connect=False):
	'''
	Regenerate target geometry for the specified blendShape target.
	@param blendShape: BlendShape to regenerate target geometry for
	@type blendShape: str
	@param target: BlendShape target to regenerate target geometry for
	@type target: str
	@param base: BlendShape base geometry to regenerate target geometry from
	@type base: str
	@param connect: Reconnect regenerated target geometry to target input
	@type connect: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not glTools.utils.blendShape.isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape!')
	if not glTools.utils.blendShape.hasTarget(blendShape,target):
		raise Exception('BlendShape "'+blendShape+'" has no target "'+target+'"!')
	if base and not glTools.utils.blendShape.hasBase(blendShape,base):
		raise Exception('BlendShape "'+blendShape+'" has no base geometry "'+base+'"!')
	
	# Check Existing Live Target Geometry
	if glTools.utils.blendShape.hasTargetGeo(blendShape,target,base=base):
		targetGeo = glTools.utils.blendShape.getTargetGeo(blendShape,target,baseGeo=base)
		print('Target "" for blendShape "" already has live target geometry! Returning existing target geometry...')
		return targetGeo
	
	# Get Base Geometry - Default to base index [0]
	if not base: base = glTools.utils.blendShape.getBaseGeo(blendShape)[0]
	baseIndex = glTools.utils.blendShape.getBaseIndex(blendShape,base)
	
	# Get Target Index
	targetIndex = glTools.utils.blendShape.getTargetIndex(blendShape,target)
	
	# ==============================
	# - Regenerate Target Geometry -
	# ==============================
	
	# Initialize Target Geometry
	targetGeo = mc.duplicate(base,n=target)[0]
	
	# Delete Unused Shapes
	for targetShape in mc.listRelatives(targetGeo,s=True,pa=True):
		if mc.getAttr(targetShape+'.intermediateObject'):
			mc.delete(targetShape)
	
	# Get Target Deltas and Components
	wtIndex = 6000
	targetDelta = mc.getAttr(blendShape+'.inputTarget['+str(baseIndex)+'].inputTargetGroup['+str(targetIndex)+'].inputTargetItem['+str(wtIndex)+'].inputPointsTarget')
	targetComp = mc.getAttr(blendShape+'.inputTarget['+str(baseIndex)+'].inputTargetGroup['+str(targetIndex)+'].inputTargetItem['+str(wtIndex)+'].inputComponentsTarget')
	for i in xrange(len(targetComp)):
		
		# Get Component Delta
		d = targetDelta[i]
		# Apply Component Delta
		mc.move(d[0],d[1],d[2],targetGeo+'.'+targetComp[i],r=True,os=True)
	
	# Freeze Vertex Transforms
	mc.polyMoveVertex(targetGeo)
	mc.delete(targetGeo,ch=True)
	
	# ===========================
	# - Connect Target Geometry -
	# ===========================
	
	if connect: mc.connectAttr(targetGeo+'.outMesh',blendShape+'.inputTarget['+str(baseIndex)+'].inputTargetGroup['+str(targetIndex)+'].inputTargetItem['+str(wtIndex)+'].inputGeomTarget',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return targetGeo

def regenerateTargetSplits(target,base,targetSplits=[],replace=False):
	'''
	Regenerate target splits from a specified master target and base geometry.
	Each split is regenerated as a blend from the master shape, weighted (per component) based on the existing split offset.
	@param target: Target shape to regenerate target splits from
	@type target: str
	@param base: Base geometry to measure against to generate split maps.
	@type base: str
	@param targetSplits: List of target splits to regenerate.
	@type targetSplits: list
	@param replace: Replace existing splits. Otherwise, create new split geometry.
	@type replace: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	pass

def updateTargets(oldBase,newBase,targetList):
	'''
	Rebuild blendShape targets given an old and a new base geometry.
	@param oldBase: Old base geometry
	@type oldBase: str
	@param newBase: new base geometry
	@type newBase: str
	@param targetList: List of target shapes to rebuild
	@type targetList: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(oldBase):
		raise Exception('Old base geometry "'+oldBase+'" does not exist!')
	if not mc.objExists(newBase):
		raise Exception('New base geometry "'+newBase+'" does not exist!')
	if not targetList: raise Exception('Empty target list!')
	for target in targetList:
		if not mc.objExists(target):
			raise Exception('Target geometry "'+target+'" does not exist!')
	
	# ==================
	# - Update Targets -
	# ==================
	
	targetList.insert(0,newBase)
	updateBlendShape = mc.blendShape(targetList,oldBase,n='updateTargets_blendShape')[0]
	updateBlendAlias = mc.listAttr(updateBlendShape+'.w',m=True)
	
	# Generate New Targets
	for i in range(len(updateBlendAlias)):
		
		if not i:
			
			# Set New Base Target Weight (1.0)
			mc.setAttr(updateBlendShape+'.'+updateBlendAlias[i],1)
		
		else:
			
			# Set Target Weight
			mc.setAttr(updateBlendShape+'.'+updateBlendAlias[i],1)
			
			# Extract New Target from Blended Base
			newTarget = mc.duplicate(oldBase,n=updateBlendAlias[0]+'NEW')[0]
			# Delete Unused Shapes
			for shape in mc.listRelatives(newTarget,s=True,pa=True):
				if mc.getAttr(shape+'.intermediateObject'):
					mc.delete(shape)
			
			# Update Target
			targetBlendShape = mc.blendShape(newTarget,targetList[i])[0]
			targetAlias = mc.listAttr(targetBlendShape+'.w',m=True)[0]
			mc.setAttr(targetBlendShape+'.'+targetAlias,1)
			mc.delete(targetList[i],ch=True)
			mc.delete(newTarget)
			
			# Reset Target Weight
			mc.setAttr(updateBlendShape+'.'+updateBlendAlias[i],0)
	
	# ===========
	# - Cleanup -
	# ===========
	
	# Reset New Base Target Weight (0.0)
	mc.setAttr(updateBlendShape+'.'+updateBlendAlias[0],0)
	
	# Delete History (Old Base)
	#mc.delete(oldBase,ch=True)
	mc.delete(updateBlendShape)
	
	# =================
	# - Return Result -
	# =================
	
	return targetList
