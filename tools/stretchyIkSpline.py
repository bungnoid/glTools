import maya.cmds as mc
import maya.mel as mm

import glTools.utils.ik
import glTools.utils.stringUtils

def stretchyIkSpline(ikHandle,parametric=True,scaleAxis='x',scaleAttr='',blendControl='',blendAttr='stretchScale',minPercent=0.0,maxPercent=1.0,prefix=''):
	'''
	Build stretchy IK spline setup
	@param ikHandle: IK Handle to create stretchy setup for
	@type ikHandle: str
	@param parametric: Use parametric or arcLength scale
	@type parametric: bool
	@param scaleAxis: Axis along which the ik joints will be scaled
	@type scaleAxis: str
	@param scaleAttr: World scale attribute
	@type scaleAttr: str
	@param blendControl: Control object that will contain the attribute to control the stretchy IK blending. If left at default (""), blending will not be enabled.
	@type blendControl: str
	@param blendAttr: The name of the attribute on blendControl that will control the stretchy IK blending.
	@type blendAttr: str
	@param minPercent: The minimum u paramerter percentage to calculate the stretch from. Parametric only.
	@type minPercent: float
	@param maxPercent: The maximum u paramerter percentage to calculate the stretch to. Parametric only.
	@type maxPercent: float
	@param prefix: Name prefix for builder created nodes
	@type prefix: str
	'''
	# Build stretchy IK
	if parametric:
		result = stretchyIkSpline_parametric(ikHandle,scaleAxis,scaleAttr,blendControl,blendAttr,minPercent,maxPercent,prefix)
	else:
		result = stretchyIkSpline_arcLength(ikHandle,scaleAxis,scaleAttr,blendControl,blendAttr,prefix)
	
	# Return Result
	return result

def stretchyIkSpline_parametric(ikHandle,scaleAxis='x',scaleAttr='',blendControl='',blendAttr='stretchScale',minPercent=0.0,maxPercent=1.0,prefix=''):
	'''
	Build stretchy IK spline setup using the parametric length of the input curve.
	@param ikHandle: IK Handle to create stretchy setup for
	@type ikHandle: str
	@param scaleAxis: Axis along which the ik joints will be scaled
	@type scaleAxis: str
	@param scaleAttr: World scale attribute
	@type scaleAttr: str
	@param blendControl: Control object that will contain the attribute to control the stretchy IK blending. If left at default (""), blending will not be enabled.
	@type blendControl: str
	@param blendAttr: The name of the attribute on blendControl that will control the stretchy IK blending.
	@type blendAttr: str
	@param minPercent: The minimum u paramerter percentage to calculate the stretch from
	@type minPercent: float
	@param maxPercent: The maximum u paramerter percentage to calculate the stretch to
	@type maxPercent: float
	@param prefix: Name prefix for builder created nodes
	@type prefix: str
	'''
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(ikHandle)
	
	# Check objects
	if not mc.objExists(ikHandle): raise UserInputError('IK handle '+ikHandle+' does not exist!')
	
	# Check scaleAttr
	scale = mc.objExists(scaleAttr)
	
	# Check blendControl
	blend = mc.objExists(blendControl)
	if blend and not mc.objExists(blendControl+'.'+blendAttr):
			mc.addAttr(blendControl,ln=blendAttr,at='double',min=0,max=1,dv=1,k=True)
	blendAttr = blendControl+'.'+blendAttr
	
	# Get IK spline information
	ik_joints = glTools.utils.ik.getAffectedJoints(ikHandle)
	ik_curve = mc.listConnections(ikHandle+'.inCurve',s=True,d=False,sh=True)[0]
	
	# Get curve parameter information
	minu = mc.getAttr(ik_curve+'.minValue')
	maxu = mc.getAttr(ik_curve+'.maxValue')
	udist = maxu - minu
	if (minPercent > 0.0) or (maxPercent < 1.0):
		if minPercent > 0.0: minu += udist * minPercent
		if maxPercent < 1.0: maxu -= udist * (1.0-maxPercent)
		udist = maxu - minu
	inc = udist / (len(ik_joints)-1)
	
	# Create pointOnCurveInfo and attach to curve
	pointOnCurveList = []
	for i in range(len(ik_joints)):
		ind = str(i+1)
		if i<9: ind = '0'+ind
		poc = mc.createNode('pointOnCurveInfo',n=prefix+ind+'_pointOnCurveInfo')
		pointOnCurveList.append(poc)
		mc.connectAttr(ik_curve+'.worldSpace[0]',poc+'.inputCurve',f=True)
		mc.setAttr(poc+'.parameter',minu+inc*i)
	
	# Create distanceBetween and connect to curvePoints
	distNodeList = []
	for i in range(len(ik_joints)-1):
		ind = str(i+1)
		if i<9: ind = '0'+ind
		dist = mc.createNode('distanceBetween',n=prefix+ind+'_distanceBetween')
		distNodeList.append(dist)
		mc.connectAttr(pointOnCurveList[i]+'.position',dist+'.point1',f=True)
		mc.connectAttr(pointOnCurveList[i+1]+'.position',dist+'.point2',f=True)
	
	# Create multiply node and connect to joints
	multNodeList = []
	scaleNodeList = []
	for i in range(len(ik_joints)-1):
		ind = glTools.utils.stringUtils.stringIndex(i+1,2)
		# Get distance to size scale ratio
		md = mc.createNode('multiplyDivide',n=prefix+ind+'_multiplyDivide')
		multNodeList.append(md)
		mc.setAttr(md+'.operation',2) # Divide
		mc.connectAttr(distNodeList[i]+'.distance',md+'.input1X',f=True)
		mc.connectAttr(ik_joints[i+1]+'.t'+scaleAxis,md+'.input2X',f=True)
		
		# Create blend node
		blendNode = ''
		if blend:
			blendNode = mc.createNode('blendTwoAttr',n=prefix+ind+'_blendTwoAttr')
			mc.connectAttr(blendAttr,blendNode+'.attributesBlender',f=True)
			mc.setAttr(blendNode+'.input[0]',1.0)
		
		# Setup scale compensation
		if scale:
			# Add global scale contribution
			scaleNode = mc.createNode('multiplyDivide',n=prefix+ind+'_multiplyDivide')
			scaleNodeList.append(scaleNode)
			mc.setAttr(scaleNode+'.operation',2) # Divide
			mc.connectAttr(md+'.outputX',scaleNode+'.input1X',f=True)
			mc.connectAttr(scaleAttr,scaleNode+'.input2X',f=True)
			# Connect to joint scale
			if blend:
				mc.connectAttr(scaleNode+'.outputX',blendNode+'.input[1]',f=True)
				mc.connectAttr(blendNode+'.output',ik_joints[i]+'.s'+scaleAxis,f=True)
			else:
				mc.connectAttr(scaleNode+'.outputX',ik_joints[i]+'.s'+scaleAxis,f=True)
		else:
			# Connect to joint scale
			if blend:
				mc.connectAttr(md+'.outputX',blendNode+'.input[1]',f=True)
				mc.connectAttr(blendNode+'.output',ik_joints[i]+'.s'+scaleAxis,f=True)
			else:
				mc.connectAttr(md+'.outputX',ik_joints[i]+'.s'+scaleAxis,f=True)
	
	# Return result
	return [pointOnCurveList,distNodeList,multNodeList,scaleNodeList]

