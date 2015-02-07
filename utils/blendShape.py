import maya.cmds as mc

import glTools.utils.component
import glTools.utils.deformer
import glTools.utils.shape

def isBlendShape(blendShape):
	'''
	Test if node is a valid blendShape deformer
	@param blendShape: Name of blendShape to query
	@type blendShape: str
	'''
	# Check blendShape exists
	if not mc.objExists(blendShape): return False
	# Check object type
	if mc.objectType(blendShape) != 'blendShape': return False
	# Return result
	return True

def create(baseGeo,targetGeo=[],origin='local',deformOrder=None,prefix=None):
	'''
	Create a blendShape deformer for the specified base geometry.
	@param baseGeo: Geometry to apply blendShape deformer to.
	@type baseGeo: str
	@param targetGeo: List of blendShape target models.
	@type targetGeo: list
	@param origin: Create a local or world space belndShape deformer. Accepted values - "local" or "world".
	@type origin: str
	@param deformOrder: Deformer order. Accepted values - "after", "before", "parallel", "split" or "foc".
	@type deformOrder: str
	@param prefix: Naming prefix
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Base Geometry
	if not mc.objExists(baseGeo):
		raise Exception('Base geometry "'+baseGeo+'" does not exist!')
	
	# Check Prefix
	if not prefix: prefix = baseGeo.split(':')[-1]
	
	# Check BlendShape
	blendShape = prefix+'_blendShape'
	if glTools.utils.blendShape.isBlendShape(blendShape):
		print('BlendShape "'+blendShape+'" already exist!')
		return blendShape
	
	# =====================
	# - Create BlendShape -
	# =====================
	
	if deformOrder == 'after':
		blendShape = mc.blendShape(baseGeo,name=blendShape,origin=origin,after=True)[0]
	elif deformOrder == 'before':
		blendShape = mc.blendShape(baseGeo,name=blendShape,origin=origin,before=True)[0]
	elif deformOrder == 'parallel':
		blendShape = mc.blendShape(baseGeo,name=blendShape,origin=origin,parallel=True)[0]
	elif deformOrder == 'split':
		blendShape = mc.blendShape(baseGeo,name=blendShape,origin=origin,split=True)[0]
	elif deformOrder == 'foc':
		blendShape = mc.blendShape(baseGeo,name=blendShape,origin=origin,foc=True)[0]
	else:
		blendShape = mc.blendShape(baseGeo,name=blendShape,origin=origin)[0]
	
	# ===============
	# - Add Targets -
	# ===============
	
	for target in targetGeo:
		addTarget(blendShape=blendShape,target=target,base=baseGeo)
	
	# =================
	# - Return Result -
	# =================
	
	return blendShape

def hasBase(blendShape,base):
	'''
	Check if the a blendShape has a specific base geometry 
	@param blendShape: BlendShape node to query
	@type blendShape: str
	@param base: Base geometry to query
	@type base: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check target
	if base in getBaseGeo(blendShape): return True
	
	# Return Result
	return False

def hasTarget(blendShape,target):
	'''
	Specify if the a named target exists on a blendShape node 
	@param blendShape: Name of blendShape to query
	@type blendShape: str
	@param target: BlendShape target to query
	@type target: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check target
	if target in getTargetList(blendShape): return True
	
	# Return Result
	return False

def hasTargetGeo(blendShape,target,base=''):
	'''
	Check if the specified blendShape target has live target geometry.  
	@param blendShape: Name of blendShape to query
	@type blendShape: str
	@param target: BlendShape target to query
	@type target: str
	@param target: The base geometry index to check for live target geometry.
	@type target: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check target
	if not target in getTargetList(blendShape):
		raise Exception('BlendShape "'+blendShape+'" has no target "'+target+'"!')
	
	# Check Target Geometry
	targetGeo = getTargetGeo(blendShape,target,baseGeo=base)
	
	# Return Result
	return bool(targetGeo)

