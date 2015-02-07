import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.stringUtils
import glTools.utils.transform

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

def verifyNode(node,nodeType):
	'''
	Run standard checks on the specified node. Raise an Exception if any checks fail.
	@param node: Node to verify
	@type node: str
	@param nodeType: Node type
	@type nodeType: str
	'''
	# Check Node Exists
	if not mc.objExists(node):
		raise Exception('Object "'+node+'" does not exists!')
	
	# Check Node Type
	objType = mc.objectType(node)
	if objType != nodeType:
		raise Exception('Object "'+node+'" is not a vaild "'+nodeType+'" node!')

def isVisible(node,checkLodVis=True,checkDrawOverride=True):
	'''
	Check if a specified DAG node is visible by check visibility of all ancestor nodes.
	@param node: Node to verify
	@type node: str
	@param checkLodVis: Check LOD visibility
	@type checkLodVis: bool
	@param checkDrawOverride: Check drawing override visibility
	@type checkDrawOverride: bool
	'''
	# Check Node
	if not mc.objExists(node):
		raise Exception('Object "'+node+'" does not exist!')
	if not mc.ls(node,dag=True):
		raise Exception('Object "'+node+'" is not a valid DAG node!')
	
	# Get Full Path
	fullPath = mc.ls(node,l=True)[0]
	pathPart = fullPath.split('|')
	pathPart.reverse()
	
	# Check Visibility
	isVisible=True
	for part in pathPart:
		
		# Skip Unknown Nodes
		if not part: continue
		if not mc.objExists(part):
			print('Unable to find ancestor node "'+part+'"!')
			continue
		
		# Check Visibility
		if not mc.getAttr(part+'.visibility'):
			isVisible=False
		# Check LOD Visibility
		if checkLodVis:
			if not mc.getAttr(part+'.lodVisibility'):
				isVisible=False
		# Check Drawing Overrides
		if checkDrawOverride:
			if mc.getAttr(part+'.overrideEnabled'):
				if not mc.getAttr(part+'.overrideVisibility'):
					isVisible=False
	
	# Return Result
	return isVisible

def getMObject(object):
	'''
	Return an MObject for the input scene object
	@param object: Object to get MObject for
	@type object: str
	'''
	# Check input object
	if not mc.objExists(object):
		raise Exception('Object "'+object+'" does not exist!!')
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
		raise Exception('Object "'+object+'" does not exist!!')
	
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
			raise Exception('Invalid point value supplied! Not enough list/tuple elements!')
		pos = point[0:3]
	elif (type(point) == str) or (type(point) == unicode):
		
		# Check Transform
		mObject = getMObject(point)
		if mObject.hasFn(OpenMaya.MFn.kTransform):
			try: pos = mc.xform(point,q=True,ws=True,rp=True)
			except: pass
		
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
			raise Exception('Invalid point value supplied! Unable to determine type of point "'+str(point)+'"!')
	else:
		raise Exception('Invalid point value supplied! Invalid argument type!')
		
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
		raise Exception('Object "'+geometry+'" does not exist!')
		
	# Get points to generate weights from
	pointList = OpenMaya.MPointArray()
	if getMObject(geometry).hasFn(OpenMaya.MFn.kTransform):
		try: geometry = mc.listRelatives(geometry,s=True,ni=True,pa=True)[0]
		except:	raise Exception('Object "'+geometry+'" contains no valid geometry!')
	
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
		ptArray.append([mPtArray[i][0],mPtArray[i][1],mPtArray[i][2]])
	
	# Return Result
	return ptArray

def getMBoundingBox(geometry,worldSpace=True):
	'''
	Return an MBoundingBox for the specified geometry
	@param geometry: Geometry to return MBoundingBox for
	@type geometry: str
	@param worldSpace: Calculate bounding box in world or local space
	@type worldSpace: bool
	'''
	# Check geometry
	if geometry and not mc.objExists(geometry):
		raise Exception('Object "'+geometry+'" does not exist!')
	
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

