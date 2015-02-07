import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.utils.component
import glTools.utils.deformer
import glTools.utils.joint
import glTools.utils.mesh
import glTools.utils.selection
import glTools.utils.stringUtils
import glTools.utils.mathUtils

class UserInterupted(Exception): pass

def isSkinCluster(skinCluster):
	'''
	Test if the input node is a valid skinCluster
	@param blendShape: Name of blendShape to query
	@type blendShape: str
	'''
	# Check object exists
	if not mc.objExists(skinCluster):
		print('SkinCluster "'+skinCluster+'" does not exists!')
		return False
	# Check object is a valid skinCluster
	if mc.objectType(skinCluster) != 'skinCluster':
		print('Object "'+skinCluster+'" is not a vaild skinCluster node!')
		return False
	
	# Retrun result
	return True

def findRelatedSkinCluster(geometry):
	'''
	Return the skinCluster attached to the specified geometry
	@param geometry: Geometry object/transform to query
	@type geometry: str
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise Exception('Object '+geometry+' does not exist!')
	# Check transform
	if mc.objectType(geometry) == 'transform':
		try: geometry = mc.listRelatives(geometry,s=True,ni=True,pa=True)[0]
		except: raise Exception('Object '+geometry+' has no deformable geometry!')
	
	# Determine skinCluster
	skin = mm.eval('findRelatedSkinCluster "'+geometry+'"')
	if not skin: 
		skin = mc.ls(mc.listHistory(geometry),type='skinCluster')
		if skin: skin = skin[0]
	if not skin: skin = ''
	
	# Return result
	return skin

def getSkinClusterFn(skinCluster):
	'''
	Return an MFnSkinCluster function class object for the speficied skinCluster
	@param skinCluster: SkinCluster to attach to function class
	@type skinCluster: str
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "' + skinCluster + '" specified!')
	
	# Get skinCluster node
	skinClusterSel = OpenMaya.MSelectionList()
	skinClusterObj = OpenMaya.MObject()
	OpenMaya.MGlobal.getSelectionListByName(skinCluster,skinClusterSel)
	skinClusterSel.getDependNode(0,skinClusterObj)
	
	# Initialize skinCluster function class
	skinClusterFn = OpenMayaAnim.MFnSkinCluster(skinClusterObj)
	
	# Return function class
	return skinClusterFn

def getInfluenceIndex(skinCluster,influence):
	'''
	Return the input index of an influence for a specified skinCluster
	@param skinCluster: SkinCluster to query influence index from
	@type skinCluster: str
	@param influence: Influence to query index of
	@type influence: str
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "'+skinCluster+'" specified!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence object "'+influence+'" does not exist!')
	
	# Get skinCluster node
	skinClusterFn = getSkinClusterFn(skinCluster)
	
	# Get influence object
	influencePath = glTools.utils.base.getMDagPath(influence)
	
	# Get influence index
	return skinClusterFn.indexForInfluenceObject(influencePath)

def getInfluenceAtIndex(skinCluster,influenceIndex):
	'''
	Return the skinClsuter influence at the specified index.
	@param skinCluster: SkinCluster to query influence from
	@type skinCluster: str
	@param influenceIndex: Influence index to query
	@type influenceIndex: int
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "'+skinCluster+'" specified!')
	
	# Get Influence at Index
	infConn = mc.listConnections(skinCluster+'.matrix['+str(influenceIndex)+']',s=True,d=False)
	
	# Check Connection
	if not infConn: raise Exception('No influence at specified index!')
	
	# Return Result
	return infConn[0]

def getInfluencePhysicalIndex(skinCluster,influence):
	'''
	Return the physical (non-sparce) index of an influence for a specified skinCluster
	@param skinCluster: SkinCluster to query influence index from
	@type skinCluster: str
	@param influence: Influence to query index of
	@type influence: str
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "'+skinCluster+'" specified!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence object "'+influence+'" does not exist!')
	
	# Get skinCluster node
	skinClusterFn = getSkinClusterFn(skinCluster)
	
	# Get influence path list
	infPathArray = OpenMaya.MDagPathArray()
	skinClusterFn.influenceObjects(infPathArray)
	infNameArray = [infPathArray[i].partialPathName() for i in range(infPathArray.length())]
	
	# Check influence
	if not influence in infNameArray:
		raise Exception('Unable to determine influence index for "'+influence+'"!')
	infIndex = infNameArray.index(influence)
	
	# Retrun result
	return infIndex

def getInfluenceWeights(skinCluster,influence,componentList=[]):
	'''
	Return the weights of an influence for a specified skinCluster
	@param skinCluster: SkinCluster to query influence weights from
	@type skinCluster: str
	@param influence: Influence to query weights from
	@type influence: str
	@param componentList: List of components to query weights for
	@type componentList: list
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "' + skinCluster + '" specified!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence object "'+influence+'" does not exists!')
	
	# Get geometry
	affectedGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]
	
	# Check component list
	if not componentList:
		componentList = glTools.utils.component.getComponentStrList(affectedGeo)
	componentSel = glTools.utils.selection.getSelectionElement(componentList,0)
	
	# Get skinCluster Fn
	skinFn = getSkinClusterFn(skinCluster)
	
	# Get Influence Index
	influenceIndex = getInfluencePhysicalIndex(skinCluster,influence)
	
	# Get weight values
	weightList = OpenMaya.MDoubleArray()
	skinFn.getWeights(componentSel[0],componentSel[1],influenceIndex,weightList)
	
	# Return weight array
	return list(weightList)

