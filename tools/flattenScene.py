import maya.cmds as mc

import glTools.tools.fixNonReferenceInputShape

import glTools.utils.namespace
import glTools.utils.reference
import glTools.utils.shape

import os.path

def flatten(verbose=True):
	'''
	Flatten scene file.
	- Import references
	- Delete namespaces
	- Delete construction history for specified DAG nodes (selection set based)
	- Reparent specified DAG nodes (selection set based)
	- Delete specified nodes (selection set based)
	- Rename shape nodes
	- Rename specified nodes (selection set based)
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# Print Header
	if verbose:
		print('=================')
		print('- Flatten Scene -')
		print('=================')
	
	# Encode Reference File Path to Nodes
	encodeReferenceFilePath(verbose)
	
	# Fix NonReference Inputs
	fixNonReferenceInputs(verbose)
	
	# Import References
	importAllReferences(verbose)
	
	# Delete Namespaces
	deleteAllNS(verbose)
	
	# Delete History
	deleteHistory(verbose)
	
	# Delete Nodes
	deleteNodes(verbose)
	
	# Reparent Nodes
	reparentOnFlatten(verbose)
	
	# Renames Nodes
	renameShapes(verbose)
	renameOnFlatten(verbose)
	
	# Cleanup - Delete and Lock FlattenScene Attributes
	cleanup(verbose)
	
	# Print Header
	if verbose:
		print('===========================')
		print('- Flatten Scene Complete! -')
		print('===========================')

def cleanup(verbose=True):
	'''
	Flatten scene cleanup. Delete unused attributes and lock info attributes
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# =====================
	# - Delete Attributes -
	# =====================
	
	# For Each Attribute
	attrList = [	'encodeReferenceFilePath',
					'renameOnFlatten',
					'reparentOnFlatten',
					'deleteHistoryOnFlatten',
					'fixNonReferenceInputsRoot'	]
	
	for attr in attrList:
		
		# For Each Node
		attrNodes = mc.ls('*.'+attr,o=True,r=True)
		for node in attrNodes:
			
			# Print Msg
			if verbose: print ('Deleting Attribute "'+node+'.'+attr+'"')
			
			# Delete Attribute
			mc.setAttr(node+'.'+attr,l=False)
			mc.deleteAttr(node+'.'+attr)
	
	# ===================
	# - Lock Attributes -
	# ===================
	
	# For Each Attribute
	attrList = ['referenceFilePath']
	for attr in attrList:
		
		# For Each Node
		attrNodes = mc.ls('*.'+attr,o=True,r=True)
		for node in attrNodes:
			
			# Print Msg
			if verbose: print ('Locking Attribute "'+node+'.'+attr+'"')
			
			# Lock Attribute
			mc.setAttr(node+'.'+attr,l=True)
	
	# =================
	# - Return Result -
	# =================
	
	return

def importAllReferences(verbose=True):
	'''
	Import all objects from references
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# List all reference nodes
	refList = glTools.utils.reference.listReferences()
	
	# Import objects from reference
	for refNode in refList:
		glTools.utils.reference.importReference(refNode,verbose)
		
def deleteAllNS(verbose=True):
	'''
	Delete all scene namespaces
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# Get scene namespace list
	nsList = glTools.utils.namespace.getAllNS(excludeList=['UI','shared'])
	
	# For each namespace
	for ns in nsList:
	
		# Delete namespace
		glTools.utils.namespace.deleteNS(ns)
		
		# Print message
		if verbose: print('Removed namespace "'+ns+'" from scene!')

