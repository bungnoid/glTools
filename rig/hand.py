import maya.cmds as mc

import glTools.rig.attach
import glTools.rig.finger
import glTools.rig.fkChain
import glTools.rig.utils

import glTools.tools.controlBuilder

import glTools.utils.attribute
import glTools.utils.channelState
import glTools.utils.joint

def build_fkFingers(handJoint,fingerBaseJoints=[],fingerEndJoints=[],fingerPrefixList=[],prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check side
	if (side != 'lf') and (side != 'rt'):
		raise Exception('Invalid side argument! "'+side+'"')
	
	# Check hand joint
	if not mc.objExists(handJoint):
		raise Exception('Hand joint "'+handJoint+'" does not exist!')
	
	# Check Fingers Lists
	if len(fingerBaseJoints) != len(fingerStartJoints):
		raise Exception('Finger list length mis-match!')
	if len(fingerEndJoints) != len(fingerPrefixList):
		raise Exception('Finger list length mis-match!')
	
	# Check Fingers Joint
	for fingerJoint in fingerBaseJoints:
		if not mc.objExists(fingerJoint):
			raise Exception('Finger base joint "'+fingerJoint+'" does not exist!')
	
	for fingerJoint in fingerEndJoints:
		if not mc.objExists(fingerJoint):
			raise Exception('Finger end joint "'+fingerJoint+'" does not exist!')
	
	# ==================
	# - Configure Hand -
	# ==================
	
	fingerCtrlScale = 1
	
	# =======================
	# - Build Base Hand Rig -
	# =======================
	
	hand_base = build_base(handJoint,prefix)
	hand_module = hand_base[0]
	hand_attach = hand_base[1]
	hand_ctrl_grp = prefix+'_ctrl_grp'
	hand_rig_grp = prefix+'_rig_grp'
	hand_skel_grp = prefix+'_skel_grp'
	hand_subModule_grp = mc.group(em=True,n=prefix+'_subModule_grp',p=hand_module)
	
	# =================
	# - Build Fingers -
	# =================
	
	# For Each Finger
	for i in fingerBaseJoints:
		
		# Construct finger prefix
		fingerPrefix = side+'_'+fingerPrefixList[i]
		
		# Build Finger Module
		finger = glTools.rig.fkChain.build(fingerBaseJoints[i],fingerEndJoints[i],controlShape='circle',endCtrl=False,ctrlRotate=[0,90,0],ctrlOrient=True,ctrlScale=1.0,ctrlLod='secondary',prefix=fingerPrefix)
		finger_module = finger[0]
		finger_attach = finger[1]
		
		# Parent Finger Module
		mc.parent(finger_module,hand_subModule_grp)
		
		# Attach Finger Module
		glTools.rig.attach.switchConstraint('parent',finger_attach,[handJoint],prefix=fingerPrefix+'Attach')
		
		# Uniform Scale
		mc.connectAttr(hand_module+'.uniformScale',finger_module+'.uniformScale',f=True)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	
	# =================
	# - Return Result -
	# =================
	
	return hand_base


def build_ikFingers(handJoint,fingerBaseJoints,fingerStartJoints,fingerEndJoints,fingerPrefixList,blendCtrl='',side='',prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check side
	if (side != 'lf') and (side != 'rt'):
		raise Exception('Invalid side argument! "'+side+'"')
	
	# Check hand joint
	if not mc.objExists(handJoint):
		raise Exception('Hand joint "'+handJoint+'" does not exist!')
	
	# Check Fingers Lists
	if len(fingerBaseJoints) != len(fingerStartJoints):
		raise Exception('Finger list length mis-match!')
	if len(fingerStartJoints) != len(fingerEndJoints):
		raise Exception('Finger list length mis-match!')
	if len(fingerEndJoints) != len(fingerPrefixList):
		raise Exception('Finger list length mis-match!')
	
	# Check Fingers Joint
	for fingerJoint in fingerBaseJoints:
		if not fingerJoint:
			if blendCtrl: continue
			else: raise Exception('Finger base joint "'+fingerJoint+'" does not exist!')
		if not mc.objExists(fingerJoint):
			raise Exception('Finger base joint "'+fingerJoint+'" does not exist!')
	
	for fingerJoint in fingerStartJoints:
		if not mc.objExists(fingerJoint):
			raise Exception('Finger start joint "'+fingerJoint+'" does not exist!')
	
	for fingerJoint in fingerEndJoints:
		if not mc.objExists(fingerJoint):
			raise Exception('Finger end joint "'+fingerJoint+'" does not exist!')
	
	# ==================
	# - Configure Hand -
	# ==================
	
	fingerIkParentCtrlScale = 2
	fingerBaseCtrlScale = 0.5
	
	ikParentTipID = 2
	
	if side == 'lf': ikParentSpin = -90
	else: ikParentSpin = 90
	
	# =======================
	# - Build Base Hand Rig -
	# =======================
	
	hand_base = build_base(handJoint,prefix)
	hand_module = hand_base[0]
	hand_attach = hand_base[1]
	hand_ctrl_grp = prefix+'_ctrl_grp'
	hand_rig_grp = prefix+'_rig_grp'
	hand_skel_grp = prefix+'_skel_grp'
	hand_subModule_grp = mc.group(em=True,n=prefix+'_subModule_grp',p=hand_module)

	# ==================================
	# - Build Finger IK Parent Control -
	# ==================================
	
	# Initialize control builder
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	# Create Control
	handScale = glTools.utils.joint.length(fingerBaseJoints[1])
	ikParentCtrl = ctrlBuilder.create('crescent',prefix+'_fingerIk_ctrl',rotate=[0,0,ikParentSpin],scale=handScale*fingerIkParentCtrlScale)
	ikParentCtrlGrp = glTools.utils.base.group(ikParentCtrl,name=ikParentCtrl+'Grp')
	glTools.rig.utils.tagCtrl(ikParentCtrl,'primary')
	
	# Position Control
	mc.delete(mc.pointConstraint(fingerEndJoints[ikParentTipID],ikParentCtrlGrp,mo=False))
	mc.delete(mc.orientConstraint(handJoint,ikParentCtrlGrp,mo=False))
	
	# Parent Control
	mc.parentConstraint(handJoint,ikParentCtrlGrp,mo=True)
	mc.parent(ikParentCtrlGrp,hand_ctrl_grp)
	
	# Connect visibility
	if blendCtrl:
		mc.addAttr(blendCtrl,ln='fingerIkParentVis',at='long',min=0,max=1,dv=0,k=True)
		mc.connectAttr(blendCtrl+'.fingerIkParentVis',ikParentCtrl+'.v',f=True)
	
	# =================
	# - Build Fingers -
	# =================
	
	# For Each Finger
	fingerBaseJointGrps = []
	for i in range(len(fingerBaseJoints)):
		
		# Construct finger prefix
		fingerPrefix = side+'_'+fingerPrefixList[i]
		
		# Build Finger Base Control
		if fingerBaseJoints[i]:
			jntLen = glTools.utils.joint.length(fingerBaseJoints[i])
			glTools.tools.controlBuilder.controlShape(fingerBaseJoints[i],'anchor',rotate=[180,90,0],scale=jntLen*fingerBaseCtrlScale)
			fingerBaseJointGrps.append(glTools.utils.joint.group(fingerBaseJoints[i]))
			glTools.rig.utils.tagCtrl(fingerBaseJoints[i],'secondary')
		
		# Build Finger Module
		if not blendCtrl:
			fingerBlendCtrl = fingerBaseJoints[i]
			fingerBlendAttr = 'fingerIK'
		else:
			fingerBlendCtrl = blendCtrl
			fingerBlendAttr = fingerPrefixList[i]+'FK'
		finger = glTools.rig.finger.build(fingerStartJoints[i],fingerEndJoints[i],fingerBlendCtrl,fingerBlendAttr,side,fingerPrefix)
		finger_module = finger[0]
		finger_attach = finger[1]
		
		# Parent Finger Module
		mc.parent(finger_module,hand_subModule_grp)
		
		# Attach Finger Module
		if fingerBaseJoints[i]:
			glTools.rig.attach.switchConstraint('parent',finger_attach,[fingerBaseJoints[i]],createTarget=True,prefix=fingerPrefix+'Attach')
		else:
			glTools.rig.attach.switchConstraint('parent',finger_attach,[handJoint],createTarget=True,prefix=fingerPrefix+'Attach')
		glTools.rig.attach.switchConstraint('parent',fingerPrefix+'_ik_ctrlGrp',[ikParentCtrl],createTarget=True,prefix=fingerPrefix+'IkParentAttach')
		
		# Uniform Scale
		mc.connectAttr(hand_module+'.uniformScale',finger_module+'.uniformScale',f=True)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[ikParentCtrlGrp])
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=[ikParentCtrl])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=fingerBaseJointGrps)
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=fingerBaseJoints)
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = []
	
	return hand_base

