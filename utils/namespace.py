import maya.cmds as mc

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
	
	# Delete namespace
	mc.namespace(mv=[NS,':'],f=True)
	mc.namespace(rm=NS)
	
def getNS(obj,topOnly=True):
	'''
	Get the namespace of the specified object
	@param obj: The object to get namespace from
	@type obj: str
	'''
	# Check Object
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!')
	
	# Check namespace
	if not obj.count(':'):
		return ''
	
	# Get namespace
	if topOnly:
		ns = obj.split(':')[0]
	else:
		ns = obj.replace(':'+obj.split(':')[-1],'')
	
	# Return namespace
	return ns

def renameNS(NS,newNS):
	'''
	'''
	# Check NS
	if not mc.namespace(exists=NS):
		raise Exception('Namespace "'+NS+'" does not exist!')
	
	# Check newNS
	if not mc.namespace(exists=newNS):
		
		# Create newNS
		newNS = mc.namespace(add=newNS,f=True)
		
	# Move namespace
	mc.namespace(mv=(NS,newNS),f=True)
	
	# Delete NS
	mc.namespace(rm=NS,f=True)
	
	# Return newNS
	return newNS

def stripNS(obj):
	'''
	Return the specified object name after stripping the namespace
	@param obj: The object to strip namespace from
	@type obj: str
	'''
	return obj.split(':')[-1]

def getNSFromSel(objList):
	'''
	Get a list of namespaces from a list of scene nodes
	@param objList: The list of object to get namespaces from
	@type objList: list
	'''
	# Get namespace list form selection
	nsList = []
	if type(objList) == str:
		objList = [objList]
	for obj in objList:
		ns = getNamespace(obj)
		if not nsList.count(ns):
			nsList.append(ns)
	
	# Sort namespace list
	nsList.sort()
	
	# Return result
	return nsList

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