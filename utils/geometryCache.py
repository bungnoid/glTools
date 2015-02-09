import maya.cmds as mc
import maya.mel as mm

import os.path

import glTools.utils.namespace

def loadAbcImportPlugin():
	'''
	Load AbcImport plugin
	'''
	# Load AbcImport plugin
	if not mc.pluginInfo('AbcImport',q=True,l=True):
		try:
			mc.loadPlugin('AbcImport', quiet=True)
		except:
			raise Exception('Error loading AbcImport plugin!')

def loadAbcExportPlugin():
	'''
	Load AbcExport plugin
	'''
	# Load AbcExport plugin
	if not mc.pluginInfo('AbcExport',q=True,l=True):
		try:
			mc.loadPlugin('AbcExport', quiet=True)
		except:
			raise Exception('Error loading AbcExport plugin!')

def loadGpuCachePlugin():
	'''
	Load gpuCache plugin
	'''
	# Load gpuCache plugin
	if not mc.pluginInfo('gpuCache',q=True,l=True):
		try:
			mc.loadPlugin('gpuCache', quiet=True)
		except:
			raise Exception('Error loading gpuCache plugin!')

def loadIkaGpuCachePlugin():
	'''
	Load glGpuCache plugin
	'''
	# Load glGpuCache plugin
	if not mc.pluginInfo('glGpuCache',q=True,l=True):
		try:
			mc.loadPlugin('glGpuCache', quiet=True)
		except:
			raise Exception('Error loading glGpuCache plugin!')

def isAlembicNode(cacheNode):
	'''
	Check if the specified node is a valid Alembic cache node
	@param cacheNode: Object to query
	@type cacheNode: str
	'''
	# Check object exists
	if not mc.objExists(cacheNode): return False
	
	# Check node type
	if mc.objectType(cacheNode) != 'AlembicNode': return False
	
	# Return result
	return True

def isGpuCacheNode(gpuCacheNode):
	'''
	Check if the specified node is a valid GPU cache node
	@param gpuCacheNode: Object to query
	@type gpuCacheNode: str
	'''
	# Check object exists
	if not mc.objExists(gpuCacheNode): return False
	
	# Check node type
	if mc.objectType(gpuCacheNode) != 'gpuCache': return False
	
	# Return result
	return True

def isIkaGpuCacheNode(glGpuCacheNode):
	'''
	Check if the specified node is a valid gl GPU cache node
	@param glGpuCacheNode: Object to query
	@type glGpuCacheNode: str
	'''
	# Check object exists
	if not mc.objExists(glGpuCacheNode): return False
	
	# Check node type
	if mc.objectType(glGpuCacheNode) != 'glGpuCache': return False
	
	# Return result
	return True

def disconnectTime(cache):
	'''
	Disconnect the time attribute for the given cache node
	@param cache: Cache node to disconnect time from
	@type cache: str
	'''
	# Get existing connections
	timeConn = mc.listConnections(cache+'.time',s=True,d=False,p=True)
	if not timeConn: return
	
	# Disconnect time plug
	mc.disconnectAttr(timeConn[0],cache+'.time')

def connectTime(cache,timeAttr='time1.outTime'):
	'''
	Connect a specified driver attribute to the time inout for a named cache node
	@param cache: Cache node to connect to
	@type cache: str
	@param timeAttr: Attribute to drive the cache nodes time value
	@type timeAttr: str
	'''
	# Check time attribute
	if not mc.objExists(timeAttr):
		raise Exception('Time attribute "'+timeAttr+'" does not exist!')
	
	# Disconnect time plug
	mc.connectAttr(timeAttr,cache+'.time',f=True)

def importMCCache(geo,cacheFile):
	'''
	Import and connect geometry cache file to the specified geometry
	@param geo: Geometry to load cache to
	@type geo: str
	@param cacheFile: Geometry cache file path to load
	@type cacheFile: str
	'''
	# Check geo
	if not mc.objExists(geo): raise Exception('Geometry "" does not exist!')
	
	# Check file
	if not os.path.isfile(cacheFile): raise Exception('Cache file "'+cacheFile+'" does not exist!')
	
	# Load cache
	mm.eval('doImportCacheFile "'+cacheFile+'" "" {"'+geo+'"} {}')

