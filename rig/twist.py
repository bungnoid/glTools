import maya.cmds as mc

import glTools.rig.utils

import glTools.utils.attribute
import glTools.utils.base
import glTools.utils.joint
import glTools.utils.stringUtils
import glTools.tools.controlBuilder

def createTwistJoints(	joint,
						numTwistJoints,
						offsetAxis = 'x',
						prefix = ''	):
	'''
	Generate twist joints for a specified rig joint.
	This function only creates the joints, it does not setup the twist control network.
	@param joint: Master rig joint that will drive the twist
	@type joint: str
	@param numTwistJoints: Number of twist joints to create
	@type numTwistJoints: int
	@param offsetAxis: Twist joint offset axis
	@type offsetAxis: str
	@param prefix: Naming prefix for twist joints
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check joint
	if not mc.objExists(joint):
		raise Exception('Joint '+joint+' does not exist!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(joint)
	
	# Offset Axis
	if not ['x','y','z'].count(offsetAxis):
		raise Exception('Invalid offset axis value! ("'+offsetAxis+'")')
	
	# =================
	# - Create Joints -
	# =================
	
	# Get joint length
	jointEnd = mc.listRelatives(joint,c=True)[0]
	jointLen = mc.getAttr(jointEnd+'.t'+offsetAxis)
	jointOffset = jointLen/(numTwistJoints-1)
	
	# Create twist joints
	twistJoints = []
	for i in range(numTwistJoints):
		
		alphaInd = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		
		# Duplicate joint
		twistJoint = mc.duplicate(joint,po=True,n=prefix+'_twist'+alphaInd+'_jnt')[0]
		# Remove user attributes
		glTools.utils.attribute.deleteUserAttrs(twistJoint)
		# Parent to joint
		mc.parent(twistJoint,joint)
		
		# Position joint
		mc.setAttr(twistJoint+'.t'+offsetAxis,jointOffset*i)
		
		# Append joint list
		twistJoints.append(twistJoint)
		
	# =================
	# - Return Result -
	# =================
	
	return twistJoints

def build(	sourceJoint,
			targetJoint,
			numJoints = 4,
			aimAxis = 'x',
			upAxis = 'y',
			baseToTip = True,
			enableCtrl = False,
			prefix = ''	):
	'''
	Build twist joint setup using an aimConstraint to calculate rotation.
	@param sourceJoint: Twist base joint 
	@type sourceJoint: str
	@param targetJoint: Twist target or end joint
	@type targetJoint: str
	@param numJoint: Number of twist joints to generate 
	@type numJoint: int
	@param aimAxis: Axis along the length of the source joint 
	@type aimAxis: list or tuple
	@param upAxis: Upward facing axis of the source joint 
	@type upAxis: list or tuple
	@param baseToTip: Twist from the base to the tip 
	@type baseToTip: bool
	@param enableCtrl: Enable the twist child joint as a control 
	@type enableCtrl: bool
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Define Axis Dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	if not mc.objExists(sourceJoint):
		raise Exception('Source joint "'+sourceJoint+'" does not exist!')
	if not mc.objExists(targetJoint):
		raise Exception('Target joint "'+targetJoint+'" does not exist!')
	
	if not axisDict.has_key(aimAxis):
		raise Exception('Invalid aim axis value! ("'+aimAxis+'")')
	if not axisDict.has_key(upAxis):
		raise Exception('Invalid up axis value! ("'+upAxis+'")')
			
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(sourceJoint)
	
	# ======================
	# - Configure Modifier -
	# ======================
	
	twistCtrlScale = 0.2
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	# =======================
	# - Create Twist Joints -
	# =======================
	
	twistJoints = createTwistJoints(	joint = sourceJoint,
										numTwistJoints = numJoints,
										offsetAxis = aimAxis[-1],
										prefix = prefix	)
	
	# Check baseToTip - Reverse list order if false
	if not baseToTip: twistJoints.reverse()
	
	# Create Joint Groups/Attributes/Tags
	twistJointGrps = []
	twistFactor = 1.0/(len(twistJoints)-1)
	jntLen = glTools.utils.joint.length(sourceJoint)
	for i in range(len(twistJoints)):
		
		# Add Twist Control Attribute
		mc.addAttr(twistJoints[i],ln='twist',min=-1.0,max=1.0,dv=twistFactor*i)
		
		# Add Twist Joint Group
		twistJointGrp = glTools.utils.joint.group(twistJoints[i],indexStr='Twist')
		twistJointGrps.append(twistJointGrp)
		
		# Tag Bind Joint
		glTools.rig.utils.tagBindJoint(twistJoints[i],True)
		
		# Create Joint Control
		if enableCtrl:
			glTools.rig.utils.tagCtrl(twistJoints[i],'tertiary')
			ctrlBuilder.controlShape(transform=twistJoints[i],controlType='sphere',controlScale=twistCtrlScale)
		
		# Set Display Override
		if enableCtrl:
			glTools.utils.base.displayOverride(twistJoints[i],overrideEnable=1,overrideDisplay=0,overrideLOD=1)
		else:
			glTools.utils.base.displayOverride(twistJoints[i],overrideEnable=1,overrideDisplay=2,overrideLOD=0)
		
	# Create Twist Group
	twistGrp = mc.joint(n=prefix+'_twistJoint_grp')
	glTools.utils.base.displayOverride(twistGrp,overrideEnable=1,overrideDisplay=2,overrideLOD=1)
	glTools.utils.transform.match(twistGrp,sourceJoint)
	mc.setAttr(twistGrp+'.segmentScaleCompensate',0)
	mc.setAttr(twistGrp+'.drawStyle',2) # None
	mc.setAttr(twistGrp+'.radius',0)
	mc.parent(twistGrp,sourceJoint)
	mc.parent(twistJointGrps,twistGrp)
	
	# Connect Inverse Scale
	for twistJointGrp in twistJointGrps:
		mc.connectAttr(sourceJoint+'.scale',twistJointGrp+'.inverseScale',f=True)
	
	# ==========================
	# - Create Twist Aim Setup -
	# ==========================
	
	# Create Twist Aim Joint
	twistAimJnt = mc.duplicate(sourceJoint,po=True,n=prefix+'_twistAim_jnt')[0]
	# Remove user attributes
	glTools.utils.attribute.deleteUserAttrs(twistAimJnt)
	# Parent to source joint
	mc.parent(twistAimJnt,sourceJoint)
	# Display Overrides
	glTools.utils.base.displayOverride(twistAimJnt,overrideEnable=1,overrideDisplay=2,overrideLOD=0)
	
	# Create Twist Aim Locator
	twistAimLoc = mc.group(em=True,n=prefix+'_twistAim_loc')
	mc.delete(mc.pointConstraint(targetJoint,twistAimLoc,mo=False))
	mc.delete(mc.orientConstraint(sourceJoint,twistAimLoc,mo=False))
	mc.parent(twistAimLoc,targetJoint)
	# Display Overrides
	glTools.utils.base.displayOverride(twistAimLoc,overrideEnable=1,overrideDisplay=2,overrideLOD=0)
	
	# Create Twist Aim Constraint
	twistAimCon = mc.aimConstraint(	targetJoint,
									twistAimJnt,
									aim=axisDict[aimAxis],
									u=axisDict[upAxis],
									wu=axisDict[upAxis],
									wuo=twistAimLoc,
									wut='objectrotation' )[0]
	
	# ========================
	# - Connect Twist Joints -
	# ========================
	
	twistMultNode = []
	for i in range(len(twistJoints)):
		
		alphaInd = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		twistMult = mc.createNode('multDoubleLinear',n=prefix+'_twist'+alphaInd+'_multDoubleLinear')
		mc.connectAttr(twistAimJnt+'.r'+aimAxis[-1],twistMult+'.input1',f=True)
		mc.connectAttr(twistJoints[i]+'.twist',twistMult+'.input2',f=True)
		mc.connectAttr(twistMult+'.output',twistJointGrps[i]+'.r'+aimAxis[-1],f=True)
		twistMultNode.append(twistMult)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[twistGrp])
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=twistJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=twistJointGrps)
	chStateUtil.setFlags([2,2,2,1,1,1,2,2,2,1],objectList=[twistAimJnt])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[twistAimLoc])
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	result['twistGrp'] = twistGrp
	result['twistJoints'] = twistJoints
	result['twistJointGrps'] = twistJointGrps
	result['twistDriveJoint'] = twistAimJnt
	result['twistAimLocator'] = twistAimLoc
	result['twistConstraint'] = twistAimCon
	result['twistMultNodes'] = twistMultNode
	return result