def getInfluenceWeightsAll(skinCluster,componentList=[]):
	'''
	Return the weights of all influence for a specified skinCluster
	@param skinCluster: SkinCluster to query influence weights from
	@type skinCluster: str
	@param componentList: List of components to query weights for
	@type componentList: list
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "' + skinCluster + '" specified!')

	# Get Geometry
	affectedGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]
	
	# Check component list
	if not componentList: componentList = glTools.utils.component.getComponentStrList(affectedGeo)
	componentSel = glTools.utils.selection.getSelectionElement(componentList,0)

	# Get skinClusterFn
	skinFn = getSkinClusterFn(skinCluster)

	# Get weight values
	weightList = OpenMaya.MDoubleArray()
	infCountUtil = OpenMaya.MScriptUtil(0)
	infCountPtr = infCountUtil.asUintPtr()
	skinFn.getWeights(componentSel[0],componentSel[1],weightList,infCountPtr)
	infCount = OpenMaya.MScriptUtil(infCountPtr).asUint()
	
	# Break List Per Influence
	wtList = list(weightList)
	infWtList = [wtList[i::infCount] for i in xrange(infCount)]
	
	# Return Result
	return infWtList

def getInfluenceWeightsSlow(skinCluster,influence,componentList=[]):
	'''
	Return the weights of an influence for a specified skinCluster
	@param skinCluster: SkinCluster to query influence weights from
	@type skinCluster: str
	@param influence: Influence to query weights from
	@type influence: str
	@param componentList: List of components to query weights for
	@type componentList: list
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "' + skinCluster + '" specified!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence object "'+influence+'" does not exists!')
	
	# Get geometry
	affectedGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]
	
	# Check component list
	if not componentList: componentList = glTools.utils.component.getComponentStrList(affectedGeo)
	componentIndexList = glTools.utils.component.getComponentIndexList(componentList)
	componentIndexList = componentIndexList[componentIndexList.keys()[0]]
	
	# Get weight values
	weightList = [mc.skinPercent(skinCluster,affectedGeo+'.vtx['+str(i)+']',transform=influence,q=True) for i in componentIndexList]
	
	# Return weight array
	return weightList

def setInfluenceWeights(skinCluster,influence,weightList,normalize=True,componentList=[]):
	'''
	Set the weights of an influence for a specified skinCluster using an input weight list
	@param skinCluster: SkinCluster to set influence weights for
	@type skinCluster: str
	@param influence: Influence to set weights for
	@type influence: str
	@param weightList: Influence weight list to apply.
	@type weightList: list
	@param normalize: Normalize weights as they are applied
	@type normalize: bool
	@param componentList: List of components to set weights for
	@type componentList: list
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "' + skinCluster + '" specified!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence object "'+influence+'" does not exists!')
	
	# Get geometry
	affectedGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]
	
	# Get skinCluster Fn
	skinFn = getSkinClusterFn(skinCluster)
	
	# Get Influence Index
	influenceIndex = getInfluencePhysicalIndex(skinCluster,influence)
	
	# Check component list
	if not componentList:
		componentList = glTools.utils.component.getComponentStrList(affectedGeo)
	componentSel = glTools.utils.selection.getSelectionElement(componentList,0)
	
	# Encode argument arrays
	infIndexArray = OpenMaya.MIntArray()
	infIndexArray.append(influenceIndex)
	
	wtArray = OpenMaya.MDoubleArray()
	oldWtArray = OpenMaya.MDoubleArray()
	[wtArray.append(i) for i in weightList]
	
	# Set skinCluster weight values
	skinFn.setWeights(componentSel[0],componentSel[1],infIndexArray,wtArray,normalize,oldWtArray)
	
	# Return result
	return list(oldWtArray)

def setInfluenceWeightsSlow(skinCluster,influence,weightList,normalize=True,componentList=[]):
	'''
	Set the weights of an influence for a specified skinCluster using an input weight list. Uses slower skinPercent cmd.
	@param skinCluster: SkinCluster to set influence weights for
	@type skinCluster: str
	@param influence: Influence to set weights for
	@type influence: str
	@param weightList: Influence weight list to apply.
	@type weightList: list
	@param normalize: Normalize weights as they are applied
	@type normalize: bool
	@param componentList: List of components to set weights for
	@type componentList: list
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "' + skinCluster + '" specified!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence object "'+influence+'" does not exists!')
	if not mc.skinCluster(skinCluster,q=True,inf=True).count(influence):
		raise Exception('Influence "'+influence+'" not connected to skinCluster "'+skinCluster+'"!')
	
	# Get geometry
	affectedGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]
	
	# Check component list
	if not componentList: componentList = glTools.utils.component.getComponentStrList(affectedGeo)
	componentIndexList = glTools.utils.component.getComponentIndexList(componentList)
	componentIndexList = componentIndexList[componentIndexList.keys()[0]]
	
	# Check component and weight list lengths
	if len(componentIndexList) != len(weightList):
		raise Exception('List length mis-match!')
	
	# Set weight values
	for i in range(len(componentIndexList)):
		comp = glTools.utils.component.getComponentStrList(affectedGeo,[componentIndexList[i]])[0]
		mc.skinPercent(skinCluster,comp,tv=(influence,weightList[i]),normalize=normalize)

