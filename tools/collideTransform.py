import maya.cmds as mc

import glTools.utils.stringUtils
import glTools.utils.surface
import glTools.utils.transform

def sphereCollideTransform():
	pass

def cylinerCollideTransform():
	pass

def planeCollideTransform(	targetTransform,
							collidePlane		= None,
							collideTransform	= None,
							offsetFalloff		= None,
							distanceFalloff		= None,
							distanceAxis		= 'XY',
							prefix				= None ):
	'''
	Setup a plane collide transform.
	Setup includes smooth offset falloff, distance falloff and collide weight attributes.
	Collision is based on the +Z axis of the collide plane transform.
	@param targetTransform: Target transform (or locator) that the collide transform will follow.
	@type targetTransform: str
	@param collidePlane: Collision plane transform. If None, creant new renderRect plane.
	@type collidePlane: str or None
	@param collideTransform: Collide transform that will collide with the plane. If None, creant new locator.
	@type collideTransform: str or None
	@param offsetFalloff: Calculate collision offset falloff. Offset falloff is calculated as collision local Z distance.
	@type offsetFalloff: float or None
	@param distanceFalloff: Calculate collision distance falloff. Distance falloff is calculated as collision local XY distance.
	@type distanceFalloff: float or None
	@param distanceAxis: Calculate collision distance falloff. Distance falloff is calculated as collision local XY distance.
	@type distanceAxis: float or None
	@param prefix: Naming prefix. If None, extracted from targetTransform
	@type prefix: str or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target Transforms
	if not mc.objExists(targetTransform):
		raise Exception('Target transform "'+targetTransform+'" does not exist!')
	if not glTools.utils.transform.isTransform(targetTransform):
		raise Exception('Object "'+targetTransform+'" is not a valid transform!')
	
	# Check Collide Plane
	if collidePlane:
		if not mc.objExists(str(collidePlane)):
			raise Exception('Collide plane "'+collidePlane+'" does not exist!')
		if not glTools.utils.transform.isTransform(collidePlane):
			raise Exception('Object "'+collidePlane+'" is not a valid transform!')
	
	# Check Collide Transforms
	if collideTransform:
		if not mc.objExists(str(collideTransform)):
			raise Exception('Collide transform "'+collideTransform+'" does not exist!')
		if not glTools.utils.transform.isTransform(collideTransform):
			raise Exception('Object "'+collideTransform+'" is not a valid transform!')
	
	# Check Distance Axis
	if distanceAxis: distanceAxis = distanceAxis.upper()
	
	# Check Prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(targetTransform)
	
	# ===================
	# - Build Collision -
	# ===================
	
	# Build Collide Objects
	if not collideTransform:
		collideTransform = mc.spaceLocator(n=prefix+'_collide_loc')[0]
	if not collidePlane:
		collidePlaneShape = mc.createNode('renderRect')
		collidePlane = mc.listRelatives(collidePlaneShape,p=True)[0]
		collidePlane = mc.rename(collidePlane,prefix+'_collide_plane')
	
	# Add Collide Attributes
	if not mc.attributeQuery('collideWeight',n=collidePlane,ex=True):
		mc.addAttr(collidePlane,ln='collideWeight',min=0,max=1,dv=1,k=True)
	
	# Build Collide Nodes
	collideCondition = mc.createNode('condition',n=prefix+'_collide_condition')
	collideBlend = mc.createNode('blendColors',n=prefix+'_collideWeight_blendColors')
	worldToCollide = mc.createNode('vectorProduct',n=prefix+'_worldToCollide_vectorProduct')
	mc.setAttr(worldToCollide+'.operation',4) # Point Matrix Product
	collideToWorld = mc.createNode('vectorProduct',n=prefix+'_collideToWorld_vectorProduct')
	mc.setAttr(collideToWorld+'.operation',4) # Point Matrix Product
	worldToLocal = mc.createNode('vectorProduct',n=prefix+'_worldToLocal_vectorProduct')
	mc.setAttr(worldToLocal+'.operation',4) # Point Matrix Product
	
	# =========================
	# - Build Collide Network -
	# =========================
	
	# World To Collide
	mc.connectAttr(collidePlane+'.worldInverseMatrix[0]',worldToCollide+'.matrix',f=True)
	if mc.objExists(targetTransform+'.worldPosition[0]'):
		mc.connectAttr(targetTransform+'.worldPosition[0]',worldToCollide+'.input1',f=True)
	else:
		localToWorld = mc.createNode('vectorProduct',n=prefix+'_localToWorld_vectorProduct')
		mc.setAttr(localToWorld+'.operation',4) # Point Matrix Product
		mc.connectAttr(targetTransform+'.worldMatrix[0]',localToWorld+'.matrix',f=True)
		mc.connectAttr(localToWorld+'.output',worldToCollide+'.input1',f=True)
	
	# Collide Condition
	mc.connectAttr(worldToCollide+'.outputZ',collideCondition+'.firstTerm',f=True)
	mc.setAttr(collideCondition+'.secondTerm',0)
	mc.setAttr(collideCondition+'.operation',2) # Greater Than
	mc.connectAttr(worldToCollide+'.output',collideCondition+'.colorIfTrue',f=True)
	mc.connectAttr(worldToCollide+'.outputX',collideCondition+'.colorIfFalseR',f=True)
	mc.connectAttr(worldToCollide+'.outputY',collideCondition+'.colorIfFalseG',f=True)
	mc.setAttr(collideCondition+'.colorIfFalseB',0)
	
	# Collide Weight Blend
	mc.connectAttr(collideCondition+'.outColor',collideBlend+'.color1',f=True)
	mc.connectAttr(worldToCollide+'.output',collideBlend+'.color2',f=True)
	mc.connectAttr(collidePlane+'.collideWeight',collideBlend+'.blender',f=True)
	
	# Collide To World
	mc.connectAttr(collideBlend+'.output',collideToWorld+'.input1',f=True)
	mc.connectAttr(collidePlane+'.worldMatrix[0]',collideToWorld+'.matrix',f=True)
	
	# World To Local
	mc.connectAttr(collideToWorld+'.output',worldToLocal+'.input1',f=True)
	mc.connectAttr(collideTransform+'.parentInverseMatrix[0]',worldToLocal+'.matrix',f=True)
	
	# Connect Output
	mc.connectAttr(worldToLocal+'.output',collideTransform+'.translate',f=True)
	
	# ============================
	# - Calculate Offset Falloff -
	# ============================
	
	if offsetFalloff != None:
		
		# Add Collide Attributes
		if not mc.attributeQuery('offsetFalloff',n=collidePlane,ex=True):
			mc.addAttr(collidePlane,ln='offsetFalloff',min=0,dv=0.5,k=True)
		
		# Build Nodes
		falloffRemap = mc.createNode('remapValue',n=prefix+'_offsetFalloff_remapValue')
		falloffMult = mc.createNode('multDoubleLinear',n=prefix+'_offsetFalloff_multDoubleLinear')
		
		# Falloff Remap
		mc.connectAttr(worldToCollide+'.outputZ',falloffRemap+'.inputValue',f=True)
		mc.connectAttr(collidePlane+'.offsetFalloff',falloffRemap+'.inputMax',f=True)
		mc.connectAttr(collidePlane+'.offsetFalloff',falloffRemap+'.outputMax',f=True)
		mc.connectAttr(collidePlane+'.offsetFalloff',falloffMult+'.input1',f=True)
		mc.setAttr(falloffMult+'.input2',-1)
		mc.connectAttr(falloffMult+'.output',falloffRemap+'.inputMin',f=True)
		
		# Override Collide Condition
		mc.connectAttr(collidePlane+'.offsetFalloff',collideCondition+'.secondTerm',f=True)
		mc.connectAttr(falloffRemap+'.outValue',collideCondition+'.colorIfFalseB',f=True)
		
		# Set Offset Falloff
		mc.setAttr(collidePlane+'.offsetFalloff',abs(offsetFalloff))
	
	# ==============================
	# - Calculate Distance Falloff -
	# ==============================
	
	if distanceFalloff != None:
		
		# Add Collide Attributes
		if not mc.attributeQuery('distanceFalloff',n=collidePlane,ex=True):
			mc.addAttr(collidePlane,ln='distanceFalloff',min=0,dv=1,k=True)
		
		# Distance Remap
		distRemap = mc.createNode('remapValue',n=prefix+'_collideDist_remapValue')
		mc.connectAttr(collidePlane+'.distanceFalloff',distRemap+'.inputMax',f=True)
		mc.setAttr(distRemap+'.outputMin',1)
		mc.setAttr(distRemap+'.outputMax',0)
		mc.setAttr(distRemap+'.inputMin',0)
		
		# Distance Falloff
		collideDist = mc.createNode('distanceBetween',n=prefix+'_collideDist_distanceBetween')
		if len(distanceAxis) == 1:
			mc.connectAttr(worldToCollide+'.output'+distanceAxis[0],collideDist+'.point1X',f=True)
		elif len(distanceAxis) == 2:
			mc.connectAttr(worldToCollide+'.output'+distanceAxis[0],collideDist+'.point1X',f=True)
			mc.connectAttr(worldToCollide+'.output'+distanceAxis[1],collideDist+'.point1Y',f=True)
		else:
			raise Exception('Invalid collision distance axis! ('+str(distanceAxis)+')')
		mc.connectAttr(collideDist+'.distance',distRemap+'.inputValue',f=True)
		
		# Distance Weight
		distMult = mc.createNode('multDoubleLinear',n=prefix+'_distanceWeight_multDoubleLinear')
		mc.connectAttr(collidePlane+'.collideWeight',distMult+'.input1',f=True)
		mc.connectAttr(distRemap+'.outValue',distMult+'.input2',f=True)
		mc.connectAttr(distMult+'.output',collideBlend+'.blender',f=True)
		
		# Set Distance Falloff
		mc.setAttr(collidePlane+'.distanceFalloff',abs(distanceFalloff))
	
	# =================
	# - Return Result -
	# =================
	
	return [collidePlane,collideTransform]

def doublePlaneCollideTransform(	targetTransform,
									collidePlane1=None,
									collidePlane2=None,
									collideTransform=None,
									offsetFalloff=None,
									distanceFalloff=None,
									distanceAxis='XY',
									prefix=None):
	'''
	Setup a plane collide transform.
	Setup includes smooth offset falloff, distance falloff and collide weight attributes.
	Collision is based on the +Z axis of the collide plane transform.
	@param targetTransform: Target transform (or locator) that the collide transform will follow.
	@type targetTransform: str
	@param collidePlane1: Collision plane 1 transform. If None, creant new renderRect plane.
	@type collidePlane1: str or None
	@param collidePlane2: Collision plane 2 transform. If None, creant new renderRect plane.
	@type collidePlane2: str or None
	@param collideTransform: Collide transform that will collide with the plane. If None, creant new locator.
	@type collideTransform: str or None
	@param offsetFalloff: Calculate collision offset falloff. Offset falloff is calculated as collision local Z distance.
	@type offsetFalloff: float or None
	@param distanceFalloff: Calculate collision distance falloff. Distance falloff is calculated as collision local XY distance.
	@type distanceFalloff: float or None
	@param prefix: Naming prefix. If None, extracted from targetTransform
	@type prefix: str or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target Transforms
	if not mc.objExists(targetTransform):
		raise Exception('Target transform "'+targetTransform+'" does not exist!')
	if not glTools.utils.transform.isTransform(targetTransform):
		raise Exception('Object "'+targetTransform+'" is not a valid transform!')
	
	# Check Collide Transforms
	if collideTransform and not mc.objExists(str(collideTransform)):
		raise Exception('Collide transform "'+collideTransform+'" does not exist!')
	if not glTools.utils.transform.isTransform(collideTransform):
		raise Exception('Object "'+collideTransform+'" is not a valid transform!')
	
	# Check Collide Plane
	if collidePlane and not mc.objExists(str(collidePlane)):
		raise Exception('Collide plane "'+collidePlane+'" does not exist!')
	if not glTools.utils.transform.isTransform(collidePlane):
		raise Exception('Object "'+collidePlane+'" is not a valid transform!')
	
	# Check Distance Axis
	if distanceAxis: distanceAxis = distanceAxis.upper()
	
	# Check Prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(targetTransform)
	
	# ===================
	# - Build Collision -
	# ===================
	
	# Build Collide Objects
	if not collideTransform:
		collideTransform = mc.spaceLocator(n=prefix+'_collide_loc')[0]
	if not collidePlane:
		collidePlaneShape = mc.createNode('renderRect')
		collidePlane = mc.listRelatives(collidePlaneShape,p=True)[0]
		collidePlane = mc.rename(collidePlane,prefix+'_collide_plane')
	
	# Add Collide Attributes
	if not mc.attributeQuery('collideWeight',n=collidePlane,ex=True):
		mc.addAttr(collidePlane,ln='collideWeight',min=0,max=1,dv=1,k=True)
	
	# Build Collide Nodes
	collideCondition = mc.createNode('condition',n=prefix+'_collide_condition')
	collideBlend = mc.createNode('blendColors',n=prefix+'_collideWeight_blendColors')
	worldToCollide = mc.createNode('vectorProduct',n=prefix+'_worldToCollide_vectorProduct')
	mc.setAttr(worldToCollide+'.operation',4) # Point Matrix Product
	collideToWorld = mc.createNode('vectorProduct',n=prefix+'_collideToWorld_vectorProduct')
	mc.setAttr(collideToWorld+'.operation',4) # Point Matrix Product
	worldToLocal = mc.createNode('vectorProduct',n=prefix+'_worldToLocal_vectorProduct')
	mc.setAttr(worldToLocal+'.operation',4) # Point Matrix Product
	
	# =========================
	# - Build Collide Network -
	# =========================
	
	# World To Collide
	mc.connectAttr(collidePlane+'.worldInverseMatrix[0]',worldToCollide+'.matrix',f=True)
	if mc.objExists(targetTransform+'.worldPosition[0]'):
		mc.connectAttr(targetTransform+'.worldPosition[0]',worldToCollide+'.input1',f=True)
	else:
		localToWorld = mc.createNode('vectorProduct',n=prefix+'_localToWorld_vectorProduct')
		mc.setAttr(localToWorld+'.operation',4) # Point Matrix Product
		mc.connectAttr(targetTransform+'.worldMatrix[0]',localToWorld+'.matrix',f=True)
		mc.connectAttr(localToWorld+'.output',worldToCollide+'.input1',f=True)
	
	# Collide Condition
	mc.connectAttr(worldToCollide+'.outputZ',collideCondition+'.firstTerm',f=True)
	mc.setAttr(collideCondition+'.secondTerm',0)
	mc.setAttr(collideCondition+'.operation',2) # Greater Than
	mc.connectAttr(worldToCollide+'.output',collideCondition+'.colorIfTrue',f=True)
	mc.connectAttr(worldToCollide+'.outputX',collideCondition+'.colorIfFalseR',f=True)
	mc.connectAttr(worldToCollide+'.outputY',collideCondition+'.colorIfFalseG',f=True)
	mc.setAttr(collideCondition+'.colorIfFalseB',0)
	
	# Collide Weight Blend
	mc.connectAttr(collideCondition+'.outColor',collideBlend+'.color1',f=True)
	mc.connectAttr(worldToCollide+'.output',collideBlend+'.color2',f=True)
	mc.connectAttr(collidePlane+'.collideWeight',collideBlend+'.blender',f=True)
	
	# Collide To World
	mc.connectAttr(collideBlend+'.output',collideToWorld+'.input1',f=True)
	mc.connectAttr(collidePlane+'.worldMatrix[0]',collideToWorld+'.matrix',f=True)
	
	# World To Local
	mc.connectAttr(collideToWorld+'.output',worldToLocal+'.input1',f=True)
	mc.connectAttr(collideTransform+'.parentInverseMatrix[0]',worldToLocal+'.matrix',f=True)
	
	# Connect Output
	mc.connectAttr(worldToLocal+'.output',collideTransform+'.translate',f=True)
	
	# ============================
	# - Calculate Offset Falloff -
	# ============================
	
	if offsetFalloff != None:
		
		# Add Collide Attributes
		if not mc.attributeQuery('offsetFalloff',n=collidePlane,ex=True):
			mc.addAttr(collidePlane,ln='offsetFalloff',min=0,dv=0.5,k=True)
		
		# Build Nodes
		falloffRemap = mc.createNode('remapValue',n=prefix+'_offsetFalloff_remapValue')
		falloffMult = mc.createNode('multDoubleLinear',n=prefix+'_offsetFalloff_multDoubleLinear')
		
		# Falloff Remap
		mc.connectAttr(worldToCollide+'.outputZ',falloffRemap+'.inputValue',f=True)
		mc.connectAttr(collidePlane+'.offsetFalloff',falloffRemap+'.inputMax',f=True)
		mc.connectAttr(collidePlane+'.offsetFalloff',falloffRemap+'.outputMax',f=True)
		mc.connectAttr(collidePlane+'.offsetFalloff',falloffMult+'.input1',f=True)
		mc.setAttr(falloffMult+'.input2',-1)
		mc.connectAttr(falloffMult+'.output',falloffRemap+'.inputMin',f=True)
		
		# Override Collide Condition
		mc.connectAttr(collidePlane+'.offsetFalloff',collideCondition+'.secondTerm',f=True)
		mc.connectAttr(falloffRemap+'.outValue',collideCondition+'.colorIfFalseB',f=True)
		
		# Set Offset Falloff
		mc.setAttr(collidePlane+'.offsetFalloff',abs(offsetFalloff))
	
	# ==============================
	# - Calculate Distance Falloff -
	# ==============================
	
	if distanceFalloff != None:
		
		# Add Collide Attributes
		if not mc.attributeQuery('distanceFalloff',n=collidePlane,ex=True):
			mc.addAttr(collidePlane,ln='distanceFalloff',min=0,dv=1,k=True)
		
		# Distance Remap
		distRemap = mc.createNode('remapValue',n=prefix+'_collideDist_remapValue')
		mc.connectAttr(collidePlane+'.distanceFalloff',distRemap+'.inputMax',f=True)
		mc.setAttr(distRemap+'.outputMin',1)
		mc.setAttr(distRemap+'.outputMax',0)
		mc.setAttr(distRemap+'.inputMin',0)
		
		# Distance Falloff
		collideDist = mc.createNode('distanceBetween',n=prefix+'_collideDist_distanceBetween')
		if len(distanceAxis) == 1:
			mc.connectAttr(worldToCollide+'.output'+distanceAxis[0],collideDist+'.point1X',f=True)
		elif len(distanceAxis) == 2:
			mc.connectAttr(worldToCollide+'.output'+distanceAxis[0],collideDist+'.point1X',f=True)
			mc.connectAttr(worldToCollide+'.output'+distanceAxis[1],collideDist+'.point1Y',f=True)
		else:
			raise Exception('Invalid collision distance axis! ('+str(distanceAxis)+')')
		mc.connectAttr(collideDist+'.distance',distRemap+'.inputValue',f=True)
		
		# Distance Weight
		distMult = mc.createNode('multDoubleLinear',n=prefix+'_distanceWeight_multDoubleLinear')
		mc.connectAttr(collidePlane+'.collideWeight',distMult+'.input1',f=True)
		mc.connectAttr(distRemap+'.outValue',distMult+'.input2',f=True)
		mc.connectAttr(distMult+'.output',collideBlend+'.blender',f=True)
		
		# Set Distance Falloff
		mc.setAttr(collidePlane+'.distanceFalloff',abs(distanceFalloff))
	
	# =================
	# - Return Result -
	# =================
	
	return

