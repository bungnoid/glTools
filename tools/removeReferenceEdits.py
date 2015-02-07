import maya.mel as mm
import maya.cmds as mc

import glTools.utils.reference

def removeReferenceEditsUI():
	'''
	'''
	# Define Local Command Prefix
	cmdPrefix = 'import glTools.tools.removeReferenceEdits;reload(glTools.tools.removeReferenceEdits);glTools.tools.removeReferenceEdits.'
	
	# ================
	# - Build Window -
	# ================
	
	window = 'removeReferenceEditsUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Remove Reference Edits')
	
	# ===============
	# - UI Elements -
	# ===============
	
	# Layout
	FL = mc.formLayout()
	
	refListTXT = mc.text(label='Reference List')
	refListTSL = mc.textScrollList('refEdits_refListTSL',allowMultiSelection=False)
	nodeListTXT = mc.text(label='Node List')
	nodeListTSL = mc.textScrollList('refEdits_nodeListTSL',allowMultiSelection=True)
	nodeSearchTFG = mc.textFieldButtonGrp('refEdits_nodeSearchTFG',label='Node Search',buttonLabel='Clear',text='',cw=(1,80))
	
	nodeSearchSEP = mc.separator(style='single')
	
	showNamespaceCBG = mc.checkBoxGrp('refEdits_showNamespaceCBG',numberOfCheckBoxes=1,label='Show Namespace',v1=False)
	showLongNamesCBG = mc.checkBoxGrp('refEdits_showLongNamesCBG',numberOfCheckBoxes=1,label='Show Long Names',v1=False)
	showSuccessEditsCBG = mc.checkBoxGrp('refEdits_showSuccessEditsCBG',numberOfCheckBoxes=1,label='Show Successful Edits',v1=True)
	showFailedEditsCBG = mc.checkBoxGrp('refEdits_showFailedEditsCBG',numberOfCheckBoxes=1,label='Show Failed Edits',v1=True)
	
	showDetailsSEP = mc.separator(style='single')
	
	# Edit Command Check Boxes
	parentCBG = mc.checkBoxGrp('refEdits_parentCBG',numberOfCheckBoxes=1,label='parent',v1=True)
	setAttrCBG = mc.checkBoxGrp('refEdits_setAttrCBG',numberOfCheckBoxes=1,label='setAttr',v1=True)
	addAttrCBG = mc.checkBoxGrp('refEdits_addAttrCBG',numberOfCheckBoxes=1,label='addAttr',v1=True)
	delAttrCBG = mc.checkBoxGrp('refEdits_delAttrCBG',numberOfCheckBoxes=1,label='deleteAttr',v1=True)
	conAttrCBG = mc.checkBoxGrp('refEdits_conAttrCBG',numberOfCheckBoxes=1,label='connectAttr',v1=True)
	disconAttrCBG = mc.checkBoxGrp('refEdits_disconAttrCBG',numberOfCheckBoxes=1,label='disconnectAttr',v1=True)
	
	# Buttons
	printEditsAttrB = mc.button(label='Print Edit Attributes',c=cmdPrefix+'printNodeEditAttributes()')
	printEditsCmdsB = mc.button(label='Print Edit Commands',c=cmdPrefix+'printNodeEditCommands()')
	removeEditsB = mc.button(label='Remove Edits',c=cmdPrefix+'removeReferenceEditsFromUI()')
	closeB = mc.button(label='Close',c='mc.deleteUI("'+window+'")')
	
	# ===============
	# - Pop-up Menu -
	# ===============
	
	# Reference List
	mc.popupMenu(parent=refListTSL)
	mc.menuItem('Reload Reference',c=cmdPrefix+'reloadReferenceFromUI()')
	mc.menuItem('Unload Reference',c=cmdPrefix+'unloadReferenceFromUI()')
	mc.menuItem('Remove Reference',c=cmdPrefix+'removeReferenceFromUI()')
	mc.menuItem('Import Reference',c=cmdPrefix+'importReferenceFromUI()')
	
	# Node List
	mc.popupMenu(parent=nodeListTSL)
	mc.menuItem('Select',c=cmdPrefix+'selectNode()')
	mc.menuItem('Print Edit Attributes',c=cmdPrefix+'printNodeEditAttributes()')
	mc.menuItem('Print Edit Commands',c=cmdPrefix+'printNodeEditCommands()')
	
	# ================
	# - UI Callbacks -
	# ================
	
	loadNodesCmd = cmdPrefix+'loadNodeList()'
	
	# Select Reference
	mc.textScrollList(refListTSL,e=True,sc=loadNodesCmd)
	
	# Search Node Field
	mc.textFieldButtonGrp(nodeSearchTFG,e=True,cc=cmdPrefix+'filterNodeList()')
	mc.textFieldButtonGrp(nodeSearchTFG,e=True,bc=cmdPrefix+'clearSeachField()')
	
	# Show Details
	mc.checkBoxGrp(showNamespaceCBG,e=True,cc=loadNodesCmd)
	mc.checkBoxGrp(showLongNamesCBG,e=True,cc=loadNodesCmd)
	mc.checkBoxGrp(showSuccessEditsCBG,e=True,cc=loadNodesCmd)
	mc.checkBoxGrp(showFailedEditsCBG,e=True,cc=loadNodesCmd)
	
	# Edit Commands
	mc.checkBoxGrp(parentCBG,e=True,cc=loadNodesCmd)
	mc.checkBoxGrp(setAttrCBG,e=True,cc=loadNodesCmd)
	mc.checkBoxGrp(addAttrCBG,e=True,cc=loadNodesCmd)
	mc.checkBoxGrp(delAttrCBG,e=True,cc=loadNodesCmd)
	mc.checkBoxGrp(conAttrCBG,e=True,cc=loadNodesCmd)
	mc.checkBoxGrp(disconAttrCBG,e=True,cc=loadNodesCmd)
	
	# ===============
	# - Form Layout -
	# ===============
	
	mc.formLayout(FL,e=True,af=[(refListTXT,'top',5),(refListTXT,'left',5)],ap=[(refListTXT,'right',5,33)])
	mc.formLayout(FL,e=True,af=[(refListTSL,'bottom',5),(refListTSL,'left',5)],ac=[(refListTSL,'top',5,refListTXT)],ap=[(refListTSL,'right',5,33)])
	mc.formLayout(FL,e=True,af=[(nodeListTXT,'top',5)],ac=[(nodeListTXT,'left',5,refListTXT)],ap=[(nodeListTXT,'right',5,66)])
	mc.formLayout(FL,e=True,af=[(nodeListTSL,'bottom',5)],ac=[(nodeListTSL,'left',5,refListTSL),(nodeListTSL,'top',5,nodeListTXT)],ap=[(nodeListTSL,'right',5,66)])
	mc.formLayout(FL,e=True,af=[(nodeSearchTFG,'top',5),(nodeSearchTFG,'right',5)],ac=[(nodeSearchTFG,'left',5,nodeListTXT)])
	
	mc.formLayout(FL,e=True,af=[(nodeSearchSEP,'right',5)],ac=[(nodeSearchSEP,'top',5,nodeSearchTFG),(nodeSearchSEP,'left',5,nodeListTXT)])
	
	mc.formLayout(FL,e=True,af=[(showNamespaceCBG,'right',5)],ac=[(showNamespaceCBG,'top',5,nodeSearchSEP)])
	mc.formLayout(FL,e=True,af=[(showLongNamesCBG,'right',5)],ac=[(showLongNamesCBG,'top',5,showNamespaceCBG)])
	mc.formLayout(FL,e=True,af=[(showSuccessEditsCBG,'right',5)],ac=[(showSuccessEditsCBG,'top',5,showLongNamesCBG)])
	mc.formLayout(FL,e=True,af=[(showFailedEditsCBG,'right',5)],ac=[(showFailedEditsCBG,'top',5,showSuccessEditsCBG)])
	
	mc.formLayout(FL,e=True,af=[(showDetailsSEP,'right',5)],ac=[(showDetailsSEP,'top',5,showFailedEditsCBG),(showDetailsSEP,'left',5,nodeListTXT)])
	
	mc.formLayout(FL,e=True,af=[(parentCBG,'right',5)],ac=[(parentCBG,'top',5,showDetailsSEP)])
	mc.formLayout(FL,e=True,af=[(setAttrCBG,'right',5)],ac=[(setAttrCBG,'top',5,parentCBG)])
	mc.formLayout(FL,e=True,af=[(addAttrCBG,'right',5)],ac=[(addAttrCBG,'top',5,setAttrCBG)])
	mc.formLayout(FL,e=True,af=[(delAttrCBG,'right',5)],ac=[(delAttrCBG,'top',5,addAttrCBG)])
	mc.formLayout(FL,e=True,af=[(conAttrCBG,'right',5)],ac=[(conAttrCBG,'top',5,delAttrCBG)])
	mc.formLayout(FL,e=True,af=[(disconAttrCBG,'right',5)],ac=[(disconAttrCBG,'top',5,conAttrCBG)])
	
	mc.formLayout(FL,e=True,af=[(printEditsAttrB,'right',5)],ac=[(printEditsAttrB,'bottom',5,printEditsCmdsB),(printEditsAttrB,'left',5,nodeListTSL)])
	mc.formLayout(FL,e=True,af=[(printEditsCmdsB,'right',5)],ac=[(printEditsCmdsB,'bottom',5,removeEditsB),(printEditsCmdsB,'left',5,nodeListTSL)])
	mc.formLayout(FL,e=True,af=[(removeEditsB,'right',5)],ac=[(removeEditsB,'bottom',5,closeB),(removeEditsB,'left',5,nodeListTSL)])
	mc.formLayout(FL,e=True,af=[(closeB,'right',5),(closeB,'bottom',5)],ac=[(closeB,'left',5,nodeListTSL)])
	
	# ===============
	# - Show Window -
	# ===============
	
	mc.showWindow(window)
	
	# Load Reference List
	loadReferenceList()

