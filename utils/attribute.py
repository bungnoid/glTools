import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import re
import random

import glTools.utils.base
import glTools.utils.mathUtils

def isAttr(attr):
	'''
	Test is the input argument string is the name of a valid attribute.
	@param attr: The attribute to query
	@type attr: str
	'''
	if not mc.objExists(attr): return False
	try: mc.getAttr(attr,l=True)
	except: return False
	else: return True

def dataType(attr):
	'''
	Return the specified attribute data type as a string value
	@param attr: The attribute to return the data type for
	@type attr: str
	'''
	# Check Attribute
	if not isAttr(attr): raise Exception('Attribute "'+attr+'" does not exist!')
	# Get Attribute Data Type
	dataType = mc.getAttr(attr,type=True)
	# Return Result
	return dataType

def getAttrMPlug(attr):
	'''
	Return the MPlug object for the specified attribute
	@param attr: The attribute to return the MPlug for
	@type attr: str
	'''
	# Check attribute
	if not mc.objExists(attr):
		raise Exception('Attribute "'+attr+'" does not exist!')
	
	# Split attr name to elements
	attrElemList = attr.split('.')
	
	# Get node function class
	attrObj = glTools.utils.base.getMObject(attrElemList[0])
	attrObjFn = OpenMaya.MFnDependencyNode(attrObj)
	
	# Get attr element components (name, index)
	attrElem = re.findall(r'\w+', attrElemList[1])
	
	# Get MPlug to top level attribute
	attrMPlug = attrObjFn.findPlug(attrElem[0],True)
	if len(attrElem) == 2: attrMPlug = attrMPlug.elementByLogicalIndex(int(attrElem[1]))
	
	# Traverse to lowest child attribute
	for i in range(2,len(attrElemList)):
		
		# Get attr element components (name, index)
		attrElem = re.findall(r'\w+', attrElemList[i])
		
		# Get child attributes
		childIndex = -1
		for n in range(attrMPlug.numChildren()):
			childPlug = attrMPlug.child(n)
			print 'Looking for "'+attrElem[0]+'", found "'+childPlug.partialName()+'"'
	
	# Return result
	return attrMPlug

def multiIndexList(attr):
	'''
	Return a list of the existing index elements of the specified multi attribute
	@param attr: The attribute to get the index list for
	@type attr: str
	'''
	# Get attribute MPlug
	attrMPlug = getAttrMPlug(attr)
	
	# Check multi
	if not attrMPlug.isArray():
		raise Exception('Attribute "'+attr+'" is not a multi!')
	
	# Check existing indices
	exIndexList = OpenMaya.MIntArray()
	attrMPlug.getExistingArrayAttributeIndices(exIndexList)
	
	# Return Result
	return list(exIndexList)

def getConnectionIndex(attr,asSource=True,connectedTo=None):
	'''
	'''
	# Get MPlug
	attrPlug = getAttrMPlug(attr)
	
	# Get Connected Plugs
	attrPlugConnections = OpenMaya.MPlugArray()
	connected = attrPlug.connectedTo(attrPlugConnections,not(asSource),asSource)
	if not connected:
		connectionType = 'outgoing' if asSource else 'incoming'
		raise Exception('No '+connectionType+' connections found for attribute "'+attr+'"!')
	
	# Get Connected Index
	for i in range(attrPlugConnections.length()):
		connectedPlug = attrPlugConnections[i]
		connectedNode = connectedPlug.partialName(True,False,False,False,False).split('.')[0]
		if connectedTo and not connectedTo == connectedNode:
			#print(connectedTo+' != '+connectedNode)
			continue
		return connectedPlug.logicalIndex()
	
	# Return Result
	return -1

