import maya.mel as mm
import maya.cmds as mc

import glTools.rig.utils

import glTools.utils.attribute
import glTools.utils.base
import glTools.utils.curve
import glTools.utils.joint
import glTools.utils.lib
import glTools.utils.mesh
import glTools.utils.shape
import glTools.utils.stringUtils

import glTools.tools.autoRivet
import glTools.tools.controlBuilder
import glTools.tools.pointFaceMesh

def subControl(	parentControl,
				ctrlType,
				ctrlPosition	= [0,0,0],
				ctrlScale		= 0.5,
				prefix			= ''	):
	'''
	Create basic sub control under a specified parent control
	@param parentControl: Parent control of the sub control.
	@type parentControl: str
	@param ctrlPosition: Control shape position offset.
	@type ctrlPosition: str
	@param ctrlType: Control shape type.
	@type ctrlType: str
	@param ctrlScale: Control shape scale.
	@type ctrlScale: str
	@param prefix: Name prefix for control and created nodes.
	@type prefix: str
	'''
	# Create Control
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	ctrl = ctrlBuilder.create(	ctrlType,
								prefix+'_ctrl',
								translate	= ctrlPosition,
								scale		= ctrlScale	)
	ctrlGrp = mc.group(em=True,n=prefix+'_ctrlGrp')
	mc.parent(ctrl,ctrlGrp)
	
	# Position and Parent control
	ctrlPt = mc.xform(parentControl,q=True,ws=True,rp=True)
	mc.move(ctrlPt[0],ctrlPt[1],ctrlPt[2],ctrlGrp)
	mc.parent(ctrlGrp,parentControl)
	mc.setAttr(ctrlGrp+'.r',0,0,0)
	
	# Add Ctrl Vis Toggle
	mc.addAttr(parentControl,ln='subCtrlVis',at='enum',en=':Off:On:',dv=1)
	mc.setAttr(parentControl+'.subCtrlVis',k=False,cb=True)
	mc.connectAttr(parentControl+'.subCtrlVis',ctrlGrp+'.v',f=True)
	
	# Return Result
	result = {}
	result['ctrl'] = ctrl
	result['ctrlGrp'] = ctrlGrp
	return result

def ctrlOffsetGrp(	ctrl,
					pivot		= None,
					orientTo	= None,
					prefix		= None ):
	'''
	Create control offset group.
	Optionally, set custom pivot and orientation.
	@param ctrl: Control or control group to create offset group for.
	@type ctrl: str
	@param pivot: Transform for pivot match. If None, use control pivot.
	@type pivot: str or None
	@param orientTo: Transform for orient match. If None, use world orientation.
	@type orientTo: str or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Control
	if not mc.objExists(ctrl):
		raise Exception('Control "'+ctrl+'" does not exist!')
	
	# Pivot
	if not pivot: pivot = ctrl
	if not mc.objExists(pivot):
		raise Exception('Pivot "'+pivot+'" does not exist!')
	
	# Orient To
	if orientTo:
		if not mc.objExists(orientTo):
			raise Exception('Orient target "'+orientTo+'" does not exist!')
	
	# Prefix
	if not prefix:
		prefix = glTools.utils.stringUtils.stripSuffix(ctrl)
	
	# ======================
	# - Build Offset Group -
	# ======================
	
	# Create Offset Group
	offsetGrp = mc.group(em=True,n=prefix+'_offsetGrp')
	
	# Set Pivot
	piv = mc.xform(pivot,q=True,ws=True,rp=True)
	mc.xform(offsetGrp,ws=True,piv=piv)
	
	# Orient Offset Group
	if orientTo:
		mc.delete(mc.orientConstraint(orientTo,offsetGrp))
	
	# Parent Control
	mc.parent(ctrl,offsetGrp)
	
	# =================
	# - Return Result -
	# =================
	
	return offsetGrp

def distanceConstrainedControl(	ctrlDistPt,
								ctrlPt,
								ctrlType,
								ctrlScale,
								aimVector	= [0,0,1],
								upVector	= [0,1,0],
								upType		= 'scene',
								upObject	= '',
								prefix		= ''	):
	'''
	Create a control object that is distance constrained from a given position
	@param ctrlDistPt: Point from which the control will be distance constrained.
	@type ctrlDistPt: list or tuple
	@param ctrlPt: Control position.
	@type ctrlPt: list or tuple
	@param ctrlType: Control shape type.
	@type ctrlType: str
	@param ctrlScale: Control shape scale.
	@type ctrlScale: float
	@param aimVector: Constraint aim vector.
	@type aimVector: list or tuple
	@param upVector: Constraint upVector.
	@type upVector: list or tuple
	@param upType: Constraint upVector type. Valid types are "scene", "object", "objectrotation", "vector", or "none".
	@type upType: str
	@param upObject: Constraint upVector object.
	@type upObject: str
	@param prefix: Name prefix for control and created nodes.
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# UpVector Object
	if (upType == 'object' or upType == 'objectrotation') and not mc.objExists(upObject):
		raise Exception('UpVector transform "'+upObject+'" does not exist!')
	
	# ==================
	# - Create Control -
	# ==================
	
	ctrl = glTools.tools.controlBuilder.ControlBuilder().create(ctrlType,prefix+'_ctrl',scale=ctrlScale)
	ctrl_mvCancelGrp = mc.group(ctrl,n=prefix+'_moveCancel_grp')
	ctrlGrp = mc.group(ctrl_mvCancelGrp,n=prefix+'_ctrlGrp')
	ctrlGrpXform = mc.group(em=True,n=prefix+'_ctrlGrpXform')
	
	# =======================================
	# - Build Reference Transform Hierarchy -
	# =======================================
	
	ctrlLocalTrans = mc.spaceLocator(n=prefix+'_localTrans_loc')[0]
	ctrlLocalTransGrp = mc.group(ctrlLocalTrans,n=prefix+'_localTrans_grp')
	ctrlReferenceGrp = mc.group(ctrlLocalTransGrp,n=prefix+'_reference_grp')
	
	mc.setAttr(ctrlLocalTrans+'.localScale',0.05,0.05,0.05)
	
	# Curvature compensation
	addCurveComp= True
	if addCurveComp:
		mc.addAttr(ctrlLocalTrans,ln='curvatureX',dv=0.0,k=True)
		mc.addAttr(ctrlLocalTrans,ln='curvatureY',dv=0.0,k=True)
		curveCompNode = mc.createNode('multiplyDivide',n=prefix+'_curvature_multiplyDivide')
		mc.connectAttr(ctrlLocalTrans+'.translateX',curveCompNode+'.input1X',f=True)
		mc.connectAttr(ctrlLocalTrans+'.translateY',curveCompNode+'.input1Y',f=True)
		mc.connectAttr(ctrlLocalTrans+'.curvatureX',curveCompNode+'.input2X',f=True)
		mc.connectAttr(ctrlLocalTrans+'.curvatureY',curveCompNode+'.input2Y',f=True)
		mc.connectAttr(curveCompNode+'.outputX',ctrlLocalTransGrp+'.rotateY',f=True)
		mc.connectAttr(curveCompNode+'.outputY',ctrlLocalTransGrp+'.rotateX',f=True)
	
	# =======================
	# - Position Transforms -
	# =======================
	
	for c in [ctrlGrp,ctrlGrpXform,ctrlReferenceGrp]:
		mc.move(ctrlPt[0],ctrlPt[1],ctrlPt[2],c)
	
	# =============================
	# - Build Distance Constraint -
	# =============================
	
	# Aim Constraint
	mc.aimConstraint(	ctrlLocalTrans,
						ctrlGrpXform,
						aim	= aimVector,
						u	= upVector,
						wut	= upType,
						wuo	= upObject,
						n	= prefix+'_aimConstraint'	)
	
	# Match Rotation
	mc.setAttr(ctrlGrp+'.r',*mc.getAttr(ctrlGrpXform+'.r')[0])
	
	# ============================
	# - Build Connection Network -
	# ============================
	
	# CtrlXform -> CtrlLocalTrans
	for at in ['tx','ty']: mc.connectAttr(ctrl+'.'+at,ctrlLocalTrans+'.'+at,f=True)
	
	# CtrlGrpXform -> CtrlGrp
	for at in ['rx','ry','rz']: mc.connectAttr(ctrlGrpXform+'.'+at,ctrlGrp+'.'+at,f=True)
	
	# Translate Negation
	localTransNeg = mc.createNode('multiplyDivide',n=prefix+'_moveCancel_multiplyDivide')
	mc.connectAttr(ctrl+'.t',localTransNeg+'.input1',f=True)
	mc.setAttr(localTransNeg+'.input2',-1,-1,-1)
	mc.connectAttr(localTransNeg+'.outputX',ctrl_mvCancelGrp+'.tx',f=True)
	mc.connectAttr(localTransNeg+'.outputY',ctrl_mvCancelGrp+'.ty',f=True)
	mc.connectAttr(localTransNeg+'.outputZ',ctrl_mvCancelGrp+'.tz',f=True)
	
	# Set Pivot Positions
	mc.xform(ctrlGrpXform,ws=True,rp=ctrlDistPt)
	mc.xform(ctrlGrp,ws=True,rp=ctrlDistPt)
	
	# Match Rotation
	mc.setAttr(ctrlReferenceGrp+'.r',*mc.getAttr(ctrlGrpXform+'.r')[0])
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	result['ctrl'] = ctrl
	result['moveCancel'] = ctrl_mvCancelGrp
	result['ctrlGrp'] = ctrlGrp
	result['ctrlGrpXform'] = ctrlGrpXform
	result['ctrlLocalTrans'] = ctrlLocalTrans
	result['ctrlLocalTransGrp'] = ctrlLocalTransGrp
	result['ctrlReferenceGrp'] = ctrlReferenceGrp
	result['localTransNeg'] = localTransNeg
	
	return result

