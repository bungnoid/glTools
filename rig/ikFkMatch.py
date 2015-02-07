import maya.cmds as mc

from glTools.nrig.module import module

import glTools.anim.utils

import glTools.rig.utils

import glTools.utils.base
import glTools.utils.lib
import glTools.utils.matrix
import glTools.utils.namespace

def match(ctrl):
	'''
	Perform IK/FK control match
	@param ctrl: IK/FK toggle attribute
	@type ctrl: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Namespace
	ns = glTools.utils.namespace.getNS(ctrl)
	ctrl = glTools.utils.namespace.stripNS(ctrl)
	if ns: ns += ':'
	NSctrl = ns+ctrl
	
	# Check Module
	if not mc.objExists(NSctrl+'.ctrlModule'):
		print('Unable to determine module from control "'+NSctrl+'"!')
		return
	
	# Get Module
	limbModule = mc.getAttr(NSctrl+'.ctrlModule')
	limbModuleGrp = ns+limbModule+'_module'
	if not mc.objExists(limbModuleGrp):
		raise Exception('Limb module "'+limbModuleGrp+'" does not exist!')
	
	# Rebuild Limb Module
	limb = module.Module()
	limb.rebuildFromData(limbModuleGrp)
	limbType = limb.moduleData['moduleType']
	
	# !!! This step is to strip the unneccessary namespace from the limb type string
	# !!! Once the rig module data is split to data/nodes/attrs...this can be removed! 
	limbType = glTools.utils.namespace.stripNS(limbType)
	
	if limbType != 'LimbModule':
		raise Exception('Unsupported IK/FK match module type "'+limbType+'"!')
	
	# Get Limb End Module
	endModule = {'lf_arm':'lf_hand','rt_arm':'rt_hand','lf_leg':'lf_foot','rt_leg':'rt_foot'}[limbModule]
	endModuleGrp = ns+endModule+'_module'
	if not mc.objExists(endModuleGrp):
		raise Exception('Limb end module "'+endModuleGrp+'" does not exist!')
	
	# Rebuild Limb End Module
	limbEnd = module.Module()
	limbEnd.rebuildFromData(endModuleGrp)
	limbEndType = limbEnd.moduleData['moduleType']
	
	# !!! This step is to strip the unneccessary namespace from the limb type string
	# !!! Once the rig module data is split to data/nodes/attrs...this can be removed! 
	limbEndType = glTools.utils.namespace.stripNS(limbEndType)
	
	# FK Joints
	fkJnts = [jnt for jnt in limb.moduleNode['fkJointList']]
	for jnt in fkJnts:
		if not mc.objExists(jnt):
			raise Exception('FK joint "'+jnt+'" does not exist!')
	# IK Joints
	ikJnts = [jnt for jnt in limb.moduleNode['ikJointList']]
	for jnt in ikJnts:
		if not mc.objExists(jnt):
			raise Exception('IK joint "'+jnt+'" does not exist!')
	
	# Rotate Order
	rotateOrder_list = glTools.utils.lib.rotateOrder_list()
	
	# ====================
	# - Get Limb Details -
	# ====================
	
	ikCtrl = limb.moduleNode['ikCtrl']
	if not mc.objExists(ikCtrl): raise Exception('IK control "'+ikCtrl+'" does not exist!')
	pvCtrl = limb.moduleNode['pvCtrl']
	if not mc.objExists(pvCtrl): raise Exception('IK pole vector control "'+pvCtrl+'" does not exist!')
	fkEnd = limb.moduleNode['fkEndJoint']
	if not mc.objExists(fkEnd): raise Exception('FK end joint "'+fkEnd+'" does not exist!')
	ikEnd = limb.moduleNode['ikEndJoint']
	if not mc.objExists(ikEnd): raise Exception('IK end joint "'+ikEnd+'" does not exist!')
	ikCtrlGrp = mc.listRelatives(ikCtrl,p=True,pa=True)[0]
	
	# IK Offset Ctrl
	ikOffset = ''
	if limb.moduleNode.has_key('ikOffset'):
		ikOffset = limb.moduleNode['ikOffset']
		if not mc.objExists(ikOffset): raise Exception('IK offset control "'+ikOffset+'" does not exist!')
	
	# Get IK Blend Attribute
	ikBlendAttr = limb.moduleAttr['ikBlendAttr']
	if not mc.objExists(ikBlendAttr):
		raise Exception('Ik Blend attribute "'+ikBlendAttr+'" does not exist!')
	ikBlendState = mc.getAttr(ikBlendAttr)
	
	# Limb End Details
	limbEndIk = ''
	limbEndFk = ''
	limbEndIkParent = ''
	limbEndFkParent = ''
	if limbEndType == 'HandModule':
		limbEndIk = limbEnd.moduleNode['ctrlList'][0]
		limbEndFk = limbEnd.moduleNode['ctrlList'][0]
	elif limbEndType == 'FootModule':
		limbEndIk = '' # limbEnd.moduleNode['ikCtrlList'][0]
		limbEndFk = limbEnd.moduleNode['fkCtrlList'][0]
	else:
		raise Exception('Unsupported limbEnd module type "'+limbEndType+'"!')
	if limbEndIk and not mc.objExists(limbEndIk): raise Exception('Limb end IK control "'+limbEndIk+'" does not exist!')
	if limbEndFk and not mc.objExists(limbEndFk): raise Exception('Limb end FK control "'+limbEndFk+'" does not exist!')
	if limbEndIk: limbEndIkParent = mc.listRelatives(limbEndIk,p=True,pa=True)[0]
	if limbEndFk: limbEndFkParent = mc.listRelatives(limbEndFk,p=True,pa=True)[0]
	
	# =========
	# - Match -
	# =========
	
	if ikBlendState:
		
		# ==================
		# - Match IK to FK -
		# ==================
		
		if limbEndFk:
			fkEndMatrix = glTools.utils.matrix.getMatrix(limbEndFk,local=False)
		
		# Switch limb to FK
		if mc.getAttr(ikBlendAttr,se=True):
			mc.setAttr(ikBlendAttr,0)
		else:
			ikBlendConn = mc.listConnections(ikBlendAttr,s=True,p=True)
			if ikBlendConn:
				if mc.getAttr(ikBlendConn[0],se=True):
					mc.setAttr(ikBlendConn[0],0)
				else:
					raise Exception('The attribute "'+ikBlendAttr+'" is locked or connected and cannot be modified!')
		
		# Calculate IK control positions
		wristPt = glTools.utils.base.getPosition(fkEnd)
		poleVec = glTools.rig.utils.poleVectorPosition(fkJnts[0],fkJnts[1],fkJnts[-1],distance=1.5)
		
		# Set IK control positions
		mc.move(wristPt[0],wristPt[1],wristPt[2],ikCtrl,ws=True,a=True)
		mc.move(poleVec[0],poleVec[1],poleVec[2],pvCtrl,ws=True,a=True)
		
		# Calculate IK control orientation
		ikMatrix = glTools.utils.matrix.getMatrix(ikEnd,local=False)
		fkMatrix = glTools.utils.matrix.getMatrix(fkEnd,local=False)
		ctrlMatrix = glTools.utils.matrix.getMatrix(ikCtrl,local=False)
		ctrlGrpMatrix = glTools.utils.matrix.getMatrix(ikCtrlGrp,local=False)
		# Matrix Manipulation
		ikfkOffsetMatrix = fkMatrix * ikMatrix.inverse()
		ctrlOffsetMatrix = ctrlMatrix * ikMatrix.inverse()
		offsetMatrix = ctrlOffsetMatrix * ikfkOffsetMatrix * ikMatrix
		localMatrix = offsetMatrix * ctrlGrpMatrix.inverse()
		
		# Set IK control orientation
		offset = glTools.utils.matrix.getRotation(localMatrix,mc.getAttr(ikCtrl+'.ro'))
		mc.rotate(offset[0],offset[1],offset[2],ikCtrl)
		
		# ============
		# - Limb End -
		# ============
		
		if limbEndFk and limbEndIk:
			ikEndPMatrix = glTools.utils.matrix.getMatrix(limbEndIkParent,local=False)
			localMatrix = fkEndMatrix * ikEndPMatrix.inverse()
			offset = glTools.utils.matrix.getRotation(localMatrix,mc.getAttr(limbEndIk+'.ro'))
			mc.rotate(offset[0],offset[1],offset[2],limbEndIk)
		
		# =============
		# - IK Offset -
		# =============
		
		if ikOffset: glTools.rig.utils.setToDefault(ikOffset)
		
	else:
		
		# ==================
		# - Match FK to IK -
		# ==================
		
		if limbEndIk:
			ikEndMatrix = glTools.utils.matrix.getMatrix(limbEndIk,local=False)
		
		# Switch limb to FK
		if mc.getAttr(ikBlendAttr,se=True):
			mc.setAttr(ikBlendAttr,1)
		else:
			ikBlendConn = mc.listConnections(ikBlendAttr,s=True,p=True)
			if ikBlendConn:
				if mc.getAttr(ikBlendConn[0],se=True):
					mc.setAttr(ikBlendConn[0],1)
				else:
					raise Exception('The attribute "'+ikBlendAttr+'" is locked or connected and cannot be modified!')
		
		# For each FK joint
		for i in range(len(fkJnts)-1):
			
			# Reset Translation
			mc.setAttr(fkJnts[i]+'.t',0,0,0)
			
			# Set FK Chain Rotation
			rotateValue = mc.getAttr(ikJnts[i]+'.r')[0]
			mc.setAttr(fkJnts[i]+'.r',rotateValue[0],rotateValue[1],rotateValue[2])
			
			# Set FK Chain Scale
			scaleValue = mc.getAttr(ikJnts[i]+'.s')[0]
			mc.setAttr(fkJnts[i]+'.s',scaleValue[0],scaleValue[1],scaleValue[2])
		
		# Get IK Wrist Matrix
		ikMatrix = glTools.utils.matrix.getMatrix(ikCtrl,local=False)
		
		# ============
		# - Limb End -
		# ============
		
		if limbEndFk and limbEndIk:
			fkEndPMatrix = glTools.utils.matrix.getMatrix(limbEndFkParent,local=False)
			localMatrix = ikEndMatrix * fkEndPMatrix.inverse()
			offset = glTools.utils.matrix.getRotation(localMatrix,mc.getAttr(limbEndFk+'.ro'))
			mc.rotate(offset[0],offset[1],offset[2],limbEndFk)

def matchAnim(ctrl,start=None,end=None):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Namespace
	ns = glTools.utils.namespace.getNS(ctrl)
	ctrl = glTools.utils.namespace.stripNS(ctrl)
	if ns: ns += ':'
	NSctrl = ns+ctrl
	
	# Check Module
	if not mc.objExists(NSctrl+'.ctrlModule'):
		print('Unable to determine module from control "'+NSctrl+'"!')
		return
	
	# ===================
	# - Get Ctrl Module -
	# ===================
	
	limbModule = mc.getAttr(NSctrl+'.ctrlModule')
	limbModuleGrp = ns+limbModule+'_module'
	if not mc.objExists(limbModuleGrp):
		raise Exception('Limb module "'+limbModuleGrp+'" does not exist!')
	
	# Rebuild Limb Module
	limb = module.Module()
	limb.rebuildFromData(limbModuleGrp)
	limbType = limb.moduleData['moduleType']
	
	# !!! This step is to strip the unneccessary namespace from the limb type string
	# !!! Once the rig module data is split to data/nodes/attrs...this can be removed!
	limbType = glTools.utils.namespace.stripNS(limbType)
	
	if limbType != 'LimbModule':
		raise Exception('Unsupported IK/FK match module type "'+limbType+'"!')
	
	# Get Limb End Module
	endModule = {'lf_arm':'lf_hand','rt_arm':'rt_hand','lf_leg':'lf_foot','rt_leg':'rt_foot'}[limbModule]
	endModuleGrp = ns+endModule+'_module'
	if not mc.objExists(endModuleGrp):
		raise Exception('Limb end module "'+endModuleGrp+'" does not exist!')
	
	# Rebuild Limb End Module
	limbEnd = module.Module()
	limbEnd.rebuildFromData(endModuleGrp)
	limbEndType = limbEnd.moduleData['moduleType']
	
	# !!! This step is to strip the unneccessary namespace from the limb type string
	# !!! Once the rig module data is split to data/nodes/attrs...this can be removed! 
	limbEndType = glTools.utils.namespace.stripNS(limbEndType)
	
	# FK Joints
	fkJnts = [jnt for jnt in limb.moduleNode['fkJointList']]
	for jnt in fkJnts:
		if not mc.objExists(jnt):
			raise Exception('FK joint "'+jnt+'" does not exist!')
	# IK Joints
	ikJnts = [jnt for jnt in limb.moduleNode['ikJointList']]
	for jnt in ikJnts:
		if not mc.objExists(jnt):
			raise Exception('IK joint "'+jnt+'" does not exist!')
	
	# Rotate Order
	rotateOrder_list = glTools.utils.lib.rotateOrder_list()
	
	# ====================
	# - Get Limb Details -
	# ====================
	
	ikCtrl = limb.moduleNode['ikCtrl']
	if not mc.objExists(ikCtrl): raise Exception('IK control "'+ikCtrl+'" does not exist!')
	pvCtrl = limb.moduleNode['pvCtrl']
	if not mc.objExists(pvCtrl): raise Exception('IK pole vector control "'+pvCtrl+'" does not exist!')
	fkEnd = limb.moduleNode['fkEndJoint']
	if not mc.objExists(fkEnd): raise Exception('FK end joint "'+fkEnd+'" does not exist!')
	ikEnd = limb.moduleNode['ikEndJoint']
	if not mc.objExists(ikEnd): raise Exception('IK end joint "'+ikEnd+'" does not exist!')
	ikCtrlGrp = mc.listRelatives(ikCtrl,p=True,pa=True)[0]
	
	# IK Offset Ctrl
	ikOffset = ''
	if limb.moduleNode.has_key('ikOffset'):
		ikOffset = limb.moduleNode['ikOffset']
		if not mc.objExists(ikOffset): raise Exception('IK offset control "'+ikOffset+'" does not exist!')
	
	# Get IK Blend Attribute
	ikBlendAttr = limb.moduleAttr['ikBlendAttr']
	if not mc.objExists(ikBlendAttr):
		raise Exception('Ik Blend attribute "'+ikBlendAttr+'" does not exist!')
	ikBlendState = mc.getAttr(ikBlendAttr)
	
	# Limb End Details
	limbEndIk = ''
	limbEndFk = ''
	limbEndIkParent = ''
	limbEndFkParent = ''
	if limbEndType == 'HandModule':
		limbEndIk = limbEnd.moduleNode['ctrlList'][0]
		limbEndFk = limbEnd.moduleNode['ctrlList'][0]
	elif limbEndType == 'FootModule':
		limbEndIk = '' # limbEnd.moduleNode['ikCtrlList'][0]
		limbEndFk = limbEnd.moduleNode['fkCtrlList'][0]
	else:
		raise Exception('Unsupported limbEnd module type "'+limbEndType+'"!')
	if limbEndIk and not mc.objExists(limbEndIk): raise Exception('Limb end IK control "'+limbEndIk+'" does not exist!')
	if limbEndFk and not mc.objExists(limbEndFk): raise Exception('Limb end FK control "'+limbEndFk+'" does not exist!')
	if limbEndIk: limbEndIkParent = mc.listRelatives(limbEndIk,p=True,pa=True)[0]
	if limbEndFk: limbEndFkParent = mc.listRelatives(limbEndFk,p=True,pa=True)[0]
	
	# =========
	# - Match -
	# =========
	
	if ikBlendState:
		
		# ==================
		# - Match IK to FK -
		# ==================
		
		if limbEndFk:
			fkEndMatrix = glTools.utils.matrix.getMatrix(limbEndFk,local=False)
		
		# Switch limb to FK
		if mc.getAttr(ikBlendAttr,se=True):
			mc.setAttr(ikBlendAttr,0)
		else:
			ikBlendConn = mc.listConnections(ikBlendAttr,s=True,p=True)
			if ikBlendConn:
				if mc.getAttr(ikBlendConn[0],se=True):
					mc.setAttr(ikBlendConn[0],0)
				else:
					raise Exception('The attribute "'+ikBlendAttr+'" is locked or connected and cannot be modified!')
		
		# Calculate IK control positions
		wristPt = glTools.utils.base.getPosition(fkEnd)
		poleVec = glTools.rig.utils.poleVectorPosition(fkJnts[0],fkJnts[1],fkJnts[-1],distance=1.5)
		
		# Set IK control positions
		mc.move(wristPt[0],wristPt[1],wristPt[2],ikCtrl,ws=True,a=True)
		mc.move(poleVec[0],poleVec[1],poleVec[2],pvCtrl,ws=True,a=True)
		
		# Calculate IK control orientation
		ikMatrix = glTools.utils.matrix.getMatrix(ikEnd,local=False)
		fkMatrix = glTools.utils.matrix.getMatrix(fkEnd,local=False)
		ctrlMatrix = glTools.utils.matrix.getMatrix(ikCtrl,local=False)
		ctrlGrpMatrix = glTools.utils.matrix.getMatrix(ikCtrlGrp,local=False)
		# Matrix Manipulation
		ikfkOffsetMatrix = fkMatrix * ikMatrix.inverse()
		ctrlOffsetMatrix = ctrlMatrix * ikMatrix.inverse()
		offsetMatrix = ctrlOffsetMatrix * ikfkOffsetMatrix * ikMatrix
		localMatrix = offsetMatrix * ctrlGrpMatrix.inverse()
		
		# Set IK control orientation
		offset = glTools.utils.matrix.getRotation(localMatrix,mc.getAttr(ikCtrl+'.ro'))
		mc.rotate(offset[0],offset[1],offset[2],ikCtrl)
		
		# ============
		# - Limb End -
		# ============
		
		if limbEndFk and limbEndIk:
			ikEndPMatrix = glTools.utils.matrix.getMatrix(limbEndIkParent,local=False)
			localMatrix = fkEndMatrix * ikEndPMatrix.inverse()
			offset = glTools.utils.matrix.getRotation(localMatrix,mc.getAttr(limbEndIk+'.ro'))
			mc.rotate(offset[0],offset[1],offset[2],limbEndIk)
		
		# =============
		# - IK Offset -
		# =============
		
		if ikOffset: glTools.rig.utils.setToDefault(ikOffset)
		
	else:
		
		# ==================
		# - Match FK to IK -
		# ==================
		
		if limbEndIk:
			ikEndMatrix = glTools.utils.matrix.getMatrix(limbEndIk,local=False)
		
		# Switch limb to FK
		if mc.getAttr(ikBlendAttr,se=True):
			mc.setAttr(ikBlendAttr,1)
		else:
			ikBlendConn = mc.listConnections(ikBlendAttr,s=True,p=True)
			if ikBlendConn:
				if mc.getAttr(ikBlendConn[0],se=True):
					mc.setAttr(ikBlendConn[0],1)
				else:
					raise Exception('The attribute "'+ikBlendAttr+'" is locked or connected and cannot be modified!')
		
		# For each FK joint
		for i in range(len(fkJnts)-1):
			# Reset Translation
			mc.setAttr(fkJnts[i]+'.t',0,0,0)
			# Set FK chain rotations
			rotateValue = mc.getAttr(ikJnts[i]+'.r')[0]
			mc.setAttr(fkJnts[i]+'.r',rotateValue[0],rotateValue[1],rotateValue[2])
			# Set FK chain scale
			scaleValue = mc.getAttr(ikJnts[i]+'.s')[0]
			mc.setAttr(fkJnts[i]+'.s',scaleValue[0],scaleValue[1],scaleValue[2])
		
		# Get IK Wrist Matrix
		ikMatrix = glTools.utils.matrix.getMatrix(ikCtrl,local=False)
		
		# ============
		# - Limb End -
		# ============
		
		if limbEndFk and limbEndIk:
			fkEndPMatrix = glTools.utils.matrix.getMatrix(limbEndFkParent,local=False)
			localMatrix = ikEndMatrix * fkEndPMatrix.inverse()
			offset = glTools.utils.matrix.getRotation(localMatrix,mc.getAttr(limbEndFk+'.ro'))
			mc.rotate(offset[0],offset[1],offset[2],limbEndFk)

def armIkToFk(rigNS,side,bakeWrist=True,start=None,end=None,sampleBy=1):
	'''
	Bake IK arm animation to FK controls
	@param rigNS: IK/FK toggle attribute
	@type rigNS: str
	@param side: Arm side ("lf" or "rt")
	@type side: str
	@param bakeWrist: Bake wrist animation
	@type bakeWrist: bool
	@param start: Transfer animation start frame
	@type start: int or None
	@param end: Transfer animation end frame
	@type end: int or None
	@param sampleBy: Bake animation by N frames
	@type sampleBy: int
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Get Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	# Get IK/FK Joints
	ikJntList = [rigNS+':'+side+'_arm_ik'+i+'_jnt' for i in ['A','B']]
	fkJntList = [rigNS+':'+side+'_arm_fk'+i+'_jnt' for i in ['A','B']]
	
	# =====================
	# - Bake IK Limb Anim -
	# =====================
	
	# Set Arm to IK mode
	mc.setAttr(rigNS+':config.'+side+'ArmIkFkBlend',0) # IK
	
	# Bake Wrist to Locator
	wristLoc = None
	wristJnt = rigNS+':'+side+'_handA_jnt'
	if bakeWrist:
		wristLoc = glTools.anim.utils.bakeAnimToLocator(	obj = wristJnt,
														start = start,
														end = end,
														sampleBy = sampleBy,
														simulation=True,
														attrList = ['rx','ry','rz']	)
	
	
	# Duplicate FK Joints and Constrain to IK
	fkDupList = []
	fkOriList = []
	for i in range(2):
		fkDupList.append(mc.duplicate(fkJntList[i],po=True)[0])
		fkOriList.append(mc.orientConstraint(ikJntList[i],fkDupList[-1])[0])
	
	# =============================
	# - Transfer Baked Anim to FK -
	# =============================
	
	mc.refresh(suspend=True)
	for i in range(2):
		mc.bakeResults(	fkDupList[i],
						t=(start,end),
						at=['rx','ry','rz'],
						simulation=True,
						preserveOutsideKeys=True,
						sampleBy=sampleBy	)
		mc.cutKey(fkDupList[i],at=['rx','ry','rz'],t=(start,end))
		mc.pasteKey(fkJntList[i],at=['rx','ry','rz'],t=(start,end),option='replace')
	mc.refresh(suspend=False)
	
	# Delete Duplicate Joints and Constraints
	if fkOriList:
		try: mc.delete(fkOriList)
		except Exception, e: print('Error deleting nodes '+str(fkOriList)+'! Exception Msg: '+str(e))
	if fkDupList:
		try: mc.delete(fkDupList)
		except Exception, e: print('Error deleting nodes '+str(fkDupList)+'! Exception Msg: '+str(e))
	
	# Set to FK mode
	mc.setAttr(rigNS+':config.'+side+'ArmIkFkBlend',1) # FK
	
	# Bake Wrist from Locator
	if bakeWrist:
		glTools.anim.utils.bakeAnimFromLocator(	loc=wristLoc,
												obj=wristJnt,
												start=start,
												end=end,
												sampleBy=sampleBy,
												simulation=False,
												attrList=['rx','ry','rz']	)
	
	# Cleanup
	if mc.objExists(wristLoc):
		try: mc.delete(wristLoc)
		except: pass
	
	# =================
	# - Return Result -
	# =================
	
	return fkJntList