def reloadReferenceFromUI():
	'''
	Reload selected reference
	'''
	refList = mc.textScrollList('refEdits_refListTSL',q=True,si=True) or []
	for ref in refList: glTools.utils.reference.reloadReference(ref,verbose=True)

def unloadReferenceFromUI():
	'''
	Unload selected reference
	'''
	refList = mc.textScrollList('refEdits_refListTSL',q=True,si=True) or []
	for ref in refList: glTools.utils.reference.unloadReference(ref,verbose=True)

def removeReferenceFromUI():
	'''
	Remove selected reference
	'''
	refList = mc.textScrollList('refEdits_refListTSL',q=True,si=True) or []
	for ref in refList: glTools.utils.reference.removeReference(ref,verbose=True)
	loadReferenceList()
	loadNodeList()

def importReferenceFromUI():
	'''
	Import selected reference
	'''
	refList = mc.textScrollList('refEdits_refListTSL',q=True,si=True) or []
	for ref in refList: glTools.utils.reference.importReference(ref,verbose=True)
	loadReferenceList()
	loadNodeList()

def clearSeachField():
	'''
	'''
	# Clear Text Field
	mc.textFieldButtonGrp('refEdits_nodeSearchTFG',e=True,text='')
	# Reload Node List
	loadNodeList()