def getCenter(ptList):
	'''
	Calculate the average center position of the specified list of points.
	@param ptList: The list of points to calculate center point for.
	@type ptList: list
	'''
	# Initialize Result
	avgPt = [0,0,0]
	
	# Get Center Point
	numPt = len(ptList)
	for pt in ptList:
		ptPos = glTools.utils.base.getPosition(pt)
		avgPt = [avgPt[0]+ptPos[0],avgPt[1]+ptPos[1],avgPt[2]+ptPos[2]]
	
	# Calculate Average Position
	avgPt = [avgPt[0]/numPt,avgPt[1]/numPt,avgPt[2]/numPt]
	
	# Return Result
	return avgPt

def displayOverride(obj,overrideEnable=0,overrideDisplay=0,overrideLOD=0,overrideVisibility=1,overrideShading=1):
	'''
	Set display override for the specified object.
	@param obj: Object to set display overrides for
	@type obj: str
	@param overrideEnable: Sets the display override enable state for the specified DAG object 
	@type overrideEnable: int
	@param overrideDisplay: Sets the display override type for the specified DAG object. 0=Normal, 1=Template, 2=Reference
	@type overrideDisplay: int
	@param overrideLOD: Sets the display override level of detail value for the specified DAG object. 0=Full, 1=BoundingBox
	@type overrideLOD: int
	@param overrideVisibility: Sets the display override visibility value for the specified DAG object 
	@type overrideVisibility: int
	@param overrideShading: Sets the display override shading value for the specified DAG object 
	@type overrideShading: int
	'''
	# Checks
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!')
	if not mc.ls(obj,dag=True):
		raise Exception('Object "'+obj+'" is not a valid DAG node!')
	# Set Display override values
	mc.setAttr(obj+'.overrideEnabled',overrideEnable)
	mc.setAttr(obj+'.overrideDisplayType',overrideDisplay)
	mc.setAttr(obj+'.overrideLevelOfDetail',overrideLOD)
	mc.setAttr(obj+'.overrideVisibility',overrideVisibility)
	mc.setAttr(obj+'.overrideShading',overrideShading)