def armFkToIk(rigNS,side,bakeWrist=True,start=None,end=None,sampleBy=1):
	'''
	Bake FK arm animation to IK controls
	@param rigNS: IK/FK toggle attribute
	@type rigNS: str
	@param side: Arm side ("lf" or "rt")
	@type side: str
	@param bakeWrist: Bake wrist animation
	@type bakeWrist: bool
	@param start: Transfer animation start frame
	@type start: int or None
	@param end: Transfer animation end frame
	@type end: int or None
	@param sampleBy: Bake animation by N frames
	@type sampleBy: int
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Get Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	# Get FK Joints
	fkShoulder = rigNS+':'+side+'_arm_fkA_jnt'
	fkElbow = rigNS+':'+side+'_arm_fkB_jnt'
	fkWrist = rigNS+':'+side+'_handA_jnt'
	
	# Get IK Controls
	ikWrist = rigNS+':'+side+'_arm_ik_ctrl'
	ikElbow = rigNS+':'+side+'_arm_pv_ctrl'
	
	# =====================
	# - Transfer FK to IK -
	# =====================
	
	# Set Arm to FK mode
	mc.setAttr(rigNS+':config.'+side+'ArmIkFkBlend',1) # FK
	
	# Bake Wrist to Locator
	wristLoc = None
	if bakeWrist:
		wristLoc = glTools.anim.utils.bakeAnimToLocator(	obj			= fkWrist,
														start		= start,
														end			= end,
														sampleBy	= sampleBy,
														simulation	= True,
														attrList	= ['rx','ry','rz'] )
	
	# Duplicate IK Controls
	ikWristLoc = mc.duplicate(ikWrist,po=True)[0]
	ikElbowLoc = mc.duplicate(ikElbow,po=True)[0]
	
	# Constrain IK to FK joints
	ikWristCon = mc.pointConstraint(fkWrist,ikWristLoc)[0]
	pvWristCon = mc.pointConstraint(fkElbow,ikElbowLoc)[0]
	
	# Bake Constraint Keys
	mc.refresh(suspend=True)
	mc.bakeResults(	[ikWristLoc,ikElbowLoc],
					t=(start,end),
					at=['tx','ty','tz'],
					simulation=True,
					preserveOutsideKeys=True,
					sampleBy=sampleBy	)
	mc.refresh(suspend=False)
	
	# Transfer Keys to IK Controls
	mc.copyKey(ikWristLoc,at=['tx','ty','tz'],t=(start,end))
	mc.pasteKey(ikWrist,at=['tx','ty','tz'],t=(start,end),option='replace')
	mc.copyKey(ikElbowLoc,at=['tx','ty','tz'],t=(start,end))
	mc.pasteKey(ikElbow,at=['tx','ty','tz'],t=(start,end),option='replace')
	
	# Delete Duplicate Joints and Constraints
	for item in [ikWristLoc,ikElbowLoc]:
		if mc.objExists(item):
			try: mc.delete(item)
			except Exception, e:
				print('Error deleting node "'+str(item)+'"!')
				print(str(e))
	
	# Set to FK mode
	mc.setAttr(rigNS+':config.'+side+'ArmIkFkBlend',0) # IK
	
	# Bake Wrist from Locator
	if bakeWrist:
		glTools.anim.utils.bakeAnimFromLocator(	loc			= wristLoc,
												obj			= fkWrist,
												start		= start,
												end			= end,
												sampleBy	= sampleBy,
												simulation	= True,
												attrList	= ['rx','ry','rz']	)
	
	# =================
	# - Return Result -
	# =================
	
	return [ikWrist,ikElbow]

def legIkToFk(rigNS,side,start=None,end=None,sampleBy=1):
	'''
	Bake IK leg animation to FK controls
	@param rigNS: IK/FK toggle attribute
	@type rigNS: str
	@param side: Leg side ("lf" or "rt")
	@type side: str
	@param start: Transfer animation start frame
	@type start: int or None
	@param end: Transfer animation end frame
	@type end: int or None
	@param sampleBy: Bake animation by N frames
	@type sampleBy: int
	'''
	# Get Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	# Set Leg to IK mode
	mc.setAttr(rigNS+':config.'+side+'LegIkFkBlend',0) # IK
	
	# Build IK/FK Joint List
	ikJntList = [rigNS+':'+side+'_leg_ik'+i+'_jnt' for i in ['A','B']]
	ikJntList += [rigNS+':'+side+'_foot_ik'+i+'_jnt' for i in ['A','B']]
	fkJntList = [rigNS+':'+side+'_leg_fk'+i+'_jnt' for i in ['A','B']]
	fkJntList += [rigNS+':'+side+'_foot_fk'+i+'_jnt' for i in ['A','B']]
	
	# Duplicate FK Joints and Constrain to IK
	fkDupList = []
	fkOriList = []
	for i in range(len(ikJntList)):
		fkDupList.append(mc.duplicate(fkJntList[i],po=True)[0])
		fkOriList.append(mc.orientConstraint(ikJntList[i],fkDupList[-1])[0])
	
	# Transfer Baked Anim to FK Joints
	mc.refresh(suspend=True)
	for i in range(len(fkDupList)):
		mc.bakeResults(	fkDupList[i],
						t=(start,end),
						at=['rx','ry','rz'],
						simulation=True,
						preserveOutsideKeys=True,
						sampleBy=sampleBy	)
		mc.copyKey(fkDupList[i],at=['rx','ry','rz'],t=(start,end))
		mc.pasteKey(fkJntList[i],at=['rx','ry','rz'],t=(start,end),option='replace')
	mc.refresh(suspend=False)
	
	# Delete Duplicate Joints and Constraints
	if fkOriList:
		try: mc.delete(fkOriList)
		except Exception, e: print('Error deleting nodes '+str(fkOriList)+'! Exception Msg: '+str(e))
	if fkDupList:
		try: mc.delete(fkDupList)
		except Exception, e: print('Error deleting nodes '+str(fkDupList)+'! Exception Msg: '+str(e))
	
	# Set to FK mode
	mc.setAttr(rigNS+':config.'+side+'LegIkFkBlend',1) # FK

def legFkToIk(rigNS,side,start=None,end=None,sampleBy=1):
	'''
	Bake FK leg animation to IK controls
	@param rigNS: IK/FK toggle attribute
	@type rigNS: str
	@param side: Leg side ("lf" or "rt")
	@type side: str
	@param start: Transfer animation start frame
	@type start: int or None
	@param end: Transfer animation end frame
	@type end: int or None
	@param sampleBy: Bake animation by N frames
	@type sampleBy: int
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Get Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	# Set Leg to FK mode
	mc.setAttr(rigNS+':config.'+side+'LegIkFkBlend',1) # FK
	
	# Get IK Controls
	ikAnkle = rigNS+':'+side+'_leg_ik_ctrl'
	ikKnee = rigNS+':'+side+'_leg_pv_ctrl'
	ikToe = rigNS+':'+side+'_foot_toe_ctrl'
	
	# Get FK Joints
	fkLeg = rigNS+':'+side+'_leg_fkA_jnt'
	fkKnee = rigNS+':'+side+'_leg_fkB_jnt'
	fkFoot = rigNS+':'+side+'_foot_fkA_jnt'
	fkToe = rigNS+':'+side+'_foot_fkB_jnt'
	
	# =====================
	# - Transfer FK to IK -
	# =====================
	
	# Duplicate IK Controls
	ikAnkleLoc = mc.duplicate(ikAnkle,po=True)[0]
	ikKneeLoc = mc.duplicate(ikKnee,po=True)[0]
	ikToeLoc = mc.duplicate(ikToe,po=True)[0]
	
	# Constrain IK to FK joints
	ikWristCon = mc.pointConstraint(fkFoot,ikAnkleLoc)[0]
	pvWristCon = mc.pointConstraint(fkKnee,ikKneeLoc)[0]
	
	# Set to IK mode
	mc.setAttr(rigNS+':config.'+side+'LegIkFkBlend',0) # IK
	
	# =================
	# - Return Result -
	# =================
	
	return [ikAnkle,ikKnee]

