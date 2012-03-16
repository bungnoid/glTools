import maya.cmds as mc
import maya.mel as mm

import glTools.utils.ik
import glTools.utils.stringUtils

def build(ikHandle,scaleAxis='x',scaleAttr='',blendControl='',blendAttr='stretchScale',shrink=False,prefix=''):
	'''
	Create a stretchy IK chain
	@param ikHandle: IK Handle to create stretchy setup for
	@type ikHandle: str
	@param scaleAttr: World scale attribute
	@type scaleAttr: str
	@param scaleAxis: Axis along which the ik joints will be scaled
	@type scaleAxis: str
	@param blendControl: Control object that will contain the attribute to control the stretchy IK blending. If left at default (""), blending will not be enabled.
	@type blendControl: str
	@param blendAttr: The name of the attribute on blendControl that will control the stretchy IK blending.
	@type blendAttr: str
	@param shrink: Enable joint shrinking.
	@type shrink: bool
	@param prefix: Name prefix for all builder created nodes. If left as deafult ('') prefix will be derived from ikHandle name.
	@type prefix: str
	'''
	
	# Check objects
	if not mc.objExists(ikHandle): raise Exception('IK handle '+ikHandle+' does not exist!')
	
	# Check blendControl
	blend = mc.objExists(blendControl)
	if blend and not mc.objExists(blendControl+'.'+blendAttr):
			mc.addAttr(blendControl,ln=blendAttr,at='double',min=0,max=1,dv=1)
			mc.setAttr(blendControl+'.'+blendAttr,e=True,k=True)
	blendAttr = blendControl+'.'+blendAttr
	
	# Extract name prefix from ikHandle name
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(ikHandle)
	
	# Get IK chain information
	ikJoints = glTools.utils.ik.getAffectedJoints(ikHandle)
	ikPos = mc.getAttr(ikHandle+'.t')[0]
	
	# Calculate actual joint lengths
	lengthNode = mc.createNode('plusMinusAverage',n=prefix+'length_plusMinusAverage')
	for j in range(len(ikJoints)-1):
		mc.connectAttr(ikJoints[j+1]+'.t'+scaleAxis,lengthNode+'.input1D['+str(j)+']')
	
	# Calculate Distance
	distNode = mc.createNode('distanceBetween',n=prefix+'_distanceBetween')
	mc.connectAttr(ikJoints[0]+'.parentMatrix[0]',distNode+'.inMatrix1',f=True)
	mc.connectAttr(ikHandle+'.parentMatrix[0]',distNode+'.inMatrix2',f=True)
	
	# -------------!!!!!!!!!!
	# Currently setting the translate attributes instead of connecting.
	# Direct connection was causing occasional cycle check warnings
	root_pos = mc.getAttr(ikJoints[0]+'.t')[0]
	mc.setAttr(distNode+'.point1',root_pos[0],root_pos[1],root_pos[2])
	mc.setAttr(distNode+'.point2',ikPos[0],ikPos[1],ikPos[2])
	#mc.connectAttr(ik_joint[0]+'.t',distNode+'.point1',f=True)
	#mc.connectAttr(ikHandle+'.t',distNode+'.point2',f=True)
	# -------------
	
	# Calculate Stretch Scale Factor
	stretchNode = mc.createNode('multiplyDivide',n=prefix+'_stretch_multiplyDivide')
	mc.setAttr(stretchNode+'.operation',2) # Divide
	mc.connectAttr(distNode+'.distance',stretchNode+'.input1X',f=True)
	
	# Add Scale Compensation
	scaleNode = ''
	if mc.objExists(scaleAttr):
		scaleNode = mc.createNode('multDoubleLinear',n=prefix+'_scale_multDoubleLinear')
		mc.connectAttr(lengthNode+'.output1D',scaleNode+'.input1',f=True)
		mc.connectAttr(scaleAttr,scaleNode+'.input2',f=True)
		mc.connectAttr(scaleNode+'.output',stretchNode+'.input2X',f=True)
	else:
		mc.connectAttr(lengthNode+'.output1D',stretchNode+'.input2X',f=True)
	
	# Condition
	condNode = ''
	if not shrink:
		condNode = mc.createNode('condition',n=prefix+'_shrink_condition')
		# Set condition operation
		mc.setAttr(condNode+'.operation',2) # Greater than
		# Set second term as current length
		mc.connectAttr(distNode+'.distance',condNode+'.firstTerm',f=True)
		# Set first term as original length
		if scaleNode: mc.connectAttr(scaleNode+'.output',condNode+'.secondTerm',f=True)
		else: mc.connectAttr(lengthNode+'.output1D',condNode+'.secondTerm',f=True)
		# Set condition results
		mc.connectAttr(stretchNode+'.outputX',condNode+'.colorIfTrueR',f=True)
		mc.setAttr(condNode+'.colorIfFalseR',1)
	
	# Setup Blend
	blendNode = ''
	if blend:
		blendNode = mc.createNode('blendTwoAttr',n=prefix+'_blend_blendTwoAttr')
		mc.connectAttr(blendAttr,blendNode+'.attributesBlender',f=True)
		# Connect Blend
		mc.setAttr(blendNode+'.input[0]',1.0)
		if shrink: mc.connectAttr(stretchNode+'.outputX',blendNode+'.input[1]',f=True)
		else: mc.connectAttr(condNode+'.outColorR',blendNode+'.input[1]',f=True)
	
	# Attach output to joint scale
	for i in range(len(ikJoints)-1):
		if blend:
			mc.connectAttr(blendNode+'.output',ikJoints[i]+'.s'+scaleAxis,f=True)
		else:
			if shrink: mc.connectAttr(stretchNode+'.outputX',ikJoints[i]+'.s'+scaleAxis,f=True)
			else: mc.connectAttr(condNode+'.outColorR',ikJoints[i]+'.s'+scaleAxis,f=True)
	
	# Set ikHandle position. Make sure IK handle evaluates correctly!
	mc.setAttr(ikHandle+'.t',ikPos[0],ikPos[1],ikPos[2])
	
	# Return result
	result = [lengthNode,distNode,stretchNode,scaleNode,condNode,blendNode]
	return result
