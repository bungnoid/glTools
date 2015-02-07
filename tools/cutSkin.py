import maya.mel as mm
import maya.cmds as mc

import glTools.tools.mesh

import glTools.utils.component
import glTools.utils.mathUtils
import glTools.utils.mesh
import glTools.utils.skinCluster

def cutSkin(mesh,weightThreshold=0.25,reducePercent=None,parentShape=False):
	'''
	Extract a per influence proxy mesh from a skinned mesh based on influence weights.
	@param mesh: Mesh to extract faces from
	@type mesh: str
	@param weightThreshold: Influence to use to extract faces
	@type weightThreshold: float
	@param reducePercent: Influence to use to extract faces
	@type reducePercent: int or None
	'''
	# Initialize
	startTime = mc.timerX()
	mc.undoInfo(state=False)
	
	# Get Skin Info
	skin = glTools.utils.skinCluster.findRelatedSkinCluster(mesh)
	if not skin:
		print('Cut Skin: Mesh "" has no skinCluster! Skipping...')
		return None
	
	# Prune Weights
	glTools.utils.skinCluster.lockSkinClusterWeights(skin,lock=False,lockAttr=False)
	pruneWts = glTools.utils.mathUtils.distributeValue(10,rangeStart=0.001,rangeEnd=weightThreshold)
	mc.select(mesh)
	for wt in pruneWts:
		try: mm.eval('doPruneSkinClusterWeightsArgList 1 {"'+str(wt)+'"}')
		except Exception, e:
			print('Prune weight FAILED ('+mesh+')! '+str(e))
			break
	
	# Extract Influence Meshes
	infMeshList = []
	infList = mc.skinCluster(skin,q=True,inf=True)
	for influence in infList:
		infMesh = cutSkin_extractInfluenceMesh(mesh,influence)
		if not infMesh: continue
		if reducePercent != None:
			try: cutSkin_reduce(infMesh,percent=reducePercent)
			except Exception, e: print('Error during reduce ('+infMesh+'): '+str(e))
		if parentShape:
			infMeshShape = cutSkin_parentShape(infMesh)
			infMeshList.extend(infMeshShape)
		else:
			infMeshList.append(infMesh)
	
	# Finalize
	totalTime = mc.timerX(startTime=startTime)
	print('CutSkin - Total Time: '+str(totalTime))
	mc.undoInfo(state=True)
	
	# Return Result
	return infMeshList

