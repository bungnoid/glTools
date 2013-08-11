import maya.cmds as mc

class SelectionUtilities(object):
	
	def __init__(self): pass

	def getShapes(self,transform,getIntermediate=0):
		'''
		Return a list of shapes under a specified transform
		@param transform: Transform to query
		@type transform: str
		@param getIntermediate: Return intermediate shapes.
		@type getIntermediate: bool
		'''
		# Initialize arrays
		returnShapes = []
		
		# Check for shape input
		if (mc.objectType(transform) == 'mesh') or (mc.objectType(transform) == 'nurbsCurve') or (mc.objectType(transform) == 'nurbsSurface'):
			# Get transform parent
			transform = mc.listRelatives(transform,p=1)[0] # Get element[0] from parent list
		
		# Get shape lists
		if mc.objectType(transform) == 'transform':
			allShapes = mc.listRelatives(transform,s=1)
			for shape in allShapes:
				if mc.getAttr(shape+'.intermediateObject') == getIntermediate:
					returnShapes.append(shape)
		else:
			raise UserInputError('Unable to find shape node for '+transform+'!')
		# Return result
		return returnShapes
	
	def componentSelectionInOrder(self):
		'''
		Returns a list of the selected components in the order they were selected.
		'''
		selection = []
		selectionAll = mc.ls(sl=1)
		lastCommand = mc.undoInfo(q=True,un=True)
		counter = 0
		
		while lastCommand.count('select'):
			lastCommand = mc.undoInfo(q=True,un=True)
			if lastCommand.count('select'):
				selectElem = lastCommand.split(' ')
				selection.append(selectElem[2])
				mc.undo()
		
		selection.reverse()
		realSelection = []
		[realSelection.append(i) for i in selection if not realSelection.count(i)]
		
		mc.select(realSelection)
		return realSelection
	
	def enableObjectVertexSelection(self,item):
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
	
	def disableObjectVertexSelection(self,item):
		'''
		Disable vertex selection for specified object
		@param item: Object to switch selection mode for
		@type item: str
		'''
		# Hilite item
		mc.hilite(item,u=1)