def importMCCacheList(geoList,cachePath,cacheFileList=[]):
	'''
	Import and connect geometry cache files from a specified path to the input geometry list
	@param geoList: List of geometry to load cache onto
	@type geoList: list
	@param cachePath: Directory path to load cache files from
	@type cachePath: str
	@param cacheFileList: List of cacheFiles to load. If empty, use geometry shape names. Optional.
	@type cacheFileList: list
	'''
	# Check source directory path
	if not os.path.isdir(cachePath):
		raise Exception('Cache path "'+cachePath+'" does not exist!')
	if not cachePath.endswith('/'): cachePath = cachePath+'/'
	
	# Check cacheFile list
	if cacheFileList and not (len(cacheFileList) == len(geoList)):
		raise Exception('Cache file and geometry list mis-match!')
	
	# For each geometry in list
	for i in range(len(geoList)):
		
		# Check geo
		if not mc.objExists(geoList[i]):
			raise Exception('Geometry "'+geoList[i]+'" does not exist!')
		
		# Determine cache file
		if cacheFileList:
			cacheFile = cacheFile = cachePath+cacheFileList[i]+'.mc'
		else:
			# Get geometry shape
			shapeList = mc.listRelatives(geoList[i],s=True,ni=True,pa=True)
			if not shapeList: raise Exception('No valid shape found for geometry!')
			geoShape = shapeList[0]
			cacheFile = cachePath+geoShape+'.mc'
		
		# Check file
		if not os.path.isfile(cacheFile):
			raise Exception('Cache file "'+cacheFile+'" does not exist!')
		
		# Import cache
		importMCCache(geoList[i],cacheFile)
	
def exportMCCache(geo,cacheFile,startFrame=1,endFrame=100,useTimeline=True,filePerFrame=False,cachePerGeo=True,forceExport=False):
	'''
	@param geo: List of geometry to cache
	@type geo: list
	@param cacheFile: Output file name
	@type cacheFile: str
	@param startFrame: Start frame for cache output
	@type startFrame: int
	@param endFrame: End frame for cache output
	@type endFrame: int
	@param useTimeline: Get start and end from from the timeline
	@type useTimeline: bool
	@param filePerFrame: Write file per frame or single file 
	@type filePerFrame: bool
	@param cachePerGeo: Write file per shape or single file 
	@type cachePerGeo: bool
	@param forceExport: Force export even if it overwrites existing files 
	@type forceExport: bool
	'''
	# Constant value args
	version = 5					# 2010
	refresh = 1					# Refresh during caching
	usePrefix = 0				# Name as prefix
	cacheAction = 'export'		# Cache action "add", "replace", "merge", "mergeDelete" or "export"
	simRate = 1					# Sim frame rate (steps per frame - ?)
	
	# Frame range
	if useTimeline:
		startFrame = mc.playbackOptions(q=True,ast=True)
		endFrame = mc.playbackOptions(q=True,aet=True)
	
	# Cache file distribution
	if filePerFrame:
		cacheDist = 'OneFilePerFrame'
	else:
		cacheDist = 'OneFile'
	
	# Determine destination directory and file
	fileName = cacheFile.split('/')[-1]
	cacheDir = cacheFile.replace(fileName,'')
	baseName = fileName.replace('.'+fileName.split('.')[-1],'')
	
	# Export cache
	mc.select(geo)
	mm.eval('doCreateGeometryCache '+str(version)+' {"0","'+str(startFrame)+'","'+str(endFrame)+'","'+cacheDist+'","'+str(refresh)+'","'+cacheDir+'","'+str(int(cachePerGeo))+'","'+baseName+'","'+str(usePrefix)+'","'+cacheAction+'","'+str(int(forceExport))+'","1","1","0","0","mcc" };')
	
