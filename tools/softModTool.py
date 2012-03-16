import maya.cmds as mc

import glTools.tools.controlBuilder

def create(geo,prefix=''):
	'''
	'''
	# Check prefix
	if not prefix: prefix = geo
	
	# Create Deformer
	sMod = mc.softMod(geo,n=prefix+'_softMod')
	sModHandle = sMod[1]
	sMod = sMod[0]
	sModBase = mc.duplicate(sModHandle,po=True,n=prefix+'_softModBase')[0]
	
	# Get Handle pivot
	piv = mc.xform(sModHandle,q=True,ws=True,rp=True)
	
	# Create Base control
	base_grp = mc.createNode('transform',n=prefix+'_softModBase_grp')
	base_ctrl = mc.createNode('transform',n=prefix+'_softModBase_ctrl',p=base_grp)
	base_ctrlShape = glTools.tools.controlBuilder.controlShape(base_ctrl,'box',scale=2)
	
	# Create Offset control
	offset_grp = mc.createNode('transform',n=prefix+'_softModOffset_grp',p=base_ctrl)
	offset_ctrl = mc.createNode('transform',n=prefix+'_softModOffset_ctrl',p=offset_grp)
	offset_ctrlShape = glTools.tools.controlBuilder.controlShape(offset_ctrl,'sphere',scale=0.25)
	
	# Create Falloff control
	falloff_grp = mc.createNode('transform',n=prefix+'_softModFalloff_grp',p=base_ctrl)
	falloff_ctrl = mc.createNode('transform',n=prefix+'_softModFalloff_ctrl',p=falloff_grp)
	falloff_ctrlShape = glTools.tools.controlBuilder.controlShape(falloff_ctrl,'circle',scale=1)
	falloff_loc = mc.spaceLocator(n=prefix+'_softModFalloff_loc')[0]
	mc.parent(falloff_loc,falloff_ctrl)
	mc.addAttr(falloff_ctrl,ln='radius',min=0.001,dv=1,k=True)
	mc.setAttr(falloff_loc+'.v',0)
	
	# Move hierarchy into place
	mc.move(piv[0],piv[1],piv[2],base_grp,a=True)
	
	# Connect to deformer
	mc.connectAttr(falloff_loc+'.worldPosition[0]',sMod+'.falloffCenter',f=True)
	mc.connectAttr(falloff_ctrl+'.radius',sMod+'.falloffRadius',f=True)
	mc.connectAttr(sModBase+'.worldInverseMatrix[0]',sMod+'.bindPreMatrix',f=True)
	
	# Parent and constrain softMod elements
	mc.parentConstraint(offset_ctrl,sModHandle,mo=True)
	mc.scaleConstraint(offset_ctrl,sModHandle,mo=True)
	mc.parentConstraint(base_ctrl,sModBase,mo=True)
	mc.scaleConstraint(base_ctrl,sModBase,mo=True)
	mc.parent(sModHandle,sModBase)
	mc.parent(sModBase,base_grp)
	
	# Return result
	return sMod
