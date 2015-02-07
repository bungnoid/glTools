import maya.cmds as mc

def isLayer(obj):
	'''
	Check if the specified object is a valid layer type
	@param obj: Object to check as layer
	@type obj: bool
	'''
	if not mc.objExists(obj): return False
	if mc.objectType(obj) == 'displayLayer': return True
	if mc.objectType(obj) == 'renderLayer': return True
	if mc.objectType(obj) == 'animLayer': return True
	return False

def isDisplayLayer(obj):
	'''
	Check if the specified object is a valid display layer
	@param obj: Object to check as display layer
	@type obj: bool
	'''
	if not mc.objExists(obj): return False
	if mc.objectType(obj) == 'displayLayer': return True
	else: return False

def isRenderLayer(obj):
	'''
	Check if the specified object is a valid render layer
	@param obj: Object to check as display layer
	@type obj: bool
	'''
	if not mc.objExists(obj): return False
	if mc.objectType(obj) == 'renderLayer': return True
	else: return False

def isAnimLayer(obj):
	'''
	Check if the specified object is a valid animation layer
	@param obj: Object to check as display layer
	@type obj: bool
	'''
	if not mc.objExists(obj): return False
	if mc.objectType(obj) == 'animLayer': return True
	else: return False

def memberList(layer,objectList=True):
	'''
	Return a list of objects assigned to the specified layer
	@param obj: The layer to return an object list for
	@type obj: bool
	'''
	# Check Layer
	if not isLayer(layer):
		raise Excpetion('Object "'+layer+'" is not a valid layer type!')
	
	# Get Member List
	members = []
	if isDisplayLayer(layer):
		members = mc.listConnections(layer+'.drawInfo',s=False,d=True,sh=True)
	if isRenderLayer(layer):
		members = mc.listConnections(layer+'.renderInfo',s=False,d=True,sh=True)
	if isAnimLayer(layer):
		members = mc.listConnections(layer+'.dagSetMembers',s=True,d=False,sh=True)
	
	# Get List of Objects from Member List
	if objectList: members = mc.ls(members,o=True)
	
	# Format Result
	if not members: members = []
	members = list(set(members))
	
	# Return Result
	return members
