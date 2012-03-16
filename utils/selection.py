import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

import base

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
	if type(selection) == 'str': selection = [selection]
	[selectionList.add(i) for i in selection]
	
	# Check length
	if element >= selectionList.length():
		raise UserInputError('Element value ('+str(element)+') out of range!')
	
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
