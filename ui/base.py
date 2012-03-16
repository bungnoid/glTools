import maya.cmds as mc

import glTools.utils.base

def parentListUI():
	'''
	UI for parentList()
	'''
	# Window
	window = 'parentListUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Parent List')
	
	# Layout
	fl = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	childTXT = mc.text(l='Child List:',al='left')
	childTSL = mc.textScrollList('parentList_childListTSL', allowMultiSelection=True )
	
	parentTXT = mc.text(l='Parent List:',al='left')
	parentTSL = mc.textScrollList('parentList_parentListTSL', allowMultiSelection=True )
	
	parentB = mc.button(label='Parent', c='glTools.ui.base.parentListFromUI()' )
	cancelB = mc.button(label='Cancel', c='mc.deleteUI("'+window+'")' )
	
	# Layout
	mc.formLayout(fl,e=True,af=[(childTXT,'left',5),(childTXT,'top',5)],ap=[(childTXT,'right',5,50)])
	mc.formLayout(fl,e=True,af=[(childTSL,'left',5)],ap=[(childTSL,'right',5,50)],ac=[(childTSL,'top',5,childTXT),(childTSL,'bottom',5,parentB)])
	
	mc.formLayout(fl,e=True,af=[(parentTXT,'right',5),(parentTXT,'top',5)],ap=[(parentTXT,'left',5,50)])
	mc.formLayout(fl,e=True,af=[(parentTSL,'right',5)],ap=[(parentTSL,'left',5,50)],ac=[(parentTSL,'top',5,parentTXT),(parentTSL,'bottom',5,cancelB)])
	
	mc.formLayout(fl,e=True,af=[(parentB,'left',5),(parentB,'bottom',5)],ap=[(parentB,'right',5,50)])
	mc.formLayout(fl,e=True,af=[(cancelB,'right',5),(cancelB,'bottom',5)],ap=[(cancelB,'left',5,50)])
	
	# UI Callbacks
	
	mc.textScrollList(childTSL,e=True,dcc='glTools.ui.utils.selectFromTSL("'+childTSL+'")')
	mc.textScrollList(childTSL,e=True,dkc='glTools.ui.utils.removeFromTSL("'+childTSL+'")')
	
	mc.textScrollList(parentTSL,e=True,dcc='glTools.ui.utils.selectFromTSL("'+parentTSL+'")')
	mc.textScrollList(parentTSL,e=True,dkc='glTools.ui.utils.removeFromTSL("'+parentTSL+'")')
	
	# Popup menu
	
	childPUM = mc.popupMenu(parent=childTSL)
	mc.menuItem(l='Add Selected',c='glTools.ui.utils.addToTSL("'+childTSL+'")')
	mc.menuItem(l='Remove Selected',c='glTools.ui.utils.removeFromTSL("'+childTSL+'")')
	mc.menuItem(l='Clear List',c='mc.textScrollList("'+childTSL+'",e=True,ra=True)')
	mc.menuItem(l='Select Hilited',c='glTools.ui.utils.selectFromTSL("'+childTSL+'")')
	
	parentPUM = mc.popupMenu(parent=parentTSL)
	mc.menuItem(l='Add Selected',c='glTools.ui.utils.addToTSL("'+parentTSL+'")')
	mc.menuItem(l='Remove Selected',c='glTools.ui.utils.removeFromTSL("'+parentTSL+'")')
	mc.menuItem(l='Clear List',c='mc.textScrollList("'+parentTSL+'",e=True,ra=True)')
	mc.menuItem(l='Select Hilited',c='glTools.ui.utils.selectFromTSL("'+parentTSL+'")')
	
	# Display UI 
	mc.showWindow(window)

def parentListFromUI():
	'''
	'''
	# Get child list
	childList = mc.textScrollList('parentList_childListTSL',q=True,ai=True)
	# Get parent list
	parentList = mc.textScrollList('parentList_parentListTSL',q=True,ai=True)
	# Parent child list to parent list
	glTools.utils.base.parentList(childList,parentList)
	
def renameHistoryNodesUI():
	'''
	UI for parentList()
	'''
	# Window
	window = 'renameHistoryNodesUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Rename History Nodes')
	
	# Layout
	cl = mc.columnLayout()
	
	# UI Elements
	nodeTypeTFG = mc.textFieldGrp('renameHist_nodeTypeTFG',label='Node Type')
	nodeSuffixTFG = mc.textFieldGrp('renameHist_nodeSuffixTFG',label='Node Suffix')
	stripSuffixCBG = mc.checkBoxGrp('renameHist_stripSuffixCBG',l='Strip Old Suffix',ncb=1,v1=True)
	
	renameB = mc.button(label='Rename', c='glTools.ui.base.renameHistoryNodesFromUI()' )
	cancelB = mc.button(label='Cancel', c='mc.deleteUI("'+window+'")' )
	
	# Display UI 
	mc.showWindow(window)

def renameHistoryNodesFromUI():
	'''
	'''
	# Get node type and suffix lists 
	nodeType = mc.textFieldGrp('renameHist_nodeTypeTFG',q=True,text=True)
	nodeSuffix = mc.textFieldGrp('renameHist_nodeSuffixTFG',q=True,text=True)
	stripSuffix = mc.checkBoxGrp('renameHist_stripSuffixCBG',q=True,v1=True)
	
	nodeTypeList = nodeType.split(' ')
	nodeSuffixList = nodeSuffix.split(' ')
	
	if len(nodeTypeList) != len(nodeSuffixList):
		if nodeSuffixList:
			raise Exception('Node type and suffix list length mis-match!')
	
	# Get scene selection
	sel = mc.ls(sl=1)
	
	# For each object in selection
	for obj in sel:
		
		# For each node type
		for i in range(len(nodeTypeList)):
			
			# Determine suffix
			nodeSuffix = ''
			if nodeSuffixList: nodeSuffix = nodeSuffixList[i]
			
			# Rename nodes
			glTools.utils.base.renameHistoryNodes(obj,nodeTypeList[i],suffix=nodeSuffix,stripOldSuffix=stripSuffix)
	