def importGpuCache(cachePath,cacheName='',namespace=''):
	'''
	Import GPU Alembic cache from file
	@param cachePath: Alembic cache file path
	@type cachePath: str
	@param cacheName: Alembic cache name. If empty, use filename.
	@type cacheName: str
	'''
	# =========
	# - Check -
	# =========
	
	# Load Import Plugin
	loadAbcImportPlugin()
	
	# Check Cache Path
	if not os.path.isfile(cachePath):
		raise Exception('Cache path "'+cachePath+'" is not a valid file!')
	
	# Check Cache Name
	if not cacheName:
		cacheBase = os.path.basename(cachePath)
		cacheName = os.path.splitext(cacheBase)[-1]
	
	# Check Namespace
	if namespace:
		if mc.namespace(ex=namespace):
			NSind = 1
			while(mc.namespace(ex=namespace+str(NSind))):
				NSind += 1
			namespace = namespace+str(NSind)
	
	# ==============
	# - Load Cache -
	# ==============
	
	# Create Cache Node
	cacheNode = mc.createNode('gpuCache',name=cacheName+'Cache')
	cacheParent = mc.listRelatives(cacheNode,p=True,pa=True)
	cacheParent = mc.rename(cacheParent,cacheName)
	
	# Set Cache Path
	mc.setAttr(cacheNode+'.cacheFileName',cachePath,type='string')
	
	# ===================
	# - Apply Namespace -
	# ===================
	
	if namespace:
		
		# Create Namespace (if necessary)
		if not mc.namespace(ex=namespace): mc.namespace(add=namespace)
		# Apply Namespace
		cacheParent = mc.rename(cacheParent,namespace+':'+cacheParent)
		# Update cacheNode
		cacheNode = mc.listRelatives(cacheParent,s=True,pa=True)[0]
	
	# =================
	# - Return Result -
	# =================
	
	return cacheParent