def surfaceConstrainedCtrl(	surface,
							ctrlPt,
							ctrlType,
							ctrlPosition	= [0,0,0],
							ctrlRotate		= [0,0,0],
							ctrlScale		= 1.0,
							method			= 'geometryConstraint',
							upVector		= [0,1,0],
							upType			= 'vector',
							upObject		= None,
							rayOrigin		= None,
							allowOffset		= False,
							addCurveComp	= False,
							prefix			= None ):
	'''
	Create a control object that is constrained to the surface of a specified geometry shape
	@param surface: Geometry to attach the control to.
	@type surface: str
	@param ctrlPt: Control position.
	@type ctrlPt: list or tuple
	@param ctrlType: Control shape type.
	@type ctrlType: str
	@param ctrlScale: Control shape scale.
	@type ctrlScale: float
	@param method: Surface constraint method. Accepted values are "geometryConstraint" and "rayIntersect".
	@type method: str
	@param upVector: Normal constraint upVector.
	@type upVector: list or tuple
	@param upType: Normal constraint upVector type. Valid types are "scene", "object", "objectrotation", "vector", or "none".
	@type upType: str
	@param upObject: Normal constraint upVector object.
	@type upObject: str
	@param rayOrigin: Ray origin locator.
	@type rayOrigin: str
	@param allowOffset: Allow the constraint to pull away form the guide surface.
	@type allowOffset: bool
	@param addCurveComp: Add curvature compensation attributes that will adjust reference transform orientation based on control translation.
	@type addCurveComp: bool
	@param prefix: Name prefix for control and created nodes.
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Surface
	if not mc.objExists(surface):
		raise Exception('Surface "'+surface+'" does not exist!')
	
	# Method
	methodList = ['geometryConstraint','rayIntersect']
	if not methodList.count(method):
		raise Exception('Invalid constraint method "'+method+'"!')
	
	# Ray Origin
	if not rayOrigin: rayOrigin = ''
	if method == 'rayIntersect' and not mc.objExists(rayOrigin):
		raise Exception('Ray origin transform "'+rayOrigin+'" does not exist!')
	
	# UpVector Object
	if (upType == 'object' or upType == 'objectrotation') and not mc.objExists(upObject):
		raise Exception('UpVector transform "'+upObject+'" does not exist!')
	
	# ==================
	# - Create Control -
	# ==================
	
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	ctrl = ctrlBuilder.create(	ctrlType,
								prefix+'_ctrl',
								translate	= ctrlPosition,
								rotate		= ctrlRotate,
								scale		= ctrlScale )
	
	ctrlGrp = mc.group(em=True,n=prefix+'_ctrlGrp')
	ctrl_mvCancelGrp = mc.group(em=True,n=prefix+'_moveCancel_grp')
	mc.parent(ctrl_mvCancelGrp,ctrlGrp)
	mc.parent(ctrl,ctrl_mvCancelGrp)
	
	# Control Xform Group
	ctrlGrpXform = mc.group(em=True,n=prefix+'_ctrlGrpXform')
	
	# =======================================
	# - Build Reference Transform Hierarchy -
	# =======================================
	
	ctrlLocalTrans = mc.spaceLocator(n=prefix+'_localTrans_loc')[0]
	ctrlLocalTransGrp = mc.group(ctrlLocalTrans,n=prefix+'_localTrans_grp')
	ctrlReferenceGrp = mc.group(ctrlLocalTransGrp,n=prefix+'_reference_grp')
	
	mc.setAttr(ctrlLocalTrans+'.localScale',0.05,0.05,0.05)
	
	# Curvature compensation
	if addCurveComp:
		mc.addAttr(ctrlLocalTrans,ln='curvatureX',dv=0.0,k=True)
		mc.addAttr(ctrlLocalTrans,ln='curvatureY',dv=0.0,k=True)
		curveCompNode = mc.createNode('multiplyDivide',n=prefix+'_curvature_multiplyDivide')
		mc.connectAttr(ctrlLocalTrans+'.translateX',curveCompNode+'.input1X',f=True)
		mc.connectAttr(ctrlLocalTrans+'.translateY',curveCompNode+'.input1Y',f=True)
		mc.connectAttr(ctrlLocalTrans+'.curvatureX',curveCompNode+'.input2X',f=True)
		mc.connectAttr(ctrlLocalTrans+'.curvatureY',curveCompNode+'.input2Y',f=True)
		mc.connectAttr(curveCompNode+'.outputX',ctrlLocalTransGrp+'.rotateY',f=True)
		mc.connectAttr(curveCompNode+'.outputY',ctrlLocalTransGrp+'.rotateX',f=True)
	
	# =======================
	# - Position Transforms -
	# =======================
	
	for c in [ctrlGrpXform,ctrlReferenceGrp]:
		mc.move(ctrlPt[0],ctrlPt[1],ctrlPt[2],c)
	
	# ============================
	# - Build Surface Constraint -
	# ============================
	
	if method == 'geometryConstraint':
		constrainToSurface_geometryConstraint(surface,ctrlLocalTrans,ctrlGrpXform,prefix)
	elif method == 'rayIntersect':
		constrainToSurface_rayIntersect(surface,ctrlLocalTrans,ctrlGrpXform,rayOrigin,allowOffset,prefix)
	
	# Normal Constraint
	if upObject:
		normCon = mc.normalConstraint(surface,ctrlGrpXform,aim=[0,0,1],u=upVector,wut=upType,wuo=upObject,n=prefix+'_normalConstraint')[0]
	else:
		normCon = mc.normalConstraint(surface,ctrlGrpXform,aim=[0,0,1],u=upVector,wut=upType,n=prefix+'_normalConstraint')[0]
	
	# Orient Control Reference
	mc.setAttr(ctrlReferenceGrp+'.r',*mc.getAttr(ctrlGrpXform+'.r')[0])
	
	# ============================
	# - Build Connection Network -
	# ============================
	
	attrList = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
	
	# CtrlXform -> CtrlLocalTrans
	for at in ['tx','ty']: mc.connectAttr(ctrl+'.'+at,ctrlLocalTrans+'.'+at,f=True)
	
	# CtrlGrpXform -> CtrlGrp
	for at in attrList: mc.connectAttr(ctrlGrpXform+'.'+at,ctrlGrp+'.'+at,f=True)
	
	# Translate Negation
	localTransNeg = mc.createNode('multiplyDivide',n=prefix+'_moveCancel_multiplyDivide')
	mc.connectAttr(ctrl+'.t',localTransNeg+'.input1',f=True)
	mc.setAttr(localTransNeg+'.input2',-1,-1,-1)
	mc.connectAttr(localTransNeg+'.outputX',ctrl_mvCancelGrp+'.tx',f=True)
	mc.connectAttr(localTransNeg+'.outputY',ctrl_mvCancelGrp+'.ty',f=True)
	mc.connectAttr(localTransNeg+'.outputZ',ctrl_mvCancelGrp+'.tz',f=True)
	# Allow Offset - Cancel translateZ negation
	if allowOffset: mc.setAttr(localTransNeg+'.input2Z',0)
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	result['ctrl'] = ctrl
	result['moveCancel'] = ctrl_mvCancelGrp
	result['ctrlGrp'] = ctrlGrp
	result['ctrlGrpXform'] = ctrlGrpXform
	result['ctrlLocalTrans'] = ctrlLocalTrans
	result['ctrlLocalTransGrp'] = ctrlLocalTransGrp
	result['ctrlReferenceGrp'] = ctrlReferenceGrp
	result['localTransNeg'] = localTransNeg
	result['normalConstraint'] = normCon
	
	return result



def constrainToSurface_geometryConstraint(surface,target,xform,prefix):
	'''
	Use a point/geometry constraint to attach the specified transform to a target surface.
	@param surface: Geometry to attach the transform to.
	@type surface: str
	@param target: Target transform that the constrained transform will try to match.
	@type target: str
	@param xform: Transform to constrainto the surface.
	@type xform: str
	@param prefix: Name prefix for created nodes.
	@type prefix: str
	'''
	# Checks
	if not mc.objExists(surface):
		raise Exception('Surface "'+surface+'" does not exist!')
	if not mc.objExists(target):
		raise Exception('Target transform "'+target+'" does not exist!')
	if not mc.objExists(xform):
		raise Exception('Constraint transform "'+xform+'" does not exist!')
	
	# Create Constraints
	pntCon = mc.pointConstraint(target,xform,n=prefix+'_pointConstraint')
	geoCon = mc.geometryConstraint(surface,xform,n=prefix+'_geometryConstraint')
	
	# Return Result
	return [geoCon,pntCon]

def constrainToSurface_rayIntersect(surface,target,xform,rayOrigin,allowOffset=False,prefix=''):
	'''
	Use the rayIntersect node to attach the specified transform to a target surface.
	@param surface: Geometry to attach the transform to.
	@type surface: str
	@param target: Target locator that the constrained transform will try to match.
	@type target: str
	@param xform: Transform to constrain to the surface.
	@type xform: str
	@param rayOrigin: Ray origin locator to feed into the rayIntersect node.
	@type rayOrigin: str
	@param allowOffset: Allow the constraint to pull away form the guide surface.
	@type allowOffset: bool
	@param prefix: Name prefix for created nodes.
	@type prefix: str
	'''
	# Checks
	if not mc.objExists(surface):
		raise Exception('Surface "'+surface+'" does not exist!')
	if not mc.objExists(target):
		raise Exception('Target transform "'+target+'" does not exist!')
	if not mc.objExists(xform):
		raise Exception('Constraint transform "'+xform+'" does not exist!')
	if not mc.objExists(rayOrigin):
		raise Exception('Ray Origin locator "'+rayOrigin+'" does not exist!')
	
	# Create Nodes
	rayIntersect = mc.createNode('rayIntersect',n=prefix+'_rayIntersect')
	rayDirectionNode = mc.createNode('plusMinusAverage',n=prefix+'_plusMinusAverage')
	intersectWorldPt = mc.createNode('vectorProduct',n=prefix+'_vectorProduct')
	
	# SetAttr
	mc.setAttr(rayDirectionNode+'.operation',2) # Subtract
	mc.setAttr(intersectWorldPt+'.operation',4) # Point/Matrix product
	
	# ConnectAttr
	mc.connectAttr(target+'.worldPosition',rayDirectionNode+'.input3D[0]',f=True)
	mc.connectAttr(rayOrigin+'.worldPosition',rayDirectionNode+'.input3D[1]',f=True)
	mc.connectAttr(rayOrigin+'.worldPosition',rayIntersect+'.rayOrigin',f=True)
	mc.connectAttr(rayDirectionNode+'.output3D',rayIntersect+'.rayDirection',f=True)
	mc.connectAttr(surface+'.outMesh',rayIntersect+'.intersectGeometry',f=True)
	mc.connectAttr(surface+'.worldMatrix[0]',rayIntersect+'.geometryMatrix',f=True)
	mc.connectAttr(rayIntersect+'.point',intersectWorldPt+'.input1',f=True)
	mc.connectAttr(xform+'.parentMatrix[0]',intersectWorldPt+'.matrix',f=True)
	mc.connectAttr(intersectWorldPt+'.output',xform+'.translate',f=True)
	
	# Surface Offset
	if allowOffset:
		rayDistNode = mc.createNode('distanceBetween',n=prefix+'_rayDist_distanceBetween')
		offsetNode = mc.createNode('condition',n=prefix+'_srfOffset_condition')
		mc.connectAttr(target+'.worldPosition',rayDistNode+'.point1',f=True)
		mc.connectAttr(rayOrigin+'.worldPosition',rayDistNode+'.point2',f=True)
		mc.connectAttr(rayDistNode+'.distance',offsetNode+'.firstTerm',f=True)
		mc.connectAttr(rayIntersect+'.distance',offsetNode+'.secondTerm',f=True)
		mc.setAttr(offsetNode+'.operation',2) # Greater Than
		mc.connectAttr(target+'.worldPosition',offsetNode+'.colorIfTrue',f=True)
		mc.connectAttr(rayIntersect+'.point',offsetNode+'.colorIfFalse',f=True)
		mc.connectAttr(offsetNode+'.outColor',intersectWorldPt+'.input1',f=True)
	
	# Return Result
	return [rayIntersect]
	
def secondaryControlInfluence(localTransGrp,slaveCtrl,targetCtrlList,targetAliasList,prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(localTransGrp):
		raise Exception('localTransGrp "'+localTransGrp+'" does not exist!')
	if not mc.objExists(slaveCtrl):
		raise Exception('Slave Control "'+slaveCtrl+'" does not exist!')
	for targetCtrl in targetCtrlList:
		if not mc.objExists(targetCtrl):
			raise Exception('Target Control "'+targetCtrl+'" does not exist!')
	
	# targetCtrlList/targetAliasList
	if len(targetCtrlList) != len(targetAliasList):
		raise Exception('Target Control and Alias list length mis-match!')
	
	# =============================
	# - Add Target Ctrl Influence -
	# =============================
	
	attrList=['tx','ty','tz']
	inputAttrList=['input2X','input2Y','input2Z']
	addInflNode = mc.createNode('plusMinusAverage',n=prefix+'_addCtrlInf_plusMinusAverage')
	for t in range(len(targetCtrlList)):
		ctrlMultNode = mc.createNode('multiplyDivide',n=prefix+'_'+targetAliasList[t]+'Inf_multiplyDivide')
		mc.connectAttr(targetCtrlList+'.t',ctrlMultNode+'.input1',f=True)
		
		# Add Influence Control Attrs
		for at in range(len(attrList)):
			if not mc.objExists(slaveCtrl+'.'+targetAliasList[t]+'_'+attrList[at].upper()):
				mc.addAttr(slaveCtrl,ln=targetAliasList[t]+'_'+attrList[at].upper(),min=-1.0,max=1.0,dv=0.0)
			mc.connectAttr(slaveCtrl+'.'+targetAliasList[t]+'_'+attrList[at].upper(),ctrlMultNode+'.'+inputAttrList[at],f=True)
		
		# Connect to Add Ctrl Influence Node
		addInfIndex = glTools.utils.attribute.nextAvailableMultiIndex(addInflNode+'.input3D')
		mc.connectAttr(ctrlMultNode+'.output',addInflNode+'.input3D['+str(addInfIndex)+']',f=True)
	
	# Connect to LocalTransGrp
	mc.connectAttr(addInflNode+'.output3D',localTransGrp+'.t',f=True)

def midControlConstraint(ctrlXform,target1,target2,prefix):
	'''
	'''
	# Create target locators
	loc1 = mc.spaceLocator(n=prefix+'_target1_loc')[0]
	loc2 = mc.spaceLocator(n=prefix+'_target2_loc')[0]
	
	# Position locators
	mc.delete(mc.parentConstraint(ctrlXform,loc1))
	mc.delete(mc.parentConstraint(ctrlXform,loc2))
	# Parent locators
	mc.parent(loc1,target1)
	mc.parent(loc2,target2)
	
	# Constrain controls xform
	ptCon = mc.pointConstraint([loc1,loc2],ctrlXform,n=prefix+'_pointConstraint')
	
	# Return Result
	return ptCon

def blendUpVector(constraint,target1,target2,upVector=[0,1,0],blendAttr='',prefix=''):
	'''
	'''
	# Get target world upVectors
	targetVector1 = mc.createNode('vectorProduct',n=prefix+'_targetVector1_vectorProduct')
	mc.connectAttr(target1+'.worldMatrix[0]',targetVector1+'.matrix',f=True)
	mc.setAttr(targetVector1+'.operation',3) # Vector/Matrix Product
	mc.setAttr(targetVector1+'.input1',*upVector)
	targetVector2 = mc.createNode('vectorProduct',n=prefix+'_targetVector2_vectorProduct')
	mc.connectAttr(target2+'.worldMatrix[0]',targetVector2+'.matrix',f=True)
	mc.setAttr(targetVector2+'.operation',3) # Vector/Matrix Product
	mc.setAttr(targetVector2+'.input1',*upVector)
	
	# Create Blend Node
	vectorBlend = mc.createNode('blendColors',n=prefix+'_blendUpVector_blendColors')
	mc.connectAttr(targetVector1+'.output',vectorBlend+'.color1',f=True)
	mc.connectAttr(targetVector2+'.output',vectorBlend+'.color2',f=True)
	
	# Add blend attribute
	if blendAttr:
		if not blendAttr.count('.'):
			raise Exception('Blend attribute is not valid ("obj.attr")!')
		blendNode = blendAttr.split('.')[0]
		blendAttr = blendAttr.split('.')[1]
		if not mc.objExists(blendNode+'.'+blendAttr):
			mc.addAttr(blendNode,ln=blendAttr,min=0,max=1,dv=0.5)
		mc.connectAttr(blendNode+'.'+blendAttr,vectorBlend+'.blender',f=True)
	
	# Connect UpVector
	mc.connectAttr(vectorBlend+'.output',constraint+'.worldUpVector',f=True)
	mc.setAttr(constraint+'.worldUpType',3) # Vector
	
	# Return Result
	result = {}
	result['worldVector1'] = targetVector1
	result['worldVector2'] = targetVector2
	result['upVectorBlend'] = vectorBlend
	return result

def ctrlMeshConstraint(ctrl,ctrlRef='',faceAxis='y',faceScale=0.05,prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(ctrl):
		raise Exception('Control object "'+ctrl+'" does not exist!!')
	if ctrlRef and not mc.objExists(ctrlRef):
		raise Exception('Control reference object "'+ctrlRef+'" does not exist!!')
	
	# =======================
	# - Create Control Face -
	# =======================
	
	ctrlFace = glTools.tools.pointFaceMesh.transformFaceMesh([ctrl],faceAxis,faceScale,False,prefix)[0]
	
	# ============================
	# - Attach Control Reference -
	# ============================
	
	if ctrlRef:
		faceLoc = ctrlRef
		faceCon = mc.pointOnPolyConstraint(ctrlFace,ctrlRef,n=prefix+'_pointOnPolyConstraint')[0]
	else:
		faceLoc = mc.spaceLocator(n=prefix+'_ctrlFace_loc')[0]
		mc.setAttr(faceLoc+'.localScale',faceScale,faceScale,faceScale)
		faceCon = mc.pointOnPolyConstraint(ctrlFace,faceLoc,n=prefix+'_pointOnPolyConstraint')[0]
	
	mc.setAttr(faceCon+'.'+ctrlFace+'U0',0.5)
	mc.setAttr(faceCon+'.'+ctrlFace+'V0',0.5)
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	result['face'] = ctrlFace
	result['locator'] = faceLoc
	result['pointOnPolyConstraint'] = faceCon
	return result

def createVertexLocators(vtxList,locScale=0.1,prefix=''):
	'''
	Create a list of vertex locators from a list of mesh vertices.
	@param vtxList: List of vertices to generate vertex locators from.
	@type vtxList: list
	@param locScale: Local scale value for the created locators.
	@type locScale: float
	@param prefix: Naming prefix string for the locators.
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Flatten vertex list
	vtxList = mc.ls(vtxList,fl=True)
	
	# ===================
	# - Create Locators -
	# ===================
	
	# Get mesh from vertex selection
	mesh = mc.ls(vtxList[0],o=True)[0]
	
	# Initialize locator list
	locList = []
	
	# For each vertex
	for v in range(len(vtxList)):
		
		# Determine string index
		strInd = glTools.utils.stringUtils.stringIndex(v+1)
		
		# Get Vtx Position
		pt = mc.pointPosition(vtxList[v])
		# Create Locator
		loc = mc.spaceLocator(n=prefix+'_'+strInd+'_loc')[0]
		mc.setAttr(loc+'.localScale',locScale,locScale,locScale)
		# Position Locator
		mc.move(pt[0],pt[1],pt[2],loc,ws=True)
		
		# Record Vertex ID
		glTools.utils.mesh.closestVertexAttr(loc,mesh)
		
		# Append Return List
		locList.append(loc)
	
	# =================
	# - Return Result -
	# =================
	
	return locList