def setInfluenceWeightsAll(skinCluster,weightList,normalize=True,componentList=[]):
	'''
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "' + skinCluster + '" specified!')
	
	# Get SkinCluster Influence List
	influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
	infIndexArray = OpenMaya.MIntArray()
	[infIndexArray.append(getInfluencePhysicalIndex(skinCluster,inf)) for inf in influenceList]
	infDict = {}
	for inf in influenceList: infDict[inf] = getInfluencePhysicalIndex(skinCluster,inf)
	
	# Get SkinCluster Geometry
	skinGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]
	if not mc.objExists(skinGeo):
		raise Exception('SkinCluster geometry "'+skinGeo+'" does not exist!')
	
	# Check Component List
	if not componentList: componentList = glTools.utils.component.getComponentStrList(skinGeo)
	componentSel = glTools.utils.selection.getSelectionElement(componentList,0)
	
	# Get Component Index List
	indexList =  OpenMaya.MIntArray()
	componentFn = OpenMaya.MFnSingleIndexedComponent(componentSel[1])
	componentFn.getElements(indexList)
	componentIndexList = list(indexList)
	
	# Check SkinCluster Weights List
	if len(weightList) != len(influenceList):
		raise Exception('Influence and weight list miss-match!')
	
	# Build Master Weight Array
	wtArray = OpenMaya.MDoubleArray()
	oldWtArray = OpenMaya.MDoubleArray()
	for c in componentIndexList:
		for inf in influenceList:
			wtArray.append(weightList[infDict[inf]][c])
	
	# Get skinCluster function set
	skinFn = glTools.utils.skinCluster.getSkinClusterFn(skinCluster)
	
	# Set skinCluster weights
	skinFn.setWeights(componentSel[0],componentSel[1],infIndexArray,wtArray,False,oldWtArray)

def lockInfluenceWeights(influence,lock=True,lockAttr=False):
	'''
	Set the specified influence weight lock state.
	@param influence: SkinCluster influence to lock weights for
	@type influence: str
	@param lock: The lock state to apply to the skinCluster influences
	@type lock: bool
	@param lockAttr: Lock the "lockInfluenceWeights" attribute
	@type lockAttr: bool
	'''
	# Check SkinCluster
	if not mc.objExists(influence):
		raise Exception('Influence "'+influence+'" does not exist!')
	
	# Check Lock Influence Weights Attr
	if not mc.attributeQuery('liw',n=influence,ex=True):
		raise Exception('Influence ("'+influence+'") does not contain attribute "lockInfluenceWeights" ("liw")!')
		
	# Set Lock Influence Weights Attr
	try:
		mc.setAttr(influence+'.liw',l=False)
		mc.setAttr(influence+'.liw',lock)
		if lockAttr: mc.setAttr(influence+'.liw',l=True)
	except: pass
	
	# Return Result
	return lock

def lockSkinClusterWeights(skinCluster,lock=True,lockAttr=False):
	'''
	Set the influence weight lock state for all influences of the specified skinCluster.
	@param skinCluster: SkinCluster to lock influence weights for
	@type skinCluster: str
	@param lock: The lock state to apply to the skinCluster influences
	@type lock: bool
	@param lockAttr: Lock the "lockInfluenceWeights" attribute
	@type lockAttr: bool
	'''
	# Check SkinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Object "'+skinCluster+'" is not a valid skinCluster node!')
	
	# Get Influence List
	influenceList = mc.skinCluster(skinCluster,q=True,inf=True) or []
	
	# For Each Influence
	for influence in influenceList:
		
		# Set Lock Influence Weights Attr
		lockInfluenceWeights(influence,lock=lock,lockAttr=lockAttr)
	
	# Return Result
	return influenceList

def lockSkinClusterWeightsFromGeo(geo,lock=True,lockAttr=False):
	'''
	Set the influence weight lock state for all influences of the skinCluster connected to the specified geometry.
	@param geo: Geometry to get skinCluster from
	@type geo: str
	@param lock: The lock state to apply to the skinCluster influences
	@type lock: bool
	@param lockAttr: Lock the "lockInfluenceWeights" attribute
	@type lockAttr: bool
	'''
	# Check SkinCluster
	if not mc.objExists(geo):
		raise Exception('Geometry "'+geo+'" does not exist!')
	
	# Get skinCluster
	skinCluster = findRelatedSkinCluster(geo)
	if not skinCluster: return []
	
	# Lock Weights
	influenceList = lockSkinClusterWeights(skinCluster,lock=lock,lockAttr=lockAttr)
	
	# Return Result
	return influenceList
	
def getAffectedPoints(skinCluster,influence):
	'''
	Get a list of points affected by a specific influence of a named skinCluster.
	@param skinCluster: SkinCluster to get affected point for
	@type skinCluster: str
	@param influence: Influence to get affected point for
	@type influence: str
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Object "'+skinCluster+'" is not a valid skinCluster!!')
	
	# Get skinCluster function set
	skinClusterFn = getSkinClusterFn(skinCluster)
	
	# Get influence DAG path
	influencePath = glTools.utils.base.getMDagPath(influence)
	
	# Get affected points
	pointSel = OpenMaya.MSelectionList()
	weightList = OpenMaya.MDoubleArray()
	skinClusterFn.getPointsAffectedByInfluence(influencePath,pointSel,weightList)
	
	# Return result
	pointList = []
	pointSel.getSelectionStrings(pointList)
	return pointList 