def build_shoulder(	shoulder,
					spine,
					numJoints = 4,
					shoulderAim = 'x',
					shoulderFront = 'y',
					spineAim = 'x',
					spineFront = 'y',
					enableCtrl = False,
					prefix = ''	):
	'''
	Build shoudler twist using custom shoulderConstraint node
	@param shoulder: Shoulder or upper arm joint 
	@type shoulder: str
	@param spine: Spine end joint 
	@type spine: str
	@param numJoint: Number of twist joints to generate 
	@type numJoint: int
	@param shoulderAim: Axis along the length of the shoulder joint 
	@type shoulderAim: list or tuple
	@param shoulderFront: Forward facing axis of the shoulder joint 
	@type shoulderFront: list or tuple
	@param spineAim: Axis along the length of the spine joint 
	@type spineAim: list or tuple
	@param spineFront: Forward facing axis of the spine joint 
	@type spineFront: list or tuple
	@param enableCtrl: Enable the twist child joint as a control 
	@type enableCtrl: bool
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Define Axis Dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	if not mc.objExists(shoulder):
		raise Exception('Shoulder joint "'+shoulder+'" does not exist!')
	if not mc.objExists(spine):
		raise Exception('Spine joint "'+spine+'" does not exist!')
	
	if not axisDict.has_key(shoulderAim):
		raise Exception('Invalid shoulder aim axis value! ("'+shoulderAim+'")')
	if not axisDict.has_key(shoulderFront):
		raise Exception('Invalid shoulder front axis value! ("'+shoulderFront+'")')
	if not axisDict.has_key(spineAim):
		raise Exception('Invalid spine aim axis value! ("'+spineAim+'")')
	if not axisDict.has_key(spineFront):
		raise Exception('Invalid spine front axis value! ("'+spineFront+'")')
			
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(shoulder)
	
	# Check Plugin
	if not mc.pluginInfo('twistConstraint',q=True,l=True):
		try: mc.loadPlugin('twistConstraint')
		except: raise Exception('Unable to load plugin "twistConstraint"!')
	
	# =====================
	# - Configure Control -
	# =====================
	
	twistCtrlScale = 0.2
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	# =======================
	# - Create Twist Joints -
	# =======================
	
	twistJoints = createTwistJoints(	joint = shoulder,
										numTwistJoints = numJoints,
										offsetAxis = shoulderAim[-1],
										prefix = prefix	)
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# Create Twist Driver Joint
	mc.select(cl=True)
	shoulderTwist = mc.joint(n=prefix+'_twistDrive_jnt')
	shoulderTwistGrp = glTools.utils.joint.group(shoulderTwist)
	mc.delete(mc.parentConstraint(shoulder,shoulderTwistGrp))
	mc.parent(shoulderTwistGrp,shoulder)
	glTools.utils.base.displayOverride(shoulderTwist,overrideEnable=1,overrideDisplay=2,overrideLOD=0)
	
	# Create Shoulder Twist Joints
	twistJointGrps = []
	twistFactor = 1.0/(len(twistJoints)-1)
	jntLen = glTools.utils.joint.length(shoulder)
	for i in range(len(twistJoints)):
		
		# Add twist attribute
		mc.addAttr(twistJoints[i],ln='twist',min=-1.0,max=1.0,dv=twistFactor*i)
		
		# Add Twist Joint Group
		twistJointGrp = glTools.utils.joint.group(twistJoints[i],indexStr='Twist')
		twistJointGrps.append(twistJointGrp)
		
		# Tag Bind joint
		glTools.rig.utils.tagBindJoint(twistJoints[i],True)
		
		# Create Joint Control
		if enableCtrl:
			glTools.rig.utils.tagCtrl(twistJoints[i],'tertiary')
			ctrlBuilder.controlShape(transform=twistJoints[i],controlType='sphere',controlScale=twistCtrlScale)
		
		# Set Display Override
		if enableCtrl:
			glTools.utils.base.displayOverride(twistJoints[i],overrideEnable=1,overrideDisplay=0,overrideLOD=1)
		else:
			glTools.utils.base.displayOverride(twistJoints[i],overrideEnable=1,overrideDisplay=2,overrideLOD=0)
	
	# Create Twist Group
	twistGrp = mc.joint(n=prefix+'_twistJoint_grp')
	glTools.utils.base.displayOverride(twistGrp,overrideEnable=1,overrideLOD=1)
	glTools.utils.transform.match(twistGrp,shoulder)
	mc.setAttr(twistGrp+'.segmentScaleCompensate',0)
	mc.setAttr(twistGrp+'.drawStyle',2) # None
	mc.setAttr(twistGrp+'.radius',0)
	mc.parent(twistGrp,shoulder)
	mc.parent(twistJointGrps,twistGrp)
	
	# Connect Inverse Scale
	for twistJointGrp in twistJointGrps:
		mc.connectAttr(shoulder+'.scale',twistJointGrp+'.inverseScale',f=True)
	
	# ===============================
	# - Create Shoulder Twist Setup -
	# ===============================
	
	# Create shoulderConstraint node
	shoulderCon = mc.createNode('shoulderConstraint',n=prefix+'_shoulderConstraint')
	
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
	mc.setAttr(shoulderCon+'.raisedAngleOffset',0)
	
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
		mc.connectAttr(twistMult+'.output',twistJointGrps[i]+'.r'+shoulderAim[-1],f=True)
		twistMultNode.append(twistMult)
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[twistGrp])
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=twistJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=twistJointGrps)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[shoulderTwistGrp])
	chStateUtil.setFlags([2,2,2,1,1,1,2,2,2,1],objectList=[shoulderTwist])
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	result['twistGrp'] = twistGrp
	result['twistJoints'] = twistJoints
	result['twistJointGrps'] = twistJointGrps
	result['twistDriveJoint'] = shoulderTwist
	result['twistConstraint'] = shoulderCon
	result['twistMultNodes'] = twistMultNode
	return result

def build_hip(	hip,
				pelvis,
				numJoints = 4,
				hipAim = 'x',
				hipFront = 'y',
				pelvisAim = 'x',
				pelvisFront = 'y',
				enableCtrl = False,
				prefix = ''	):
	'''
	Build hip twist using custom hipConstraint node
	@param hip: Hip or upper leg joint 
	@type hip: str
	@param pelvis: Pelvis joint 
	@type pelvis: str
	@param numJoint: Number of twist joints to generate 
	@type numJoint: int
	@param hipAim: Axis along the length of the hip/leg joint 
	@type hipAim: list or tuple
	@param hipFront: Forward facing axis of the hip/leg joint 
	@type hipFront: list or tuple
	@param pelvisAim: Axis along the length of the pelvis joint 
	@type pelvisAim: list or tuple
	@param pelvisFront: Forward facing axis of the pelvis joint 
	@type pelvisFront: list or tuple
	@param enableCtrl: Enable the twist child joint as a control 
	@type enableCtrl: bool
	@param prefix: Naming prefix for created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Define Axis Dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	if not mc.objExists(hip):
		raise Exception('Hip joint "'+hip+'" does not exist!')
	if not mc.objExists(pelvis):
		raise Exception('Pelvis joint "'+pelvis+'" does not exist!')
	
	if not axisDict.has_key(hipAim):
		raise Exception('Invalid hip aim axis value! ("'+hipAim+'")')
	if not axisDict.has_key(hipFront):
		raise Exception('Invalid hip front axis value! ("'+hipFront+'")')
	if not axisDict.has_key(pelvisAim):
		raise Exception('Invalid pelvis aim axis value! ("'+pelvisAim+'")')
	if not axisDict.has_key(pelvisFront):
		raise Exception('Invalid pelvis front axis value! ("'+pelvisFront+'")')
			
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(hip)
	
	# Check Plugin
	if not mc.pluginInfo('twistConstraint',q=True,l=True):
		try: mc.loadPlugin('twistConstraint')
		except: raise Exception('Unable to load plugin "twistConstraint"!')
	
	# ======================
	# - Configure Modifier -
	# ======================
	
	twistCtrlScale = 0.2
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	# =======================
	# - Create Twist Joints -
	# =======================
	
	twistJoints = createTwistJoints(	joint = hip,
										numTwistJoints = numJoints,
										offsetAxis = hipAim[-1],
										prefix = prefix	)
	# Reverse twist joint list
	twistJoints.reverse()
	
	# Create Twist Driver Joint
	mc.select(cl=True)
	hipTwist = mc.joint(n=prefix+'_twistDrive_jnt')
	hipTwistGrp = glTools.utils.joint.group(hipTwist)
	mc.delete(mc.parentConstraint(hip,hipTwistGrp))
	mc.parent(hipTwistGrp,hip)
	glTools.utils.base.displayOverride(hipTwist,overrideEnable=1,overrideDisplay=2,overrideLOD=0)
	
	# Create Hip Twist Joints
	twistJointGrps = []
	twistFactor = 1.0/(len(twistJoints)-1)
	jntLen = glTools.utils.joint.length(hip)
	for i in range(len(twistJoints)):
		
		# Add Twist Control Attribute
		mc.addAttr(twistJoints[i],ln='twist',min=-1.0,max=1.0,dv=twistFactor*i)
		
		# Add Twist Joint Group
		twistJointGrp = glTools.utils.joint.group(twistJoints[i],indexStr='Twist')
		twistJointGrps.append(twistJointGrp)
		
		# Tag Bind Joint
		glTools.rig.utils.tagBindJoint(twistJoints[i],True)
		
		# Create Joint Control
		if enableCtrl:
			glTools.rig.utils.tagCtrl(twistJoints[i],'tertiary')
			ctrlBuilder.controlShape(transform=twistJoints[i],controlType='sphere',controlScale=twistCtrlScale)
		
		# Set Display Override
		if enableCtrl:
			glTools.utils.base.displayOverride(twistJoints[i],overrideEnable=1,overrideDisplay=0,overrideLOD=1)
		else:
			glTools.utils.base.displayOverride(twistJoints[i],overrideEnable=1,overrideDisplay=2,overrideLOD=0)
	
	# Create Twist Group
	twistGrp = mc.joint(n=prefix+'_twistJoint_grp')
	glTools.utils.base.displayOverride(twistGrp,overrideEnable=1,overrideLOD=1)
	glTools.utils.transform.match(twistGrp,hip)
	mc.setAttr(twistGrp+'.segmentScaleCompensate',0)
	mc.setAttr(twistGrp+'.drawStyle',2) # None
	mc.setAttr(twistGrp+'.radius',0)
	mc.parent(twistGrp,hip)
	mc.parent(twistJointGrps,twistGrp)
	
	# Connect Inverse Scale
	for twistJointGrp in twistJointGrps:
		mc.connectAttr(hip+'.scale',twistJointGrp+'.inverseScale',f=True)
	
	# ==========================
	# - Create Hip Twist Setup -
	# ==========================
	
	# Create hipConstraint node
	hipCon = mc.createNode('hipConstraint',n=prefix+'_hipConstraint')
	
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
		mc.connectAttr(twistMult+'.output',twistJointGrps[i]+'.r'+hipAim[-1],f=True)
		twistMultNode.append(twistMult)
	
	# Reverse twist joint list
	twistJoints.reverse()
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[twistGrp])
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=twistJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=twistJointGrps)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[hipTwistGrp])
	chStateUtil.setFlags([2,2,2,1,1,1,2,2,2,1],objectList=[hipTwist])
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	result['twistGrp'] = twistGrp
	result['twistJoints'] = twistJoints
	result['twistJointGrps'] = twistJointGrps
	result['twistDriveJoint'] = hipTwist
	result['twistConstraint'] = hipCon
	result['twistMultNodes'] = twistMultNode
	return result