def renameShapes(verbose=True):
	'''
	Rename previously referenced shape nodes.
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# List all scene transforms
	xformList = mc.ls(type='transform')
	
	# Iterate over transforms
	for xform in xformList:
		
		# Get Xform Short Name
		xformSN = xform.split('|')[-1]
		
		# List all shapes
		allShapeList = mc.listRelatives(xform,s=True,pa=True)
		if not allShapeList: continue
		
		# List all non-intermediate shape children
		shapeList = mc.listRelatives(xform,s=True,ni=True,pa=True)
		if not shapeList: continue
		
		# List all intermediate shapes
		if len(allShapeList) == len(shapeList): continue
		intShapeList = list(set(allShapeList)-set(shapeList))
		
		# Check shape naming
		for shape in shapeList:
			
			# Get Shape Short Name
			shapeSN = shape.split('|')[-1]
			
			# Check for ShapeDeformed naming
			if shapeSN.endswith('Deformed'):
				
				# Find input shape
				try: inputShape = glTools.utils.shape.findInputShape(shape)
				except: inputShape = glTools.utils.shape.findInputShape2(shape)
				
				# Get InputShape Short Name
				inputShapeSN = inputShape.split('|')[-1]
				
				# Check Input Shape
				if inputShapeSN != shapeSN:
					# Rename input shape
					if verbose: print('Renaming: '+inputShapeSN+' -> '+xformSN+'IntermediateShape')
					inputShape = mc.rename(inputShape,xformSN+'IntermediateShape')
				
				# Rename current shape
				if verbose: print('Renaming: '+shapeSN+' -> '+xformSN+'Shape')
				shape = mc.rename(shape,xformSN+'Shape')
				mc.reorder(shape,f=True)

def deleteNodes(verbose=True):
	'''
	Delete all nodes in set "nodesToDelete"
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Set Exists
	if not mc.objExists('nodesToDelete'): return []
	
	# Check Nodes
	nodesToDelete = mc.sets('nodesToDelete',q=True)
	for node in nodesToDelete:
		if not mc.objExists(node):
			raise Exception('Object "" does not exist! Unable to delete')
	
	# ================
	# - Delete Nodes -
	# ================
	
	deletedNodes = []
	for node in nodesToDelete:
		
		try:
			# Delete Node
			mc.delete(node)
		except:
			# Unable to Delete Node
			if verbose:
				print('Unable to delete object "'+node+'"! Skipping')
		else:
			# Node Deleted
			if verbose:
				print ('Object "'+node+'" successfully delete!')
			# Append Return List
			deletedNodes.append(node)
	
	# =================
	# - Return Result -
	# =================
	
	return deletedNodes

def renameOnFlatten(verbose=True):
	'''
	Rename nodes during flattenScene
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	nodeList = mc.ls('*.renameOnFlatten',o=True)
	if not nodeList: return []
	
	# ================
	# - Rename Nodes -
	# ================
	
	renameList = []
	for node in nodeList:
		
		# Get Rename String
		renameStr = mc.getAttr(node+'.renameOnFlatten')
		# Check Empty String
		if not renameStr: continue
		if mc.objExists(renameStr):
			raise Exception('RenameOnFlatten: Object "'+node+'" cant be renamed to "'+renameStr+'"! Object of that name already exists...')
		
		# Rename Node
		renamed = mc.rename(node,renameStr)
		
		# Print Msg
		if verbose: print ('Renaming "'+node+'" -> "'+renamed+'"')
		
		# Append Result
		renameList.append(renamed)
	
	# =================
	# - Return Result -
	# =================
	
	return renameList

def reparentOnFlatten(verbose):
	'''
	Reparent nodes during flattenScene
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	nodeList = mc.ls('*.reparentOnFlatten',o=True)
	if not nodeList: return []
	
	# ==================
	# - Reparent Nodes -
	# ==================
	
	reparentList = []
	for node in nodeList:
		
		# Get Parent
		parentConn = mc.listConnections(node+'.reparentOnFlatten',s=True,d=False)
		if not parentConn: continue
		parent = parentConn[0]
		
		# Check Parent
		if not mc.objExists(parent):
			raise Exception('Target parent node "'+parent+'" does not exist!')
		
		# Reparent Node
		reparented = mc.parent(node,parent)[0]
		
		# Print Msg
		if verbose:
			print ('Reparenting "'+node+'" -> "'+parent+'"')
		
		# Append Result
		reparentList.append(reparented)
	
	# =================
	# - Return Result -
	# =================
	
	return reparentList

