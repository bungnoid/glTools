import maya.cmds as mc
import maya.mel as mm

import glTools.utils.base
import glTools.utils.curve
import glTools.utils.mesh
import glTools.utils.namespace
import glTools.utils.osUtils
import glTools.utils.stringUtils
import glTools.utils.surface

import re

class UserInputError(Exception): pass
class UIError(Exception): pass

# ==============
# - Text Field -
# ==============

def loadFilePath(textField,fileFilter=None,caption='Load File',startDir=None):
	'''
	Select a file path to load into a specified textField.
	@param textField: TextField UI object to load file path to
	@type textField: str
	@param fileFilter: File filter to apply to the file selection UI
	@type fileFilter: str
	@param caption: File selection UI caption string
	@type caption: str
	@param startDir: Directory to start browsing from. In None, use the default or last selected directory.
	@type startDir: str
	'''
	# Get File Path
	filePath = mc.fileDialog2(	fileFilter=fileFilter,
								dialogStyle=2,
								fileMode=1,
								caption=caption,
								okCaption='Load',
								startingDirectory=startDir )
	
	# Check File Path
	if not filePath:
		print('Invalid file path!')
		return
	
	# Load File Path to TextField
	if mc.textField(textField,q=True,ex=True):
		mc.textField(textField,e=True,text=filePath[0])
	elif mc.textFieldGrp(textField,q=True,ex=True):
		mc.textFieldGrp(textField,e=True,text=filePath[0])
	elif mc.textFieldButtonGrp(textField,q=True,ex=True):
		mc.textFieldButtonGrp(textField,e=True,text=filePath[0])
	else:
		print('UI element "" is not a valid textField, textFieldGrp or textFieldButtonGrp!')
		return
	
	# Return Result
	return filePath[0]

def loadDirectoryPath(textField,caption='Load Directory',startDir=None):
	'''
	Select a file path to load into a specified textField.
	@param textField: TextField UI object to load file path to
	@type textField: str
	@param caption: File selection UI caption string
	@type caption: str
	@param startDir: Directory to start browsing from. In None, use the default or last selected directory.
	@type startDir: str
	'''
	# Get File Path
	dirPath = mc.fileDialog2(	dialogStyle=2,
								fileMode=3,
								caption=caption,
								okCaption='Load',
								startingDirectory=startDir )
	
	# Check File Path
	if not dirPath:
		print('Invalid directory path!')
		return
	
	# Load File Path to TextField
	if mc.textField(textField,q=True,ex=True):
		mc.textField(textField,e=True,text=dirPath[0])
	elif mc.textFieldGrp(textField,q=True,ex=True):
		mc.textFieldGrp(textField,e=True,text=dirPath[0])
	elif mc.textFieldButtonGrp(textField,q=True,ex=True):
		mc.textFieldButtonGrp(textField,e=True,text=dirPath[0])
	else:
		print('UI element "'+textField+'" is of type "'+mc.objectTypeUI(textField)+'"! Expected textField, textFieldGrp or textFieldButtonGrp.')
		return
	
	# Return Result
	return dirPath[0]

def importFolderBrowser(textField): # ,caption='Import',startingDirectory=None):
	'''
	Set the input directory from file browser selection
	'''
	mm.eval('global proc importGetFolder(string $textField,string $path,string $type){ textFieldButtonGrp -e -text $path $textField; deleteUI projectViewerWindow; }')
	mm.eval('fileBrowser "importGetFolder '+textField+'" Import "" 4')
	
	#dirPath = mc.fileDialog2(dialogStyle=2,fileMode=3,caption='Load Scenegraph XML',okCaption='Load',startingDirectory=startingDirectory)

def exportFolderBrowser(textField):
	'''
	Set the output directory from file browser selection
	'''
	mm.eval('global proc exportGetFolder(string $textField,string $path,string $type){ textFieldButtonGrp -e -text $path $textField; /*deleteUI projectViewerWindow;*/ }')
	mm.eval('fileBrowser "exportGetFolder '+textField+'" Export "" 4')