def limbsIkToFkOLD(rigNS,start=None,end=None,sampleBy=1):
	'''
	Bake IK limb animation to FK controls
	@param rigNS: IK/FK toggle attribute
	@type rigNS: str
	@param start: Transfer animation start frame
	@type start: int or None
	@param end: Transfer animation end frame
	@type end: int or None
	@param sampleBy: Bake animation by N frames
	@type sampleBy: int
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Get Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	# ==========================
	# - Build IK/FK Joint List -
	# ==========================
	
	ikJntList = []
	fkJntList = []
	
	index = ['A','B']
	sides = ['lf','rt']
	for side in sides:
		if not mc.getAttr(rigNS+':config.'+side+'ArmIkFkBlend'):
			#ikJntList += [rigNS+':'+side+'_arm_ik'+i+'_jnt' for i in index]
			#fkJntList += [rigNS+':'+side+'_arm_fk'+i+'_jnt' for i in index]
			
			armIkToFk(rigNS,side,True,start,end,sampleBy)
			
		if not mc.getAttr(rigNS+':config.'+side+'LegIkFkBlend'):
			#ikJntList += [rigNS+':'+side+'_leg_ik'+i+'_jnt' for i in index]
			#fkJntList += [rigNS+':'+side+'_leg_fk'+i+'_jnt' for i in index]
			#ikJntList += [rigNS+':'+side+'_foot_ik'+i+'_jnt' for i in index]
			#fkJntList += [rigNS+':'+side+'_foot_fk'+i+'_jnt' for i in index]
			
			legIkToFk(rigNS,side,start,end,sampleBy)
	
	# Check IK/FK State
	if not fkJntList:
		print('Limbs already in FK mode! Nothing to do...')
		return fkJntList
	
	# ====================================
	# - Bake Wrist Animation to Locators -
	# ====================================
	
	# Build Wrist Duplicates for Baking
	wristJnts = [rigNS+':'+side+'_handA_jnt' for side in sides]
	wristDups = [mc.duplicate(jnt,po=True)[0] for jnt in wristJnts]
	keys = mc.copyKey(wristJnts,at=['rx','ry','rz'],t=(start,end))
	if keys: mc.pasteKey(wristDups,at=['rx','ry','rz'],t=(start,end),option='replace')
	
	# Bake Wrists to Locators
	wristLocs = glTools.anim.utils.bakeAnimToLocators(	objList		= wristJnts,
														start		= start,
														end			= end,
														sampleBy	= sampleBy,
														simulation	= True,
														attrList	= ['rx','ry','rz'] )
	
	# =======================
	# - Bake Limb Animation -
	# =======================
	
	# Duplicate FK Joints and Constrain to IK
	fkDupList = []
	fkOriList = []
	for i in range(len(ikJntList)):
		fkDupList.append(mc.duplicate(fkJntList[i],po=True)[0])
		fkOriList.append(mc.orientConstraint(ikJntList[i],fkDupList[-1])[0])
	
	# Transfer Baked Anim to FK Joints
	mc.refresh(suspend=True)
	for i in range(len(fkDupList)):
		mc.bakeResults(	fkDupList[i],
						t=(start,end),
						at=['rx','ry','rz'],
						simulation=True,
						preserveOutsideKeys=True,
						sampleBy=sampleBy )
	
	# Transfer Keys
	for i in range(len(fkDupList)):
		keys = mc.copyKey(fkDupList[i],at=['rx','ry','rz'],t=(start,end))
		if keys: mc.pasteKey(fkJntList[i],at=['rx','ry','rz'],t=(start,end),option='replace')
	
	mc.refresh(suspend=False)
	
	# Delete Duplicate Joints and Constraints
	if fkOriList:
		try: mc.delete(fkOriList)
		except Exception, e: print('Error deleting nodes '+str(fkOriList)+'! Exception Msg: '+str(e))
	if fkDupList:
		try: mc.delete(fkDupList)
		except Exception, e: print('Error deleting nodes '+str(fkDupList)+'! Exception Msg: '+str(e))
	
	# ======================================
	# - Bake Wrist Animation from Locators -
	# ======================================
	
	# Set to FK Mode
	for side in sides:
		mc.setAttr(rigNS+':config.'+side+'ArmIkFkBlend',1)
		mc.setAttr(rigNS+':config.'+side+'LegIkFkBlend',1)
	
	# Bake Wrists from Locators
	glTools.anim.utils.bakeAnimFromLocators(	locList		= wristLocs,
											start		= start,
											end			= end,
											sampleBy	= sampleBy,
											simulation	= True,
											attrList	= ['rx','ry','rz'] )
	
	# Transfer Baked Keys
	keys = mc.copyKey(wristDups,at=['rx','ry','rz'],t=(start,end))
	if keys: mc.pasteKey(wristJnts,at=['rx','ry','rz'],t=(start,end),option='replace')
	
	# Cleanup
	if wristLocs:
		try: mc.delete(wristLocs)
		except: pass
	if wristDups:
		try: mc.delete(wristDups)
		except: pass
	
	# =================
	# - Return Result -
	# =================
	
	return fkJntList

def limbsIkToFk(rigNS,start=None,end=None,sampleBy=1,lock=False):
	'''
	Bake IK limb animation to FK controls
	@param rigNS: IK/FK toggle attribute
	@type rigNS: str
	@param start: Transfer animation start frame
	@type start: int or None
	@param end: Transfer animation end frame
	@type end: int or None
	@param sampleBy: Bake animation by N frames
	@type sampleBy: int
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Get Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	# ==========================
	# - Build IK/FK Joint List -
	# ==========================
	
	index = ['A','B']
	sides = ['lf','rt']
	for side in sides:
		if not mc.getAttr(rigNS+':config.'+side+'ArmIkFkBlend'):
			armIkToFk(rigNS,side,True,start,end,sampleBy)
			if lock: mc.cutKey(rigNS+':config.'+side+'ArmIkFkBlend')
		if not mc.getAttr(rigNS+':config.'+side+'LegIkFkBlend'):
			legIkToFk(rigNS,side,start,end,sampleBy)
			if lock: mc.cutKey(rigNS+':config.'+side+'ArmIkFkBlend')
	
	# =================
	# - Return Result -
	# =================
	
	print('Limbs IK -> FK bake complete!')
	return

