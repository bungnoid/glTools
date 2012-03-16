import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.stringUtils

def isType(nodeName,nodeType):
	'''
	Check if the input object is of the specified node type
	@param nodeName: Object to query type
	@type nodeName: str
	@param nodeType: Node type to query
	@type nodeType: str
	'''
	# Check object exists
	if not mc.objExists(nodeName): return False
	# Check node type
	if mc.objectType(nodeName) != nodeType: return False
	# Return result
	return True

def getMObject(object):
	'''
	Return an MObject for the input scene object
	@param object: Object to get MObject for
	@type object: str
	'''
	# Check input object
	if not mc.objExists(object):
		raise UserInputError('Object "'+object+'" does not exist!!')
	# Get selection list
	selectionList = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(object,selectionList)
	mObject = OpenMaya.MObject()
	selectionList.getDependNode(0,mObject)
	# Return result
	return mObject
	
def getMDagPath(object):
	'''
	Return an MDagPath for the input scene object
	@param object: Object to get MDagPath for
	@type object: str
	'''
	# Check input object
	if not mc.objExists(object):
		raise UserInputError('Object "'+object+'" does not exist!!')
	
	# Get selection list
	selectionList = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(object,selectionList)
	mDagPath = OpenMaya.MDagPath()
	selectionList.getDagPath(0,mDagPath)
	
	# Return result
	return mDagPath

def getPosition(point):
	'''
	Return the position of any point or transform
	@param point: Point to return position for
	@type point: str or list or tuple
	'''
	# Initialize point value
	pos = []
	
	# Determine point type
	if (type(point) == list) or (type(point) == tuple):
		if len(point) < 3:
			raise UserInputError('Invalid point value supplied! Not enough list/tuple elements!')
		pos = point[0:3]
	elif (type(point) == str) or (type(point) == unicode):
		
		# pointPosition query
		if not pos:
			try: pos = mc.pointPosition(point)
			except: pass
		
		# xform - rotate pivot query
		if not pos:
			try: pos = mc.xform(point,q=True,ws=True,rp=True)
			except: pass
		
		# Unknown type
		if not pos:
			raise UserInputError('Invalid point value supplied! Unable to determine type of point "'+str(point)+'"!')
	else:
		raise UserInputError('Invalid point value supplied! Invalid argument type!')
		
	# Return result
	return pos

def getMPoint(point):
	'''
	Return the position of any point or transform as an MPoint object
	@param point: Point to return MPoint position for
	@type point: str or list or tuple
	'''
	# Check for MPoint
	if type(point) == OpenMaya.MPoint: return point
	# Get position
	pos = getPosition(point)
	# Build MPoint
	mPoint = OpenMaya.MPoint(pos[0],pos[1],pos[2],1.0)
	# Return result
	return mPoint
	
def getMPointArray(geometry,worldSpace=True):
	'''
	Return an MPointArray containing the component positions for the specified geometry
	@param geometry: Geometry to return MPointArray for
	@type geometry: str
	@param worldSpace: Return point positions in world or object space
	@type worldSpace: bool
	'''
	# Check geometry
	if geometry and not mc.objExists(geometry):
		raise UserInputError('Object "'+geometry+'" does not exist!')
		
	# Get points to generate weights from
	pointList = OpenMaya.MPointArray()
	if getMObject(geometry).hasFn(OpenMaya.MFn.kTransform):
		try: geometry = mc.listRelatives(geometry,s=True,ni=True,pa=True)[0]
		except:	raise UserInputError('Object "'+geometry+'" contains no valid geometry!')
	
	# Check worldSpace
	if worldSpace:
		shapeObj = getMDagPath(geometry)
		mSpace = OpenMaya.MSpace.kWorld
	else:
		shapeObj = getMObject(geometry)
		mSpace = OpenMaya.MSpace.kObject
	
	# Check shape type
	shapeType = mc.objectType(geometry)
	if shapeType == 'mesh':
		meshFn = OpenMaya.MFnMesh(shapeObj)
		meshFn.getPoints(pointList,mSpace)
	if shapeType == 'nurbsCurve':
		curveFn = OpenMaya.MFnNurbsCurve(shapeObj)
		curveFn.getCVs(pointList,mSpace)
	if shapeType == 'nurbsSurface':
		surfaceFn = OpenMaya.MFnNurbsSurface(shapeObj)
		surfaceFn.getCVs(pointList,mSpace)
	
	# Return result
	return pointList

def getPointArray(geometry,worldSpace=True):
	'''
	Return a point array containing the component positions for the specified geometry
	@param geometry: Geometry to return point array for
	@type geometry: str
	@param worldSpace: Return point positions in world or object space
	@type worldSpace: bool
	'''
	# Initialize arrays
	ptArray = []
	mPtArray = getMPointArray(geometry,worldSpace)
	
	# Convert to python list
	for i in range(mPtArray.length()):
		ptArray.extend([mPtArray[i][0],mPtArray[i][1],mPtArray[i][2]])
	
	# Return Result
	return ptArray

