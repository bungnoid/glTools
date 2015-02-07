import maya.cmds as mc

def isContainer(node):
	'''
	Check if node is a valid container node.
	@param containerNode: Node to check as container.
	@type containerNode: str
	'''
	# Check Node Exists
	if not mc.objExists(node): return False
	# Check Node Inheritance
	if not 'containerBase' in mc.nodeType(node,i=True): return False
	# Check Exact Node Type
	# if not mc.objectType(containerNode) == 'dagContainer' and not mc.objectType(containerNode) == 'container': return False
	# Return Result
	return True

def create(name,nodes=None,dagContainer=True):
	'''
	Create container.
	@param name: Container name
	@type name: str
	@param nodes: List of nodes to add to container
	@type nodes: list or None
	@param dagContainer: Create a DAG container or DG container
	@type dagContainer: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Asset Node
	if mc.objExists(name):
		raise Exception('Object "'+name+'" already exist! Unable to create container...')
	
	# Nodes
	if nodes:
		for node in nodes:
			if not mc.objExists(node):
				raise Exception('Object "'+node+'" does not exist! Unable to add to container...')
	
	# ==========================
	# - Create Asset Container -
	# ==========================
	
	# Create Node
	if not dagContainer: containerNode = mc.container(n=name)
	else: containerNode = mc.container(n=name,typ='dagContainer')
	
	# Add Nodes
	if nodes: mc.container(containerNode,e=True,addNode=nodes,f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return containerNode

def nodeList(containerNode):
	'''
	Get contained node list from the specified container node.
	@param containerNode: Asset container node to get node list from.
	@type containerNode: str
	'''
	# Check Asset Node
	if not isContainer(containerNode):
		raise Exception('Object "'+containerNode+'" is not a valid container node!')
	
	# Get Asset Container Nodes
	nodeList = mc.container(containerNode,q=True,nodeList=True)
	if not nodeList: nodeList = []
	else: nodeList = [str(i) for i in nodeList]
	
	# Return Result
	return nodeList

def containerFromNode(node):
	'''
	Determine the encompassing container from a specified node
	@param node: Contained node to get container from.
	@type node: str
	'''
	# Get Asset Node
	containerNode = mc.container(q=True,findContainer=node)
	# Check Container Node
	if not containerNode: containerNode = ''
	# Return Result
	return containerNode

def publishAttr(attr,assetAttrName=None,bind=True):
	'''
	Publish specified attribute to asset node.
	@param attr: Contained node attribute to publish to asset. Attribute should be in "node.attr" format.
	@type attr: str
	@param assetAttrName: Bound asset attribute name. If None, is generated from node and attribute name (node_attr)
	@type assetAttrName: str or None
	@param bind: Bind published asset attribute to specified attribute.
	@type bind: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Attribute
	if not mc.objExists(attr):
		raise Exception('Attribute "'+attr+'" does not exist! Unable to publish attribute to asset...')
	
	# Asset Attribute Name
	if not assetAttrName: assetAttrName = attr.replace('.','_')
	
	# ======================
	# - Get Node and Asset -
	# ======================
	
	node = mc.ls(attr,o=True)
	containerNode = assetFromNode(node)
	
	# =====================
	# - Publish Attribute -
	# =====================
	
	# Publish Attribute (Unbound)
	mc.container(containerNode,e=True,publishName=assetAttrName)
	
	# Bid to Attribute
	if bind: mc.container(containerNode,e=True,bindAttr=[attr,assetAttrName])
	
	# =================
	# - Return Result -
	# =================
	
	return containerNode+'.'+assetAttrName
