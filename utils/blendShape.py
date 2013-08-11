import maya.cmds as mc

import glTools.utils.component
import glTools.utils.deformer

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
	
	# Return result
	return targetList

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

def connectToTarget(blendShape,geometry,target,baseGeometry,weight=1.0,force=False):
	'''
	Connect a new target geometry to a specified blendShape target
	@param blendShape: Name of blendShape to connect geometry target to
	@type blendShape: str
	@param geometry: Geometry to connect to blendShape target
	@type geometry: str
	@param target: BlendShape target name to connect geometry to
	@type target: str
	@param baseGeometry: BlendShape base geometry name
	@type baseGeometry: str
	@param weight: BlendShape target weight value to connect geometry to
	@type weight: float
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check target
	if not mc.objExists(blendShape+'.'+target):
		raise Exception('Blendshape "'+blendShape+'" has no target "'+target+'"!')
	
	# Check geometry
	if not mc.objExists(geometry):
		raise Exception('Geometry object "'+geometry+'" does not exist!')
	
	# Get target index
	targetIndex = getTargetIndex(blendShape,target)
	
	# FORCE connection
	if force:
		
		# Get geometry details
		geomIndex = glTools.utils.deformer.getGeomIndex(baseGeometry,blendShape)
		geomShape = mc.listRelatives(geometry,s=True,ni=True)
		if geomShape:
			geomShape = geomShape[0]
			geomType = mc.objectType(geomShape)
		else:
			geomShape = geometry
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
		
		# Connect geometry to target input
		mc.blendShape(blendShape,e=True,t=[baseGeometry,targetIndex,geometry,weight])
	
def removeTarget(blendShape,target,baseGeometry):
	'''
	Remove the specified blendShape target
	@param blendShape: Name of blendShape to remove target from
	@type blendShape: str
	@param target: BlendShape target to remove
	@type target: str
	@param baseGeometry: BlendShape base geometry name
	@type baseGeometry: str
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Get target index
	targetIndex = getTargetIndex(blendShape,target)
	
	# Connect null duplicate
	mc.setAttr(blendShape+'.envelope',0.0)
	dup = mc.duplicate(baseGeometry)
	mc.setAttr(blendShape+'.envelope',1.0)
	connectToTarget(blendShape,dup[0],target,baseGeometry,1.0,force=True)
	
	# Remove target
	mc.blendShape(blendShape,e=True,rm=True,t=[baseGeometry,targetIndex,dup[0],1.0])
	
	# Delete duplicate geometry
	mc.delete(dup)

def addTargetInbetween(blendShape,inbetweenGeo,baseGeo,inbetweenTarget,inbetweenWeight):
	'''
	Add blendShape target inbetween shape at the specified weight value.
	@param blendShape: Name of blendShape to add inbetween target to
	@type blendShape: str
	@param inbetweenGeo: BlendShape inbetween target geometry
	@type inbetweenGeo: str
	@param baseGeo: BlendShape base geometry to add inbetween to
	@type baseGeo: str
	@param inbetweenTarget: BlendShape target to add inbetween to.
	@type inbetweenTarget: str
	@param inbetweenWeight: BlendShape target weight to add inbetween to.
	@type inbetweenWeight: float
	'''
	# Check blendShape
	if not isBlendShape(blendShape):
		raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')
	
	# Check inbetween target geometry
	if not mc.objExists(inbetweenGeo):
		raise Exception('Inbetween target geometry "'+inbetweenGeo+'" does not exist!')
	
	# Get target index
	targetIndex = getTargetIndex(blendShape,inbetweenTarget)
	
	# Add inbetween
	mc.blendShape(blendShape,e=True,ib=True,t=[baseGeo,targetIndex,inbetweenGeo,inbetweenWeight])
