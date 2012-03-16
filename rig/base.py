import maya.cmds as mc

import glTools.utils.base
import glTools.utils.channelState
import glTools.tools.controlBuilder

import glTools.rig.utils

def build(char,root,cn_config=True,lf_config=True,rt_config=True):
	'''
	Build generic base rig structure
	@param char: Character name
	@type char: str
	@param root: Character root locator or joint
	@type root: str
	@param cn_config: Create a center character configuration control
	@type cn_config: bool
	@param lf_config: Create a left character configuration control
	@type lf_config: bool
	@param rt_config: Create a right character configuration control
	@type rt_config: bool
	'''
	# Check Root
	if not mc.objExists(root): raise Exception('Root object "'+root+'" does not exist!')
	
	# Initialize Control Builder
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	# Determine Character Scale
	rootPt = glTools.utils.base.getPosition(root)
	charScale = rootPt[1]
	
	# ============
	# - All Node -
	# ============
	
	all = mc.createNode('transform',n='all')
	
	# =====================
	# - AllTrans Controls -
	# =====================
	
	allTransA = mc.createNode('transform',n='allTransA_ctrl',p=all)
	allTransB = mc.createNode('transform',n='allTransB_ctrl',p=allTransA)
	allTransC = mc.createNode('transform',n='allTransC_ctrl',p=allTransB)
	allTransD = mc.createNode('transform',n='allTransD_ctrl',p=allTransC)
	allTransE = mc.createNode('transform',n='allTransE_ctrl',p=allTransD)
	
	# - Control Shapes -
	glTools.tools.controlBuilder.controlShape(allTransA,'circle',rotate=(-90,0,0),scale=charScale*2)
	textCrvs = glTools.tools.controlBuilder.controlShape(allTransA,'text',text=char,translate=(0,0,charScale*1.25),rotate=(-90,0,0),scale=charScale*1.5)
	for crv in textCrvs: mc.setAttr(crv+'.template',1)
	
	# Tag controls
	for allTransCtrl in [allTransA,allTransB,allTransC,allTransD,allTransE]:
		glTools.rig.utils.tagCtrl(allTransCtrl,'primary')
	
	# - AllTrans Attrs -
	
	# Char
	mc.addAttr(allTransA,ln='char',at='enum',en=char+':',k=True)
	mc.setAttr(allTransA+'.char',l=True)
	
	# Uniform Scale
	mc.addAttr(allTransA,ln='uniformScale',min=0.001,dv=1.0,k=True)
	mc.connectAttr(allTransA+'.uniformScale',allTransA+'.scaleX',f=True)
	mc.connectAttr(allTransA+'.uniformScale',allTransA+'.scaleY',f=True)
	mc.connectAttr(allTransA+'.uniformScale',allTransA+'.scaleZ',f=True)
	
	# Ctrl Vis
	mc.addAttr(allTransA,ln='primaryCtrlVis',at='enum',en='Off:On:',k=True)
	mc.setAttr(allTransA+'.primaryCtrlVis',1)
	mc.addAttr(allTransA,ln='secondaryCtrlVis',at='enum',en='Off:On:',k=True)
	mc.setAttr(allTransA+'.secondaryCtrlVis',1)
	mc.addAttr(allTransA,ln='tertiaryCtrlVis',at='enum',en='Off:On:',k=True)
	mc.setAttr(allTransA+'.tertiaryCtrlVis',1)
	
	# Geometry Vis
	mc.addAttr(allTransA,ln='loGeoVis',at='enum',en='Off:On:',k=True)
	mc.setAttr(allTransA+'.loGeoVis',0)
	mc.addAttr(allTransA,ln='hiGeoVis',at='enum',en='Off:On:',k=True)
	mc.setAttr(allTransA+'.hiGeoVis',0)
	
	# ================
	# - Body Control -
	# ================
	
	bodyCtrlGrp = mc.createNode('transform',n='body_ctrlGrp',p=allTransE)
	bodyCtrl = mc.createNode('transform',n='cn_body_ctrl',p=bodyCtrlGrp)
	glTools.tools.controlBuilder.controlShape(bodyCtrl,'teardrop',rotate=(90,0,0),scale=charScale*1.5)
	glTools.rig.utils.tagCtrl(bodyCtrl,'primary')
	
	mc.delete(mc.pointConstraint(root,bodyCtrlGrp))
	mc.parent(root,bodyCtrl)
	
	# ===================
	# - Config Controls -
	# ===================
	
	config_grp = mc.createNode('transform',n='config_grp',p=allTransA)
	mc.parentConstraint(allTransA,config_grp)
	
	# Center
	if cn_config:
		cnConfigCtrl = ctrlBuilder.create('circle','cn_config_ctrl',rotate=(-90,0,0),scale=charScale*.3)
		glTools.tools.controlBuilder.controlShape(cnConfigCtrl,'text',text='C',rotate=(-90,0,0),scale=charScale*0.2)
		glTools.rig.utils.tagCtrl(cnConfigCtrl,'primary')
		cnConfigCtrlGrp = glTools.utils.base.group(cnConfigCtrl,cnConfigCtrl+'Grp')
		mc.move(0,0,-.65*charScale,cnConfigCtrlGrp,ws=True,a=True)
		mc.parent(cnConfigCtrlGrp,config_grp)
	
	# Left
	if lf_config:
		lfConfigCtrl = ctrlBuilder.create('circle','lf_config_ctrl',rotate=(-90,0,0),scale=charScale*.3)
		glTools.tools.controlBuilder.controlShape(lfConfigCtrl,'text',text='L',rotate=(-90,0,0),scale=charScale*0.2)
		glTools.rig.utils.tagCtrl(lfConfigCtrl,'primary')
		lfConfigCtrlGrp = glTools.utils.base.group(lfConfigCtrl,lfConfigCtrl+'Grp')
		mc.move(.65*charScale,0,0,lfConfigCtrlGrp,ws=True,a=True)
		mc.parent(lfConfigCtrlGrp,config_grp)
	
	# Right
	if rt_config:
		rtConfigCtrl = ctrlBuilder.create('circle','rt_config_ctrl',rotate=(-90,0,0),scale=charScale*.3)
		glTools.tools.controlBuilder.controlShape(rtConfigCtrl,'text',text='R',rotate=(-90,0,0),scale=charScale*0.2)
		glTools.rig.utils.tagCtrl(rtConfigCtrl,'primary')
		rtConfigCtrlGrp = glTools.utils.base.group(rtConfigCtrl,rtConfigCtrl+'Grp')
		mc.move(-.65*charScale,0,0,rtConfigCtrlGrp,ws=True,a=True)
		mc.parent(rtConfigCtrlGrp,config_grp)
	
	# =================
	# - Modules Group -
	# =================
	
	module_grp = mc.createNode('transform',n='module_grp',p=all)
	
	# =====================
	# - Control List Attr -
	# =====================
	
	# Build Control List
	ctrlList = [allTransA,allTransB,allTransC,allTransD,allTransE]
	if cn_config: ctrlList.append(cnConfigCtrl)
	if lf_config: ctrlList.append(lfConfigCtrl)
	if rt_config: ctrlList.append(rtConfigCtrl)
	ctrlList.append(bodyCtrl)
	
	# Set Control List
	glTools.rig.utils.setAllCtrls(all,ctrlList)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[all])
	chStateUtil.setFlags([0,0,0,0,0,0,2,2,2,1],objectList=[allTransA,allTransB,allTransC,allTransD,allTransE])
	chStateUtil.setFlags([0,0,0,0,0,0,2,2,2,1],objectList=[bodyCtrl])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[bodyCtrlGrp])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[root])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[config_grp])
	if cn_config: chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[cnConfigCtrl])
	if lf_config: chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[lfConfigCtrl])
	if rt_config: chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[rtConfigCtrl])
	
	# =================
	# - Return Result -
	# =================
	
	return [all,module_grp,ctrlList]