def addTarget(blendShape,target,base='',targetIndex=-1,targetAlias='',targetWeight=0.0,topologyCheck=False):
	'''
	Add a new target to the specified blendShape
	@param blendShape: Name of blendShape to remove target from
	@type blendShape: str
	@param target: New blendShape target geometry
	@type target: str
	@param base: BlendShape base geometry. If empty, use first connected base geomtry
	@type base: str
	@param targetIndex: Specify the target index. If less than 0, use next available index. 
	@type targetIndex: str
	@param targetAlias: Override the default blendShape target alias with this string
	@type targetAlias: str
	@param targetWeight: Set the target weight value
	@type targetWeight: float
	'''
	# ==========
	# - Checks -
	# ==========
	
	# BlendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Target
	if not mc.objExists(target):
		raise Exception('Target geometry "'+target+'" does not exist!')
	
	# Base
	if base and not mc.objExists(base):
		raise Exception('Base geometry "'+base+'" does not exist!')
	
	# ==============
	# - Add Target -
	# ==============
	
	# Get Base Geometry
	if not base: base = getBaseGeo(blendShape)[0]
	# Get Target Index 
	if targetIndex < 0: targetIndex = nextAvailableTargetIndex(blendShape)
	
	# Add Target
	mc.blendShape(blendShape,e=True,t=(base,targetIndex,target,1.0),topologyCheck=topologyCheck)
	
	# Get Target Name
	targetName = getTargetName(blendShape,target)
	
	# Override Target Alias
	if targetAlias:
		targetIndex = getTargetIndex(blendShape,targetName)
		mc.aliasAttr(targetAlias,blendShape+'.weight['+str(targetIndex)+']')
		targetName = targetAlias
	
	# =====================
	# - Set Target Weight -
	# =====================
	
	if targetWeight: mc.setAttr(blendShape+'.'+targetName,targetWeight)
	
	# =================
	# - Return Result -
	# =================
	
	return (blendShape+'.'+targetName)

def addTargetInbetween(blendShape,targetGeo,targetName,base='',targetWeight='0.5'):
	'''
	Add a new target inbetween to the specified blendShape target
	@param blendShape: Name of blendShape to remove target from
	@type blendShape: str
	@param targetGeo: New blendShape target inbetween geometry
	@type targetGeo: str
	@param targetName: BlendShape target name to add inbetween target to
	@type targetName: str
	@param base: BlendShape base geometry. If empty, use first connected base geomtry
	@type base: str
	@param targetWeight: BlendShape inbetween target weight value
	@type targetWeight: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# BlendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Target
	if not mc.objExists(targetGeo):
		raise Exception('Target geometry "'+target+'" does not exist!')
	if not hasTarget(blendShape,targetName):
		raise Exception('BlendShape "'+blendShape+'" has no target "'+targetName+'"!')
	
	# Base
	if base and not mc.objExists(base):
		raise Exception('Base geometry "'+base+'" does not exist!')
	
	# ========================
	# - Add Target Inbetween -
	# ========================
	
	# Get Base Geometry
	if not base: base = getBaseGeo(blendShape)[0]
	
	# Get Target Index
	targetIndex = getTargetIndex(blendShape,targetName)
	
	# Add Target
	mc.blendShape(blendShape,e=True,t=(base,targetIndex,targetGeo,targetWeight))
	
	# =================
	# - Return Result -
	# =================
	
	return (blendShape+'.'+targetName)

def getBaseGeo(blendShape):
	'''
	Get list of blendShape base geometry.
	@param blendShape: BlendShape to get base geometry from
	@type blendShape: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# BlendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# =====================
	# - Get Base Geometry -
	# =====================
	
	baseGeo = glTools.utils.deformer.getAffectedGeometry(blendShape)
	baseGeoList = zip(baseGeo.values(),baseGeo.keys())
	baseGeoList.sort()
	baseGeoList = [i[1] for i in baseGeoList]
	
	# =================
	# - Return Result -
	# =================
	
	return baseGeoList

def getBaseIndex(blendShape,base):
	'''
	Return the blendShape input geometry index for the specified base geometry.
	@param blendShape: BlendShape to get base geometry index from
	@type blendShape: str
	@param base: Base geometry to get the input geometry index for.
	@type base: str
	'''
	# Checks
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	if not hasBase(blendShape,base):
		raise Exception('Obejct "'+base+'" is not a base geometry for blendShape "'+blendShape+'"!')
	
	# Get Base Index
	baseGeo = glTools.utils.deformer.getAffectedGeometry(blendShape)
	if not baseGeo.has_key(base):
		raise Exception('Unable to determine base index for "'+base+'" on blendShape "'+blendShape+'"!')
	baseGeo[base]
	
	# Return Result
	return baseGeo[base]

