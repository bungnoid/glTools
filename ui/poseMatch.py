import maya.cmds as mc
import glTools.tools.match
import glTools.ui.utils

global gEvalOrder

class UserInputError(Exception): pass

def evaluationOrderUI():
	'''
	Main UI method for Evaluation Order setup tools
	'''
	# Window
	win = 'evaluationOrderUI'
	if mc.window(win,q=True,ex=True): mc.deleteUI(win)
	win = mc.window(win,t='Evaluation Order')
	# Form Layout
	evaluationOrderFL = mc.formLayout(numberOfDivisions=100)
	
	# Evaluation Order List
	evalOrderTSL = mc.textScrollList('evalOrderTSL',allowMultiSelection=True)
	
	# Buttons
	evalOrderRootB = mc.button(label='Set Selected As Root',c='glTools.ui.poseMatch.evalOrderUIsetRoot()')
	evalOrderBuildB = mc.button(label='Build Root Hierarchy',c='glTools.ui.poseMatch.evalOrderUIbuildHierarchy()')
	evalOrderIKB = mc.button(label='Reorder Using IK',c='glTools.ui.poseMatch.evalOrderUIreorderIK()')
	evalOrderConstraintB = mc.button(label='Reorder Using Constraints',c='glTools.ui.poseMatch.evalOrderUIreorderConstraints()')
	evalOrderReduceB = mc.button(label='Reduce To Selection',c='glTools.ui.poseMatch.evalOrderUIreduceToSelection()')
	evalOrderMoveUpB = mc.button(label='Move Up',c='glTools.ui.utils.moveUpTSLPosition("'+evalOrderTSL+'")')
	evalOrderMoveDnB = mc.button(label='Move Down',c='glTools.ui.utils.moveDownTSLPosition("'+evalOrderTSL+'")')
	evalOrderMoveToBottomB = mc.button(label='Move To Bottom',c='glTools.ui.utils.moveToTSLPosition("'+evalOrderTSL+'",-1)')
	evalOrderAddAttrB = mc.button(label='Add "evalOrder" attribute',c='glTools.ui.poseMatch.evalOrderUIaddAttr()')
	
	# Separators
	evalOrderReorderSEP = mc.separator(h=10,style='single')
	evalOrderReduceSEP = mc.separator(h=10,style='single')
	evalOrderMoveSEP = mc.separator(h=10,style='single')
	evalOrderAddAttrSEP = mc.separator(h=10,style='single')
	
	# Form Layout - MAIM
	#-
	# evalOrderTSL
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderTSL,'left',5),(evalOrderTSL,'bottom',5),(evalOrderTSL,'top',5)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderTSL,'right',5,50)])
	# evalOrderRootB
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderRootB,'top',5),(evalOrderRootB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderRootB,'left',5,50)])
	# evalOrderBuildB
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderBuildB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderBuildB,'top',5,evalOrderRootB)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderBuildB,'left',5,50)])
	
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderReorderSEP,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderReorderSEP,'top',5,evalOrderBuildB)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderReorderSEP,'left',5,50)])
	
	# evalOrderIKB
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderIKB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderIKB,'top',5,evalOrderReorderSEP)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderIKB,'left',5,50)])
	# evalOrderConstraintB
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderConstraintB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderConstraintB,'top',5,evalOrderIKB)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderConstraintB,'left',5,50)])
	
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderReduceSEP,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderReduceSEP,'top',5,evalOrderConstraintB)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderReduceSEP,'left',5,50)])
	
	# evalOrderReduceB
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderReduceB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderReduceB,'top',5,evalOrderReduceSEP)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderReduceB,'left',5,50)])
	
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderMoveSEP,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderMoveSEP,'top',5,evalOrderReduceB)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderMoveSEP,'left',5,50)])
	
	# evalOrderMoveUpB
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderMoveUpB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderMoveUpB,'top',5,evalOrderMoveSEP)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderMoveUpB,'left',5,50)])
	# evalOrderMoveDnB
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderMoveDnB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderMoveDnB,'top',5,evalOrderMoveUpB)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderMoveDnB,'left',5,50)])
	# evalOrderMoveToBottomB
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderMoveToBottomB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderMoveToBottomB,'top',5,evalOrderMoveDnB)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderMoveToBottomB,'left',5,50)])
	
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderAddAttrSEP,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderAddAttrSEP,'top',5,evalOrderMoveToBottomB)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderAddAttrSEP,'left',5,50)])
	
	# evalOrderAddAttrB
	mc.formLayout(evaluationOrderFL,e=True,af=[(evalOrderAddAttrB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(evalOrderAddAttrB,'top',5,evalOrderAddAttrSEP)])
	mc.formLayout(evaluationOrderFL,e=True,ap=[(evalOrderAddAttrB,'left',5,50)])
	
	# Show Window
	mc.showWindow(win)
	
def evalOrderUIrefreshList(evalOrderList=[]):
	'''
	UI method for Evaluation Order setup tools
	Refreshes the evaluation order textScrollList
	'''
	# Get evalOrder list
	if not evalOrderList: evalOrderList = gEvalOrder.hierarchy.generationList()
	# Display evaluation order list in UI
	mc.textScrollList('evalOrderTSL',e=True,ra=True)
	for item in evalOrderList: mc.textScrollList('evalOrderTSL',e=True,a=item)

def evalOrderUIsetRoot():
	'''
	UI method for Evaluation Order setup tools
	Set the root of the evaluation order to the selected object
	'''
	# Check window
	win = 'evaluationOrderUI'
	if not mc.window(win,q=True,ex=True):
		raise UserInputError('Evaluation Order UI is not open!!')
	
	# Get Selection
	sel = mc.ls(sl=True,type='transform')
	if not sel: return
	
	# Add first selected item as root of evaluation order list
	mc.textScrollList('evalOrderTSL',e=True,ra=True)
	mc.textScrollList('evalOrderTSL',e=True,a=sel[0])

def evalOrderUIbuildHierarchy():
	'''
	UI method for Evaluation Order setup tools
	Build evaluation order list from hierarchy root object
	'''
	global gEvalOrder
	
	# Check window
	win = 'evaluationOrderUI'
	if not mc.window(win,q=True,ex=True):
		raise UserInputError('Evaluation Order UI is not open!!')
	
	# Get root object
	rootList = mc.textScrollList('evalOrderTSL',q=True,ai=True)
	if not rootList: raise UserInputError('Specify a hierarchy root!')
	
	# Build hierarchy list
	gEvalOrder = glTools.common.EvaluationOrder(rootList[0],debug=True)
	
	# Display evaluation order list in UI
	evalOrderUIrefreshList()
	
def evalOrderUIreorderIK():
	'''
	UI method for Evaluation Order setup tools
	Reorder the evaluation order based on IK dependencies
	'''
	global gEvalOrder
	
	# Check window
	win = 'evaluationOrderUI'
	if not mc.window(win,q=True,ex=True):
		raise UserInputError('Evaluation Order UI is not open!!')
	
	# Reorder using IK
	gEvalOrder.ikReorder()
	
	# Display evaluation order list in UI
	evalOrderUIrefreshList()

def evalOrderUIreorderConstraints():
	'''
	UI method for Evaluation Order setup tools
	Reorder the evaluation order based on constraint dependencies
	'''
	global gEvalOrder
	
	# Check window
	win = 'evaluationOrderUI'
	if not mc.window(win,q=True,ex=True):
		raise UserInputError('Evaluation Order UI is not open!!')
	
	# Reorder using IK
	gEvalOrder.constraintReorder()
	
	# Display evaluation order list in UI
	evalOrderUIrefreshList()

def evalOrderUIreduceToSelection():
	'''
	UI method for Evaluation Order setup tools
	Reduce the evaluation order list to the selected objects
	'''
	global gEvalOrder
	
	# Check window
	win = 'evaluationOrderUI'
	if not mc.window(win,q=True,ex=True):
		raise UserInputError('Evaluation Order UI is not open!!')
	
	# Get selection
	sel = mc.ls(sl=True)
	if not sel: return
	
	# Get evalOrder list
	evalOrderList = gEvalOrder.hierarchy.generationList()
	evalIntersectList = [i for i in evalOrderList if sel.count(i)]
	
	# Display evaluation order list in UI
	evalOrderUIrefreshList(evalIntersectList)

def evalOrderUIaddAttr():
	'''
	UI method for Evaluation Order setup tools
	Add the evaluation order list as an attribute to the root object
	'''
	global gEvalOrder
	
	# Check window
	win = 'evaluationOrderUI'
	if not mc.window(win,q=True,ex=True):
		raise UserInputError('Evaluation Order UI is not open!!')
	
	# Get evaluation order list
	evalOrderList = gEvalOrder.hierarchy.generationList()
	if not evalOrderList: raise UserInputError('Evaluation order list invalid!!')
	# Determine hierarchy root
	evalOrderRoot = evalOrderList[0]
	
	# Get intersectionList
	intersectList = mc.textScrollList('evalOrderTSL',q=True,ai=True)
	if not intersectList: return
	
	# Add list attribute to root object
	gEvalOrder.setAttr(evalOrderRoot,intersectList=intersectList,evalOrderList=evalOrderList)

def matchRulesUI():
	'''
	Main UI method for Pose Match setup tools
	'''
	# Window
	win = 'matchRulesUI'
	if mc.window(win,q=True,ex=True): mc.deleteUI(win)
	win = mc.window(win,t='Pose Match Rules')
	
	# Form Layout
	evaluationOrderFL = mc.formLayout(numberOfDivisions=100)
	
	# Pivot Object
	pivotTFB = mc.textFieldButtonGrp('matchRulesPivotTFB',label='Pivot Object',text='',buttonLabel='Load Selected')
	
	# Mirror Axis
	axisList = ['X','Y','Z']
	axisOMG = mc.optionMenuGrp('matchRulesAxisOMG',label='Mirror Axis')
	for axis in axisList: mc.menuItem(label=axis)
	
	# Mirror Mode
	modeList = ['World','Local']
	modeOMG = mc.optionMenuGrp('matchRulesModeOMG',label='Mirror Mode')
	for mode in modeList: mc.menuItem(label=mode)
	
	# Search/Replace Field
	searchTFG = mc.textFieldGrp('matchRulesSearchTFG',label='Search',text='lf_')
	replaceTFG = mc.textFieldGrp('matchRulesReplaceTFG',label='Replace',text='rt_')
	
	# Separator
	sep = mc.separator(height=10,style='single')
	
	# Buttons
	twinMatchB = mc.button('matchRulesTwinMatchB',l='Setup Twin Match',c='glTools.ui.poseMatch.setTwinMatchAttrsFromUI()')
	selfPivotB = mc.button('matchRulesSelfPivotB',l='Setup Self Pivot',c='glTools.ui.poseMatch.setSelfPivotAttrsFromUI()')
	closeB = mc.button('matchRulesCloseB',l='Close',c='mc.deleteUI("'+win+'")')
	
	# UI Callbacks
	mc.textFieldButtonGrp(pivotTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+pivotTFB+'","","transform")')
	
	# Form Layout - MAIN
	mc.formLayout(evaluationOrderFL,e=True,af=[(pivotTFB,'left',5),(pivotTFB,'top',5),(pivotTFB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,af=[(axisOMG,'left',5),(axisOMG,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(axisOMG,'top',5,pivotTFB)])
	mc.formLayout(evaluationOrderFL,e=True,af=[(modeOMG,'left',5),(modeOMG,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(modeOMG,'top',5,axisOMG)])
	mc.formLayout(evaluationOrderFL,e=True,af=[(searchTFG,'left',5),(searchTFG,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(searchTFG,'top',5,modeOMG)])
	mc.formLayout(evaluationOrderFL,e=True,af=[(replaceTFG,'left',5),(replaceTFG,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(replaceTFG,'top',5,searchTFG)])
	mc.formLayout(evaluationOrderFL,e=True,af=[(sep,'left',5),(sep,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(sep,'top',5,replaceTFG)])
	mc.formLayout(evaluationOrderFL,e=True,af=[(twinMatchB,'left',5)],ap=[(twinMatchB,'right',5,50)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(twinMatchB,'top',5,sep)])
	mc.formLayout(evaluationOrderFL,e=True,af=[(selfPivotB,'right',5)],ap=[(selfPivotB,'left',5,50)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(selfPivotB,'top',5,sep)])
	mc.formLayout(evaluationOrderFL,e=True,af=[(closeB,'left',5),(closeB,'right',5)])
	mc.formLayout(evaluationOrderFL,e=True,ac=[(closeB,'top',5,selfPivotB)])
	
	# Show Window
	mc.showWindow(win)
	
def setTwinMatchAttrsFromUI():
	'''
	UI method for Pose Match setup tools
	Setup pose twin attributes from UI
	'''
	# Get selection
	sel = mc.ls(sl=True,type=['transform','joint'])
	if not sel: return
	
	# Window
	win = 'matchRulesUI'
	if not mc.window(win,q=True,ex=True): raise UserInputError('Pose Match UI does not exist!!')
	
	# Pivot
	pivotObj = str(mc.textFieldButtonGrp('matchRulesPivotTFB',q=True,text=True))
	
	# Axis
	axis = str(mc.optionMenuGrp('matchRulesAxisOMG',q=True,v=True)).lower()
	
	# Mode
	mode = mc.optionMenuGrp('matchRulesModeOMG',q=True,sl=True) - 1
	
	# Search/Replace
	search = str(mc.textFieldGrp('matchRulesSearchTFG',q=True,text=True))
	replace = str(mc.textFieldGrp('matchRulesReplaceTFG',q=True,text=True))
	
	# Set match rules attributes
	glTools.common.match.Match().setTwinMatchAttrs(sel,pivotObj,axis,mode,search,replace)
	
def setSelfPivotAttrsFromUI():
	'''
	UI method for Pose Match setup tools
	Setup self pivot pose attributes from UI
	'''
	# Get selection
	sel = mc.ls(sl=True,type=['transform','joint'])
	if not sel: return
	
	# Window
	win = 'matchRulesUI'
	if not mc.window(win,q=True,ex=True): raise UserInputError('Pose Match UI does not exist!!')
	
	# Axis
	axis = str(mc.optionMenuGrp('matchRulesAxisOMG',q=True,v=True)).lower()
	
	# Mode
	mode = mc.optionMenuGrp('matchRulesModeOMG',q=True,sl=True) - 1
	
	# Set match rules attributes
	glTools.common.match.Match().setSelfPivotAttrs(sel,axis,mode)
