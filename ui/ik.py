import maya.cmds as mc

import glTools.ui.utils
import glTools.utils.ik
import glTools.tools.ikHandle
import glTools.builder.stretchyIkChain
import glTools.builder.stretchyIkLimb
import glTools.builder.stretchyIkSpline_parametric
import glTools.builder.stretchyIkSpline_arcLength

class UserInputError(Exception): pass
class UIError(Exception): pass

# IK Handle --

def ikHandleUI():
	'''
	UI for ikHandle()
	'''
	# Window
	window = 'ikHandleUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Create IK Handle')
	# Layout
	FL = mc.formLayout()
	# UI Elements
	#---
	# Joints
	sJointTFB = mc.textFieldButtonGrp('ikHandleStartJointTFB',label='Start Joint',text='',buttonLabel='Load Selected')
	eJointTFB = mc.textFieldButtonGrp('ikHandleEndJointTFB',label='End Joint',text='',buttonLabel='Load Selected')
	# Prefix
	prefixTFG = mc.textFieldGrp('ikHandlePrefixTFG',label='Prefix', text='')
	
	# IK Solver
	solverList = ['ikSplineSolver','ikSCsolver','ikRPsolver','ik2Bsolver']
	solverOMG = mc.optionMenuGrp('ikHandleSolverOMG',label='IK Solver')
	for solver in solverList: mc.menuItem(label=solver)
	mc.optionMenuGrp(solverOMG,e=True,sl=3)
	
	# Spline IK
	splineFrameL = mc.frameLayout('ikHandleSplineFL',l='Spline IK Options',cll=0,en=0)
	splineFormL = mc.formLayout(numberOfDivisions=100)
	# Curve
	curveTFB = mc.textFieldButtonGrp('ikHandleCurveTFB',label='Curve',text='',buttonLabel='Load Selected',en=0)
	offsetFSG = mc.floatSliderGrp('ikHandleOffsetFSG',label='Offset',field=True,minValue=0.0,maxValue=1.0,fieldMinValue=0.0,fieldMaxValue=1.0,value=0,en=0)
	
	mc.setParent('..')
	mc.setParent('..')
	
	# Buttons
	createB = mc.button('ikHandleCreateB',l='Create',c='glTools.ui.ik.ikHandleFromUI(False)')
	cancelB = mc.button('ikHandleCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# UI callback commands
	mc.optionMenuGrp(solverOMG,e=True,cc='mc.frameLayout("'+splineFrameL+'",e=True,en=not(mc.optionMenuGrp("'+solverOMG+'",q=True,sl=True)-1))')
	mc.textFieldButtonGrp(sJointTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+sJointTFB+'","'+prefixTFG+'",selType="joint")')
	mc.textFieldButtonGrp(eJointTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+eJointTFB+'",selType="joint")')
	mc.textFieldButtonGrp(curveTFB,e=True,bc='glTools.ui.utils.loadCurveSel("'+curveTFB+'")')
	
	# Form Layout - MAIM
	mc.formLayout(FL,e=True,af=[(sJointTFB,'top',5),(sJointTFB,'left',5),(sJointTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(eJointTFB,'top',5,sJointTFB)])
	mc.formLayout(FL,e=True,af=[(eJointTFB,'left',5),(eJointTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(prefixTFG,'top',5,eJointTFB)])
	mc.formLayout(FL,e=True,af=[(prefixTFG,'left',5),(prefixTFG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(solverOMG,'top',5,prefixTFG)])
	mc.formLayout(FL,e=True,af=[(solverOMG,'left',5),(solverOMG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(splineFrameL,'top',5,solverOMG)])
	mc.formLayout(FL,e=True,af=[(splineFrameL,'left',5),(splineFrameL,'right',5)])
	mc.formLayout(FL,e=True,ac=[(splineFrameL,'bottom',5,createB)])
	mc.formLayout(FL,e=True,af=[(createB,'left',5),(createB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(createB,'bottom',5,cancelB)])
	mc.formLayout(FL,e=True,af=[(cancelB,'left',5),(cancelB,'right',5),(cancelB,'bottom',5)])
	
	# Form Layout - Spline
	mc.formLayout(splineFormL,e=True,af=[(curveTFB,'top',5),(curveTFB,'left',5),(curveTFB,'right',5)])
	mc.formLayout(splineFormL,e=True,ac=[(offsetFSG,'top',5,curveTFB)])
	mc.formLayout(splineFormL,e=True,af=[(offsetFSG,'left',5),(offsetFSG,'right',5)])
	
	# Show Window
	mc.showWindow(window)

def ikHandleFromUI(close=False):
	'''
	Execute ikHandle() from UI
	'''
	# Window
	window = 'ikHandleUI'
	if not mc.window(window,q=True,ex=1): raise UIError('IkHandle UI does not exist!!')
	
	# Get UI data
	startJ = mc.textFieldButtonGrp('ikHandleStartJointTFB',q=True,text=True)
	endJ = mc.textFieldButtonGrp('ikHandleEndJointTFB',q=True,text=True)
	pre = mc.textFieldGrp('ikHandlePrefixTFG',q=True,text=True)
	solver = mc.optionMenuGrp('ikHandleSolverOMG',q=True,v=True)
	curve = mc.textFieldButtonGrp('ikHandleCurveTFB',q=True,text=True)
	offset = mc.floatSliderGrp('ikHandleOffsetFSG',q=True,v=True)
	
	# Execute command
	glTools.tools.ikHandle.build(startJoint=startJ,endJoint=endJ,solver=solver,curve=curve,ikSplineOffset=offset,prefix=pre)
	
	# Cleanup
	if close: mc.deleteUI(window)

# Stretchy IK Chain --

def stretchyIkChainUI():
	'''
	UI for stretchyIkChain()
	'''
	# Window
	window = 'stretchyIkChainUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Stretchy IK Chain')
	# Layout
	FL = mc.formLayout()
	# UI Elements
	#---
	# IK Handle
	handleTFB = mc.textFieldButtonGrp('stretchyIkChainTFB',label='IK Handle',text='',buttonLabel='Load Selected')
	# Prefix
	prefixTFG = mc.textFieldGrp('stretchyIkChainPrefixTFG',label='Prefix', text='')
	# Shrink
	shrinkCBG = mc.checkBoxGrp('stretchyIkChainShrinkCBG',l='Shrink',ncb=1,v1=False)
	# Scale Axis
	axisList = ['X','Y','Z']
	scaleAxisOMG = mc.optionMenuGrp('stretchyIkChainAxisOMG',label='Joint Scale Axis')
	for axis in axisList: mc.menuItem(label=axis)
	mc.optionMenuGrp(scaleAxisOMG,e=True,sl=1)
	# Scale Attr
	scaleAttrTFB = mc.textFieldButtonGrp('stretchyIkChainScaleAttrTFB',label='Scale Attribute',text='',buttonLabel='Load Selected')
	# Blend
	blendCtrlTFB = mc.textFieldButtonGrp('stretchyIkChainBlendCtrlTFB',label='Blend Control',text='',buttonLabel='Load Selected')
	blendAttrTFG = mc.textFieldGrp('stretchyIkChainBlendAttrTFB',label='Blend Attribute',text='stretchScale')
	
	# Separator
	SEP = mc.separator(height=10,style='single')
	
	# Buttons
	createB = mc.button('stretchyIkChainCreateB',l='Create',c='glTools.ui.ik.stretchyIkChainFromUI(False)')
	cancelB = mc.button('stretchyIkChainCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# UI callback commands
	mc.textFieldButtonGrp(handleTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+handleTFB+'","'+prefixTFG+'",selType="ikHandle")')
	mc.textFieldButtonGrp(blendCtrlTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+blendCtrlTFB+'")')
	mc.textFieldButtonGrp(scaleAttrTFB,e=True,bc='glTools.ui.utils.loadChannelBoxSel("'+scaleAttrTFB+'")')
	
	# Form Layout - MAIN
	mc.formLayout(FL,e=True,af=[(handleTFB,'top',5),(handleTFB,'left',5),(handleTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(prefixTFG,'top',5,handleTFB)])
	mc.formLayout(FL,e=True,af=[(prefixTFG,'left',5),(prefixTFG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(shrinkCBG,'top',5,prefixTFG)])
	mc.formLayout(FL,e=True,af=[(shrinkCBG,'left',5),(shrinkCBG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(scaleAxisOMG,'top',5,shrinkCBG)])
	mc.formLayout(FL,e=True,af=[(scaleAxisOMG,'left',5),(scaleAxisOMG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(scaleAttrTFB,'top',5,scaleAxisOMG)])
	mc.formLayout(FL,e=True,af=[(scaleAttrTFB,'left',5),(scaleAttrTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(blendCtrlTFB,'top',5,scaleAttrTFB)])
	mc.formLayout(FL,e=True,af=[(blendCtrlTFB,'left',5),(blendCtrlTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(blendAttrTFG,'top',5,blendCtrlTFB)])
	mc.formLayout(FL,e=True,af=[(blendAttrTFG,'left',5),(blendAttrTFG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(SEP,'top',5,blendAttrTFG)])
	mc.formLayout(FL,e=True,af=[(SEP,'left',5),(SEP,'right',5)])
	mc.formLayout(FL,e=True,ac=[(createB,'top',5,SEP)])
	mc.formLayout(FL,e=True,af=[(createB,'left',5),(createB,'bottom',5)])
	mc.formLayout(FL,e=True,ap=[(createB,'right',5,50)])
	mc.formLayout(FL,e=True,ac=[(cancelB,'top',5,SEP)])
	mc.formLayout(FL,e=True,af=[(cancelB,'right',5),(cancelB,'bottom',5)])
	mc.formLayout(FL,e=True,ap=[(cancelB,'left',5,50)])
	
	# Show Window
	mc.showWindow(window)

def stretchyIkChainFromUI(close=False):
	'''
	Execute stretchyIkChain() from UI
	'''
	# Window
	window = 'stretchyIkChainUI'
	if not mc.window(window,q=True,ex=1): raise UIError('StretchyIkChain UI does not exist!!')
	
	# Get UI data
	ik = mc.textFieldButtonGrp('stretchyIkChainTFB',q=True,text=True)
	pre = mc.textFieldGrp('stretchyIkChainPrefixTFG',q=True,text=True)
	shrink = mc.checkBoxGrp('stretchyIkChainShrinkCBG',q=True,v1=True)
	scaleAxis = str.lower(str(mc.optionMenuGrp('stretchyIkChainAxisOMG',q=True,v=True)))
	scaleAttr = mc.textFieldButtonGrp('stretchyIkChainScaleAttrTFB',q=True,text=True)
	blendCtrl = mc.textFieldButtonGrp('stretchyIkChainBlendCtrlTFB',q=True,text=True)
	blendAttr = mc.textFieldGrp('stretchyIkChainBlendAttrTFB',q=True,text=True)
	
	# Execute command
	glTools.builder.stretchyIkChain.StretchyIkChain().build(ikHandle=ik,scaleAttr=scaleAttr,scaleAxis=scaleAxis,blendControl=blendCtrl,blendAttr=blendAttr,shrink=shrink,prefix=pre)
	
	# Cleanup
	if close: mc.deleteUI(window)

def stretchyIkLimbUI():
	'''
	UI for stretchyIkLimb()
	'''
	# Window
	window = 'stretchyIkLimbUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Stretchy IK Limb')
	# Layout
	FL = mc.formLayout()
	# UI Elements
	#---
	# IK Handle
	handleTFB = mc.textFieldButtonGrp('stretchyIkLimbTFB',label='IK Handle',text='',buttonLabel='Load Selected')
	# Prefix
	prefixTFG = mc.textFieldGrp('stretchyIkLimbPrefixTFG',label='Prefix', text='')
	# Control
	controlTFB = mc.textFieldButtonGrp('stretchyIkLimbControlTFB',label='Control Object',text='',buttonLabel='Load Selected')
	# Scale Axis
	axisList = ['X','Y','Z']
	scaleAxisOMG = mc.optionMenuGrp('stretchyIkLimbAxisOMG',label='Joint Scale Axis')
	for axis in axisList: mc.menuItem(label=axis)
	mc.optionMenuGrp(scaleAxisOMG,e=True,sl=1)
	# Scale Attr
	scaleAttrTFB = mc.textFieldButtonGrp('stretchyIkLimbScaleAttrTFB',label='Scale Attribute',text='',buttonLabel='Load Selected')
	
	# Separator
	SEP = mc.separator(height=10,style='single')
	
	# Buttons
	createB = mc.button('stretchyIkLimbCreateB',l='Create',c='glTools.ui.ik.stretchyIkLimbFromUI(False)')
	cancelB = mc.button('stretchyIkLimbCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# UI callback commands
	mc.textFieldButtonGrp(handleTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+handleTFB+'","'+prefixTFG+'",selType="ikHandle")')
	mc.textFieldButtonGrp(controlTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+controlTFB+'")')
	mc.textFieldButtonGrp(scaleAttrTFB,e=True,bc='glTools.ui.utils.loadChannelBoxSel("'+scaleAttrTFB+'")')
	
	# Form Layout - MAIN
	mc.formLayout(FL,e=True,af=[(handleTFB,'top',5),(handleTFB,'left',5),(handleTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(prefixTFG,'top',5,handleTFB)])
	mc.formLayout(FL,e=True,af=[(prefixTFG,'left',5),(prefixTFG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(controlTFB,'top',5,prefixTFG)])
	mc.formLayout(FL,e=True,af=[(controlTFB,'left',5),(controlTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(scaleAxisOMG,'top',5,controlTFB)])
	mc.formLayout(FL,e=True,af=[(scaleAxisOMG,'left',5),(scaleAxisOMG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(scaleAttrTFB,'top',5,scaleAxisOMG)])
	mc.formLayout(FL,e=True,af=[(scaleAttrTFB,'left',5),(scaleAttrTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(SEP,'top',5,scaleAttrTFB)])
	mc.formLayout(FL,e=True,af=[(SEP,'left',5),(SEP,'right',5)])
	mc.formLayout(FL,e=True,ac=[(createB,'top',5,SEP)])
	mc.formLayout(FL,e=True,af=[(createB,'left',5),(createB,'bottom',5)])
	mc.formLayout(FL,e=True,ap=[(createB,'right',5,50)])
	mc.formLayout(FL,e=True,ac=[(cancelB,'top',5,SEP)])
	mc.formLayout(FL,e=True,af=[(cancelB,'right',5),(cancelB,'bottom',5)])
	mc.formLayout(FL,e=True,ap=[(cancelB,'left',5,50)])
	
	# Show Window
	mc.showWindow(window)

def stretchyIkLimbFromUI(close=False):
	'''
	Execute stretchyIkLimb() from UI
	'''
	# Window
	window = 'stretchyIkLimbUI'
	if not mc.window(window,q=True,ex=1): raise UIError('StretchyIkChain UI does not exist!!')
	
	# Get UI data
	ik = mc.textFieldButtonGrp('stretchyIkLimbTFB',q=True,text=True)
	pre = mc.textFieldGrp('stretchyIkLimbPrefixTFG',q=True,text=True)
	ctrl = mc.textFieldButtonGrp('stretchyIkLimbControlTFB',q=True,text=True)
	scaleAxis = str.lower(str(mc.optionMenuGrp('stretchyIkLimbAxisOMG',q=True,v=True)))
	scaleAttr = mc.textFieldButtonGrp('stretchyIkLimbScaleAttrTFB',q=True,text=True)
	
	# Execute command
	glTools.builder.stretchyIkLimb.StretchyIkLimb().build(ikHandle=ik,control=ctrl,scaleAttr=scaleAttr,scaleAxis=scaleAxis,prefix=pre)
	
	# Cleanup
	if close: mc.deleteUI(window)

def stretchyIkSplineUI():
	'''
	UI for stretchyIkSpline()
	'''
	# Window
	window = 'stretchyIkSplineUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Stretchy IK Spline')
	# Layout
	FL = mc.formLayout()
	# UI Elements
	#---
	# IK Handle
	handleTFB = mc.textFieldButtonGrp('stretchyIkSplineTFB',label='IK Handle',text='',buttonLabel='Load Selected')
	# Prefix
	prefixTFG = mc.textFieldGrp('stretchyIkSplinePrefixTFG',label='Prefix', text='')
	# Scale Axis
	axisList = ['X','Y','Z']
	scaleAxisOMG = mc.optionMenuGrp('stretchyIkSplineAxisOMG',label='Joint Scale Axis')
	for axis in axisList: mc.menuItem(label=axis)
	mc.optionMenuGrp(scaleAxisOMG,e=True,sl=1)
	# Scale Attr
	scaleAttrTFB = mc.textFieldButtonGrp('stretchyIkSplineScaleAttrTFB',label='Scale Attribute',text='',buttonLabel='Load Selected')
	# Blend
	blendCtrlTFB = mc.textFieldButtonGrp('stretchyIkSplineBlendCtrlTFB',label='Blend Control',text='',buttonLabel='Load Selected')
	blendAttrTFG = mc.textFieldGrp('stretchyIkSplineBlendAttrTFG',label='Blend Attribute',text='stretchScale')
	
	# Stretch Method
	methodList = ['Arc Length','Parametric']
	methodOMG = mc.optionMenuGrp('stretchyIkSplineMethodOMG',label='Stretch Method')
	for method in methodList: mc.menuItem(label=method)
	mc.optionMenuGrp(methodOMG,e=True,sl=2)
	
	# Parametric Layout
	paramFrameL = mc.frameLayout('stretchyIkSplineParamFL',l='Parametric Bounds',cll=0)
	paramFormL = mc.formLayout(numberOfDivisions=100)
	
	# Min/Max Percent
	minPercentFSG = mc.floatSliderGrp('stretchyIkSplineMinPFSG',label='Min Percent',field=True,minValue=0.0,maxValue=1.0,fieldMinValue=0.0,fieldMaxValue=1.0,value=0.0)
	maxPercentFSG = mc.floatSliderGrp('stretchyIkSplineMaxPFSG',label='Max Percent',field=True,minValue=0.0,maxValue=1.0,fieldMinValue=0.0,fieldMaxValue=1.0,value=1.0)
	#closestPointCBG = mc.checkBoxGrp('stretchyIkSplineClosestPointCBG',l='Use Closest Point',ncb=1,v1=True)
	
	mc.setParent('..')
	mc.setParent('..')
	
	# Buttons
	createB = mc.button('stretchyIkSplineCreateB',l='Create',c='glTools.ui.ik.stretchyIkSplineFromUI(False)')
	cancelB = mc.button('stretchyIkSplineCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# UI callback commands
	mc.textFieldButtonGrp(handleTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+handleTFB+'","'+prefixTFG+'",selType="ikHandle")')
	mc.textFieldButtonGrp(scaleAttrTFB,e=True,bc='glTools.ui.utils.loadChannelBoxSel("'+scaleAttrTFB+'")')
	mc.textFieldButtonGrp(blendCtrlTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+blendCtrlTFB+'")')
	mc.optionMenuGrp(methodOMG,e=True,cc='mc.frameLayout("'+paramFrameL+'",e=True,en=mc.optionMenuGrp("'+methodOMG+'",q=True,sl=True)-1)')
	
	# Form Layout - MAIN
	mc.formLayout(FL,e=True,af=[(handleTFB,'top',5),(handleTFB,'left',5),(handleTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(prefixTFG,'top',5,handleTFB)])
	mc.formLayout(FL,e=True,af=[(prefixTFG,'left',5),(prefixTFG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(scaleAxisOMG,'top',5,prefixTFG)])
	mc.formLayout(FL,e=True,af=[(scaleAxisOMG,'left',5),(scaleAxisOMG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(scaleAttrTFB,'top',5,scaleAxisOMG)])
	mc.formLayout(FL,e=True,af=[(scaleAttrTFB,'left',5),(scaleAttrTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(blendCtrlTFB,'top',5,scaleAttrTFB)])
	mc.formLayout(FL,e=True,af=[(blendCtrlTFB,'left',5),(blendCtrlTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(blendAttrTFG,'top',5,blendCtrlTFB)])
	mc.formLayout(FL,e=True,af=[(blendAttrTFG,'left',5),(blendAttrTFG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(methodOMG,'top',5,blendAttrTFG)])
	mc.formLayout(FL,e=True,af=[(methodOMG,'left',5),(methodOMG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(paramFrameL,'top',5,methodOMG),(paramFrameL,'bottom',5,createB)])
	mc.formLayout(FL,e=True,af=[(paramFrameL,'left',5),(paramFrameL,'right',5)])
	mc.formLayout(FL,e=True,af=[(createB,'left',5),(createB,'bottom',5)])
	mc.formLayout(FL,e=True,ap=[(createB,'right',5,50)])
	mc.formLayout(FL,e=True,af=[(cancelB,'right',5),(cancelB,'bottom',5)])
	mc.formLayout(FL,e=True,ap=[(cancelB,'left',5,50)])
	
	# Form Layout - Parametric
	mc.formLayout(paramFormL,e=True,af=[(minPercentFSG,'top',5),(minPercentFSG,'left',5),(minPercentFSG,'right',5)])
	mc.formLayout(paramFormL,e=True,ac=[(maxPercentFSG,'top',5,minPercentFSG)])
	mc.formLayout(paramFormL,e=True,af=[(maxPercentFSG,'left',5),(maxPercentFSG,'right',5)])
	
	# Show Window
	mc.showWindow(window)

def stretchyIkSplineFromUI(close=False):
	'''
	'''
	# Window
	window = 'stretchyIkSplineUI'
	if not mc.window(window,q=True,ex=1): raise UIError('StretchyIkSpline UI does not exist!!')
	
	# Get UI data
	ik = mc.textFieldButtonGrp('stretchyIkSplineTFB',q=True,text=True)
	pre = mc.textFieldGrp('stretchyIkSplinePrefixTFG',q=True,text=True)
	scaleAxis = str.lower(str(mc.optionMenuGrp('stretchyIkSplineAxisOMG',q=True,v=True)))
	scaleAttr = mc.textFieldButtonGrp('stretchyIkSplineScaleAttrTFB',q=True,text=True)
	blendCtrl = mc.textFieldButtonGrp('stretchyIkSplineBlendCtrlTFB',q=True,text=True)
	blendAttr = mc.textFieldGrp('stretchyIkSplineBlendAttrTFG',q=True,text=True)
	method = mc.optionMenuGrp('stretchyIkSplineMethodOMG',q=True,sl=True)-1
	minPercent = mc.floatSliderGrp('stretchyIkSplineMinPFSG',q=True,v=True)
	maxPercent = mc.floatSliderGrp('stretchyIkSplineMaxPFSG',q=True,v=True)
	
	# Execute command
	if method: # Parametric
		glTools.builder.stretchyIkSpline_parametric.StretchyIkSpline_parametric().build(ikHandle=ik,scaleAttr=scaleAttr,blendControl=blendCtrl,blendAttr=blendAttr,scaleAxis=scaleAxis,minPercent=minPercent,maxPercent=maxPercent,prefix=pre)
	else: # Arc Length
		glTools.builder.stretchyIkSpline_arcLength.StretchyIkSpline_arcLength().build(ikHandle=ik,scaleAttr=scaleAttr,blendControl=blendCtrl,blendAttr=blendAttr,scaleAxis=scaleAxis,prefix=pre)
	
	# Cleanup
	if close: mc.deleteUI(window)