def importAbcCache(cachePath='',cacheName='',namespace='',parent='',mode='import',debug=False):
	'''
	Import Alembic cache from file
	@param cachePath: Alembic cache file path
	@type cachePath: str
	@param cacheName: Alembic cache name. If empty, use filename.
	@type cacheName: str
	@param namespace: Namespace for cache.
	@type namespace: str
	@param parent: Reparent the whole hierarchy under an existing node in the current scene.
	@type parent: str
	@param mode: Import mode. "import", "open" or "replace".
	@type mode: str
	@param debug: Turn on debug message printout.
	@type debug: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Load Import Plugin
	loadAbcImportPlugin()
	
	# Check Cache Path
	if not os.path.isfile(cachePath):
		raise Exception('Cache path "'+cachePath+'" is not a valid file!')
	
	# Check Cache Name
	if not cacheName:
		cacheBase = os.path.basename(cachePath)
		cacheName = os.path.splitext(cacheBase)[-1]
	
	# Check Namespace
	if namespace:
		if mc.namespace(ex=namespace):
			NSind = 1
			while(mc.namespace(ex=namespace+str(NSind))):
				NSind += 1
			namespace = namespace+str(NSind)
	
	# ==============
	# - Load Cache -
	# ==============
	
	cacheNode = mc.AbcImport(cachePath,mode=mode,debug=debug)
	cacheNode = mc.rename(cacheNode,cacheName+'Cache')
	
	# Get Cache Nodes
	cacheList = mc.listConnections(cacheNode,s=False,d=True)
	
	# Get Cache Roots
	rootList = []
	for cacheItem in cacheList:
		root = cacheItem
		while mc.listRelatives(root,p=True) != None:
			root = mc.listRelatives(root,p=True,pa=True)[0]
		if not rootList.count(root):
				rootList.append(root)
	
	
	# Add to Namespace
	if namespace:
		for root in rootList:
			glTools.utils.namespace.addHierarchyToNS(root,namespace)
	
	# Parent
	if parent:
		
		# Check Parent Transform
		if not mc.objExists(parent):
			parent = mc.group(em=True,n=parent)
		
		# Parent
		mc.parent(rootList,parent)
	
	# =================
	# - Return Result -
	# =================
	
	return cacheNode



def loadAbcFromGpuCache(gpuCacheNode,debug=False):
	'''
	Load Alembic cache from a specified gpuCache node.
	@param gpuCacheNode: GPU cache node to replace with alembic cache.
	@type gpuCacheNode: str
	@param debug: Print debug info to script editor
	@type debug: bool
	'''
	# =========
	# - Check -
	# =========
	
	# Load Import Plugin
	loadAbcImportPlugin()
	
	# Check GPU  Cache Node
	if not isGpuCacheNode(gpuCacheNode):
		raise Exception('Object "'+gpuCacheNode+'" is not a valid GPU Cache Node!')
	
	# =====================
	# - Get Cache Details -
	# =====================
	
	cachePath = mc.getAttr(gpuCacheNode+'.cacheFileName')
	
	# Get Cache Node Transform and Parent
	cacheXform = mc.listRelatives(gpuCacheNode,p=True,pa=True)[0]
	cacheParent = mc.listRelatives(cacheXform,p=True,pa=True)
	if not cacheParent: cacheParent = ''
	
	# Get Cache Namespace
	cacheNS = glTools.utils.namespace.getNS(gpuCacheNode)
	
	# Get Cache Name
	cacheName = gpuCacheNode
	if gpuCacheNode.count('Cache'):
		cacheName = gpuCacheNode.replace('Cache','')
	
	# Delete GPU Cache
	mc.delete(cacheXform)
	
	# ======================
	# - Load Alembic Cache -
	# ======================
	
	cacheNode = importAbcCache(cachePath,cacheName=cacheName,namespace=cacheNS,parent=cacheParent,mode='import',debug=debug)
	#cacheXform = mc.listRelatives(cacheNode,p=True,pa=True)[0]
	
	# Parent Cache
	#
	if cacheParent: mc.parent(cacheXform,cacheParent)
	
	# =================
	# - Return Result -
	# =================
	
	return cacheNode

def abcTimeOffset(offsetNode,offsetAttr='alembicTimeOffset',cacheList=[]):
	'''
	Setup a time offset attribute to control the incoming time value for the specified cache nodes.
	@param offsetNode: Node that will hold the time offset attribute
	@type offsetNode: str
	@param offsetAttr: Time offset attribute name.
	@type offsetAttr: str
	@param cacheList: List of cache nodes to connect to time offset.
	@type cacheList: list
	'''
	# =========
	# - Check -
	# =========
	
	# Check Cache List
	if not cacheList: return ''
	
	# Check offsetNode
	if not mc.objExists(offsetNode):
		raise Exception('Offset node "'+offsetNode+'" does not exist!')
	
	# Check offsetAttr
	if not offsetAttr: offsetAttr = 'alembicTimeOffset'
	
	# ========================
	# - Add Offset Attribute -
	# ========================
	
	if not mc.objExists(offsetNode+'.'+offsetAttr):
		mc.addAttr(offsetNode,ln=offsetAttr,at='long',dv=0,k=True)
	
	# =======================
	# - Connect Time Offset -
	# =======================
	
	for cache in cacheList:
		
		# Get Current Time Connection
		timeConn = mc.listConnections(cache+'.time',s=True,d=False,p=True)
		if not timeConn: timeConn = ['time1.outTime']
		
		# Offset Node
		addNode = mc.createNode('addDoubleLinear',n=cache+'_abcOffset_addDoubleLinear')
		
		# Connect to Offset Time
		mc.connectAttr(timeConn[0],addNode+'.input1',f=True)
		mc.connectAttr(offsetNode+'.'+offsetAttr,addNode+'.input2',f=True)
		mc.connectAttr(addNode+'.output',cache+'.time',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return offsetNode+'.'+offsetAttr