def build_base(handJoint,prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(handJoint):
		raise Exception('Hand joint "'+handJoint+'" does not exist!')
		
	# ==================
	# - Configure Hand -
	# ==================
	
	# Control Scale
	handCtrlScale = 2
	
	# ==========================
	# - Build Module Structure -
	# ==========================
	
	# Create control group
	ctrl_grp = mc.group(em=True,n=prefix+'_ctrl_grp',w=True)
	
	# Create rig group
	rig_grp = mc.group(em=True,n=prefix+'_rig_grp',w=True)
	
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
	
	# =====================
	# - Create Hand Joint -
	# =====================
	
	handJointLen = glTools.utils.joint.length(handJoint)
	handJointShape = glTools.tools.controlBuilder.controlShape(handJoint,'circle',rotate=[0,90,0],scale=handJointLen*handCtrlScale)
	handJointGrp = glTools.utils.joint.group(handJoint)
	glTools.rig.utils.tagCtrl(handJoint,'primary')
	
	# =======================
	# - Create Attach Joint -
	# =======================
	
	mc.select(cl=True)
	
	# Create attach
	attachJoint = mc.joint(n=prefix+'_attachA_jnt')
	attachJointGrp = glTools.utils.joint.group(attachJoint)
	mc.delete(mc.parentConstraint(handJoint,attachJointGrp))
	
	# Attach joint display
	mc.setAttr(attachJoint+'.overrideEnabled',1)
	mc.setAttr(attachJoint+'.overrideLevelOfDetail',1)
	
	# Parent attach joint
	mc.parent(handJointGrp,attachJoint)
	mc.parent(attachJointGrp,skel_grp)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=[handJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[handJointGrp])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[attachJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=[attachJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[module,ctrl_grp,rig_grp,skel_grp])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = handJoint
	
	# Return result
	return [module,attachJoint]