import maya.cmds as mc

import glTools.rig.utils

import glTools.utils.joint
import glTools.utils.stringUtils
import glTools.tools.controlBuilder

def build(sourceJoint,targetJoint,twistJoints,aimAxis='x',upAxis='y',baseToTip=True,prefix=''):
	'''
	Build twist joint setup using an aimConstraint to calculate rotation.
	@param sourceJoint: Twist base joint 
	@type sourceJoint: str
	@param targetJoint: Twist target or end joint
	@type targetJoint: str
	@param twistJoints: List of twist joints 
	@type twistJoints: list
	@param aimAxis: Axis along the length of the source joint 
	@type aimAxis: list or tuple
	@param upAxis: Upward facing axis of the source joint 
	@type upAxis: list or tuple
	@param baseToTip: Twist from the base to the tip 
	@type baseToTip: bool
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(sourceJoint):
		raise Exception('Source joint "'+sourceJoint+'" does not exist!')
	if not mc.objExists(targetJoint):
		raise Exception('Target joint "'+targetJoint+'" does not exist!')
	for twistJoint in twistJoints:
		if not mc.objExists(twistJoint):
			raise Exception('Twist joint "'+twistJoint+'" does not exist!')
			
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(sourceJoint)
	
	# ======================
	# - Configure Modifier -
	# ======================
	
	# Define Axis Dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	twistCtrlScale = 0.2
	
	# =======================
	# - Create Twist Joints -
	# =======================
	
	# Check baseToTip - Reverse list order if false
	if not baseToTip: twistJoints.reverse()
	
	twistJointGrp = []
	twistFactor = 1.0/(len(twistJoints)-1)
	jntLen = glTools.utils.joint.length(sourceJoint)
	for i in range(len(twistJoints)):
		
		controlShape = glTools.tools.controlBuilder.controlShape(twistJoints[i],'box',scale=twistCtrlScale*jntLen)
		glTools.rig.utils.tagCtrl(twistJoints[i],'tertiary')
		twistJointGrp.append(glTools.utils.joint.group(twistJoints[i],indexStr='Twist'))
		mc.addAttr(twistJoints[i],ln='twist',min=-1.0,max=1.0,dv=twistFactor*i)
	
	# ==========================
	# - Create Twist Aim Setup -
	# ==========================
	
	# Create Twist Aim Joint
	twistAimJnt = mc.duplicate(sourceJoint,po=True,n=prefix+'_twistAim_jnt')[0]
	mc.parent(twistAimJnt,sourceJoint)
	
	# Create Twist Aim Locator
	twistAimLoc = mc.group(em=True,n=prefix+'_twistAim_loc')
	mc.delete(mc.pointConstraint(targetJoint,twistAimLoc,mo=False))
	mc.delete(mc.orientConstraint(sourceJoint,twistAimLoc,mo=False))
	mc.parent(twistAimLoc,targetJoint)
	
	# Create Twist Aim Constraint
	twistAimCon = mc.aimConstraint(targetJoint,twistAimJnt,aim=axisDict[aimAxis],u=axisDict[upAxis],wu=axisDict[upAxis],wuo=twistAimLoc,wut='objectrotation')[0]
	
	# ========================
	# - Connect Twist Joints -
	# ========================
	
	twistMultNode = []
	for i in range(len(twistJoints)):
		
		alphaInd = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		twistMult = mc.createNode('multDoubleLinear',n=prefix+'_twist'+alphaInd+'_multDoubleLinear')
		mc.connectAttr(twistAimJnt+'.r'+aimAxis[-1],twistMult+'.input1',f=True)
		mc.connectAttr(twistJoints[i]+'.twist',twistMult+'.input2',f=True)
		mc.connectAttr(twistMult+'.output',twistJointGrp[i]+'.r'+aimAxis[-1],f=True)
		twistMultNode.append(twistMult)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=twistJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=twistJointGrp)
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = twistJoints
	
	return

def build_shoulder(shoulder,spine,twistJoints,shoulderAim='x',shoulderFront='y',spineAim='x',spineFront='y',prefix=''):
	'''
	Build shoudler twist using custom shoulderConstraint node
	@param shoulder: Shoulder or upper arm joint 
	@type shoulder: str
	@param spine: Spine end joint 
	@type spine: str
	@param twistJoints: List of twist joints 
	@type twistJoints: list
	@param shoulderAim: Axis along the length of the shoulder joint 
	@type shoulderAim: list or tuple
	@param shoulderFront: Forward facing axis of the shoulder joint 
	@type shoulderFront: list or tuple
	@param spineAim: Axis along the length of the spine joint 
	@type spineAim: list or tuple
	@param spineFront: Forward facing axis of the spine joint 
	@type spineFront: list or tuple
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(shoulder):
		raise Exception('Shoulder joint "'+shoulder+'" does not exist!')
	if not mc.objExists(spine):
		raise Exception('Spine joint "'+spine+'" does not exist!')
	for twistJoint in twistJoints:
		if not mc.objExists(twistJoint):
			raise Exception('Twist joint "'+twistJoint+'" does not exist!')
			
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(shoulder)
	
	# Check Plugin
	if not mc.pluginInfo('twistConstraint',q=True,l=True):
		try: mc.loadPlugin('twistConstraint')
		except: raise Exception('Unable to load plugin "twistConstraint"!')
	
	# ======================
	# - Configure Modifier -
	# ======================
	
	# Define Axis Dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	twistCtrlScale = 0.2
	
	# =======================
	# - Create Twist Joints -
	# =======================
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# Create Twist Driver Joint
	mc.select(cl=True)
	shoulderTwist = mc.joint(n=prefix+'_jnt')
	shoulderTwistGrp = glTools.utils.joint.group(shoulderTwist)
	mc.delete(mc.parentConstraint(shoulder,shoulderTwistGrp))
	mc.parent(shoulderTwistGrp,shoulder)
	
	# Create Shoulder Twist Joints
	twistJointGrp = []
	twistFactor = 1.0/(len(twistJoints)-1)
	jntLen = glTools.utils.joint.length(shoulder)
	for i in range(len(twistJoints)):
		
		controlShape = glTools.tools.controlBuilder.controlShape(twistJoints[i],'box',scale=twistCtrlScale*jntLen)
		glTools.rig.utils.tagCtrl(twistJoints[i],'tertiary')
		mc.addAttr(twistJoints[i],ln='twist',min=-1.0,max=1.0,dv=twistFactor*i)
		twistJointGrp.append(glTools.utils.joint.group(twistJoints[i]))
	
	# ===============================
	# - Create Shoudler Twist Setup -
	# ===============================
	
	# Create shoulderConstraint node
	shoulderCon = mc.createNode('shoulderConstraint')
	
	# Set and connect shoulderConstraint attributes
	mc.connectAttr(shoulder+'.worldMatrix[0]',shoulderCon+'.shoulder',f=True)
	mc.connectAttr(spine+'.worldMatrix[0]',shoulderCon+'.spine',f=True)
	mc.connectAttr(shoulderTwist+'.parentInverseMatrix[0]',shoulderCon+'.parentInverseMatrix',f=True)
	mc.connectAttr(shoulderTwist+'.rotateOrder',shoulderCon+'.rotateOrder',f=True)
	mc.connectAttr(shoulderTwist+'.jointOrient',shoulderCon+'.jointOrient',f=True)
	mc.setAttr(shoulderCon+'.shoulderAim',*axisDict[shoulderAim])
	mc.setAttr(shoulderCon+'.shoulderFront',*axisDict[shoulderFront])
	mc.setAttr(shoulderCon+'.spineAim',*axisDict[spineAim])
	mc.setAttr(shoulderCon+'.spineFront',*axisDict[spineFront])
	
	# Connect to shoudler twist joint
	mc.connectAttr(shoulderCon+'.outRotate',shoulderTwist+'.rotate',f=True)
	
	# Correct initial offset
	twistOffset = mc.getAttr(shoulderTwist+'.r'+shoulderAim[-1])
	mc.setAttr(shoulderTwist+'.jo'+shoulderAim[-1],twistOffset)
	
	# ========================
	# - Connect Twist Joints -
	# ========================
	
	twistMultNode = []
	for i in range(len(twistJoints)):
		
		alphaInd = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		twistMult = mc.createNode('multDoubleLinear',n=prefix+'_twist'+alphaInd+'_multDoubleLinear')
		mc.connectAttr(shoulderTwist+'.r'+shoulderAim[-1],twistMult+'.input1',f=True)
		mc.connectAttr(twistJoints[i]+'.twist',twistMult+'.input2',f=True)
		mc.connectAttr(twistMult+'.output',twistJointGrp[i]+'.r'+shoulderAim[-1],f=True)
		twistMultNode.append(twistMult)
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=twistJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=twistJointGrp)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[shoulderTwistGrp])
	chStateUtil.setFlags([2,2,2,1,1,1,2,2,2,1],objectList=[shoulderTwist])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = twistJoints
	
	return

