import maya.cmds as mc
import maya.OpenMaya as OpenMaya

def connectionListToAttr(toNode,toAttr):
	'''
	Return a dictionary containing incoming connection information for a specific attribute
	
	@param toNode: Node to query connection information from
	@type toAttr: Attribute to query connection information from
	'''
	# Verify
	if not mc.objExists(toNode+'.'+toAttr):
		raise Exception('Attribute ' + toNode+'.'+toAttr + ' does not exist!')
		return
	
	# Initialize empty connection dictionary
	connectionList = {}
	
	# Get user selection
	userSel = mc.ls(sl=1)
	
	# Initialize MSelectionList
	selList = OpenMaya.MSelectionList()
	
	# Get toNode
	selList.clear()
	OpenMaya.MGlobal.clearSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(toNode,selList)
	toNodeObj = OpenMaya.MObject()
	selList.getDependNode(0,toNodeObj)
	
	# Get MPlug to toAttr
	toAttrPlug = OpenMaya.MFnDependencyNode(toNodeObj).findPlug(toAttr)
	
	# Get MPlugArray of connected plugs
	connectedPlugArray = OpenMaya.MPlugArray()
	if toAttrPlug.isArray():
		numElems = toAttrPlug.numElements()
		elementPlugArray = OpenMaya.MPlugArray()
		for i in range(numElems):
			elemAttrPlug = toAttrPlug.elementByPhysicalIndex(i)
			elemAttrPlug.connectedTo(elementPlugArray,1,0)
			numPlugs = elementPlugArray.length()
			for n in range(numPlugs):
				name = OpenMaya.MFnDependencyNode(elementPlugArray[n].node()).name()
				connectionList[name] = (elementPlugArray[n].partialName(0,0,1,0,0,1),elemAttrPlug.logicalIndex())
	else:
		toAttrPlug.connectedTo(connectedPlugArray,1,0)
		for i in range(connectedPlugArray.length()):
			plugElem = connectedPlugArray[i].name().split('.')
			node = plugElem[0]
			attr = ''
			for elem in plugElem[1:]:
				attr += elem
				if (len(elem) > 1) and (elem != plugElem[-1]): attr += '.'
			connectionList[node] = (attr,-(i+1))
	
	# Restore original selection
	mc.select(cl=1)
	if type(userSel) == list:
		if len(userSel): mc.select(userSel)
	
	return connectionList
	
def connectionListFromAttr(fromNode,fromAttr):
	'''
	Return a dictionary containing outgoing connection information for a specific attribute
	
	@param fromNode: Node to query connection information from
	@type fromAttr: Attribute to query connection information from
	'''
	# Verify
	if not mc.objExists(fromNode+'.'+fromAttr):
		raise Exception('Attribute ' + fromNode+'.'+fromAttr + ' does not exist!')
		return
	
	# Get user selection
	userSel = mc.ls(sl=1)
	
	# Initialize MSelectionList
	selList = OpenMaya.MSelectionList()
	
	# Get fromNode
	selList.clear()
	OpenMaya.MGlobal.clearSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(fromNode,selList)
	fromNodeObj = OpenMaya.MObject()
	selList.getDependNode(0,fromNodeObj)
	
	# Get MPlug to fromAttr
	fromAttrPlug = OpenMaya.MFnDependencyNode(fromNodeObj).findPlug(fromAttr)
	
	# Get MPlugArray of connected plugs
	connectedPlugArray = OpenMaya.MPlugArray()
	if fromAttrPlug.isArray():
		numElems = fromAttrPlug.numElements()
		elementPlugArray = OpenMaya.MPlugArray()
		for i in range(numElems):
			elemAttrPlug = toAttrPlug.elementByPhysicalIndex(i)
			elemAttrPlug.connectedTo(elementPlugArray,0,1)
			numPlugs = elementPlugArray.length()
			for n in range(numPlugs):
				name = OpenMaya.MFnDependencyNode(elementPlugArray[n].node()).name()
				connectionList[name] = (elementPlugArray[n].partialName(0,0,1,0,0,1),elemAttrPlug.logicalIndex())
	else:
		fromAttrPlug.connectedTo(connectedPlugArray,0,1)
		for i in range(connectedPlugArray.length()):
			plugElem = connectedPlugArray[i].name().split('.')
			node = plugElem[0]
			attr = ''
			for elem in plugElem[1:]:
				attr += elem
				if (len(elem) > 1) and (elem != plugElem[-1]): attr += '.'
			connectionList[node] = (attr,-(i+1))
	
	# Restore original selection
	mc.select(cl=1)
	if type(userSel) == list:
		if len(userSel): mc.select(userSel)
	
	return self.connectionList