def deleteHistory(verbose):
	'''
	Delete construction history during flattenScene
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	nodeList = mc.ls('*.deleteHistoryOnFlatten',o=True,dag=True)
	if not nodeList: return []
	
	# ==================
	# - Delete History -
	# ==================
	
	for node in nodeList:
		
		# Print Msg
		if verbose: print ('Deleting Construction History for "'+node+'"')
		
		# Delete History
		try: mc.delete(node,ch=True)
		except: print('Problem deleting construction history on node "'+node+'" during flattenScene!')
		
	# =================
	# - Return Result -
	# =================
	
	return nodeList

def fixNonReferenceInputs(verbose=False):
	'''
	Fix nonReference input shapes for all geometry under the specified root nodes.
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# Get Root Nodes
	rootNodes = mc.ls('*.fixNonReferenceInputsRoot',o=True,r=True) or []
	
	# For Each Root Node
	for root in rootNodes:
		
		# Check Non Reference Inputs
		if glTools.tools.fixNonReferenceInputShape.checkNonReferenceInputShapes(root,verbose=verbose):
			
			# Check Non Reference Inputs
			glTools.tools.fixNonReferenceInputShape.fixNonReferenceInputShapes(root,verbose=verbose)
	
	# Return Result
	return rootNodes

def encodeReferenceFilePath(verbose=True):
	'''
	Encode the source reference file path to tagged scene nodes.
	@param verbose: Print progress messages
	@type verbose: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Get Node to Encode File Path To 
	nodeList = mc.ls('*.encodeReferenceFilePath',o=True,r=True)
	if not nodeList: return []
	
	# ==============================
	# - Encode Reference File Path -
	# ==============================
	
	attr = 'ABC_referenceFilePath'
	for node in nodeList:
		
		# Add File Path Attribute
		if not mc.objExists(node+'.'+attr):
			mc.addAttr(node,ln=attr,dt='string')
		
		# Get Reference File Path
		refFile = glTools.utils.reference.getReferenceFile(node,withoutCopyNumber=True)
		realPath = os.path.realpath(refFile)
		
		# Print Msg
		if verbose: print ('Encoding Reference File Path to node "'+node+'": ('+realPath+')')
		
		# Set Reference File Path String
		mc.setAttr(node+'.'+attr,realPath,type='string')
	
	# =================
	# - Return Result -
	# =================
	
	return nodeList

def createNodesToDeleteSet(nodes=[]):
	'''
	Create nodesToDelete set.
	@param nodes: List of nodes to add to set
	@type nodes: list
	'''
	# Create Set
	nodesToDeleteSet = 'nodesToDelete'
	if not mc.objExists(nodesToDeleteSet):
		mc.sets(n=nodesToDeleteSet,empty=True)
	
	# Add Items to Set
	if nodes: mc.sets(nodes,fe=nodesToDeleteSet)
	
	# Return Result
	return nodesToDeleteSet

def addReferencePathAttr(node):
	'''
	Add encodeReferenceFilePath attribute to the specified node.
	Tags the specified referenced node to have the source reference file path encoded to the node on flatten scene.
	@param node: Node to add encodeReferenceFilePath attribute to.
	@type node: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Node
	if not mc.objExists(node):
		raise Exception('Object "'+node+'" does not exist!')
	
	# Check Reference
	if not glTools.utils.reference.isReferenced(node):
		raise Exception('Object "'+node+'" is not a referenced node!')
	
	# Check Attribute
	attr = 'encodeReferenceFilePath'
	if mc.objExists(node+'.'+attr):
		print('Attribute "'+node+'.'+attr+'" already exists!')
		return node+'.'+attr
	
	# ================================
	# - Add Reference Path Attribute -
	# ================================
	
	# Add Attribute
	mc.addAttr(node,ln=attr,at='bool')
	# Set Rename Value
	mc.setAttr(node+'.'+attr,1)
	
	# =================
	# - Return Result -
	# =================
	
	print('"'+attr+'" attribute added to node "'+node+'".')
	
	return node+'.'+attr