def selectNode():
	'''
	Select node from reference edits UI.
	'''
	# Get Selected Ref Node 
	refNode = mc.textScrollList('refEdits_refListTSL',q=True,si=True)
	if not refNode: return
	refNS = glTools.utils.reference.getNamespace(refNode[0])+':'
	
	# Get Selected Nodes
	nodeList = mc.textScrollList('refEdits_nodeListTSL',q=True,si=True)
	if not nodeList: return
	
	# Select Nodes
	selNodes = []
	for node in nodeList:
	
		# Check Node
		editNode = node
		if not mc.objExists(node): node = node.split('|')[-1]
		if not mc.objExists(node): node = refNS+node
		if not mc.objExists(node): raise Exception('Reference edit node "'+editNode+'" not found!')
		
		# Append to Selection List
		selNodes.append(node)
	
	# Select Node
	if selNodes: mc.select(selNodes)

def loadReferenceList():
	'''
	List all existing reference nodes to the UI textScrollList
	'''
	refList = mc.ls(type='reference')
	if 'sharedReferenceNode' in refList: refList.remove('sharedReferenceNode')
	for ref in refList: mc.textScrollList('refEdits_refListTSL',e=True,a=ref)

def loadNodeList():
	'''
	'''
	# Get Selected Ref Node 
	refNode = mc.textScrollList('refEdits_refListTSL',q=True,si=True) or []
	
	# Check Ref Node
	if not refNode:
		# No Reference Selected, Clear Node List
		mc.textScrollList('refEdits_nodeListTSL',e=True,ra=True)
		return
	
	# Get Show Details
	showNamespace = mc.checkBoxGrp('refEdits_showNamespaceCBG',q=True,v1=True)
	showDagPath = mc.checkBoxGrp('refEdits_showLongNamesCBG',q=True,v1=True)
	successfulEdits = mc.checkBoxGrp('refEdits_showSuccessEditsCBG',q=True,v1=True)
	failedEdits = mc.checkBoxGrp('refEdits_showFailedEditsCBG',q=True,v1=True)
		
	# Get Edit Commands
	editCmd_parent = mc.checkBoxGrp('refEdits_parentCBG',q=True,v1=True)
	editCmd_setAttr = mc.checkBoxGrp('refEdits_setAttrCBG',q=True,v1=True)
	editCmd_addAttr = mc.checkBoxGrp('refEdits_addAttrCBG',q=True,v1=True)
	editCmd_delAttr = mc.checkBoxGrp('refEdits_delAttrCBG',q=True,v1=True)
	editCmd_conAttr = mc.checkBoxGrp('refEdits_conAttrCBG',q=True,v1=True)
	editCmd_disconAttr = mc.checkBoxGrp('refEdits_disconAttrCBG',q=True,v1=True)
	if not (editCmd_parent or editCmd_setAttr or editCmd_addAttr or editCmd_delAttr or editCmd_conAttr or editCmd_disconAttr):
		# No Edit Commands Checked, Clear Node List 
		mc.textScrollList('refEdits_nodeListTSL',e=True,ra=True)
		return
	
	# Get Reference Edit Nodes
	nodeList = glTools.utils.reference.getEditNodes(	refNode[0],
													showNamespace=showNamespace,
													showDagPath=showDagPath,
													successfulEdits=successfulEdits,
													failedEdits=failedEdits,
													parent=editCmd_parent,
													setAttr=editCmd_setAttr,
													addAttr=editCmd_addAttr,
													deleteAttr=editCmd_delAttr,
													connectAttr=editCmd_conAttr,
													disconnectAttr=editCmd_disconAttr	)
	
	# Remove Duplicates and Sort
	nodeList = list(set([i for i in nodeList])) or []
	nodeList.sort()
		
	# Apply Node List
	mc.textScrollList('refEdits_nodeListTSL',e=True,ra=True)
	for node in nodeList: mc.textScrollList('refEdits_nodeListTSL',e=True,a=node)
	
	# Filter List
	filterNodeList()