def getTargetList(blendShape):
	'''
	Return the target list for the input blendShape
	@param blendShape: Name of blendShape to get target list for
	@type blendShape: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Get attribute alias
	targetList = mc.listAttr(blendShape+'.w',m=True)
	if not targetList: targetList = []
	
	# Return result
	return targetList

def getTargetGeoList(blendShape,baseGeo=''):
	'''
	Get the list of connected target geometry to the specified blendShape
	@param blendShape: BlendShape node to get target geometry list from
	@type blendShape: str
	@param baseGeo: The base geometry of the blendshape to get the target geometry for. If empty, use base geometry at geomIndex 0.
	@type baseGeo: str
	'''
	# Get blendShape Target List
	targetList = getTargetList(blendShape)
	
	# Get Target Geo List
	targetGeoList = []
	for target in targetList:
		
		# Get Target Source Geo
		targetGeo = getTargetGeo(blendShape,target,baseGeo)
		targetGeoList.append(targetGeo)
		
	# Return Result
	return targetGeoList

def getTargetGeo(blendShape,target,baseGeo=''):
	'''
	Get the connected target geometry given a blendShape and specified target.
	@param blendShape: BlendShape node to get target geometry from
	@type blendShape: str
	@param target: BlendShape target to get source geometry from
	@type target: str
	@param baseGeo: The base geometry of the blendshape to get the target geometry for. If empty, use base geometry at geomIndex 0.
	@type baseGeo: str
	'''
	# Get Target Index
	targetIndex = getTargetIndex(blendShape,target)
	
	# Get Geometry Index
	geomIndex = 0
	if baseGeo: geomIndex = glTools.utils.deformer.getGeomIndex(baseGeo,blendShape)
	
	# Get Weight Index
	# !!! Hardcoded to check "inputTargetItem" index 6000. This could be more robust by check all existing multi indexes.
	wtIndex = 6000
	
	# Get Connected Target Geometry
	targetGeoAttr = blendShape+'.inputTarget['+str(geomIndex)+'].inputTargetGroup['+str(targetIndex)+'].inputTargetItem['+str(wtIndex)+'].inputGeomTarget'
	targetGeoConn = mc.listConnections(targetGeoAttr,s=True,d=False)
	
	# Check Target Geometry
	if not targetGeoConn: targetGeoConn = ['']
	
	# Return Result
	return targetGeoConn[0]

def getTargetName(blendShape,targetGeo):
	'''
	Get blendShape target alias for specified target geometry
	@param blendShape: BlendShape node to get target name from
	@type blendShape: str
	@param targetGeo: BlendShape target geometry to get alia name for
	@type targetGeo: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# BlendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Target
	if not mc.objExists(targetGeo):
		raise Exception('Target geometry "'+targetGeo+'" does not exist!')
	
	# ===================
	# - Get Target Name -
	# ===================
	
	# Get Target Shapes
	targetShape = glTools.utils.shape.getShapes(targetGeo,nonIntermediates=True,intermediates=False)
	if not targetShape: targetShape = mc.ls(mc.listRelatives(targetGeo,ad=True,pa=True),shapes=True,noIntermediate=True)
	if not targetShape: raise Exception('No shapes found under target geometry "'+targetGeo+'"!')
	
	# Find Target Connection
	targetConn = mc.listConnections(targetShape,sh=True,d=True,s=False,p=False,c=True)
	if not targetConn.count(blendShape):
		raise Exception('Target geometry "'+targetGeo+'" is not connected to blendShape "'+blendShape+'"!')
	targetConnInd = targetConn.index(blendShape)
	targetConnAttr = targetConn[targetConnInd-1]
	targetConnPlug = mc.listConnections(targetConnAttr,sh=True,p=True,d=True,s=False)[0]
	
	# Get Target Index
	targetInd = int(targetConnPlug.split('.')[2].split('[')[1].split(']')[0])
	# Get Target Alias
	targetAlias = mc.aliasAttr(blendShape+'.weight['+str(targetInd)+']',q=True)
	
	# =================
	# - Return Result -
	# =================
	
	return targetAlias

