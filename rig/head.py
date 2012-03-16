import maya.cmds as mc

import glTools.utils.channelState
import glTools.utils.joint
import glTools.utils.transform

def build(headJoint,jawJoint='',lfEyeJoint='',rtEyeJoint='',prefix='cn_head'):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(headJoint):
		raise Exception('Head joint "'+headJoint+'" does not exist!')
	if jawJoint and not mc.objExists(jawJoint):
		raise Exception('Jaw joint "'+jawJoint+'" does not exist!')
	if lfEyeJoint and not mc.objExists(lfEyeJoint):
		raise Exception('Left Eye joint "'+lfEyeJoint+'" does not exist!')
	if rtEyeJoint and not mc.objExists(rtEyeJoint):
		raise Exception('Reft Eye joint "'+rtEyeJoint+'" does not exist!')
	
	# ==================
	# - Configure Head -
	# ==================
	
	headCtrlScale = 1
	
	jawTransCtrlScale = .35
	jawRotateCtrlScale = 1
	
	lfEyeCtrlScale = 1
	rtEyeCtrlScale = 1
	lfEyePrefix = 'lf_eye'
	rtEyePrefix = 'rt_eye'
	
	orientJawCtrl = False
	
	headAimOffset = 10
	headAimVec = (0,0,1)
	headUpVec = (1,0,0)
	headWorldUpVec = (0,1,0)
	
	eyeAimVec = (1,0,0)
	eyeUpVec = (0,1,0)
	eyeWorldUpVec = (0,1,0)
	
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
	
	# ======================
	# - Create Head Joints -
	# ======================
	
	# Head
	headJointLen = glTools.utils.joint.length(headJoint)
	headJointShape = glTools.tools.controlBuilder.controlShape(headJoint,'box',scale=headJointLen*headCtrlScale)
	glTools.rig.utils.tagCtrl(headJoint,'primary')
	headJointGrp = glTools.utils.joint.group(headJoint)
	headAimGrp = glTools.utils.joint.group(headJoint,indexStr='Aim')
	
	# Jaw
	if jawJoint:
		jawJointGrp = glTools.utils.joint.group(jawJoint)
	
	# Left Eye
	if lfEyeJoint:
		jntLen = glTools.utils.joint.length(lfEyeJoint)
		lfEyeJointShape = glTools.tools.controlBuilder.controlShape(lfEyeJoint,'arrow',translate=(jntLen*2,0,0),rotate=(0,90,0),scale=jntLen*lfEyeCtrlScale)
		glTools.rig.utils.tagCtrl(lfEyeJoint,'primary')
		lfEyeJointGrp = glTools.utils.joint.group(lfEyeJoint)
		lfEyeAimGrp = glTools.utils.joint.group(lfEyeJoint,indexStr='Aim')
	# Right Eye
	if rtEyeJoint:
		jntLen = glTools.utils.joint.length(rtEyeJoint)
		rtEyeJointShape = glTools.tools.controlBuilder.controlShape(rtEyeJoint,'arrow',translate=(jntLen*2,0,0),rotate=(0,90,0),scale=jntLen*rtEyeCtrlScale)
		rtEyeJointGrp = glTools.utils.joint.group(rtEyeJoint)
		glTools.rig.utils.tagCtrl(rtEyeJoint,'primary')
		rtEyeAimGrp = glTools.utils.joint.group(rtEyeJoint,indexStr='Aim')
	
	# =======================
	# - Create Attach Joint -
	# =======================
	
	mc.select(cl=True)
	
	# Attach joint
	attachJoint = mc.joint(n=prefix+'_attachA_jnt')
	attachJointGrp = glTools.utils.joint.group(attachJoint)
	mc.delete(mc.pointConstraint(headJoint,attachJointGrp))
	
	# Attach joint display
	mc.setAttr(attachJoint+'.overrideEnabled',1)
	mc.setAttr(attachJoint+'.overrideLevelOfDetail',1)
	
	# Parent attach joint
	mc.parent(headJointGrp,attachJoint)
	mc.parent(attachJointGrp,skel_grp)
	
	# =======================
	# - Create Jaw Controls -
	# =======================
	
	# Initialize control builder
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	if jawJoint:
	
		# Calculate joint length
		jntLen = glTools.utils.joint.length(jawJoint)
		jawEnd = mc.listRelatives(jawJoint,c=True,type='joint')
		if not jawEnd: raise Exception('Jaw end joint not found!')
		else: jawEnd = jawEnd[0]
		
		# Rotate control
		jawRotateCtrl = ctrlBuilder.create('arch',prefix+'_jaw_ctrl',rotate=(90,0,90),scale=jntLen*jawRotateCtrlScale)
		jawRotateCtrlGrp = glTools.utils.base.group(jawRotateCtrl,name=prefix+'_jaw_ctrlGrp')
		glTools.rig.utils.tagCtrl(jawRotateCtrl,'primary')
		# Orient control
		if orientJawCtrl: mc.delete(mc.orientConstraint(startJoint,jawRotateCtrlGrp,mo=False))
		
		# Translate control
		jawTransCtrl = ctrlBuilder.create('box',prefix+'_jawIk_ctrl',scale=jntLen*jawTransCtrlScale)
		jawTransCtrlGrp = glTools.utils.base.group(jawTransCtrl,name=prefix+'_jawIk_ctrlGrp')
		glTools.rig.utils.tagCtrl(jawTransCtrl,'primary')
		
		# Position Controls
		pt = glTools.utils.base.getPosition(jawJoint)
		mc.move(pt[0],pt[1],pt[2],jawRotateCtrlGrp,ws=True,a=True)
		pt = glTools.utils.base.getPosition(jawEnd)
		mc.move(pt[0],pt[1],pt[2],jawTransCtrlGrp,ws=True,a=True)
		
		# Parent Controls
		mc.parent(jawTransCtrlGrp,jawRotateCtrl)
		mc.parent(jawRotateCtrlGrp,ctrl_grp)
		
		# Constrain to Control
		mc.pointConstraint(jawRotateCtrl,jawJoint)
		mc.parentConstraint(headJoint,jawRotateCtrlGrp,mo=True)
	
	# ================
	# - Build Jaw IK -
	# ================
	
	# Create ikHandle
	jawIk = glTools.tools.ikHandle.build(jawJoint,jawEnd,solver='ikSCsolver',prefix=prefix+'_jaw')
	
	# Parent ikHandle
	jawIkGrp = glTools.utils.base.group(jawIk,name=prefix+'_ikHandle_grp')
	mc.parent(jawIkGrp,jawTransCtrl)
	mc.setAttr(jawIkGrp+'.v',0)
	
	# ========================
	# - Build Head Aim Setup -
	# ========================
	
	# Create Aim Joints
	headAimXform = mc.duplicate(headAimGrp,po=True,n=prefix+'_aimFollow_jnt')[0]
	headFollowXform = mc.duplicate(headAimGrp,po=True,n=prefix+'_headFollow_jnt')[0]
	
	# Create control
	headJointLen = glTools.utils.joint.length(headJoint)
	headAimCtrl = ctrlBuilder.create('face',prefix+'_aim_ctrl',scale=headJointLen*headCtrlScale)
	headAimCtrlShape = mc.listRelatives(headAimCtrl,s=True,pa=True)
	headAimCtrlGrp = glTools.utils.base.group(headAimCtrl,name=prefix+'_aim_ctrlGrp')
	glTools.rig.utils.tagCtrl(headAimCtrl,'primary')
	
	# Position control
	pt = glTools.utils.base.getPosition(headJoint)
	vec = glTools.utils.transform.axisVector(headJoint,'z',normalize=True)
	headAimOffset *= headJointLen
	mc.move(pt[0]+(vec[0]*headAimOffset),pt[1]+(vec[1]*headAimOffset),pt[2]+(vec[2]*headAimOffset),headAimCtrlGrp,ws=True,a=True)
	
	# Create Aim Constraint
	headAimConstraint = mc.aimConstraint(headAimCtrl,headAimXform,aim=headAimVec,u=headUpVec,wu=headWorldUpVec,wuo=headAimCtrl)[0]
	
	# Create Aim Blend Constraint
	headAimBlendConstraint = mc.orientConstraint([headFollowXform,headAimXform],headAimGrp)[0]
	headAimBlendAlias = mc.orientConstraint(headAimBlendConstraint,q=True,wal=True)
	
	# Connect Blend Aim Constraint
	mc.addAttr(headJoint,ln='aim',min=0.0,max=1.0,dv=0.0,k=True)
	headAimReverse = mc.createNode('reverse',n=prefix+'_aimBlend_reverse')
	mc.connectAttr(headJoint+'.aim',headAimReverse+'.inputX',f=True)
	mc.connectAttr(headJoint+'.aim',headAimBlendConstraint+'.'+headAimBlendAlias[1],f=True)
	mc.connectAttr(headAimReverse+'.outputX',headAimBlendConstraint+'.'+headAimBlendAlias[0],f=True)
	mc.connectAttr(headJoint+'.aim',headAimCtrlShape[0]+'.v',f=True)
	
	# Parent to Control Group
	mc.parent(headAimCtrlGrp,ctrl_grp)
	
	# =======================
	# - Build Eye Aim Setup -
	# =======================
	
	if lfEyeJoint:
		
		# Create Aim Joints
		lfEyeAimXform = mc.duplicate(lfEyeAimGrp,po=True,n=lfEyePrefix+'_aimFollow_jnt')[0]
		lfEyeFollowXform = mc.duplicate(lfEyeAimGrp,po=True,n=lfEyePrefix+'_headFollow_jnt')[0]
		
		# Create control
		lfEyeJointLen = glTools.utils.joint.length(lfEyeJoint)
		lfEyeAimCtrl = ctrlBuilder.create('eye',lfEyePrefix+'_aim_ctrl',scale=lfEyeJointLen*lfEyeCtrlScale)
		lfEyeAimCtrlShape = mc.listRelatives(lfEyeAimCtrl,s=True,pa=True)
		lfEyeAimCtrlGrp = glTools.utils.base.group(lfEyeAimCtrl,name=lfEyePrefix+'_aim_ctrlGrp')
		glTools.rig.utils.tagCtrl(lfEyeAimCtrl,'primary')
		
		# Position control
		pt = glTools.utils.base.getPosition(lfEyeJoint)
		vec = glTools.utils.transform.axisVector(lfEyeJoint,'x',normalize=True)
		mc.move(pt[0]+(vec[0]*headAimOffset),pt[1]+(vec[1]*headAimOffset),pt[2]+(vec[2]*headAimOffset),lfEyeAimCtrlGrp,ws=True,a=True)
		
		# Create Aim Constraint
		lfEyeAimConstraint = mc.aimConstraint(lfEyeAimCtrl,lfEyeAimXform,aim=eyeAimVec,u=eyeUpVec,wu=eyeWorldUpVec,wuo=lfEyeAimCtrl)[0]
		
		# Create Aim Blend Constraint
		lfEyeAimBlendConstraint = mc.orientConstraint([lfEyeFollowXform,lfEyeAimXform],lfEyeAimGrp)[0]
		lfEyeAimBlendAlias = mc.orientConstraint(lfEyeAimBlendConstraint,q=True,wal=True)
		
		# Connect Blend Aim Constraint
		mc.addAttr(lfEyeJoint,ln='aim',min=0.0,max=1.0,dv=0.0,k=True)
		lfEyeAimReverse = mc.createNode('reverse',n=lfEyePrefix+'_aimBlend_reverse')
		mc.connectAttr(lfEyeJoint+'.aim',lfEyeAimReverse+'.inputX',f=True)
		mc.connectAttr(lfEyeJoint+'.aim',lfEyeAimBlendConstraint+'.'+lfEyeAimBlendAlias[1],f=True)
		mc.connectAttr(lfEyeAimReverse+'.outputX',lfEyeAimBlendConstraint+'.'+lfEyeAimBlendAlias[0],f=True)
		mc.connectAttr(lfEyeJoint+'.aim',lfEyeAimCtrlShape[0]+'.v',f=True)
		
		# Parent Control
		mc.parent(lfEyeAimCtrlGrp,headAimCtrl)
		
		# Tweak ctrl position
		aimCtrlPos = mc.getAttr(lfEyeAimCtrlGrp+'.t')[0]
		mc.setAttr(lfEyeAimCtrlGrp+'.t',aimCtrlPos[0]*(1.0-headAimVec[0]),aimCtrlPos[1]*(1.0-headAimVec[1]),aimCtrlPos[2]*(1.0-headAimVec[2]))
	
	if rtEyeJoint:
		
		# Create Aim Joints
		rtEyeAimXform = mc.duplicate(rtEyeAimGrp,po=True,n=rtEyePrefix+'_aimFollow_jnt')[0]
		rtEyeFollowXform = mc.duplicate(rtEyeAimGrp,po=True,n=rtEyePrefix+'_headFollow_jnt')[0]
		
		# Create control
		rtEyeJointLen = glTools.utils.joint.length(rtEyeJoint)
		rtEyeAimCtrl = ctrlBuilder.create('eye',rtEyePrefix+'_aim_ctrl',scale=rtEyeJointLen*rtEyeCtrlScale)
		rtEyeAimCtrlShape = mc.listRelatives(rtEyeAimCtrl,s=True,pa=True)
		rtEyeAimCtrlGrp = glTools.utils.base.group(rtEyeAimCtrl,name=rtEyePrefix+'_aim_ctrlGrp')
		glTools.rig.utils.tagCtrl(rtEyeAimCtrl,'primary')
		
		# Position control
		pt = glTools.utils.base.getPosition(rtEyeJoint)
		vec = glTools.utils.transform.axisVector(rtEyeJoint,'x',normalize=True)
		mc.move(pt[0]+(vec[0]*headAimOffset),pt[1]+(vec[1]*headAimOffset),pt[2]+(vec[2]*headAimOffset),rtEyeAimCtrlGrp,ws=True,a=True)
		
		# Create Aim Constraint
		rtEyeAimConstraint = mc.aimConstraint(rtEyeAimCtrl,rtEyeAimXform,aim=eyeAimVec,u=eyeUpVec,wu=eyeWorldUpVec,wuo=rtEyeAimCtrl)[0]
		
		# Create Aim Blend Constraint
		rtEyeAimBlendConstraint = mc.orientConstraint([rtEyeFollowXform,rtEyeAimXform],rtEyeAimGrp)[0]
		rtEyeAimBlendAlias = mc.orientConstraint(rtEyeAimBlendConstraint,q=True,wal=True)
		
		# Connect Blend Aim Constraint
		mc.addAttr(rtEyeJoint,ln='aim',min=0.0,max=1.0,dv=0.0,k=True)
		rtEyeAimReverse = mc.createNode('reverse',n=rtEyePrefix+'_aimBlend_reverse')
		mc.connectAttr(rtEyeJoint+'.aim',rtEyeAimReverse+'.inputX',f=True)
		mc.connectAttr(rtEyeJoint+'.aim',rtEyeAimBlendConstraint+'.'+rtEyeAimBlendAlias[1],f=True)
		mc.connectAttr(rtEyeAimReverse+'.outputX',rtEyeAimBlendConstraint+'.'+rtEyeAimBlendAlias[0],f=True)
		mc.connectAttr(rtEyeJoint+'.aim',rtEyeAimCtrlShape[0]+'.v',f=True)
		
		# Parent Control
		mc.parent(rtEyeAimCtrlGrp,headAimCtrl)
		
		# Tweak ctrl position
		aimCtrlPos = mc.getAttr(rtEyeAimCtrlGrp+'.t')[0]
		mc.setAttr(rtEyeAimCtrlGrp+'.t',aimCtrlPos[0]*(1.0-headAimVec[0]),aimCtrlPos[1]*(1.0-headAimVec[1]),aimCtrlPos[2]*(1.0-headAimVec[2]))
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([0,0,0,0,0,0,2,2,2,1],objectList=[jawRotateCtrl])
	chStateUtil.setFlags([0,0,0,2,2,2,2,2,2,1],objectList=[jawTransCtrl])
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=[headJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[headJointGrp])
	if jawJoint:
		chStateUtil.setFlags([1,1,1,1,1,1,1,2,2,1],objectList=[jawJoint])
		chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[jawJointGrp])
		chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[jawRotateCtrlGrp,jawTransCtrlGrp])
		chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[jawIk,jawIkGrp])
	if lfEyeJoint:
		chStateUtil.setFlags([2,2,2,0,0,0,2,2,2,1],objectList=[lfEyeJoint])
		chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[lfEyeJointGrp])
	if rtEyeJoint:
		chStateUtil.setFlags([2,2,2,0,0,0,2,2,2,1],objectList=[rtEyeJoint])
		chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[rtEyeJointGrp])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[attachJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=[attachJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[module,ctrl_grp,rig_grp,skel_grp])
	
	# =================
	# - Return Result -
	# =================
	
	return [module,attachJoint]