def filterNodeList():
	'''
	'''
	# Filter List
	nodeSearchStr = mc.textFieldButtonGrp('refEdits_nodeSearchTFG',q=True,text=True)
	if not nodeSearchStr: return
	
	# Get Node List
	nodeList = mc.textScrollList('refEdits_nodeListTSL',q=True,ai=True)
	if not nodeList: return
	
	# Check Negative Filter
	if nodeSearchStr.startswith('!'):
		if nodeSearchStr.startswith('!*'):
			nodeList = list(set([i for i in nodeList if not i.endswith(nodeSearchStr[2:])]))
		elif nodeSearchStr.endswith('*'):
			nodeList = list(set([i for i in nodeList if not i.startswith(nodeSearchStr[1:-1])]))
		else:
			nodeList = list(set([i for i in nodeList if not nodeSearchStr[1:] in i]))
	else:
		if nodeSearchStr.startswith('*'):
			nodeList = list(set([i for i in nodeList if i.endswith(nodeSearchStr[1:])]))
		elif nodeSearchStr.endswith('*'):
			nodeList = list(set([i for i in nodeList if i.startswith(nodeSearchStr[:-1])]))
		else:
			nodeList = list(set([i for i in nodeList if nodeSearchStr in i]))
	
	# Apply Filtered Node List
	mc.textScrollList('refEdits_nodeListTSL',e=True,ra=True)
	for node in sorted(nodeList): mc.textScrollList('refEdits_nodeListTSL',e=True,a=node)