def getTargetIndex(blendShape,target):
	'''
	Get the target index of the specified blendShape and target name
	@param blendShape: Name of blendShape to get target index for
	@type blendShape: str
	@param target: BlendShape target to get the index for
	@type target: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check target
	if not mc.objExists(blendShape+'.'+target):
		raise Exception('Blendshape "'+blendShape+'" has no target "'+target+'"!')
	
	# Get attribute alias
	aliasList = mc.aliasAttr(blendShape,q=True)
	aliasIndex = aliasList.index(target)
	aliasAttr = aliasList[aliasIndex+1]
	
	# Get index
	targetIndex = int(aliasAttr.split('[')[-1].split(']')[0])
	
	# Return result
	return targetIndex

def nextAvailableTargetIndex(blendShape):
	'''
	Get the next available blendShape target index
	@param blendShape: Name of blendShape to get next available target index for
	@type blendShape: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Get blendShape target list
	targetList = getTargetList(blendShape)
	if not targetList: return 0
	
	# Get last index
	lastIndex = getTargetIndex(blendShape,targetList[-1])
	nextIndex = lastIndex + 1
	
	# Return result
	return nextIndex

def getTargetWeights(blendShape,target,geometry=''):
	'''
	Get per vertex target weights for the specified blendShape target
	@param blendShape: Name of blendShape to get target weights for
	@type blendShape: str
	@param target: Name of blendShape target to get weights for
	@type target: str
	@param geometry: Name of blendShape driven geometry to get weights from
	@type geometry: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check target
	if not mc.objExists(blendShape+'.'+target):
		raise Exception('blendShape "'+blendShape+'" has no "'+target+'" target attribute!')
	
	# Check geometry
	if geometry and not mc.objExists(geometry):
		raise Exception('Object "'+geometry+'" does not exist!')
	
	# Get target index
	aliasList = mc.aliasAttr(blendShape,q=True)
	aliasTarget = aliasList[(aliasList.index(target)+1)]
	targetIndex = aliasTarget.split('[')[-1]
	targetIndex = int(targetIndex.split(']')[0])
	
	# Get geometry index into blendShape
	geomIndex = 0
	if geometry: geomIndex = glTools.utils.deformer.getGeomIndex(geometry,blendShape)
	
	# Get weights
	wt = mc.getAttr(blendShape+'.it['+str(geomIndex)+'].itg['+str(targetIndex)+'].tw')[0]
	
	# Return result
	return list(wt)
	
def setTargetWeights(blendShape,target,wt,geometry=''):
	'''
	Set per vertex target weights for the specified blendShape target
	@param blendShape: Name of blendShape to set target weights for
	@type blendShape: str
	@param target: Name of blendShape target to set weights for
	@type target: str
	@param wt: Weight value list to apply to the specified blendShape target
	@type wt: list
	@param geometry: Name of blendShape driven geometry to set weights on
	@type geometry: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check target
	if not mc.objExists(blendShape+'.'+target):
		raise Exception('blendShape "'+blendShape+'" has no "'+target+'" target attribute!')
	
	# Check geometry
	if geometry and not mc.objExists(geometry):
		raise Exception('Object "'+geometry+'" does not exist!')
	
	# Get target index
	aliasList = mc.aliasAttr(blendShape,q=True)
	aliasTarget = aliasList[(aliasList.index(target)+1)]
	targetIndex = aliasTarget.split('[')[-1]
	targetIndex = int(targetIndex.split(']')[0])
	
	# Get geometry index into blendShape
	geomIndex = 0
	if geometry: geomIndex = glTools.utils.deformer.getGeomIndex(geometry,blendShape)
	# Get number of geometry components
	compCount = glTools.utils.component.getComponentCount(geometry)
	
	# Set target weights
	mc.setAttr(blendShape+'.it['+str(geomIndex)+'].itg['+str(targetIndex)+'].tw[0:'+str(compCount-1)+']',*wt)

