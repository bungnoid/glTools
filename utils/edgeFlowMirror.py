import maya.cmds as mc
import maya.mel as mm

import glTools.utils.base
import glTools.utils.component
import glTools.utils.deformer
import glTools.utils.skinCluster

def loadPlugin():
	'''
	Load edgFlowMirror plugin.
	'''
	if not mc.pluginInfo('edgeFlowMirror',q=True,l=True):
		mc.loadPlugin('edgeFlowMirror')
	return 1

def addSymEdgeAttr(edge):
	'''
	Add mesh symmetry edge attribute based on specified mesh edge.
	@param edge: Mesh edge that defined the center edge row of a symmetrical mesh
	@type edge: str
	'''
	# Check Edge
	edge = mc.filterExpand(edge,ex=True,sm=32) or []
	if not edge:
		raise Exception('No valid mesh edge selected!')
	if len(edge) > 1:
		print('Multiple mesh edges found! Using first edge only ("'+edge[0]+'").')
	edge = edge[0]
	
	# Get Edge Mesh
	mesh = mc.ls(edge,o=True) or []
	if not mesh:
		raise Exception('Unable to determine mesh from edge!')
	if len(mesh) > 1:
		print('Multiple mesh objects found from edge!')
	mesh = mesh[0]
	mc.select(mesh)
	
	# Get Edge ID
	edgeID = glTools.utils.component.index(edge)
	
	# Add Attribute
	symAttr = 'symmetryEdgeId'
	if not mc.objExists(mesh+'.'+symAttr):
		mc.addAttr(mesh,ln=symAttr,at='long',min=0,dv=edgeID)
	mc.setAttr(mesh+'.'+symAttr,edgeID)
	
	# Return Result
	return mesh+'.'+symAttr

def autoMirror():
	'''
	Perform standard auto mirror based on selected center mesh edge.
	Mesh must be topologically symmetrical.
	'''
	# Load plugin
	loadPlugin()
	
	# Get middle edge selection
	edgeSel = mc.ls(sl=1,fl=1)[0]
	meshSel = mc.ls(edgeSel,o=True)[0]
	
	# Duplicate mesh
	meshDup = mc.duplicate(meshSel,rr=True,n=meshSel+'_symmetry')[0]
	
	# Get base vertex array
	pts = glTools.utils.base.getMPointArray(meshSel)
	
	# Get Symmetry map
	map = mm.eval('edgeFlowMirror -task "getMapArray" -middleEdge '+edgeSel)
	
	# Flip mesh
	for i in range(len(map)):
		mc.move(-pts[i][0],pts[i][1],pts[i][2],meshDup+'.vtx['+str(map[i])+']',a=True,ws=True)
	
	# BlendShape original
	bs = mc.blendShape(meshDup,meshSel)[0]
	bsAlias = mc.listAttr(bs+'.w',m=True)[0]
	mc.setAttr(bs+'.'+bsAlias,0.5)
	
	# Delete history
	mc.delete(meshDup)
	mc.delete(meshSel,ch=True)

def mirrorGeo(middleEdge,axis='x',posToNeg=True):
	'''
	Mirror mesh geometry based on the input arguments
	Mesh must be topologically symmetrical.
	@param middleEdge: Center edge of the mesh to mirror
	@type middleEdge: str
	@param axis: Axis to use for mirror function
	@type axis: str
	@param posToNeg: Mirror from positive to negative across the specified axis
	@type posToNeg: bool
	'''
	# Load plugin
	loadPlugin()
	
	# Get middle edge selection
	mesh = mc.ls(middleEdge,o=True)[0]
	
	# Get base vertex array
	pts = glTools.utils.base.getMPointArray(mesh)
	
	# Get Symmetry map
	map = mm.eval('edgeFlowMirror -task "getMapArray" -middleEdge '+middleEdge)
	side = mm.eval('edgeFlowMirror -task "getSideArray" -middleEdge '+middleEdge)
	
	# Mirror mesh
	for i in range(len(map)):
		
		# Skip center verts
		if not side[i]: continue
		
		if axis == 'x':
			if posToNeg:
				if side[i] == 1: # < 0
					mc.move(-pts[i][0],pts[i][1],pts[i][2],mesh+'.vtx['+str(map[i])+']',a=True,ws=True)
			else:
				if side[i] == 2: # > 0
					mc.move(-pts[i][0],pts[i][1],pts[i][2],mesh+'.vtx['+str(map[i])+']',a=True,ws=True)

