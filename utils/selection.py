import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

import base
import glTools.utils.namespace

def numSelectionElements(selection):
	'''
	Return the number of selection elements are specified by the input selection list
	@param selection: Selection list to return the element count for.
	@type selection: list or str
	'''
	# Initialize function wrappers
	selectionList = OpenMaya.MSelectionList()
	
	# Build selection list
	if type(selection) == str or type(selection) == unicode: selection = [str(selection)]
	[selectionList.add(i) for i in selection]
	
	# Return Result
	return selectionList.length()

def getSelectionElement(selection,element=0):
	'''
	Return the selection components (MDagPath object, MObject component)
	for the specified element of the input selection list
	@param selection: Selection to return the element components for.
	@type selection: list or str
	@param element: Element of the selection to return selection components for.
	@type element: int
	'''
	# Initialize function wrappers
	selectionList = OpenMaya.MSelectionList()
	selectionPath = OpenMaya.MDagPath()
	selectionObj = OpenMaya.MObject()
	
	# Build selection list
	if type(selection) == str or type(selection) == unicode: selection = [str(selection)]
	[selectionList.add(i) for i in selection]
	
	# Check length
	if element >= selectionList.length():
		raise Exception('Element value ('+str(element)+') out of range!')
	
	# Get selection elements
	selectionList.getDagPath(element,selectionPath,selectionObj)
	
	# Return result
	return[selectionPath,selectionObj]

def getShapes(transform,returnNonIntermediate=True,returnIntermediate=True):
	'''
	Return a list of shapes under a specified transform
	@param transform: Transform to query
	@type transform: str
	@param returnNonIntermediate: Return non intermediate shapes.
	@type returnNonIntermediate: bool
	@param returnIntermediate: Return intermediate shapes.
	@type returnIntermediate: bool
	'''
	# Initialize arrays
	shapeList = []
	
	# Check for shape input
	transformObj = base.getMObject(transform)
	if not transformObj.hasFn(OpenMaya.MFn.kTransform):
		transform = mc.listRelatives(transform,p=True,pa=True)[0]
	
	# Get shape lists
	allShapeList = mc.listRelatives(transform,s=True,pa=True)
	if not allShapeList: return []
	for shape in allShapeList:
		intermediate = bool(mc.getAttr(shape+'.intermediateObject'))
		if intermediate and returnIntermediate: shapeList.append(shape)
		if not intermediate and returnNonIntermediate: shapeList.append(shape)
		
	# Return result
	return shapeList

def componentSelectionInOrder():
	'''
	Returns a list of the selected components in the order they were selected.
	'''
	# Get selection
	selection = []
	selectionAll = mc.ls(sl=1)
	lastCommand = mc.undoInfo(q=True,un=True)
	counter = 0
	
	# Traverse undo list
	while lastCommand.count('select'):
		lastCommand = mc.undoInfo(q=True,un=True)
		if lastCommand.count('select'):
			selectElem = lastCommand.split(' ')
			selection.append(selectElem[2])
			mc.undo()
	
	# Sort selection
	selection.reverse()
	realSelection = []
	[realSelection.append(i) for i in selection if not realSelection.count(i)]
	
	# Return result
	return realSelection

def enableObjectVertexSelection(item):
	'''
	Enable vertex selection for specified object
	@param item: Object to switch selection mode for
	@type item: str
	'''
	# Hilite item
	mc.hilite(item)
	# Get item type
	itemType = mc.objectType(mc.listRelatives(item,s=1,ni=1)[0])
	# Set selection mode
	if itemType == 'mesh':
		mc.selectType(ocm=1,vertex=1)
	if itemType == 'nurbsSurface' or itemType == 'nurbsCurve':
		mc.selectType(ocm=1,controlVertex=1)

def disableObjectVertexSelection(item):
	'''
	Disable vertex selection for specified object
	@param item: Object to switch selection mode for
	@type item: str
	'''
	# Hilite item
	mc.hilite(item,u=1)

def selectFromViewport():
	'''
	Select all objects visible in the current active viewport
	'''
	# Get active viewport
	viewPort = OpenMayaUI.M3dView.active3dView()
	
	# Select from screen
	OpenMaya.MGlobal.selectFromScreen(0,0,viewPort.portWidth(),viewPort.portHeight(),OpenMaya.MGlobal.kReplaceList,OpenMaya.MGlobal.kWireframeSelectMethod)

