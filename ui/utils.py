import maya.cmds as mc
import maya.mel as mm

import glTools.utils.base
import glTools.utils.curve
import glTools.utils.mesh
import glTools.utils.stringUtils
import glTools.utils.surface

class UserInputError(Exception): pass
class UIError(Exception): pass

# --------------
# - Text Field -
# --------------

def exportFolderBrowser(textField):
	'''
	Set the output directory from file browser selection
	'''
	mm.eval('global proc exportGetFolder(string $textField,string $path,string $type){ textFieldButtonGrp -e -text $path $textField; deleteUI projectViewerWindow; }')
	mm.eval('fileBrowser "exportGetFolder '+textField+'" Export "" 4')

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
	@param textField: TextField UI object to load curve selection into
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

def loadChannelBoxSel(textField):
	'''
	Load selected channel into UI text field
	@param textField: TextField UI object to load curve selection into
	@type textField: str
	@param prefixTextField: TextField UI object to load curve name prefix into
	@type prefixTextField: str
	'''
	# Get channelBox
	channelBox = 'MayaWindow|mayaMainWindowForm|formLayout3|formLayout11|formLayout32|formLayout33|ChannelsLayersPaneLayout|formLayout36|menuBarLayout1|frameLayout1|mainChannelBox'
	
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
	if mc.textField(textField,q=True,ex=True):
		mc.textField(textField,e=True,text=str(nodeList[0]+'.'+channelList[0]))
	if mc.textFieldGrp(textField,q=True,ex=True):
		mc.textFieldGrp(textField,e=True,text=str(nodeList[0]+'.'+channelList[0]))
	if mc.textFieldButtonGrp(textField,q=True,ex=True):
		mc.textFieldButtonGrp(textField,e=True,text=str(nodeList[0]+'.'+channelList[0]))

# --------------------
# - Text Scroll List -
# --------------------

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

def selectFromTSL(TSL):
	'''
	Select the hilited items from the specified textScrollList
	@param TSL: TextScrollList UI object to remove items from
	@type TSL: str
	'''
	listItems = mc.textScrollList(TSL,q=True,si=True)
	if not listItems: return
	
	for item in listItems:
		if not mc.objExists(item):
			raise Exception('Object "'+item+'" does not exist!')
	
	mc.select(listItems)

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
	
# -------------
# - Check Box -
# -------------
	
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

# --------------------
# - Option Menu List -
# --------------------

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
			
# ---------------------
# - Float Field Group -
# ---------------------

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
	
	