def loadNsSel(textField,topOnly=True):
	'''
	Load selected namespace into UI text field
	@param textField: TextField UI object to load namespace selection into
	@type textField: str
	@param topOnly: Return the top level namespace only.
	@type topOnly: bool
	'''
	# Get Selection
	sel = mc.ls(sl=True)
	if not sel: return
	
	# Get Selected Namespace
	NS = ''
	NS = glTools.utils.namespace.getNS(sel[0],topOnly)
	
	# Update UI
	mc.textFieldButtonGrp(textField,e=True,text=NS)

def loadObjectSel(textField,prefixTextField=''):
	'''
	Load selected object into UI text field
	@param textField: TextField UI object to load object selection into
	@type textField: str
	@param prefixTextField: TextField UI object to load object name prefix into
	@type prefixTextField: str
	'''
	# Get user selection
	sel = mc.ls(sl=True)
	# Check selection
	if not sel: return
	# Update UI
	mc.textFieldButtonGrp(textField,e=True,text=sel[0])
	if prefixTextField:
		if not mc.textFieldGrp(prefixTextField,q=True,text=True):
			prefix = glTools.utils.stringUtils.stripSuffix(sel[0])
			mc.textFieldGrp(prefixTextField,e=True,text=prefix)

def loadTypeSel(textField,prefixTextField='',selType=''):
	'''
	Load selected joint into UI text field
	@param textField: TextField UI object to load joint selection into
	@type textField: str
	@param prefixTextField: TextField UI object to load curve name prefix into
	@type prefixTextField: str
	'''
	if not selType: raise UserInputError('No selection type specified!!')
	# Get user selection
	sel = mc.ls(sl=True,type=selType)
	# Check selection
	if not sel: return
	# Update UI
	mc.textFieldButtonGrp(textField,e=True,text=sel[0])
	if prefixTextField:
		prefix = glTools.utils.stringUtils.stripSuffix(sel[0])
		mc.textFieldGrp(prefixTextField,e=True,text=prefix)

def loadCurveSel(textField,prefixTextField=''):
	'''
	Load selected curve into UI text field
	@param textField: TextField UI object to load curve selection into
	@type textField: str
	@param prefixTextField: TextField UI object to load curve name prefix into
	@type prefixTextField: str
	'''
	# Get user selection
	sel = mc.ls(sl=True)
	# Check selection
	if not sel: return
	if not glTools.utils.curve.isCurve(sel[0]):
		raise UserInputError('Object "'+sel[0]+'" is not a valid nurbs curve!!')
	# Update UI
	mc.textFieldButtonGrp(textField,e=True,text=sel[0])
	if prefixTextField:
		if not mc.textFieldGrp(prefixTextField,q=True,text=True):
			prefix = glTools.utils.stringUtils.stripSuffix(sel[0])
			mc.textFieldGrp(prefixTextField,e=True,text=prefix)

def loadSurfaceSel(textField,prefixTextField=''):
	'''
	Load selected surface into UI text field
	@param textField: TextField UI object to load surface selection into
	@type textField: str
	@param prefixTextField: TextField UI object to load surface name prefix into
	@type prefixTextField: str
	'''
	# Get user selection
	sel = mc.ls(sl=True)
	# Check selection
	if not sel: return
	if not glTools.utils.surface.isSurface(sel[0]):
		raise UserInputError('Object "'+sel[0]+'" is not a valid nurbs surface!!')
	# Update UI
	mc.textFieldButtonGrp(textField,e=True,text=sel[0])
	if prefixTextField:
		if not mc.textFieldGrp(prefixTextField,q=True,text=True):
			prefix = glTools.utils.stringUtils.stripSuffix(sel[0])
			mc.textFieldGrp(prefixTextField,e=True,text=prefix)

def loadMeshSel(textField,prefixTextField=''):
	'''
	Load selected curve into UI text field
	@param textField: TextField UI object to load mesh selection into
	@type textField: str
	@param prefixTextField: TextField UI object to load curve name prefix into
	@type prefixTextField: str
	'''
	# Get user selection
	sel = mc.ls(sl=True)
	# Check selection
	if not sel: return
	if not glTools.utils.mesh.isMesh(sel[0]):
		raise UserInputError('Object "'+sel[0]+'" is not a valid polygon mesh!!')
	# Update UI
	mc.textFieldButtonGrp(textField,e=True,text=sel[0])
	if prefixTextField:
		if not mc.textFieldGrp(prefixTextField,q=True,text=True):
			prefix = glTools.utils.stringUtils.stripSuffix(sel[0])
			mc.textFieldGrp(prefixTextField,e=True,text=prefix)

