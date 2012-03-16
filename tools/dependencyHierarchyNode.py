import maya.cmds as mc

class UserInputError( Exception ): pass

class DependencyHierarchyNode( object ):
	'''
	This maya python object is used to represent a hierarchy node that can be used to replicate a maya DAG hierarchy.
	A DependencyHierarchyNode has data members that store information about child and parent relationships. It also
	contains methods for constructing and traversing hierarchies of nodes.
	This class was originally designed to assist in the calculation of a reliable evaluation order for a complex hierarchy
	of rig controls.
	'''

	def __init__(self):
		
		self.fullName = ''
		self.shortName = ''
		self.parent = None
		self.childList = []
		self.childCache = {}
		
	def buildHierarchyFromNode(self,root):
		'''
		This will map an entire hierarchy from a given root node.
		@param root: The root transform from which the hierarchy will be mapped
		@type root: str
		'''
		# Check root exists
		if not mc.objExists(root): raise UserInputError('Root object '+root+' does not exists!')
		
		# Get root information
		self.fullName = mc.ls(root,l=True)[0]
		self.shortName = self.fullName.split('|')[1]
		self.parent = None
		self.childList = []
		self.childCache = {}
		
		# Traverse all decendant children
		self.mapDecendants(recursive=True)
	
	def mapDecendants(self,recursive=True):
		'''
		Finds maya DAG children for the current object and records hierarchy information to class member array types
		@param recursive: Traverse the entire downstream decendant hierarchy
		@type recursive: bool
		'''
		# Get dag children
		children = mc.listRelatives(self.fullName,c=True,pa=True,type=['transform','joint','ikHandle'])
		
		# Escape if no children
		if not children: return
		
		# Build child array
		for child in children:
			childNode = DependencyHierarchyNode()
			childNode.fullName = str(mc.ls(child,l=True)[0])
			childNode.shortName = childNode.fullName.split('|')[-1]
			childNode.parent = self
			self.childList.append(childNode)
			self.childCache[childNode.fullName] = childNode
		# Recurse through decendant hierarchy
		if recursive:
			for childNode in self.childList:
				childNode.mapDecendants(recursive=True)
		
	def getDependPath(self,delineator='|'):
		'''
		Return the dependency based path for the current node
		@param delineator: String that will be used to separate nodes in the return path string
		@type delineator: str
		'''
		path = self.shortName
		parent = self.parent
		while parent:
			path = parent.shortName+delineator+path
			parent = parent.parent
		return path
	
	def getGeneration(self):
		'''
		Return the dependency depth (generation) for the current node
		'''
		generation = 0
		parent = self.parent
		while parent:
			generation += 1
			parent = parent.parent
		return generation
	
	def findDependNode(self,fullName):
		'''
		Find and return the node representing the specified maya object.
		@param fullName: Find the node representing this object
		@type fullName: str
		'''
		# Check node exists
		if not mc.objExists(fullName): raise UserInputError('Object '+fullName+' does not exists!')
		fullName = mc.ls(fullName,l=True)[0]
		
		# Search for node in hierarchy
		dependNode = None
		if self.fullName == fullName: return self
		if self.childCache.has_key(fullName): return self.childCache[fullName]
		for child in self.childList:
			if child.childCache.has_key(fullName): return child.childCache[fullName]
		for child in self.childList:
			dependNode = child.findDependNode(fullName)
			if dependNode: break
		return dependNode
	
	def reparent(self,newParentNode):
		'''
		Reparent the current object node under another object node
		@param newParentNode: The object to which the current object node will be parented
		@type newParentNode: DependencyHierarchyNode
		'''
		# Check nodes exist
		if not mc.objExists(self.fullName): raise UserInputError('Child object '+child+' does not exists!')
		if not mc.objExists(newParentNode.fullName): raise UserInputError('Parent object '+newParentNode.shortName+' does not exists!')
		
		# Get current parent node
		currentParentNode = self.parent
		
		# Check parent is not the current node
		if self.fullName == newParentNode.fullName: return
		# Check current node is not already a child of parent
		if currentParentNode.fullName == newParentNode.fullName: return
		# Check parent is not a decendant of child
		if self.findDependNode(newParentNode.fullName): raise UserInputError('Object "'+newParentNode.shortName+'" is a decendant of "'+self.shortName+'"!! Unable to perform reparent!')
		
		# Break old child/parent connections
		currentParentNode.childCache.pop(self.fullName)
		currentParentNode.childList.remove(self)
		
		# Make new child/parent connections
		self.parent = newParentNode
		newParentNode.childList.append(self)
		newParentNode.childCache[self.fullName] = self
		
	def flatList(self,longNames=False):
		'''
		Return a dependency node name list from the current hierarchy
		@param longNames: Return a list of long object names
		@type longNames: bool
		'''
		flatList = []
		if longNames:	flatList.append(self.fullName)
		else:		flatList.append(self.shortName)
		flatList.extend(self.listChildren(longNames=longNames,recursive=True))
		return flatList
	
	def flatListNodes(self):
		'''
		Return a dependency node list from the current hierarchy
		'''
		nodeList = []
		nodeList.append(self)
		nodeList.extend(self.listChildNodes(recursive=True))
		return nodeList
	
	def listChildren(self,longNames=False,recursive=False):
		'''
		Return a flat list of child dependency nodes
		@param longNames: Return a list of long object names
		@type longNames: bool
		@param recursive: Traverse the entire downstream decendant hierarchy
		@type recursive: bool
		'''
		childList = []
		for child in self.childList:
			if longNames:	childList.append(child.fullName)
			else:		childList.append(child.shortName)
		for child in self.childList:
			if recursive: childList.extend(child.listChildren(longNames=longNames,recursive=True))
		return childList
	
	def listChildNodes(self,longNames=False,recursive=False):
		'''
		Return a flat list of child dependency nodes
		@param recursive: Traverse the entire downstream decendant hierarchy
		@type recursive: bool
		'''
		childList = []
		for child in self.childList: childList.append(child)
		for child in self.childList:
			if recursive: childList.extend(child.listChildNodes(recursive=True))
		return childList
	
	def generationDict(self):
		'''
		Create a generation based dictionary of all nodes in the dependency hierarchy.
		'''
		generationDict = {}
		for node in self.flatListNodes():
			gen = node.getGeneration()
			if not generationDict.has_key(gen): generationDict[gen] = []
			generationDict[gen].append(node.shortName)
		return generationDict
	
	def generationList(self):
		'''
		Create a list of all dependency hierarchy nodes in order of generation.
		'''
		generationList = []
		generationDict = self.generationDict()
		generationDictKeys = generationDict.keys()
		generationDictKeys.sort()
		for key in generationDictKeys: generationList.extend(generationDict[key])
		return generationList
		
