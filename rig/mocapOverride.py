import maya.cmds as mc
import maya.mel as mm

import glTools.rig.utils

import glTools.tools.constraint

import glTools.utils.attribute
import glTools.utils.base
import glTools.utils.channelState
import glTools.utils.constraint
import glTools.utils.joint
import glTools.utils.stringUtils

import os.path
import types

def overrideAttribute():
	'''
	Return the control override toggle attribute name.
	'''
	return 'enableMocapOverride'

def overrideOffsetAttribute():
	'''
	Return the control override offset attribute name.
	'''
	return 'mocapOverrideOffset'

def buildOverrideTransform(transform,prefix=None):
	'''
	Build a mocap override transform from the specified input transform
	@param transform: Control transform to create override transforms from
	@type transform: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(transform):
		raise Exception('Rig control transform "'+transform+'" does not exist!')
	
	if not prefix:
		prefix = glTools.utils.stringUtils.stripSuffix(transform)
	
	# =============================
	# - Create Override Transform -
	# =============================
	
	# Duplicate Transform
	overrideTransform = mc.duplicate(transform,po=True,n=prefix+'_grp')[0]
	
	# Set Display Mode
	glTools.utils.base.displayOverride(overrideTransform,overrideEnable=1,overrideLOD=1)
	if glTools.utils.joint.isJoint(overrideTransform):
		mc.setAttr(overrideTransform+'.drawStyle',2) # None
	
	# Delete Unused Attributes
	glTools.utils.attribute.deleteUserAttrs(overrideTransform)
	
	# =================
	# - Return Result -
	# =================
	
	return overrideTransform

def getOverrideConstraint(control):
	'''
	Return the mocap override constraint(s) for the specified control.
	@param control: The control to get the mocap override constraint for.
	@type control: list
	'''
	# Check Control
	if not mc.objExists(control):
		raise Exception('Rig control transform "'+control+'" does not exist!')
	
	# Override Enable Attribute
	overrideAttr = overrideAttribute()
	if not mc.objExists(control+'.'+overrideAttr):
		raise Exception('OverrideEnable attribute "'+control+'.'+overrideAttr+'" does not exist!')
	
	# Override Constraint
	overrideConstraint = mc.listConnections(control+'.'+overrideAttr,s=False,d=True)
	if not overrideConstraint:
		raise Exception('Override constraint could not be determined from overrideEnabled attribute "'+control+'.'+overrideAttr+'"!')
	overrideConstraint = mc.ls(overrideConstraint,type='constraint')
	if not overrideConstraint:
		raise Exception('Override constraint could not be determined from overrideEnabled attribute "'+control+'.'+overrideAttr+'"!')
	
	# Return Result
	return list(set(overrideConstraint))

def getOverrideTarget(control):
	'''
	Return the mocap override target for the specified control.
	@param control: The control to get the mocap override constraint for.
	@type control: list
	'''
	# Get Override Constraint
	overrideConstraint = getOverrideConstraint(control)
	
	# Get Override Target
	overrideTarget = glTools.utils.constraint.targetList(overrideConstraint[0])
	if not overrideTarget:
		raise Exception('Unable to determine override target transform from constraint "'+overrideConstraint[0]+'"!')
	
	# Return Result
	return overrideTarget[0]

def getOverrideTargetNew(control):
	'''
	Return the mocap override target for the specified control.
	@param control: The control to get the mocap override constraint for.
	@type control: list
	'''
	# Get Override Target
	overrideTargetAttr = 'mocapOverrideTarget'
	if not mc.attributeQuery(overrideTargetAttr,n=control,ex=True):
		raise Exception('Unable to determine override target transform! Attribute "'+control+'.'+overrideTargetAttr+'" does not exist.')
	overrideTarget = mc.listConnections(control+'.'+overrideTargetAttr,s=True,d=False)
	if not overrideTarget:
		raise Exception('Unable to determine override target transform! Attribute "'+control+'.'+overrideTargetAttr+'" has no incoming connections.')
	
	# Return Result
	return overrideTarget[0]

def createControlOverride(transform,prefix=None):
	'''
	Create mocap anim override transforms for the specified control transform.
	@param transform: Control transform to create mocap override transforms for
	@type transform: str
	@param prefix: Name prefix for override nodes created by function. If empty, prefix is taken from the input transform name.
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(transform):
		raise Exception('Rig control transform "'+transform+'" does not exist!')
	
	if not prefix:
		prefix = glTools.utils.stringUtils.stripSuffix(transform)
	
	# ======================================
	# - Create Control Override Transforms -
	# ======================================
	
	overrideTarget = buildOverrideTransform(transform,prefix=prefix+'_overrideTarget')
	overrideTransform = buildOverrideTransform(transform,prefix=prefix+'_overrideTransform')
	
	# Set Channel States
	channelState = glTools.utils.channelState.ChannelState()
	channelState.setFlags([0,0,0,0,0,0,2,2,2,1],objectList=[overrideTarget])
	channelState.setFlags([1,1,1,1,1,1,2,2,2,1],objectList=[overrideTransform])
	channelState.set(1,[overrideTarget,overrideTransform])
	
	# Parent Control to Override Transform
	mc.parent(transform,overrideTransform)
	
	# ======================================
	# - Create Control Override Constraint -
	# ======================================
	
	# Create ParentConstraint
	overrideConstraint = mc.parentConstraint(overrideTarget,overrideTransform,n=prefix+'_overrideTransform_parentConstraint')[0]
	overrideAlias = mc.parentConstraint(overrideConstraint,q=True,wal=True)
	
	# Reset Rest Values
	mc.setAttr(overrideConstraint+'.restTranslate',0,0,0)
	mc.setAttr(overrideConstraint+'.restRotate',0,0,0)
	
	# ==========================
	# - Create Override Toggle -
	# ==========================
	
	# Create Toggle Attribute
	overrideAttr = overrideAttribute()
	if mc.objExists(transform+'.'+overrideAttr):
		mc.deleteAttr(transform+'.'+overrideAttr)
	mc.addAttr(transform,ln=overrideAttr,at='bool')
	mc.setAttr(transform+'.'+overrideAttr,False)
	
	# Connect Toggle Attribute
	mc.connectAttr(transform+'.'+overrideAttr,overrideConstraint+'.'+overrideAlias[0],f=True)
	
	# ==========================
	# - Create Override Offset -
	# ==========================
	
	offsetAttr = overrideOffsetAttribute()
	if mc.objExists(transform+'.'+offsetAttr):
		mc.deleteAttr(transform+'.'+offsetAttr)
	
	mc.addAttr(transform,ln=offsetAttr,at='double3')
	mc.addAttr(transform,ln=offsetAttr+'X',at='double',p=offsetAttr,dv=0)
	mc.addAttr(transform,ln=offsetAttr+'Y',at='double',p=offsetAttr,dv=0)
	mc.addAttr(transform,ln=offsetAttr+'Z',at='double',p=offsetAttr,dv=0)
	
	# Connect Offset
	mc.connectAttr(transform+'.'+offsetAttr,overrideConstraint+'.target[0].targetOffsetTranslate',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	result['overrideTarget'] = overrideTarget
	result['overrideTransform'] = overrideTransform
	result['overrideConstraint'] = overrideConstraint
	return result

def createControlOverrideNew(transform,prefix=''):
	'''
	Create mocap anim override transforms for the specified control transform.
	@param transform: Control transform to create mocap override transforms for
	@type transform: str
	@param prefix: Name prefix for override nodes created by function. If empty, prefix is taken from the input transform name.
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(transform):
		raise Exception('Rig control transform "'+transform+'" does not exist!')
	
	if not prefix:
		prefix = glTools.utils.stringUtils.stripSuffix(transform)
	
	# ======================================
	# - Create Control Override Transforms -
	# ======================================
	
	overrideTarget = buildOverrideTransform(transform,prefix=prefix+'_overrideTarget')
	overrideTransform = buildOverrideTransform(transform,prefix=prefix+'_overrideTransform')
	
	# Parent Control to Override Transform
	mc.parent(transform,overrideTransform)
	
	# ==========================
	# - Create Override Toggle -
	# ==========================
	
	# Create Toggle Attribute
	overrideAttr = overrideAttribute()
	if mc.objExists(transform+'.'+overrideAttr):
		mc.deleteAttr(transform+'.'+overrideAttr)
	mc.addAttr(transform,ln=overrideAttr,at='enum',en='Off:On')
	mc.setAttr(transform+'.'+overrideAttr,k=False,cb=True)
	mc.setAttr(transform+'.'+overrideAttr,False)
	
	# Mocap Override Message Connection
	overrideTargetAttr = 'mocapOverrideTarget'
	if mc.objExists(transform+'.'+overrideTargetAttr):
		mc.deleteAttr(transform+'.'+overrideTargetAttr)
	mc.addAttr(transform,ln=overrideTargetAttr,at='message')
	mc.connectAttr(overrideTarget+'.message',transform+'.'+overrideTargetAttr,f=True)
	
	# ===================================
	# - Create Control Override Network -
	# ===================================
	
	# Create Override Conditions
	overrideTranslate = mc.createNode('condition',n=prefix+'_overrideTranslate_condition')
	overrideRotate = mc.createNode('condition',n=prefix+'_overrideRotate_condition')
	
	# Override Translate
	baseTranslate = mc.getAttr(overrideTransform+'.t')[0]
	mc.setAttr(overrideTranslate+'.colorIfFalse',*baseTranslate,l=True,cb=False)
	mc.connectAttr(overrideTarget+'.t',overrideTranslate+'.colorIfTrue',f=True)
	mc.setAttr(overrideTranslate+'.colorIfTrue',l=True,cb=False)
	mc.setAttr(overrideTranslate+'.operation',0,l=True,cb=False) # Equal
	mc.setAttr(overrideTranslate+'.secondTerm',1,l=True,cb=False)
	mc.connectAttr(transform+'.'+overrideAttr,overrideTranslate+'.firstTerm',f=True)
	mc.setAttr(overrideTranslate+'.firstTerm',l=True,cb=False)
	
	# Override Rotate
	baseRotate = mc.getAttr(overrideTransform+'.r')[0]
	mc.setAttr(overrideRotate+'.colorIfFalse',*baseRotate,l=True,cb=False)
	mc.connectAttr(overrideTarget+'.t',overrideRotate+'.colorIfTrue',f=True)
	mc.setAttr(overrideRotate+'.colorIfTrue',l=True,cb=False)
	mc.setAttr(overrideRotate+'.secondTerm',1,l=True,cb=False)
	mc.setAttr(overrideRotate+'.operation',0,l=True,cb=False) # Equal
	mc.connectAttr(transform+'.'+overrideAttr,overrideRotate+'.firstTerm',f=True)
	mc.setAttr(overrideRotate+'.firstTerm',l=True,cb=False)
	
	# ==================
	# - Channel States -
	# ==================
	
	chanState = glTools.utils.channelState.ChannelState()
	chanState.setFlags([0,0,0,0,0,0,2,2,2,1],objectList=[overrideTarget])
	chanState.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[overrideTransform])
	#chanState.set(1,[overrideTarget,overrideTransform])
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	result['overrideTarget'] = overrideTarget
	result['overrideTransform'] = overrideTransform
	result['overrideTranslate'] = overrideTranslate
	result['overrideRotate'] = overrideRotate
	
	return result

def constrainControlOverrideTarget(	control,
									constraintTarget,
									constraintType	= 'parent',
									maintainOffset	= False,
									skipTranslate	= [],
									skipRotate		= [],
									interpType		= None,
									prefix			= '' ):
	'''
	Constrain the override target transform of the specified control to a given target transform.
	This function can be used to constrain rig controls to a mocap driven skeleton.
	@param control: The control that will have its override target transform constrainted to the specified target transform.
	@type control: str
	@param constraintTarget: The target transform that the override target transform will be constrainted to.
	@type constraintTarget: str
	@param constraintType: The constraint type to apply to the override target transform.
	@type constraintType: str
	@param maintainOffset: Initialize the constraint offset necessary for the slave transform to mainatain its current position and orientation.
	@type maintainOffset: bool
	@param skipTranslate: List the translate channels to leave unaffected by the constraint.
	@type skipTranslate: list
	@param skipRotate: List the rotate channels to leave unaffected by the constraint.
	@type skipRotate: list
	@param interpType: Orientation interpolation type. "average", "shortest", "longest"
	@type interpType: str or None
	@param prefix: Name prefix for override nodes created by the function. If empty, prefix is taken from the input control name.
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Control
	if not mc.objExists(control):
		raise Exception('Rig control transform "'+control+'" does not exist!')
	
	# Constraint Target
	if isinstance(constraintTarget,types.StringTypes):
		if not mc.objExists(constraintTarget):
			raise Exception('Override transform target "'+constraintTarget+'" does not exist!')
	elif isinstance(constraintTarget,types.ListType):
		for target in constraintTarget:
			if not mc.objExists(target):
				raise Exception('Override transform target "'+target+'" does not exist!')
	else:
		raise Exception('Invalid argument type for constraintTarget!')
	
	# Constraint Type
	if not constraintType in ['point','orient','parent']:
		raise Exception('Unsupported constraint type "'+constraintType+'"!')
	
	# Override Enable Attribute
	overrideAttr = overrideAttribute()
	if not mc.objExists(control+'.'+overrideAttr):
		raise Exception('OverrideEnable attribute "'+control+'.'+overrideAttr+'" does not exist!')
		
	# Override Constraint
	overrideConstraint = mc.listConnections(control+'.'+overrideAttr,s=False,d=True)
	if not overrideConstraint:
		raise Exception('Override constraint could not be determined from overrideEnabled attribute "'+control+'.'+overrideAttr+'"!')
	overrideConstraint = mc.ls(overrideConstraint,type='constraint')
	if not overrideConstraint:
		raise Exception('Override constraint could not be determined from overrideEnabled attribute "'+control+'.'+overrideAttr+'"!')
	
	# Override Target
	overrideTarget = glTools.utils.constraint.targetList(overrideConstraint[0])
	if not overrideTarget:
		raise Exception('Unable to determine override target transform from constraint "'+overrideConstraint[0]+'"!')
	
	# InterpType
	interpIndex = {'average':1,'shortest':2,'longest':3}
	if constraintType == 'parent' or constraintType == 'orient':
		if interpType and not interpType in interpIndex.keys():
				raise Exception('Invalid interpolation type "'+interpType+'"!')
	
	# Prefix
	if not prefix:
		prefix = glTools.utils.stringUtils.stripSuffix(control)
	
	# =====================================
	# - Create Override Target Constraint -
	# =====================================
	
	overrideTargetConstraint = ''
	
	# Create pointConstraint
	if constraintType == 'point':
		overrideTargetConstraint = mc.pointConstraint(	constraintTarget,
														overrideTarget[0],
														mo = maintainOffset,
														sk = skipTranslate,
														n = prefix+'_overrideTarget_pointConstraint' )[0]
	
	# Create orientConstraint
	elif constraintType == 'orient':
		overrideTargetConstraint = mc.orientConstraint(	constraintTarget,
														overrideTarget[0],
														mo = maintainOffset,
														sk = skipRotate,
														n = prefix+'_overrideTarget_orientConstraint' )[0]
		# Interp Type
		if interpType: mc.setAttr(overrideTargetConstraint+'.interpType',interpIndex[interpType])
	
	# Create parentConstraint
	elif constraintType == 'parent':
		overrideTargetConstraint = mc.parentConstraint(	constraintTarget,
														overrideTarget[0],
														mo = maintainOffset,
														st = skipTranslate,
														sr = skipRotate,
														n = prefix+'_overrideTarget_parentConstraint' )[0]
		# Interp Type
		if interpType: mc.setAttr(overrideTargetConstraint+'.interpType',interpIndex[interpType])
	
	# Unsupported Constraint Type
	else:
		raise Exception('Unsupported constraint type "'+constraintType+'"!')
	
	# Enable overrideConstraint
	mc.setAttr(control+'.'+overrideAttr,True)
	
	# =================
	# - Return Result -
	# =================
	
	return overrideTargetConstraint

def constrainControlToTarget(	control,
								constraintTarget,
								constraintType	= 'parent',
								maintainOffset	= False,
								skipTranslate	= [],
								skipRotate		= [],
								interpType		= None,
								prefix			= '' ):
	'''
	Constrain the the specified control to a given target transform.
	This function can be used to constrain rig controls to a mocap driven skeleton.
	@param control: The control that will be constrainted to the specified target transform.
	@type control: str
	@param constraintTarget: The target transform that the control transform will be constrainted to.
	@type constraintTarget: str
	@param constraintType: The constraint type to apply to the control transform.
	@type constraintType: str
	@param maintainOffset: Initialize the constraint offset necessary for the slave transform to mainatain its current position and orientation.
	@type maintainOffset: bool
	@param skipTranslate: List the translate channels to leave unaffected by the constraint.
	@type skipTranslate: list
	@param skipRotate: List the rotate channels to leave unaffected by the constraint.
	@type skipRotate: list
	@param interpType: Orientation interpolation type. "average", "shortest", "longest"
	@type interpType: str or None
	@param prefix: Name prefix for override nodes created by the function. If empty, prefix is taken from the input control name.
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Control
	if not mc.objExists(control):
		raise Exception('Rig control transform "'+control+'" does not exist!')
	
	# Constraint Target
	if isinstance(constraintTarget,types.StringTypes):
		if not mc.objExists(constraintTarget):
			raise Exception('Override transform target "'+constraintTarget+'" does not exist!')
	elif isinstance(constraintTarget,types.ListType):
		for target in constraintTarget:
			if not mc.objExists(target):
				raise Exception('Override transform target "'+target+'" does not exist!')
	
	# Constraint Type
	if not constraintType in ['point','orient','parent']:
		raise Exception('Unsupported constraint type "'+constraintType+'"!')
	
	# InterpType
	interpIndex = {'average':1,'shortest':2,'longest':3}
	if constraintType == 'parent' or constraintType == 'orient':
		if interpType and not interpType in interpIndex.keys():
				raise Exception('Invalid interpolation type "'+interpType+'"!')
	
	# Prefix
	if not prefix:
		prefix = glTools.utils.stringUtils.stripSuffix(control)
	
	# =====================================
	# - Create Override Target Constraint -
	# =====================================
	
	overrideCtrlConstraint = None
	
	# Create pointConstraint
	if constraintType == 'point':
		try:
			overrideCtrlConstraint = mc.pointConstraint(	constraintTarget,
															control,
															mo = maintainOffset,
															sk = skipTranslate,
															n = prefix+'_overrideCtrl_pointConstraint' )[0]
		except Exception, e:
			raise Exception('Error creating point constraint for control "'+control+'"! '+str(e))
	
	# Create orientConstraint
	elif constraintType == 'orient':
		try:
			overrideCtrlConstraint = mc.orientConstraint(	constraintTarget,
															control,
															mo = maintainOffset,
															sk = skipRotate,
															n = prefix+'_overrideCtrl_orientConstraint' )[0]
		except Exception, e:
			raise Exception('Error creating orient constraint for control "'+control+'"! '+str(e))
		
		# Interp Type
		if interpType: mc.setAttr(overrideCtrlConstraint+'.interpType',interpIndex[interpType])
	
	# Create parentConstraint
	elif constraintType == 'parent':
		try:
			attrList	= ['tx','ty','tz','rx','ry','rz']
			if skipTranslate: [attrList.remove('t'+i) for i in skipTranslate if 't'+i in attrList]
			if skipRotate: [attrList.remove('r'+i) for i in skipRotate if 'r'+i in attrList]
			overrideCtrlConstraint = glTools.tools.constraint.parentConstraint(	master		= constraintTarget,
																				slave		= control,
																				mo			= maintainOffset,
																				attrList	= attrList )
		except Exception, e:
			raise Exception('Error creating parent constraint for control "'+control+'"! '+str(e))
		
		# Interp Type
		if interpType: mc.setAttr(overrideCtrlConstraint+'.interpType',interpIndex[interpType])
	
	# =================
	# - Return Result -
	# =================
	
	return overrideCtrlConstraint

def bakeControlOverrideTarget(controlList,start=None,end=None,bakeSim=True):
	'''
	Bake control override target constraint to transform channel keys.
	@param controlList: The control list that will have its override target transform constraints baked to keyframes.
	@type controlList: list
	@param start: Start frame of the bake animation range. If greater that end, use current playback settings.
	@type start: float
	@param end: End frame of the bake animation range. If less that start, use current playback settings.
	@type end: float
	@param bakeSim: Bake results using simulation option which updates the entire scene at each bake sample.
	@type bakeSim: bool
	'''
	print('!!==== DEPRICATED ====!! (glTools.rig.mocapOverride.bakeControlOverrideTarget)')
	
	# ==========
	# - Checks -
	# ==========
	
	# Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	# For Each Control
	overrideTargetList = []
	overrideConstraintList = []
	for control in controlList:
		
		# Control
		if not mc.objExists(control):
			raise Exception('Rig control transform "'+control+'" does not exist!')
		
		# Override Enable Attribute
		overrideAttr = overrideAttribute()
		if not mc.objExists(control+'.'+overrideAttr):
			raise Exception('OverrideEnable attribute "'+control+'.'+overrideAttr+'" does not exist!')
		
		# Override Constraint
		overrideConstraint = mc.listConnections(control+'.'+overrideAttr,s=False,d=True)
		if not overrideConstraint:
			raise Exception('Override constraint could not be determined from overrideEnabled attribute "'+control+'.'+overrideAttr+'"!')
		overrideConstraint = mc.ls(overrideConstraint,type='constraint')
		if not overrideConstraint:
			raise Exception('Override constraint could not be determined from overrideEnabled attribute "'+control+'.'+overrideAttr+'"!')
		
		# Override Target
		overrideTarget = glTools.utils.constraint.targetList(overrideConstraint[0])
		if not overrideTarget:
			raise Exception('Unable to determine override target transform from constraint "'+overrideConstraint[0]+'"!')
		
		# Override Target Constraint
		overrideTargetConstraint = mc.ls(mc.listConnections(overrideTarget[0],s=True,d=False),type='constraint')
		if not overrideTargetConstraint:
			
			# Check PairBlend (intermediate) Connection
			# - This fix was made in preparation for baking keys from multiple mocap sources (bake in frame chunks).
			overrideTargetPairBlend = mc.ls(mc.listConnections(overrideTarget[0],s=True,d=False),type='pairBlend')
			if overrideTargetPairBlend:
				overrideTargetConstraint = mc.ls(mc.listConnections(overrideTargetPairBlend,s=True,d=False),type='constraint')
			
			if not overrideTargetConstraint:
				print('Unable to determine override target constraint from override target transform "'+overrideTarget[0]+'"!')
				continue
		
		# Append to Override Target List
		overrideTargetList.append(overrideTarget[0])
		# Append to Override Constraint List
		[overrideConstraintList.append(i) for i in overrideTargetConstraint if not i in overrideConstraintList]
	
	# =================================
	# - Bake Override Target Channels -
	# =================================
	
	mc.bakeResults(	overrideTargetList,
					t = (start,end),
					at = ['tx','ty','tz','rx','ry','rz'],
					preserveOutsideKeys = True,
					simulation = bakeSim )
	
	# ======================
	# - Delete Constraints -
	# ======================
	
	mc.delete(overrideConstraintList)

def bakeControlOverride(controlList,start=None,end=None,bakeSim=True):
	'''
	Bake control constraint to transform channel keys.
	@param controlList: The control list that will have its constraints baked to keyframes.
	@type controlList: list
	@param start: Start frame of the bake animation range. If greater that end, use current playback settings.
	@type start: float
	@param end: End frame of the bake animation range. If less that start, use current playback settings.
	@type end: float
	@param bakeSim: Bake results using simulation option which updates the entire scene at each bake sample.
	@type bakeSim: bool
	'''
	print('!!==== DEPRICATED ====!! (glTools.rig.mocapOverride.bakeControlOverride)')
	
	# ==========
	# - Checks -
	# ==========
	
	# Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	# For Each Control
	bakeControlList = []
	constraintList = []
	for control in controlList:
		
		# Control
		if not mc.objExists(control):
			raise Exception('Rig control transform "'+control+'" does not exist!')
		
		# Override Target Constraint
		overrideConstraint = mc.ls(mc.listConnections(control+'.'+overrideAttribute(),d=True,s=False),type='constraint')
		if not overrideConstraint:
			
			# Check PairBlend (intermediate) Connection
			# - This fix was made in preparation for baking keys from multiple mocap sources (bake in frame chunks).
			overridePairBlend = mc.ls(mc.listConnections(control,s=True,d=False),type='pairBlend')
			if overridePairBlend:
				overrideConstraint = mc.ls(mc.listConnections(overrideTargetPairBlend,s=True,d=False) or [],type='constraint')
			
			if not overrideConstraint:
				print('Unable to determine override constraint from control transform "'+control+'"!')
				continue
		
		# Append to Override Target List
		bakeControlList.append(control)
		# Append to Override Constraint List
		[constraintList.append(i) for i in overrideConstraint if not i in constraintList]
	
	# =================================
	# - Bake Override Target Channels -
	# =================================
	
	# Check Bake Control List
	if not bakeControlList:
		print('Found no controls to bake! Skipping...')
		return None
	
	# Bake to Controls
	mc.bakeResults(	bakeControlList,
					t = (start,end),
					at = ['tx','ty','tz','rx','ry','rz'],
					preserveOutsideKeys = True,
					simulation = bakeSim )
	
	# ======================
	# - Delete Constraints -
	# ======================
	
	if constraintList: mc.delete(constraintList)
	
	# =================
	# - Return Result -
	# =================
	
	return bakeControlList

def bakeExportSkeleton(exportNS,start=1,end=0):
	'''
	Bake export skeleton constraints to joint channel keysframes.
	@param exportNS: The namespace of the export skeleton.
	@type exportNS: str
	@param start: Start frame of the bake animation range. If greater that end, use current playback settings.
	@type start: float
	@param end: End frame of the bake animation range. If less that start, use current playback settings.
	@type end: float
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Start/End
	if start > end:
		start = mc.playbackOptions(q=True,min=True)
		end = mc.playbackOptions(q=True,max=True)
	
	# Namespace
	if not exportNS:
		raise Exception('An export namespace must be specified')
	
	exportNS = exportNS+':'
	if not mc.namespace(exists=':'+exportNS):
		raise Exception('Export namespace "'+exportNS+'" does not exist!')
	
	# ======================
	# - Bake Export Joints -
	# ======================
	
	jointList = mc.ls(exportNS+'*',type='joint')
	bakeList = [i for i in jointList if mc.ls(mc.listConnections(i,s=True,d=False),type='constraint')]
	mc.bakeResults(bakeList,t=(start,end),at=['tx','ty','tz','rx','ry','rz','sx','sy','sz'],simulation=True)
	
	# ======================
	# - Delete Constraints -
	# ======================
	
	constraintList = mc.ls(exportNS+'*',type='constraint')
	if not constraintList:
		raise Exception('Unbale to determine export skeleton constraint list!')
	mc.delete(constraintList)
	
	# =================
	# - Return Result -
	# =================
	
	return bakeList

def fbxExportSkeleton(exportNS,exportPath,force=False):
	'''
	Export an animated skeleton as FBX (v2009) to the specified file path.
	@param exportNS: Namespace of the skeleton to be exported.
	@type exportNS: str
	@param exportPath: The destination file path.
	@type exportPath: str
	@param force: Force save if file already exists. (Overwrite).
	@type force: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Namespace
	if not exportNS:
		raise Exception('An export namespace must be specified')
	exportNS = exportNS+':'
	if not mc.namespace(exists=':'+exportNS):
		raise Exception('Export namespace "'+exportNS+'" does not exist!')
	
	# Check Directory Path
	exportDir = os.path.dirname(exportPath)
	if not os.path.isdir(exportDir):
		if force:
			os.makedirs(exportDir)
		else:
			raise Exception('Export directory "'+exportDir+'" does not exist! Use "force=True" to automatically create the required directory structure.')
	
	# Check File Extension
	if not os.path.splitext(exportPath)[-1].lower() == '.fbx':
		exportPath += '.fbx'
	
	# Check File Path
	if os.path.isfile(exportPath) and not force:
		raise Exception('File "'+exportPath+'" already exista! Use "force=True" to overwrite the existing file.')
	
	# ==========
	# - Export -
	# ==========
	
	# Define export selection
	exportList = mc.ls(exportNS+'*',type='joint')
	if not exportList:
		raise Exception('Export namespace "'+exportNS+'" is empty!')
	mc.select(exportList)
	
	# Set FBX export options
	mm.eval('FBXExportFileVersion "FBX200900"')
	mm.eval('FBXExportInAscii -v 1')
	mm.eval('FBXExportSkins -v 1')
	mm.eval('FBXExportDxfDeformation -v 1')
	mm.eval('FBXExportSmoothMesh -v 1')
	mm.eval('FBXExportCameras -v 0')
	mm.eval('FBXExportLights -v 0')
	mm.eval('FBXExportAnimationOnly -v 0')
	
	# Set Scale Conversion
	#mm.eval('FBXExportConvertUnitString "m"')
	
	# Export Selected Nodes to FBX file
	mm.eval('FBXExport -f "'+exportPath+'" -s;')
	
	# Clear Selection
	mc.select(cl=True)
	
	# =================
	# - Return Result -
	# =================
	
	return exportPath
