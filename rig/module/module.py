import maya.cmds as mc

import glRig.rig.ctrl
import glRig.rig.channelState

class Module(object):
	
	def __init__(self):
		'''
		'''
		# Initialize Control Builder
		self.ctrlBuilder = glRig.rig.ctrl.ControlBuilder()
		self.channelState = glRig.rig.channelState.ChannelState()
	
	def build(all,prefix):
		'''
		'''
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
		module = mc.group([ctrl_grp,rig_grp,skel_grp],n=prefix+'_module')
		
		# Parent Module
		if mc.objExists(all+'|modules'): mc.parent(module,all+'|modules')
		
		# ======================
		# - Build Attach Joint -
		# ======================
		
		mc.select(cl=True)
	
		# Attach joint
		attachJoint = mc.joint(n=prefix+'_attachA_jnt')
		attachJointGrp = glRig.utils.joint.group(attachJoint)
		
		# Attach joint display
		mc.setAttr(attachJoint+'.overrideEnabled',1)
		mc.setAttr(attachJoint+'.overrideLevelOfDetail',1)
		
		# Parent to attach joint
		mc.parent(attachJointGrp,skel_grp)
		
		# =================
		# - Return Result -
		# =================
		
		self.result = {}
		self.result['module'] = module
		self.result['ctrlGrp'] = ctrl_grp
		self.result['rigGrp'] = rig_grp
		self.result['skelGrp'] = skel_grp
		self.result['attachJoint'] = skel_grp
		
		return self.result