def mirrorSkinWeights(middleEdge,leftToRight=True,search='lf_',replace='rt_',refMesh=None):
	'''
	Mirror skin weights for the selected mesh.
	Weights are mirrored based on topological symmetry. If mesh is not topologically symmetrical, this operation will fail.
	@param middleEdge: Center edge of the mesh to mirror skin weights for
	@type middleEdge: str
	@param leftToRight: Mirror skin weights from right to left.
	@type leftToRight: bool
	@param search: Influence search/replace string.
	@type search: str
	@param replace: Influence search/replace string.
	@type replace: str
	@param refMesh: Reference mesh when command wont recognize current mesh.
	@type refMesh: str
	'''
	# Load plugin
	loadPlugin()
	
	# =================
	# - Get Mesh Data -
	# =================
	
	# Get Middle Edge Mesh
	mesh = mc.ls(middleEdge,o=True)[0]
	
	if not refMesh:
		middleEdge.replace(mesh,refMesh)
		#refMesh = mesh
	
	# Get Edge Flow Data
	vmap = mm.eval('edgeFlowMirror -task "getMapArray" -middleEdge '+middleEdge)
	side = mm.eval('edgeFlowMirror -task "getSideArray" -middleEdge '+middleEdge)
	
	# ========================
	# - Get SkinCluster Data -
	# ========================
	
	# Get SkinCluster
	skinCluster = glTools.utils.skinCluster.findRelatedSkinCluster(mesh)
	
	# Get SkinCluster Inluence/Weight Lists
	wt = glTools.utils.skinCluster.getInfluenceWeightsAll(skinCluster)
	infList = mc.skinCluster(skinCluster,q=True,inf=True)
	
	# =======================
	# - Build Influence Map -
	# =======================
	
	infIndex = {}
	infMirror = {}
	for inf in infList:
		
		# Influence Index Map
		infIndex[inf] = glTools.utils.skinCluster.getInfluencePhysicalIndex(skinCluster,inf)
		
		# Influence Mirror Map
		mInf = inf
		if inf.startswith(search): mInf = inf.replace(search,replace)
		if inf.startswith(replace): mInf = inf.replace(replace,search)
		infMirror[inf] = mInf
	
	# ==============================
	# - Mirror SkinCluster Weights -
	# ==============================
	
	# Determine SideToSide ID
	leftToRightId = [2,1][int(leftToRight)]
	
	for v in range(len(vmap)):
		
		if side[v] == leftToRightId:
			
			# Get Mirror Vertex ID
			m = vmap[v]
			
			for inf in infMirror.keys():
				
				# Get Influence and Mirror ID
				mInf = infMirror[inf]
				infInd = infIndex[inf]
				mInfInd = infIndex[mInf]
				
				# Assign Mirror Weight Value
				wt[mInfInd][m] = wt[infInd][v]
	
	# Apply Mirrored Weights
	glTools.utils.skinCluster.setInfluenceWeightsAll(skinCluster,wt,normalize=True,componentList=[])
	
	# =================
	# - Return Result -
	# =================
	
	return wt

def mirrorDeformerWeightValues(middleEdge,deformer):
	'''
	Mirror weight values of a specified deformer given the middle edge of a deformed mesh.
	Geometry is expected to be topologically symmetrical.
	@param middleEdge: Center edge of the mesh to mirror weights for
	@type middleEdge: str
	@param deformer: Source deformer to mirror weights from
	@type deformer: str
	'''
	# Load plugin
	loadPlugin()
	
	# Get Mesh Data
	mesh = mc.ls(middleEdge,o=True)[0]
	vmap = mm.eval('edgeFlowMirror -task "getMapArray" -middleEdge '+middleEdge)
	
	# Get Deformer Weights
	wt = glTools.utils.deformer.getWeights(deformer,geometry=mesh)
	
	# Mirror Deformer Weights
	if len(vmap) > len(wt):
		
		# Membership Weight Mirror - (Generates weight list based on mirrored membership)
		mem = glTools.utils.deformer.getDeformerSetMemberIndices(deformer,mesh)
		mirror_mem = sorted([vmap[i] for i in mem])
		wt = [wt[mem.index(vmap[i])] for i in mirror_mem]
	
	else:
		
		# Basic Weight Mirror
		wt = [wt[i] for i in vmap]
	
	# Return Result
	return wt

