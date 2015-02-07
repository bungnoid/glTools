import maya.mel as mm
import maya.cmds as mc

import ika.maya.file
import ika.context.util

import os.path

def listReferences(parentNS=None):
	'''
	Return a list of reference node found in the current scene
	@param parentNS: Parent namespace to query reference nodes from
	@type parentNS: str or None
	'''
	# Get Reference List
	refNodes = []
	for ref in mc.ls(type='reference'):
		if 'sharedReferenceNode' in ref: continue
		if '_UNKNOWN_REF_NODE_' in ref: continue
		if parentNS:
			if not ref.startswith(parentNS):
				continue
		refNodes.append(ref)
	
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

def isProxyManager(proxyManager):
	'''
	Query if the given node is a valid proxyManager node
	@param proxyManager: Proxy manager node to query
	@type proxyManager: str
	'''
	# Check Proxy Manager
	if not proxyManager: return False
	if not mc.objExists(proxyManager): return False
	if mc.objectType(proxyManager) != 'proxyManager': return False
	
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
	
	# Return Result
	return refNode

def getReferenceFile(node,withoutCopyNumber=True):
	'''
	Get the reference file associated with the given referenced object or reference node
	@param refNode: Reference node to query
	@type refNode: str
	'''
	# Check Reference/Referenced Node
	if not isReference(node) and not isReferenced(node):
		raise Exception('Object "'+node+'" is not a valid reference node or a node from a referenced file!')
	
	# Get Reference details
	refFile = mc.referenceQuery(node,filename=True,wcn=withoutCopyNumber)
	
	# Return Result
	return refFile

def getReferenceProxyManager(refNode):
	'''
	Get the reference proxy manager attached to the specified reference node
	@param refNode: Reference node to query
	@type refNode: str
	'''
	# Check Reference Proxy Message Attribute
	if not mc.attributeQuery('proxyMsg',n=refNode,ex=True):
		print('Reference "'+refNode+'" has no "proxyMsg" attribute! Unable to determine proxy manager...')
		return None
	
	# Get Connected Proxy Manager	
	proxyManager = mc.ls(mc.listConnections(refNode+'.proxyMsg',s=True,d=False) or [],type='proxyManager') or []
	if not proxyManager:
		print('Reference "'+refNode+'" has no valid "proxyMsg" connections! Unable to determine proxy manager...')
		return None
	
	# Check Result
	if len(proxyManager) > 1:
		print('Multiple proxy manager nodes attached to reference "'+refNode+'"! Retunring first node only...')
		print(str(proxyManager))
	
	# Return Result
	return proxyManager[0]

def getReferencesFromProxyManager(proxyManager):
	'''
	Get reference nodes attached to the specified proxy manager node.
	@param proxyManager: Proxy manager node to get reference nodes from.
	@type proxyManager: str
	'''
	# Check Proxy Manager
	if not isProxyManager(proxyManager):
		raise Exception('Object "'+str(proxyManager)+'" is not a valid proxyManager node!')
	
	# Get Connected Reference Nodes
	refList = mc.listConnections(proxyManager+'.proxyList',s=False,d=True) or []
	
	# Return Result
	return refList

def getNamespace(refNode):
	'''
	Get the namespace associated with the specified reference node
	@param refNode: Reference node to query namespace from
	@type refNode: str
	'''
	# Check Referenced Node
	if not isReference(refNode):
		raise Exception('Object "'+refNode+'" is not a referenced node!')
	
	# Get Namespace from File - OLD
	#refFile = getReferenceFile(refNode,withoutCopyNumber=False)
	#ns = mc.file(refFile,q=True,ns=True)
	
	# Get Namespace from Reference - NEW
	ns = mc.referenceQuery(refNode,namespace=True)
	if ns.startswith(':'): ns = ns[1:]
	
	# Return Result
	return ns

