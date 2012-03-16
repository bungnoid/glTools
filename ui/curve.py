import maya.cmds as mc

import glTools.ui.utils
import glTools.utils.attach
import glTools.utils.curve
import glTools.tools.createAlongCurve

class UserInputError(Exception): pass
class UIError(Exception): pass

# Locator Curve --

def locatorCurveUI():
	'''
	UI for locatorCurve()
	'''
	# Window
	window = 'locatorCurveUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Locator Curve')
	# Layout
	cl = mc.columnLayout()
	# UI Elements
	#---
	# Curve
	curveTFB = mc.textFieldButtonGrp('locatorCurveTFB',label='Source Curve',text='',buttonLabel='Load Selected')
	# Prefix
	prefixTFG = mc.textFieldGrp('locatorCurvePrefixTFG',label='Prefix', text='')
	# Scale
	scaleFSG = mc.floatSliderGrp('locatorCurveScaleFSG',label='Locator Scale',field=True,minValue=0.0,maxValue=1.0,fieldMinValue=0.0,fieldMaxValue=10.0,value=0.05,pre=3)
	# Edit Points
	editPointCBG = mc.checkBoxGrp('locatorCurveEditPointCBG',numberOfCheckBoxes=1,label='Use Edit Points',v1=False)
	# Buttons
	createB = mc.button('locatorCurveCreateB',l='Create',c='glTools.ui.curve.locatorCurveFromUI(False)')
	cancelB = mc.button('locatorCurveCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# TFB commands
	mc.textFieldButtonGrp(curveTFB,e=True,bc='glTools.ui.utils.loadCurveSel("'+curveTFB+'","'+prefixTFG+'")')
	
	# Show Window
	mc.showWindow(window)

def locatorCurveFromUI(close=False):
	'''
	Execute locatorCurve() from UI
	'''
	# Window
	window = 'locatorCurveUI'
	if not mc.window(window,q=True,ex=1): raise UIError('LocatorCurve UI does not exist!!')
	# Get UI data
	curve = mc.textFieldGrp('locatorCurveTFB',q=True,text=True)
	prefix = mc.textFieldGrp('locatorCurvePrefixTFG',q=True,text=True)
	scale = mc.floatSliderGrp('locatorCurveScaleFSG',q=True,v=True)
	editPoints = mc.checkBoxGrp('locatorCurveEditPointCBG',q=True,v1=True)
	# Check curve
	if not glTools.utils.curve.isCurve(curve):
		raise UserInputError('Object "'+curve+'" is not a valid nurbs curve!!')
	# Execute
	if editPoints:
		glTools.utils.curve.locatorEpCurve(curve=curve,locatorScale=scale,prefix=prefix)
	else:
		glTools.utils.curve.locatorCurve(curve=curve,locatorScale=scale,prefix=prefix)
	# Cleanup
	if close: mc.deleteUI(window)

# Attach to Curve --

def attachToCurveUI():
	'''
	UI for attachToCurve()
	'''
	# Window
	window = 'attachToCurveUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Attach To Curve')
	# Layout
	cl = mc.columnLayout()
	# UI Elements
	#---
	# Curve
	curveTFB = mc.textFieldButtonGrp('attachToCurveTFB',label='Target Curve',text='',buttonLabel='Load Selected')
	# Transform
	transformTFB = mc.textFieldButtonGrp('attachToCurveTransformTFB',label='Attach Transform',text='',buttonLabel='Load Selected')
	# Prefix
	prefixTFG = mc.textFieldGrp('attachToCurvePrefixTFG',label='Prefix', text='')
	# Closest Point
	closestPointCBG = mc.checkBoxGrp('attachToCurveClosestPointCBG',numberOfCheckBoxes=1,label='Use Closest Point',v1=False)
	# Parameter
	parameterFSG = mc.floatSliderGrp('attachToCurveParamFSG',label='Parameter',field=True,minValue=0.0,maxValue=1.0,fieldMinValue=0.0,fieldMaxValue=10.0,value=0.05,pre=3)
	# Parameter Attribute
	paramAttrTFG = mc.textFieldGrp('attachToCurveParamAttrTFG',label='Parameter Attribute', text='param')
	# Orient
	orientCBG = mc.checkBoxGrp('attachToCurveOrientCBG',label='Orient',numberOfCheckBoxes=1,v1=True)
	# Up Vector
	upVectorFFG = mc.floatFieldGrp('attachToCurveUpVecFFG',label='UpVector',nf=3,v1=0,v2=1,v3=0)
	upVectorObjectTFB = mc.textFieldButtonGrp('attachToCurveUpVecObjTFG',label='WorldUpObject',text='',buttonLabel='Load Selected')
	# Buttons
	createB = mc.button('attachToCurveCreateB',l='Create',c='glTools.ui.curve.attachToCurveFromUI(False)')
	cancelB = mc.button('attachToCurveCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# UI callback commands
	mc.textFieldButtonGrp(curveTFB,e=True,bc='glTools.ui.utils.loadCurveSel("'+curveTFB+'")')
	mc.textFieldButtonGrp(transformTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+transformTFB+'","'+prefixTFG+'")')
	mc.textFieldButtonGrp(upVectorObjectTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+upVectorObjectTFB+'")')
	mc.checkBoxGrp(closestPointCBG,e=True,cc='glTools.ui.utils.checkBoxToggleControl("'+closestPointCBG+'","'+parameterFSG+'",invert=True)')
	
	# Show Window
	mc.showWindow(window)

def attachToCurveFromUI(close=False):
	'''
	Execute attachToCurve() from UI
	'''
	# Window
	window = 'attachToCurveUI'
	if not mc.window(window,q=True,ex=1): raise UIError('AttachToCurve UI does not exist!!')
	# Get UI data
	curve = mc.textFieldGrp('attachToCurveTFB',q=True,text=True)
	transform = mc.textFieldGrp('attachToCurveTransformTFB',q=True,text=True)
	prefix = mc.textFieldGrp('attachToCurvePrefixTFG',q=True,text=True)
	closestPoint = mc.checkBoxGrp('attachToCurveClosestPointCBG',q=True,v1=True)
	param = mc.floatSliderGrp('attachToCurveParamFSG',q=True,v=True)
	paramAttr = mc.textFieldGrp('attachToCurveParamAttrTFG',q=True,text=True)
	orient = mc.checkBoxGrp('attachToCurveOrientCBG',q=True,v1=True)
	upVec = (mc.floatFieldGrp('attachToCurveUpVecFFG',q=True,v1=True),mc.floatFieldGrp('attachToCurveUpVecFFG',q=True,v2=True),mc.floatFieldGrp('attachToCurveUpVecFFG',q=True,v3=True))
	upVecObj = mc.textFieldButtonGrp('attachToCurveUpVecObjTFG',q=True,text=True)
	# Check curve
	if not glTools.utils.curve.isCurve(curve):
		raise UserInputError('Object "'+curve+'" is not a valid nurbs curve!!')
	glTools.utils.attach.attachToCurve(curve=curve,transform=transform,uValue=param,useClosestPoint=closestPoint,orient=orient,upVector=upVec,worldUpObject=upVecObj,uAttr=paramAttr,prefix=prefix)
	# Cleanup
	if close: mc.deleteUI(window)

# Curve To Locators --

def curveToLocatorsUI():
	'''
	UI for curveToLocators()
	'''
	# Window
	window = 'curveToLocatorsUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Curve To Locators')
	# Layout
	fl = mc.formLayout(numberOfDivisions=100)
	# UI Elements
	#---
	# Curve
	curveTFB = mc.textFieldButtonGrp('curveToLocatorsTFB',label='Target Curve',text='',buttonLabel='Load Selected')
	# Locator List
	locListTSL = mc.textScrollList('curveToLocatorsTSL',numberOfRows=8,allowMultiSelection=True)
	# TSL Buttons
	locAddB = mc.button('attachToCurveAddLocB',l='Add',c='glTools.ui.utils.addToTSL("'+locListTSL+'")')
	locRemB = mc.button('attachToCurveRemLocB',l='Remove',c='glTools.ui.utils.removeFromTSL("'+locListTSL+'")')
	# Buttons
	createB = mc.button('attachToCurveCreateB',l='Create',c='glTools.ui.curve.curveToLocatorsFromUI(False)')
	cancelB = mc.button('attachToCurveCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# Form Layout
	mc.formLayout(fl,e=True,af=[(curveTFB,'top',5),(curveTFB,'left',5),(curveTFB,'right',5)])
	mc.formLayout(fl,e=True,ac=[(locListTSL,'top',5,curveTFB),(locListTSL,'bottom',5,locAddB)])
	mc.formLayout(fl,e=True,af=[(locListTSL,'left',5),(locListTSL,'right',5)])
	mc.formLayout(fl,e=True,ac=[(locAddB,'bottom',1,locRemB)])
	mc.formLayout(fl,e=True,af=[(locAddB,'left',5),(locAddB,'right',5)])
	mc.formLayout(fl,e=True,ac=[(locRemB,'bottom',1,createB)])
	mc.formLayout(fl,e=True,af=[(locRemB,'left',5),(locRemB,'right',5)])
	mc.formLayout(fl,e=True,ac=[(createB,'bottom',1,cancelB)])
	mc.formLayout(fl,e=True,af=[(createB,'left',5),(createB,'right',5)])
	mc.formLayout(fl,e=True,af=[(cancelB,'bottom',5),(cancelB,'left',5),(cancelB,'right',5)])
	
	# TFB commands
	mc.textFieldButtonGrp(curveTFB,e=True,bc='glTools.ui.utils.loadCurveSel("'+curveTFB+'")')
	
	# Show Window
	mc.showWindow(window)

def curveToLocatorsFromUI(close=False):
	'''
	Execute curveToLocators() from UI
	'''
	# Window
	window = 'curveToLocatorsUI'
	if not mc.window(window,q=True,ex=1): raise UIError('CurveToLocators UI does not exist!!')
	curve = mc.textFieldGrp('curveToLocatorsTFB',q=True,text=True)
	locList = mc.textScrollList('curveToLocatorsTSL',q=True,ai=True)
	# Check curve
	if not glTools.utils.curve.isCurve(curve):
		raise UserInputError('Object "'+curve+'" is not a valid nurbs curve!!')
	# Execute command
	glTools.utils.curve.curveToLocators(curve=curve,locatorList=locList)
	# Cleanup
	if close: mc.deleteUI(window)

# Create Along Curve --

def createAlongCurveUI():
	'''
	UI for createAlongCurve()
	'''
	# Window
	window = 'createAlongCurveUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Create Along Curve')
	
	# Layout
	cl = mc.columnLayout()
	# Curve
	curveTFB = mc.textFieldButtonGrp('createAlongCurveTFB',label='Target Curve',text='',buttonLabel='Load Selected')
	# Prefix
	prefixTFG = mc.textFieldGrp('createAlongCurvePrefixTFG',label='Prefix',text='')
	# Object Type
	typeOMG = mc.optionMenuGrp('createAlongCurveTypeOMG',label='Object Type')
	for item in ['joint','transform','locator']: mc.menuItem(label=item)
	# Object Count
	countISG = mc.intSliderGrp('createAlongCurveCountISG',field=True,label='Object Count',minValue=0,maxValue=10,fieldMinValue=0,fieldMaxValue=100,value=0)
	# Parent Objects
	parentCBG = mc.checkBoxGrp('createAlongCurveParentCBG',numberOfCheckBoxes=1,label='Parent Objects',v1=True)
	# Use Distance
	distanceCBG = mc.checkBoxGrp('createAlongCurveDistCBG',numberOfCheckBoxes=1,label='Use Distance',v1=False)
	# Min/Max Percent
	minPercentFFG = mc.floatSliderGrp('createAlongCurveMinFSG',label='Min Percent',field=True,minValue=0.0,maxValue=1.0,fieldMinValue=0.0,fieldMaxValue=1.0,value=0.0)
	maxPercentFFG = mc.floatSliderGrp('createAlongCurveMaxFSG',label='Max Percent',field=True,minValue=0.0,maxValue=1.0,fieldMinValue=0.0,fieldMaxValue=1.0,value=1.0)
	
	# Buttons
	createB = mc.button('createAlongCurveCreateB',l='Create',c='glTools.ui.curve.createAlongCurveFromUI(False)')
	createCloseB = mc.button('createAlongCurveCreateCloseB',l='Create and Close',c='glTools.ui.curve.createAlongCurveFromUI(True)')
	cancelB = mc.button('createAlongCurveCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# TFB commands
	mc.textFieldButtonGrp(curveTFB,e=True,bc='glTools.ui.utils.loadCurveSel("'+curveTFB+'","'+prefixTFG+'")')
	
	# Show Window
	mc.showWindow(window)

def createAlongCurveFromUI(close=False):
	'''
	Execute createAlongCurve() from UI
	'''
	# Window
	window = 'createAlongCurveUI'
	if not mc.window(window,q=True,ex=1): raise UIError('CreateAlongCurve UI does not exist!!')
	curve = str(mc.textFieldGrp('createAlongCurveTFB',q=True,text=True))
	prefix = str(mc.textFieldGrp('createAlongCurvePrefixTFG',q=True,text=True))
	objType = str(mc.optionMenuGrp('createAlongCurveTypeOMG',q=True,v=True))
	objCount = mc.intSliderGrp('createAlongCurveCountISG',q=True,v=True)
	parent = mc.checkBoxGrp('createAlongCurveParentCBG',q=True,v1=True)
	useDist = mc.checkBoxGrp('createAlongCurveDistCBG',q=True,v1=True)
	minVal = mc.floatSliderGrp('createAlongCurveMinFSG',q=True,v=True)
	maxVal = mc.floatSliderGrp('createAlongCurveMaxFSG',q=True,v=True)
	
	# Execute command
	glTools.tools.createAlongCurve.create(curve,objType,objCount,parent,useDist,minVal,maxVal,prefix)
	
	# Cleanup
	if close: mc.deleteUI(window)

# Edge Loop Curve --

def edgeLoopCurveUI():
	'''
	UI for edgeLoopCurve()
	'''
	# Window
	window = 'edgeLoopCurveUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Edge Loop Curve')
	
	# Layout
	CL = mc.columnLayout()
	# Prefix
	prefixTFG = mc.textFieldGrp('edgeLoopCurvePrefixTFG',label='Prefix',text='')
	# Rebuild
	rebuildCBG = mc.checkBoxGrp('edgeLoopCurveRebuildCBG',numberOfCheckBoxes=1,label='Rebuild Curve',v1=True)
	# Span Count
	spanISG = mc.intSliderGrp('edgeLoopCurveSpanISG',field=True,label='Rebuild Spans',minValue=0,maxValue=10,fieldMinValue=0,fieldMaxValue=100,value=0,en=1)
	
	# Toggle UI element
	mc.checkBoxGrp('edgeLoopCurveRebuildCBG',e=True,cc='mc.intSliderGrp("edgeLoopCurveSpanISG",e=1,en=(not mc.intSliderGrp("edgeLoopCurveSpanISG",q=1,en=1)))')
	
	# Buttons
	createB = mc.button('edgeLoopCurveCreateB',l='Create',c='glTools.ui.curve.edgeLoopCurveFromUI(False)')
	createCloseB = mc.button('edgeLoopCurveCreateCloseB',l='Create and Close',c='glTools.ui.curve.edgeLoopCurveFromUI(True)')
	cancelB = mc.button('edgeLoopCurveCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# Show Window
	mc.showWindow(window)

def edgeLoopCurveFromUI(close=False):
	'''
	Execute createAlongCurve() from UI
	'''
	# Get mesh edge selection
	selection = mc.filterExpand(sm=32)
	if not selection: raise UserInputError('No current valid mesh edge selection!!')
	# Window
	window = 'edgeLoopCurveUI'
	if not mc.window(window,q=True,ex=1): raise UIError('EdgeLoopCurve UI does not exist!!')
	prefix = str(mc.textFieldGrp('edgeLoopCurvePrefixTFG',q=True,text=True))
	rebuildCrv = mc.checkBoxGrp('edgeLoopCurveRebuildCBG',q=True,v1=True)
	spans = mc.intSliderGrp('edgeLoopCurveSpanISG',q=True,v=True)
	
	# Execute command
	glTools.utils.curve.edgeLoopCrv(selection,rebuild=rebuildCrv,rebuildSpans=spans,prefix=prefix)
	
	# Cleanup
	if close: mc.deleteUI(window)

# Uniform Rebuild Curve --

def uniformRebuildCurveUI():
	'''
	UI for uniformRebuild()
	'''
	# Window
	window = 'uniformRebuildCurveUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Uniform Rebuild Curve')
	
	# Layout
	cl = mc.columnLayout()
	# Curve
	curveTFB = mc.textFieldButtonGrp('uniformRebuildCurveTFB',label='Source Curve',text='',buttonLabel='Load Selected')
	# Prefix
	prefixTFG = mc.textFieldGrp('uniformRebuildCurvePrefixTFG',label='Prefix',text='')
	# Replace Original
	replaceCBG = mc.checkBoxGrp('uniformRebuildCurveReplaceCBG',numberOfCheckBoxes=1,label='Replace Original',v1=False)
	# Spans
	spanISG = mc.intSliderGrp('uniformRebuildCurveSpansISG',field=True,label='Rebuild Spans',minValue=2,maxValue=10,fieldMinValue=2,fieldMaxValue=100,value=6)
	
	# Buttons
	createB = mc.button('uniformRebuildCurveCreateB',l='Create',c='glTools.ui.curve.uniformRebuildCurveFromUI(False)')
	createCloseB = mc.button('uniformRebuildCurveCreateCloseB',l='Create and Close',c='glTools.ui.curve.uniformRebuildCurveFromUI(True)')
	cancelB = mc.button('uniformRebuildCurveCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# TFB commands
	mc.textFieldButtonGrp(curveTFB,e=True,bc='glTools.ui.utils.loadCurveSel("'+curveTFB+'","'+prefixTFG+'")')
	
	# Show Window
	mc.showWindow(window)

def uniformRebuildCurveFromUI(close=False):
	'''
	Execute uniformRebuild() from UI
	'''
	# Window
	window = 'uniformRebuildCurveUI'
	if not mc.window(window,q=True,ex=1): raise UIError('uniformRebuildCurve UI does not exist!!')
	curve = str(mc.textFieldGrp('uniformRebuildCurveTFB',q=True,text=True))
	if not glTools.utils.curve.isCurve(curve):
		raise UserInputError('Object "'+curve+'" is not a valid nurbs curve!!')
	prefix = str(mc.textFieldGrp('uniformRebuildCurvePrefixTFG',q=True,text=True))
	replace = mc.checkBoxGrp('uniformRebuildCurveReplaceCBG',q=True,v1=True)
	spans = mc.intSliderGrp('uniformRebuildCurveSpansISG',q=True,v=True)
	
	# Execute command
	glTools.utils.curve.uniformRebuild(curve=curve,spans=spans,replaceOriginal=replace,prefix=prefix)
	
	# Cleanup
	if close: mc.deleteUI(window)

