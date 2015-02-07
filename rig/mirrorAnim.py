import maya.cmds as mc

import glTools.utils.namespace

def cutPasteKey(src,dst):
	'''
	'''
	keys = mc.cutKey(src)
	if keys: mc.pasteKey(dst)

def swapAnim(srcCtrl,dstCtrl):
	'''
	'''
	# Temp Key Node
	tmpCtrl = mc.duplicate(srcCtrl,po=True,n=srcCtrl+'TEMP')[0]
	
	# Swap Left <> Right
	cutPasteKey(srcCtrl,tmpCtrl)
	cutPasteKey(dstCtrl,srcCtrl)
	cutPasteKey(tmpCtrl,dstCtrl)
	
	# Delete Temp Node
	if mc.objExists(tmpCtrl):
		try: mc.delete(tmpCtrl)
		except: print('Error deleting temp control object "'+tmpCtrl+'"!')

def mirrorBipedAnim(rigNS):
	'''
	Mirror biped body animation
	@param rigNS: Rig namespace.
	@type rigNS: str
	'''
	# =============
	# - Check Rig -
	# =============
	
	if not mc.namespace(ex=rigNS):
		raise Exception('Rig namespace "'+rigNS+'" not found! Unable to mirror animation...')
	
	# ====================
	# - Get Rig Controls -
	# ====================
	
	# Body
	bodyA = rigNS+':cn_bodyA_jnt'
	bodyB = rigNS+':cn_bodyB_jnt'
	
	# Spine/Neck/Head
	spineA = rigNS+':cn_spineA_jnt'
	spineB = rigNS+':cn_spineB_jnt'
	spineC = rigNS+':cn_spineC_jnt'
	
	spineBase = rigNS+':cn_spine_base_ctrl'
	spineMid = rigNS+':cn_spine_mid_ctrl'
	spineTop = rigNS+':cn_spine_top_ctrl'
	
	neck = rigNS+':cn_neckA_jnt'
	head = rigNS+':cn_headA_jnt'
	
	# Arms
	clav = rigNS+':SIDE_clavicleA_jnt'
	armFkA = rigNS+':SIDE_arm_fkA_jnt'
	armFkB = rigNS+':SIDE_arm_fkB_jnt'
	armIk = rigNS+':SIDE_arm_ik_ctrl'
	armPv = rigNS+':SIDE_arm_pv_ctrl'
	hand = rigNS+':SIDE_handA_jnt'
	
	# Fingers
	fingerList = [	'thumbA','thumbB','thumbC',
					'indexA','indexB','indexC','indexD',
					'middleA','middleB','middleC','middleD',
					'ringA','ringB','ringC','ringD',
					'pinkyA','pinkyB','pinkyC','pinkyD'	]
	fingers = [rigNS+':SIDE_'+finger+'_jnt' for finger in fingerList]
	
	# Legs
	legFkA = rigNS+':SIDE_leg_fkA_jnt'
	legFkB = rigNS+':SIDE_leg_fkB_jnt'
	legIk = rigNS+':SIDE_leg_ik_ctrl'
	legPv = rigNS+':SIDE_leg_pv_ctrl'
	
	# Feet
	footIk = rigNS+':SIDE_foot_ik_ctrl'
	toeIk = rigNS+':SIDE_foot_toe_ctrl'
	footFkA = rigNS+':foot_fkA_jnt'
	footFkB = rigNS+':foot_fkB_jnt'
	
	# ====================
	# - Mirror Animation -
	# ====================
	
	# Body
	for ctrl in [bodyA,bodyB]:
		if mc.objExists(ctrl):
			mc.scaleKey(ctrl,at=['tx','ry','rz'],valueScale=-1.0,valuePivot=0.0)
	
	# Spine/Neck/Head
	for ctrl in [spineA,spineB,spineC,spineBase,spineMid,spineTop,neck,head]:
		if mc.objExists(ctrl):
			mc.scaleKey(ctrl,at=['tz','rx','ry'],valueScale=-1.0,valuePivot=0.0)
	
	# Arms - FK (Clavicle,Arm,Hand)
	for ctrl in [clav,armFkA,armFkB,hand]:
		
		# Get Left/Right Nodes
		lfCtrl = ctrl.replace('SIDE','lf')
		rtCtrl = ctrl.replace('SIDE','rt')
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			
			# Swap Left <> Right
			swapAnim(lfCtrl,rtCtrl)
			
			# Scale Keys
			mc.scaleKey(lfCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
	
	# Arms - IK
	for ctrl in [armIk,armPv]:
		
		# Get Left/Right Nodes
		lfCtrl = ctrl.replace('SIDE','lf')
		rtCtrl = ctrl.replace('SIDE','rt')
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			
			# Swap Left <> Right
			swapAnim(lfCtrl,rtCtrl)
			
			# Scale Keys
			mc.scaleKey(lfCtrl,at=['tx','ry','rz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tx','ry','rz'],valueScale=-1.0,valuePivot=0.0)
	
	# Fingers
	for ctrl in fingers:
		
		# Get Left/Right Nodes
		lfCtrl = ctrl.replace('SIDE','lf')
		rtCtrl = ctrl.replace('SIDE','rt')
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			
			# Swap Left <> Right
			swapAnim(lfCtrl,rtCtrl)
			
			# Scale Keys
			mc.scaleKey(lfCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
			
	# Legs - FK
	for ctrl in [legFkA,legFkB,footFkA,footFkB]:
		
		# Get Left/Right Nodes
		lfCtrl = ctrl.replace('SIDE','lf')
		rtCtrl = ctrl.replace('SIDE','rt')
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			
			# Swap Left <> Right
			swapAnim(lfCtrl,rtCtrl)
			
			# Scale Keys
			mc.scaleKey(lfCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
	
	# Legs - IK
	for ctrl in [legIk,legPv]:
		
		# Get Left/Right Nodes
		lfCtrl = ctrl.replace('SIDE','lf')
		rtCtrl = ctrl.replace('SIDE','rt')
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			
			# Swap Left <> Right
			swapAnim(lfCtrl,rtCtrl)
			
			# Scale Keys
			mc.scaleKey(lfCtrl,at=['tx','ry','rz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tx','ry','rz'],valueScale=-1.0,valuePivot=0.0)		
	
	# Feet - IK
	for ctrl in [footIk,toeIk]:
		
		# Get Left/Right Nodes
		lfCtrl = ctrl.replace('SIDE','lf')
		rtCtrl = ctrl.replace('SIDE','rt')
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			
			# Swap Left <> Right
			swapAnim(lfCtrl,rtCtrl)
			
			# Scale Keys
			mc.scaleKey(lfCtrl,at=['tx','ry','rz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tx','ry','rz'],valueScale=-1.0,valuePivot=0.0)

def mirrorBipedAnimFromSel():
	'''
	'''
	# Get Current Selection
	sel = mc.ls(sl=True,transforms=True)
	NSlist = glTools.utils.namespace.getNSList(sel,topOnly=True)
	
	# Mirror Animation
	for rigNS in NSlist:
		try: mirrorBipedAnim(rigNS)
		except Exception, e: print('Error mirroring animation for "'+rigNS+'"! Skipping...')

def mirrorBipedMocap(rigNS):
	'''
	Mirror biped body mocap animation
	@param rigNS: Rig namespace.
	@type rigNS: str
	'''
	# =============
	# - Check Rig -
	# =============
	
	if not mc.namespace(ex=rigNS):
		raise Exception('Rig namespace "'+rigNS+'" not found! Unable to mirror animation...')
	
	# ====================
	# - Get Rig Controls -
	# ====================
	
	# Body
	body = rigNS+':Hips'
	
	# Spine/Neck/Head
	spine = rigNS+':Spine'
	neck = rigNS+':Neck'
	head = rigNS+':Head'
	
	# Arms
	clav = rigNS+':SIDEShoulder'
	arm = rigNS+':SIDEArm'
	foreArm = rigNS+':SIDEForeArm'
	
	# Hand
	hand = rigNS+':SIDEHand'
	thumb = rigNS+':SIDEHandThumb'
	index = rigNS+':SIDEHandIndex'
	middle = rigNS+':SIDEHandMiddle'
	ring = rigNS+':SIDEHandRing'
	pinky = rigNS+':SIDEHandPinky'
	finger = [thumb,index,middle,ring,pinky]
	
	# Legs
	upLeg = rigNS+':SIDEUpLeg'
	leg = rigNS+':SIDELeg'
	
	# Foot
	foot = rigNS+':SIDEFoot'
	toe = rigNS+':SIDEToeBase'
	
	# Roll
	roll = 'Roll'
	
	# Side
	left = 'Left'
	right = 'Right'
	
	# ====================
	# - Mirror Animation -
	# ====================
	
	# Body
	for ctrl in [body]:
		if mc.objExists(ctrl):
			mc.scaleKey(ctrl,at=['tx','ry','rz'],valueScale=-1.0,valuePivot=0.0)
	
	# Spine/Neck/Head
	for item in [spine,neck,head]:
		ind = ''
		while mc.objExists(item+str(ind)):
			ctrl = item+str(ind)
			mc.scaleKey(ctrl,at=['rx','ry'],valueScale=-1.0,valuePivot=0.0)
			if not ind: ind = 0
			ind += 1
	
	# Shoulder
	for ctrl in [clav]:
		# Get Left/Right Nodes
		lfCtrl = ctrl.replace('SIDE',left)
		rtCtrl = ctrl.replace('SIDE',right)
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			swapAnim(lfCtrl,rtCtrl)
			mc.scaleKey(lfCtrl,at=['tz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tz'],valueScale=-1.0,valuePivot=0.0)
	
	# Arms
	for ctrl in [arm,foreArm,hand]:
		
		# Get Left/Right Nodes
		lfCtrl = ctrl.replace('SIDE',left)
		rtCtrl = ctrl.replace('SIDE',right)
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			swapAnim(lfCtrl,rtCtrl)
			mc.scaleKey(lfCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
		
		# Get Roll Nodes
		lfCtrl = lfCtrl+roll
		rtCtrl = rtCtrl+roll
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			swapAnim(lfCtrl,rtCtrl)
			mc.scaleKey(lfCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
		
	# Fingers
	for ctrl in finger:
		
		# Get Left/Right Nodes
		lfCtrl = ctrl.replace('SIDE',left)
		rtCtrl = ctrl.replace('SIDE',right)
		
		ind = 1
		while mc.objExists(lfCtrl+str(ind)) and mc.objExists(rtCtrl+str(ind)):
			lfCtrlInd = lfCtrl+str(ind)
			rtCtrlInd = rtCtrl+str(ind)
			swapAnim(lfCtrlInd,rtCtrlInd)
			mc.scaleKey(lfCtrlInd,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrlInd,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
			if not ind: ind = 0
			ind += 1
	
	# Legs
	for ctrl in [upLeg,leg,foot,toe]:
		
		# Get Left/Right Nodes
		lfCtrl = ctrl.replace('SIDE',left)
		rtCtrl = ctrl.replace('SIDE',right)
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			swapAnim(lfCtrl,rtCtrl)
			mc.scaleKey(lfCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
		
		# Get Roll Nodes
		lfCtrl = lfCtrl+roll
		rtCtrl = rtCtrl+roll
		if mc.objExists(lfCtrl) and mc.objExists(rtCtrl):
			swapAnim(lfCtrl,rtCtrl)
			mc.scaleKey(lfCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)
			mc.scaleKey(rtCtrl,at=['tx','ty','tz'],valueScale=-1.0,valuePivot=0.0)

def mirrorBipedMocaFromSel():
	'''
	'''
	# Get Current Selection
	sel = mc.ls(sl=True,transforms=True)
	NSlist = glTools.utils.namespace.getNSList(sel,topOnly=True)
	
	# Mirror Animation
	for rigNS in NSlist:
		try: mirrorBipedMocap(rigNS)
		except Exception, e: print('Error mirroring mocap animation for "'+rigNS+'"! Skipping...')