def rename(geometry,suffix='skinCluster'):
	'''
	Rename skinCluster based on affected geometry name
	@param geometry: The geometry affected by the skinCluster to rename
	@type geometry: str
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise Exception('Geometry "'+geometry+'" does not exist!')
	
	# Get name prefix
	prefix = geometry.split(':')[-1] # glTools.utils.stringUtils.stripSuffix(geometry)
	
	# Get connected skinCluster
	try:
		skinCluster = findRelatedSkinCluster(geometry)
	except:
		print ('Object "'+geometry+'" is not connected to a valid skinCluster!!')
		skinCluster = ''
	
	# Check skinCluster
	if not skinCluster: return ''
	
	# Rename skinCluster
	skinCluster = mc.rename(skinCluster,prefix+'_'+suffix)
	return skinCluster

def reset(geometry):
	'''
	Reset the skin cluster attached to the specified object
	@param geometry: Object whose attached skinCluster will be reset
	@type geometry: str
	'''
	# Delete bind pose nodes
	deleteBindPose()
	
	# Determine skinCluster
	skinCluster = findRelatedSkinCluster(geometry)
	
	# Detach skinCluster
	mc.skinCluster(geometry,e=True,ubk=True)
	
	# Get influence list
	influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
	
	# Get MaxInfluence settings
	maxInfluences = mc.getAttr(skinCluster+'.maxInfluences')
	useMaxInfluences = mc.getAttr(skinCluster+'.maintainMaxInfluences')
	
	# Rebuild skinCluster
	skinCluster = mc.skinCluster(geometry,influenceList,dr=4,mi=maxInfluences,omi=useMaxInfluences,tsb=True)
	
	# Delete bind pose nodes
	deleteBindPose()
	
	# Return skinCluster
	return skinCluster

def clearWeights(geometry):
	'''
	Reset the skinCluster weight values (set to 0.0) for the specified objects/components
	@param geometry: Geometry whose skinCluster weights will have its weights reset to 0.0
	@type geometry: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Geometry
	if not mc.objExists(geometry):
		raise Exception('Geometry object "'+geometry+'" does not exist!')
	
	# Get SkinCluster
	skinCluster = findRelatedSkinCluster(geometry)
	if not mc.objExists(skinCluster):
		raise Exception('Geometry object "'+geometry+'" is not attached to a valid skinCluster!')
	
	# =================
	# - Clear Weights -
	# =================
	
	# Get geometry component list
	componentList = glTools.utils.component.getComponentStrList(geometry)
	componentSel = glTools.utils.selection.getSelectionElement(componentList,0)
	
	# Build influence index array
	infList = mc.skinCluster(skinCluster,q=True,inf=True)
	infIndexArray = OpenMaya.MIntArray()
	for inf in infList:
		infIndex = getInfluencePhysicalIndex(skinCluster,inf)
		infIndexArray.append(infIndex)
	
	# Build master weight array
	wtArray = OpenMaya.MDoubleArray()
	oldWtArray = OpenMaya.MDoubleArray()
	[wtArray.append(0.0) for i in range(len(componentList)*len(infList))]
	
	# Set skinCluster weights
	skinFn = glTools.utils.skinCluster.getSkinClusterFn(skinCluster)
	skinFn.setWeights(componentSel[0],componentSel[1],infIndexArray,wtArray,False,oldWtArray)

def deleteBindPose():
	'''
	Delete all bind pose nodes (dagPose) in scene
	'''
	# Delete bind pose nodes
	dagPoseNodes = mc.ls(typ='dagPose')
	if dagPoseNodes: mc.delete(dagPoseNodes)

def mirrorSkinWIP(	srcGeo,
				dstGeo,
				axis		= 'x',
				infMethod	= 'closest',
				search		= 'lf_',
				replace		= 'rt_',
				jointList	= None ):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Source Geometry and SkinCluster
	if not mc.objExists(srcGeo):
		raise Exception('Source geometry "'+srcGeo+'" does not exist!')
	srcSkin = findRelatedSkinCluster(srcGeo)
	if not srcSkin:
		raise Exception('No skinCluster found for source geometry "'+srcGeo+'"!')
	
	# Check Destination Geometry and SkinCluster
	if not mc.objExists(dstGeo):
		raise Exception('Destination geometry "'+dstGeo+'" does not exist!')
	dstSkin = findRelatedSkinCluster(dstGeo)
	if not dstSkin: dstSkin = dstGeo.split(':')[-1]+'_skinCluster'
	
	# Get Source Influence List
	srcInfluenceList = mc.skinCluster(srcSkin,q=True,inf=True)
	
	# Check Joint List
	if not jointList: jointList = mc.ls(type='joint')
	
	# ====================================
	# - Build Destination Influence List -
	# ====================================
	
	# Get Destination Influence List
	dstInfluenceList = []
	if mc.objExists(dstSkin):
		dstInfluenceList = mc.skinCluster(dstSkin,q=True,inf=True)
	
	
	

