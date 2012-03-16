import maya.cmds as mc

import glTools.utils.channelState

import glTools.tools.ikHandle
import glTools.tools.stretchyIkChain

def build(startJoint,endJoint,clavOrient='',ctrlRotate=(0,0,0),prefix=''):
	'''
	@param startJoint: Clavicle start joint
	@type startJoint: str
	@param endJoint: Clavicle end joint
	@type endJoint: str
	@param scaleAttr: Global character scale attribute
	@type scaleAttr: str
	@param clavOrient: Clavicle orient transform
	@type clavOrient: str
	@param clavOrient: Rotate clavicle control shape
	@type clavOrient: list or tuple
	@param prefix: Name prefix for new nodes
	@type prefix: str
	'''
	
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(startJoint):
		raise Exception('Start joint "'+startJoint+'" does not exist!')
	if not mc.objExists(endJoint):
		raise Exception('End joint "'+endJoint+'" does not exist!')
	if clavOrient and not mc.objExists(clavOrient):
		raise Exception('Clavicle orient transform "'+clavOrient+'" does not exist!')
	
	# ======================
	# - Configure Clavicle -
	# ======================
	
	scaleAxis = 'x'
	
	rotateCtrlScale = 0.5
	transCtrlScale = 0.2
	
	blendAttr = 'stretchToControl'
	
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
	
	# =======================
	# - Create Attach Joint -
	# =======================
	
	mc.select(cl=True)
	
	# Attach joint
	attachJoint = mc.joint(n=prefix+'_attachA_jnt')
	attachJointGrp = glTools.utils.joint.group(attachJoint)
	
	# Attach joint display
	mc.setAttr(attachJoint+'.overrideEnabled',1)
	mc.setAttr(attachJoint+'.overrideLevelOfDetail',1)
	
	# Parent Attach Joint
	mc.parent(attachJointGrp,skel_grp)
	
	# =========================
	# - Create Clavicle Joint -
	# =========================
	
	# Add start joint buffer
	startJointGrp = glTools.utils.joint.group(startJoint)
	mc.delete(mc.pointConstraint(startJointGrp,attachJointGrp))
	mc.parentConstraint(attachJoint,ctrl_grp,mo=True)
	mc.parent(startJointGrp,attachJoint)
	
	# ===================
	# - Create Controls -
	# ===================
	
	# Initialize control builder
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	# Calculate joint length
	jntLen = glTools.utils.joint.length(startJoint)
	
	# Rotate control
	clavRotateCtrl = mc.group(em=True,n=prefix+'_rot_ctrl')
	if clavOrient: mc.delete(mc.orientConstraint(clavOrient,clavRotateCtrl))
	clavRotateCtrlShape = glTools.tools.controlBuilder.controlShape(clavRotateCtrl,'anchor',rotate=ctrlRotate,scale=jntLen*rotateCtrlScale,orient=False)
	clavRotateCtrlGrp = glTools.utils.base.group(clavRotateCtrl,name=prefix+'_rot_ctrlGrp')
	glTools.rig.utils.tagCtrl(clavRotateCtrl,'primary')
	
	# Translate control
	clavTransCtrl = ctrlBuilder.create('box',prefix+'_trans_ctrl',scale=jntLen*transCtrlScale)
	clavTransCtrlGrp = glTools.utils.base.group(clavTransCtrl,name=prefix+'_trans_ctrlGrp')
	glTools.rig.utils.tagCtrl(clavTransCtrl,'primary')
	
	# Position Controls
	pt = glTools.utils.base.getPosition(startJoint)
	mc.move(pt[0],pt[1],pt[2],clavRotateCtrlGrp,ws=True,a=True)
	pt = glTools.utils.base.getPosition(endJoint)
	mc.move(pt[0],pt[1],pt[2],clavTransCtrlGrp,ws=True,a=True)
	
	# Parent Controls
	mc.parent(clavTransCtrlGrp,clavRotateCtrl)
	mc.parent(clavRotateCtrlGrp,ctrl_grp)
	
	# Constrain to Control
	mc.pointConstraint(clavRotateCtrl,startJoint)
	
	# =====================
	# - Build Clavicle IK -
	# =====================
	
	# Create ikHandle
	clavIk = glTools.tools.ikHandle.build(startJoint,endJoint,solver='ikSCsolver',prefix=prefix)
	
	# Parent ikHandle
	clavIkGrp = glTools.utils.base.group(clavIk,name=prefix+'_ikHandle_grp')
	mc.parent(clavIkGrp,clavTransCtrl)
	mc.setAttr(clavIkGrp+'.v',0)
	
	# Create stretchy IK
	clavStretch = glTools.tools.stretchyIkChain.build(clavIk,scaleAxis=scaleAxis,scaleAttr=module+'.uniformScale',blendControl=clavTransCtrl,blendAttr=blendAttr,shrink=True,prefix=prefix)
	mc.setAttr(clavTransCtrl+'.'+blendAttr,0.0)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([0,0,0,0,0,0,2,2,2,1],objectList=[clavRotateCtrl])
	chStateUtil.setFlags([0,0,0,2,2,2,2,2,2,1],objectList=[clavTransCtrl])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[clavRotateCtrlGrp,clavTransCtrlGrp])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[clavIk,clavIkGrp])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[endJoint,startJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,2,2,1],objectList=[startJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[attachJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=[attachJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[module,ctrl_grp,rig_grp,skel_grp])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = [clavRotateCtrl,clavTransCtrl]
	
	return [module,attachJoint]