def printNodeEditAttributes():
	'''
	Print list of node attributes that have reference edits.
	'''
	# Get Reference and Node Selection
	refList = mc.textScrollList('refEdits_refListTSL',q=True,si=True) or []
	nodeList = mc.textScrollList('refEdits_nodeListTSL',q=True,si=True) or []
	
	# Get Show Details
	showNamespace = mc.checkBoxGrp('refEdits_showNamespaceCBG',q=True,v1=True)
	showDagPath = mc.checkBoxGrp('refEdits_showLongNamesCBG',q=True,v1=True)
	successfulEdits = mc.checkBoxGrp('refEdits_showSuccessEditsCBG',q=True,v1=True)
	failedEdits = mc.checkBoxGrp('refEdits_showFailedEditsCBG',q=True,v1=True)
	
	# Get Edit Commands
	editCmd_parent = mc.checkBoxGrp('refEdits_parentCBG',q=True,v1=True)
	editCmd_setAttr = mc.checkBoxGrp('refEdits_setAttrCBG',q=True,v1=True)
	editCmd_addAttr = mc.checkBoxGrp('refEdits_addAttrCBG',q=True,v1=True)
	editCmd_delAttr = mc.checkBoxGrp('refEdits_delAttrCBG',q=True,v1=True)
	editCmd_conAttr = mc.checkBoxGrp('refEdits_conAttrCBG',q=True,v1=True)
	editCmd_disconAttr = mc.checkBoxGrp('refEdits_disconAttrCBG',q=True,v1=True)
	
	# Get Edit Commands
	for refNode in refList:
		
		# Get Reference Namespace
		ns = ''
		if showNamespace: ns = glTools.utils.reference.getNamespace(refNode)+':'
		
		for node in nodeList:
			
			# Get Edit Attributes
			attrList = glTools.utils.reference.getEditAttrs(	refNode,
															node,
															showNamespace=showNamespace,
															showDagPath=showDagPath,
															successfulEdits=successfulEdits,
															failedEdits=failedEdits,
															parent=editCmd_parent,
															setAttr=editCmd_setAttr,
															addAttr=editCmd_addAttr,
															deleteAttr=editCmd_delAttr,
															connectAttr=editCmd_conAttr,
															disconnectAttr=editCmd_disconAttr	)
			
			# Append Output List
			if attrList:
				
				# Remove Duplicates and Sort
				attrList = list(set(attrList))
				attrList.sort()
				
				# Print Result
				print('\n=== Edit Attributes: '+node+' ===\n')
				for attr in attrList: print attr

def printNodeEditCommands():
	'''
	Print list of node edit commands.
	'''
	# Get Reference and Node Selection
	refList = mc.textScrollList('refEdits_refListTSL',q=True,si=True) or []
	nodeList = mc.textScrollList('refEdits_nodeListTSL',q=True,si=True) or []
	
	# Get Show Details
	showNamespace = mc.checkBoxGrp('refEdits_showNamespaceCBG',q=True,v1=True)
	showDagPath = mc.checkBoxGrp('refEdits_showLongNamesCBG',q=True,v1=True)
	successfulEdits = mc.checkBoxGrp('refEdits_showSuccessEditsCBG',q=True,v1=True)
	failedEdits = mc.checkBoxGrp('refEdits_showFailedEditsCBG',q=True,v1=True)
	
	# Get Edit Commands
	editCmd_parent = mc.checkBoxGrp('refEdits_parentCBG',q=True,v1=True)
	editCmd_setAttr = mc.checkBoxGrp('refEdits_setAttrCBG',q=True,v1=True)
	editCmd_addAttr = mc.checkBoxGrp('refEdits_addAttrCBG',q=True,v1=True)
	editCmd_delAttr = mc.checkBoxGrp('refEdits_delAttrCBG',q=True,v1=True)
	editCmd_conAttr = mc.checkBoxGrp('refEdits_conAttrCBG',q=True,v1=True)
	editCmd_disconAttr = mc.checkBoxGrp('refEdits_disconAttrCBG',q=True,v1=True)
	
	# Get Edit Commands
	for refNode in refList:
		
		# Get Reference Namespace
		ns = ''
		if showNamespace: ns = glTools.utils.reference.getNamespace(refNode)+':'
		
		for node in nodeList:
			cmdList = glTools.utils.reference.getEditCommands(	refNode,
																ns+node,
																showNamespace=showNamespace,
																showDagPath=showDagPath,
																successfulEdits=successfulEdits,
																failedEdits=failedEdits,
																parent=editCmd_parent,
																setAttr=editCmd_setAttr,
																addAttr=editCmd_addAttr,
																deleteAttr=editCmd_delAttr,
																connectAttr=editCmd_conAttr,
																disconnectAttr=editCmd_disconAttr	)
			
			# Append Output List
			if cmdList:
				
				# Remove Duplicates and Sort
				cmdList = list(set(cmdList))
				
				# Print Result
				print('\n=== Edit Commands: '+node+' ===\n')
				for cmd in cmdList: print cmd