def getReferenceFromNamespace(ns,parentNS=None):
	'''
	Get the reference node associated with the specified namespace 
	@param ns: Namespace to query reference node from
	@type ns: str
	@param parentNS: Parent namespace to query reference nodes from
	@type parentNS: str or None
	'''
	# Check Namespace
	if ns.endswith(':'): ns = ns[:-1]
	if not mc.namespace(ex=ns):
		raise Exception('Namespace "'+ns+'" does not exist!')
	
	# Check Parent Namespace
	if parentNS: parentNS+=':'
	else: parentNS=''
		
	# Check Each Reference
	for refNode in listReferences(parentNS):
		
		# Get Reference Namespace
		try: refNS = mc.referenceQuery(refNode,namespace=True)
		except:
			#print('Unable to get namespace from reference "'+refNode+'"!')
			continue
		
		# Strip Leading ":"
		if refNS.startswith(':'): refNS = refNS[1:]
		
		# Check Namespace Match
		if refNS == parentNS+ns:
			
			# Check Proxy Manager Connections
			if mc.attributeQuery('proxyMsg',n=refNode,ex=True):
				proxyManager = mc.ls(mc.listConnections(refNode+'.proxyMsg',s=True,d=False) or [],type='proxyManager') or []
				if proxyManager:
					# Check Active Proxy
					activeProxyPlug = mc.connectionInfo(proxyManager[0]+'.activeProxy',destinationFromSource=True)[0]
					activeProxyInfo = mc.connectionInfo(activeProxyPlug,destinationFromSource=True)
					if not activeProxyInfo: raise Exception('Error getting active reference from proxy manager "'+proxyManager[0]+'"!')
					return mc.ls(activeProxyInfo[0],o=True)[0]
					
			# Return Reference
			return refNode
		
	# No Reference Found from Namespace - Print Msg
	print('Unable to determine reference from namespace: '+ns)
	return ''

def allReferencesFromNamespace(ns):
	'''
	Get all reference nodes associated with the specified namespace.
	This is used to return all reference nodes associated with a Reference Proxy Manager.
	@param ns: Namespace to query reference nodes from
	@type ns: str
	'''
	# Get Loaded Reference from Namespace
	refMain = getReferenceFromNamespace(ns)
	
	# Get Proxy Manager from Reference
	proxyManager = getReferenceProxyManager(refMain)
	
	# Get Reference Nodes from Proxy Manager
	refList = getReferencesFromProxyManager(proxyManager)
	
	# Return Reference
	return refList

def getReferenceFromNamespaceOLD(ns):
	'''
	Get the reference node associated with the specified namespace 
	#@param ns: Namespace to query reference node from
	#@type ns: str
	'''
	# Check Namespace
	if ns.endswith(':'): ns = ns[:-1]
	if not mc.namespace(ex=ns):
		raise Exception('Namespace "'+ns+'" does not exist!')
		
	# Get all Nodes in Namespace
	nodes = mc.ls(ns+':*')
	
	# For each node in list
	refNode = ''
	for node in nodes:
		
		# Check referenced node
		if not isReferenced(node):
			print('('+ns+') NS node not referenced - '+node)
			continue
		
		# Get reference node - escape
		refNode = getReferenceNode(node)
		break
	
	# Check refNode
	if not refNode:
		print('Unable to determine reference from namespace: '+ns)
	
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
	@param verbose: Print detailed progress messages
	@type verbose: bool
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
			
			# Print message
			if verbose: print('No file associated with reference! Deleting node "'+refNode+'"')
			
			# Delete refNode
			mc.lockNode(refNode,l=False)
			mc.delete(refNode)
	
	else:
		
		# Import reference
		mc.file(refFile,importReference=True)
		
		# Print message
		if verbose: print('Imported reference "'+refNode+'" from - "'+refFile)

def replaceReference(refNode,refPath,verbose=True):
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
	
	# Print message
	if verbose: print('Replaced reference "'+refNode+'" using file - "'+refPath+'"')
	
	# Return result
	return refPath

def removeReference(refNode,verbose=True):
	'''
	Remove the reference associated with the given reference node
	@param refNode: Reference node to remove
	@type refNode: str
	'''
	# Check reference node
	if not isReference(refNode):
		raise Exception('Object "'+refNode+'" is not a valid reference node!')
	
	# Remove Reference
	refFile = getReferenceFile(refNode)
	try: mc.file(referenceNode=refNode,removeReference=True)
	except Exception, e:
		print('Error removing reference "'+refNode+'"! Exception Msg: '+str(e))
		return
	
	# Print message
	if verbose: print('Removed reference "'+refNode+'"! ('+refFile+')')