def addRenameAttr(node,rename=''):
	'''
	Add renameOnFlatten attribute to the specified node.
	@param node: Node to add rename attribute to.
	@type node: str
	@param rename: Initialize rename attribute with the given string value
	@type rename: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(node):
		raise Exception('Object "'+node+'" does not exist!')
	
	if mc.objExists(node+'.renameOnFlatten'):
		print('RenameOnFlatten attribute "'+node+'.renameOnFlatten" already exist!')
		return node+'.renameOnFlatten'
	
	# ========================
	# - Add Rename Attribute -
	# ========================
	
	# Add Attribute
	attr = 'renameOnFlatten'
	mc.addAttr(node,ln=attr,dt='string')
	
	# Set Rename Value
	if rename: mc.setAttr(node+'.'+attr,rename,type='string')
	
	# =================
	# - Return Result -
	# =================
	
	print('"'+attr+'" attribute added to node "'+node+'".')
	
	return node+'.'+attr

def addReparentAttr(node,parent=''):
	'''
	Add reparentOnFlatten (message) attribute to the specified node.
	@param node: Node to add reparent attribute to.
	@type node: str
	@param rename: Connect an existing node (message attr) to the reparent attribute. 
	@type rename: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(node):
		raise Exception('Object "'+node+'" does not exist!')
	
	if parent and not mc.objExists(parent):
		raise Exception('Parent target "'+node+'" does not exist!')
	
	# ========================
	# - Add Rename Attribute -
	# ========================
	
	# Add Attribute
	attr = 'reparentOnFlatten'
	if not mc.attributeQuery(attr,n=node,ex=True):
		mc.addAttr(node,ln=attr,at='message')
	
	# Connect Reparent Node
	if parent:
		try: mc.connectAttr(parent+'.message',node+'.'+attr,f=True)
		except: pass
	
	# =================
	# - Return Result -
	# =================
	
	print('"'+attr+'" attribute added to node "'+node+'".')
	return node+'.'+attr

def addDeleteHistoryAttr(node):
	'''
	Add deleteHistoryOnFlatten attribute to the specified node.
	Tags the specified node to have its construction history deleted on flatten scene.
	@param node: Node to add deleteHistoryOnFlatten attribute to.
	@type node: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Node
	if not mc.objExists(node):
		raise Exception('Object "'+node+'" does not exist!')
	
	# Check Attribute
	attr = 'deleteHistoryOnFlatten'
	if mc.objExists(node+'.'+attr):
		print('Attribute "'+node+'.'+attr+'" already exists!')
		return node+'.'+attr
	
	# ================================
	# - Add Reference Path Attribute -
	# ================================
	
	# Add Attribute
	mc.addAttr(node,ln=attr,at='bool')
	# Set Rename Value
	mc.setAttr(node+'.'+attr,1)
	
	# =================
	# - Return Result -
	# =================
	
	print('"'+attr+'" attribute added to node "'+node+'".')
	
	return node+'.'+attr

def addFixNonReferenceInputAttr(node):
	'''
	Add fixNonReferenceInputsRoot attribute to the specified node.
	Tags the specified node to be checked/fixed for nonReference inputs on flatten scene.
	@param node: Node to add fixNonReferenceInputsRoot attribute to.
	@type node: str
	'''
	# Check Node
	if not mc.objExists(node):
		raise Exception('Object "'+node+'" does not exist!')
	
	# Check Attribute
	attr = 'fixNonReferenceInputsRoot'
	if mc.objExists(node+'.'+attr):
		print('Attribute "'+node+'.'+attr+'" already exists!')
		return node+'.'+attr
	
	# ================================
	# - Add Reference Path Attribute -
	# ================================
	
	# Add Attribute
	mc.addAttr(node,ln=attr,at='bool')
	# Set Rename Value
	mc.setAttr(node+'.'+attr,1)
	
	# =================
	# - Return Result -
	# =================
	
	print('"'+attr+'" attribute added to node "'+node+'".')
	
	return node+'.'+attr

def addReparentAttrFromSel():
	'''
	Add reparentOnFlatten (message) attribute and connection based on the current selection.
	'''
	# Get Selection
	sel = mc.ls(sl=True,transforms=True)
	
	# Check Selection
	if len(sel) < 2:
		raise Exception('Invalid selection for addReparentAttrFromSel()! Select the child and parent object and run again.')
	
	# Add Reparent Attr
	for obj in sel[:-1]:
		addReparentAttr(node=obj,parent=sel[-1])
	

