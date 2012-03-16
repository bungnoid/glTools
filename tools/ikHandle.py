import maya.cmds as mc

import glTools.utils.base
import glTools.utils.mathUtils
import glTools.utils.stringUtils

def build(startJoint,endJoint,solver='ikSCsolver',curve='',ikSplineOffset=0.0,prefix=''):
	'''
	INPUTS:
	@input startJoint: Start joint for the IK handle
	@inputType startJoint: str
	@input endJoint: End joint for the IK handle
	@inputType endJoint: str
	@input solver: IK Solver to use
	@inputType solver: str
	@input curve: Input curve for splineIK
	@inputType curve: str
	@input ikSplineOffset: Offset value for ikSplineSolver
	@inputType ikSplineOffset: float
	@input prefix: Name prefix for all builder created nodes
	@inputType prefix: str
	'''
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
	
	#-----------------
	# Create ikHandle
	ik = []
	if solver == ikType[0]:
		# Spline IK solver
		ik = mc.ikHandle(sj=startJoint,ee=endJoint,sol=solver,curve=curve,ccv=createCurve,pcv=False)
	else:
		# Chain IK solver
		ik = mc.ikHandle(sj=startJoint,ee=endJoint,sol=solver)
	
	# Clear selection (to avoid printed warning message)
	mc.select(cl=True)
	
	# Rename ikHandle and endEffector
	ikHandle = str(mc.rename(ik[0],prefix+'_ikHandle'))
	ikEffector = str(mc.rename(ik[1],prefix+'_ikEffector'))
	
	# Set ikHandle offset value
	mc.setAttr(ikHandle+'.offset',ikSplineOffset)
	
	# Return result
	return ikHandle