def setNodeState(nodeList,state=1):
	'''
	Set the nodeState attribute value of a specified list on nodes
	@param nodeList: List of nodes to set nodeState on.
	@type nodeList: list
	@param state: NodeState value to set.
	@type state: int
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

def renameChain(root,renameStr='',useAlpha=True):
	"""
	Recursive function that renames a non branching hierarchy of nodes based on a rename string.
	The rename string should contain a # character to denate where to place the instance token for the new name.
	@param root: Chain root node
	@type root: str
	@param renameStr: The rename string used to generate the names for each chain node.
	@type renameStr: str
	@param useAlpha: Use alphabetical instance tokens, as opposed to numeric.
	@type useAlpha: bool
	"""
	# =======================
	# - Check Rename String -
	# =======================
	
	# Check Rename String
	if not renameStr:
	
		result = mc.promptDialog(	title='Rename Chain',
									message='Enter Rename String:',
									button=['Rename', 'Cancel'],
									defaultButton='Rename',
									cancelButton='Cancel',
									dismissString='Cancel'	)
		
		if result == 'Rename':
			renameStr = mc.promptDialog(q=True,text=True)	
    
    # Check "#" Characters
	numHash = renameStr.count('#')
	substring = '#' * numHash
	if not renameStr.count(substring):
		raise Exception('Invalid rename string! Pound characters must be consecutive!')
	
	# ==================
	# - Get Chain List -
	# ==================
	
	root = str(root)
	
	chainList = []    
	chainNode = str(mc.ls(mc.listRelatives(root,ad=True,pa=True),type='joint')[0])
	while(True):
		chainList.append(chainNode)
		if chainList[-1] == root: break
		chainNode = str(mc.listRelatives(chainList[-1],p=True,pa=True)[0])
	chainList.reverse()
	chainLen = len(chainList)
	
	# ======================
	# - Rename Chain Nodes -
	# ======================
	
	# Temp Rename to Avoid Name Clash
	for i in range(chainLen):
		indStr = 'XXX'+str(i)
		chainList[i] = mc.rename(chainList[i],renameStr.replace(substring,indStr))
	
	for i in range(chainLen-1):
		
		# Get instance string
		indStr = ''
		if useAlpha: indStr = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		else: indStr = glTools.utils.stringUtils.stringIndex(i+1,len(substring))
		
		# Rename
		chainList[i] = mc.rename(chainList[i],renameStr.replace(substring,indStr))
	
	# Rename Chain End
	chainList[-1] = mc.rename(chainList[-1],renameStr.replace(substring,'End'))
	
	# =================
	# - Retrun Result -
	# =================
	
	return chainList

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
	if not name: name = obj + 'Grp'
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
		raise Exception('Invalid groupType value supplied!!('+str(groupType)+')')
	
	# Generate group name
	prefix = glTools.utils.stringUtils.stripSuffix(control)
	grp = prefix+'_'+groupType
	
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

def dagSort(objectList=[]):
	'''
	Sort the list of DAG objects in the hierarchy
	@param objectList: List of DAG object to sort. If empty, use current selection.
	@type objectList: list
	'''
	# Check Object List
	if not objectList:
		objectList = mc.ls(sl=1)
		objectList = mc.listRelatives(objectList,ad=True)
		objectList = mc.ls(objectList,transforms=True)
	
	# Sort Object List
	objectList.sort()
	objectList.reverse()
	
	# Reorder Objects
	for i in objectList:
		mc.reorder(i,f=True)
	
	# Return Result
	return objectList

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

def renameDuplicates(padding=3):
	'''
	Rename Duplicate Node Names
	@param padding: Index padding for duplicate renaming
	@type padding: int
	'''
	# Get NonUnique Names
	badXforms = [f for f in mc.ls() if '|' in f]
	badXformsUnlock = [f for f in badXforms if mc.lockNode(f,q=1,lock=1)[0] == False]
	count = 0
	
	# Sort list by the number of '|' appearing in each name.
	# This way we can edit names from the bottom of the hierarchy up, and not worry about losing child objects from the list.
	countDict = {}
	for f in badXformsUnlock: countDict[f] = f.count('|')
	
	# Sort the dictionary by value, in reverse, and start renaming.
	renamed = []
	for key,value in sorted(countDict.iteritems(),reverse=True, key=lambda (key,value): (value,key)):
		n = 1
		newObj = mc.rename(key,key.split('|')[-1]+'_'+str(n).zfill(padding))
		renamed.append(newObj)
		while newObj.count('|') > 0:
			# INFINITE LOOP PROBLEM: if the transform and the shape are named the same, this will go on forever.
			# we need to write some kind of exception to prevent this from happening.
			n += 1
			basename = newObj.split('|')[-1]
			newName = '_'.join(basename.split('_')[0:-1])+'_'+str(n).zfill(padding)
			newObj = mc.rename(newObj,newName)
			renamed.append(newObj)
		print 'renamed %s to %s' % (key,newObj)
		count = count+1
	
	# Return Result
	if count < 1:
		print 'No duplicate names found.'
		return []
	else:
		print('Found and renamed '+str(count)+' objects with duplicate names. Check script editor for details.')
		return renamed

def closestPointIndex(pt,ptList):
	'''
	Return the index of the closest point given a list of target points
	@param pt: The source point
	@type pt: list
	@param ptList: List of target points
	@type pt: list
	'''
	# Initialize
	dist = 99999999999
	ind = -1
	
	# Iterate over target points
	for p in range(len(ptList)):
		d = glTools.utils.mathUtils.distanceBetween(pt,ptList[p])
		if d < dist:
			dist = d
			ind = p
	
	# Return Result
	return ind

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
	if not mc.objExists(plug): raise Exception('Plug '+plug+' does not exist!!')
	if not plug.count('.'): raise Exception('Object '+plug+' is not a valid plug (node.attr)!!')
	
	# Check conversionFactorSourcePlug
	if conversionFactorSourcePlug:
		if not mc.objExists(conversionFactorSourcePlug):
			raise Exception('Conversion factor source plug '+conversionFactorSourcePlug+' does not exist!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(control.split('.')[0])
	
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

def remapValue(inputAttr,targetAttr='',inputMin=0,inputMax=1,outputMin=0,outputMax=1,interpType='linear',rampValues=[],prefix=''):
	'''
	Create a remapValue node based on the incoming arguments
	@param inputAttr: Input attribute plug to connect to the remapValue node input.
	@type inputAttr: str
	@param targetAttr: Optional target attribute to receive the output value of the remapValue node.
	@type targetAttr: str
	@param inputMin: Input minimum value for the remapValue node.
	@type inputMin: float
	@param inputMax: Input maximum value for the remapValue node.
	@type inputMax: float
	@param outputMin: Output minimum value for the remapValue node.
	@type outputMin: float
	@param outputMax: Output maximum value for the remapValue node.
	@type outputMax: float
	@param interpType: Ramp interpolation method.
	@type interpType: str
	@param rampValues: List of ramp position and value pairs. [(pos1,val1),(pos2,val2),(pos3,val3)]
	@type rampValues: list
	@param prefix: Naming prefix string for remapValue node
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Input Attributes
	if not mc.objExists(inputAttr):
		raise Exception('Input attribute "'+inputAttr+'" does not exist!')
	try: mc.getAttr(inputAttr,l=True)
	except: raise Exception('Input attribute argument "'+inputAttr+'" is not a valid attribute!')
	
	# Target
	if targetAttr:
		if not mc.objExists(targetAttr):
			raise Exception('Target attribute "'+targetAttr+'" does not exist!')
		try: mc.getAttr(targetAttr,l=True)
		except: raise Exception('Target attribute argument "'+targetAttr+'" is not a valid attribute!')
	
	# Interp Type
	interpTypeList = ['none','linear','smooth','spline']
	if not interpTypeList.count(interpType):
		raise Exception('Invalid interpolation type specified! ("'+interpType+'")')
	
	# Prefix
	if not prefix: prefix = inputAttr.replace('.','_')
	
	# ==========================
	# - Create RemapValue Node -
	# ==========================
	
	remapValueNode = mc.createNode('remapValue',n=prefix+'_remapValue')
	
	# Connect Input
	mc.connectAttr(inputAttr,remapValueNode+'.inputValue',f=True)
	
	# Set Input/Output Min/Max
	mc.setAttr(remapValueNode+'.inputMin',inputMin)
	mc.setAttr(remapValueNode+'.inputMax',inputMax)
	mc.setAttr(remapValueNode+'.outputMin',outputMin)
	mc.setAttr(remapValueNode+'.outputMax',outputMax)
	
	# Interp Type
	interpTypeInd = interpTypeList.index(interpType)
	mc.setAttr(remapValueNode+'.value[0].value_Interp',interpTypeInd)
	mc.setAttr(remapValueNode+'.value[1].value_Interp',interpTypeInd)
	
	# ====================
	# - Plot Ramp Values -
	# ====================
	
	for i in range(len(rampValues)):
		
		mc.setAttr(remapValueNode+'.value['+str(i)+'].value_Position',rampValues[i][0])
		mc.setAttr(remapValueNode+'.value['+str(i)+'].value_FloatValue',rampValues[i][1])
		mc.setAttr(remapValueNode+'.value['+str(i)+'].value_Interp',interpTypeInd)
	
	# ===============================
	# - Connect to Target Attribute -
	# ===============================
	
	if targetAttr: mc.connectAttr(remapValueNode+'.outValue',targetAttr,f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return remapValueNode
