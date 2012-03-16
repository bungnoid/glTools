import maya.cmds as mc

import glTools.ui.utils
import glTools.utils.lidSurface

class UIError(Exception): pass

# LidSurface Create ===============

def lidSurfaceCreateUI():
	'''
	LidSurface Create UI
	'''
	# Create Window
	win = 'lidSurfaceCreateUI'
	if mc.window(win,q=True,ex=True): mc.deleteUI(win)
	win = mc.window(win,t='Create LidSurface')
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# Curve List
	crvListTXT = mc.text(l='Curve List')
	crvListTSL = mc.textScrollList('lidSurface_crvListTSL',ams=True)
	crvListAddB = mc.button(l='Add',c='glTools.ui.utils.addToTSL("'+crvListTSL+'")')
	crvListRemB = mc.button(l='Remove',c='glTools.ui.utils.removeFromTSL("'+crvListTSL+'")')
	
	# Prefix
	prefixTFG = mc.textFieldGrp('lidSurface_prefixTFG',l='Prefix',tx='')
	# Side
	sideTFG = mc.textFieldGrp('lidSurface_sideTFG',l='Side',tx='lf')
	
	# Spans
	spansFSG = mc.intSliderGrp('lidSurface_spansFSG',label='Spans',field=True,minValue=2,maxValue=10,fieldMinValue=0,fieldMaxValue=100,value=4)
	
	# Attribute Object
	attrObjTFB = mc.textFieldButtonGrp('lidSurface_attrObjTFB',l='Attribute Object',bl='Load Sel')
	# Collision Object
	collObjTFB = mc.textFieldButtonGrp('lidSurface_collObjTFB',l='Collision Object',bl='Load Sel')
	
	# Create / Close
	createB = mc.button(l='Create',c='')
	closeB = mc.button(l='Close',c='mc.deleteUI("'+win+'")')
	
	# UI Callbacks
	mc.textScrollList(crvListTSL,e=True,dkc='glTools.ui.utils.removeFromTSL("'+crvListTSL+'")')
	mc.textFieldGrp(prefixTFG,e=True,cc='glTools.ui.lidSurface.lidSurfaceCreate_updateSide()')
	mc.textFieldButtonGrp(attrObjTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+attrObjTFB+'")')
	mc.textFieldButtonGrp(collObjTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+collObjTFB+'")')
	
	# FormLayout - MAIN
	mc.formLayout(FL,e=True,af=[(crvListTXT,'left',5),(crvListTXT,'top',5)],ap=[(crvListTXT,'right',5,30)])
	mc.formLayout(FL,e=True,af=[(crvListRemB,'left',5),(crvListRemB,'bottom',5)],ap=[(crvListRemB,'right',5,30)])
	mc.formLayout(FL,e=True,af=[(crvListAddB,'left',5)],ap=[(crvListAddB,'right',5,30)],ac=[(crvListAddB,'bottom',5,crvListRemB)])
	mc.formLayout(FL,e=True,af=[(crvListTSL,'left',5)],ap=[(crvListTSL,'right',5,30)],ac=[(crvListTSL,'top',5,crvListTXT),(crvListTSL,'bottom',5,crvListAddB)])
	mc.formLayout(FL,e=True,af=[(prefixTFG,'right',5),(prefixTFG,'top',5)],ap=[(prefixTFG,'left',5,30)])
	mc.formLayout(FL,e=True,af=[(sideTFG,'right',5)],ap=[(sideTFG,'left',5,30)],ac=[(sideTFG,'top',5,prefixTFG)])
	mc.formLayout(FL,e=True,af=[(spansFSG,'right',5)],ap=[(spansFSG,'left',5,30)],ac=[(spansFSG,'top',5,sideTFG)])
	mc.formLayout(FL,e=True,af=[(attrObjTFB,'right',5)],ap=[(attrObjTFB,'left',5,30)],ac=[(attrObjTFB,'top',5,spansFSG)])
	mc.formLayout(FL,e=True,af=[(collObjTFB,'right',5)],ap=[(collObjTFB,'left',5,30)],ac=[(collObjTFB,'top',5,attrObjTFB)])
	mc.formLayout(FL,e=True,af=[(closeB,'right',5),(closeB,'bottom',5)],ap=[(closeB,'left',5,30)])
	mc.formLayout(FL,e=True,af=[(createB,'right',5)],ap=[(createB,'left',5,30)],ac=[(createB,'bottom',5,closeB)])
	
	# Show Window
	mc.showWindow(win)

def lidSurfaceCreateFromUI():
	'''
	'''
	# Check window
	win = 'lidSurfaceCreateUI'
	if mc.window(win,q=True,ex=True): raise UIError('LidSurface Create UI does not exist!')
	
	# Get UI values
	crvList = mc.textScrollList('lidSurface_crvListTSL',q=True,ai=True)
	spans = mc.intSliderGrp('lidSurface_spansFSG',q=True,v=True)
	attrObj = mc.textFieldButtonGrp('lidSurface_attrObjTFB',q=True,tx=True)
	collObj = mc.textFieldButtonGrp('lidSurface_collObjTFB',q=True,tx=True)
	side = mc.textFieldGrp('lidSurface_sideTFG',q=True,tx=True)
	prefix = mc.textFieldGrp('lidSurface_prefixTFG',q=True,tx=True)
	
	# Execute command
	glTools.utils.lidSurface.lidSurface_create(curveList=crvList,spans=spans,attributeObject=attrObj,collisionObject=collObj,side=side,prefix=prefix)

def lidSurfaceCreate_updateSide():
	'''
	LidSurface Create UI method
	Updates the side text field based on updates to the prefix text field
	'''
	prefix = mc.textFieldGrp('lidSurface_prefixTFG',q=True,tx=True)
	if prefix:
		side = prefix.split('_')[0]
		if side:
			mc.textFieldGrp('lidSurface_sideTFG',e=True,tx=side)

# LidSurface 3 Control Setup ===============

def threeCtrlSetupUI():
	'''
	'''
	pass

def threeCtrlSetupFromUI():
	'''
	'''
	pass

# LidSurface 4 Control Setup ===============

def fourCtrlSetupUI():
	'''
	'''
	pass

def fourCtrlSetupFromUI():
	'''
	'''
	pass