def cutSkin_extractInfluenceMesh(mesh,influence):
	'''
	Extract new mesh from faces of original skinned mesh based on influence weights.
	@param mesh: Mesh to extract faces from
	@type mesh: str
	@param influence: Influence to use to extract faces
	@type influence: str
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh! Unable to extract influence mesh...')
	
	# Get SkinCluster
	skin = glTools.utils.skinCluster.findRelatedSkinCluster(mesh)
	if not skin:
		raise Exception('Mesh "'+mesh+'" has no skinCluster! Unable to extract influence mesh...')
	# Get Influence List
	infList = mc.skinCluster(skin,q=True,inf=True)
	if not influence in infList:
		raise Exception('SkinCluster "'+skin+'" has no influence "'+influence+'"! Unable to extract influence mesh...')
	
	# Get Influence Faces
	mc.select(cl=True)
	mc.skinCluster(skin,e=True,selectInfluenceVerts=influence)
	infVtxList = mc.ls(sl=1)
	if not infVtxList: return None
	try:
		infVtxList = glTools.utils.component.expandVertexSelection(infVtxList)
		infVtxList = glTools.utils.component.shrinkVertexSelection(infVtxList)
	except: pass
	if not infVtxList: return None
	infFaceList = mc.polyListComponentConversion(infVtxList,fv=True,tf=True,internal=True) or []
	if not infFaceList: return None
	if '*' in infFaceList[0]: return None
	
	# Duplicate Mesh
	infMesh = glTools.tools.mesh.reconstructMesh(mesh)
	infMeshShape = mc.listRelatives(infMesh,s=True,ni=True)[0]
	childNodes = mc.listRelatives(infMesh,c=True)
	if infMeshShape in childNodes: childNodes.remove(infMeshShape)
	if childNodes: mc.delete(childNodes)
	try: mc.parent(infMesh,w=True)
	except: pass
	mc.setAttr(infMesh+'.overrideEnabled',0)
	
	# Extract Influence Faces
	infFaceList = [i.replace(mesh,infMesh) for i in infFaceList]
	mc.select(infFaceList)
	mm.eval('InvertSelection')
	mc.delete()
	mc.delete(infMesh,ch=True)
	
	# Add Attributes
	infProxyAttr = 'influenceProxy'
	meshProxyAttr = 'meshProxy'
	mc.addAttr(infMesh,ln=infProxyAttr,dt='string')
	mc.setAttr(infMesh+'.'+infProxyAttr,influence,type='string',l=True)
	mc.addAttr(infMesh,ln=meshProxyAttr,dt='string')
	mc.setAttr(infMesh+'.'+meshProxyAttr,mesh,type='string',l=True)
	
	# Return Result
	return infMesh
	
def cutSkin_reduce(mesh,percent=50):
	'''
	Basic mesh cleanup and reduce.
	@param mesh: Mesh to cleanup and reduce
	@type mesh: str
	@param percent: Poly reduce percent amount
	@type percent: int or float
	'''
	# Get Influence Mesh Attributes
	infProxy = None
	infProxyAttr = 'influenceProxy'
	if mc.objExists(mesh+'.'+infProxyAttr): infProxy = mc.getAttr(mesh+'.'+infProxyAttr)
	meshProxy = None
	meshProxyAttr = 'meshProxy'
	if mc.objExists(mesh+'.'+meshProxyAttr): meshProxy = mc.getAttr(mesh+'.'+meshProxyAttr)
	
	# Separate to Shells
	meshItems = [mesh]
	try: meshItems = mc.polySeparate(mesh,ch=False)
	except: pass
	
	# Clean Non-manifold Geometry
	glTools.utils.mesh.polyCleanup(	meshList = meshItems,
									nonManifold = True,
									keepHistory = False,
									fix = True )
	
	# Poly Reduce
	for meshItem in meshItems:
		try:
			mc.polyReduce(	meshItem,
							version		= 1,	# New
							termination	= 0,	# Percentage termination
							percentage	= percent,
							sharpness	= 1,
							keepBorder	= 1,
							keepMapBorder = 1,
							keepColorBorder = 0,
							keepFaceGroupBorder = 0,
							keepHardEdge = 0,
							keepCreaseEdge = 0,
							keepBorderWeight = 1,
							keepMapBorderWeight = 1,
							preserveTopology = 1,
							keepQuadsWeight = 1,
							replaceOriginal = 1,
							cachingReduce = 0,
							constructionHistory = 0 )
		except: pass
	
	# Cleanup
	if len(meshItems) > 1:
		meshResult = mc.polyUnite(meshItems,ch=False,mergeUVSets=True)
		if mc.objExists(mesh): mc.delete(mesh)
		mesh = mc.rename(meshResult,mesh)
	
	# Rebuild Influence Mesh Attributes
	if infProxy and not mc.objExists(mesh+'.'+infProxyAttr):
		mc.addAttr(mesh,ln=infProxyAttr,dt='string')
		mc.setAttr(mesh+'.'+infProxyAttr,infProxy,type='string',l=True)
	if meshProxy and not mc.objExists(mesh+'.'+meshProxyAttr):
		mc.addAttr(mesh,ln=meshProxyAttr,dt='string')
		mc.setAttr(mesh+'.'+meshProxyAttr,meshProxy,type='string',l=True)
	
	# Return Result
	return mesh

def cutSkin_parentShape(infMesh):
	'''
	Parent influence mesh shape to influence transform.
	@param infMesh: Influence mesh to parent to influence transform.
	@type infMesh: str
	'''
	# Checks Influence Mesh
	if not mc.objExists(infMesh):
		raise Exception('Influence mesh "'+infMesh+'" does not exist!')
	
	# Checks Influence Attr	
	infProxyAttr = 'influenceProxy'
	if not mc.attributeQuery(infProxyAttr,n=infMesh,ex=True):
		raise Exception('Influence mesh "'+infMesh+'" has no "'+infProxyAttr+'" attribute! Unable to parent influence shape...')
	influence = mc.getAttr(infMesh+'.'+infProxyAttr)
	if not mc.objExists(influence):
		raise Exception('Influence does not exist! Unable to parent shape...')
	
	# Get Shape(s)
	infShapes = []
	if glTools.utils.transform.isTransform(infMesh):
		infShapes = mc.listRelatives(infMesh,s=True,ni=True,pa=True)
	elif str(mc.objectType(infMesh)) in ['mesh','nurbsSurface']:
		infShapes = [str(infMesh)]
	
	# Parent Proxy Shapes to Joint
	for i in range(len(infShapes)):
		infShapesParent = mc.listRelatives(infShapes[i],p=True,pa=True)[0]
		for at in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
			try: mc.setAttr(infShapesParent+'.'+at,l=False)
			except: pass
		infShapes[i] = glTools.utils.shape.parent(infShapes[i],influence)[0]
		glTools.utils.base.displayOverride(infShapes[i],overrideEnable=1,overrideDisplay=2,overrideLOD=0)
	
	# Delete Original
	mc.delete(infMesh)
	
	# Tag Shapes
	proxyAttr = 'proxyJoint'
	for shape in infShapes:
		if not mc.objExists(shape+'.'+proxyAttr):
			mc.addAttr(shape,ln=proxyAttr,dt='string')
			mc.setAttr(shape+'.'+proxyAttr,influence,type='string',l=True)
	
	# Return Result
	return infShapes