def connectToTarget(blendShape,targetGeo,targetName,baseGeo,weight=1.0,force=False):
	'''
	Connect a new target geometry to a specified blendShape target
	@param blendShape: Name of blendShape to connect geometry target to
	@type blendShape: str
	@param targetGeo: Geometry to connect to blendShape target
	@type targetGeo: str
	@param targetName: BlendShape target name to connect geometry to
	@type targetName: str
	@param baseGeo: BlendShape base geometry name
	@type baseGeo: str
	@param weight: BlendShape target weight value to connect geometry to
	@type weight: float
	@param force: Force connection
	@type force: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check target
	if not hasTarget(blendShape,targetName):
		raise Exception('Blendshape "'+blendShape+'" has no target "'+target+'"!')
	
	# Check Target Geometry
	if not mc.objExists(targetGeo):
		raise Exception('Target geometry "'+targetGeo+'" does not exist!')
	
	# =====================
	# - Connect To Target -
	# =====================
	
	# Get target index
	targetIndex = getTargetIndex(blendShape,targetName)
	
	# FORCE connection
	if force:
		
		# Get geometry details
		geomIndex = glTools.utils.deformer.getGeomIndex(baseGeo,blendShape)
		geomShape = mc.listRelatives(targetGeo,s=True,ni=True)
		if geomShape:
			geomShape = geomShape[0]
			geomType = mc.objectType(geomShape)
		else:
			geomShape = targetGeo
			geomType = 'none'
		
		# Get geometry type output attribute.
		# Non dict values allow specific node attributes to be connected!!
		geomDict = {'mesh':'.worldMesh[0]','nurbsSurface':'.worldSpace[0]','nurbsCurve':'.worldSpace[0]'}
		if geomDict.has_key(geomType): geomAttr = geomDict[geomType]
		else: geomAttr = ''
		
		# Get weight index
		wtIndex = int(weight*6000)
		
		# Connect geometry to target input
		mc.connectAttr(geomShape+geomAttr,blendShape+'.inputTarget['+str(geomIndex)+'].inputTargetGroup['+str(targetIndex)+'].inputTargetItem['+str(wtIndex)+'].inputGeomTarget',f=True)
		
	else:
		
		# Check InBetween
		if hasTarget(blendShape,targetName) and weight != 1.0:
			# Connect geometry to target input as inbetween
			mc.blendShape(blendShape,e=True,ib=True,t=[baseGeo,targetIndex,targetGeo,weight])
		else:
			# Connect geometry to target input
			mc.blendShape(blendShape,e=True,t=[baseGeo,targetIndex,targetGeo,weight])
	
def renameTarget(blendShape,target,newName):
	'''
	Rename the specified blendShape target
	@param blendShape: Name of blendShape to rename target from
	@type blendShape: str
	@param target: BlendShape target to rename
	@type target: str
	@param newName: New name for the blendShape target
	@type newName: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check target
	if not hasTarget(blendShape,target):
		raise Exception('BlendShape "'+blendShape+'" has no target "'+target+'"!')
	
	# Rename target attribute
	mc.aliasAttr(newName,blendShape+'.'+target)
	
	# Return Result
	return newName

def removeTarget(blendShape,target,baseGeo):
	'''
	Remove the specified blendShape target
	@param blendShape: Name of blendShape to remove target from
	@type blendShape: str
	@param target: BlendShape target to remove
	@type target: str
	@param baseGeo: BlendShape base geometry name
	@type baseGeo: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check target
	if not hasTarget(blendShape,target):
		raise Exception('BlendShape "'+blendShape+'" has no target "'+target+'"!')
	
	# Get target index
	targetIndex = getTargetIndex(blendShape,target)
	
	# Connect null duplicate
	targetGeo = getTargetGeo(blendShape,target,baseGeo)
	if not targetGeo:
		mc.setAttr(blendShape+'.envelope',0.0)
		targetGeo = mc.duplicate(baseGeo)[0]
		mc.setAttr(blendShape+'.envelope',1.0)
		connectToTarget(blendShape,targetGeo,target,baseGeo,1.0,force=True)
	
	# Remove target
	mc.blendShape(blendShape,e=True,rm=True,t=[baseGeo,targetIndex,targetGeo,1.0])

def removeUnconnectedTargets(blendShape,base):
	'''
	Remove unconnected blendShape targets
	@param blendShape: The blendShape deformer to operate on
	@type blendShape: str
	@param base: The base geometry connected to the blendShape
	@type base: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape deformer!!')
	
	# Get blendShape target list
	targetList = getTargetList(blendShape)
	
	# Check blendShape target connections
	deletedTargetList = []
	for target in targetList:
		targetConn = mc.listConnections(blendShape+'.'+target,s=True,d=False)
		
		# If no incoming connnections, delete target
		if not targetConn:
			try:
				removeTarget(blendShape,target,base)
			except:
				print('Unable to delete blendShape target "'+target+'"!')
			else:
				print('Target "'+target+'" deleted!')
				deletedTargetList.append(target)
	
	# Return result
	return deletedTargetList