def armIkToFk_fromSel():
	'''
	Bake IK arm animation to FK controls from user selection
	'''
	# Get User Selection
	sel = mc.ls(sl=1,transforms=True)
	if not sel:
		print('Invalid or empty selection! Unable to transfer IK to FK...')
		return
	
	# Iterate Over Selection
	for item in sel:
		
		# Get Item Namespace
		rigNS = glTools.utils.namespace.getNS(item)
		if rigNS: rigNS += ':'
		else: rigNS = ''
		
		# Check Side
		side = ''
		if item.startswith(rigNS+'lf'): side = 'lf'
		if item.startswith(rigNS+'rt'): side = 'rt'
		if not side:
			print('Invalid side item ('+item+')! Select left ("lf*") or right ("rt*") control...')
			continue
		
		# Check IK Control(s)
		ikCtrl = rigNS+side+'_arm_ik_ctrl'
		if not mc.objExists(ikCtrl):
			print('IK control "'+ikCtrl+'" not found! Unable to transfer IK to FK...')
			continue
		
		# Transfer IK to FK
		try: armIkToFk(rigNS[:-1],side)
		except Exception, e: print('Error transferring IK to FK! Exception Msg: '+str(e))
		else: print('IK to FK animation transfer complete - '+rigNS+side)

def armFkToIk_fromSel():
	'''
	Bake FK arm animation to IK controls from user selection
	'''
	# Get User Selection
	sel = mc.ls(sl=1,transforms=True)
	if not sel:
		print('Invalid or empty selection! Unable to transfer FK to IK...')
		return
	
	# Iterate Over Selection
	for item in sel:
		
		# Get Item Namespace
		rigNS = glTools.utils.namespace.getNS(item)
		if rigNS: rigNS += ':'
		else: rigNS = ''
		
		# Check Side
		side = ''
		if item.startswith(rigNS+'lf'): side = 'lf'
		if item.startswith(rigNS+'rt'): side = 'rt'
		if not side:
			print('Invalid side item ('+item+')! Select left ("lf*") or right ("rt*") control...')
			continue
		
		# Check FK Control(s)
		fkCtrl = rigNS+side+'_arm_fkA_jnt'
		if not mc.objExists(fkCtrl):
			print('FK control "'+fkCtrl+'" not found! Unable to transfer FK to IK...')
			continue
		
		# Transfer FK to IK
		try: armFkToIk(rigNS[:-1],side)
		except Exception, e: print('Error transferring FK to IK! Exception Msg: '+str(e))
		else: print('FK to IK animation transfer complete - '+rigNS+side)