def createControlLocators(ptList):
	'''
	'''
	pass

def controlFromLocator(	locList,
						ctrlType	= 'transform',
						ctrlShape	= 'box',
						ctrlScale	= 0.1,
						ctrlLod		= 'primary',
						driverType	= None,
						orient		= True,
						parentToLoc	= False ):
	'''
	Generate controls objects from a list of locators
	@param locList: List of locators to generate controls from.
	@type locList: list
	@param ctrlType: Control transform type. Accepted values include "transform" and "joint".
	@type ctrlType: str
	@param ctrlShape: Control transform type.
	@type ctrlShape: str
	@param ctrlScale: Control shape scale.
	@type ctrlScale: float
	@param ctrlLod: Control LOD type.
	@type ctrlLod: str
	@param driverType: Control driver type. If None, don't create control driver.
	@type driverType: str or None
	@param orient: Orient control to locator.
	@type orient: bool
	@param parentToLoc: Parent control group to locator.
	@type parentToLoc: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Locators
	for loc in locList:
		if not mc.objExists(loc):
			raise Exception('Locator "'+loc+'" does not exist!')
	
	# Check Control LOD
	ctrlLodList = ['primary','secondary', 'tertiary']
	if not ctrlLod in ctrlLodList:
		raise Exception('Invalid control LOD (level of detail)! ("'+ctrlLod+'")')
	
	# ===================
	# - Create Controls -
	# ===================
	
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	ctrlList = []
	ctrlGrpList = []
	driverList = []
	driverGrpList = []
	for loc in locList:
		
		# Clear Selection
		mc.select(cl=True)
		
		# Generate Naming Prefix
		prefix = glTools.utils.stringUtils.stripSuffix(loc)
		
		# Create Control
		ctrl = ''
		ctrlGrp = ''
		if ctrlType == 'transform':
			ctrl = mc.createNode(ctrlType,n=prefix+'_ctrl')
			ctrlGrp = mc.group(ctrl,n=prefix+'_ctrlGrp')
		elif ctrlType == 'joint':
			ctrl = mc.joint(n=prefix+'_jnt')
			ctrlGrp = glTools.utils.joint.group(ctrl,'A')
			mc.setAttr(ctrl+'.radius',ctrlScale)
			mc.setAttr(ctrlGrp+'.radius',ctrlScale)
			glTools.utils.base.displayOverride(ctrl,overrideEnable=1,overrideLOD=1)
			glTools.utils.base.displayOverride(ctrlGrp,overrideEnable=1,overrideLOD=1)
			if not driverType: glTools.rig.utils.tagBindJoint(ctrl)
		else:
			raise Exception('Invalid control transform type "'+ctrlType+'"!')
		
		# Parent to Locator
		if parentToLoc: mc.parent(ctrlGrp,loc)
		
		# Create Control Shape
		ctrlBuilder.controlShape(ctrl,controlType=ctrlShape,scale=ctrlScale)
		
		# Tag Control
		glTools.rig.utils.tagCtrl(ctrl,ctrlLod)
			
		# Create Driver
		driver = None
		driverGrp = None
		if driverType:
			
			# Clear Selection
			mc.select(cl=True)
			
			if driverType == 'transform':
				driver = mc.createNode(ctrlType,n=prefix+'_driver')
				driverGrp = mc.group(ctrl,n=prefix+'_driverGrp')
			elif driverType == 'joint':
				driver = mc.joint(n=prefix+'_driver')
				driverGrp = glTools.utils.joint.group(driver,'A')
				mc.setAttr(driver+'.radius',ctrlScale)
				mc.setAttr(driverGrp+'.radius',ctrlScale)
				glTools.utils.base.displayOverride(driver,overrideEnable=1,overrideLOD=1)
				glTools.utils.base.displayOverride(driverGrp,overrideEnable=1,overrideLOD=1)
				glTools.rig.utils.tagBindJoint(driver)
			else:
				raise Exception('Invalid control driver type "'+driverType+'"!')
			
			# Connect Driver
			for at in 'trs':
				mc.connectAttr(ctrl+'.'+at,driver+'.'+at,f=True)
				mc.connectAttr(driverGrp+'.'+at,ctrlGrp+'.'+at,f=True)
			
			# Position Driver Group
			mc.delete(mc.pointConstraint(loc,driverGrp))
			if orient: mc.delete(mc.orientConstraint(loc,driverGrp))
			
			# Parent to Locator
			if parentToLoc: mc.parent(driverGrp,loc)
		
		else:
		
			# Position Control Group
			mc.delete(mc.pointConstraint(loc,ctrlGrp))
			if orient: mc.delete(mc.orientConstraint(loc,ctrlGrp))
		
		# Append to Return Lists
		ctrlList.append(ctrl)
		ctrlGrpList.append(ctrlGrp)
		driverList.append(driver)
		driverGrpList.append(driverGrp)
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	
	result['ctrl'] = ctrlList
	result['ctrlGrp'] = ctrlGrpList
	result['driver'] = driverList
	result['driverGrp'] = driverGrpList
	
	return result

def separateInfluenceMesh(baseMesh,inputMesh,setList,suffix='mesh'):
	'''
	Separate a mesh to history driven mesh shells based on face sets
	@param baseMesh: Base mesh to define face sets.
	@type baseMesh: str
	@param inputMesh: Mesh to separate influence shells from.
	@type inputMesh: str
	@param setList: List of face sets to define shells.
	@type setList: list
	@param suffix: Naming suffix for separated mesh shells.
	@type suffix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Mesh
	if not mc.objExists(baseMesh):
		raise Exception('Base Mesh "'+baseMesh+'" does not exist!')
	if not mc.objExists(inputMesh):
		raise Exception('Input Mesh "'+inputMesh+'" does not exist!')
	
	# Sets
	for faceSet in setList:
		for face in mc.sets(faceSet,q=True):
			if not mc.ls(face,o=True)[0] != baseMesh:
				raise Exception('Invalid item "'+face+'" in set "'+faceSet+'"')
	
	# ===========================
	# - Separate Mesh Face Sets -
	# ===========================
	
	infMeshList = []
	delCompList = []
	
	for faceSet in setList:
		
		# Get Set Prefix
		prefix = glTools.utils.stringUtils.stripSuffix(faceSet)
		
		# Duplicate Connected Mesh
		infMesh = mc.polyDuplicateAndConnect(inputMesh)[0]
		infMesh = mc.rename(infMesh,prefix+'_'+suffix)
		
		# Delete Unwanted Faces
		allFaces = mc.ls(infMesh+'.f[*]',fl=True)
		setFaces = mc.ls(mc.sets(faceSet,q=True),fl=True)
		setFaces = [i.replace(baseMesh,infMesh) for i in setFaces if i.count(baseMesh)]
		#meshFaces = list(set(allFaces) & set(setFaces)) # Set Intersection
		delFaces = list(set(allFaces) - set(setFaces))
		mc.delete(delFaces)
		
		# Rename deleteComponent node
		delNode = mc.ls(mc.listHistory(infMesh),type='deleteComponent')
		if not delNode: raise Exception('Unable to determine deleteComponent from mesh "'+infMesh+'"!')
		delNode = mc.rename(delNode[0],prefix+'_deleteComponent')
		
		# Append to return list
		infMeshList.append(infMesh)
		delCompList.append(delNode)
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	
	result['influenceMesh'] = infMeshList
	result['deleteComponent'] = delCompList
	
	return result