def loadChannelBoxSel(textField,fullName=True):
	'''
	Load selected channel into UI text field
	@param textField: TextField UI object to load channelbox selection into
	@type textField: str
	@param fullName: Use full name of attribute (node.attribute)
	@type fullName: bool
	'''
	# Get channelBox
	channelBox = 'mainChannelBox'
	
	# Check main object channels
	nodeList = mc.channelBox(channelBox,q=True,mol=True)
	channelList = mc.channelBox(channelBox,q=True,sma=True)
	# Check shape channels
	if not channelList:
		channelList = mc.channelBox(channelBox,q=True,ssa=True)
		nodeList = mc.channelBox(channelBox,q=True,sol=True)
	# Check history channels
	if not channelList:
		channelList = mc.channelBox(channelBox,q=True,sha=True)
		nodeList = mc.channelBox(channelBox,q=True,hol=True)
	# Check output channels
	if not channelList:
		channelList = mc.channelBox(channelBox,q=True,soa=True)
		nodeList = mc.channelBox(channelBox,q=True,ool=True)
	
	# Check selection
	if not channelList:
		print('No channel selected in the channelBox!')
		return
	
	# Update UI
	attr = ''
	if fullName: attr += str(nodeList[0]+'.')
	attr += str(channelList[0])
	mc.textFieldButtonGrp(textField,e=True,text=attr)

# ====================
# - Text Scroll List -
# ====================

def copyTSLselToTSL(sourceTSL,targetTSL,removeFromSource=False,replaceTargetContents=False):
	'''
	Copy selected items from one textScrollList to another.
	Options to remove from the source list (move) and replace existing target list items.
	@param sourceTSL: Source textScrollList to copy selected items from
	@type sourceTSL: str
	@param targetTSL: Target textScrollList to copy selected items to
	@type targetTSL: str
	@param removeFromSource: Remove the selected itmes from the source list (move)
	@type removeFromSource: bool
	@param replaceTargetContents: Replace the existing target list items with the source selection
	@type replaceTargetContents: bool
	'''
	# Get source selection
	srcItems = mc.textScrollList(sourceTSL,q=True,si=True)
	if not srcItems: return
	
	# Clear target list
	if replaceTragetContents: mc.textScrollList(targetTSL,e=True,ra=True)
	
	# Get current target items
	tgtItems = mc.textScrollList(targetTSL,q=True,si=True)
	
	# Copy to target list
	for src in srcItems:
		
		# Check existing target items
		if tgtItems.count(src): continue
			
		# Append to target list
		mc.textScrollList(targetTSL,e=True,a=src)
		tgtItems.append(src)

		# Remove from source
		if removeFromSource: mc.textScrollList(sourceTSL,e=True,ri=src)

def addToTSL(TSL,itemList=[]):
	'''
	Add selected items to the specified textScrollList
	@param TSL: TextScrollList UI object to load object selection into
	@type TSL: str
	'''
	# Get user selection
	if not itemList: itemList = mc.ls(sl=True)
	# Check selection
	if not itemList: return
	# Update UI
	currentList = mc.textScrollList(TSL,q=True,ai=True)
	if not currentList: currentList = []
	for item in itemList:
		if not currentList.count(item):
			mc.textScrollList(TSL,e=True,a=item)

def addCvsToTSL(TSL):
	'''
	Add selected nurbs control points to the specified textScrollList
	@param TSL: TextScrollList UI object to load object selection into
	@type TSL: str
	'''
	# Get user selection
	sel = mc.filterExpand(sm=28)
	# Check selection
	if not sel: return
	# Update UI
	currentList = mc.textScrollList(TSL,q=True,ai=True)
	if not currentList: currentList = []
	for obj in sel:
		if not currentList.count(obj):
			mc.textScrollList(TSL,e=True,a=obj)