def mirrorSkin(skinCluster,search='lf_',replace='rt_',destGeo=''):
	'''
	Create a mirrored skinCluster based on the influence list and weights of another specified skinCluster
	@param skinCluster: The existing skinCluster to mirror
	@type skinCluster: str
	@param search: Name prefix of the source skinCluster
	@type search: str
	@param replace: Name prefix of the destination skinCluster geometry/influences
	@type replace: str
	@param destGeo: Destination geometry to create new skinCluster for
	@type destGeo: str
	'''
	# Check skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Object "'+skinCluster+'" is not a valid skinCluster!')
	
	# Check Source Geometry
	sourceGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]
	
	# Get Destination Geometry
	if not destGeo:
		destGeo = sourceGeo.replace(search,replace)
	if not mc.objExists(destGeo):
		raise Exception('Destination geometry "'+destGeo+'" does not exist!')
	
	# Get influence list
	influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
	
	# Check destination skinCluster
	mSkinCluster = skinCluster.replace(search,replace)
	destSkinCluster = findRelatedSkinCluster(destGeo)
	if destSkinCluster and destSkinCluster != mSkinCluster:
		mc.rename(destSkinCluster,mSkinCluster)
	
	# Check influenceList
	mInfluenceList = [inf.replace(search,replace) for inf in influenceList]
	for mInf in mInfluenceList:
		if not mc.objExists(mInf):
			raise Exception('Mirror influence "'+mInf+'" does not exist!!')
	
	# Check mirror skinCluster
	if not mc.objExists(mSkinCluster):
		# Create skinCluster
		mSkinCluster = mc.skinCluster(mInfluenceList,destGeo,tsb=True,n=mSkinCluster)[0]
	else:
		# Add influence
		destInfluenceList = mc.skinCluster(mSkinCluster,q=True,inf=True)
		for mInf in mInfluenceList:
			if not destInfluenceList.count(mInf):
				mc.skinCluster(mSkinCluster,e=True,ai=mInf)
	
	# Get Mirror Weights
	mirroWeightList = {}
	for inf in influenceList:
		mirroWeightList[inf] = getInfluenceWeights(skinCluster,inf)
	
	# Clear mirrorSkin weights
	clearWeights(destGeo)
	
	# Apply mirror weights
	for i in range(len(influenceList)):
		setInfluenceWeights(mSkinCluster,mInfluenceList[i],mirroWeightList[influenceList[i]])
		
def createMirrorInfluenceList(influenceList, searchJointList=None, flipAxis	= [-1,1,1]):
	
	# Check Joint List
	if not searchJointList: searchJointList = mc.ls(type='joint')
	
	mInfluenceList = [i for i in influenceList]
	for i in range(len(influenceList)):
		
		# Get Joint Mirror Position
		inf = influenceList[i]
		pos = mc.xform(inf,q=True,ws=True,rp=True)
		mirrorPos = [pos[x]*flipAxis[x] for x in range(len(pos))]
		
		closestJoint = inf
		smallestDist = 1000
		for jnt in searchJointList:
			
			# Check Mirror Joint
			testPos = mc.xform(jnt,q=True,ws=True,rp=True)
			dist = glTools.utils.mathUtils.distanceBetween(point1=mirrorPos,point2=testPos)
			
			# Test Distance
			if dist < smallestDist:
				closestJoint = jnt
				smallestDist = dist
		
		# Append Mirror Influence List
		mInfluenceList[i] = closestJoint
	
	# Check influenceList
	for mInf in mInfluenceList:
		if not mc.objExists(mInf):
			print ('Warning :: Mirror influence "'+mInf+'" does not exist!!')
			mInfluenceList.remove(mInf)
			
	return mInfluenceList