def asymmetricalBaseMesh(baseMesh,symMesh,asymMesh):
	'''
	Generate an asymmetrical base mesh from standard geometry
	@param baseMesh: Base mesh to generate asymmetrical base from.
	@type baseMesh: str
	@param symMesh: Symmetrical target mesh.
	@type symMesh: str
	@param asymMesh: Asymmetrical target mesh.
	@type asymMesh: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(baseMesh):
		raise Exception('Base mesh "'+baseMesh+'" does not exist!')
	if not mc.objExists(symMesh):
		raise Exception('Symmetrical target mesh "'+symMesh+'" does not exist!')
	if not mc.objExists(asymMesh):
		raise Exception('Asymmetrical target mesh "'+asymMesh+'" does not exist!')
	
	# ==============================
	# - Generate Asymmetrical Base -
	# ==============================
	
	# Duplicate base to create asymmetrical base
	asymBase = mc.duplicate(baseMesh,n='face_asym_target')[0]
	
	# Duplicate target to use as wrap deformer
	symWrap = mc.duplicate(symMesh,n='face_asym_wrapTarget')[0]
	# Create Asymmetricl BlendShape
	asymBlend = mc.blendShape(asymMesh,symWrap)[0]
	asymAlias = mc.listAttr(asymBlend+'.w',m=True)[0]
	
	# Create Wrap Deformer -------------- WTF! Wrap Deformers Suck BALLLZ!
	sel = mc.ls(sl=1)
	mc.select(asymBase,symWrap)
	mm.eval('CreateWrap')
	wrap = mc.ls(mc.listHistory(asymBase),type='wrap')[0]
	wrapBase = mc.listConnections(wrap+'.basePoints',s=True,d=False)
	if sel: mc.select(sel)
	
	# Apply Blend Target
	mc.setAttr(asymBlend+'.'+asymAlias,1.0)
	
	# ============
	# - Clean Up -
	# ============
	
	mc.delete(asymBase,ch=True)
	mc.delete(symWrap)
	mc.delete(wrapBase)
	
	# =================
	# - Return Result -
	# =================
	
	return asymBase

def surfaceControlMesh(baseMesh,inputMesh,asymMesh='',asymAttr='',prefix=''):
	'''
	Generate "On Surface" control drive mesh and control deform mesh based on specified inputs.
	@param baseMesh: Base mesh to generate control drive mesh from.
	@type baseMesh: str
	@param inputMesh: Input mesh that will drive the control mesh.
	@type inputMesh: str
	@param asymMesh: Asymmetrical mesh target. (optional)
	@type asymMesh: str
	@param asymAttr: Asymmetry control attribute. Must vary from 0.0 -> 1.0. (optional)
	@type asymAttr: str
	@param prefix: Naming prefix for new nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(baseMesh):
		raise Exception('Base mesh "'+baseMesh+'" does not exist!')
	if not mc.objExists(inputMesh):
		raise Exception('Input mesh "'+inputMesh+'" does not exist!')
	if asymMesh and not mc.objExists(asymMesh):
		raise Exception('Asymmetrical target mesh "'+asymMesh+'" does not exist!')
	if asymAttr and not mc.objExists(asymAttr):
		raise Exception('Asymmetry control attribute "'+asymAttr+'" does not exist!')
	
	# ===============================
	# - Generate Control Drive Mesh -
	# ===============================
	
	# Duplicate base mesh to create drive and deform mesh
	driveMesh = mc.duplicate(baseMesh,n=prefix+'Drive_mesh')[0]
	deformMesh = mc.duplicate(baseMesh,n=prefix+'Deform_mesh')[0]
	
	# ======================
	# - Connect Input Mesh -
	# ======================
	
	# Drive Mesh
	driveTargetList = [inputMesh]
	if mc.objExists(asymMesh): driveTargetList.append(asymMesh)
	driveBlendShape = mc.blendShape(driveTargetList,driveMesh,n=prefix+'Drive_blendShape')[0]
	driveBlendAlias = mc.listAttr(driveBlendShape+'.w',m=True)
	mc.setAttr(driveBlendShape+'.'+driveBlendAlias[0],1.0)
	if mc.objExists(asymAttr): mc.connectAttr(asymAttr,driveBlendShape+'.'+driveBlendAlias[1],f=True)
	
	# Deform Mesh
	deformTargetList = [inputMesh]
	#if mc.objExists(asymMesh): deformTargetList.append(asymMesh)
	deformBlendShape = mc.blendShape(deformTargetList,deformMesh,n=prefix+'Deform_blendShape')[0]
	deformBlendAlias = mc.listAttr(deformBlendShape+'.w',m=True)
	mc.setAttr(deformBlendShape+'.'+deformBlendAlias[0],1.0)
	#if mc.objExists(asymAttr): mc.connectAttr(asymAttr,deformBlendShape+'.'+deformBlendAlias[1],f=True)
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	result['driveMesh'] = driveMesh
	result['deformMesh'] = deformMesh
	return result

