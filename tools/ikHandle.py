import maya.cmds as mc

import glTools.utils.base
import glTools.utils.lib
import glTools.utils.mathUtils
import glTools.utils.stringUtils

def build(	startJoint,
			endJoint,
			solver='ikSCsolver',
			curve='',
			ikSplineOffset=0.0,
			priority=1,
			sticky=False,
			prefix=''	):
	'''
	Build an IK handle based on the input argument values
	@param startJoint: Start joint for the IK handle
	@type startJoint: str
	@param endJoint: End joint for the IK handle
	@type endJoint: str
	@param solver: IK Solver to use. "ikSplineSolver", "ikSCsolver", "ikRPsolver" or "ik2Bsolver"
	@type solver: str
	@param curve: Input curve for splineIK
	@type curve: str
	@param ikSplineOffset: Offset value for ikSplineSolver
	@type ikSplineOffset: float
	@param priority: IK handle priority
	@type priority: int
	@param sticky: IK handle sticky value.
	@type sticky: bool
	@param prefix: Name prefix for all builder created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check joints
	if not mc.objExists(startJoint): raise Exception('Joint '+startJoint+' does not exist!!')
	if not mc.objExists(endJoint): raise Exception('Joint '+endJoint+' does not exist!!')
	
	# Check solver type
	ikType = ['ikSplineSolver','ikSCsolver','ikRPsolver','ik2Bsolver']
	if not ikType.count(solver):
		raise Exception('Invalid ikSlover type specified ("'+solver+ '")!!')
	
	# Check curve
	createCurve = False
	if solver == ikType[0]: # solver = ikSplineSolver
		if not mc.objExists(curve):
			createCurve = True
	
	# Extract name prefix from joint name
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(startJoint)
	
	mc.select(cl=True)
	
	# ===================
	# - Create ikHandle -
	# ===================
	
	ik = []
	if solver == ikType[0]:
		
		# Spline IK solver
		ik = mc.ikHandle(	sj=startJoint,
							ee=endJoint,
							sol=solver,
							curve=curve,
							ccv=createCurve,
							pcv=False,
							priority=priority	)
	else:
		
		# Chain IK solver
		if sticky:
			ik = mc.ikHandle(	sj=startJoint,
								ee=endJoint,
								sol=solver,
								priority=priority,
								sticky='sticky'	)
		else:
			ik = mc.ikHandle(	sj=startJoint,
								ee=endJoint,
								sol=solver,
								priority=priority	)
	
	# Clear selection (to avoid printed warning message)
	mc.select(cl=True)
	
	# Rename ikHandle and endEffector
	ikHandle = str(mc.rename(ik[0],prefix+'_ikHandle'))
	ikEffector = str(mc.rename(ik[1],prefix+'_ikEffector'))
	
	# Set ikHandle offset value
	mc.setAttr(ikHandle+'.offset',ikSplineOffset)
	
	# =================
	# - Return Result -
	# =================
	
	return ikHandle

def advancedTwistSetup(	ikHandle,
						worldUpType=0,
						upAxis='y',
						upVectorBase='y',
						upVectorTip='y',
						upObjectBase='',
						upObjectTip='',
						twistType='total',
						twistStart=0,
						twistEnd=0,
						twistRamp='',
						twistMult=90	):
	'''
	Setup IK Spline Advnced Twist
	@param ikHandle: IK spline handle to setup advanced twist for 
	@type ikHandle: str
	@param worldUpType: World Up Type. 0=SceneUp, 1=ObjectUp, 2=ObjectUp(Start/End), 3=ObjectRotationUp, 4=ObjectRotationUp(Start/End), 5=Vector, 6=Vector(Start/End), 7=Relative.
	@type worldUpType: int
	@param upAxis: Joint axis to aim towards the current upVector 
	@type upAxis: str
	@param upVectorBase: Spline IK base (start) upVector
	@type upVectorBase: str
	@param upVectorTip: Spline IK tip (end) upVector
	@type upVectorTip: str
	@param upObjectBase: Spline IK base (start) upVector object
	@type upObjectBase: str
	@param upObjectTip: Spline IK tip (end) upVector object
	@type upObjectTip: str
	@param twistType: IK twist value type. Accepted values are - "total", "start/end" and "ramp"
	@type twistType: str
	@param twistStart: IK twist start value. Only used if twistValueType = "start/end"
	@type twistStart: float
	@param twistEnd: IK twist end value. Only used if twistValueType = "start/end"
	@type twistEnd: float
	@param twistRamp: IK twist ramp. Only used if twistValueType = "ramp"
	@type twistRamp: str
	@param twistMult: IK twist ramp multiplier. Only used if twistValueType = "ramp"
	@type twistMult: float
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Ik Handle
	if not mc.objExists(ikHandle):
		raise Exception('IkHandle '+ikHandle+' does not exist!!')
	
	# World Up Objects
	if (worldUpType==1) or (worldUpType==2) or (worldUpType==3) or (worldUpType==4):
		if not upObjectBase:
			raise Exception('No base worldUp object specified!')
		if not mc.objExists(upObjectBase):
			raise Exception('Base worldUp object "'+upObjectBase+'" does not exist!')
	if (worldUpType==2) or (worldUpType==4):
		if not upObjectTip:
			raise Exception('No end worldUp object specified!')
		if not mc.objExists(upObjectBase):
			raise Exception('End worldUp object "'+upObjectTip+'" does not exist!')
	
	# Joint World Up Axis
	jntWorldUp = {'y':0,'-y':1,'*y':2,'z':3,'-z':4,'*z':5}
	if not jntWorldUp.has_key(upAxis):
		raise Exception('Invalid UpAxis value supplied ("'+upAxis+'")! Valid values are "y", "-y", "*y" (closest Y), "z", "-z" and "*z" (closest Z).')
	
	# World Up Axis
	worldUp = glTools.utils.lib.axis_dict()
	if not worldUp.has_key(upVectorBase):
		raise Exception('Invalid base (start) upVector value supplied ("'+upVectorBase+'")! Valid values are "x", "-x", "y", "-y", "z" and "-z".')
	if not worldUp.has_key(upVectorTip):
		raise Exception('Invalid tip (end) upVector value supplied ("'+upVectorTip+'")! Valid values are "x", "-x", "y", "-y", "z" and "-z".')
	
	# Twist Value Type
	twistTypeDict = {'total':0,'start/end':1,'ramp':2}
	if not twistTypeDict.has_key(twistType):
		raise Exception('Invalid twsit value type ("'+twistType+'")! Valid values are "total", "start/end" and "ramp".')
	
	# Twist Ramp
	if twistType=='ramp':
		if not twistRamp:
			raise Exception('No valid ramp provided for ramp twist type!')
		if not mc.objExists(twistRamp+'.outColor'):
			raise Exception('Ramp "'+twistRamp+'" has no ".outColor" attribute to drive the ikHandle ramp twist value!')
	
	# ===========================
	# - Setup Advanced IK Twist -
	# ===========================
	
	# Enable Advanced Twist
	mc.setAttr(ikHandle+'.dTwistControlEnable',1)
	
	# Set World Up Type
	mc.setAttr(ikHandle+'.dWorldUpType',worldUpType)
	
	# Set Joint World Up Axis
	mc.setAttr(ikHandle+'.dWorldUpAxis',jntWorldUp[upAxis])
	
	# World Up Objects
	mc.connectAttr(upObjectBase+'.worldMatrix[0]',ikHandle+'.dWorldUpMatrix',f=True)
	mc.connectAttr(upObjectTip+'.worldMatrix[0]',ikHandle+'.dWorldUpMatrixEnd',f=True)
	
	# World Up Axis'
	mc.setAttr(ikHandle+'.dWorldUpVector',*worldUp[upVectorBase])
	mc.setAttr(ikHandle+'.dWorldUpVectorEnd',*worldUp[upVectorTip])
	
	# Twist Value Type
	mc.setAttr(ikHandle+'.dTwistValueType',twistTypeDict[twistType])
	
	# Start/End Twist
	mc.setAttr(ikHandle+'.dTwistStart',twistStart)
	mc.setAttr(ikHandle+'.dTwistEnd',twistEnd)
	
	# Twist Ramp
	if twistType=='ramp':
		mc.connectAttr(twistRamp+'.outColor',ikHandle+'.dTwistRamp',f=True)
	
	# Twist Ramp Multiplier
	mc.setAttr(ikHandle+'.dTwistRampMult',twistMult)
