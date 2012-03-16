import maya.mel as mm
import maya.cmds as mc

def listReferences():
	'''
	Return a list of reference node found in the current scene
	'''
	# Get reference list
	refNodes = [str(x) for x in mc.ls(type='reference') if x not in ('sharedReferenceNode', '_UNKNOWN_REF_NODE_')]
	
	# Return Result
	return refNodes

def isReference(refNode):
	'''
	Query if the given node is a valid reference node
	@param refNode: Reference node to query
	@type refNode: str
	'''
	# Check reference node
	if refNode not in listReferences(): return False
	
	# Return Result
	return True

def isReferenced(node):
	'''
	Query if the given node is referenced from an external file
	@param node: Reference node to query
	@type node: str
	'''
	# Check referenced node
	if mc.referenceQuery(node,isNodeReferenced=True): return True
	else: return False
	
def isLoaded(refNode):
	'''
	Query if the reference associated with the given reference node is currently loaded
	@param refNode: Reference node to query
	@type refNode: str
	'''
	# Check reference node
	if not isReference(refNode):
		raise Exception('Object "'+refNode+'" is not a valid reference node!')
		
	# Check load state for given reference
	isLoaded = not mc.file(referenceNode=refNode,q=True,deferReference=True)
	
	# Return Result
	return isLoaded

def getReferenceNode(node):
	'''
	Get the reference node associated with the given referenced object
	@param refNode: Reference node to query
	@type refNode: str
	'''
	# Check Referenced Node
	if not isReferenced(node):
		raise Exception('Object "'+node+'" is not a referenced node!')
	
	# Get Reference Node
	refNode = mc.referenceQuery(node,referenceNode=True)
	
	# Retrun Result
	return refNode

def getReferenceFile(node,withoutCopyNumber=True):
	'''
	Get the reference node associated with the given referenced object or reference node
	@param refNode: Reference node to query
	@type refNode: str
	'''
	# Check Reference/Referenced Node
	if not isReference(node) and not isReferenced(node):
		raise Exception('Object "'+node+'" is not a valid reference node or a node from a referenced file!')
	
	# Get Reference details
	refFile = mc.referenceQuery(node,filename=True,wcn=withoutCopyNumber)
	
	# Retrun Result
	return refFile

def getNamespace(refNode):
	'''
	Get the namespace associated with the specified reference node
	@param refNode: Reference node to query namespace from
	@type refNode: str
	'''
	# Check Referenced Node
	if not isReference(refNode):
		raise Exception('Object "'+refNode+'" is not a referenced node!')
	
	# Get referenced file
	refFile = getReferenceFile(refNode,withoutCopyNumber=False)
	
	# Get Namespace
	ns = mc.file(refFile,q=True,ns=True)
	
	# Return Result
	return ns

def getReferenceFromNamespace(ns):
	'''
	Get the reference node associated with the specified namespace 
	@param ns: Namespace to query reference node from
	@type ns: str
	'''
	# Check Namespace
	if not mc.namespace(ex=ns):
		raise Exception('Namespace "'+ns+'" does not exist!')
	
	# Get all Nodes in Namespace
	nodes = mc.ls(ns+':*')
	
	# For each node in list
	refNode = ''
	for node in nodes:
		
		# Check referenced node
		if not isReferenced(node): continue
		
		# Get reference node - escape
		refNode = getReferenceNode(node)
		break
	
	# Check refNode
	if not refNode:
		print 'Unable to determine reference from namespace'
	
	# Return result
	return refNode

def getReferencedNodes(refNode):
	'''
	Get list of nodes associated with a specified reference node
	@param refNode: Reference node to get list of associated nodes
	@type refNode: str
	'''
	# Check reference node
	if not isReference(refNode):
		raise Exception('Object "'+refNode+'" is not a valid reference node!')
	
	# Get list of associated nodes
	nodes = mc.referenceQuery(refNode,nodes=True,dagPath=True)
	if not nodes: return []
	
	# Return Result
	return nodes

def importReference(refNode,verbose=True):
	'''
	Import the reference associated with the given reference node
	@param refNode: Reference node to import
	@type refNode: str
	'''
	# Check reference node
	if not isReference(refNode):
		raise Exception('Object "'+refNode+'" is not a valid reference node!')
	
	# Get referenced file path
	refFile = ''
	try:
		
		# Get reference file path
		refFile = mc.referenceQuery(refNode,filename=True)
		
	except:
		
		# Check reference node
		if mc.objExists(refNode):
			
			# Delete refNode
			mc.lockNode(refNode,l=False)
			mc.delete(refNode)
		
			# Print message
			if verbose: print('No file associated with reference! Deleting node "'+refNode+'"')
	
	else:
		
		# Import reference
		mc.file(refFile,importReference=True)
		
		# Print message
		if verbose: print('Imported reference "'+refNode+'" from - "'+refFile)

def replaceReference(refNode,refPath):
	'''
	Replace the reference file path for a specified reference node.
	@param refNode: Reference node to replace file path for
	@type refNode: str
	@param refPath: New reference file path
	@type refPath: str
	'''
	# Check reference node
	if not isReference(refNode):
		raise Exception('Object "'+refNode+'" is not a valid reference node!')
	
	# Check reference file
	if getReferenceFile(refNode,withoutCopyNumber=True) == refPath:
		print ('Reference "'+refNode+'" already referencing "'+refPath+'"!')
		return
	
	# Get file type
	refType = ''
	if refPath.endswith('.ma'): refType = 'mayaAscii'
	elif refPath.endswith('.mb'): refType = 'mayaBinary'
	else: raise Exception('Invalid file type! ("'+refPath+'")')
	
	# Replace reference
	mc.file(refPath,loadReference=refNode,typ=refType,options='v=0')
	
	# Return result
	return refPath

