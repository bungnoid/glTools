import maya.cmds as mc

import glTools.utils.channelState
import glTools.utils.curve

def build(startJoint,endJoint,upperLimbJoints,lowerLimbJoint,limbModule,prefix):
	'''
	Build spline based limb deform module
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(startJoint): raise Exception('Start joint "'+startJoint+'" does not exist!')
	if not mc.objExists(endJoint): raise Exception('End joint "'+endJoint+'" does not exist!')
	for limbJoint in upperLimbJoints:
		if not mc.objExists(limbJoint): raise Exception('Limb joint "'+limbJoint+'" does not exist!')
	for limbJoint in lowerLimbJoint:
		if not mc.objExists(limbJoint): raise Exception('Limb joint "'+limbJoint+'" does not exist!')
	if not mc.objExists(module): raise Exception('Module "'+module+'" does not exist!')
	
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
	
	# =============================
	# - Create Limb Deform Joints -
	# =============================
	
	