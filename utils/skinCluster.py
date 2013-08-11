import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.utils.component
import glTools.utils.deformer
import glTools.utils.mesh
import glTools.utils.selection
import glTools.utils.stringUtils

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
	if not mc.objExists(geometry): raise Exception('Object '+geometry+' does not exist!')
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
	if not infNameArray.count(influence):
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
	
	# Get connected skinCluster
	try:
		skinCluster = findRelatedSkinCluster(geometry)
	except:
		print ('Object "'+geometry+'" is not connected to a valid skinCluster!!')
		return ''
	
	# Get name prefix
	prefix = glTools.utils.stringUtils.stripSuffix(geometry)
	
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

def clearWeights(objectList=None):
	'''
	Reset the skinCluster weight values (set to 0.0) for the specified objects/components
	@param objectList: List of objects/components whose skinCluster weights will be reset
	@type objectList: list
	'''
	# Define valid geometry list
	geometryList = ['mesh','nurbsCurve','nurbsSurface','lattice']
	
	# Get selection
	if objectList: mc.select(objectList)
	objectList = mc.ls(sl=True,fl=True)
	
	# Get component selection
	compSel = mc.filterExpand(sm=(28,31,46))
	if compSel: mc.select(compSel,d=True)
	else: compSel = []
	
	# Get object selection
	objSel = mc.ls(sl=True)
	for obj in objSel:
		objType = mc.objectType(obj)
		if objType == 'transform':
			try:
				obj = mc.listRelatives(obj,s=True,ni=True)[0]
				objType = mc.objectType(obj)
			except: continue
		if not geometryList.count(objType): continue
		compSel.extend(glTools.utils.component.getComponentStrList(obj))
	
	if not compSel: return
	mc.select(compSel)
	objPath = OpenMaya.MDagPath()
	compObj = OpenMaya.MObject()
	objSel = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getActiveSelectionList(objSel)
	
	# Iterate through selection
	for i in range(objSel.length()):
		# Get geometry MDagPath and component MObject
		objSel.getDagPath(i,objPath,compObj)
		if compObj.isNull(): continue
		
		# Find related skinCluster
		skinCluster = findRelatedSkinCluster(objPath.partialPathName())
		skinClusterFn = getSkinClusterFn(skinCluster)
		
		# Get skinCluster influence count
		influenceArray = OpenMaya.MDagPathArray()
		influenceCount = skinClusterFn.influenceObjects(influenceArray)
		
		# Clear skinCluster weights to 0.0
		for i in range(influenceCount):
			skinClusterFn.setWeights(objPath,compObj,i,0.0,False)

def deleteBindPose():
	'''
	Delete all bind pose nodes (dagPose) in scene
	'''
	# Delete bind pose nodes
	dagPoseNodes = mc.ls(typ='dagPose')
	if dagPoseNodes: mc.delete(dagPoseNodes)

def smoothFlood(skinCluster,iterations=1):
	'''
	Smooth flood all influences
	@param geometry: The geometry connected to the skinCluster to smooth
	@type geometry: str
	@param iterations: Number of smooth iterations
	@type iterations: int
	'''
	# Check zero iterations
	if not iterations: return
	
	# Get current tool
	currentTool = mc.currentCtx()
	
	# Select geometry
	geometry = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()
	mc.select(geometry)
	
	# Get skinCluster influence list
	influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
	
	# Unlock influence weights
	for influence in influenceList: mc.setAttr(influence+'.lockInfluenceWeights',0)
	
	# Initialize paint context
	skinPaintTool = 'artAttrSkinContext'
	if not mc.artAttrSkinPaintCtx(skinPaintTool,ex=True):
		mc.artAttrSkinPaintCtx(skinPaintTool,i1='paintSkinWeights.xpm',whichTool='skinWeights')
	mc.setToolTo(skinPaintTool)
	mc.artAttrSkinPaintCtx(skinPaintTool,edit=True,sao='smooth')
	
	# Smooth Weights
	for i in range(iterations):
		print(skinCluster+': Smooth Iteration - '+str(i+1))
		for influence in influenceList:
			# Lock current influence weights
			mc.setAttr(influence+'.lockInfluenceWeights',1)
			# Smooth Flood
			mm.eval('artSkinSelectInfluence artAttrSkinPaintCtx "'+influence+'" "'+influence+'"')
			mc.artAttrSkinPaintCtx(skinPaintTool,e=True,clear=True)
			# Unlock current influence weights
			mc.setAttr(influence+'.lockInfluenceWeights',0)
	
	# Reset current tool
	mc.setToolTo(currentTool)