def getMBoundingBox(geometry,worldSpace=True):
	'''
	Return an MBoundingBox for the specified geometry
	@param geometry: Geometry to return MBoundingBox for
	@type geometry: str
	'''
	# Check geometry
	if geometry and not mc.objExists(geometry):
		raise UserInputError('Object "'+geometry+'" does not exist!')
	
	# Get MBoundingBox
	geoPath = getMDagPath(geometry)
	geoNodeFn = OpenMaya.MFnDagNode(geoPath)
	geoBBox = geoNodeFn.boundingBox()
	
	# Transform to world space
	if worldSpace:
		geoBBox.transformUsing(geoPath.exclusiveMatrix())
	else:
		print('!!!Local space bounding box is not reliable with current code!!!')
		geoBBox.transformUsing(geoNodeFn.transformationMatrix().inverse())
	
	# Return result
	return geoBBox

def toggleNode(nodeList,state=1):
	'''
	Toggle the nodeState attribute value of a specified list on nodes
	@param obj: Object to group
	@type obj: str
	'''
	# Check input type
	if type(nodeList) == str or type(nodeList) == unicode: nodeList = [str(nodeList)]
	
	# For each node in the input list
	for node in nodeList:
		
		# Check node
		if not mc.objExists(node):
			raise Exception('Node "'+node+'" does not exist!')
		
		# Check nodeState attr
		if state and mc.getAttr(node+'.nodeState') == 0: continue
		if not state and mc.getAttr(node+'.nodeState') == 1: continue
		if not mc.getAttr(node+'.nodeState',se=True):
			print('nodeState attribute for node "'+node+'" is not settable! Skipping node...')
		
		# Set nodeState value
		if state: mc.setAttr(node+'.nodeState',0)
		else: mc.setAttr(node+'.nodeState',1)

def group(obj,center=True,orient=True,groupType='transform',name=''):
	'''
	Create a group centered and oriented to the specified transform.
	@param obj: Object to group
	@type obj: str
	@param center: Match group pivot to transform
	@type center: bool
	@param orient: Orient group to transform
	@type orient: bool
	@param groupType: Group transform type
	@type groupType: str
	@param name: Name for group transform node
	@type name: bool
	'''
	# Check group name
	if not name: name = obj.replace(obj.split('_')[-1],'grp')
	# Create Group
	grp = mc.createNode(groupType,n=name)
	# Align to object
	if center: mc.delete(mc.pointConstraint(obj,grp))
	if orient: mc.delete(mc.orientConstraint(obj,grp))
	# Parent group and control
 	objParent = mc.listRelatives(obj,p=True,pa=True)
	if objParent: grp = mc.parent(grp,objParent[0])[0]
	mc.parent(obj,grp)
	# Return result
	return grp

def group_old(control,groupType=1,center=True,orient=True):
	'''
	Create a group centered and oriented to the specified control.
	@param control: Control to group
	@type control: str
	@param groupType: Specify type of buffer. 0=Group:"*_grp", 1=Buffer:"*_buf", 2=BufferJoint:"*_bfj"
	@type groupType: int
	@param center: Match group pivot to transform
	@type center: bool
	@param orient: Orient group to transform
	@type orient: bool
	'''
	# Check groupType
	if not range(3).count(groupType):
		raise UserInputError('Invalid groupType value supplied!!('+str(groupType)+')')
	
	# Generate group name
	prefix = stringUtils.stripSuffix(control)
	grp = prefix+'_'+grpType
	
	# Create Group
	if groupType == 2: grp = mc.createNode('joint',n=grp)
	else: grp = mc.createNode('transform',n=grp)
	
	# Align to object
	grp = mc.parent(grp,control)[0]
	mc.makeIdentity(grp,apply=True,t=1,r=orient,s=1,jo=1,n=0)
	
	# Correct heirarchy
	parent = mc.listRelatives(control,p=True,pa=True)
	if parent: grp = mc.parent(grp,parent[0])[0]
	else: grp = mc.parent(grp,w=1)[0]
	# Reset transform scale values
	mc.makeIdentity(grp,apply=True,t=0,r=0,s=1,n=0)
	control = mc.parent(control,grp)[0]
	
	# Center pivot
	if center:
		piv = mc.xform(control,q=True,ws=True,rp=True)
		mc.xform(grp,piv=piv,ws=True)
	
	# Return group name as result string
	return grp
	
