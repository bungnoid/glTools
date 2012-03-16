import maya.cmds as mc

import glTools.tools.faceForward
import glTools.ui.utils

class UserInputError(Exception): pass

def faceForwardUI():
	'''
	'''
	# Window
	win = 'faceForwardUI'
	if mc.window(win,q=True,ex=True): mc.deleteUI(win)
	win = mc.window(win,t='Face Forward')
	
	# Layout
	formLayout = mc.formLayout(numberOfDivisions=100)
	
	# Transform
	transformTFB = mc.textFieldButtonGrp('faceForwardTransformTFB',label='Transform',text='',buttonLabel='Load Selected')
	
	# Axis'
	axisList = ['X','Y','Z','-X','-Y','-Z']
	aimOMG = mc.optionMenuGrp('faceForwardAimOMG',label='Aim Axis')
	for axis in axisList: mc.menuItem(label=axis)
	upOMG = mc.optionMenuGrp('faceForwardUpOMG',label='Up Axis')
	for axis in axisList: mc.menuItem(label=axis)
	
	# Up Vector
	upVecFFG = mc.floatFieldGrp('faceForwardUpVecFFG',label='Up Vector',numberOfFields=3,value1=0.0,value2=1.0,value3=0.0)
	upVecTypeOMG = mc.optionMenuGrp('faceForwardUpVecTypeOMG',label='Up Vector Type')
	for method in ['Current','Vector','Object','ObjectUp']: mc.menuItem(label=method)
	upVecObjTFB = mc.textFieldButtonGrp('faceForwardUpVecObjTFB',label='Up Vector Object',text='',buttonLabel='Load Selected')
	
	# Previous Frame
	prevFrameCBG = mc.checkBoxGrp('faceForwardPrevFrameCBG',label='Prev Frame Velocity',numberOfCheckBoxes=1)
	# Key
	keyframeCBG = mc.checkBoxGrp('faceForwardKeyCBG',label='Set Keyframe',numberOfCheckBoxes=1)
	
	# Buttons
	faceForwardB = mc.button(label='Face Forward',c='glTools.ui.faceForward.faceForwardFromUI()')
	cancelB = mc.button(label='Cancel',c='mc.deleteUI("'+win+'")')
	
	# UI Callbacks
	mc.textFieldButtonGrp(transformTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+transformTFB+'","","transform")')
	mc.textFieldButtonGrp(upVecObjTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+upVecObjTFB+'","","transform")')
	
	# Form Layout - MAIN
	mc.formLayout(formLayout,e=True,af=[(transformTFB,'left',5),(transformTFB,'top',5),(transformTFB,'right',5)])
	mc.formLayout(formLayout,e=True,af=[(aimOMG,'left',5),(aimOMG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(aimOMG,'top',5,transformTFB)])
	mc.formLayout(formLayout,e=True,af=[(upOMG,'left',5),(upOMG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(upOMG,'top',5,aimOMG)])
	mc.formLayout(formLayout,e=True,af=[(upVecFFG,'left',5),(upVecFFG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(upVecFFG,'top',5,upOMG)])
	mc.formLayout(formLayout,e=True,af=[(upVecTypeOMG,'left',5),(upVecTypeOMG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(upVecTypeOMG,'top',5,upVecFFG)])
	mc.formLayout(formLayout,e=True,af=[(upVecObjTFB,'left',5),(upVecObjTFB,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(upVecObjTFB,'top',5,upVecTypeOMG)])
	mc.formLayout(formLayout,e=True,af=[(prevFrameCBG,'left',5),(prevFrameCBG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(prevFrameCBG,'top',5,upVecObjTFB)])
	mc.formLayout(formLayout,e=True,af=[(keyframeCBG,'left',5),(keyframeCBG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(keyframeCBG,'top',5,prevFrameCBG)])
	
	mc.formLayout(formLayout,e=True,af=[(faceForwardB,'right',5),(faceForwardB,'bottom',5)])
	mc.formLayout(formLayout,e=True,ac=[(faceForwardB,'top',5,keyframeCBG)])
	mc.formLayout(formLayout,e=True,ap=[(faceForwardB,'left',5,50)])
	
	mc.formLayout(formLayout,e=True,af=[(cancelB,'left',5),(cancelB,'bottom',5)])
	mc.formLayout(formLayout,e=True,ac=[(cancelB,'top',5,keyframeCBG)])
	mc.formLayout(formLayout,e=True,ap=[(cancelB,'right',5,50)])
	
	# Show Window
	mc.showWindow(win)

def faceForwardFromUI():
	'''
	'''
	pass

def faceForwardAnimUI():
	'''
	'''
	# Window
	win = 'faceForwardAnimUI'
	if mc.window(win,q=True,ex=True): mc.deleteUI(win)
	win = mc.window(win,t='Face Forward Anim')
	
	# Layout
	formLayout = mc.formLayout(numberOfDivisions=100)
	
	# Transform
	transformTFB = mc.textFieldButtonGrp('faceForwardAnimTransformTFB',label='Transform',text='',buttonLabel='Load Selected')
	
	# Axis'
	axisList = ['X','Y','Z','-X','-Y','-Z']
	aimOMG = mc.optionMenuGrp('faceForwardAnimAimOMG',label='Aim Axis')
	for axis in axisList: mc.menuItem(label=axis)
	upOMG = mc.optionMenuGrp('faceForwardAnimUpOMG',label='Up Axis')
	for axis in axisList: mc.menuItem(label=axis)
	
	# Up Vector
	upVecFFG = mc.floatFieldGrp('faceForwardAnimUpVecFFG',label='Up Vector',numberOfFields=3,value1=0.0,value2=1.0,value3=0.0)
	upVecTypeOMG = mc.optionMenuGrp('faceForwardAnimUpVecTypeOMG',label='Up Vector Type')
	for method in ['Current','Vector','Object','ObjectUp']: mc.menuItem(label=method)
	upVecObjTFB = mc.textFieldButtonGrp('faceForwardAnimUpVecObjTFB',label='Up Vector Object',text='',buttonLabel='Load Selected')
	
	# Start / End Frame
	rangeFFG = mc.floatFieldGrp('faceForwardAnimRangeFFG',label='Start/End Frame',numberOfFields=2,value1=-1.0,value2=-1.0)
	
	# Samples
	samplesIFG = mc.intFieldGrp('faceForwardAnimSampleIFG',label='Samples',numberOfFields=1)
	
	# Previous Frame
	prevFrameCBG = mc.checkBoxGrp('faceForwardAnimPrevFrameCBG',label='Prev Frame Velocity',numberOfCheckBoxes=1)
	
	# Buttons
	faceForwardAnimB = mc.button(label='Face Forward',c='glTools.ui.faceForward.faceForwardAnimFromUI()')
	cancelB = mc.button(label='Cancel',c='mc.deleteUI("'+win+'")')
	
	# UI Callbacks
	mc.textFieldButtonGrp(transformTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+transformTFB+'","","transform")')
	mc.textFieldButtonGrp(upVecObjTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+upVecObjTFB+'","","transform")')
	
	# Form Layout - MAIN
	mc.formLayout(formLayout,e=True,af=[(transformTFB,'left',5),(transformTFB,'top',5),(transformTFB,'right',5)])
	mc.formLayout(formLayout,e=True,af=[(aimOMG,'left',5),(aimOMG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(aimOMG,'top',5,transformTFB)])
	mc.formLayout(formLayout,e=True,af=[(upOMG,'left',5),(upOMG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(upOMG,'top',5,aimOMG)])
	mc.formLayout(formLayout,e=True,af=[(upVecFFG,'left',5),(upVecFFG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(upVecFFG,'top',5,upOMG)])
	mc.formLayout(formLayout,e=True,af=[(upVecTypeOMG,'left',5),(upVecTypeOMG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(upVecTypeOMG,'top',5,upVecFFG)])
	mc.formLayout(formLayout,e=True,af=[(upVecObjTFB,'left',5),(upVecObjTFB,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(upVecObjTFB,'top',5,upVecTypeOMG)])
	mc.formLayout(formLayout,e=True,af=[(rangeFFG,'left',5),(rangeFFG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(rangeFFG,'top',5,upVecObjTFB)])
	mc.formLayout(formLayout,e=True,af=[(samplesIFG,'left',5),(samplesIFG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(samplesIFG,'top',5,rangeFFG)])
	mc.formLayout(formLayout,e=True,af=[(prevFrameCBG,'left',5),(prevFrameCBG,'right',5)])
	mc.formLayout(formLayout,e=True,ac=[(prevFrameCBG,'top',5,samplesIFG)])
	
	mc.formLayout(formLayout,e=True,af=[(faceForwardAnimB,'right',5),(faceForwardAnimB,'bottom',5)])
	mc.formLayout(formLayout,e=True,ac=[(faceForwardAnimB,'top',5,prevFrameCBG)])
	mc.formLayout(formLayout,e=True,ap=[(faceForwardAnimB,'left',5,50)])
	
	mc.formLayout(formLayout,e=True,af=[(cancelB,'left',5),(cancelB,'bottom',5)])
	mc.formLayout(formLayout,e=True,ac=[(cancelB,'top',5,prevFrameCBG)])
	mc.formLayout(formLayout,e=True,ap=[(cancelB,'right',5,50)])
	
	# Show Window
	mc.showWindow(win)

def faceForwardAnimFromUI():
	'''
	'''
	pass
