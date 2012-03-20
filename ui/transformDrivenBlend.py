import maya.cmds as mc

import glTools.tools.transformDrivenBlend
import glTools.ui.utils

def create():
	'''
	'''
	# Window
	window = 'transformDrivenBlendUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Transform Driven Blend',s=False)
	
	# Layout
	cl = mc.columnLayout()
	
	# UI Elements
	driveAttrTFG = mc.textFieldGrp('tdb_driveAttrTFG',label='Drive Attr', text='')
	blendShapeTFG = mc.textFieldGrp('tdb_blendShapeTFG',label='BlendShape', text='')
	target1TFG = mc.textFieldGrp('tdb_target1TFG',label='Target 1', text='',cc='glTools.ui.transformDrivenBlend.refreshUI()')
	target2TFG = mc.textFieldGrp('tdb_target2TFG',label='Target 2', text='',cc='glTools.ui.transformDrivenBlend.refreshUI()')
	weight1FFG = mc.floatFieldGrp('tdb_weight1FFG',numberOfFields=1,label='MinValue(1)',v1=1.0)
	weight2FFG = mc.floatFieldGrp('tdb_weight2FFG',numberOfFields=1,label='MaxValue(2)',v1=-1.0)
	overlapFFG = mc.floatFieldGrp('tdb_overlapFFG',numberOfFields=1,label='Overlap',v1=0.0)
	prefixTFG = mc.textFieldGrp('tdb_prefixTFG',label='Prefix', text='')
	createB = mc.button('tdb_createB',label='Create',c='glTools.ui.transformDrivenBlend.executeFromUI()',w=380)
	refreshB = mc.button('tdb_refreshB',label='Refresh',c='glTools.ui.transformDrivenBlend.refreshUI()',w=380)
	cancelB = mc.button('tdb_cancelB',label='Cancel',c='mc.deleteUI("'+window+'")',w=380)
	
	# Popup Menus
	mc.popupMenu('tdb_blendShapePUM',p=blendShapeTFG)
	mc.popupMenu('tdb_target1PUM',p=target1TFG)
	mc.popupMenu('tdb_target2PUM',p=target2TFG)
	mc.popupMenu('tdb_driveAttrPUM',p=driveAttrTFG)
	mc.menuItem(label='Set from selected',c='glTools.ui.utils.loadChannelBoxSel("'+driveAttrTFG+'")')
	
	# Show Window
	refreshUI()
	mc.window(window,e=True,w=388,h=270)
	mc.showWindow(window)
	
def refreshUI():
	'''
	'''
	# Get UI input values
	blendShape = mc.textFieldGrp('tdb_blendShapeTFG',q=True,text=True)
	target1 = mc.textFieldGrp('tdb_target1TFG',q=True,text=True)
	target2 = mc.textFieldGrp('tdb_target1TFG',q=True,text=True)
	
	print blendShape
	print target1
	print target2
	
	# Update blendShape menu list
	blendShapeList = mc.ls(type='blendShape')
	mc.popupMenu('tdb_blendShapePUM',e=True,deleteAllItems=True)
	mc.setParent('tdb_blendShapePUM',m=True)
	for item in blendShapeList:
		mc.menuItem(label=item,c='mc.textFieldGrp("tdb_blendShapeTFG",e=True,text="'+item+'");glTools.ui.transformDrivenBlend.refreshUI()')
	
	# Check BlendShape
	if blendShape and mc.objExists(blendShape) and (mc.objectType(blendShape) == 'blendShape'):
		targetList = mc.listAttr(blendShape+'.w',m=True)
		
		print targetList
		
		mc.popupMenu('tdb_target1PUM',e=True,deleteAllItems=True)
		mc.popupMenu('tdb_target2PUM',e=True,deleteAllItems=True)
		for target in targetList:
			targetCon = mc.listConnections(blendShape+'.'+target,s=True,d=False)
			if target == target1: targetCon = True
			if target == target2: targetCon = True
			mc.setParent('tdb_target1PUM',m=True)
			mc.menuItem(label=target,c='mc.textFieldGrp("tdb_target1TFG",e=True,text="'+target+'");glTools.ui.transformDrivenBlend.refreshUI()',en=not bool(targetCon))
			mc.setParent('tdb_target2PUM',m=True)
			mc.menuItem(label=target,c='mc.textFieldGrp("tdb_target2TFG",e=True,text="'+target+'");glTools.ui.transformDrivenBlend.refreshUI()',en=not bool(targetCon))
			
def executeFromUI():
	'''
	'''
	# Set Default Values 
	minValue = 0.0
	maxValue = 1.0
	
	# Get UI input values
	driveAttr = mc.textFieldGrp('tdb_driveAttrTFG',q=True,text=True)
	blendShape = mc.textFieldGrp('tdb_blendShapeTFG',q=True,text=True)
	target1 = mc.textFieldGrp('tdb_target1TFG',q=True,text=True)
	target2 = mc.textFieldGrp('tdb_target2TFG',q=True,text=True)
	weight1 = mc.floatFieldGrp('tdb_weight1FFG',q=True,v1=True)
	weight2 = mc.floatFieldGrp('tdb_weight2FFG',q=True,v1=True)
	overlap = mc.floatFieldGrp('tdb_overlapFFG',q=True,v1=True)
	prefix = mc.textFieldGrp('tdb_prefixTFG',q=True,text=True)
	
	# Check Arguments
	if not blendShape: raise Exception('No blendShape specified!')
	if not target1: raise Exception('Target 1 not specified!')
	minValue = weight1
	maxValue = weight2
	
	# Execute Command
	if target1 and target2:
		glTools.tools.transformDrivenBlend.drive2Shapes(blendShape,target1,target2,driveAttr,minValue,maxValue,overlap,prefix)
	else:
		glTools.tools.transformDrivenBlend.driveShape(blendShape,target1,driveAttr,minValue,maxValue,prefix)