def nextAvailableMultiIndex(attr,start=0,useConnectedOnly=True,maxIndex=10000000):
	'''
	Return the index of the first available (no incoming connections) element of the specified attribute
	@param attr: The attribute to find the next available index for
	@type attr: str
	@param start: Multi index to start the connection check from
	@type start: int
	@param useConnectedOnly: Specifies if existing indices are based in incoming connection only. Otherwise, any existing indices will be considered unavailable.
	@type useConnectedOnly: bool
	@param maxIndex: The maximum index search value
	@type maxIndex: int
	'''
	# Initialize next index 
	nextIndex = -1
	
	if useConnectedOnly:
		
		# Check array indices
		for i in range(start,maxIndex):
			
			# Check connections
			conn = mc.connectionInfo(attr+'['+str(i)+']',sourceFromDestination=True)
			if not conn:
				nextIndex = i
				break
	else:
		
		# Check existing indices
		exIndexList = multiIndexList(attr)
		indexCount = len(exIndexList)
		
		# Determin next available
		if indexCount: nextIndex = list(exIndexList)[-1] + 1
		else: nextIndex = 0
	
	# Return result
	return nextIndex

def default(attr):
	'''
	Return the default value for the specified attribute
	@param attr: The attribute to query the default value for
	@type attr: str
	'''
	# Check attr
	if not mc.objExists(attr):
		raise Exception('Attribute "'+attr+'" does not exist!')
	
	# Get object from attribute
	obj = mc.ls(attr,o=True)[0]
	at = attr.replace(obj+'.','')
	
	# Build default attribute lists
	xformAttrList = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ']
	xformAttrList.extend(['tx','tx','tx','rx','rx','rx'])
	scaleAttrList = ['scaleX','scaleY','scaleZ']
	scaleAttrList.extend(['sx','sx','sx'])
	visAttrList = ['visibility','v']
	
	# Query attribute default value
	if xformAttrList.count(at): return 0.0
	if scaleAttrList.count(at): return 1.0
	if visAttrList.count(at): return 1.0
	
	# Query default for user defined attribute
	val = mc.addAttr(attr,q=True,dv=True)
	
	# Return result
	return val

def distributeAttrValue(targetList,targetAttr,rangeStart=0.0,rangeEnd=1.0,smoothStep=0.0):
	'''
	Distribute a range of attribute values across list of target objects
	@param targetList: List of target objects to distribute the attribute values across
	@type targetList: list
	@param targetAttr: The target attribute that the distributed values will be applied to
	@type targetAttr: str
	@param rangeStart: The distribution range minimum value
	@type rangeStart: float
	@param rangeEnd: The distribution range maximum value
	@type rangeEnd: float
	@param smoothStep: Amount of value smoothing to apply to the distribution
	@type smoothStep: float
	'''
	# Check target list
	for i in range(len(targetList)):
		if not mc.objExists(targetList[i]):
			raise Exception('Object "'+targetList[i]+'" does not exist!')
		if not mc.objExists(targetList[i]+'.'+targetAttr):
			raise Exception('Object "'+targetList[i]+'" has no ".'+targetAttr+'" attribute!')
	
	# Get value list
	vList = glTools.utils.mathUtils.distributeValue(len(targetList),1.0,rangeStart,rangeEnd)
	
	# Apply values to target list
	for i in range(len(targetList)):
		val = vList[i]
		if smoothStep: val = glTools.utils.mathUtils.smoothStep(val,rangeStart,rangeEnd,smoothStep)
		mc.setAttr(targetList[i]+'.'+targetAttr,val)

def randomizeAttrValues(objectList,attr,minValue=0.0,maxValue=1.0):
	'''
	Randomize attribute values on a list of objects
	@param objectList: List of objects to randomize attributes on
	@type objectList: list
	@param attr: Attribute to randomize
	@type attr: str
	@param minValue: Minimum value to randomize, default is 0
	@type minValue: float
	@param maxValue: Maximum value to randomize, default is 1
	@type maxValue: float
	'''
	# Verify list type argument
	if type(objectList) == str: objectList = [objectList]
	
	# Iterate through object list
	for i in range(len(objectList)):
		# Append abject and attribute names
		objAttr = objectList[i]+'.'+attr
		
		# Check attribute extists
		if not mc.objExists(objAttr):
			raise Exception('Attribute "'+objAttr+'" does not exist!!')
		
		# Generate random attribute value
		rnd = random.random()
		attrVal = minValue + (maxValue - minValue) * rnd
		
		# Set Attribute value
		mc.setAttr(objAttr, attrVal)

