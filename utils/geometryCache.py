import maya.cmds as mc
import maya.mel as mm

import os.path

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

def importCache(geo,cacheFile):
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

def importCacheList(geoList,cachePath,cacheFileList=[]):
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
		importCache(geoList[i],cacheFile)
	
def exportCache(geo,cacheFile,startFrame=1,endFrame=100,useTimeline=True,filePerFrame=False,cachePerGeo=True,forceExport=False):
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