def removeFromTSL(TSL):
	'''
	Remove selected items from the specified textScrollList
	@param TSL: TextScrollList UI object to remove items from
	@type TSL: str
	'''
	# Update UI
	listItems = mc.textScrollList(TSL,q=True,sii=True)
	listItems.sort()
	listItems.reverse()
	mc.textScrollList(TSL,e=True,rii=listItems)

def selectFromTSL(TSL,mode='replace',safeFail=True):
	'''
	Select (replace mode) the hilited items from the specified textScrollList
	@param TSL: TextScrollList UI object to remove items from
	@type TSL: str
	@param mode: Selection mode. Accepted values are "add", "replace", "toggle" and "remove"
	@type mode: str
	@param safeFail: Print safe message if item not found. Else, raise Exception.
	@type safeFail: bool
	'''
	# Check Mode
	if not mode in ['add','replace','toggle','remove']:
		raise Exception('Invalid selection mode! ("'+mode+'")')
	
	# Get Items to Select
	listItems = mc.textScrollList(TSL,q=True,si=True)
	if not listItems: return
	
	# Clear Selection
	if mode.lower() == 'replace': mc.select(cl=True)
	
	# Select Items
	for item in listItems:
		
		# Check Object Exists
		if not mc.objExists(item):
			
			# Check Safe Fail
			if safeFail:
				print('Object "'+item+'" does not exist! Skipping...')
				continue
			else:
				raise Exception('Object "'+item+'" does not exist!')
		
		# Add Item to Selection
		if (mode == 'add') or (mode == 'replace'):
			mc.select(listItems,add=True,noExpand=True)
		# Toggle Item Selection
		if (mode == 'toggle'):
			mc.select(listItems,tgl=True,noExpand=True)
		# Remove Item Selection
		if (mode == 'remove'):
			mc.select(listItems,d=True,noExpand=True)
		

def moveToTSLPosition(TSL,index):
	'''
	Move the selected textScrollList item(s) to the specified position in the list
	@param TSL: The name of th textScrollList to manipulate
	@type TSL: str
	@param index: The new index position for the selected list items
	@type index: int
	'''
	# Get all list entries
	listLen = len(mc.textScrollList(TSL,q=True,ai=True))
	
	# Get selected item indices
	listItems = mc.textScrollList(TSL,q=True,si=True)
	listIndex = mc.textScrollList(TSL,q=True,sii=True)
	listItems.reverse()
	listIndex.reverse()
	
	# Check position value
	if not index or index > listLen:
		raise UserInputError('Invalid position ('+str(index)+') provided for textScrollList!!')
	if index < 0:
		index = 2 + listLen + index
	
	# Remove items
	for i in range(len(listIndex)):
		if listIndex[i] < index: index -= 1
	mc.textScrollList(TSL,e=True,rii=listIndex)
	
	# Append items to position
	for i in range(len(listIndex)):
		mc.textScrollList(TSL,e=True,ap=(index,listItems[i]))
		listIndex[i] = index + i
	
	# Select list items
	mc.textScrollList(TSL,e=True,da=True)
	mc.textScrollList(TSL,e=True,sii=listIndex)
	mc.textScrollList(TSL,e=True,shi=listIndex[0])
	
def moveUpTSLPosition(TSL):
	'''
	Move the selected textScrollList items up by one position
	@param TSL: The name of th textScrollList to manipulate
	@type TSL: str
	'''
	# Method variables
	minIndex = 1
	
	# Get selected item indices
	listItems = mc.textScrollList(TSL,q=True,si=True)
	listIndex = mc.textScrollList(TSL,q=True,sii=True)
	
	# Iterate through list items
	for i in range(len(listIndex)):
		# Check minIndex
		if listIndex[i] <= minIndex:
			minIndex += 1
			continue
		mc.textScrollList(TSL,e=True,sii=listIndex[i])
		listIndex[i] -= 1
		moveToTSLPosition(TSL,listIndex[i])
	
	# Select list items
	mc.textScrollList(TSL,e=True,da=True)
	mc.textScrollList(TSL,e=True,sii=listIndex)
	mc.textScrollList(TSL,e=True,shi=listIndex[0])
	