def combineSingleAttrConnections(targetAttr,inputAttr1='',inputAttr2='',inputAttr1Value=None,inputAttr2Value=None,combineMode='add',enableAttributeOverride=False,blendAttr=''):
	'''
	Connect the combined result of 2 input attributes/values to a target attribute.
	
	@param targetAttr: Target attribute to receive the combined values result
	@type targetAttr: str
	@param inputAttr1: First attribute to be used to obtain the combined result
	@type inputAttr1: str
	@param inputAttr2: Second attribute to be used to obtain the combined result. If left as default (''), the existing input connection to targetAttr will be used.
	@type inputAttr2: str
	@param inputAttr1Value: Set the value of the first input
	@type inputAttr1Value: float
	@param inputAttr2Value: Set the value of the second input
	@type inputAttr2Value: float
	@param combineMode: How to combine the 2 input attribute values. Accepted inputs are "add", "mult" and "blend".
	@type combineMode: str
	@param enableAttributeOverride: If you specify both a source attribute and value for an input, this will attempt to set the source attribute to the input value.
	@type enableAttributeOverride: str
	@param blendAttr: Source attribute that will drive the attribute blend amount. If left as default (''), no connection will be made to the "blendNode.attributeBlender" attribute.
	@type blendAttr: str
	'''
	# Check existing connections
	existingConn = mc.listConnections(targetAttr,s=True,d=False,p=True)
	
	# Check target attributes
	if not mc.objExists(targetAttr): raise Exception('Target attribute '+targetAttr+' does not exist!')
	# Check inputs
	if (not inputAttr1) and (inputAttr1Value==None): raise Exception('No input attribute or value specified for input1!')
	if (not inputAttr2) and (inputAttr2Value==None): raise Exception('No input attribute or value specified for input2!')
	# Check input attributes
	if inputAttr1 and not mc.objExists(inputAttr1): raise Exception('Input attribute 1 '+inputAttr1+' does not exist!')
	if inputAttr2 and not mc.objExists(inputAttr2): raise Exception('Input attribute 2 '+inputAttr2+' does not exist!')
	
	# Get target node name
	if not targetAttr.count('.'): raise Exception(targetAttr+' is not a valid attribute!')
	targetNode = targetAttr.split('.')[0]
	
	# Combine inputs
	combineNode = ''
	combineAttr1 = 'input1'
	combineAttr2 = 'input2'
	if combineMode == 'add':
		combineNode = self.nameUtil.appendName(targetNode,self.nameUtil.node['addDoubleLinear'],stripNameSuffix=True)
		combineNode = mc.createNode('addDoubleLinear',n=combineNode)
	if combineMode == 'mult':
		combineNode = self.nameUtil.appendName(targetNode,self.nameUtil.node['multDoubleLinear'],stripNameSuffix=True)
		combineNode = mc.createNode('multDoubleLinear',n=combineNode)
	if combineMode == 'blend':
		combineNode = self.nameUtil.appendName(targetNode,self.nameUtil.node['blendTwoAttr'],stripNameSuffix=True)
		combineNode = mc.createNode('blendTwoAttr',n=combineNode)
		combineAttr1 = 'input[0]'
		combineAttr2 = 'input[1]'
	
	# Set Input 1
	if inputAttr1:
		mc.connectAttr(inputAttr1,combineNode+'.'+combineAttr1,f=True)
		if enableAttributeOverride and mc.getAttr(inputAttr1,se=True):
			mc.setAttr(inputAttr1,inputAttr1Value)
	else:
		mc.setAttr(combineNode+'.'+combineAttr1,inputAttr1Value)
	# Set Input 2
	if inputAttr2:
		mc.connectAttr(inputAttr2,combineNode+'.'+combineAttr2,f=True)
		if enableAttributeOverride and mc.getAttr(inputAttr2,se=True):
			mc.setAttr(inputAttr2,inputAttr2Value)
	else:
		mc.setAttr(combineNode+'.'+combineAttr2,inputAttr2Value)
	
	# Connect to target attribute
	mc.connectAttr(combineNode+'.output',targetAttr,f=True)
	
	# Connect blend attribute
	if combineMode == 'blend' and blendAttr:
		# Check blend attribute
		if not mc.objExists(blendAttr):
			if not blendAttr.count('.'): raise Exception(targetAttr+' is not a valid object.attribute name!')
			blendAttrName = blendAttr.split('.')
			if len(blendAttrName) != 2: raise Exception(targetAttr+' is not a valid object.attribute name!')
			if not mc.objExists(blendAttrName[0]): raise Exception('Object '+blendAttrName[0]+' does not exist!')
			mc.addAttr(blendAttrName[0],ln=blendAttrName[1],at='float',min=0,max=1,dv=0)
			mc.setAttr(blendAttr,k=True)
		mc.connectAttr(blendAttr,blendNode+'.attributesBlender',f=True)
	
	# Return result
	return combineNode