def getHierarchyList(start,end):
	'''
	Return an ordered hierarchy object list between a specified start and end object
	@param start: Start object to generate hierarchy list for
	@type start: str
	@param end: End object to generate hierarchy list for
	@type end: str
	'''
	# Check start and end objects
	if not mc.objExists(start):
		raise Exception('Start object "'+start+'" does not exist!')
	if not mc.objExists(end):
		raise Exception('End object "'+end+'" does not exist!')
		
	# Check end is in start hierarchy
	start_hier = mc.listRelatives(start,ad=True)
	if not start_hier.count(end):
		raise Exception('End object "'+end+'" is not a decendant of start object "'+start+'"!')
	
	# Build hierarchy list
	heir = [end]
	while heir[-1] != start:
		par = mc.listRelatives(heir[-1],p=True)[0]
		heir.append(par)
	
	# Reverse hierarchy list for correct order
	heir.reverse()
	
	# Return result
	return heir

def parentList(childList,parentList):
	'''
	Parent a list of child transforms to a list of parent transforms
	@param childList: List of transforms to be parented
	@type childList: list
	@param parentList: List of transforms to be parented to
	@type parentList: list
	'''
	if len(childList) != len(parentList):
		raise Exception('List match error!! Child/Parent count mis-match!')
	for i in range(len(childList)):
		mc.parent(childList[i],parentList[i])

def renameHistoryNodes(obj,nodeType,prefix='',suffix='',stripOldSuffix=True):
	'''
	Rename nodes in a specified objects history based on a given or derived prefix and suffix
	@param obj: Object whose history nodes will be renamed
	@type obj: str
	@param nodeType: Node types to isolate for rename
	@type nodeType: str or list
	@param prefix: Name prefix for nodes. If empty, derive from object name
	@type prefix: str
	@param suffix: Name suffix for nodes. If empty, derive from node type
	@type suffix: str
	'''
	# Check object
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!')
	
	# Check prefix
	if not prefix:
		if stripOldSuffix: prefix = glTools.utils.stringUtils.stripSuffix(obj)
		else: prefix = obj
	
	# Get object history
	if nodeType.lower() == 'all': nodeHist = mc.ls(mc.listHistory(obj))
	else: nodeHist = mc.ls(mc.listHistory(obj),type=nodeType)
	nodeHist.sort()
	
	# For each history node
	nodeCount = len(nodeHist)
	for n in range(nodeCount):
		
		# Check suffix
		if not suffix: nodeSuffix = mc.objectType(nodeHist[n])
		else: nodeSuffix = suffix
		
		# Check index
		if nodeCount > 1: nodeSuffix = glTools.utils.stringUtils.stringIndex(n,1) + '_' + nodeSuffix
		
		# Rename node
		nodeHist[n] = mc.rename(nodeHist[n],prefix+'_'+nodeSuffix)
	
	# Return result
	return nodeHist

def unitConversion(plug,conversionFactor=1.0,conversionFactorSourcePlug='',plugIsSource=True,prefix=''):
	'''
	Create a unit conversion node for the given destination attribute
	@param plug: Plug to be connected to the unitConversion node
	@type plug: str
	@param conversionFactor: Conversion factor value
	@type conversionFactor: float
	@param conversionFactorSourcePlug: Plug to supply incoming connection for conversion factor
	@type conversionFactorSourcePlug: str
	@param plugIsSource: Specifies the plug as either the source or destination of the unitConversion
	@type plugIsSource: bool
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Check plug
	if not mc.objExists(plug): raise UserInputError('Plug '+plug+' does not exist!!')
	if not plug.count('.'): raise UserInputError('Object '+plug+' is not a valid plug (node.attr)!!')
	
	# Check conversionFactorSourcePlug
	if conversionFactorSourcePlug:
		if not mc.objExists(conversionFactorSourcePlug):
			raise UserInputError('Conversion factor source plug '+conversionFactorSourcePlug+' does not exist!')
	
	# Check prefix
	if not prefix: prefix = stringUtils.stripSuffix(control.split('.')[0])
	
	# Get existing plug connections
	conns = mc.listConnections(plug,s=not plugIsSource,d=plugIsSource,p=True)
			
	# Create unitConversion node
	unitConversion = mc.createNode('unitConversion',n=prefix+'_unitConversion')
	mc.setAttr(unitConversion+'.conversionFactor',conversionFactor)
	
	# Connect conversion factor
	if conversionFactorSourcePlug:
		mc.connectAttr(conversionFactorSourcePlug,unitConversion+'.conversionFactor',f=True)
	
	# Connect plug
	if plugIsSource:
		mc.connectAttr(plug,unitConversion+'.input',f=True)
	else:
		if conns: mc.connectAttr(conns[0],unitConversion+'.input',f=True)
	
	# Connect to destination plugs
	if plugIsSource:
		if conns:
			for conn in conns: mc.connectAttr(unitConversion+'.output',conn,f=True)
	else:
		mc.connectAttr(unitConversion+'.output',plug,f=True)
	
	# Return result
	return unitConversion