def mirrorSkinToNewGeom(	srcSkin,
							dstGeo,
							jointList	= None,
							flipAxis	= [-1,1,1] ):
	'''
	Mirrors skinCluster in world space across two pieces of geometry
	To Do: modularize and remove duplicate code
	@param srcSkin: The existing skinCluster to mirror
	@type srcSkin: str
	@param dstGeo: The destination geometry to mirror to.
	@type dstGeo: str
	@param jointList: List of joints to mirror. If None, use all influences from source skinCluster
	@type jointList: str or None
	@param flipAxis: Axis to mirror across.
	@type flipAxis: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check skinCluster
	if not isSkinCluster(srcSkin):
		raise Exception('Object "'+srcSkin+'" is not a valid skinCluster!')
	
	# Get Destination Geometry
	if not mc.objExists(dstGeo):
		raise Exception('Destination geometry "'+dstGeo+'" does not exist!')
	
	# Get Destination SkinCluster
	dstSkin = findRelatedSkinCluster(dstGeo)
	if not dstSkin: dstSkin = dstGeo+'_skinCluster'
	
	# Get Influence List
	influenceList = mc.skinCluster(srcSkin,q=True,inf=True)
	
	# Check Joint List
	if not jointList: jointList = mc.ls(type='joint')
	
	# =============================
	# - Get Mirror Influence List -
	# =============================
	
	mInfluenceList = [i for i in influenceList]
	for i in range(len(influenceList)):
		
		# Get Joint Mirror Position
		inf = influenceList[i]
		pos = mc.xform(inf,q=True,ws=True,rp=True)
		mirrorPos = [pos[x]*flipAxis[x] for x in range(len(pos))]
		
		closestJoint = inf
		smallestDist = 1000
		for jnt in jointList:
			
			# Check Mirror Joint
			testPos = mc.xform(jnt,q=True,ws=True,rp=True)
			dist = glTools.utils.mathUtils.distanceBetween(point1=mirrorPos,point2=testPos)
			
			# Test Distance
			if dist < smallestDist:
				closestJoint = jnt
				smallestDist = dist
		
		# Append Mirror Influence List
		mInfluenceList[i] = closestJoint
	
	# Check influenceList
	for mInf in mInfluenceList:
		if not mc.objExists(mInf):
			print ('Warning :: Mirror influence "'+mInf+'" does not exist!!')
			mInfluenceList.remove(mInf)
	
	# ============================
	# - Build Mirror SkinCluster -
	# ============================
	
	if not mc.objExists(dstSkin):
		# Create SkinCluster
		dstSkin = mc.skinCluster(mInfluenceList,dstGeo,tsb=True,n=dstSkin)[0]
	else:
		# Add Influence
		dstInfluenceList = mc.skinCluster(dstSkin,q=True,inf=True)
		for mInf in mInfluenceList:
			if not mInf in dstInfluenceList:
				try: mc.skinCluster(dstSkin,e=True,ai=mInf)
				except: print "Warning :: Could not add %s to %s" % (mInf, dstSkin)
	
	# Clear Weights
	mc.setAttr(dstSkin+'.normalizeWeights',0)
	clearWeights(dstGeo)
	
	
	# Mirror Weights
	for i in range(len(influenceList)):
		print(influenceList[i]+' : '+mInfluenceList[i])
		wt = getInfluenceWeights(srcSkin,influenceList[i])
		setInfluenceWeights(dstSkin,mInfluenceList[i],wt)
	
	mc.setAttr(dstSkin+'.normalizeWeights',1)
	
def bindPreMatrix(skinCluster,influence,influenceBase=None,parent=True):
	'''
	Set a skinCluster influences deformation relative to a specified transform.
	@param skinCluster: SkinCluster deformer to create bindPreMatrix for
	@type skinCluster: str
	@param influence: SkinCluster influence to make bindPreMatrix for
	@type influence: str
	@param influenceBase: BindPreMatrix transform
	@type influenceBase: str or None
	@param parent: Parent joint to bindPreMatrix transform
	@type parent: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check SkinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "'+skinCluster+'" specified!')
	
	# Check Influence
	if not mc.objExists(influence):
		raise Exception('Influence "'+influence+'" does not exist!')
	
	# Check InfluenceBase
	if influenceBase:
		if not mc.objExists(influenceBase):
			raise Exception('Influence base "'+influenceBase+'" does not exist!')
	if not influenceBase: influenceBase = influence
	
	# =========================
	# - Connect BindPreMatrix -
	# =========================
	
	# Get Influence Index
	infIndex = getInfluenceIndex(skinCluster,influence)
	
	# Check influence == influenceBase
	if influence == influenceBase:
		print('BindPreMatrix >> '+influence)
		mc.connectAttr(influence+'.parentInverseMatrix[0]',skinCluster+'.bindPreMatrix['+str(infIndex)+']',f=True)
		return influence
	
	# Create BindPreMatrix Transform
	bpm = None
	if influenceBase:
		bpm = influenceBase
	else:
		bpm = mc.createNode('transform',n=influence.replace(influence.split('_')[-1],'')+'bindPreMatrix')
		# Position, orient and scale bindPreMatrix transform
		mc.delete(mc.parentConstraint(influence,bpm))
		mc.delete(mc.scaleConstraint(influence,bpm))
		# Parent bindPreMatrix transform to relativeTo object
		if parent: mc.parent(influence,bpm)
	
	# Connect bindPreMatrix message to skinCluster influence
	if not mc.objExists(influence+'.influenceBase'):
		mc.addAttr(influence,ln='influenceBase',at='message')
	try: mc.connectAttr(bpm+'.message',influence+'.influenceBase',f=True)
	except: pass
	
	# Connect bindPreMatrix to skinCluster
	try: mc.connectAttr(bpm+'.worldInverseMatrix[0]',skinCluster+'.bindPreMatrix['+str(infIndex)+']',f=1)
	except: pass
	
	# =================
	# - Return Result -
	# =================
	
	return bpm

def setGeomMatrix(geo):
	'''
	'''
	# Determine skinCluster
	skinCluster = findRelatedSkinCluster(geo)
	
	# Get Geometry Matrix
	mat = mc.getAttr(geo+'.worldMatrix[0]')
	mc.setAttr(skinCluster+'.geomMatrix',mat,type='matrix')
	
	# Return Result
	return skinCluster

