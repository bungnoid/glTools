import maya.cmds as mc

import glTools.utils.base
import glTools.utils.joint
import glTools.utils.stringUtils
import glTools.utils.transform

import glTools.tools.controlBuilder
import glTools.tools.ikHandle

import glTools.rig.utils

def build(startJoint,endJoint,limbEnd='',blendCtrl='',blendAttr='ikFkBlend',orientIkCtrl=True,prefix=''):
	'''
	Build a basic limb module with 3 chain IK/FK blending.
	@param startJoint: Limb start joint
	@type startJoint: str
	@param endJoint: Limb end joint
	@type endJoint: str
	@param limbEnd: Limb hand or foot transform
	@type limbEnd: str
	@param blendCtrl: Limb start joint
	@type blendCtrl: str
	@param blendAttr: Limb start joint
	@type blendAttr: str
	@param orientIkCtrl: Limb start joint
	@type orientIkCtrl: bool
	@param prefix: Name prefix for new nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(startJoint):
		raise Exception('Start joint "'+startJoint+'" does not exist!')
	if not mc.objExists(endJoint):
		raise Exception('End joint "'+endJoint+'" does not exist!')
	if blendCtrl and not mc.objExists(blendCtrl):
		raise Exception('Blend control "'+blendCtrl+'" does not exist!')
		
	if not limbEnd: limbEnd = endJoint
	
	# ====================
	# - Configure Module -
	# ====================
	
	fkCtrlScale = 0.5
	
	ikWristScale = 0.2
	poleVecScale = 0.075
	poleVecLen = 1.0
	
	# Limb mid joint index - For poleVector position
	midID = 1
	
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
	limbJoints = glTools.utils.joint.getJointList(startJoint,endJoint)
	
	# Create IK Joints
	ikJoints = glTools.utils.joint.duplicateChain(startJoint,endJoint,prefix=prefix+'_ik')
	ikJointGrp = glTools.utils.joint.group(ikJoints[0])
	
	# Create FK Joints
	fkJoints = glTools.utils.joint.duplicateChain(startJoint,endJoint,prefix=prefix+'_fk')
	fkJointGrps = [glTools.utils.joint.group(i) for i in fkJoints]
	
	# Create Limb Joint Groups
	limbJointGrps = [glTools.utils.joint.group(i) for i in limbJoints]
	
	# =======================
	# - Create Attach Joint -
	# =======================
	
	mc.select(cl=True)
	
	# Attach joint
	attachJoint = mc.joint(n=prefix+'_attachA_jnt')
	attachJointGrp = glTools.utils.joint.group(attachJoint)
	mc.delete(mc.parentConstraint(limbJoints[0],attachJointGrp))
	
	# Attach joint display
	mc.setAttr(attachJoint+'.overrideEnabled',1)
	mc.setAttr(attachJoint+'.overrideLevelOfDetail',1)
	
	# Parent attach joint
	mc.parent([limbJointGrps[0],fkJointGrps[0],ikJointGrp],attachJoint)
	mc.parent(attachJointGrp,skel_grp)
	
	# ==================
	# - Build Controls -
	# ==================
	
	# Initialize control builder
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	# Define limb length
	limbLen = glTools.utils.joint.length(limbJoints[0]) + glTools.utils.joint.length(limbJoints[1])
	
	# FK Controls
	for jnt in fkJoints[:-1]:
		
		jntLen = glTools.utils.joint.length(jnt)
		glTools.tools.controlBuilder.controlShape(jnt,'circle',rotate=[0,90,0],scale=jntLen*fkCtrlScale)
		glTools.rig.utils.tagCtrl(jnt,'primary')
	
	# IK Control
	ikCtrl = ctrlBuilder.create('box',prefix+'_ik_ctrl',scale=limbLen*ikWristScale)
	ikCtrlGrp = glTools.utils.base.group(ikCtrl,name=ikCtrl+'Grp')
	glTools.rig.utils.tagCtrl(ikCtrl,'primary')
	# Position Control
	if orientIkCtrl:
		glTools.utils.transform.match(ikCtrlGrp,limbEnd)
	else:
		mc.delete(mc.pointConstraint(limbEnd,ikCtrlGrp,mo=False))
	
	# Pole Vector Control
	pvCtrl = ctrlBuilder.create('sphere',prefix+'_pv_ctrl',scale=limbLen*poleVecScale)
	glTools.tools.controlBuilder.anchorCurve(pvCtrl,ikJoints[midID],template=True)
	glTools.rig.utils.tagCtrl(pvCtrl,'primary')
	pvCtrlGrp = glTools.utils.base.group(pvCtrl,name=pvCtrl+'Grp')
	pvPos = glTools.rig.utils.poleVectorPosition(ikJoints[0],ikJoints[midID],ikJoints[-1],distance=poleVecLen)
	mc.move(pvPos[0],pvPos[1],pvPos[2],pvCtrlGrp,ws=True,a=True)
	
	# Parent Controls
	mc.parent([ikCtrlGrp,pvCtrlGrp],ctrl_grp)
	
	# =====================
	# - Setup Ik/Fk Blend -
	# =====================
	
	# Create blend setup
	fkIkBlend = glTools.rig.utils.ikFkBlend(limbJoints,fkJoints,ikJoints,blendCtrl+'.'+blendAttr,True,True,True,True,prefix)
	
	# Setup visibility switch
	visReverse = mc.createNode('reverse',n=prefix+'_ikFkVis_reverse')
	mc.connectAttr(blendCtrl+'.'+blendAttr,visReverse+'.inputX',f=True)
	
	# Define visibility lists
	fkVisNodes = [fkJointGrps[0]]
	ikVisNodes = [ikJointGrp,ikCtrl,pvCtrl]
	for node in fkVisNodes:
		mc.connectAttr(blendCtrl+'.'+blendAttr,node+'.v',f=True)
	for node in ikVisNodes:
		mc.connectAttr(visReverse+'.outputX',node+'.v',f=True)
	
	# ===============================
	# - Setup Limb End/Follow Blend -
	# ===============================
	
	# Create Limb End/Follow Joints
	limbEndJoint = mc.duplicate(endJoint,po=True,n=prefix+'_limbEnd_jnt')[0]
	limbFkFollowJoint = mc.duplicate(endJoint,po=True,n=prefix+'_limbFkFollow_jnt')[0]
	limbIkFollowJoint = mc.duplicate(endJoint,po=True,n=prefix+'_limbIkFollow_jnt')[0]
	mc.parent([limbEndJoint,limbFkFollowJoint,limbIkFollowJoint],w=True)
	mc.makeIdentity(limbEndJoint,apply=True,t=True,r=True,s=True,jo=True,n=False)
	mc.makeIdentity(limbFkFollowJoint,apply=True,t=True,r=True,s=True,jo=True,n=False)
	mc.makeIdentity(limbIkFollowJoint,apply=True,t=True,r=True,s=True,jo=True,n=False)
	
	# Orient Joints
	mc.delete(mc.orientConstraint(limbEnd,limbEndJoint))
	mc.delete(mc.orientConstraint(limbEnd,limbFkFollowJoint))
	mc.delete(mc.orientConstraint(limbEnd,limbIkFollowJoint))
	
	# Parent Joints to Limb
	mc.parent([limbEndJoint,limbFkFollowJoint],endJoint)
	mc.parent([limbEndJoint,limbIkFollowJoint],ikCtrl)
	
	# Create Constraint
	limbEndConstraint = mc.orientConstraint([limbIkFollowJoint,limbFkFollowJoint],limbEndJoint,mo=False)[0]
	limbEndAlias = mc.orientConstraint(limbEndConstraint,q=True,wal=True)
	
	# Setup Constraint Blend
	limbEndReverse = mc.createNode('reverse',n=prefix+'_limbEndBlend_reverse')
	mc.connectAttr(blendCtrl+'.'+blendAttr,limbEndReverse+'.inputX',f=True)
	mc.connectAttr(blendCtrl+'.'+blendAttr,limbEndConstraint+'.'+limbEndAlias[1],f=True)
	mc.connectAttr(limbEndReverse+'.outputX',limbEndConstraint+'.'+limbEndAlias[0],f=True)
	
	# ===================
	# - Build IK Handle -
	# ===================
	
	ikHandle = glTools.tools.ikHandle.build(ikJoints[0],ikJoints[-1],solver='ikRPsolver',prefix=prefix)
	ikHandleGrp = glTools.utils.base.group(ikHandle,name=ikHandle+'Grp')
	mc.setAttr(ikHandleGrp+'.v',0)
	
	# Parent to control
	mc.parent(ikHandleGrp,ikCtrl)
	
	# Connect to control
	if not mc.objExists(ikCtrl+'.twist'):
		mc.addAttr(ikCtrl,ln='twist',min=-360,max=360,dv=0,k=True)
	mc.connectAttr(ikCtrl+'.twist',ikHandle+'.twist',f=True)
	
	# Constrain poleVector
	pvCon = mc.poleVectorConstraint(pvCtrl,ikHandle)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=limbJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=limbJointGrps)
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=fkJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=fkJointGrps)
	chStateUtil.setFlags([2,2,2,1,1,1,1,1,1,1],objectList=ikJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=ikJointGrp)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[limbEndJoint,limbFkFollowJoint,limbIkFollowJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[ikHandle,ikHandleGrp])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[ikCtrlGrp,pvCtrlGrp])
	chStateUtil.setFlags([0,0,0,0,0,0,2,2,2,1],objectList=[ikCtrl])
	chStateUtil.setFlags([0,0,0,2,2,2,2,2,2,1],objectList=[pvCtrl])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[attachJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=[attachJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[module,ctrl_grp,rig_grp,skel_grp])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = fkJoints[:-1]
	ctrlList.append(ikCtrl)
	ctrlList.append(pvCtrl)
	
	return [module,attachJoint]