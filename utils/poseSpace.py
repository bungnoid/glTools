import maya.cmds as mc

import glTools.utils.stringUtils

def poseDrivenAttr(poseTransform,poseAxis='x',targetAttr,remapValue=False,prefix=''):
	'''
	Create a pose driven attribute.
	@param poseTransform: The transform that the pose is based on
	@type poseTransform: str
	@param targetAttr: The attribute that will be driven by the pose
	@type targetAttr: str
	@param poseAxis: The axis of the pose transform that will describe the pose
	@type poseAxis: str
	@param prefix: The name prefix for all created nodes
	@type prefix: str
	'''
	# ----------
	# - Checks -
	# ----------
	
	# Check pose transform
	if not mc.objExists(poseTransform):
		raise Exception('PoseTransform "'+poseTransform+'" does not exist!')
	
	# Check target attribute
	if not mc.objExists(targetAttr):
		raise Exception('Target attribute "'+targetAttr+'" does not exist!')
	
	# Check reference axis
	poseAxis = poseAxis.lower()
	if not poseAxis in ['x','y','z']:
		raise Exception('Invalid pose axis! Valid pose axis values are "x" "y" and "z"!!')
	
	# Check prefix
	if not prefix:
		prefix = glTools.utils.stringUtils.stripSuffix(poseTransform)
	
	# ----------------------------------
	# - Create poseReference transform -
	# ----------------------------------
	
	poseReference = prefix+'_poseReference'
	poseReference = mc.duplicate(transform,parentOnly=True,n=poseReference)
	
	# Add poseTransform message attribute
	mc.addAttr(poseReference,ln='poseTransform',at='message')
	mc.connectAttr(poseTransform+'.message',poseReference+'.poseTransform',f=True)
	
	# ------------------------------------
	# - Create vector comparison network -
	# ------------------------------------
	
	poseVector = {'x':[1,0,0],'y':[0,1,0],'z':[0,0,1]}[poseAxis]
	
	# - Pose Transform Vector
	poseVecDotProduct = mc.createNode('vectorProduct',n=prefix+'_poseVector_vectorProduct')
	mc.setAttr(poseVecDotProduct+'.operation',3) # Vector Matric Product
	mc.setAttr(poseVecDotProduct+'.input',poseVector[0],poseVector[1],poseVector[2])
	mc.setAttr(poseVecDotProduct+'.normalizeOutput',1)
	mc.connectAttr(poseTransform+'.worldMatrix[0]',poseVecDotProduct+'.matrix',f=True)
	
	# - Pose Reference Vector
	referenceVecDotProduct = mc.createNode('vectorProduct',n=prefix+'_referenceVector_vectorProduct')
	mc.setAttr(referenceVecDotProduct+'.operation',3) # Vector Matric Product
	mc.setAttr(referenceVecDotProduct+'.input',poseVector[0],poseVector[1],poseVector[2])
	mc.setAttr(referenceVecDotProduct+'.normalizeOutput',1)
	mc.connectAttr(poseReference+'.worldMatrix[0]',referenceVecDotProduct+'.matrix',f=True)
	
	# - Pose Vector Comparison
	vectorCompareDotProduct = mc.createNode('vectorProduct',n=prefix+'_vectorCompare_vectorProduct')
	mc.setAttr(vectorCompareDotProduct+'.operation',1) # Dot Product
	mc.setAttr(vectorCompareDotProduct+'.normalizeOutput',1)
	mc.connectAttr(poseVecDotProduct+'.output',vectorCompareDotProduct+'.input1')
	mc.connectAttr(referenceVecDotProduct+'.output',vectorCompareDotProduct+'.input2')
	
	# -----------------------
	# - Clamp output values -
	# -----------------------
	poseClamp = mc.createNode('clamp',prefix+'_clamp')
	mc.connectAttr(vectorCompareDotProduct+'.outputX',poseClamp+'.inputR',f=True)
	mc.setAttr(poseClamp+'.minR',0.0)
	mc.setAttr(poseClamp+'.maxR',1.0)
	
	# -----------------------
	# - Remap output Values -
	# -----------------------
	remapValueNode = ''
	if remapValue:
		remapValNode = mc.createNode('remapValue',n=prefix+'_remapValue')
		mc.connectAttr(poseClamp+'.outputR',remapValNode+'.inputValue',f=True)
		mc.connectAttr(remapValNode+'.outValue',targetAttr,f=True)
	else:
		mc.connectAttr(poseClamp+'.outputR',targetAttr,f=True)
	
	# -----------------
	# - Return Result -
	# -----------------
	
	return poseReference