def build_shoulderAM(shoulder,spine,twistJoints,shoulderAim='x',shoulderFront='y',spineAim='x',spineFront='y',prefix=''):
	'''
	Build shoudler twist using custom shoulderConstraint node
	@param shoulder: Shoulder or upper arm joint 
	@type shoulder: str
	@param spine: Spine end joint 
	@type spine: str
	@param twistJoints: List of twist joints 
	@type twistJoints: list
	@param shoulderAim: Axis along the length of the shoulder joint 
	@type shoulderAim: list or tuple
	@param shoulderFront: Forward facing axis of the shoulder joint 
	@type shoulderFront: list or tuple
	@param spineAim: Axis along the length of the spine joint 
	@type spineAim: list or tuple
	@param spineFront: Forward facing axis of the spine joint 
	@type spineFront: list or tuple
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(shoulder):
		raise Exception('Shoulder joint "'+shoulder+'" does not exist!')
	if not mc.objExists(spine):
		raise Exception('Spine joint "'+spine+'" does not exist!')
	for twistJoint in twistJoints:
		if not mc.objExists(twistJoint):
			raise Exception('Twist joint "'+twistJoint+'" does not exist!')
			
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(shoulder)
	
	# Check Plugin
	if not mc.pluginInfo('AM_ShoulderConstraint',q=True,l=True):
		try: mc.loadPlugin('AM_ShoulderConstraint')
		except: raise Exception('Unable to load plugin "AM_ShoulderConstraint"!')
	
	# ======================
	# - Configure Modifier -
	# ======================
	
	# Define Axis Dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	twistCtrlScale = 0.2
	
	# =======================
	# - Create Twist Joints -
	# =======================
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# Create Twist Driver Joint
	mc.select(cl=True)
	shoulderTwist = mc.joint(n=prefix+'_jnt')
	shoulderTwistGrp = glTools.utils.joint.group(shoulderTwist)
	mc.delete(mc.parentConstraint(shoulder,shoulderTwistGrp))
	mc.parent(shoulderTwistGrp,shoulder)
	
	# Create Shoulder Twist Joints
	twistJointGrp = []
	twistFactor = 1.0/(len(twistJoints)-1)
	jntLen = glTools.utils.joint.length(shoulder)
	for i in range(len(twistJoints)):
		
		controlShape = glTools.tools.controlBuilder.controlShape(twistJoints[i],'box',scale=twistCtrlScale*jntLen)
		glTools.rig.utils.tagCtrl(twistJoints[i],'tertiary')
		mc.addAttr(twistJoints[i],ln='twist',min=-1.0,max=1.0,dv=twistFactor*i)
		twistJointGrp.append(glTools.utils.joint.group(twistJoints[i]))
	
	# ===============================
	# - Create Shoudler Twist Setup -
	# ===============================
	
	# Create shoulderConstraint node
	shoulderCon = mc.createNode('am_shoulderConstraint')
	
	# Set and connect shoulderConstraint attributes
	mc.connectAttr(shoulder+'.worldMatrix[0]',shoulderCon+'.shoulder',f=True)
	mc.connectAttr(spine+'.worldMatrix[0]',shoulderCon+'.spine',f=True)
	mc.connectAttr(shoulderTwist+'.parentInverseMatrix[0]',shoulderCon+'.parentInverseMatrix',f=True)
	mc.connectAttr(shoulderTwist+'.rotateOrder',shoulderCon+'.rotateOrder',f=True)
	mc.connectAttr(shoulderTwist+'.jointOrient',shoulderCon+'.jointOrient',f=True)
	mc.setAttr(shoulderCon+'.shoulderAim',*axisDict[shoulderAim])
	mc.setAttr(shoulderCon+'.shoulderFront',*axisDict[shoulderFront])
	mc.setAttr(shoulderCon+'.spineAim',*axisDict[spineAim])
	mc.setAttr(shoulderCon+'.spineFront',*axisDict[spineFront])
	
	# Connect to shoudler twist joint
	mc.connectAttr(shoulderCon+'.rotate',shoulderTwist+'.rotate',f=True)
	
	# Correct initial offset
	twistOffset = mc.getAttr(shoulderTwist+'.r'+shoulderAim[-1])
	mc.setAttr(shoulderTwist+'.jo'+shoulderAim[-1],twistOffset)
	
	# ========================
	# - Connect Twist Joints -
	# ========================
	
	twistMultNode = []
	for i in range(len(twistJoints)):
		
		alphaInd = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		twistMult = mc.createNode('multDoubleLinear',n=prefix+'_twist'+alphaInd+'_multDoubleLinear')
		mc.connectAttr(shoulderTwist+'.r'+shoulderAim[-1],twistMult+'.input1',f=True)
		mc.connectAttr(twistJoints[i]+'.twist',twistMult+'.input2',f=True)
		mc.connectAttr(twistMult+'.output',twistJointGrp[i]+'.r'+shoulderAim[-1],f=True)
		twistMultNode.append(twistMult)
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=twistJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=twistJointGrp)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[shoulderTwistGrp])
	chStateUtil.setFlags([2,2,2,1,1,1,2,2,2,1],objectList=[shoulderTwist])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = twistJoints
	
	return

def build_hip(hip,pelvis,twistJoints,hipAim='x',hipFront='y',pelvisAim='x',pelvisFront='y',prefix=''):
	'''
	Build hip twist using custom hipConstraint node
	@param hip: Hip or upper leg joint 
	@type hip: str
	@param pelvis: Pelvis joint 
	@type pelvis: str
	@param twistJoints: List of twist joints 
	@type twistJoints: list
	@param hipAim: Axis along the length of the hip/leg joint 
	@type hipAim: list or tuple
	@param hipFront: Forward facing axis of the hip/leg joint 
	@type hipFront: list or tuple
	@param pelvisAim: Axis along the length of the pelvis joint 
	@type pelvisAim: list or tuple
	@param pelvisFront: Forward facing axis of the pelvis joint 
	@type pelvisFront: list or tuple
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(hip):
		raise Exception('Hip joint "'+hip+'" does not exist!')
	if not mc.objExists(pelvis):
		raise Exception('Pelvis joint "'+pelvis+'" does not exist!')
	for twistJoint in twistJoints:
		if not mc.objExists(twistJoint):
			raise Exception('Twist joint "'+twistJoint+'" does not exist!')
			
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(hip)
	
	# Check Plugin
	if not mc.pluginInfo('twistConstraint',q=True,l=True):
		try: mc.loadPlugin('twistConstraint')
		except: raise Exception('Unable to load plugin "twistConstraint"!')
	
	# ======================
	# - Configure Modifier -
	# ======================
	
	# Define Axis Dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	twistCtrlScale = 0.2
	
	# =======================
	# - Create Twist Joints -
	# =======================
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# Create Twist Driver Joint
	mc.select(cl=True)
	hipTwist = mc.joint(n=prefix+'Twist_jnt')
	hipTwistGrp = glTools.utils.joint.group(hipTwist)
	mc.delete(mc.parentConstraint(hip,hipTwistGrp))
	mc.parent(hipTwistGrp,hip)
	
	# Create Hip Twist Joints
	twistJointGrp = []
	twistFactor = 1.0/(len(twistJoints)-1)
	jntLen = glTools.utils.joint.length(hip)
	for i in range(len(twistJoints)):
		
		controlShape = glTools.tools.controlBuilder.controlShape(twistJoints[i],'box',scale=twistCtrlScale*jntLen)
		glTools.rig.utils.tagCtrl(twistJoints[i],'tertiary')
		mc.addAttr(twistJoints[i],ln='twist',min=-1.0,max=1.0,dv=twistFactor*i)
		twistJointGrp.append(glTools.utils.joint.group(twistJoints[i]))
	
	# ==========================
	# - Create Hip Twist Setup -
	# ==========================
	
	# Create hipConstraint node
	hipCon = mc.createNode('hipConstraint')
	
	# Set and connect hipConstraint attributes
	mc.connectAttr(hip+'.worldMatrix[0]',hipCon+'.hip',f=True)
	mc.connectAttr(pelvis+'.worldMatrix[0]',hipCon+'.pelvis',f=True)
	mc.connectAttr(hipTwist+'.parentInverseMatrix[0]',hipCon+'.parentInverseMatrix',f=True)
	mc.connectAttr(hipTwist+'.rotateOrder',hipCon+'.rotateOrder',f=True)
	mc.connectAttr(hipTwist+'.jointOrient',hipCon+'.jointOrient',f=True)
	mc.setAttr(hipCon+'.hipAim',*axisDict[hipAim])
	mc.setAttr(hipCon+'.hipFront',*axisDict[hipFront])
	mc.setAttr(hipCon+'.pelvisAim',*axisDict[pelvisAim])
	mc.setAttr(hipCon+'.pelvisFront',*axisDict[pelvisFront])
	
	# Connect to hip twist joint
	mc.connectAttr(hipCon+'.outRotate',hipTwist+'.rotate',f=True)
	
	# Correct initial offset
	twistOffset = mc.getAttr(hipTwist+'.r'+hipAim[-1])
	mc.setAttr(hipTwist+'.jo'+hipAim[-1],twistOffset)
	
	# ========================
	# - Connect Twist Joints -
	# ========================
	
	twistMultNode = []
	for i in range(len(twistJoints)):
		
		alphaInd = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		twistMult = mc.createNode('multDoubleLinear',n=prefix+'_twist'+alphaInd+'_multDoubleLinear')
		mc.connectAttr(hipTwist+'.r'+hipAim[-1],twistMult+'.input1',f=True)
		mc.connectAttr(twistJoints[i]+'.twist',twistMult+'.input2',f=True)
		mc.connectAttr(twistMult+'.output',twistJointGrp[i]+'.r'+hipAim[-1],f=True)
		twistMultNode.append(twistMult)
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=twistJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=twistJointGrp)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[hipTwistGrp])
	chStateUtil.setFlags([2,2,2,1,1,1,2,2,2,1],objectList=[hipTwist])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = twistJoints
	
	return

