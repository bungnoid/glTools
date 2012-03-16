import maya.cmds as mc

import glTools.rig.utils

import glTools.utils.channelState
import glTools.utils.joint

def build(startJoint,endJoint,blendCtrl='',blendAttr='ikFkBlend',side='',prefix=''):
	'''
	Build blendable FK/IK finger setup
	@param startJoint:
	@type startJoint:
	@param endJoint:
	@type endJoint:
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check joints
	if not mc.objExists(startJoint):
		raise Exception('Start joint "'+startJoint+'" does not exist!')
	if not mc.objExists(endJoint):
		raise Exception('End joint "'+endJoint+'" does not exist!')
	
	# Check blendCtrl
	if blendCtrl and not mc.objExists(blendCtrl):
		raise Exception('Blend control "'+blendCtrl+'" does not exist!')
	
	# Check side
	if (side != 'lf') and (side != 'rt'):
		raise Exception('Invalid side argument value!')
	
	# ====================
	# - Configure Module -
	# ====================
	
	fkCtrlScale = 0.75
	ikCtrlScale = 0.5
	ikTipScale = 0.25
	
	ikfkDefault = 1
	
	if side == 'lf': fkCtrlSpin = 180
	else: fkCtrlSpin = 0
	
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
	
	# =================
	# - Create Joints -
	# =================
	
	# Get joint list
	fingerJoints = glTools.utils.joint.getJointList(startJoint,endJoint)
	
	# Create IK Joints
	ikJoints = glTools.utils.joint.duplicateChain(startJoint,endJoint,prefix=prefix+'_ik')
	ikJointGrp = glTools.utils.joint.group(ikJoints[0])
	
	# Create FK Joints
	fkJoints = glTools.utils.joint.duplicateChain(startJoint,endJoint,prefix=prefix+'_fk')
	fkJointGrps = [glTools.utils.joint.group(i) for i in fkJoints]
	
	# Create Limb Joint Groups
	fingerJointGrps = [glTools.utils.joint.group(i) for i in fingerJoints]
	
	# =======================
	# - Create Attach Joint -
	# =======================
	
	mc.select(cl=True)
	
	# Attach joint
	attachJoint = mc.joint(n=prefix+'_attachA_jnt')
	attachJointGrp = glTools.utils.joint.group(attachJoint)
	mc.delete(mc.parentConstraint(fingerJoints[0],attachJointGrp))
	
	# Attach joint display
	mc.setAttr(attachJoint+'.overrideEnabled',1)
	mc.setAttr(attachJoint+'.overrideLevelOfDetail',1)
	
	# Parent attach joint
	mc.parent([fingerJointGrps[0],fkJointGrps[0],ikJointGrp],attachJoint)
	mc.parent(attachJointGrp,skel_grp)
	
	# ==================
	# - Build Controls -
	# ==================
	
	# Initialize control builder
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	# Define finger tip length
	tipLen = glTools.utils.joint.length(fingerJoints[-2])
	
	# FK Controls
	for jnt in fkJoints[:-1]:
		jntLen = glTools.utils.joint.length(jnt)
		glTools.tools.controlBuilder.controlShape(jnt,'crescent',rotate=[fkCtrlSpin,90,0],scale=tipLen*fkCtrlScale)
		glTools.rig.utils.tagCtrl(jnt,'secondary')
	
	# IK Control
	#ikCtrl = ctrlBuilder.create('circle',prefix+'_ik_ctrl',translate=[tipLen*.5,tipLen*.75,0],rotate=[0,90,90],scale=tipLen*ikCtrlScale)
	ikCtrl = ctrlBuilder.create('circle',prefix+'_ik_ctrl',rotate=[0,90,90],scale=tipLen*ikCtrlScale)
	ikCtrlGrp = glTools.utils.base.group(ikCtrl,name=ikCtrl+'Grp')
	glTools.rig.utils.tagCtrl(ikCtrl,'secondary')
	mc.delete(mc.pointConstraint(fingerJoints[-2],ikCtrlGrp))
	mc.delete(mc.orientConstraint(fingerJoints[-2],ikCtrlGrp))
	
	# IK Tip Control
	tipCtrl = ctrlBuilder.create('sphere',prefix+'_tip_ctrl',scale=tipLen*ikTipScale)
	tipCtrlGrp = glTools.utils.base.group(tipCtrl,name=tipCtrl+'Grp')
	glTools.rig.utils.tagCtrl(tipCtrl,'secondary')
	mc.delete(mc.pointConstraint(fingerJoints[-1],tipCtrlGrp))
	mc.delete(mc.orientConstraint(fingerJoints[-1],tipCtrlGrp))
	
	# Parent Controls
	mc.parent(tipCtrlGrp,ikCtrl)
	mc.parent(ikCtrlGrp,ctrl_grp)
	
	# =====================
	# - Setup Ik/Fk Blend -
	# =====================
	
	# Create blend setup
	fkIkBlend = glTools.rig.utils.ikFkBlend(fingerJoints,fkJoints,ikJoints,blendCtrl+'.'+blendAttr,translate=True,rotate=True,scale=True,skipEnd=True,prefix=prefix)
	mc.setAttr(blendCtrl+'.'+blendAttr,ikfkDefault)
	
	# Setup visibility switch
	visReverse = mc.createNode('reverse',n=prefix+'_ikFkVis_reverse')
	mc.connectAttr(blendCtrl+'.'+blendAttr,visReverse+'.inputX',f=True)
	
	# Define visibility lists
	fkVisNodes = [fkJointGrps[0]]
	ikVisNodes = [ikJointGrp,ikCtrl,tipCtrl]
	for node in fkVisNodes:
		mc.connectAttr(blendCtrl+'.'+blendAttr,node+'.v',f=True)
	for node in ikVisNodes:
		mc.connectAttr(visReverse+'.outputX',node+'.v',f=True)
	
	# ===================
	# - Build IK Handle -
	# ===================
	
	ikHandle = glTools.tools.ikHandle.build(ikJoints[0],ikJoints[-2],solver='ikSCsolver',prefix=prefix)
	ikHandleGrp = glTools.utils.base.group(ikHandle,name=ikHandle+'Grp')
	mc.setAttr(ikHandleGrp+'.v',0)
	
	tipIkHandle = glTools.tools.ikHandle.build(ikJoints[-2],ikJoints[-1],solver='ikSCsolver',prefix=prefix+'Tip')
	tipIkHandleGrp = glTools.utils.base.group(tipIkHandle,name=tipIkHandle+'Grp')
	mc.setAttr(tipIkHandleGrp+'.v',0)
	
	# Parent to controls
	mc.parent([ikHandleGrp,tipIkHandleGrp],tipCtrl)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=fingerJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=fingerJointGrps)
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=fkJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=fkJointGrps)
	chStateUtil.setFlags([2,2,2,1,1,1,1,1,1,1],objectList=ikJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=ikJointGrp)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[ikHandle,ikHandleGrp,tipIkHandle,tipIkHandleGrp])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[ikCtrlGrp,tipCtrlGrp])
	chStateUtil.setFlags([0,0,0,0,0,0,2,2,2,1],objectList=[ikCtrl])
	chStateUtil.setFlags([2,2,2,0,0,0,2,2,2,1],objectList=[tipCtrl])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[attachJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=[attachJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[module,ctrl_grp,rig_grp,skel_grp])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = fkJoints[:-1]
	ctrlList.append(ikCtrl)
	ctrlList.append(tipCtrl)
	
	return [module,attachJoint]