def stretchyIkSpline_arcLength(ikHandle,scaleAxis='x',scaleAttr='',blendControl='',blendAttr='stretchScale',prefix=''):
	'''
	Build stretchy IK spline setup using the arc length of the input curve.
	@param ikHandle: IK Handle to create stretchy setup for
	@type ikHandle: str
	@param scaleAxis: Axis along which the ik joints will be scaled
	@type scaleAxis: str
	@param scaleAttr: World scale attribute
	@type scaleAttr: str
	@param blendControl: Control object that will contain the attribute to control the stretchy IK blending. If left at default (""), blending will not be enabled.
	@type blendControl: str
	@param blendAttr: The name of the attribute on blendControl that will control the stretchy IK blending.
	@type blendAttr: str
	@param prefix: Name prefix for builder created nodes
	@type prefix: str
	'''
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(ikHandle)
	
	# Check objects
	if not mc.objExists(ikHandle): raise UserInputError('IK handle '+ikHandle+' does not exist!')
	
	# Check blendControl
	blend = mc.objExists(blendControl)
	if blend and not mc.objExists(blendControl+'.'+blendAttr):
			mc.addAttr(blendControl,ln=blendAttr,at='double',min=0,max=1,dv=1,k=True)
	blendAttr = blendControl+'.'+blendAttr
	
	# Get IK spline information
	ik_joints = glTools.utils.ik.getAffectedJoints(ikHandle)
	ik_curve = mc.listConnections(ikHandle+'.inCurve',s=1,d=0,sh=1)[0]
	ik_length = mc.arclen(ik_curve)
	
	# Setup multily node
	multDbl = mc.createNode('multDoubleLinear',n=prefix+'_multDoubleLinear')
	mc.setAttr(multDbl+'.input2',1.0/ik_length)
	
	# Setup blend
	blendNode = ''
	if blend:
		blendNode = mc.createNode('blendTwoAttr',n=prefix+'_blendTwoAttr')
		mc.addAttr(blendNode,ln=self.defaultScaleAttr,at='double',min=1,max=1,dv=1)
		mc.connectAttr(blendAttr,blendNode+'.attributesBlender',f=True)
		mc.connectAttr(blendNode+'.'+self.defaultScaleAttr,blendNode+'.input[0]',f=True)
	
	# Create curveInfo
	crvInfo = mc.createNode('curveInfo',n=prefix+'_curveInfo')
	mc.connectAttr(ik_curve+'.worldSpace[0]',crvInfo+'.inputCurve',f=True)
	# Connect multilyDivide
	mc.connectAttr(crvInfo+'.arcLength',multDbl+'.input1',f=True)
	# Attach stretchy IK network to joint scale
	if blend:
		mc.connectAttr(multDbl+'.output',blendNode+'.input[1]',f=True)
		# Attach output of blendNode to joint scale
		for i in range(len(ik_joints)-1):
			mc.connectAttr(blendNode+'.output',ik_joints[i]+'.s'+scaleAxis,f=True)
	else:
		for i in range(len(ik_joints)-1):
			mc.connectAttr(multDbl+'.output',ik_joints[i]+'.s'+scaleAxis,f=True)
	
	# Return result
	return [crvInfo,multDbl,blendNode]
