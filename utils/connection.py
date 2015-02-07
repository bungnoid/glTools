import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base

def connectionListToAttr(toNode,toAttr):
	'''
	Return a dictionary containing incoming connection information for a specific attribute
	@param toNode: Node to query connection information from
	@type toAttr: Attribute to query connection information from
	'''
	# Verify
	if not mc.objExists(toNode+'.'+toAttr):
		raise Exception('Attribute ' + toNode+'.'+toAttr + ' does not exist!')
	
	# Get MPlug to toAttr
	toNodeObj = glTools.utils.base.getMObject(toNode)
	toAttrPlug = OpenMaya.MFnDependencyNode(toNodeObj).findPlug(toAttr)
	
	# Get MPlugArray of connected plugs
	connectionList = {}
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
	
	# Return Result
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
	
	# Get MPlug to fromAttr
	fromNodeObj = glTools.utils.base.getMObject(fromNode)
	fromAttrPlug = OpenMaya.MFnDependencyNode(fromNodeObj).findPlug(fromAttr)
	
	# Get MPlugArray of connected plugs
	connectionList = {}
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
	
	# Return Result
	return connectionList

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
	Replace all incoming and/or outgoing attribute connections from one node to another.
	Basically replaces a node in the graph with another.
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
					try: mc.connectAttr(inputList[i],new,f=True)
					except: raise Exception('FAILED: '+inputList[i]+' -> '+new+'!')
					print ('Connected: '+inputList[i]+' -> '+new)
		else:
			inputList = mc.listConnections(original,s=True,d=False,p=True,c=True)
			if inputList:
				for i in range(len(inputList)/2):
					newDest = inputList[i*2].replace(original,new)
					if not mc.objExists(newDest): raise Exception('Object attribute "'+newDest+'" does not exist!')
					try: mc.connectAttr(inputList[(i*2)+1],newDest,f=True)
					except: raise Exception('FAILED: '+inputList[(i*2)+1]+' -> '+newDest+'!')
					else: print ('Connected: '+inputList[(i*2)+1]+' -> '+newDest)
	
	# OUTPUTS
	if outputs:
		if asAttr:
			outputList = mc.listConnections(original,d=True,s=False,p=True)
			if outputList:
				for i in range(len(outputList)):
					try: mc.connectAttr(new,outputList[i],f=True)
					except: raise Exception('FAILED: '+new+' -> '+inputList[i]+'!')
					else: print('Connected: '+new+' -> '+inputList[i])
		else:
			outputList = mc.listConnections(original,d=True,s=False,p=True,c=True)
			if outputList:
				for i in range(len(outputList)/2):
					newOutput = outputList[i*2].replace(original,new)
					if not mc.objExists(newOutput): raise Exception('Object attribute "'+newOutput+'" does not exist!')
					try: mc.connectAttr(newOutput,outputList[(i*2)+1],f=True)
					except: raise Exception('FAILED: '+newOutput+' -> '+outputList[(i*2)+1]+'!')
					else: print ('Connected: '+newOutput+' -> '+outputList[(i*2)+1])

def swap(node1,node2):
	'''
	'''
	# ========================
	# - Get Node Connections -
	# ========================
	
	node1conn_src = mc.listConnections(node1,s=True,d=False,p=True,c=True,sh=True) or []
	node1conn_dst = mc.listConnections(node1,s=False,d=True,p=True,c=True,sh=True) or []
	node2conn_src = mc.listConnections(node2,s=True,d=False,p=True,c=True,sh=True) or []
	node2conn_dst = mc.listConnections(node2,s=False,d=True,p=True,c=True,sh=True) or []
	
	# ====================
	# - Disconnect Attrs -
	# ====================
	
	# Disconnect Node 1 Source
	for i in range(0,len(node1conn_src),2):
		try: mc.disconnectAttr(node1conn_src[i+1],node1conn_src[i])
		except: print ('FAILED: '+node1conn_src[i+1]+' X '+node1conn_src[i]+'!')
		else: print ('Disconnected: '+node1conn_src[i+1]+' X '+node1conn_src[i]+'!')
	
	# Disconnect Node 1 Destination
	for i in range(0,len(node1conn_dst),2):
		try: mc.disconnectAttr(node1conn_dst[i],node1conn_dst[i+1])
		except: print ('FAILED: '+node1conn_dst[i]+' X '+node1conn_dst[i+1]+'!')
		else: print ('Disconnected: '+node1conn_dst[i]+' X '+node1conn_dst[i+1]+'!')
		
	# -
	
	# Disconnect Node 2 Source
	for i in range(0,len(node2conn_src),2):
		try: mc.disconnectAttr(node2conn_src[i+1],node2conn_src[i])
		except: print ('FAILED: '+node2conn_src[i+1]+' X '+node2conn_src[i]+'!')
		else: print ('Disconnected: '+node2conn_src[i+1]+' X '+node2conn_src[i]+'!')
	
	# Disconnect Node 2 Destination
	for i in range(0,len(node2conn_dst),2):
		try: mc.disconnectAttr(node2conn_dst[i],node2conn_dst[i+1])
		except: print ('FAILED: '+node2conn_dst[i]+' X '+node2conn_dst[i+1]+'!')
		else: print ('Disconnected: '+node2conn_dst[i]+' X '+node2conn_dst[i+1]+'!')
	
	# =================
	# - Connect Attrs -
	# =================
	
	# - Connect Node 1 ---
	
	# Connect Node 1 Source
	for i in range(0,len(node1conn_src),2):
		dst = node1conn_src[i].replace(node1,node2)
		src = node1conn_src[i+1]
		try: mc.connectAttr(src,dst,f=True)
		except: print ('FAILED: '+src+' -> '+dst+'!')
		else: print ('Connected: '+src+' -> '+dst+'...')
	
	# Connect Node 1 Destination
	for i in range(0,len(node1conn_dst),2):
		src = node1conn_dst[i].replace(node1,node2)
		dst = node1conn_dst[i+1]
		try: mc.connectAttr(src,dst,f=True)
		except: print ('FAILED: '+src+' -> '+dst+'!')
		else: print ('Connected: '+src+' -> '+dst+'...')
	
	# - Connect Node 2 ---
	
	# Connect Node 2 Source
	for i in range(0,len(node2conn_src),2):
		dst = node2conn_src[i].replace(node2,node1)
		src = node2conn_src[i+1]
		try: mc.connectAttr(src,dst,f=True)
		except: print ('FAILED: '+src+' -> '+dst+'!')
		else: print ('Connected: '+src+' -> '+dst+'...')
	
	# Connect Node 2 Destination
	for i in range(0,len(node2conn_dst),2):
		src = node2conn_dst[i].replace(node2,node1)
		dst = node2conn_dst[i+1]
		try: mc.connectAttr(src,dst,f=True)
		except: print ('FAILED: '+src+' -> '+dst+'!')
		else: print ('Connected: '+src+' -> '+dst+'...')
	
	# =================
	# - Return Result -
	# =================
	
	return