def removeReference(refNode):
	'''
	Remove the reference associated with the given reference node
	@param refNode: Reference node to remove
	@type refNode: str
	'''
	# Check reference node
	if not isReference(refNode):
		raise Exception('Object "'+refNode+'" is not a valid reference node!')
	
	# Remove Reference
	mc.file(referenceNode=refNode,removeReference=True)

def unloadReference(refNode):
	'''
	Unload the reference associated with the given reference node
	@param refNode: Reference node to unload
	@type refNode: str
	'''
	# Check reference node
	if not isReference(refNode):
		raise Exception('Object "'+refNode+'" is not a valid reference node!')
	
	# Unload Reference
	mc.file(referenceNode=refNode,unloadReference=True)

def reloadReference(refNode):
	'''
	Reload the reference associated with the given reference node
	@param refNode: Reference node to reload
	@type refNode: str
	'''
	# Check reference node
	if not isReference(refNode):
		raise Exception('Object "'+refNode+'" is not a valid reference node!')
	
	# Unload Reference
	mc.file(referenceNode=refNode,loadReference=True)


def removeUnloadedReferences():
	'''
	Remove all unloaded references from the current scene
	'''
	# Get list of scene reference nodes
	refNodes = listReferences()
	
	# For each reference node
	for refNode in refNodes:
		
		# If NOT loaded
		if not isLoaded(refNode):
			
			# Print message
			print 'Removing unloaded reference "'+str(refNode)+'"...'
			
			# Remove Reference
			mc.file(referenceNode=refNode,removeReference=True)

def removeBakeXformReferences():
	'''
	Remove all bakedXforms references from the current scene
	'''
	# Get list of scene reference nodes
	refNodes = listReferences()
	
	# For each reference node
	for refNode in refNodes:
		
		# Check bakeXform reference
		if ref.count('bakedXforms'):
		
			# Print message
			print 'Unloading bakeXform reference "'+str(ref)+'"...'
		
		# Remove Reference
		mc.file(referenceNode=refNode,removeReference=True)

def removeReferenceEdits(nodeList,parent=False,setAttr=False,addAttr=False,deleteAttr=False,connectAttr=False,disconnectAttr=False):
	'''
	Remove reference edits from a specified list of nodes
	@param nodeList: Reference node to remove
	@type nodeList: list
	@param parent: Remove parent command reference edits
	@type parent: str
	@param setAttr: Remove setAttr command reference edits
	@type setAttr: str
	@param addAttr: Remove addAttr command reference edits
	@type addAttr: str
	@param deleteAttr: Remove deleteAttr command reference edits
	@type deleteAttr: str
	@param connectAttr: Remove connectAttr command reference edits
	@type connectAttr: str
	@param disconnectAttr: Remove disconnectAttr command reference edits
	@type disconnectAttr: str
	'''
	# Check referenced nodes
	rNodeList = []
	for node in nodeList:
		if isReferenced(node): rNodeList.append(node)
		else: print 'Object "'+node+'" is not a referenced node...skipping!'
	
	# Get list for associated reference nodes
	refDict = {}
	for rNode in rNodeList:
		refNode = getReferenceNode(rNode)
		if refDict.has_key(refNode):
			refDict[refNode].append(rNode)
		else:
			refDict[refNode] = [rNode]
	
	# Remove Reference Edits
	for refNode in refDict.keys():
		
		# Unload Reference
		mc.file(unloadReference=refNode)
		
		# Remove Edits - referenceEdit command not working correctly using python WTF??
		for node in refDict[refNode]:
			if setAttr:
				mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand setAttr -removeEdits '+node)
			if addAttr:
				mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand addAttr -removeEdits '+node)
			if deleteAttr:
				mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand deleteAttr -removeEdits '+node)
			if connectAttr:
				mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand connectAttr -removeEdits '+node)
			if disconnectAttr:
				mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand disconnectAttr -removeEdits '+node)
			if parent:
				mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand parent -removeEdits '+node)
		
		# Reload Reference
		mc.file(loadReference=refNode)
	
	# Return result
	return sorted([str(ref) in refDict.keys()])

def removeParentEdits(node):
	'''
	'''
	# Get Reference details
	refNode = getReferenceNode(node)
	
	# Unload Reference
	mc.file(unloadReference=refNode)
	
	# Remove Edits - referenceEdit command not working correctly using python WTF??
	mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand parent -removeEdits '+refNode)
	
	# Reload Reference
	mc.file(loadReference=refNode)

def removeConnectAttrEdits(nodeList):
	'''
	'''
	# Get Reference details
	refNode = getReferenceNode(nodeList[0])
	
	# Unload Reference
	mc.file(unloadReference=refNode)
	
	# Remove Edits - referenceEdit command not working correctly using python WTF??
	for node in nodeList:
		mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand connectAttr -removeEdits '+node)
		mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand disconnectAttr -removeEdits '+node)
	
	# Reload Reference
	mc.file(loadReference=refNode)