def moveDownTSLPosition(TSL):
	'''
	Move the selected textScrollList items down by one position
	@param TSL: The name of th textScrollList to manipulate
	@type TSL: str
	'''
	# Get list length
	listLen = len(mc.textScrollList(TSL,q=True,ai=True))
	maxIndex = listLen
	
	# Get selected item indices
	listItems = mc.textScrollList(TSL,q=True,si=True)
	listIndex = mc.textScrollList(TSL,q=True,sii=True)
	# Reverse lists
	listItems.reverse()
	listIndex.reverse()
	
	# Iterate through list items
	for i in range(len(listItems)):
		# Check maxIndex
		if listIndex[i] >= maxIndex:
			maxIndex -= 1
			continue
		mc.textScrollList(TSL,e=True,sii=listIndex[i])
		listIndex[i] += 1
		if listIndex[i] == listLen:
			moveToTSLPosition(TSL,-1)
		else:
			moveToTSLPosition(TSL,listIndex[i]+1)
	
	# Select list items
	mc.textScrollList(TSL,e=True,da=True)
	mc.textScrollList(TSL,e=True,sii=listIndex)
	mc.textScrollList(TSL,e=True,shi=listIndex[0])

def loadFileSelection(TSL,fileFilter='*.*',startDir=None,caption='Load Files'):
	'''
	'''
	# Select Files
	fileList = mc.fileDialog2(	fileFilter=fileFilter,
								dialogStyle=2,
								fileMode=4,
								caption=caption,
								okCaption='Load',
								startingDirectory=startDir )
	
	# Add File Selection
	if fileList:
		for item in fileList:
			mc.textScrollList(TSL,e=True,a=item)

def loadFileList(TSL,path,filesOnly=False,filterStr='',sort=False):
	'''
	Load the file list of a specified directory path to a textScrollList
	@param TSL: TextScrollList UI object to load file list into.
	@type TSL: str
	@param path: The directory path to get the file list from.
	@type path: str
	@param filesOnly: List files only (excludes directories).
	@type filesOnly: bool
	@param filterStr: Filter string for file name match.
	@type filterStr: str
	@param sort: Alpha sort list.
	@type sort: bool
	'''
	# Get File List
	fileList = glTools.utils.osUtils.getFileList(path,filesOnly=filesOnly)
	
	# Filter (regex)
	if filterStr:
		reFilter = re.compile(filterStr)
		fileList = filter(reFilter.search, fileList)
	
	# Sort
	if sort: fileList.sort()
	
	# Add File List to textScrollList
	addToTSL(TSL,fileList)
	
# =============
# - Check Box -
# =============
	
def checkBoxToggleLayout(CBG,layout,invert=False):
	'''
	Toggle the enabled state of a UI layout based on a checkBoxGrp
	@param CBG: CheckBoxGrp used to toggle layout
	@type CBG: str
	@param layout: Layout to toggle
	@type layout: str
	@param invert: Invert the checkBox value
	@type invert: bool
	'''
	# Check CheckBoxGrp
	if not mc.checkBoxGrp(CBG,q=True,ex=True):
		raise UIError('CheckBoxGrp "'+CBG+'" does not exist!!')
	# Check layout
	if not mc.layout(layout,q=True,ex=True):
		raise UIError('Layout "'+layout+'" does not exist!!')
	
	# Get checkBoxGrp state
	state = mc.checkBoxGrp(CBG,q=True,v1=True)
	if invert: state = not state
	
	# Toggle Layout
	mc.layout(layout,e=True,en=state)

def checkBoxToggleControl(CBG,control,invert=False):
	'''
	Toggle the enabled state of a UI layout based on a checkBoxGrp
	@param CBG: CheckBoxGrp used to toggle layout
	@type CBG: str
	@param layout: Layout to toggle
	@type layout: str
	@param invert: Invert the checkBox value
	@type invert: bool
	'''
	# Check CheckBoxGrp
	if not mc.checkBoxGrp(CBG,q=True,ex=True):
		raise UIError('CheckBoxGrp "'+CBG+'" does not exist!!')
	# Check control
	if not mc.control(control,q=True,ex=True):
		raise UIError('Control "'+control+'" does not exist!!')
	
	# Get checkBoxGrp state
	state = mc.checkBoxGrp(CBG,q=True,v1=True)
	if invert: state = not state
	
	# Toggle Layout
	mc.control(control,e=True,en=state)

