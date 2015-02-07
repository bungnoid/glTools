import maya.cmds as mc

import glTools.utils.transformWire

def connectToSource(srcNS,dstNS,wireCrv,baseCrv='',addArmIk=False,connectFingers=False):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if srcNS: srcNS += ':'
	if dstNS: dstNS += ':'
	
	# Duplicate Wire to Generate Base
	if not baseCrv: baseCrv = mc.duplicate(wireCrv,n=wireCrv+'Base')[0]
	
	# ========================
	# - Target (IK) Locators -
	# ========================
	
	# Create Locators (Source)
	hip_src = mc.spaceLocator(n='hip_src')[0]
	lf_foot_src = mc.spaceLocator(n='lf_foot_src')[0]
	rt_foot_src = mc.spaceLocator(n='rt_foot_src')[0]
	lf_knee_src = mc.spaceLocator(n='lf_knee_src')[0]
	rt_knee_src = mc.spaceLocator(n='rt_knee_src')[0]
	if addArmIk:
		lf_hand_src = mc.spaceLocator(n='lf_hand_src')[0]
		rt_hand_src = mc.spaceLocator(n='rt_hand_src')[0]
		lf_elbow_src = mc.spaceLocator(n='lf_elbow_src')[0]
		rt_elbow_src = mc.spaceLocator(n='rt_elbow_src')[0]
	
	# Create Locators (Destination)
	hip_dst = mc.spaceLocator(n='hip_dst')[0]
	lf_foot_dst = mc.spaceLocator(n='lf_foot_dst')[0]
	rt_foot_dst = mc.spaceLocator(n='rt_foot_dst')[0]
	lf_knee_dst = mc.spaceLocator(n='lf_knee_dst')[0]
	rt_knee_dst = mc.spaceLocator(n='rt_knee_dst')[0]
	if addArmIk:
		lf_hand_dst = mc.spaceLocator(n='lf_hand_dst')[0]
		rt_hand_dst = mc.spaceLocator(n='rt_hand_dst')[0]
		lf_elbow_dst = mc.spaceLocator(n='lf_elbow_dst')[0]
		rt_elbow_dst = mc.spaceLocator(n='rt_elbow_dst')[0]
	
	# Position Locators (Source)
	mc.delete(mc.parentConstraint(srcNS+'Hips',hip_src))
	mc.delete(mc.parentConstraint(srcNS+'LeftFoot',lf_foot_src))
	mc.delete(mc.parentConstraint(srcNS+'RightFoot',rt_foot_src))
	mc.delete(mc.parentConstraint(srcNS+'LeftLeg',lf_knee_src))
	mc.delete(mc.parentConstraint(srcNS+'RightLeg',rt_knee_src))
	if addArmIk:
		mc.delete(mc.parentConstraint(srcNS+'LeftHand',lf_hand_src))
		mc.delete(mc.parentConstraint(srcNS+'RightHand',rt_hand_src))
		mc.delete(mc.parentConstraint(srcNS+'LeftForeArm',lf_elbow_src))
		mc.delete(mc.parentConstraint(srcNS+'RightForeArm',rt_elbow_src))
	
	# Position Locators (Destination)
	mc.delete(mc.parentConstraint(dstNS+'Hips',hip_dst))
	mc.delete(mc.parentConstraint(dstNS+'LeftFoot',lf_foot_dst))
	mc.delete(mc.parentConstraint(dstNS+'RightFoot',rt_foot_dst))
	mc.delete(mc.parentConstraint(dstNS+'LeftLeg',lf_knee_dst))
	mc.delete(mc.parentConstraint(dstNS+'RightLeg',rt_knee_dst))
	if addArmIk:
		mc.delete(mc.parentConstraint(dstNS+'LeftHand',lf_hand_dst))
		mc.delete(mc.parentConstraint(dstNS+'RightHand',rt_hand_dstc))
		mc.delete(mc.parentConstraint(dstNS+'LeftLeg',lf_elbow_dst))
		mc.delete(mc.parentConstraint(dstNS+'RightLeg',rt_elbow_dst))
	
	# Parent Locators (Source)
	mc.parent(hip_src,srcNS+'Hips')
	mc.parent(lf_foot_src,srcNS+'LeftFoot')
	mc.parent(rt_foot_src,srcNS+'RightFoot')
	mc.parent(lf_knee_src,srcNS+'LeftLeg')
	mc.parent(rt_knee_src,srcNS+'RightLeg')
	if addArmIk:
		mc.parent(lf_hand_loc,srcNS+'LeftHand')
		mc.parent(rt_hand_loc,srcNS+'RightHand')
		mc.parent(lf_elbow_loc,srcNS+'LeftForeArm')
		mc.parent(rt_elbow_loc,srcNS+'RightForeArm')
	
	# =====================
	# - Connect To Source -
	# =====================
	
	# Hip Constraint
	hip_con = mc.parentConstraint(hip_dst,dstNS+'Hips')[0]
	
	# -------------
	# - Legs (IK) -
	# -------------
	
	lf_leg_ik = mc.ikHandle(startJoint=dstNS+'LeftUpLeg',endEffector=dstNS+'LeftFoot',solver='ikRPsolver',n='lf_leg_ik')[0]
	rt_leg_ik = mc.ikHandle(startJoint=dstNS+'RightUpLeg',endEffector=dstNS+'RightFoot',solver='ikRPsolver',n='rt_leg_ik')[0]
	
	# Limit Roll Bones
	mc.transformLimits(dstNS+'LeftLegRoll',ry=(0,0),rz=(0,0),ery=(1,1),erz=(1,1))
	mc.transformLimits(dstNS+'RightLegRoll',ry=(0,0),rz=(0,0),ery=(1,1),erz=(1,1))
	mc.transformLimits(dstNS+'LeftUpLegRoll',ry=(0,0),rz=(0,0),ery=(1,1),erz=(1,1))
	mc.transformLimits(dstNS+'RightUpLegRoll',ry=(0,0),rz=(0,0),ery=(1,1),erz=(1,1))
	
	# Constrain IK
	lf_leg_ik_con = mc.parentConstraint(lf_foot_dst,lf_leg_ik)
	rt_leg_ik_con = mc.parentConstraint(rt_foot_dst,rt_leg_ik)
	lf_leg_pv_con = mc.poleVectorConstraint(lf_knee_dst,lf_leg_ik)
	rt_leg_pv_con = mc.poleVectorConstraint(rt_knee_dst,rt_leg_ik)
	
	# Constrain Foot
	lf_foot_con = mc.orientConstraint(lf_foot_dst,dstNS+'LeftFoot')
	rt_foot_con = mc.orientConstraint(rt_foot_dst,dstNS+'RightFoot')
	
	# -------------
	# - Arms (IK) -
	# -------------
	
	if addArmIk:
		
		lf_arm_ik = mc.ikHandle(startJoint=dstNS+'LeftArm',endEffector=dstNS+'LeftHand',solver='ikRPsolver',n='lf_arm_ik')[0]
		rt_arm_ik = mc.ikHandle(startJoint=dstNS+'RightArm',endEffector=dstNS+'RightHand',solver='ikRPsolver',n='rt_arm_ik')[0]
		
		# Limit Roll Bones
		mc.transformLimits(dstNS+'LeftArmRoll',ry=(0,0),rz=(0,0),ery=(1,1),erz=(1,1))
		mc.transformLimits(dstNS+'RightArmRoll',ry=(0,0),rz=(0,0),ery=(1,1),erz=(1,1))
		mc.transformLimits(dstNS+'LeftForeArmRoll',ry=(0,0),rz=(0,0),ery=(1,1),erz=(1,1))
		mc.transformLimits(dstNS+'RightForeArmRoll',ry=(0,0),rz=(0,0),ery=(1,1),erz=(1,1))
		
		# Constrain IK
		lf_arm_ik_con = mc.parentConstraint(lf_hand_dst,lf_arm_ik)
		rt_arm_ik_con = mc.parentConstraint(rt_hand_dst,rt_arm_ik)
		lf_arm_pv_con = mc.poleVectorConstraint(lf_elbow_dst,lf_leg_ik)
		rt_arm_pv_con = mc.poleVectorConstraint(rt_elbow_dst,rt_leg_ik)
		
		# Constrain Hand
		lf_hand_con = mc.orientConstraint(lf_hand_dst,dstNS+'LeftHand')
		rt_hand_con = mc.orientConstraint(rt_hand_dst,dstNS+'RightHand')
	
	# -----------------------
	# - Upper Body Rotation -
	# -----------------------
	
	body_jnts = [	'Spine',
					'Spine1',
					'Spine2',
					'LeftShoulder',
					'RightShoulder',
					'Neck',
					'Head'	]
	
	arm_jnts = [	'Arm',
					'ArmRoll',
					'ForeArm',
					'ForeArmRoll',
					'Hand'	]
	
	hand_jnts = [	'HandThumb1',
					'HandThumb2',
					'HandThumb3',
					'InHandIndex',
					'InHandMiddle',
					'InHandRing',
					'InHandPinky',
					'HandIndex1',
					'HandMiddle1',
					'HandRing1',
					'HandPinky1',
					'HandPinky2',
					'HandRing2',
					'HandMiddle2',
					'HandIndex2',
					'HandPinky3',
					'HandRing3',
					'HandMiddle3',
					'HandIndex3'	]
	
	foot_jnts = [	'ToeBase'	]
	
	# Connect Body
	for jnt in body_jnts:
		mc.connectAttr(srcNS+jnt+'.r',dstNS+jnt+'.r',f=True)
	
	# Connect Feet
	for side in ['Left','Right']:
		for jnt in foot_jnts:
			mc.connectAttr(srcNS+side+jnt+'.r',dstNS+side+jnt+'.r',f=True)
	
	# Connect Arms
	if not addArmIk:
		for side in ['Left','Right']:
			for jnt in arm_jnts:
				mc.connectAttr(srcNS+side+jnt+'.r',dstNS+side+jnt+'.r',f=True)
	
	# Connect Fingers
	if connectFingers:
		for side in ['Left','Right']:
			for jnt in hand_jnts:
				mc.connectAttr(srcNS+side+jnt+'.r',dstNS+side+jnt+'.r',f=True)
	
	# ========================
	# - Transform Wire Setup -
	# ========================
	
	# Hips
	glTools.utils.transformWire.create(	wireCrv = wireCrv,
										baseCrv = baseCrv,
										srcTransform = hip_src,
										dstTransform = hip_dst,
										mode='distance',
										aim=1.0,
										tilt=0.0,
										bank=0.0,
										connectPos=True,
										connectRot=True,
										orientList=[],
										prefix='')
	
	# Legs (lf_foot)
	glTools.utils.transformWire.create(	wireCrv = wireCrv,
										baseCrv = baseCrv,
										srcTransform = lf_foot_src,
										dstTransform = lf_foot_dst,
										mode='distance',
										aim=1.0,
										tilt=1.0,
										bank=0.0,
										connectPos=True,
										connectRot=True,
										orientList=[],
										prefix='')
	
	# Legs (rt_foot)
	glTools.utils.transformWire.create(	wireCrv = wireCrv,
										baseCrv = baseCrv,
										srcTransform = rt_foot_src,
										dstTransform = rt_foot_dst,
										mode='distance',
										aim=1.0,
										tilt=1.0,
										bank=0.0,
										connectPos=True,
										connectRot=True,
										orientList=[],
										prefix='')
	
	# Legs (lf_knee)
	glTools.utils.transformWire.create(	wireCrv = wireCrv,
										baseCrv = baseCrv,
										srcTransform = lf_knee_src,
										dstTransform = lf_knee_dst,
										mode='distance',
										aim=1.0,
										tilt=1.0,
										bank=.0,
										connectPos=True,
										connectRot=True,
										orientList=[],
										prefix='')
	
	# Legs (rt_knee)
	glTools.utils.transformWire.create(	wireCrv = wireCrv,
										baseCrv = baseCrv,
										srcTransform = rt_knee_src,
										dstTransform = rt_knee_dst,
										mode='distance',
										aim=1.0,
										tilt=1.0,
										bank=.0,
										connectPos=True,
										connectRot=True,
										orientList=[],
										prefix='')
	
	# Arms
	if addArmIk:
		
		# Arms (lf_hand)
		glTools.utils.transformWire.create(	wireCrv = wireCrv,
											baseCrv = baseCrv,
											srcTransform = lf_hand_src,
											dstTransform = lf_hand_dst,
											mode='distance',
											aim=1.0,
											tilt=0.0,
											bank=0.0,
											connectPos=True,
											connectRot=True,
											orientList=[],
											prefix='')
		
		# Arms (rt_hand)
		glTools.utils.transformWire.create(	wireCrv = wireCrv,
											baseCrv = baseCrv,
											srcTransform = rt_hand_src,
											dstTransform = rt_hand_dst,
											mode='distance',
											aim=1.0,
											tilt=0.0,
											bank=0.0,
											connectPos=True,
											connectRot=True,
											orientList=[],
											prefix='')
		
		# Arms (lf_elbow)
		glTools.utils.transformWire.create(	wireCrv = wireCrv,
											baseCrv = baseCrv,
											srcTransform = lf_elbow_src,
											dstTransform = lf_elbow_dst,
											mode='distance',
											aim=1.0,
											tilt=0.0,
											bank=0.0,
											connectPos=True,
											connectRot=True,
											orientList=[],
											prefix='')
		
		# Arms (rt_elbow)
		glTools.utils.transformWire.create(	wireCrv = wireCrv,
											baseCrv = baseCrv,
											srcTransform = rt_elbow_src,
											dstTransform = rt_elbow_dst,
											mode='distance',
											aim=1.0,
											tilt=0.0,
											bank=0.0,
											connectPos=True,
											connectRot=True,
											orientList=[],
											prefix='')