def makeRelative(skinCluster,relativeTo):
	'''
	Set a skinClusters deformation relative to a specified transform.
	@param skinCluster: SkinCluster deformer to set as relative
	@type skinCluster: str
	@param relativeTo: Transform that the skinCluster deformation will be relative to
	@type relativeTo: str
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "' + skinCluster + '" specified!')
	
	# Verify relativeTo object
	if not mc.objExists(relativeTo):
		raise Exception('Object "'+relativeTo+'" does not exist!')
	else:
		if mc.objectType(relativeTo) != 'transform':
			raise Exception('Object "'+relativeTo+'" is not a valid transform!')
	
	# Build bindPreMatrix network
	influenceList = mc.skinCluster(skinCluster,q=1,inf=1)
	infBaseList = []
	for inf in influenceList:
		
		# Determine influenceIndex
		infInd = -1
		plugConnection = mc.listConnections(inf+'.worldMatrix[0]',s=0,d=1,p=1,type="skinCluster")
		for plug in plugConnection:
			plugElem = plug.split('.')
			if plugElem[0] == skinCluster:
				index = plugElem[1].split('[')
				index = index[1].split(']')
				infInd = index[0]
				break
		if infInd < 0:
			raise Exception('Influence index could not be determined!')
		
		# Create bindPreMatrix transform
		bpm = ''
		try:
			# Check for existing bindPreMatrix connection
			bpm = mc.listConnections(inf+'.influenceBase',s=True,d=False)[0]
			infBaseList.append(bpm)
		except:
			bmpName = inf+'_bpm'
			if inf.count('_'):
				bmpName = inf.replace(inf.split('_')[-1],'bmp')
				print bmpName
			bpm = mc.createNode('transform',n=bmpName)
			infBaseList.append(bpm)
			# Connect bindPreMatrix message to skinCluster influence
			if not mc.objExists(inf+'.influenceBase'):
				mc.addAttr(inf,ln='influenceBase',at='message')
			mc.connectAttr(bpm+'.message',inf+'.influenceBase',)
			# Position, orient and scale bindPreMatrix transform
			mc.delete(mc.parentConstraint(inf,bpm))
			mc.delete(mc.scaleConstraint(inf,bpm))
			# Parent bindPreMatrix transform to relativeTo object
			mc.parent(bpm,relativeTo)
		# Connect bindPreMatrix to skinCluster
		bpmConn = mc.listConnections(skinCluster+'.bindPreMatrix['+str(infInd)+']',s=1,d=0)
		if type(bpmConn) == list:
			if bpm != bpmConn[0]: mc.connectAttr(bpm+'.worldInverseMatrix[0]',skinCluster+'.bindPreMatrix['+str(infInd)+']',f=1)
		else:
			mc.connectAttr(bpm+'.worldInverseMatrix[0]',skinCluster+'.bindPreMatrix['+str(infInd)+']',f=1)
	
	# Determine skin object
	obj = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]
	# Connect skinned geometry parent matrix to skinCluster.geomMatrix
	mc.connectAttr(obj+'.parentMatrix[0]',skinCluster+'.geomMatrix',f=1)
	
	# Return InfluenceBase List
	return infBaseList

def skinAs(src,dst,smooth=False):
	'''
	Bind a destination mesh based on the influence list and weights of the skinCluster of a source mesh.
	@param src: Source mesh that will be used to determine influence list and weights of destination mesh.
	@type src: str
	@param dst: Destination mesh to bind based on source mesh skinCluster.
	@type dst: str
	@param smooth: Smooth incoming skinCluster weights for destination mesh.
	@type smooth: bool
	'''
	# Check inputs
	if not mc.objExists(src): raise Exception('Source object "'+src+'" does not exist!')
	if not mc.objExists(dst): raise Exception('Destination object "'+dst+'" does not exist!')
	
	# Get source skinCluster
	srcSkin = findRelatedSkinCluster(src)
	
	# Check destination skinCluster
	dstSkin = findRelatedSkinCluster(dst)
	
	# Build destination skinCluster
	if not dstSkin:
		dstPrefix = dst.split(':')[-1]
		srcInfList = mc.skinCluster(srcSkin,q=True,inf=True)
		dstSkin = mc.skinCluster(srcInfList,dst,toSelectedBones=True,rui=False,n=dstPrefix+'_skinCluster')[0]
	
	# Copy skin weights
	mc.copySkinWeights(	sourceSkin=str(srcSkin),
						destinationSkin=str(dstSkin),
						surfaceAssociation='closestPoint',
						influenceAssociation='name',
						noMirror=True,
						smooth=smooth	)
	
	# Return result
	return dstSkin

def skinObjectList(objList,jntList):
	'''
	Skin a list of objects to a list of influences
	@param objList: List of geoemrty to create skinClusters for.
	@type objList: list
	@param jntList: List of joints to add as skinCluster influences.
	@type jntList: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Geometry
	for obj in objList:
		if not mc.objExists(obj):
			raise Exception('Object "'+obj+'" does not exist!')
	
	# Check Joints
	for jnt in jntList:
		if not mc.objExists(jnt):
			raise Exception('Joint "'+jnt+'" does not exist!')
	
	# =======================
	# - Create SkinClusters -
	# =======================
	
	# Initialize SkinCluster List
	skinClusterList = []
	
	for obj in objList:
		
		# Get Short Name
		objName = mc.ls(obj,sn=True)[0].split(':')[-1]
		
		# Create SkinCluster
		skinCluster = mc.skinCluster(jntList,obj,toSelectedBones=True,rui=False,n=objName+'_skinCluster')[0]
		
		# Append to Return List
		skinClusterList.append(skinCluster)
	
	# =================
	# - Return Result -
	# =================
	
	return skinClusterList