def unloadReference(refNode,verbose=True):
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
	
	# Print message
	if verbose: print('Unloadeded reference "'+refNode+'"! ('+getReferenceFile(refNode)+')')

def reloadReference(refNode,verbose=True):
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
	
	# Print message
	if verbose: print('Reloadeded reference "'+refNode+'"! ('+getReferenceFile(refNode)+')')

def renameReferenceNamespace(refNS,newNS):
	'''
	Rename reference namespace
	@param refNS: Reference namespace to rename
	@type refNS: str
	@param newNS: New namespace
	@type newNS: str
	'''
	# Check Namespace
	if mc.namespace(ex=newNS): raise Exception('Namespace "'+newNS+'" already exists! Unable to rename reference namespace...')
	
	# Get Reference Node from Namespace
	refNode = getReferenceFromNamespace(refNS)
	if not refNode: raise Exception('Namespace "'+refNS+'" is not a reference namespace!')
	
	# Get Reference File Path
	refPath = getReferenceFile(refNode)
	
	# Rename Reference Namespace
	mc.file(refPath,e=True,namespace=newNS)
	
	# Return Result
	return newNS

def recordSourcePath(targetNode):
	'''
	Record the reference source file path to the specified target node based on the connected reference node
	@param targetNode: Referenced node to record source reference path to
	@type targetNode: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Referenced Node
	if not isReferenced(targetNode):
		raise Exception('Object "'+targetNode+'" is not a referenced node!')
	
	# ======================
	# - Get Reference Data -
	# ======================
	
	# Get Reference Node
	refNode = getReferenceNode(targetNode)
	
	# Get Reference Source Path
	refPath = getReferenceFile(refNode,withoutCopyNumber=True)
	realPath = os.path.realpath(refPath)
	
	# ======================
	# - Record Source Path -
	# ======================
	
	# Add String Attr
	mc.addAttr(targetNode,ln='sourceReferencePath',dt='string')
	# Set String Attr Value
	mc.setAttr(targetNode+'.sourceReferencePath',realPath,type='string')
	# Lock Attribute
	#mc.setAttr(targetNode+'.sourceReferencePath',l=True)
	
	# =================
	# - Return Result -
	# =================
	
	return realPath

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

def getEditNodes(	refNode,
					showNamespace=False,
					showDagPath=False,
					successfulEdits=True,
					failedEdits=True,
					parent=True,
					setAttr=True,
					addAttr=True,
					deleteAttr=True,
					connectAttr=True,
					disconnectAttr=True	):
	'''
	List nodes with reference edits from a specified reference node
	@param refNode: Reference node to get editted nodes from
	@type refNode: str
	@param showNamespace: Return node names including namespace
	@type showNamespace: bool
	@param showDagPath: Return node names with full dag path
	@type showDagPath: bool
	@param successfulEdits: Return successful edits
	@type successfulEdits: bool
	@param failedEdits: Return Failed edits
	@type failedEdits: bool
	@param parent: Return parent command edits
	@type parent: bool
	@param setAttr: Return setAttr command edits
	@type setAttr: bool
	@param addAttr: Return addAttr command edits
	@type addAttr: bool
	@param deleteAttr: Return deleteAttr command edits
	@type deleteAttr: bool
	@param connectAttr: Return connectAttr command edits
	@type connectAttr: bool
	@param disconnectAttr: Return disconnectAttr command edits
	@type disconnectAttr: bool
	'''
	# ================================
	# - Build ReferenceQuery Command -
	# ================================
	
	refQueryCmd = 'referenceQuery '
	refQueryCmd += ' -showNamespace '+str(showNamespace).lower()
	refQueryCmd += ' -showDagPath '+str(showDagPath).lower()
	refQueryCmd += ' -successfulEdits '+str(successfulEdits).lower()
	refQueryCmd += ' -failedEdits '+str(failedEdits).lower()
	
	nodeList = []
	if parent and setAttr and addAttr and deleteAttr and connectAttr and disconnectAttr:
		nodeList.extend(mm.eval(refQueryCmd+' -editNodes '+refNode) or [])
	else:
		if parent: nodeList.extend(mm.eval(refQueryCmd+' -editCommand parent -editNodes '+refNode) or [])
		if setAttr: nodeList.extend(mm.eval(refQueryCmd+' -editCommand setAttr -editNodes '+refNode) or [])
		if addAttr: nodeList.extend(mm.eval(refQueryCmd+' -editCommand addAttr -editNodes '+refNode) or [])
		if deleteAttr: nodeList.extend(mm.eval(refQueryCmd+' -editCommand deleteAttr -editNodes '+refNode) or [])
		if connectAttr: nodeList.extend(mm.eval(refQueryCmd+' -editCommand connectAttr -editNodes '+refNode) or [])
		if disconnectAttr: nodeList.extend(mm.eval(refQueryCmd+' -editCommand disconnectAttr -editNodes '+refNode) or [])
	
	# Remove Duplicates and Sort
	if nodeList:
		nodeList = list(set(nodeList))
		nodeList.sort()
	
	# Clean Node Names
	if not showDagPath: nodeList = [i.split('|')[-1] for i in nodeList]
	
	# =================
	# - Return Result -
	# =================
	
	return nodeList

def getEditAttrs(	refNode,
					node = '',
					showNamespace=False,
					showDagPath=False,
					successfulEdits=True,
					failedEdits=True,
					parent=True,
					setAttr=True,
					addAttr=True,
					deleteAttr=True,
					connectAttr=True,
					disconnectAttr=True	):
	'''
	List nodes with reference edits from a specified reference node
	@param refNode: Reference node to get editted nodes from
	@type refNode: str
	@param node: Referenced node to get editted attributes from
	@type node: str
	@param showNamespace: Return node names including namespace
	@type showNamespace: bool
	@param showDagPath: Return node names with full dag path
	@type showDagPath: bool
	@param successfulEdits: Return successful edits
	@type successfulEdits: bool
	@param failedEdits: Return Failed edits
	@type failedEdits: bool
	@param parent: Return parent command edits
	@type parent: bool
	@param setAttr: Return setAttr command edits
	@type setAttr: bool
	@param addAttr: Return addAttr command edits
	@type addAttr: bool
	@param deleteAttr: Return deleteAttr command edits
	@type deleteAttr: bool
	@param connectAttr: Return connectAttr command edits
	@type connectAttr: bool
	@param disconnectAttr: Return disconnectAttr command edits
	@type disconnectAttr: bool
	'''
	# ==============
	# - Check Node -
	# ==============
	
	refNS = getNamespace(refNode)+':'
	editNode = node
	
	# Check Short Name
	#if not mc.objExists(node): node = node.split('|')[-1]
	# Check Append NS
	#if not mc.objExists(node): node = refNS+node
	node = refNS+node
	# Unable to Determine Node
	#if not mc.objExists(node): raise Exception('Reference edit node "'+editNode+'" not found!')
	
	# ================================
	# - Build ReferenceQuery Command -
	# ================================
	
	refQueryCmd = 'referenceQuery '
	refQueryCmd += ' -showNamespace '+str(showNamespace).lower()
	refQueryCmd += ' -showDagPath '+str(showDagPath).lower()
	refQueryCmd += ' -successfulEdits '+str(successfulEdits).lower()
	refQueryCmd += ' -failedEdits '+str(failedEdits).lower()
	
	attrList = []
	if parent and setAttr and addAttr and deleteAttr and connectAttr and disconnectAttr:
		attrList.extend(mm.eval(refQueryCmd+' -editAttrs '+node) or [])
	else:
		if parent: attrList.extend(mm.eval(refQueryCmd+' -editCommand parent -editAttrs '+node) or [])
		if setAttr: attrList.extend(mm.eval(refQueryCmd+' -editCommand setAttr -editAttrs '+node) or [])
		if addAttr: attrList.extend(mm.eval(refQueryCmd+' -editCommand addAttr -editAttrs '+node) or [])
		if deleteAttr: attrList.extend(mm.eval(refQueryCmd+' -editCommand deleteAttr -editAttrs '+node) or [])
		if connectAttr: attrList.extend(mm.eval(refQueryCmd+' -editCommand connectAttr -editAttrs '+node) or [])
		if disconnectAttr: attrList.extend(mm.eval(refQueryCmd+' -editCommand disconnectAttr -editAttrs '+node) or [])
	
	# Remove Duplicates and Sort
	if attrList:
		attrList = list(set(attrList))
		attrList.sort()
	
	# =================
	# - Return Result -
	# =================
	
	return attrList

def getEditCommands(	refNode,
						node = '',
						showNamespace=False,
						showDagPath=False,
						successfulEdits=True,
						failedEdits=True,
						parent=True,
						setAttr=True,
						addAttr=True,
						deleteAttr=True,
						connectAttr=True,
						disconnectAttr=True):
	'''
	Remove reference edits from a specified list of nodes
	@param refNode: Reference node to get editted nodes from
	@type refNode: str
	@param node: Referenced node to get edit commands from
	@type node: str
	@param showNamespace: Return node names including namespace
	@type showNamespace: bool
	@param showDagPath: Return node names with full dag path
	@type showDagPath: bool
	@param successfulEdits: Return successful edits
	@type successfulEdits: bool
	@param failedEdits: Return Failed edits
	@type failedEdits: bool
	@param parent: Return parent command edits
	@type parent: bool
	@param setAttr: Return setAttr command edits
	@type setAttr: bool
	@param addAttr: Return addAttr command edits
	@type addAttr: bool
	@param deleteAttr: Return deleteAttr command edits
	@type deleteAttr: bool
	@param connectAttr: Return connectAttr command edits
	@type connectAttr: bool
	@param disconnectAttr: Return disconnectAttr command edits
	@type disconnectAttr: bool
	'''
	# ==============
	# - Check Node -
	# ==============
	
	refNS = getNamespace(refNode)+':'
	editNode = node
	
	if not node: node = refNode
	else: node = refNS+node
	
	# Check Short Name
	#if not mc.objExists(node): node = node.split('|')[-1]
	# Check Append NS
	#if not mc.objExists(node): node = refNS+node
	#node = refNS+node
	# Unable to Determine Node
	#if not mc.objExists(node): raise Exception('Reference edit node "'+editNode+'" not found!')
	
	# ================================
	# - Build ReferenceQuery Command -
	# ================================
	
	refQueryCmd = 'referenceQuery '
	refQueryCmd += ' -showNamespace '+str(showNamespace).lower()
	refQueryCmd += ' -showDagPath '+str(showDagPath).lower()
	refQueryCmd += ' -successfulEdits '+str(successfulEdits).lower()
	refQueryCmd += ' -failedEdits '+str(failedEdits).lower()
	
	cmdList = []
	if parent and setAttr and addAttr and deleteAttr and connectAttr and disconnectAttr:
		cmdList.extend(mm.eval(refQueryCmd+' -editStrings '+node) or [])
	else:
		if parent: cmdList.extend(mm.eval(refQueryCmd+' -editCommand parent -editStrings '+node) or [])
		if setAttr: cmdList.extend(mm.eval(refQueryCmd+' -editCommand setAttr -editStrings '+node) or [])
		if addAttr: cmdList.extend(mm.eval(refQueryCmd+' -editCommand addAttr -editStrings '+node) or [])
		if deleteAttr: cmdList.extend(mm.eval(refQueryCmd+' -editCommand deleteAttr -editStrings '+node) or [])
		if connectAttr: cmdList.extend(mm.eval(refQueryCmd+' -editCommand connectAttr -editStrings '+node) or [])
		if disconnectAttr: cmdList.extend(mm.eval(refQueryCmd+' -editCommand disconnectAttr -editStrings '+node) or [])
	
	# Remove Duplicates and Sort
	if cmdList:
		cmdList = list(set(cmdList))
		#cmdList.sort()
	
	# Return Result
	return cmdList

def removeReferenceEdits(	refNode,
							node='',
							successfulEdits=True,
							failedEdits=True,
							parent=False,
							setAttr=False,
							addAttr=False,
							deleteAttr=False,
							connectAttr=False,
							disconnectAttr=False	):
	'''
	Remove reference edits from a specified list of nodes
	@param refNode: Reference node to remove node edits from
	@type refNode: str
	@param node: Referenced node to remove reference edits for
	@type node: str
	@param successfulEdits: Return successful edits
	@type successfulEdits: bool
	@param failedEdits: Return Failed edits
	@type failedEdits: bool
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
	# ==========
	# - Checks -
	# ==========
	
	# Check Reference Node
	if not isReference(refNode): raise Exception('Object "'+refNode+'" is not a valid reference node!')
	refNS = getNamespace(refNode)+':'
	
	# Check Reference is Loaded
	refLoaded = isLoaded(refNode)
	if refLoaded: mc.file(unloadReference=refNode)
	
	# Check Node
	if not node: node = refNode
	
	# ==========================
	# - Remove Reference Edits -
	# ==========================
	
	refQueryCmd = 'referenceEdit'
	refQueryCmd += ' -successfulEdits '+str(successfulEdits).lower()
	refQueryCmd += ' -failedEdits '+str(failedEdits).lower()
	
	# Print Progress
	print('Removing Reference Edits: "'+node+'"...')
	
	# Remove Edits
	if parent and setAttr and addAttr and deleteAttr and connectAttr and disconnectAttr:
		# Remove All Edits
		print(refQueryCmd+' -removeEdits '+node)
		mm.eval(refQueryCmd+' -removeEdits '+node)
	else:
		# Remove Edits Per Command
		if parent: mm.eval(refQueryCmd+'-editCommand parent -removeEdits '+node)
		if setAttr: mm.eval(refQueryCmd+'-editCommand setAttr -removeEdits '+node)
		if addAttr: mm.eval(refQueryCmd+'-editCommand addAttr -removeEdits '+node)
		if deleteAttr: mm.eval(refQueryCmd+'-editCommand deleteAttr -removeEdits '+node)
		if connectAttr: mm.eval(refQueryCmd+'-editCommand connectAttr -removeEdits '+node)
		if disconnectAttr: mm.eval(refQueryCmd+'-editCommand disconnectAttr -removeEdits '+node)
		
	# Reload Reference
	if refLoaded: mc.file(loadReference=refNode)
	
	# Return Result
	#print('Removing Reference Edits Complete!')
	return