def removeReferenceEditsFromUI():
	'''
	Remove Reference Edits
	'''
	# =======================
	# - Get Details From UI -
	# =======================
	
	# Get Reference and Node Selection
	refList = mc.textScrollList('refEdits_refListTSL',q=True,si=True) or []
	nodeList = mc.textScrollList('refEdits_nodeListTSL',q=True,si=True) or []
	
	# Get Edit Details
	successfulEdits = mc.checkBoxGrp('refEdits_showSuccessEditsCBG',q=True,v1=True)
	failedEdits = mc.checkBoxGrp('refEdits_showFailedEditsCBG',q=True,v1=True)
	
	# Get Edit Commands
	editCmd_parent = mc.checkBoxGrp('refEdits_parentCBG',q=True,v1=True)
	editCmd_setAttr = mc.checkBoxGrp('refEdits_setAttrCBG',q=True,v1=True)
	editCmd_addAttr = mc.checkBoxGrp('refEdits_addAttrCBG',q=True,v1=True)
	editCmd_delAttr = mc.checkBoxGrp('refEdits_delAttrCBG',q=True,v1=True)
	editCmd_conAttr = mc.checkBoxGrp('refEdits_conAttrCBG',q=True,v1=True)
	editCmd_disconAttr = mc.checkBoxGrp('refEdits_disconAttrCBG',q=True,v1=True)
	
	# Get Show Namespace
	showNamespace = mc.checkBoxGrp('refEdits_showNamespaceCBG',q=True,v1=True)
	
	# ==========================
	# - Remove Reference Edits -
	# ==========================
	
	for refNode in refList:
		
		# Check Reference Loaded
		refLoaded = glTools.utils.reference.isLoaded(refNode)
		if refLoaded: mc.file(unloadReference=refNode)
		
		# Get Reference Namespace
		ns = ''
		if not showNamespace: ns = glTools.utils.reference.getNamespace(refNode)+':'
		
		if not nodeList:
			
			# Remove All Reference Edits
			glTools.utils.reference.removeReferenceEdits(	refNode,
															node='',
															successfulEdits=successfulEdits,
															failedEdits=failedEdits,
															parent=editCmd_parent,
															setAttr=editCmd_setAttr,
															addAttr=editCmd_addAttr,
															deleteAttr=editCmd_delAttr,
															connectAttr=editCmd_conAttr,
															disconnectAttr=editCmd_disconAttr	)
		
		for node in nodeList:
			
			# Remove Node Edits
			glTools.utils.reference.removeReferenceEdits(	refNode,
															ns+node,
															successfulEdits=successfulEdits,
															failedEdits=failedEdits,
															parent=editCmd_parent,
															setAttr=editCmd_setAttr,
															addAttr=editCmd_addAttr,
															deleteAttr=editCmd_delAttr,
															connectAttr=editCmd_conAttr,
															disconnectAttr=editCmd_disconAttr	)
		
		# Reload Reference
		if refLoaded: mc.file(loadReference=refNode)
