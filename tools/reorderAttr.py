import maya.cmds as mc

import glTools.ui.utils

def reorderAttrUI():
	'''
	'''
	# Window
	window = 'reorderAttrUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Reorder Attributes')
	
	# Layout
	fl = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	objTFB = mc.textFieldButtonGrp('reorderAttrTFB',label='',text='',buttonLabel='Load Selected',cw=[1,5])
	attrTSL = mc.textScrollList('reorderAttrTSL', allowMultiSelection=True )
	moveUpB = mc.button(label='Move Up', c='glTools.tools.reorderAttr.reorderAttrFromUI(0)' )
	moveDnB = mc.button(label='Move Down', c='glTools.tools.reorderAttr.reorderAttrFromUI(1)' )
	moveTpB = mc.button(label='Move to Top', c='glTools.tools.reorderAttr.reorderAttrFromUI(2)' )
	moveBtB = mc.button(label='Move to Bottom', c='glTools.tools.reorderAttr.reorderAttrFromUI(3)' )
	cancelB = mc.button(label='Cancel', c='mc.deleteUI("'+window+'")' )
	
	# Form Layout
	mc.formLayout(fl,e=True,af=[(objTFB,'left',5),(objTFB,'top',5),(objTFB,'right',5)])
	mc.formLayout(fl,e=True,af=[(moveUpB,'left',5),(moveUpB,'right',5)],ac=[(moveUpB,'bottom',5,moveDnB)])
	mc.formLayout(fl,e=True,af=[(moveDnB,'left',5),(moveDnB,'right',5)],ac=[(moveDnB,'bottom',5,moveTpB)])
	mc.formLayout(fl,e=True,af=[(moveTpB,'left',5),(moveTpB,'right',5)],ac=[(moveTpB,'bottom',5,moveBtB)])
	mc.formLayout(fl,e=True,af=[(moveBtB,'left',5),(moveBtB,'right',5)],ac=[(moveBtB,'bottom',5,cancelB)])
	mc.formLayout(fl,e=True,af=[(cancelB,'left',5),(cancelB,'right',5),(cancelB,'bottom',5)])
	mc.formLayout(fl,e=True,af=[(attrTSL,'left',5),(attrTSL,'right',5)],ac=[(attrTSL,'top',5,objTFB),(attrTSL,'bottom',5,moveUpB)])
	
	# UI callback commands
	mc.textFieldButtonGrp('reorderAttrTFB',e=True,bc='glTools.tools.reorderAttr.reorderAttrLoadSelected()')
	
	# Load selection
	sel = mc.ls(sl=1)
	if sel: reorderAttrLoadSelected()
	
	# Display UI 
	mc.showWindow(window)
	
def reorderAttrLoadSelected():
	'''
	'''
	# Load Selected to Text Field
	glTools.ui.utils.loadObjectSel('reorderAttrTFB')
	
	# Refresh attribute list
	reorderAttrRefreshList()
	
def reorderAttrRefreshList(selList=[]):
	'''
	'''
	# Get object
	obj = mc.textFieldButtonGrp('reorderAttrTFB',q=True,text=True)
	
	# Get attr list
	udAttrList = mc.listAttr(obj,ud=True)
	cbAttrList = []
	tmpAttrList = mc.listAttr(obj,k=True)
	if tmpAttrList: cbAttrList.extend(tmpAttrList)
	tmpAttrList = mc.listAttr(obj,cb=True)
	if tmpAttrList: cbAttrList.extend(tmpAttrList)
	allAttrList = [i for i in udAttrList if cbAttrList.count(i)]
	
	# Update attribute text scroll list
	mc.textScrollList('reorderAttrTSL',e=True,ra=True)
	for attr in allAttrList: mc.textScrollList('reorderAttrTSL',e=True,a=attr)
	
	# Select list items
	selAttrList = []
	if selList: selAttrList = list(set(selList).intersection(set(allAttrList)))
	if selAttrList: mc.textScrollList('reorderAttrTSL',e=True,si=selAttrList)

def reorderAttrFromUI(dir):
	'''
	Reorder attributes based on info from the control UI
	@param dir: Direction to move attribute in current oreder
	@type dir: int
	'''
	# Get UI info
	obj = mc.textFieldButtonGrp('reorderAttrTFB',q=True,text=True)
	attrList = mc.textScrollList('reorderAttrTSL',q=True,si=True)
	
	# Check object
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!')
	
	# Check attributes
	for attr in attrList:
		if not mc.objExists(obj+'.'+attr):
			raise Exception('Attribute "'+obj+'.'+attr+'" does not exist!')
	
	# Get attr list
	udAttrList = mc.listAttr(obj,ud=True)
	keyAttrList = mc.listAttr(obj,k=True)
	cbAttrList = mc.listAttr(obj,cb=True)
	allAttrList = [i for i in udAttrList if keyAttrList.count(i) or cbAttrList.count(i)]
	allAttrLen = len(allAttrList)
	
	# Reorder Attributes
	for attr in attrList:
		
		# Get relative attribute index 
		attrInd = allAttrList.index(attr)
		
		if dir == 0: # Move Up
			
			print 'move up'
			
			if not attrInd: continue
				
			mc.renameAttr(obj+'.'+allAttrList[attrInd-1],allAttrList[attrInd-1]+'XXX')
			mc.renameAttr(obj+'.'+allAttrList[attrInd-1]+'XXX',allAttrList[attrInd-1])
			
			for i in allAttrList[attrInd+1:]:
				mc.renameAttr(obj+'.'+i,i+'XXX')
				mc.renameAttr(obj+'.'+i+'XXX',i)
			
		if dir == 1: # Move Down
			
			print 'move down'
			
			if attrInd == (allAttrLen-1): continue
			
			mc.renameAttr(obj+'.'+allAttrList[attrInd],allAttrList[attrInd]+'XXX')
			mc.renameAttr(obj+'.'+allAttrList[attrInd]+'XXX',allAttrList[attrInd])
			
			if attrInd >= (allAttrLen-1): continue
			
			for i in allAttrList[attrInd+2:]:
				mc.renameAttr(obj+'.'+i,i+'XXX')
				mc.renameAttr(obj+'.'+i+'XXX',i)
			
		
		if dir == 2: # Move to Top
			
			print 'move to top'
			
			for i in range(len(allAttrList)):
				if i == attrInd: continue
				mc.renameAttr(obj+'.'+allAttrList[i],allAttrList[i]+'XXX')
				mc.renameAttr(obj+'.'+allAttrList[i]+'XXX',allAttrList[i])
		
		if dir == 3: # Move to Bottom
			
			print 'move to bottom'
			
			mc.renameAttr(obj+'.'+allAttrList[attrInd],allAttrList[attrInd]+'XXX')
			mc.renameAttr(obj+'.'+allAttrList[attrInd]+'XXX',allAttrList[attrInd])
	
	# Refresh attribute list
	reorderAttrRefreshList(attrList)
	
	# Refresh UI
	channelBox = 'MayaWindow|mayaMainWindowForm|formLayout3|formLayout11|formLayout32|formLayout33|ChannelsLayersPaneLayout|formLayout36|menuBarLayout1|frameLayout1|mainChannelBox'
	mc.channelBox(channelBox,e=True,update=True)