def mirrorDeformerWeights(middleEdge,srcDeformer,dstDeformer=None,dstMesh=None):
	'''
	Mirror deformer weights from a source deformer to a destination deformer.
	Geometry is expected to be topologically symmetrical.
	@param middleEdge: Center edge of the mesh to mirror weights for
	@type middleEdge: str
	@param srcDeformer: Source deformer to mirror weights from
	@type srcDeformer: str
	@param dstDeformer: Destination deformer to mirror weights to. If None, use source deformer.
	@type dstDeformer: str or None
	@param dstMesh: Destination mesh geometry to mirror weights to. If None, use source mesh.
	@type dstMesh: str or None
	'''
	# Load Plugin
	loadPlugin()
	
	# Get Mesh Data
	mesh = mc.ls(middleEdge,o=True)[0]
	
	# Check Destination Deformer/Mesh
	if not dstDeformer: dstDeformer = srcDeformer
	if not dstMesh: dstMesh = mesh
	
	# Mirror Deformer Weights
	dstWt = mirrorDeformerWeightValues(middleEdge,srcDeformer)
	glTools.utils.deformer.setWeights(dstDeformer,dstWt,geometry=mesh)
	
	# Return Result
	return dstWt

def mirrorSelection():
	'''
	Mirror the selection on a polygon mesh. Middle edge
	must be selected.
	'''
	# Load plugin
	loadPlugin()
	
	# Seperate selection
	selection = mc.ls(sl=1,fl=1)

	vtxList=[]
	edgeList=[]
	for name in selection:
		if name.count('vtx'):  vtxList.append(name)
		if name.count('e['): edgeList.append(name)

	if not len(vtxList):
		raise Exception('You must select a vertex to mirror!')
		
	if not len(edgeList):
		raise Exception('You must select a middle edge!')
		
	mirrorList = mirrorComponentList(vtxList,edgeList[0])
	
	mc.select(mirrorList)
	
	return mirrorList
		
def mirrorComponentList(componentList,middleEdge):
	'''
	'''
	# Load Plugin
	loadPlugin()
	
	# Check Component List
	if not componentList: raise Exception('Invalid component list!')
	
	# Get Mirror Component List
	mesh = mc.ls(componentList[0],o=True)[0]
	vmap = mm.eval('edgeFlowMirror -task "getMapArray" -middleEdge '+middleEdge)
	indList = glTools.utils.component.getComponentIndexList(componentList)[mesh]
	
	# Build Component List
	mirrorList = [mesh+'.vtx['+str(vmap[i])+']' for i in indList]
	
	# Return Result
	return mirrorList

def mirrorDeformer(middleEdge,deformer,search='lf',replace='rt'):
	'''
	'''
	# Load plugin
	loadPlugin()
	
	# Get Mesh Data
	mesh = mc.ls(middleEdge,o=True)[0]
	vmap = mm.eval('edgeFlowMirror -task "getMapArray" -middleEdge '+middleEdge)
	
	# Mirror Membership
	mem = glTools.utils.deformer.getDeformerSetMemberIndices(deformer,mesh)
	if len(vmap) > len(mem): mem = sorted([vmap[i] for i in mem])
	mem = [mesh+'.vtx['+str(i)+']' for i in mem]
	
	# Create Mirror Deformer
	deformerType = mc.objectType(deformer)
	deformerName = deformer
	if deformerName.startswith(search): deformerName = deformerName.replace(search,replace)
	elif deformerName.startswith(replace): deformerName = deformerName.replace(replace,search)
	else: deformerName = deformerName+'_mirror'
	
	mDeformer = mc.deformer(mem,type=deformerType,name=deformerName)[0]
	
	# Mirror Deofmer Weights
	mirrorDeformerWeights(middleEdge,deformer,dstDeformer=mDeformer)
	
	# Return Result
	return mDeformer
