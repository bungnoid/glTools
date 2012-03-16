import maya.cmds as mc
import maya.mel as mm

def ui():
	'''
	'''
	# Window
	win = 'graphFilterUI'
	if mc.window(win,q=True,ex=True): mc.deleteUI(win)
	win = mc.window(win,t='Graph Editor Filter',mxb=True,mnb=True,s=True,wh=[248,210])
		
	# Layout
	fl = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	graphFilterAttrListTSL = mc.textScrollList('graphFilter_attrListTSL',w=120,nr=8,ams=True)
	
	graphFilterModeRBG = mc.radioButtonGrp('graphFilter_modeRBG',label='Mode',labelArray2=['Replace','Append'],nrb=2,sl=1)
	
	graphEditorB = mc.button(l='Graph Editor',c='mm.eval("GraphEditor")')
	allCurveB = mc.button(l='All Curves',c='displayAllCurves()')
	clearViewB = mc.button(l='Clear View',c='mc.selectionConnection("graphEditor1FromOutliner",e=True,clear=True)')
	
	graphFilterFilterB = mc.button('graphFilter_filterB',l='Filter Selected',c='glTools.tools.graphFilter.filterCurves()')
	graphFilterSelectB = mc.button('graphFilter_selectB',l='Select All',c='glTools.tools.graphFilter.selectAll()')
	graphFilterClearB = mc.button('graphFilter_clearB',l='Clear list',c='mc.textScrollList("graphFilter_attrListTSL",e=True,ra=True)')
	graphFilterUpdateB = mc.button('graphFilter_updateB',l='Update List',c='glTools.tools.graphFilter.updateAttrList()')
	
	# Form Layout
	mc.formLayout(fl,e=True,af=[(graphFilterAttrListTSL,'left',5),(graphFilterAttrListTSL,'bottom',5)],ap=[(graphFilterAttrListTSL,'right',5,50)],ac=[(graphFilterAttrListTSL,'top',5,graphFilterModeRBG)])
	mc.formLayout(fl,e=True,af=[(graphFilterModeRBG,'left',5),(graphFilterModeRBG,'right',5)],ac=[(graphFilterModeRBG,'top',5,graphEditorB)])
	mc.formLayout(fl,e=True,af=[(graphEditorB,'left',5),(graphEditorB,'top',5)],ap=[(graphEditorB,'right',5,33)])
	mc.formLayout(fl,e=True,af=[(allCurveB,'top',5)],ap=[(allCurveB,'left',5,33),(allCurveB,'right',5,66)])
	mc.formLayout(fl,e=True,af=[(clearViewB,'right',5),(clearViewB,'top',5)],ap=[(clearViewB,'left',5,66)])
	mc.formLayout(fl,e=True,af=[(graphFilterFilterB,'right',5)],ap=[(graphFilterFilterB,'left',5,50)],ac=[(graphFilterFilterB,'top',5,graphFilterModeRBG)])
	mc.formLayout(fl,e=True,af=[(graphFilterSelectB,'right',5)],ap=[(graphFilterSelectB,'left',5,50)],ac=[(graphFilterSelectB,'top',5,graphFilterFilterB)])
	mc.formLayout(fl,e=True,af=[(graphFilterClearB,'right',5)],ap=[(graphFilterClearB,'left',5,50)],ac=[(graphFilterClearB,'top',5,graphFilterSelectB)])
	mc.formLayout(fl,e=True,af=[(graphFilterUpdateB,'right',5)],ap=[(graphFilterUpdateB,'left',5,50)],ac=[(graphFilterUpdateB,'top',5,graphFilterClearB)])
	
	# Update keyable attribute list
	updateAttrList()
	
	# Show window
	mc.showWindow(win)

def updateAttrList():
	'''
	'''
	# Clear attribute list
	mc.textScrollList('graphFilter_attrListTSL',e=True,ra=True)
	
	# Get current selection
	sel = mc.ls(sl=True)
	if not sel: return
	
	# List all keyable attributes
	attrList = list(set(mc.listAttr(sel,k=True)))
	attrList.sort()
	
	# Update textScrollList
	for attr in attrList: mc.textScrollList('graphFilter_attrListTSL',e=True,a=attr)
	
	# Return result
	return attrList

def selectAll():
	'''
	'''
	# Select all attributes in the list
	for i in range(mc.textScrollList('graphFilter_attrListTSL',q=True,ni=True)):
		mc.textScrollList('graphFilter_attrListTSL',e=True,sii=(i+1))

def displayAllCurves():
	'''
	'''
	# Display all attribute curves
	sel = mc.selectionConnection('graphEditorList',q=True,object=True)
	for obj in sel: mc.selectionConnection('graphEditor1FromOutliner',e=True,select=obj)

def addCurveToEditor(attr):
	'''
	'''
	# Get current selection
	sel = mc.ls(sl=True)
	for obj in sel:
		objAttr = obj+'.'+attr
		# Check attr
		if mc.objExists(objAttr):
			# Add to graphEditor
			mc.selectionConnection('graphEditor1FromOutliner',e=True,select=objAttr)

def filterCurves():
	'''
	'''
	# Check attribute list selection
	if mc.textScrollList('graphFilter_attrListTSL',q=True,nsi=True):
		
		# Check mode
		if mc.radioButtonGrp('graphFilter_modeRBG',q=True,sl=True) == 1:
			mc.selectionConnection('graphEditor1FromOutliner',e=True,clear=True)
		attrs = mc.textScrollList('graphFilter_attrListTSL',q=True,si=True) 
		for attr in attrs: addCurveToEditor(attr)
	 
	# Update UI
	mm.eval('GraphEditor')
	mm.eval('SelectAllMarkingMenu') 
	mm.eval('buildSelectAllMM')
	mm.eval('SelectAllMarkingMenuPopDown')