def build_hipAM(hip,pelvis,twistJoints,hipAim='x',hipFront='y',pelvisAim='x',pelvisFront='y',prefix=''):
	'''
	Build hip twist using custom hipConstraint node
	@param hip: Hip or upper leg joint 
	@type hip: str
	@param pelvis: Pelvis joint 
	@type pelvis: str
	@param twistJoints: List of twist joints 
	@type twistJoints: list
	@param hipAim: Axis along the length of the hip/leg joint 
	@type hipAim: list or tuple
	@param hipFront: Forward facing axis of the hip/leg joint 
	@type hipFront: list or tuple
	@param pelvisAim: Axis along the length of the pelvis joint 
	@type pelvisAim: list or tuple
	@param pelvisFront: Forward facing axis of the pelvis joint 
	@type pelvisFront: list or tuple
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(hip):
		raise Exception('Hip joint "'+hip+'" does not exist!')
	if not mc.objExists(pelvis):
		raise Exception('Pelvis joint "'+pelvis+'" does not exist!')
	for twistJoint in twistJoints:
		if not mc.objExists(twistJoint):
			raise Exception('Twist joint "'+twistJoint+'" does not exist!')
			
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(hip)
	
	# Check Plugin
	if not mc.pluginInfo('AM_HipConstraint',q=True,l=True):
		try: mc.loadPlugin('AM_HipConstraint')
		except: raise Exception('Unable to load plugin "AM_HipConstraint"!')
	
	# ======================
	# - Configure Modifier -
	# ======================
	
	# Define Axis Dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	twistCtrlScale = 0.2
	
	# =======================
	# - Create Twist Joints -
	# =======================
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# Create Twist Driver Joint
	mc.select(cl=True)
	hipTwist = mc.joint(n=prefix+'Twist_jnt')
	hipTwistGrp = glTools.utils.joint.group(hipTwist)
	mc.delete(mc.parentConstraint(hip,hipTwistGrp))
	mc.parent(hipTwistGrp,hip)
	
	# Create Hip Twist Joints
	twistJointGrp = []
	twistFactor = 1.0/(len(twistJoints)-1)
	jntLen = glTools.utils.joint.length(hip)
	for i in range(len(twistJoints)):
		
		controlShape = glTools.tools.controlBuilder.controlShape(twistJoints[i],'box',scale=twistCtrlScale*jntLen)
		glTools.rig.utils.tagCtrl(twistJoints[i],'tertiary')
		mc.addAttr(twistJoints[i],ln='twist',min=-1.0,max=1.0,dv=twistFactor*i)
		twistJointGrp.append(glTools.utils.joint.group(twistJoints[i]))
	
	# ==========================
	# - Create Hip Twist Setup -
	# ==========================
	
	# Create hipConstraint node
	hipCon = mc.createNode('am_hipConstraint')
	
	# Set and connect hipConstraint attributes
	mc.connectAttr(hip+'.worldMatrix[0]',hipCon+'.hip',f=True)
	mc.connectAttr(pelvis+'.worldMatrix[0]',hipCon+'.pelvis',f=True)
	mc.connectAttr(hipTwist+'.parentInverseMatrix[0]',hipCon+'.parentInverseMatrix',f=True)
	mc.connectAttr(hipTwist+'.rotateOrder',hipCon+'.rotateOrder',f=True)
	mc.connectAttr(hipTwist+'.jointOrient',hipCon+'.jointOrient',f=True)
	mc.setAttr(hipCon+'.hipAim',*axisDict[hipAim])
	mc.setAttr(hipCon+'.hipFront',*axisDict[hipFront])
	mc.setAttr(hipCon+'.pelvisAim',*axisDict[pelvisAim])
	mc.setAttr(hipCon+'.pelvisFront',*axisDict[pelvisFront])
	
	# Connect to hip twist joint
	mc.connectAttr(hipCon+'.rotate',hipTwist+'.rotate',f=True)
	
	# Correct initial offset
	twistOffset = mc.getAttr(hipTwist+'.r'+hipAim[-1])
	mc.setAttr(hipTwist+'.jo'+hipAim[-1],twistOffset)
	
	# ========================
	# - Connect Twist Joints -
	# ========================
	
	twistMultNode = []
	for i in range(len(twistJoints)):
		
		alphaInd = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		twistMult = mc.createNode('multDoubleLinear',n=prefix+'_twist'+alphaInd+'_multDoubleLinear')
		mc.connectAttr(hipTwist+'.r'+hipAim[-1],twistMult+'.input1',f=True)
		mc.connectAttr(twistJoints[i]+'.twist',twistMult+'.input2',f=True)
		mc.connectAttr(twistMult+'.output',twistJointGrp[i]+'.r'+hipAim[-1],f=True)
		twistMultNode.append(twistMult)
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=twistJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=twistJointGrp)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[hipTwistGrp])
	chStateUtil.setFlags([2,2,2,1,1,1,2,2,2,1],objectList=[hipTwist])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = twistJoints
	
	return