def surfaceControlCreate(ctrlLocs,ctrlDriveMesh,guideMesh,ctrlType='joint',ctrlShape='sphere',ctrlScale=0.05,ctrlLod='primary',prefix=''):
	'''
	Generate surface constrainted control
	@param ctrlLocs: 
	@type ctrlLocs: list
	@param ctrlDriveMesh: 
	@type ctrlDriveMesh: str
	@param guideMesh: 
	@type guideMesh: str
	@param ctrlType: 
	@type ctrlType: str
	@param ctrlShape: 
	@type ctrlShape: str
	@param ctrlScale: 
	@type ctrlScale: str
	@param ctrlLod: 
	@type ctrlLod: str
	@param prefix: Naming prefix for new nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# ===================================
	# - Constrain Locator To Drive Mesh -
	# ===================================
	
	# Build Target Vertex List
	vtxList = [ctrlDriveMesh+'.vtx['+str(mc.getAttr(loc+'.vtx'))+']' for loc in ctrlLocs]
	meshConstraint = glTools.tools.autoRivet.meshVertexConstraintList(vtxList,ctrlLocs,orient=False,prefix=prefix)
	
	# Orient Locators to Guide Mesh
	for loc in ctrlLocs:
		mc.delete( mc.normalConstraint(guideMesh,loc,aim=[0,0,1],u=[1,0,0],wut='vector',wu=[1,0,0]) )
	
	# =================================
	# - Create Controls From Locators -
	# =================================
	
	locCtrl = glTools.rig.face_utils.controlFromLocator(	ctrlLocs,
														ctrlType,
														ctrlShape,
														ctrlScale,
														ctrlLod,
														orient=True,
														parentToLoc=True	)
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	
	result['locator'] = ctrlLocs
	result['ctrl'] = locCtrl['ctrl']
	result['ctrlGrp'] = locCtrl['ctrlGrp']
	result['constraint'] = meshConstraint
	
	return result
	
def controlOverride(ctrl,duplicateParentOnly=True,connect=True,originalIsSlave=True,autoDetectParent=False,parentTo=''):
	'''
	Create an override control for the specified control transform. Options to connect the override control,
	using the original as either the slave or master. Connections are established as local transform overrides.
	@param ctrl: Control to create control override for. 
	@type ctrl: str
	@param duplicateParentOnly: Duplicate parent transform only, all child transforms and shapes will be ignored. 
	@type duplicateParentOnly: bool
	@param connect: Connect the control and control override transforms. 
	@type connect: bool
	@param originalIsSlave: Set the original as the destination transform for all incoming connections. 
	@type originalIsSlave: bool
	@param autoDetectParent: Parent the control override based on incoming control override connections of the original control parent. 
	@type autoDetectParent: bool
	@param parentTo: The transform to parent the control override to. This will be overridden if a valid parent is detected as a sresult of autoDetectParent=True.  
	@type parentTo: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Control
	if not mc.objExists(ctrl):
		raise Exception('Control object "'+ctrl+'" does not exist!')
	# Parent
	if parentTo and not mc.objExists(parentTo):
		raise Exception('Parent object "'+parentTo+'" does not exist!')
	
	# =====================
	# - Duplicate Control -
	# =====================
	
	ctrlDup = mc.duplicate(ctrl,po=duplicateParentOnly)[0]
	if not duplicateParentOnly:
		ctrlDupChildren = mc.listRelatives(ctrlDup,c=True,pa=True)
		ctrlDupChildren = mc.ls(ctrlDupChildren,type=['transform','joint','ikHandle'])
		if ctrlDupChildren: mc.delete(ctrlDupChildren)
	
	# Rename Controls
	ctrlDrive = mc.rename(ctrl,ctrl+'DRV')
	ctrl = mc.rename(ctrlDup,ctrl)
	
	# Connect Controls
	if originalIsSlave:
		src = ctrl
		dst = ctrlDrive
	else:
		src = ctrlDrive
		dst = ctrl
	if connect:
		xformList = glTools.utils.lib.xform_list()
		udAttrList = mc.listAttr(ctrl,ud=True,k=True)
		cbAttrList = mc.listAttr(ctrl,ud=True,cb=True)
		if not udAttrList: udAttrList = []
		if not cbAttrList: cbAttrList = []
		# Connect Xform Attrs
		for attr in xformList:
			#if mc.getAttr(dst+'.'+attr,se=True):
			mc.setAttr(dst+'.'+attr,l=False)
			mc.connectAttr(src+'.'+attr,dst+'.'+attr,f=True)
		# Connect UserDefined Attrs
		for attr in udAttrList:
			if mc.getAttr(dst+'.'+attr,se=True):
				mc.connectAttr(src+'.'+attr,dst+'.'+attr,f=True)
		for attr in cbAttrList:
			if mc.getAttr(dst+'.'+attr,se=True):
				mc.connectAttr(src+'.'+attr,dst+'.'+attr,f=True)
	
	# Connect Shape Vis
	if connect:
		ctrlShapes = mc.listRelatives(ctrl,s=True,pa=True)
		ctrlDrvShapes = mc.listRelatives(ctrlDrive,s=True,pa=True)
		if not ctrlShapes: ctrlShapes = []
		if not ctrlDrvShapes: ctrlDrvShapes = []
		for i in range(len(ctrlShapes)):
			if i > len(ctrlDrvShapes): break
			mc.connectAttr(ctrlDrvShapes[i]+'.v',ctrlShapes[i]+'.v',f=True)
	
	# Connect Visibility
	mc.setAttr(ctrl+'.v',l=False)
	mc.connectAttr(ctrlDrive+'.v',ctrl+'.v',f=True)
	
	# Connect Msg Attributes
	mc.addAttr(dst,ln='controlMaster',at='message')
	mc.addAttr(src,ln='controlSlave',at='message')
	mc.connectAttr(src+'.message',dst+'.controlMaster')
	mc.connectAttr(dst+'.message',src+'.controlSlave')
	
	# ==========
	# - Parent -
	# ==========
	
	# Auto Detect
	if autoDetectParent:
		dstParent = mc.listRelatives(dst,p=True,pa=True)[0]
		if mc.objExists(dstParent+'.controlSlave'):
			dstTarget = mc.listConnections(dstParent+'.controlSlave',s=True,d=False)
			if dstTarget: parentTo = dstTarget[0]
		elif mc.objExists(dstParent+'.controlMaster'):
			dstTarget = mc.listConnections(dstParent+'.controlMaster',s=True,d=False)
			if dstTarget: parentTo = dstTarget[0]
	
	# Parent
	if parentTo:
		mc.parent(ctrl,parentTo)
	
	# =================
	# - Return Result -
	# =================
	
	return ctrlDrive
