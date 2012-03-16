import maya.cmds as mc


import glTools.utils.channelState
import glTools.utils.joint

import glTools.tools.controlBuilder

def build(startJoint,endJoint,controlShape='circle',endCtrl=False,ctrlRotate=[0,0,0],ctrlOrient=True,ctrlScale=1.0,ctrlLod='primary',prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not prefix: prefix = 'fkChain'
	
	if not mc.objExists(startJoint):
		raise Exception('Start Joint "'+startJoint+'" does nto exist!')
	if not mc.objExists(endJoint):
		raise Exception('End Joint "'+endJoint+'" does nto exist!')
	
	# ====================
	# - Configure Module -
	# ====================
	
	
	
	# ==========================
	# - Build Module Structure -
	# ==========================
	
	# Create control group
	ctrl_grp = mc.group(em=True,n=prefix+'_ctrl_grp',w=True)
	
	# Create rig group
	rig_grp = mc.group(em=True,n=prefix+'_rig_grp',w=True)
	
	# Create skel group
	skel_grp = mc.group(em=True,n=prefix+'_skel_grp',w=True)
	
	# Create module group
	module = mc.group(em=True,n=prefix+'_module')
	mc.parent([ctrl_grp,rig_grp,skel_grp],module)
	
	# - Uniform Scale -
	mc.addAttr(module,ln='uniformScale',min=0.001,dv=1.0)
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleX')
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleY')
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleZ')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleX')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleY')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleZ')
	
	# ===================
	# - Create Controls -
	# ===================
	
	# Get joint list
	jointList = glTools.utils.joint.getJointList(startJoint,endJoint)
	
	# Get joint length
	jntLen = 0.0
	for jnt in jointList:
		cJntLen = glTools.utils.joint.length(jnt)
		if cJntLen > jntLen: jntLen = cJntLen
	
	# Build joint controls
	jointGrps = []
	jointShape = []
	for joint in jointList[:-1]:
		
		# Add control shape
		jntShape = glTools.tools.controlBuilder.controlShape(joint,controlShape,rotate=ctrlRotate,orient=ctrlOrient,scale=jntLen*ctrlScale)
		# Add joint buffer
		jntGrp = glTools.utils.joint.group(joint)
		# Tag Control
		glTools.rig.utils.tagCtrl(joint,ctrlLod)
		# Append arrays
		jointGrps.append(jntGrp)
		jointShape.extend(jntShape)
	
	# End Control
	if endCtrl:
		
		# Add control shape
		jntShape = glTools.tools.controlBuilder.controlShape(jointList[-1],controlShape,rotate=ctrlRotate,scale=jntLen*ctrlScale)
		# Add joint buffer
		jntGrp = glTools.utils.joint.group(jointList[-1])
		# Tag Control
		glTools.rig.utils.tagCtrl(jointList[-1],ctrlLod)
		# Append arrays
		jointGrps.append(jntGrp)
		jointShape.extend(jntShape)
	
	# =======================
	# - Create Attach Joint -
	# =======================
	
	mc.select(cl=True)
	
	# Attach joint
	attachJoint = mc.joint(n=prefix+'_attachA_jnt')
	attachJointGrp = glTools.utils.joint.group(attachJoint)
	mc.delete(mc.pointConstraint(startJoint,attachJointGrp))
	
	# Attach joint display
	mc.setAttr(attachJoint+'.overrideEnabled',1)
	mc.setAttr(attachJoint+'.overrideLevelOfDetail',1)
	
	# Parent attach joint
	mc.parent(jointGrps[0],attachJoint)
	mc.parent(attachJointGrp,skel_grp)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=jointList[:-1])
	if endCtrl: chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=[jointList[-1]])
	else: chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[jointList[-1]])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=jointGrps)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[attachJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=[attachJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[module,ctrl_grp,rig_grp,skel_grp])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = jointList[:-1]
	if endCtrl: ctrlList.append(jointList[-1])
	
	return [module,attachJoint]