# ====================
# - Option Menu List -
# ====================

def setOptionMenuList(OMG,itemList,add=False):
	'''
	Set the list of items for the specified optionMenuGrp control
	@param OMG: OptionMenuGrp to set the item list for
	@type OMG: str
	@param itemList: List of items to add to optionMenuGrp
	@type itemList: list
	@param add: Add to existing menu items
	@type add: bool
	'''
	# Check optionMenuGrp
	if not mc.optionMenuGrp(OMG,q=True,ex=True):
		raise UIError('OptionMenu "'+OMG+'" does not exist!')
	
	# Get existing items
	exItemList = mc.optionMenuGrp(OMG,q=True,ill=True)
	
	# Add items
	for item in itemList:
		mc.setParent(OMG)
		mc.menuItem(l=item)
	
	# Remove previous items
	if exItemList:
		for item in exItemList:
			mc.deleteUI(item)
			
# =====================
# - Float Field Group -
# =====================

def setPointValue(FFG,point=''):
	'''
	Set the value of a floatFieldGrp with the position value of a specifeid point
	@param FFG: FloatFieldgrp to set values for
	@type FFG: str
	@param point: Point to get position from
	@type point: str
	'''
	# Check point
	if point and not mc.objExists(point):
			raise Exception('Point object "'+point+'" does not exist!')
	
	# Get object selection
	sel = mc.ls(sl=1)
	if not point and not sel:
		raise Exception('No point specified for floatFieldGrp values!')
	
	# Get point
	if point: pos = glTools.utils.base.getPosition(point)
	else: pos = glTools.utils.base.getPosition(sel[0])
	
	# Set float field values
	mc.floatFieldGrp(FFG,e=True,v1=pos[0],v2=pos[1],v3=pos[2])
	
# =============
# - Custom UI -
# =============

def displayListWindow(itemList,title,enableSelect=False):
	'''
	Create a basic list selection window.
	@param itemList: Item list to display in window
	@type itemList: list
	@param title: Window title string
	@type title: str
	'''
	# Check itemList
	if not itemList:
		mc.confirmDialog(t=title,m='No items to display!',ma='center',b='Close')
		return
	
	# Window
	window = 'displayListWindowUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,t=title,s=True)
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# ===============
	# - UI Elements -
	# ===============
	
	# TextScrollList
	TSL = mc.textScrollList('displayListWindowTSL',allowMultiSelection=True)
	for item in itemList: mc.textScrollList(TSL,e=True,a=item)
	if enableSelect: mc.textScrollList(TSL,e=True,sc='glTools.ui.utils.selectFromTSL("'+TSL+'")')
	
	# Close Button
	closeB = mc.button('displayListWindowB',l='Close',c='mc.deleteUI("'+window+'")')
	
	# Form Layout
	mc.formLayout(FL,e=True,af=[(TSL,'top',5),(TSL,'left',5),(TSL,'right',5)])
	mc.formLayout(FL,e=True,af=[(closeB,'bottom',5),(closeB,'left',5),(closeB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(TSL,'bottom',5,closeB)])
	
	# Display Window
	mc.showWindow(window)

def displayMessageWindow(msg,title):
	'''
	Create a basic message/report window.
	@param msg: Message string to display in window.
	@type msg: str
	@param title: Window title string
	@type title: str
	'''
	# Check message
	if not msg: return
	
	# Window
	window = 'messageWindowUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,t=title,s=True)
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	reportSF = mc.scrollField('messageWindowSF',editable=False,wordWrap=True,text=msg)
	closeB = mc.button('messageWindowB',l='Close',c='mc.deleteUI("'+window+'")')
	
	# Form Layout
	mc.formLayout(FL,e=True,af=[(reportSF,'top',5),(reportSF,'left',5),(reportSF,'right',5)])
	mc.formLayout(FL,e=True,af=[(closeB,'bottom',5),(closeB,'left',5),(closeB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(reportSF,'bottom',5,closeB)])
	
	# Display Window
	mc.showWindow(window)
