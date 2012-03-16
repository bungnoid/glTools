import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import re
import random

import glTools.utils.base
import glTools.utils.mathUtils

class UserInputError(Exception): pass

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
	if len(attrElem) == 2: attrMPlug = attrMPlug.elementByLogicalIndex(attrElem[1])
	
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

def nextAvailableMultiIndex(attr,start=0,useConnectedOnly=True,maxIndex=10000000):
	'''
	Return the index of the first available (no incoming connections) element of the specified attribute
	@param attr: The attribute to find the next available index for
	@type attr: str
	@param start: Multi index to start the connection check from
	@type start: int
	@param useConnectedOnly: Specifies if existing indices are based in incoming connection only
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
			conn = mc.connectionInfo(attr+'['+str(i)+']',sfd=True)
			if not conn:
				nextIndex = i
				break
	else:
		
		# Get attribute MPlug
		attrMPlug = getAttrMPlug(attr)
		
		# Check multi
		if not attrMPlug.isArray():
			raise Exception('Attribute "'+attr+'" is not a multi!')
		
		# Check existing indices
		exIndexList = OpenMaya.MIntArray()
		indexCount = attrMPlug.getExistingArrayAttributeIndices(exIndexList)
		
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
	obj = mc.ls(attr,o=True)
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
			raise UserInputError('Object "'+targetList[i]+'" does not exist!')
		if not mc.objExists(targetList[i]+'.'+targetAttr):
			raise UserInputError('Object "'+targetList[i]+'" has no ".'+targetAttr+'" attribute!')
	
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
			raise UserInputError('Attribute "'+objAttr+'" does not exist!!')
		
		# Generate random attribute value
		rnd = random.random()
		attrVal = minValue + (maxValue - minValue) * rnd
		
		# Set Attribute value
		mc.setAttr(objAttr, attrVal)

def deleteUserAttrs(obj,attrList=[]):
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
		try:
			mc.setAttr(obj+'.'+attr,l=False)
			mc.deleteAttr(obj,at=attr)
		except:
			print('Problem removing attribute "'+obj+'.'+attr+'". Continuing onto next arttribute.')
	
	# Return result
	return attrList

def copyUserAttrs(src,dst,attrList=[],search='',replace='',copyConnections=False):
	'''
	Copy user defined attrs from a source object to a destination object
	@param src: The source objects to copy the attributes from 
	@type src: str
	@param dst: The destination objects to copy the attributes to 
	@type dst: str
	@param attrList: A list of attributes to delete. If empty, defaults to all. 
	@type attrList: list
	@param search: A string to search (and replace) for in attribute values 
	@type search: str
	@param replace: A string to replace (and search) for in attribute values 
	@type replace: str
	'''
	# Check Source and Destination
	if not mc.objExists(src):
		raise Exception('Source object "'+src+'" does not exist!!')
	if not mc.objExists(dst):
		raise Exception('Destination object "'+dst+'" does not exist!!')
	
	# Get attribute list
	if not attrList: attrList = mc.listAttr(src,ud=True)
	if not attrList: attrList = []
	
	# Delete attributes
	for attr in attrList:
		
		# Get attrbute value
		try: attrVal = mc.getAttr(src+'.'+attr)
		except: attrVal = None
		
		# Get attrbute details
		attrType = mc.addAttr(src+'.'+attr,q=True,at=True)
		
		# Check attribute lock state
		attrLocked = mc.getAttr(dst+'.'+attr,l=True)
		
		# Add attribute to destination object
		if attrType == 'typed':
			# Get attribute data type
			dataType = str(mc.addAttr(src+'.'+attr,q=True,dt=True)[0])
			
			# Add attribute
			if not mc.objExists(dst+'.'+attr):
				mc.addAttr(dst,ln=attr,dt=dataType)
			
			# Search and Replace
			mAttrVal = attrVal.replace(search,replace)
			
			# Set attribute value
			if attrLocked: mc.setAttr(dst+'.'+attr,l=False)
			try: mc.setAttr(dst+'.'+attr,mAttrVal,type=dataType)
			except: print ('Unable to set attribte "'+dst+'.'+attr+'"!')
			if attrLocked: mc.setAttr(dst+'.'+attr,l=True)
		else:
			# Add attribute
			if not mc.objExists(dst+'.'+attr):
				mc.addAttr(dst,ln=attr,at=attrType)
			
			# Set attribute value
			if attrLocked: mc.setAttr(dst+'.'+attr,l=False)
			try: mc.setAttr(dst+'.'+attr,attrVal)
			except: print ('Unable to set attribte "'+dst+'.'+attr+'"!')
			if attrLocked: mc.setAttr(dst+'.'+attr,l=True)
		
		# Copy connections
		if copyConnections:
			
			# Incoming connections
			inConnList = mc.listConnections(src+'.'+attr,s=True,d=False,p=True)
			if inConnList:
				for inConn in inConnList:
					if search or replace:
						inConn = inConn.replace(search,replace)
					mc.connectAttr(inConn,dst+'.'+attr,f=True)
			
			# Outgoing connections
			outConnList = mc.listConnections(src+'.'+attr,d=True,s=False,p=True)
			if outConnList:
				for outConn in outConnList:
					if search or replace:
						outConn = inConn.replace(search,replace)
					mc.connectAttr(dst+'.'+attr,outConn,f=True)
		
	# Return result
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
	# Get channel selection
	if not attrList:
		channelBox = 'MayaWindow|mayaMainWindowForm|formLayout3|formLayout11|formLayout32|formLayout33|ChannelsLayersPaneLayout|formLayout36|menuBarLayout1|frameLayout1|mainChannelBox'
		attrList = mc.channelBox(channelBox,q=True,selectedMainAttributes=True)
		if not attrList: cbAttrList = []
	
	# Check source attribute
	if not mc.objExists(src+'.'+attr):
		raise Exception('Source attribute "'+src+'.'+attr+'" does not exist!')
	
	# Create attributes on destination
	for attr in attrList:
		if not mc.objExists(dst+'.'+attr):
			defaultValue = mc.getAttr(src+'.'+attr)
			mc.addAttr(dst,ln=attr,dv=defaultValue,k=True)
			
		# Connect attributes
		if connect:
			if srcAsMaster:
				mc.connectAttr(src+'.'+attr,dst+'.'+attr,f=True)
			else:
				mc.connectAttr(dst+'.'+attr,src+'.'+attr,f=True)
	
	# Return result
	return [dst+'.'+attr for attr in attrList]

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
	
	# Return result
	return (control+'.'+attr)

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
	keyAttrList = mc.listAttr(obj,k=True)
	cbAttrList = mc.listAttr(obj,cb=True)
	allAttrList = [i for i in udAttrList if keyAttrList.count(i) or cbAttrList.count(i)]
	allAttrLen = len(allAttrList)
	
	# Get relative attribute index 
	attrInd = allAttrList.index(at)
	
	# Move UP
	if pos == 'up':
		
		if not attrInd: return	
		mc.renameAttr(obj+'.'+allAttrList[attrInd-1],allAttrList[attrInd-1]+'XXX')
		mc.renameAttr(obj+'.'+allAttrList[attrInd-1]+'XXX',allAttrList[attrInd-1])
		for i in allAttrList[attrInd+1:]:
			mc.renameAttr(obj+'.'+i,i+'XXX')
			mc.renameAttr(obj+'.'+i+'XXX',i)
		
	# Move DOWN
	if pos == 'down':
		
		if attrInd == (allAttrLen-1): return
		mc.renameAttr(obj+'.'+allAttrList[attrInd],allAttrList[attrInd]+'XXX')
		mc.renameAttr(obj+'.'+allAttrList[attrInd]+'XXX',allAttrList[attrInd])
		
		if attrInd >= (allAttrLen-1): return
		
		for i in allAttrList[attrInd+2:]:
			mc.renameAttr(obj+'.'+i,i+'XXX')
			mc.renameAttr(obj+'.'+i+'XXX',i)
		
	# Move to TOP
	if pos == 'top':
		
		for i in range(len(allAttrList)):
			if i == attrInd: return
			mc.renameAttr(obj+'.'+allAttrList[i],allAttrList[i]+'XXX')
			mc.renameAttr(obj+'.'+allAttrList[i]+'XXX',allAttrList[i])
	
	# Move to BOTTOM
	if pos == 'bottom':
		
		mc.renameAttr(obj+'.'+allAttrList[attrInd],allAttrList[attrInd]+'XXX')
		mc.renameAttr(obj+'.'+allAttrList[attrInd]+'XXX',allAttrList[attrInd])
	
	# Refresh UI
	channelBox = 'MayaWindow|mayaMainWindowForm|formLayout3|formLayout11|formLayout32|formLayout33|ChannelsLayersPaneLayout|formLayout36|menuBarLayout1|frameLayout1|mainChannelBox'
	mc.channelBox(channelBox,e=True,update=True)
