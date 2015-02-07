import maya.cmds as mc

import types

def getNS(obj,topOnly=True):
	'''
	Get the namespace of the specified object
	@param obj: The object to get namespace from
	@type obj: str
	@param topOnly: Return the top level namespace only.
	@type topOnly: bool
	'''
	# Check Object
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!')
	
	# Check namespace
	NS = ''
	if not obj.count(':'): return NS
	
	# Get Namespace
	if topOnly: NS = obj.split(':')[0]
	else: NS = obj.replace(':'+obj.split(':')[-1],'')
	
	# Return namespace
	return NS

def getNSList(objList,topOnly=True):
	'''
	Get a list of namespaces from a list of scene nodes
	@param objList: The list of object to get namespaces from
	@type objList: list
	@param topOnly: Return the top level namespace only.
	@type topOnly: bool
	'''
	# Get namespace list form selection
	NSlist = []
	if isinstance(objList,types.StringTypes):
		objList = [str(objList)]
	for obj in objList:
		NS = getNS(obj,topOnly=topOnly)
		if not NS in NSlist:
			NSlist.append(NS)
	
	# Remove Duplicates (Done Above!)
	#returnNSlist = []
	#[returnNSlist.append(NS) for NS in NSlist if not NS in returnNSlist]
	#NSlist = list(set(NSlist)) - Set does not return corrent order!
	
	# Return result
	return NSlist

def getAllNS(excludeList=['UI','shared']):
	'''
	List all scene namespaces, excluding those specified in the excludeList argument
	@param excludeList: List of namespaces to exclude from result
	@type excludeList: list
	'''
	# Get all scene namespaces
	nsList = mc.namespaceInfo(lon=True)
	
	# Remove exclude list items
	[nsList.remove(ns) for ns in excludeList if nsList.count(ns)]
	
	# Return result
	return nsList

def resetNS():
	'''
	Reset to global namespace (':') 
	'''
	# Reset scene namespace
	mc.namespace(set=':')

def deleteNS(NS):
	'''
	Delete the specified namespace
	@param NS: The namespace to delete
	@type NS: str
	'''
	# Check namespace
	if not NS:
		raise Exception('Invalid namespace specified!')
	if not mc.namespace(ex=NS):
		raise Exception('Namespace "'+NS+'" does not exist!')
	
	# Print Message
	print('Deleting Namespace: '+NS)
	
	# Delete namespace
	mc.namespace(mv=[NS,':'],f=True)
	mc.namespace(rm=NS)

def moveNS(srcNS,dstNS):
	'''
	Move all items from the source namespace to the destination namespace.
	@param srcNS: The source namespace
	@type srcNS: str
	@param dstNS: The destination namespace
	@type dstNS: str
	'''
	# Check NS
	if not mc.namespace(exists=srcNS):
		raise Exception('Source namespace "'+srcNS+'" does not exist!')
	
	# Check Destination NS
	if not mc.namespace(exists=dstNS):
		
		# Create newNS
		dstNS = mc.namespace(add=dstNS,f=True)
		
	# Move namespace
	mc.namespace(mv=(srcNS,dstNS),f=True)
	
	# Return newNS
	return newNS

def renameNS(NS,newNS,parentNS=None):
	'''
	Rename the specified namespace
	@param NS: The current namespace name
	@type NS: str
	@param newNS: The new namespace name
	@type newNS: str
	@param parentNS: The new namespace name
	@type parentNS: str or None
	'''
	# Check NS
	if not mc.namespace(exists=NS):
		raise Exception('Namespace "'+NS+'" does not exist!')
	if mc.namespace(exists=newNS):
		raise Exception('Namespace "'+newNS+'" already exist!')
	
	# Rename NS
	if not parentNS: mc.namespace(rename=[NS,newNS])
	else: mc.namespace(rename=[NS,newNS],parent=parentNS)
	
	# Return newNS
	return newNS

def stripNS(obj):
	'''
	Return the specified object name after stripping the namespace
	@param obj: The object to strip namespace from
	@type obj: str
	'''
	return obj.split(':')[-1]

def getAllInNS(ns):
	'''
	Get all the dependency node contained in the specified namespace
	@param ns: The namespace to query
	@type ns: str
	'''
	# Check namespace
	if not mc.namespace(ex=ns):
		raise Exception('Namespace "'+ns+'" does not exist!')
	
	# Get Current Namespace
	currNS = mc.namespaceInfo(currentNamespace=True)
	
	# Set Namespace
	mc.namespace(set=ns)
	
	# List all objects in namespace
	nsNodeList = mc.namespaceInfo(lod=True,dagPath=True)
	
	# Reset Namespace
	mc.namespace(set=currNS)
	
	# Return result
	return nsNodeList

def addHierarchyToNS(root,NS,replaceNS=True):
	'''
	Add all DAG objects under a specified root to the given namespace.
	@param root: The hierarchy root object
	@type root: str
	@param NS: The hierarchy namespace
	@type NS: str
	@param replaceNS: Replace existing namespaces. If False, append the NS.
	@type replaceNS: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check namespace
	if not mc.namespace(ex=NS): mc.namespace(add=NS)
	
	# Check Hierarchy Root
	if not mc.objExists(root):
		raise Exception('Hierarchy root object "'+root+'" does not exist!')
	
	# ======================
	# - Get Hierarchy List -
	# ======================
	
	hier = mc.ls(mc.listRelatives(root,ad=True,pa=True),transforms=True)
	hier.append(root)
	
	# ====================
	# - Add to Namespace -
	# ====================
	
	for i in range(len(hier)):
		item = hier[i]
		currNS = getNS(item,topOnly=False)
		if currNS:
			mc.rename(item,item.replace(currNS,NS))
		else:
			mc.rename(item,NS+':'+item)
		hier[i] = item
	
	# =================
	# - Return Result -
	# =================
	
	return hier