def deleteUserAttrs(obj,attrList=[],keepIfConnected=False):
	'''
	Delete user defined attrs from a specified object
	@param obj: The source objects to copy the attributes from 
	@type obj: str
	@param attrList: A list of attributes to delete. If empty, defaults to all. 
	@type attrList: list
	'''
	# Check object
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!!')
	
	# Get attribute list
	if not attrList: attrList = mc.listAttr(obj,ud=True)
	if not attrList: attrList = []
	
	# Delete attributes
	for attr in attrList:
		
		# Check Attribute Exists
		if mc.objExists(obj+'.'+attr):
			
			# Check Connections
			if keepIfConnected:
				conns = mc.listConnections(obj+'.'+attr,s=True,d=True)
				if conns: continue
			
			# Delete Attribute
			try:
				mc.setAttr(obj+'.'+attr,l=False)
				mc.deleteAttr(obj,at=attr)
			except:
				print('Problem removing attribute "'+obj+'.'+attr+'". Skipping to next attribute.')
	
	# Return result
	return attrList

def copyAttr(src,dst,attr):
	'''
	Copy attribute from a source object to a destination object
	@param src: The source object to copy the attribute from
	@type src: str
	@param dst: The destination object to copy the attribute to
	@type dst: str
	@param attr: The attributes to copy.
	@type attr: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Source and Destination
	if not mc.objExists(src):
		raise Exception('Source object "'+src+'" does not exist!!')
	if not mc.objExists(dst):
		raise Exception('Destination object "'+dst+'" does not exist!!')
	
	# Check Source Attribute
	if not mc.attributeQuery(attr,n=src,ex=True):
		raise Exception('Source attribute "'+src+'.'+attr+'" does not exist!!')
	
	# ==================
	# - Copy Attribute -
	# ==================
	
	# Check/Skip Multi
	if mc.attributeQuery(attr,n=src,m=True):
		print('Skipping multi attribute "'+src+'.'+attr+'"...')
		return src+'.'+attr
	
	# Get Attribute Details
	attrVal = mc.getAttr(src+'.'+attr)
	attrType = mc.addAttr(src+'.'+attr,q=True,at=True)
	defaultVal = mc.addAttr(src+'.'+attr,q=True,dv=True)
	attrVisible = mc.getAttr(src+'.'+attr,cb=True)
	attrKeyable = mc.getAttr(src+'.'+attr,k=True)
	attrLocked = mc.getAttr(src+'.'+attr,l=True)
	
	# Get Attribute Data Type
	dataType = attrType
	if attrType == 'typed':
		dataType = str(mc.addAttr(src+'.'+attr,q=True,dt=True)[0])
	
	# Check Destination Attribute
	if not mc.attributeQuery(attr,n=dst,ex=True):
		
		# Add Destination Attribute
		if attrType == 'typed':
			mc.addAttr(dst,ln=attr,dt=dataType)	
		else:
			mc.addAttr(dst,ln=attr,at=attrType,dv=defaultVal)
	
	# Set Destination Attribute
	if attrType == 'typed':
		mc.setAttr(dst+'.'+attr,attrVal,type=dataType)
	else:
		mc.setAttr(dst+'.'+attr,attrVal)
	
	# Attribute Visibile
	if attrVisible:
		try: mc.setAttr(dst+'.'+attr,cb=True)
		except: pass
	
	# Attribute Keyable
	if attrKeyable:
		try: mc.setAttr(dst+'.'+attr,k=True)
		except: pass
	
	# Lock Attribute
	if attrLocked:
		try: mc.setAttr(dst+'.'+attr,l=True)
		except: pass
	
	# =================
	# - Return Result -
	# =================
	
	return dst+'.'+attr

def copyUserAttrs(src,dst,attrList=[],search='',replace='',copyConnections=False):
	'''
	Copy user defined attrs from a source object to a destination object
	@param src: The source objects to copy the attributes from.
	@type src: str
	@param dst: The destination objects to copy the attributes to.
	@type dst: str
	@param attrList: A list of attributes to delete. If empty, defaults to all.
	@type attrList: list
	@param search: A string to search (and replace) for in attribute values.
	@type search: str
	@param replace: A string to replace (and search) for in attribute values.
	@type replace: str
	@param copyConnections: Copy incoming and outgoing attribute connections.
	@type copyConnections: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Source and Destination
	if not mc.objExists(src):
		raise Exception('Source object "'+src+'" does not exist!!')
	if not mc.objExists(dst):
		raise Exception('Destination object "'+dst+'" does not exist!!')
	
	# Check Attribute List
	if not attrList: attrList = mc.listAttr(src,ud=True)
	if not attrList: return []
	
	# ===================
	# - Copy Attributes -
	# ===================
	
	for attr in attrList:
		
		srcAttr = src+'.'+attr
		dstAttr = copyAttr(src,dst,attr)
		
		# Search and Replace Attr Value
		attrType = mc.addAttr(srcAttr,q=True,at=True)
		if attrType == 'typed':
			dataType = str(mc.addAttr(src+'.'+attr,q=True,dt=True)[0])
			if dataType == 'string':
					attrVal = mc.getAttr(srcAttr)
					attrVal = attrVal.replace(search,replace)
					mc.setAttr(dstAttr,attrVal,type='string')
		
		# Copy connections
		if copyConnections:
			
			# Incoming connections
			inConnList = mc.listConnections(srcAttr,s=True,d=False,p=True)
			if inConnList:
				for inConn in inConnList:
					if search or replace:
						inConn = inConn.replace(search,replace)
					mc.connectAttr(inConn,dstAttr,f=True)
			
			# Outgoing connections
			outConnList = mc.listConnections(srcAttr,d=True,s=False,p=True)
			if outConnList:
				for outConn in outConnList:
					if search or replace:
						outConn = inConn.replace(search,replace)
					mc.connectAttr(dstAttr,outConn,f=True)
		
	# =================
	# - Return Result -
	# =================
	
	return attrList
	