def selectByAttr(attr=''):
	'''
	Select nodes with the specified attribute
	@param attr: Attribute to use a for the selection filter
	@type attr: str
	'''
	# Check Attribute
	if not attr:
	
		result = mc.promptDialog(	title='Select By Attribute',
									message='Attribute:',
									button=['Select','Cancel'],
									defaultButton='Select',
									cancelButton='Cancel',
									dismissString='Cancel'	)
		
		if result == 'Select':
			attr = mc.promptDialog(q=True,text=True)	
		
		# Check Attribute
		if not attr: return
	
	# Select By Attribute
	sel = mc.ls('*.'+attr,o=True)
	
	# Return Result
	return sel

def componentListByObject(componentList=[]):
	'''
	Return a list of component lists.
	Each components list is grouped by parent object.
	@param componentList: Flat component list that will be grouped by object
	@type componentList: list
	'''
	# Check Component List - If empty, get user selection
	if not componentList: componentList = mc.ls(sl=1,fl=1)
	if not componentList: return []
	
	# Initialize function wrappers
	selList = OpenMaya.MSelectionList()
	objPath = OpenMaya.MDagPath()
	compObj = OpenMaya.MObject()
	
	# Build Selection List
	if type(componentList) == str or type(componentList) == unicode: componentList = [str(componentList)]
	[selList.add(i) for i in componentList]
	
	# For Each Object
	objCompList = []
	for i in range(selList.length()):
		
		# Get Object Selection
		selList.getDagPath(i,objPath,compObj)
		compList = OpenMaya.MSelectionList()
		compList.clear()
		compList.add(objPath,compObj)
		
		# Get Component Selection List
		compStrList = []
		compList.getSelectionStrings(compStrList)
		
		# Append to Output List
		objCompList.append(compStrList)
	
	# Return Result
	return objCompList

def componentDictByObject(componentList=[]):
	'''
	Return a dictionary of component lists, using the components object as a key.
	@param componentList: Flat component list that will be grouped by object
	@type componentList: list
	'''
	# Check Component List - If empty, get user selection
	if not componentList: componentList = mc.ls(sl=1,fl=1)
	if not componentList: return []
	
	# Initialize function wrappers
	selList = OpenMaya.MSelectionList()
	objPath = OpenMaya.MDagPath()
	compObj = OpenMaya.MObject()
	
	# Build Selection List
	if type(componentList) == str or type(componentList) == unicode: componentList = [str(componentList)]
	[selList.add(i) for i in componentList]
	
	# For Each Object
	objCompDict = {}
	for i in range(selList.length()):
		
		# Get Object Selection
		selList.getDagPath(i,objPath,compObj)
		compList = OpenMaya.MSelectionList()
		compList.clear()
		compList.add(objPath,compObj)
		
		# Get Component Selection List
		compStrList = []
		compList.getSelectionStrings(compStrList)
		
		# Append to Output List
		objCompDict[objPath.name()] = compStrList
	
	# Return Result
	return objCompList

def mirrorSelection(sel=[],mirrorPrefix=[('lf','rt')],addToSel=False):
	'''
	Mirror selection
	@param sel: User defined selection to mirror. If empty, use current active selection.
	@type sel: list
	@param mirrorPrefix: List of side prefix pairs.
	@type mirrorPrefix: list
	@param addToSel: Add to or replace current selection.
	@type addToSel: bool
	'''
	# Check Selection
	if not sel: sel = mc.ls(sl=True)
	
	# Get Mirror Selection
	mSel = []
	for obj in sel:
		
		# Get Namespace and Short Name
		NS = glTools.utils.namespace.getNS(obj)
		if NS: NS += ':'
		objSN = glTools.utils.namespace.stripNS(obj)
		
		# Get Side Prefix
		side = objSN.split('_')[0]
		
		# Get Mirror
		mObj = objSN
		for mPrefix in mirrorPrefix:
			if side == mPrefix[0]:
				mObj = objSN.replace(mPrefix[0],mPrefix[1])
				break
			if side == mPrefix[1]:
				mObj = objSN.replace(mPrefix[1],mPrefix[0])
				break
		
		# Check Mirror Object
		if not mc.objExists(NS+mObj):
			print ('Mirror object "'+NS+mObj+'" does not exist!')
			continue
		
		# Add to Mirror Selection
		mSel.append(NS+mObj)
		
	# Set Selection
	if addToSel: mSel = sel + mSel
	mc.select(mSel)
	
	# Return Result
	return mSel