def surfaceCollideTransform(targetTransform,slaveTransform,collideSurface,inside=True,prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(targetTransform):
		raise Exception('Target transform "'+targetTransform+'" does not exist!')
	if not mc.objExists(slaveTransform):
		raise Exception('Slave transform "'+slaveTransform+'" does not exist!')
	if not mc.objExists(collideSurface):
		raise Exception('Collide surface "'+collideSurface+'" does not exist!')
	if not glTools.utils.surface.isSurface(collideSurface):
		raise Exception('Collide object "'+collideSurface+'" is not a valid NURBS surface!')
	
	if not prefix: prefix = 'collideSurface'
	
	# ===================
	# - Create Locators -
	# ===================
	
	slave_loc = mc.spaceLocator(n=slaveTransform+'_loc')[0]
	target_loc = mc.spaceLocator(n=targetTransform+'_loc')[0]
	target_ptCon = mc.pointConstraint(targetTransform,target_loc)[0]
	
	# - Setup -
	con = mc.createNode('condition',n=prefix+'_condition')
	vp = mc.createNode('vectorProduct',n=prefix+'_vectorProduct')
	pma = mc.createNode('plusMinusAverage',n=prefix+'_plusMinusAverage')
	posi = mc.createNode('pointOnSurfaceInfo',n=prefix+'_pointOnSurfaceInfo')
	cpos = mc.createNode('closestPointOnSurface',n=prefix+'_closestPointOnSurface')
	
	# Surface Connect
	mc.connectAttr(collideSurface+'.worldSpace[0]',posi+'.inputSurface',f=True)
	mc.connectAttr(collideSurface+'.worldSpace[0]',cpos+'.inputSurface',f=True)
	mc.connectAttr(target_loc+'.worldPosition[0]',cpos+'.inPosition',f=True)
	
	# Parameter Connect
	mc.connectAttr(cpos+'.parameterU',posi+'.parameterU',f=True)
	mc.connectAttr(cpos+'.parameterV',posi+'.parameterV',f=True)
	
	# Offset Calc
	mc.setAttr(pma+'.operation',2) # SUBTRACT
	mc.connectAttr(target_loc+'.worldPosition[0]',pma+'.input3D[0]',f=True)
	mc.connectAttr(cpos+'.position',pma+'.input3D[1]',f=True)
	
	# Dot Product
	mc.setAttr(vp+'.operation',1) # DOT PRODUCT
	mc.connectAttr(posi+'.normal',vp+'.input1',f=True)
	mc.connectAttr(pma+'.output3D',vp+'.input2',f=True)
	
	# Condition
	if inside: mc.setAttr(con+'.operation',2) # Greater Than
	else: mc.setAttr(con+'.operation',4) # Less Than
	mc.setAttr(con+'.firstTerm',0.0)
	mc.connectAttr(vp+'.outputX',con+'.secondTerm',f=True)
	mc.connectAttr(target_loc+'.worldPosition[0]',con+'.colorIfTrue',f=True)
	mc.connectAttr(cpos+'.position',con+'.colorIfFalse',f=True)
	
	# Output
	mc.connectAttr(con+'.outColor',slave_loc+'.t',f=True)

	return target_loc, slave_loc