def skinObjectListFromUI():
	'''
	Skin a list of objects to a list of influences based on the current selection.
	'''
	# Get User Selection
	sel = mc.ls(sl=1,o=True)
	
	# Sort Geometry from Joints
	jntList = [jnt for jnt in sel if glTools.utils.joint.isJoint(jnt)]
	objList = [jnt for jnt in sel if not glTools.utils.joint.isJoint(jnt)]
	
	# Create SkinClusters
	skinClusterList = skinObjectList(objList,jntList)
	
	# Return Result
	return skinClusterList

def clean(skinCluster,tolerance=0.005):
	'''
	Clean SkinCluster. Prune weights below the specified threshold, and remove unused influences.
	@param skinCluster: SkinCluster to clean.
	@type skinCluster: str
	@param tolerance: Prune all influence weights below this value.
	@type tolerance: float
	'''
	# Print Message
	print('Cleaning skinCluster: '+skinCluster)
	
	# Get Affected Geometry
	geoShape = mc.skinCluster(skinCluster,q=True,g=True)
	if not geoShape:
		raise Exception('Unable to determine deformed geometry from skinCluster "'+skinCluster+'"!')
	geo = mc.listRelatives(geoShape[0],p=True,pa=True)
	if not geo:
		raise Exception('Unable to determine geometry from deformed shape "'+geoShape[0]+'"!')
	# Select Geometry
	mc.select(geo[0])
	
	# Unlock Influence Weights
	lockSkinClusterWeights(skinCluster,lock=False,lockAttr=False)
	
	# Prune weights
	mm.eval('doPruneSkinClusterWeightsArgList 1 { "'+str(tolerance)+'" }')
	
	# Remove unused influences
	mm.eval('removeUnusedInfluences')
	
	# Lock Influence Weights
	lockSkinClusterWeights(skinCluster,lock=True,lockAttr=True)

def removeMultipleInfluenceBases(base,duplicates):
	'''
	Remove duplicate skinCluster influence base mesh objects
	@param base: Original skinCluster influence base mesh to replace duplicates.
	@type base: str
	@param duplicates: List of duplicate skinCluster influence base mesh objects
	@type duplicates: list
	'''
	# Check Base Influence
	if not mc.objExists(base):
		raise Exception('Base influence "'+base+'" does not exist!')
	baseShape = mc.listRelatives(base,s=True,ni=True)[0]
	if not baseShape:
		raise Exception('Unable to determine base influence shape for "'+base+'"!')
	
	# For Each Duplicate Base
	for dup in duplicates:
		
		# Get Duplicate Base Shape
		dupShape = mc.listRelatives(dup,s=True,ni=True)
		if not dupShape:
			print('Unable to determine base influence shape for "'+base+'"! Skipping...')
			continue
		
		# Get SkinCluster Connection
		dupConn = mc.listConnections(dup+'.outMesh',s=0,d=1,p=True,type='skinCluster')
		if not dupConn:
			print('Base influence "'+dup+'" deleted! No outgoing skinCluster connections...')
			mc.delete(dup)
			continue
		
		# Get SkinCluster
		dupConnSkin = mc.ls(dupConn[0],o=True)[0]
		
		# Override Connection
		try:
			mc.connectAttr(baseShape+'.outMesh',dupConn[0],f=True)
			print('Base influence connection to skinCluster"'+dupConnSkin+'" overridden ('+dup+' >>> '+base+' )')
		except:
			print('Unable to override base influence connection to skinCluster"'+dupConnSkin+'" ('+dup+' >>> '+base+' )! Skipping...')
			continue
		
		# Delete Duplicate Base Influence
		mc.delete(dup)
	
	# Return Result
	return

def replaceGeomInfluenceBase(skinCluster,influence,influenceBase,deleteOldBase=False):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "' + skinCluster + '" specified!')
	
	# Influence
	infList = mc.skinCluster(skinCluster,q=True,inf=True)
	if not infList.count(influence):
		raise Exception('Object "'+influence+'" is not a valid influence of skinCluster "'+skinCluster+'"!')
	
	# ==========================
	# - Replace Influence Base -
	# ==========================
	
	# Get influence index
	infIndex = getInfluenceIndex(skinCluster,influence)
	
	# Get Existing Influence Base
	oldBase = mc.listConnections(skinCluster+'.basePoints['+str(infIndex)+']',s=True,d=False)
	
	# Connect to SkinCluster
	mc.connectAttr(influenceBase+'.outMesh',skinCluster+'.basePoints['+str(infIndex)+']',f=True)
	
	# Delete Old Influence Base
	if deleteOldBase: mc.delete(oldBase)
	
	# =================
	# - Return Result -
	# =================
	
	return infIndex
