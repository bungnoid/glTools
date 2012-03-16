import maya.cmds as mc

import glTools.utils.base
import glTools.utils.joint

import glTools.tools.controlBuilder
import glTools.tools.ikHandle

import glTools.rig.utils

def build(footJoint,ballJoint,toeJoint,footOrient,toePiv,heelPiv,innerPiv,outerPiv,ikHandle,ikCtrl,blendCtrl='',blendAttr='ikFkBlend',prefix=''):
	'''
	Build foot rig based on standard FK/IK limb.
	@param footJoint: Foot ankle joint
	@type footJoint: str
	@param ballJoint: Foot ball joint
	@type ballJoint: str
	@param toeJoint: Foot toe joint
	@type toeJoint: str
	@param footOrient: Foot orient locator
	@type footOrient: str
	@param toePiv: Foot toe pivot
	@type toePiv: str
	@param heelPiv: Foot heel pivot
	@type heelPiv: str
	@param innerPiv: Foot inner pivot
	@type innerPiv: str
	@param outerPiv: Foot outer pivot
	@type outerPiv: str
	@param ikHandle: Limb IK handle transform. Generally the ikHandle group.
	@type ikHandle: str
	@param ikCtrl: Limb IK control
	@type ikCtrl: str
	@param blendCtrl: Limb IK/FK blend control. Default to ikCtrl if empty
	@type blendCtrl: str
	@param blendAttr: Limb IK/FK blend attribute.
	@type blendAttr: str
	@param prefix: Name prefix for new nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not blendCtrl: blendCtrl = ikCtrl
	
	if not mc.objExists(footJoint):
		raise Exception('Foot ankle joint "'+footJoint+'" does not exist!')
	if not mc.objExists(ballJoint):
		raise Exception('Foot ball joint "'+ballJoint+'" does not exist!')
	if not mc.objExists(toeJoint):
		raise Exception('Foot toe joint "'+toeJoint+'" does not exist!')
	if not mc.objExists(footOrient):
		raise Exception('Foot orient locator "'+footOrient+'" does not exist!')
	if not mc.objExists(toePiv):
		raise Exception('Foot toe pivot "'+toePiv+'" does not exist!')
	if not mc.objExists(heelPiv):
		raise Exception('Foot heel pivot "'+heelPiv+'" does not exist!')
	if not mc.objExists(innerPiv):
		raise Exception('Foot inner pivot "'+innerPiv+'" does not exist!')
	if not mc.objExists(outerPiv):
		raise Exception('Foot outer pivot "'+outerPiv+'" does not exist!')
	if not mc.objExists(ikCtrl):
		raise Exception('Limb IK control "'+ikCtrl+'" does not exist!')
	if not mc.objExists(ikHandle):
		raise Exception('Limb IK handle transform "'+ikHandle+'" does not exist!')
	if not mc.objExists(blendCtrl+'.'+blendAttr):
		raise Exception('Limb IK/FK blend attribute "'+blendCtrl+'.'+blendAttr+'" does not exist!')
	
	# ====================
	# - Configure Module -
	# ====================
	
	fkCtrlScale = 0.5
	ikCtrlScale = 1
	
	toeRollAngle = 60
	footRollAngle = 60
	footPivotAngle = 60
	footTapAngle = 60
	
	footPos = glTools.utils.base.getPosition(footJoint)
	if footPos[0] > 0.0: footTiltAngle = 60
	else: footTiltAngle = -60
	
	footRollAttrRange = 10
	
	# ==========================
	# - Build Module Structure -
	# ==========================
	
	# Create control group
	ctrl_grp = mc.group(em=True,n=prefix+'_ctrl_grp',w=True)
	
	# Create rig group
	rig_grp = mc.group(em=True,n=prefix+'_rig_grp',w=True)
	mc.setAttr(rig_grp+'.v',0)
	
	# Create skel group
	skel_grp = mc.group(em=True,n=prefix+'_skel_grp',w=True)
	
	# Create module group
	module = mc.group(em=True,n=prefix+'_module')
	mc.parent([ctrl_grp,rig_grp,skel_grp],module)
	
	# - Uniform Scale -
	mc.addAttr(module,ln='uniformScale',min=0.001,dv=1.0)
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleX')
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleY')
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleZ')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleX')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleY')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleZ')
	mc.connectAttr(module+'.uniformScale',rig_grp+'.scaleX')
	mc.connectAttr(module+'.uniformScale',rig_grp+'.scaleY')
	mc.connectAttr(module+'.uniformScale',rig_grp+'.scaleZ')
	
	# =================
	# - Create Joints -
	# =================
	
	footJoints = [footJoint,ballJoint,toeJoint]
	
	# IK Joints
	ikJoints = glTools.utils.joint.duplicateChain(footJoint,toeJoint,prefix=prefix+'_ik')
	ikJointGrp = glTools.utils.joint.group(ikJoints[0])
	
	# FK Joints
	fkJoints = glTools.utils.joint.duplicateChain(footJoint,toeJoint,prefix=prefix+'_fk')
	fkJointGrps = [glTools.utils.joint.group(fkJoint) for fkJoint in fkJoints]
	
	# Joint Buffers
	ballJointGrp = glTools.utils.joint.group(ballJoint)
	footJointGrp = glTools.utils.joint.group(footJoint)
	
	# =======================
	# - Create Attach Joint -
	# =======================
	
	mc.select(cl=True)
	
	# Attach joint
	attachJoint = mc.joint(n=prefix+'_attachA_jnt')
	attachJointGrp = glTools.utils.joint.group(attachJoint)
	mc.delete(mc.pointConstraint(footJoint,attachJointGrp))
	
	# Attach joint display
	mc.setAttr(attachJoint+'.overrideEnabled',1)
	mc.setAttr(attachJoint+'.overrideLevelOfDetail',1)
	
	# Parent attach joint
	mc.parent([footJointGrp,ikJointGrp,fkJointGrps[0]],attachJoint)
	mc.parent(attachJointGrp,skel_grp)
	
	# ==================
	# - Build Controls -
	# ==================
	
	# Calculate max joint length
	jntLen = 0.0
	for fkJoint in fkJoints[:-1]:
		cJntLen = glTools.utils.joint.length(fkJoint)
		if cJntLen > jntLen: jntLen = cJntLen
	
	# FK Controls
	for fkJoint in fkJoints[:-1]:
		glTools.tools.controlBuilder.controlShape(fkJoint,'circle',rotate=[0,90,0],scale=jntLen*fkCtrlScale)
		glTools.rig.utils.tagCtrl(fkJoint,'primary')
	
	# Add foot roll attributes
	footAttr = ['toeRoll','footRoll','footTilt','heelPivot','ballPivot','toePivot','toeTap']
	for attr in footAttr:
		if not mc.objExists(ikCtrl+'.'+attr):
			mc.addAttr(ikCtrl,ln=attr,min=-1*footRollAttrRange,max=1*footRollAttrRange,dv=0,k=True)
	
	# Add Foot IK Control
	footIkCtrl = mc.group(em=True,n=prefix+'_ik_ctrl')
	footIkCtrlGrp = glTools.utils.base.group(footIkCtrl,name=footIkCtrl+'Grp')
	glTools.tools.controlBuilder.controlShape(footIkCtrl,'circle',rotate=[90,0,0],scale=jntLen*ikCtrlScale)
	glTools.rig.utils.tagCtrl(footIkCtrl,'primary')
	# Position Control
	mc.delete(mc.pointConstraint(footOrient,footIkCtrlGrp))
	mc.delete(mc.orientConstraint(footOrient,footIkCtrlGrp))
	# Parent IK Control
	mc.parent(footIkCtrlGrp,ctrl_grp)
	# Constrain IK Control
	mc.parentConstraint(ikCtrl,footIkCtrlGrp,mo=True)
	
	# =================
	# - Build IK Foot -
	# =================
	
	# Ball IK
	ballIk = glTools.tools.ikHandle.build(ikJoints[0],ikJoints[1],prefix=prefix+'_ballA')
	ballIkGrp = glTools.utils.base.group(ballIk,name=ballIk+'Grp')
	
	# Toe IK
	toeIk = glTools.tools.ikHandle.build(ikJoints[1],ikJoints[2],prefix=prefix+'_toeA')
	toeIkGrp = glTools.utils.base.group(toeIk,name=toeIk+'Grp')
	
	# Limb Attach Group
	limbPivot = mc.group(em=True,n=prefix+'_limbPivot_grp')
	mc.delete(mc.pointConstraint(footJoint,limbPivot))
	mc.delete(mc.orientConstraint(footOrient,limbPivot))
	
	# Ball Roll
	ballRoll = mc.group(em=True,n=prefix+'_ballRoll_grp')
	mc.delete(mc.pointConstraint(ballJoint,ballRoll))
	mc.delete(mc.orientConstraint(footOrient,ballRoll))
	mc.parent(limbPivot,ballRoll)
	
	# Toe Tap Pivot
	toeTapPivot = mc.group(em=True,n=prefix+'_toeTapPivot_grp')
	mc.delete(mc.pointConstraint(ballJoint,toeTapPivot))
	mc.delete(mc.orientConstraint(footOrient,toeTapPivot))
	
	# Ball Pivot
	ballPivot = mc.group(em=True,n=prefix+'_ballPivot_grp')
	mc.delete(mc.pointConstraint(ballJoint,ballPivot))
	mc.delete(mc.orientConstraint(footOrient,ballPivot))
	mc.parent(ballRoll,ballPivot)
	mc.parent(toeTapPivot,ballPivot)
	
	# Toe Pivot
	toePivot = mc.group(em=True,n=prefix+'_toePivot_grp')
	mc.delete(mc.pointConstraint(toePiv,toePivot))
	mc.delete(mc.orientConstraint(footOrient,toePivot))
	mc.parent(ballPivot,toePivot)
	
	# Heel Pivot
	heelPivot = mc.group(em=True,n=prefix+'_heelPivot_grp')
	mc.delete(mc.pointConstraint(heelPiv,heelPivot))
	mc.delete(mc.orientConstraint(footOrient,heelPivot))
	mc.parent(toePivot,heelPivot)
	
	# Inner Pivot
	innerPivot = mc.group(em=True,n=prefix+'_innerPivot_grp')
	mc.delete(mc.pointConstraint(innerPiv,innerPivot))
	mc.delete(mc.orientConstraint(footOrient,innerPivot))
	mc.parent(heelPivot,innerPivot)
	
	# Outer Pivot
	outerPivot = mc.group(em=True,n=prefix+'_outerPivot_grp')
	mc.delete(mc.pointConstraint(outerPiv,outerPivot))
	mc.delete(mc.orientConstraint(footOrient,outerPivot))
	mc.parent(innerPivot,outerPivot)
	
	# Foot Pivot
	footPivot = mc.group(em=True,n=prefix+'_footPivot_grp')
	mc.delete(mc.pointConstraint(footJoint,footPivot))
	mc.delete(mc.orientConstraint(footOrient,footPivot))
	mc.parent(outerPivot,footPivot)
	
	# Parent IK
	mc.parent(toeIkGrp,toeTapPivot)
	mc.parent(ballIkGrp,ballPivot)
	mc.parent(footPivot,rig_grp)
	
	# ===================
	# - Connect IK Limb -
	# ===================
	
	limbIkConstraint = mc.pointConstraint(limbPivot,ikHandle)
	footConstraint = mc.parentConstraint(footIkCtrl,footPivot,mo=True)
	
	# =======================
	# - Connect to Controls -
	# =======================
	
	# Toe Roll
	toeRollAdd = mc.createNode('addDoubleLinear',n=prefix+'_toeRoll_addDoubleLinear')
	toeRollRemap = mc.createNode('remapValue',n=prefix+'_toeRoll_remapValue')
	
	mc.connectAttr(ikCtrl+'.toeRoll',toeRollRemap+'.inputValue',f=True)
	mc.setAttr(toeRollRemap+'.inputMin',-footRollAttrRange)
	mc.setAttr(toeRollRemap+'.inputMax',footRollAttrRange)
	mc.setAttr(toeRollRemap+'.outputMin',-toeRollAngle)
	mc.setAttr(toeRollRemap+'.outputMax',toeRollAngle)
	mc.connectAttr(toeRollRemap+'.outValue',toeRollAdd+'.input1',f=True)
	
	# Foot Roll
	toeFootRollRemap = mc.createNode('remapValue',n=prefix+'_toeFootRoll_remapValue')
	ballFootRollRemap = mc.createNode('remapValue',n=prefix+'_ballFootRoll_remapValue')
	hellFootRollRemap = mc.createNode('remapValue',n=prefix+'_heelFootRoll_remapValue')
	
	mc.connectAttr(ikCtrl+'.footRoll',toeFootRollRemap+'.inputValue',f=True)
	mc.setAttr(toeFootRollRemap+'.inputMin',footRollAttrRange*0.5)
	mc.setAttr(toeFootRollRemap+'.inputMax',footRollAttrRange)
	mc.setAttr(toeFootRollRemap+'.outputMin',0.0)
	mc.setAttr(toeFootRollRemap+'.outputMax',footRollAngle*1.5)
	mc.connectAttr(toeFootRollRemap+'.outValue',toeRollAdd+'.input2',f=True)
	mc.connectAttr(toeRollAdd+'.output',toePivot+'.rx',f=True)
	
	mc.connectAttr(ikCtrl+'.footRoll',ballFootRollRemap+'.inputValue',f=True)
	mc.setAttr(ballFootRollRemap+'.inputMin',0.0)
	mc.setAttr(ballFootRollRemap+'.inputMax',footRollAttrRange)
	mc.setAttr(ballFootRollRemap+'.outputMin',0.0)
	mc.setAttr(ballFootRollRemap+'.outputMax',footRollAngle)
	mc.setAttr(ballFootRollRemap+'.value[0].value_Position',0.0)
	mc.setAttr(ballFootRollRemap+'.value[0].value_FloatValue',0.0)
	mc.setAttr(ballFootRollRemap+'.value[0].value_Interp',3)
	mc.setAttr(ballFootRollRemap+'.value[1].value_Position',0.5)
	mc.setAttr(ballFootRollRemap+'.value[1].value_FloatValue',1.0)
	mc.setAttr(ballFootRollRemap+'.value[1].value_Interp',3)
	mc.setAttr(ballFootRollRemap+'.value[2].value_Position',1.0)
	mc.setAttr(ballFootRollRemap+'.value[2].value_FloatValue',0.0)
	mc.setAttr(ballFootRollRemap+'.value[2].value_Interp',3)
	mc.connectAttr(ballFootRollRemap+'.outValue',ballRoll+'.rx',f=True)
	
	mc.connectAttr(ikCtrl+'.footRoll',hellFootRollRemap+'.inputValue',f=True)
	mc.setAttr(hellFootRollRemap+'.inputMin',-footRollAttrRange)
	mc.setAttr(hellFootRollRemap+'.inputMax',0.0)
	mc.setAttr(hellFootRollRemap+'.outputMin',-footRollAngle)
	mc.setAttr(hellFootRollRemap+'.outputMax',0.0)
	mc.connectAttr(hellFootRollRemap+'.outValue',heelPivot+'.rx',f=True)
	
	# Foot Tilt
	innerTiltRemap = mc.createNode('remapValue',n=prefix+'_innerTilt_remapValue')
	outerTiltRemap = mc.createNode('remapValue',n=prefix+'_outerTilt_remapValue')
	
	mc.connectAttr(ikCtrl+'.footTilt',innerTiltRemap+'.inputValue',f=True)
	mc.setAttr(innerTiltRemap+'.inputMin',-footRollAttrRange)
	mc.setAttr(innerTiltRemap+'.inputMax',0.0)
	mc.setAttr(innerTiltRemap+'.outputMin',footTiltAngle)
	mc.setAttr(innerTiltRemap+'.outputMax',0.0)
	mc.connectAttr(innerTiltRemap+'.outValue',innerPivot+'.rz',f=True)
	
	mc.connectAttr(ikCtrl+'.footTilt',outerTiltRemap+'.inputValue',f=True)
	mc.setAttr(outerTiltRemap+'.inputMin',0.0)
	mc.setAttr(outerTiltRemap+'.inputMax',footRollAttrRange)
	mc.setAttr(outerTiltRemap+'.outputMin',0.0)
	mc.setAttr(outerTiltRemap+'.outputMax',-footTiltAngle)
	mc.connectAttr(outerTiltRemap+'.outValue',outerPivot+'.rz',f=True)
	
	# Toe/Ball/Heel Pivot
	toePivotRemap = mc.createNode('remapValue',n=prefix+'_toePivot_remapValue')
	ballPivotRemap = mc.createNode('remapValue',n=prefix+'_ballPivot_remapValue')
	heelPivotRemap = mc.createNode('remapValue',n=prefix+'_heelPivot_remapValue')
	
	mc.connectAttr(ikCtrl+'.toePivot',toePivotRemap+'.inputValue',f=True)
	mc.setAttr(toePivotRemap+'.inputMin',-footRollAttrRange)
	mc.setAttr(toePivotRemap+'.inputMax',footRollAttrRange)
	mc.setAttr(toePivotRemap+'.outputMin',-footPivotAngle)
	mc.setAttr(toePivotRemap+'.outputMax',footPivotAngle)
	mc.connectAttr(toePivotRemap+'.outValue',toePivot+'.ry',f=True)
	
	mc.connectAttr(ikCtrl+'.ballPivot',ballPivotRemap+'.inputValue',f=True)
	mc.setAttr(ballPivotRemap+'.inputMin',-footRollAttrRange)
	mc.setAttr(ballPivotRemap+'.inputMax',footRollAttrRange)
	mc.setAttr(ballPivotRemap+'.outputMin',-footPivotAngle)
	mc.setAttr(ballPivotRemap+'.outputMax',footPivotAngle)
	mc.connectAttr(ballPivotRemap+'.outValue',ballPivot+'.ry',f=True)
	
	mc.connectAttr(ikCtrl+'.heelPivot',heelPivotRemap+'.inputValue',f=True)
	mc.setAttr(heelPivotRemap+'.inputMin',-footRollAttrRange)
	mc.setAttr(heelPivotRemap+'.inputMax',footRollAttrRange)
	mc.setAttr(heelPivotRemap+'.outputMin',-footPivotAngle)
	mc.setAttr(heelPivotRemap+'.outputMax',footPivotAngle)
	mc.connectAttr(heelPivotRemap+'.outValue',heelPivot+'.ry',f=True)
	
	# Toe Tap
	toeTapRemap = mc.createNode('remapValue',n=prefix+'_toeTap_remapValue')
	
	mc.connectAttr(ikCtrl+'.toeTap',toeTapRemap+'.inputValue',f=True)
	mc.setAttr(toeTapRemap+'.inputMin',-footRollAttrRange)
	mc.setAttr(toeTapRemap+'.inputMax',footRollAttrRange)
	mc.setAttr(toeTapRemap+'.outputMin',footTapAngle)
	mc.setAttr(toeTapRemap+'.outputMax',-footTapAngle)
	mc.connectAttr(toeTapRemap+'.outValue',toeTapPivot+'.rx',f=True)
	
	# =====================
	# - Setup Ik/Fk Blend -
	# =====================
	
	# Create blend setup
	fkIkBlend = glTools.rig.utils.ikFkBlend(footJoints,fkJoints,ikJoints,blendCtrl+'.'+blendAttr,True,True,True,True,prefix)
	
	# Setup visibility switch
	visReverse = mc.createNode('reverse',n=prefix+'_ikFkVis_reverse')
	mc.connectAttr(blendCtrl+'.'+blendAttr,visReverse+'.inputX',f=True)
	
	# Define visibility lists
	fkVisNodes = [fkJointGrps[0]]
	ikVisNodes = [ikJointGrp,footIkCtrlGrp]
	for node in fkVisNodes:
		mc.connectAttr(blendCtrl+'.'+blendAttr,node+'.v',f=True)
	for node in ikVisNodes:
		mc.connectAttr(visReverse+'.outputX',node+'.v',f=True)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[footJoint,ballJoint,toeJoint,footJointGrp,ballJointGrp])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[ikJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=ikJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=fkJointGrps)
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=fkJoints)
	chStateUtil.setFlags([2,2,2,0,0,0,2,2,2,1],objectList=[footIkCtrl])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[footIkCtrlGrp])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[limbPivot,ballRoll,toeTapPivot,ballPivot,toePivot,heelPivot,innerPivot,outerPivot,footPivot])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[ballIk,ballIkGrp,toeIk,toeIkGrp])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[attachJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=[attachJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[module,ctrl_grp,rig_grp,skel_grp])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = fkJoints[:-1]
	
	return [module,attachJoint]