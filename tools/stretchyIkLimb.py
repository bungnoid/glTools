import maya.cmds as mc

import glTools.utils.ik
import glTools.utils.joint

def build(	ikHandle,
			ikCtrl,
			pvCtrl,
			scaleAxis='x',
			scaleAttr='',
			prefix=''):
	'''
	Create a stretchy IK limb
	@param ikHandle: IK Handle to create stretchy limb setup for
	@type ikHandle: str
	@param ikCtrl: IK Handle or limb end (wrist/ankle) control
	@type ikCtrl: str
	@param pvCtrl: Pole vector or limb mid (elbow/knee) control
	@type pvCtrl: str
	@param scaleAxis: Axis along which the ik joints will be scaled
	@type scaleAxis: str
	@param scaleAttr: World scale attribute
	@type scaleAttr: str
	@param prefix: Name prefix for all builder created nodes. If left as deafult ('') prefix will be derived from ikHandle name.
	@type prefix: str
	'''
	
	upperScaleAttr = 'upperLimbScale'
	lowerScaleAttr = 'lowerLimbScale'
	blendAttr = 'stretchToControl'
	biasAttr = 'stretchBias'
	
	# ==============
	# - Get Joints -
	# ==============
	
	ikJoints = glTools.utils.ik.getAffectedJoints(ikHandle)
	
	# ========================
	# - Add Joint Attributes -
	# ========================
	
	for ikJoint in ikJoints[:-1]:
		jntLen = glTools.utils.joint.length(ikJoint)
		mc.addAttr(ikJoint,ln='restLength',dv=jntLen)
	
	# =============================
	# - Add IK Control Attributes -
	# =============================
	
	# IK Control
	mc.addAttr(ikCtrl,ln=upperScaleAttr,min=0.01,dv=1.0,k=True)
	mc.addAttr(ikCtrl,ln=lowerScaleAttr,min=0.01,dv=1.0,k=True)
	mc.addAttr(ikCtrl,ln=blendAttr,min=0.0,max=1.0,dv=0.0,k=True)
	mc.addAttr(ikCtrl,ln=biasAttr,min=0.0,max=1.0,dv=0.5,k=True)
	
	# PV Control
	mc.addAttr(pvCtrl,ln=blendAttr,min=0.0,max=1.0,dv=0.0,k=True)
	
	# ===============================
	# - Create Limb Stretch Network -
	# ===============================
	
	# Limb Length - Character Scale
	limbCharScale = mc.createNode('multiplyDivide',n=prefix+'_characterScale_multiplyDivide')
	mc.setAttr(limbCharScale+'.operation',2) # Divide
	mc.connectAttr(scaleAttr,limbCharScale+'.input2X',f=True)
	mc.connectAttr(scaleAttr,limbCharScale+'.input2Y',f=True)
	mc.connectAttr(scaleAttr,limbCharScale+'.input2Z',f=True)
	
	# Rest Length
	limbRestLenNode = mc.createNode('plusMinusAverage',n=prefix+'_limbRestLength_plusMinusAverage')
	for i in range(len(ikJoints[:-1])):
		mc.connectAttr(ikJoints[i]+'.restLength',limbRestLenNode+'.input1D['+str(i)+']',f=True)
	
	# Limb Length
	limbDistNode = mc.createNode('distanceBetween',n=prefix+'_limbLength_distanceBetween')
	mc.connectAttr(ikJoints[0]+'.parentMatrix[0]',limbDistNode+'.inMatrix1',f=True)
	mc.connectAttr(ikCtrl+'.worldMatrix[0]',limbDistNode+'.inMatrix2',f=True)
	mc.connectAttr(limbDistNode+'.distance',limbCharScale+'.input1X',f=True)
	
	# Limb Length Diff
	limbDiffNode = mc.createNode('plusMinusAverage',n=prefix+'_limbLengthDiff_plusMinusAverage')
	mc.setAttr(limbDiffNode+'.operation',2) # Subtract
	mc.connectAttr(limbCharScale+'.outputX',limbDiffNode+'.input1D[0]',f=True)
	mc.connectAttr(limbRestLenNode+'.output1D',limbDiffNode+'.input1D[1]',f=True)
	
	# Bias Reverse
	limbBiasRev = mc.createNode('reverse',n=prefix+'_limbBias_reverse')
	mc.connectAttr(ikCtrl+'.'+biasAttr,limbBiasRev+'.inputX',f=True)
	
	# Upper Stretch Diff
	upperStretchDiff = mc.createNode('multDoubleLinear',n=prefix+'_upperStretchDiff_multDoubleLinear')
	mc.connectAttr(limbDiffNode+'.output1D',upperStretchDiff+'.input1',f=True)
	mc.connectAttr(ikCtrl+'.'+biasAttr,upperStretchDiff+'.input2',f=True)
	
	# Lower Stretch Diff
	lowerStretchDiff = mc.createNode('multDoubleLinear',n=prefix+'_lowerStretchDiff_multDoubleLinear')
	mc.connectAttr(limbDiffNode+'.output1D',lowerStretchDiff+'.input1',f=True)
	mc.connectAttr(limbBiasRev+'.outputX',lowerStretchDiff+'.input2',f=True)
	
	# Upper Stretch Length
	upperStretchLen = mc.createNode('addDoubleLinear',n=prefix+'_upperStretchTarget_addDoubleLinear')
	mc.connectAttr(ikJoints[0]+'.restLength',upperStretchLen+'.input1',f=True)
	mc.connectAttr(upperStretchDiff+'.output',upperStretchLen+'.input2',f=True)
	
	# Lower Stretch Length
	lowerStretchLen = mc.createNode('addDoubleLinear',n=prefix+'_lowerStretchTarget_addDoubleLinear')
	mc.connectAttr(ikJoints[1]+'.restLength',lowerStretchLen+'.input1',f=True)
	mc.connectAttr(lowerStretchDiff+'.output',lowerStretchLen+'.input2',f=True)
	
	# Upper Stretch Scale
	upperStretchScale = mc.createNode('multiplyDivide',n=prefix+'_upperStretchScale_multiplyDivide')
	mc.setAttr(upperStretchScale+'.operation',2) # Divide
	mc.connectAttr(upperStretchLen+'.output',upperStretchScale+'.input1X',f=True)
	mc.connectAttr(ikJoints[0]+'.restLength',upperStretchScale+'.input2X',f=True)
	
	# Lower Stretch Scale
	lowerStretchScale = mc.createNode('multiplyDivide',n=prefix+'_lowerStretchScale_multiplyDivide')
	mc.setAttr(lowerStretchScale+'.operation',2) # Divide
	mc.connectAttr(lowerStretchLen+'.output',lowerStretchScale+'.input1X',f=True)
	mc.connectAttr(ikJoints[1]+'.restLength',lowerStretchScale+'.input2X',f=True)
	
	# =====================================
	# - Create Stretch To Control Network -
	# =====================================
	
	# Shoulder to PV distance
	upperPvDist = mc.createNode('distanceBetween',n=prefix+'_upperPV_distanceBetween')
	mc.connectAttr(ikJoints[0]+'.parentMatrix[0]',upperPvDist+'.inMatrix1',f=True)
	mc.connectAttr(pvCtrl+'.worldMatrix[0]',upperPvDist+'.inMatrix2',f=True)
	mc.connectAttr(upperPvDist+'.distance',limbCharScale+'.input1Y',f=True)
	
	# Wrist to PV distance
	lowerPvDist = mc.createNode('distanceBetween',n=prefix+'_lowerPV_distanceBetween')
	mc.connectAttr(ikCtrl+'.worldMatrix[0]',lowerPvDist+'.inMatrix1',f=True)
	mc.connectAttr(pvCtrl+'.worldMatrix[0]',lowerPvDist+'.inMatrix2',f=True)
	mc.connectAttr(lowerPvDist+'.distance',limbCharScale+'.input1Z',f=True)
	
	# Upper to PV scale
	upperPvScale = mc.createNode('multiplyDivide',n=prefix+'_upperPV_multiplyDivide')
	mc.setAttr(upperPvScale+'.operation',2) # Divide
	mc.connectAttr(limbCharScale+'.outputY',upperPvScale+'.input1X',f=True)
	mc.connectAttr(ikJoints[0]+'.restLength',upperPvScale+'.input2X',f=True)
	
	# Lower to PV scale
	lowerPvScale = mc.createNode('multiplyDivide',n=prefix+'_lowerPV_multiplyDivide')
	mc.setAttr(lowerPvScale+'.operation',2) # Divide
	mc.connectAttr(limbCharScale+'.outputZ',lowerPvScale+'.input1X',f=True)
	mc.connectAttr(ikJoints[1]+'.restLength',lowerPvScale+'.input2X',f=True)
	
	# ============================
	# - Create Condition Network -
	# ============================
	
	# Limb Stretch - Condition
	limbStretchCondition = mc.createNode('condition',n=prefix+'_limbStretch_condition')
	mc.setAttr(limbStretchCondition+'.operation',2) # Greater Than
	# !!!!!!!!!!!!! ".secondTerm" had been set to 1.0 for some reason? Should be 0 to register any difference
	mc.setAttr(limbStretchCondition+'.secondTerm',0.0)
	mc.connectAttr(limbDiffNode+'.output1D',limbStretchCondition+'.firstTerm',f=True)
	mc.setAttr(limbStretchCondition+'.colorIfFalse',1.0,1.0,1.0)
	mc.connectAttr(upperStretchScale+'.outputX',limbStretchCondition+'.colorIfTrueR',f=True)
	mc.connectAttr(lowerStretchScale+'.outputX',limbStretchCondition+'.colorIfTrueG',f=True)
	
	# Limb Stretch - Upper Blend
	upperLimbStretchBlend = mc.createNode('blendTwoAttr',n=prefix+'_upperLimbSTretch_blendTwoAttr')
	mc.connectAttr(ikCtrl+'.'+blendAttr,upperLimbStretchBlend+'.attributesBlender',f=True)
	mc.setAttr(upperLimbStretchBlend+'.input[0]',1.0)
	mc.connectAttr(limbStretchCondition+'.outColorR',upperLimbStretchBlend+'.input[1]',f=True)
	
	# Limb Stretch - Lower Blend
	lowerLimbStretchBlend = mc.createNode('blendTwoAttr',n=prefix+'_lowerLimbSTretch_blendTwoAttr')
	mc.connectAttr(ikCtrl+'.'+blendAttr,lowerLimbStretchBlend+'.attributesBlender',f=True)
	mc.setAttr(lowerLimbStretchBlend+'.input[0]',1.0)
	mc.connectAttr(limbStretchCondition+'.outColorG',lowerLimbStretchBlend+'.input[1]',f=True)
	
	# Limb Stretch - Upper Scale
	upperLimbStretchScale = mc.createNode('multDoubleLinear',n=prefix+'_upperStretchScale_multDoubleLinear')
	mc.connectAttr(upperLimbStretchBlend+'.output',upperLimbStretchScale+'.input1',f=True)
	mc.connectAttr(ikCtrl+'.upperLimbScale',upperLimbStretchScale+'.input2',f=True)
	
	# Limb Stretch - Lower Scale
	lowerLimbStretchScale = mc.createNode('multDoubleLinear',n=prefix+'_lowerStretchScale_multDoubleLinear')
	mc.connectAttr(lowerLimbStretchBlend+'.output',lowerLimbStretchScale+'.input1',f=True)
	mc.connectAttr(ikCtrl+'.lowerLimbScale',lowerLimbStretchScale+'.input2',f=True)
	
	# Stretch To Control - Upper Blend
	upStretchToCtrlBlend = mc.createNode('blendTwoAttr',n=prefix+'_upperStretchToControl_blendTwoAttr')
	mc.connectAttr(pvCtrl+'.'+blendAttr,upStretchToCtrlBlend+'.attributesBlender',f=True)
	mc.connectAttr(upperLimbStretchScale+'.output',upStretchToCtrlBlend+'.input[0]',f=True)
	mc.connectAttr(upperPvScale+'.outputX',upStretchToCtrlBlend+'.input[1]',f=True)
	
	# Stretch To Control - Lower Mult
	stretchToCtrlAllMult = mc.createNode('multDoubleLinear',n=prefix+'_stretchCombineWt_multDoubleLinear')
	mc.connectAttr(ikCtrl+'.'+blendAttr,stretchToCtrlAllMult+'.input1',f=True)
	mc.connectAttr(pvCtrl+'.'+blendAttr,stretchToCtrlAllMult+'.input2',f=True)
	
	# Stretch To Control - Lower Blend
	loStretchToCtrlBlend = mc.createNode('blendTwoAttr',n=prefix+'_lowerStretchToControl_blendTwoAttr')
	mc.connectAttr(stretchToCtrlAllMult+'.output',loStretchToCtrlBlend+'.attributesBlender',f=True)
	mc.connectAttr(lowerLimbStretchScale+'.output',loStretchToCtrlBlend+'.input[0]',f=True)
	mc.connectAttr(lowerPvScale+'.outputX',loStretchToCtrlBlend+'.input[1]',f=True)
	
	# =======================
	# - End Effector Offset -
	# =======================
	
	# Get End Effector
	endEffector = mc.listConnections(ikHandle+'.endEffector',s=True,d=False)[0]
	endEffectorCon = mc.listConnections(endEffector+'.tx',s=True,d=False)[0]
	
	# Disconnect End Effector
	mc.disconnectAttr(endEffectorCon+'.tx',endEffector+'.tx')
	mc.disconnectAttr(endEffectorCon+'.ty',endEffector+'.ty')
	mc.disconnectAttr(endEffectorCon+'.tz',endEffector+'.tz')
	
	# End Effector Offset
	endOffsetReverse = mc.createNode('reverse',n=prefix+'_limbEndOffset_reverse')
	mc.connectAttr(ikCtrl+'.'+blendAttr,endOffsetReverse+'.inputX',f=True)
	endOffsetMultiply = mc.createNode('multDoubleLinear',n=prefix+'limbEndOffset_multDoubleLinear')
	mc.connectAttr(pvCtrl+'.'+blendAttr,endOffsetMultiply+'.input1',f=True)
	mc.connectAttr(endOffsetReverse+'.outputX',endOffsetMultiply+'.input2',f=True)
	
	# End Effector Offset Length
	endEffectorScale = mc.createNode('multDoubleLinear',n=prefix+'_limbEndScale_multDoubleLinear')
	mc.connectAttr(ikJoints[1]+'.restLength',endEffectorScale+'.input1',f=True)
	mc.connectAttr(lowerPvScale+'.outputX',endEffectorScale+'.input2',f=True)
	
	# End Effector Offset Scale
	endEffectorScaleMD = mc.createNode('multiplyDivide',n=prefix+'_limbEndScale_multiplyDivide')
	mc.setAttr(endEffectorScaleMD+'.operation',2) # Divide
	mc.connectAttr(endEffectorScale+'.output',endEffectorScaleMD+'.input1X',f=True)
	mc.connectAttr(loStretchToCtrlBlend+'.output',endEffectorScaleMD+'.input2X',f=True)
	
	# End Effector Offset Blend
	endEffectorBlend = mc.createNode('blendTwoAttr',n=prefix+'_limbEndOffset_blendTwoAttr')
	mc.connectAttr(endOffsetMultiply+'.output',endEffectorBlend+'.attributesBlender',f=True)
	mc.connectAttr(ikJoints[1]+'.restLength',endEffectorBlend+'.input[0]',f=True)
	#mc.connectAttr(endEffectorScale+'.output',endEffectorBlend+'.input[1]',f=True)
	mc.connectAttr(endEffectorScaleMD+'.outputX',endEffectorBlend+'.input[1]',f=True)
	
	# =====================
	# - Connect To Joints -
	# =====================
	
	mc.connectAttr(upStretchToCtrlBlend+'.output',ikJoints[0]+'.s'+scaleAxis,f=True)
	mc.connectAttr(loStretchToCtrlBlend+'.output',ikJoints[1]+'.s'+scaleAxis,f=True)
	
	# ===========================
	# - Connect To End Effector -
	# ===========================
	
	# Check Negative Translate Values
	endEffectorNegate = ''
	if mc.getAttr(endEffectorCon+'.t'+scaleAxis) < 0.0:
		
		# Negate Result
		endEffectorNegate = mc.createNode('unitConversion',n=prefix+'_endEffectorNegate_unitConversio')
		mc.connectAttr(endEffectorBlend+'.output',endEffectorNegate+'.input',f=True)
		mc.setAttr(endEffectorNegate+'.conversionFactor',-1)
		mc.connectAttr(endEffectorNegate+'.output',endEffector+'.t'+scaleAxis,f=True)
		
	else:
		
		# Direct Connection
		mc.connectAttr(endEffectorBlend+'.output',endEffector+'.t'+scaleAxis,f=True)
	
	# =================
	# - Return Result -
	# =================
	
	result = {}
	
	result['ikHandle'] = ikHandle
	result['endEffector'] = endEffector
	result['ikCtrl'] = ikCtrl
	result['pvCtrl'] = pvCtrl
	result['joints'] = ikJoints
	result['charScaleNode'] = limbCharScale
	result['restLengthNode'] = limbRestLenNode
	result['limbDistNode'] = limbDistNode
	result['limbDiffNode'] = limbDiffNode
	result['limbBiasReverse'] = limbBiasRev
	result['upperStretchDiff'] = upperStretchDiff
	result['lowerStretchDiff'] = lowerStretchDiff
	result['upperStretchLen'] = upperStretchLen
	result['lowerStretchLen'] = lowerStretchLen
	result['upperStretchScale'] = upperStretchScale
	result['lowerStretchScale'] = lowerStretchScale
	result['upperPoleVectorDist'] = upperPvDist
	result['lowerPoleVectorDist'] = lowerPvDist
	result['upperPoleVectorScale'] = upperPvScale
	result['lowerPoleVectorScale'] = lowerPvScale
	result['limbStretchCondition'] = limbStretchCondition
	result['upperLimbStretchBlend'] = upperLimbStretchBlend
	result['lowerLimbStretchBlend'] = lowerLimbStretchBlend
	result['upperLimbStretchScale'] = upperLimbStretchScale
	result['lowerLimbStretchScale'] = lowerLimbStretchScale
	result['upperStretchToCtrlBlend'] = upStretchToCtrlBlend
	result['lowerStretchToCtrlBlend'] = loStretchToCtrlBlend
	result['stretchToCtrlMult'] = stretchToCtrlAllMult
	result['endOffsetReverse'] = endOffsetReverse
	result['endEffectorScale'] = endEffectorScale
	result['endEffectorScaleMult'] = endEffectorScaleMD
	result['endEffectorBlend'] = endEffectorBlend
	result['endEffectorNegate'] = endEffectorNegate
	
	return result