def replace(original,new,inputs=True,outputs=True):
	'''
	@param original: The node or plug to be replaced
	@type original: str
	@param new: The node or plug to replace the original node or plug
	@type new: str
	@param inputs: Replace incoming connections
	@type inputs: bool
	@param outputs: Replace outgoing connections
	@type outputs: bool
	'''
	# Check original
	if not mc.objExists(original): raise Exception('Object "'+original+'" does not exist!!')
	origAttr = bool(original.count('.'))
	# Check new
	if not mc.objExists(new): raise Exception('Object "'+new+'" does not exist!!')
	newAttr = bool(new.count('.'))
	
	# Check argument types
	if origAttr != newAttr: raise Exception('Specify 2 nodes or node attributes! Cannot mix nodes and attributes!!')
	asAttr = origAttr
	
	# INPUTS
	if inputs:
		if asAttr:
			inputList = mc.listConnections(original,s=True,d=False,p=True)
			if inputList:
				for i in range(len(inputList)):
					mc.connectAttr(inputList[i],new,f=True)
		else:
			inputList = mc.listConnections(original,s=True,d=False,p=True,c=True)
			if inputList:
				for i in range(len(inputList)/2):
					newDest = inputList[i*2].replace(original,new)
					if not mc.objExists(newDest): raise Exception('Object attribute "'+newDest+'" does not exist!')
					mc.connectAttr(inputList[(i*2)+1],newDest,f=True)
	
	# OUTPUTS
	if outputs:
		if asAttr:
			outputList = mc.listConnections(original,d=True,s=False,p=True)
			if outputList:
				for i in range(len(outputList)):
					mc.connectAttr(new,outputList[i],f=True)
		else:
			outputList = mc.listConnections(original,d=True,s=False,p=True,c=True)
			if outputList:
				for i in range(len(outputList)/2):
					newOutput = outputList[i*2].replace(original,new)
					if not mc.objExists(newOutput): raise Exception('Object attribute "'+newOutput+'" does not exist!')
					mc.connectAttr(newOutput,outputList[(i*2)+1],f=True)