def removeParentEdits(node=''):
	'''
	'''
	# Get Reference details
	refNode = getReferenceNode(node)
	
	# Unload Reference
	refLoaded = isLoaded(refNode)
	if refLoaded: mc.file(unloadReference=refNode)
	
	# Remove Edits - referenceEdit command not working correctly using python WTF??
	mm.eval('referenceEdit -removeEdits -failedEdits true -successfulEdits true -editCommand parent '+refNode)
	
	# Reload Reference
	if refLoaded: mc.file(loadReference=refNode)

def removeSetAttrEdits(node='',refFile=''):
	'''
	'''
	# Get Reference details
	refNode = getReferenceNode(node)
	
	# Unload Reference
	refLoaded = isLoaded(refNode)
	if refLoaded: mc.file(unloadReference=refNode)
	
	# Remove Edits - referenceEdit command not working correctly using python WTF??
	mm.eval('referenceEdit -removeEdits -failedEdits true -successfulEdits true -editCommand setAttr "'+refFile+'"')
	
	# Reload Reference
	if refLoaded: mc.file(loadReference=refNode)

def removeConnectAttrEdits(nodeList=''):
	'''
	'''
	# Get Reference details
	refNode = getReferenceNode(nodeList[0])
	
	# Unload Reference
	refLoaded = isLoaded(refNode)
	if refLoaded: mc.file(unloadReference=refNode)
	
	# Remove Edits - referenceEdit command not working correctly using python WTF??
	for node in nodeList:
		mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand connectAttr -removeEdits '+node)
		mm.eval('referenceEdit -failedEdits true -successfulEdits true -editCommand disconnectAttr -removeEdits '+node)
	
	# Reload Reference
	if refLoaded: mc.file(loadReference=refNode)

def contextFromNsReferencePath(NS):
	'''
	Return the context for the reference file path of the specified namespace
	@param NS: Namespace to query reference file for
	@type NS: str
	'''
	# Get Reference From Namespace
	refNode = getReferenceFromNamespace(NS)
	if not refNode: raise Exception('No referenced nodes in "'+NS+'" namespace!')
	
	# Get Reference File Path
	refFile = getReferenceFile(refNode,withoutCopyNumber=True)
	
	# Get Context From Reference File Path
	ctx = ika.context.util.getContext(*os.path.split(refFile))
	
	# Return Result
	return ctx