def smoothWeights(mesh,ptList=[],iterations=1,faceConnectivity=False):
	'''
	'''
	# Check mesh
	if not mc.objExists(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!')
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check ptList
	if not ptList:
		ptList = glTools.utils.component.getComponentStrList(mesh)
	
	# Get connected skinCluster
	skin = findRelatedSkinCluster(mesh)
	
	# Get skinCluster influence list
	infList = mc.skinCluster(skin,q=True,inf=True)
		
	# Build vertex connectivity list
	vtxConnList = glTools.utils.mesh.vertexConnectivityList(mesh,faceConnectivity)
	
	# Build weight list
	vtxWtList = []
	infWtList = [wtList.append(getInfluenceWeights(skin,inf)) for inf in infList]
	for i in range(len(vtxConnList)): vtxWtList[i] = [wt[i] for wt in infWtList]
		
	# Smooth Weights
	for i in range(iterations):
		
		for pt in ptList:
				
			# Get component details
			ptSel = glTools.utils.selection.getSelectionElement(pt,0)
			ptObj = ptSel[1]
			ptInd = glTools.utils.component.index(pt)
			
			# Get component data
			ptWt = [wt[ptInd] for wt in wtList]
			

def mirrorSkin(skinCluster,search='L_',replace='R_'):
	'''
	Create a mirrored skinCluster based on the influence list and weights of another specified skinCluster
	@param skinCluster: The existing skinCluster to mirror
	@type skinCluster: str
	@param search: Name prefix of the source skinCluster
	@type search: str
	@param replace: Name prefix of the destination skinCluster geometry/influences
	@type replace: str
	'''
	# Check skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Object "'+skinCluster+'" is not a valid skinCluster!')
	
	# Get affected object
	sourceGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]
	if not sourceGeo.startswith(search):
		raise Exception('Search string "'+search+'" not found in source geometry name!')
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
	
def bindPreMatrix(skinCluster,influence,parent=True):
	'''
	Set a skinClusters deformoration relative to a specified transform.
	@param skinCluster: SkinCluster deformer to create bindPreMatrix for
	@type skinCluster: str
	@param influence: SkinCluster influence to make bindPreMatrix for
	@type influence: str
	@param parent: Parent joint to bindPreMatrix transform
	@type parent: bool
	'''
	# Verify skinCluster
	if not isSkinCluster(skinCluster):
		raise Exception('Invalid skinCluster "' + skinCluster + '" specified!')
	
	# Check influence
	if not mc.objExists(influence):
		raise Exception('Influence "' + influence + '" does not exist!')
	
	# Get influence index
	infIndex = getInfluenceIndex(skinCluster,influence)
	
	# Create bindPreMatrix transform
	bpm = ''
	if mc.objExists(influence+'.influenceBase'):
		bpm = mc.listConnections(influence+'.influenceBase',s=True,d=False)
	if not bpm:
		bpm = mc.createNode('transform',n=influence.replace(influence.split('_')[-1],'')+'bindPreMatrix')
		# Connect bindPreMatrix message to skinCluster influence
		if not mc.objExists(influence+'.influenceBase'):
			mc.addAttr(influence,ln='influenceBase',at='message')
		mc.connectAttr(bpm+'.message',influence+'.influenceBase',)
		# Position, orient and scale bindPreMatrix transform
		mc.delete(mc.parentConstraint(influence,bpm))
		mc.delete(mc.scaleConstraint(influence,bpm))
		# Parent bindPreMatrix transform to relativeTo object
		if parent: mc.parent(influence,bpm)
	else:
		bpm = bpm[0]
	
	# Connect bindPreMatrix to skinCluster
	mc.connectAttr(bpm+'.worldInverseMatrix[0]',skinCluster+'.bindPreMatrix['+str(infIndex)+']',f=1)
	
	# Return Influence Base List
	return bpm

def makeRelative(skinCluster,relativeTo):
	'''
	Set a skinClusters deformeration relative to a specified transform.
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
		srcInfList = mc.skinCluster(srcSkin,q=True,inf=True)
		dstSkin = mc.skinCluster(srcInfList,dst,rui=False,n=dst+'_skinCluster')[0]
	
	# Copy skin weights
	mc.copySkinWeights(ss=str(srcSkin),ds=str(dstSkin),noMirror=True,sm=smooth)
	
	# Return result
	return dstSkin

def clean(skinCluster,tolerance=0.005):
	'''
	'''
	# Get affected geometry
	geoShape = mc.skinCluster(q=True,g=skinCluster)
	geo = mc.listRelatives(geoShape[0],p=True,pa=True)
	mc.select(geo[0])
	
	# Prune weights
	mm.eval('doPruneSkinClusterWeightsArgList 1 { "'+tolerance+'" }')
	
	# Remove unused influences
	mm.eval('removeUnusedInfluences')
	