def copyAttrList(src,dst,connect=False,srcAsMaster=True,attrList=[]):
	'''
	Copy user defined attrs from a source object to a destination object
	@param src: The source objects to copy the attributes from 
	@type src: str
	@param dst: The destination objects to copy the attributes to 
	@type dst: str
	@param connect: Connect the copied attribute to the original 
	@type connect: bool
	@param srcAsMaster: Specifies the direction of the attribute connection. 
	@type srcAsMaster: bool
	@param attrList: List of attributes to copy. If empty, use channelbox selection 
	@type attrList: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Source and Destination
	if not mc.objExists(src):
		raise Exception('Source object "'+src+'" does not exist!!')
	if not mc.objExists(dst):
		raise Exception('Destination object "'+dst+'" does not exist!!')
	
	# Check Attribute List
	if not attrList:
		channelBox = 'mainChannelBox'
		attrList = mc.channelBox(channelBox,q=True,selectedMainAttributes=True)
	if not attrList: return []
	
	# ===================
	# - Copy Attributes -
	# ===================
	
	dstAttrList = []
	for attr in attrList:
		
		# Check Source Attributes
		srcAttr = src+'.'+attr
		if not mc.attributeQuery(attr,n=src,ex=True):
			raise Exception('Source attribute "'+src+'.'+attr+'" does not exist!')
		
		# Check Destination Attribute
		dstAttr = copyAttr(src,dst,attr)
		dstAttrList.append(dstAttr)
			
		# Connect attributes
		if connect:
			if srcAsMaster:
				mc.connectAttr(srcAttr,dstAttr,f=True)
			else:
				mc.connectAttr(dstAttr,srcAttr,f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return dstAttrList

def attributeSeparator(control,attr):
	'''
	Create a separator attribute on the specified control object
	@param control: The control to add the separator attribute to
	@type control: str
	@param control: The separator attribute name
	@type control: str
	'''
	# Check control
	if not mc.objExists(control):
		raise Exception('Control object "'+control+'" does not exist!')
	
	# Check attribute
	if mc.objExists(control+'.'+attr):
		raise Exception('Control attribute "'+control+'.'+attr+'" already exists!')
	
	# Create attribute
	mc.addAttr(control,ln=attr,at='enum',en=':-:')
	mc.setAttr(control+'.'+attr,cb=True)
	mc.setAttr(control+'.'+attr,l=True)
	
	# Return result
	return (control+'.'+attr)

def moveToBottom(attribute):
	'''
	Move specified attribute to the bottom of the channel box
	'''
	# Determine object and attribute names from input argument
	obj = attribute.split('.')[0]
	attr = attribute.split('.')[-1]
	
	# Delete attribute temporarily
	mc.deleteAttr(obj,attribute=attr)
	
	# Undo deletion
	mc.undo()

def reorder(attr,pos='bottom'):
	'''
	Reorder specified user defined attribute
	@param attr: Attribute to reorder
	@type attr: str
	@param pos: Reorder position. Valid position values - "up", "down", "top" and "bottom".
	@type pos: str
	'''
	# Checks
	if not mc.objExists(attr):
		raise Exception('Attribute "'+attr+'" does not exist!')
	
	if not attr.count('.'):
		raise Exception('Unable to determine object from attribute"'+attr+'"!')
	
	# Get attribute info
	obj = mc.ls(attr,o=True)
	if not obj: raise Exception('Unable to determine object from attribute"'+attr+'"!')
	obj = obj[0]
	at = attr.replace(obj+'.','')
	
	# Get attribute lists
	udAttrList = mc.listAttr(obj,ud=True)
	if not udAttrList: udAttrList = []
	keyAttrList = mc.listAttr(obj,k=True)
	if not keyAttrList: keyAttrList = []
	cbAttrList = mc.listAttr(obj,cb=True)
	if not cbAttrList: cbAttrList = []
	allAttrList = [i for i in udAttrList if keyAttrList.count(i) or cbAttrList.count(i)]
	allAttrLen = len(allAttrList)
	
	# Get relative attribute index 
	attrInd = allAttrList.index(at)
	
	# Move UP
	if pos == 'up':
		
		if not attrInd: return	
		moveToBottom(obj+'.'+allAttrList[attrInd-1])
		for i in allAttrList[attrInd+1:]:
			moveToBottom(obj+'.'+i)
		
	# Move DOWN
	if pos == 'down':
		
		if attrInd == (allAttrLen-1): return
		moveToBottom(obj+'.'+allAttrList[attrInd])
		
		if attrInd >= (allAttrLen-1): return
		
		for i in allAttrList[attrInd+2:]:
			moveToBottom(obj+'.'+i)
		
	# Move to TOP
	if pos == 'top':
		
		for i in range(len(allAttrList)):
			if i == attrInd: return
			moveToBottom(obj+'.'+allAttrList[i])
	
	# Move to BOTTOM
	if pos == 'bottom':
		
		moveToBottom(obj+'.'+allAttrList[attrInd])
	
	# Refresh UI
	mc.channelBox('mainChannelBox',e=True,update=True)

def rename(attr,name):
	'''
	Rename specified attribute
	'''
	# Check attribute
	if not mc.objExists(attr):
		raise Exception('Attribute "'+attr+'" does not exist!')
	
	# Rename (alias) attribute
	result = mc.aliasAttr(name,attr)
	
	# Return result
	return result
