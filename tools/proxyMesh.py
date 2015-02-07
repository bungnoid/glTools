import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.colorize
import glTools.utils.joint
import glTools.utils.lib
import glTools.utils.mathUtils
import glTools.utils.matrix
import glTools.utils.mesh
import glTools.utils.shape
import glTools.utils.skinCluster
import glTools.utils.stringUtils
import glTools.utils.transform

import ast

def isProxyBound(proxy):
	'''
	Check if the specified object is a valid proxy bounds mesh
	@param proxy: The proxy bounds mesh to query
	@type proxy: str
	'''
	# Check Proxy Attribute
	if not mc.objExists(proxy+'.jointProxy'): return False
	# Check Mesh
	if not glTools.utils.mesh.isMesh(proxy): return False
	# Return Result
	return True
	
def proxyParent(proxyMesh,joint):
	'''
	Parent a proxy mesh shape to a specified parent joint
	@param proxyMesh: Proxy mesh shape to parent to joint
	@type proxyMesh: str
	@param joint: Joint to parent mesh shape to
	@type joint: str
	'''
	# Checks
	if not mc.objExists(proxyMesh):
		raise Exception('Proxy mesh "'+proxyMesh+'" does not exist!')
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	
	# Get Proxy Shape(s)
	proxyShapes = []
	if glTools.utils.transform.isTransform(proxyMesh):
		proxyShapes = mc.listRelatives(proxyMesh,s=True,ni=True,pa=True)
	elif str(mc.objectType(proxyMesh)) in ['mesh','nurbsSurface']:
		proxyShapes = [str(proxyMesh)]
	
	# Parent Proxy Shapes to Joint
	for i in range(len(proxyShapes)):
		proxyShapes[i] = glTools.utils.shape.parent(proxyShapes[i],joint)[0]
		glTools.utils.base.displayOverride(proxyShapes[i],overrideEnable=1,overrideDisplay=2,overrideLOD=0)
	# Delete Old Transform
	mc.delete(proxyMesh)
	
	# Tag Shapes
	proxyAttr = 'proxyJoint'
	for shape in proxyShapes:
		if not mc.objExists(shape+'.'+proxyAttr):
			mc.addAttr(shape,ln=proxyAttr,dt='string')
			mc.setAttr(shape+'.'+proxyAttr,joint,type='string',l=True)
	
	# Return Result
	return proxyShapes

def proxyConstraint(proxyGeo,deleteConstraint=False):
	'''
	Constrain a proxy geometry to the target joint defined by the string value of its "jointProxy" attribute.
	@param proxyGeo: Proxy geometry to constrain to an associated joint.
	@type proxyMesh: str
	'''
	# Checks
	if not isProxyBound(proxyGeo):
		raise Exception('Object "'+proxyGeo+'" is not a valid proxy bounds object!')
	
	# Get Target Joint
	joint = mc.getAttr(proxyGeo+'.jointProxy')
	# Get Proxy Parent
	proxyGrp = mc.listRelatives(proxyGeo,p=True,pa=True)[0]
	
	# Create Constraint
	pCon = mc.parentConstraint(joint,proxyGrp,n=proxyGeo+'_parentConstraint')
	if deleteConstraint: mc.delete(pCon)
	
	# Return Result
	return pCon

def proxyCylinder(joint,axis='x',radius=1.0,divisions=10,cutGeo=[]):
	'''
	Create a basic polygon proxy cube for the specified joint
	@param joint: Joint to create proxy cylinder for
	@type joint: str
	@param axis: Joint axis
	@type axis: str
	@param radius: Proxy cylinder radius
	@type radius: float
	@param divisions: Proxy cylinder radial divisions
	@type divisions: int
	@param cutGeo: List of geometry to be cut by this proxy cylinder
	@type cutGeo: int
	'''
	# Convert Incoming Values
	axis = axis[-1].lower()
	jntChild = mc.ls(mc.listRelatives(joint,c=True,pa=True),type=['joint'])
	if jntChild: jntLen = mc.getAttr(jntChild[0]+'.t'+axis)
	else: jntLen = 0.1
	if jntLen < 0.1: jntLen = 0.1
	axis = glTools.utils.lib.axis_dict()[axis]
	
	# Build Cylinder Mesh
	proxy_cyl = mc.polyCylinder(ch=False,r=radius,h=abs(jntLen)*1.1,sx=divisions,sy=1,sz=0,ax=axis,rcp=0,cuv=0,n=joint+'_PROXY')
	proxy_cyl = proxy_cyl[0]
	
	# Adjust Pivot And Freeze Transforms
	mc.move(axis[0]*jntLen*0.5,axis[1]*jntLen*0.5,axis[2]*jntLen*0.5,proxy_cyl)
	mc.makeIdentity(proxy_cyl,apply=True,t=True)
	mc.xform(proxy_cyl,piv=[0,0,0])
	
	# Create Proxy Group
	proxy_grp = glTools.utils.base.group(proxy_cyl)
	makeProxyBounds(proxy_cyl,joint=joint,cutGeo=cutGeo)
	
	# Constrain To Joint
	proxyConstraint(proxy_cyl)
	
	# Return Result
	return [proxy_grp,proxy_cyl]
	
def proxyCylinder_subDiv(proxy_cyl,numV=5,numU=1):
	'''
	Subdivide proxy cylinder mesh.
	@param proxy_cyl: Proxy cylinder mesh to subdivide
	@type proxy_cyl: str
	@param numV: Number of V subdivisions
	@type numV: int
	@param numU: Number of U subdivisions
	@type numU: int
	'''
	mc.polySubdivideFacet(proxy_cyl,duv=numU,dvv=numV,sbm=1,ch=False)

def makeProxyBounds(mesh,joint=None,cutGeo=None):
	'''
	Make a specified mesh a proxy bounds object.
	@param mesh: Mesh to make into proxy bounds object
	@type mesh: str
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is nat avalid mesh! Unable to create proxy bounds object...')
	
	# Add Joint Tag
	jointProxyAttr = 'jointProxy'
	if not mc.attributeQuery(jointProxyAttr,n=mesh,ex=True):
		mc.addAttr(mesh,ln=jointProxyAttr,dt='string')
	if joint: mc.setAttr(mesh+'.jointProxy',joint,type='string')
	
	# Set Display Override - Shading OFF
	shadingAttr = 'shading'
	if not mc.attributeQuery(shadingAttr,n=mesh,ex=True):
		mc.addAttr(mesh,ln=shadingAttr,at='long',min=0,max=1,dv=0,k=True)
	mc.connectAttr(mesh+'.'+shadingAttr,mesh+'.overrideShading')
	mc.setAttr(mesh+'.overrideEnabled',1)
	mc.setAttr(mesh+'.doubleSided',0)
	mc.setAttr(mesh+'.opposite',0)
	
	# Cut Geometry Attribute
	cutGeoAttr = 'shading'
	if not mc.attributeQuery(cutGeoAttr,n=mesh,ex=True):
		mc.addAttr(mesh,ln=cutGeoAttr,dt='string')
	if cutGeo: mc.setAttr(mesh+'.'+cutGeoAttr,str(cutGeo),type='string')
	
	# Set Colour
	glTools.utils.colorize.setColour(mesh)
	
	# Return Result
	return mesh

def cutGeoAttr(proxyList):
	'''
	Add a "cutGeometry" attribute to the specified list of proxy bounds objects
	@param proxyList: List of proxy bounds objects to add attributes to.
	@type proxyList: list
	'''
	# Define Attribute
	attr = 'cutGeometry'
	
	# Check Proxy List
	if not proxyList:
		raise Exception('Empty or invalid proxy list!')
	
	for proxy in proxyList:
		if mc.attributeQuery(attr,n=proxy,ex=True):
			print('Proxy bounds object "'+proxy+'" already has a "'+attr+'" attribute! Skipping...')
			continue
		
		# Add Cut Geometry Attribute
		mc.addAttr(proxy,ln=attr,dt='string')
	
	# Return Result
	return proxyList

def addGeoAttr(proxyList):
	'''
	Add a "addGeometry" attribute to the specified list of proxy bounds objects
	@param proxyList: List of proxy bounds objects to add attributes to.
	@type proxyList: list
	'''
	# Define Attribute
	attr = 'addGeometry'
	
	# Check Proxy List
	if not proxyList:
		raise Exception('Empty or invalid proxy list!')
	
	for proxy in proxyList:
		if mc.attributeQuery(attr,n=proxy,ex=True):
			print('Proxy bounds object "'+proxy+'" already has a "'+attr+'" attribute! Skipping...')
			continue
	
		# Add Cut Geometry Attribute
		mc.addAttr(proxy,ln=attr,dt='string')
	
	# Return Result
	return proxyList

def initialShadingGroupAttr(proxyList):
	'''
	Add a "addInitialShadingGroup" attribute to the specified list of proxy bounds objects
	@param proxyList: List of proxy bounds objects to add attributes to.
	@type proxyList: list
	'''
	# Define Attribute
	attr = 'applyInitialShadingGroup'
	
	# Check Proxy List
	if not proxyList:
		raise Exception('Empty or invalid proxy list!')
	
	for proxy in proxyList:
		
		# Add InitialShadingGroup Attribute
		if not mc.attributeQuery(attr,n=proxy,ex=True):
			mc.addAttr(proxy,ln=attr,at='bool')
		
		# Apply InitialShadingGroup Attribute
		mc.setAttr(proxy+'.'+attr,1)
	
	# Return Result
	return proxyList

def skeletonProxyCage(jntList,cutGeo=[]):
	'''
	Create proxy bounds geometry for every joint in the input list.
	Optionally, provide a mesh that the proxy bounds geometry will try to scale to fit around.
	@param jntList: List of joints to create proxy bounds geometry for
	@type jntList: list
	@param cutGeo: List of geometry to be cut by the proxy cylinders
	@type cutGeo: int
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Boundary
	if not jntList: return
	for jnt in jntList:
		if not mc.objExists(jnt):
			raise Exception('Joint "'+jnt+'" does not exist!')
	
	# Check Cut Geometry
	if not cutGeo:
		result = mc.promptDialog(	title='Set Cut Geo List',
									message='Cut Geometry List:',
									button=['Set', 'Cancel'],
									defaultButton='Set',
									cancelButton='Cancel',
									dismissString='Cancel'	)
	
		if result == 'Set':
			cutGeoStr = mc.promptDialog(q=True,text=True)
			if cutGeoStr.count(','):
				cutGeo = cutGeoStr.split(',')
			else:
				cutGeo = [cutGeoStr]
		else:
			print 'No cut geometry provided! Exiting...'
			return
	
	# ========================
	# - Build Proxy Geometry -
	# ========================
	
	proxyMainGrp = 'PROXY_grp'
	if not mc.objExists(proxyMainGrp):
		proxyMainGrp = mc.group(em=True,n='PROXY_grp')
	
	# For Each Joint
	proxyGeoList = []
	for jnt in jntList:
		
		# Check End Joint
		jntChildren = mc.ls(mc.listRelatives(jnt,ad=True),type='joint')
		#if not jntChildren: continue
		
		# Create Proxy Geo
		proxy = proxyCylinder(	joint = jnt,
								axis = 'x',
								radius = 0.5,
								divisions = 10,
								cutGeo = cutGeo )
		proxyGrp = proxy[0]
		proxyGeo = proxy[1]
		
		# Parent to main Proxy Group
		mc.parent(proxyGrp,proxyMainGrp)
		
		# Append To Return List
		proxyGeoList.append(proxyGeo)
	
	# Return Result
	return proxyGeoList

def proxyFitJoint(proxyGeo,joint='',axis='x'):
	'''
	Fit the specified proxy geometry (mesh cylinder) to a given joint.
	If no joint is specified, use the joint specified by the proxy "jointProxy" attribute.
	@param proxyGeo: Proxy geometry to to fit to the joint 
	@type proxyGeo: str
	@param joint: Joint to fit the proxy geometry to. If empty, use the "jointProxy" string attribute value. 
	@type joint: str
	@param axis: Length-wise axis of the joint. 
	@type axis: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Proxy Geo
	if not isProxyBound(proxyGeo):
		raise Exception('Object "'+proxyGeo+'" is not a valid proxy bound object!')
	
	# Joint
	if not joint:
		joint = mc.getAttr(proxyGeo+'.jointProxy')
	if not glTools.utils.joint.isJoint(joint):
		raise Exception('Object "'+joint+'" is not a valid joint!')
	
	# Axis
	axis = axis.lower()
	axisList = ['x','y','z']
	if not axisList.count(axis):
		raise Exception('Invalid axis value! ("'+axis+'")')
	axisInd = axisList.index(axis)
	
	# ================
	# - Fit To Joint -
	# ================
	
	# Get Joint Length
	jntLen = glTools.utils.joint.length(joint)
	#jntLen = glTools.utils.mathUtils.mag(mc.getAttr(joint+'.t')[0])
	jntEnd = mc.listRelatives(joint,c=True)
	if jntEnd: jntLen = mc.getAttr(jntEnd[0]+'.t'+axis)
	jntMat = glTools.utils.matrix.getMatrix(joint,local=False,time=None)
	
	print(jntLen)
	
	# For Each Vertex
	for i in range(mc.polyEvaluate(proxyGeo,v=True)):
		vtx = proxyGeo+'.vtx['+str(i)+']'
		
		# Get Position
		pos = mc.pointPosition(vtx)
		localPos = glTools.utils.matrix.vectorMatrixMultiply(pos,jntMat,transformAsPoint=True,invertMatrix=True)
		
		# Check joint relative position 
		if localPos[axisInd] < (jntLen*0.5):
			localPos[axisInd] = -jntLen*0.1
		elif localPos[axisInd] > (jntLen*0.5):
			localPos[axisInd] = jntLen*1.1
		
		# Get new world position
		pos = glTools.utils.matrix.vectorMatrixMultiply(localPos,jntMat,transformAsPoint=True,invertMatrix=False)
		
		# Set Position
		mc.move(pos[0],pos[1],pos[2],vtx,ws=True,a=True)
	
	# =================
	# - Return Result -
	# =================
	
	return joint

def proxyFitMesh(proxyGeo,boundaryMesh,boundaryOffset=0.0):
	'''
	Fit the specified proxy geometry (mesh cylinder) to a given boundary mesh.
	@param proxyGeo: Proxy geometry to to fit to mesh 
	@type proxyGeo: str
	@param boundaryMesh: Boundary mesh to fit proxy geo to.
	@type boundaryMesh: str
	@param boundaryOffset: Distance by which the proxy mesh will overshoot the boundary mesh.
	@type boundaryOffset: float
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not isProxyBound(proxyGeo):
		raise Exception('Object "'+proxyGeo+'" is not a valid proxy bound object!')
	if not mc.objExists(boundaryMesh):
		raise Exception('Boundary mesh "'+boundaryMesh+'" does not exist!')
	
	# Check Vertex Count
	vtxCount = mc.polyEvaluate(proxyGeo,v=True)
	#if vtxCount%2: raise Exception('Uneven number of vertices!')
	
	# Get Joint Details
	jntSt = mc.getAttr(proxyGeo+'.jointProxy')
	jntStPos = mc.xform(jntSt,q=True,ws=True,rp=True)
	jntEn = mc.ls(mc.listRelatives(jntSt,c=True),type='joint')
	if jntEn:
		jntEnPos = mc.xform(jntEn[0],q=True,ws=True,rp=True)
	else:
		jntAxis = glTools.utils.transform.axisVector(jntSt,'x',normalize=True)
		jntEnPos = map(sum,zip(jntStPos,jntAxis))
	
	# ===============
	# - Fit To Mesh -
	# ===============
	
	# Get Vertex Position List
	pntList = glTools.utils.base.getPointArray(proxyGeo)
	
	for i in range(vtxCount):
		
		# Get intersection source point
		#srcPt = jntEnPos
		#if i < (vtxCount/2): srcPt = jntStPos
		srcPt = glTools.utils.mathUtils.closestPointOnLine(pntList[i],jntStPos,jntEnPos,clampSegment=False)
		
		# Get intersection direction
		intersectVec = glTools.utils.mathUtils.normalizeVector(glTools.utils.mathUtils.offsetVector(srcPt,pntList[i]))
		
		# Get intersection point
		intersectPnt = glTools.utils.mesh.allIntersections(	mesh = boundaryMesh,
															source = srcPt,
															direction = intersectVec,
															testBothDirections = False,
															maxDist = 9999,
															sort = True	)
		
		# Get intersection distance
		intersectDist = glTools.utils.mathUtils.distanceBetween(srcPt,intersectPnt[0])
		
		# Offset Point
		#mc.move(	intersectPnt[0][0],intersectPnt[0][1],intersectPnt[0][2],proxyGeo+'.vtx['+str(i)+']',ws=True,a=True	)
		#continue
		
		# Check intersection distance
		if len(intersectPnt) > 1:
			nextDistance = glTools.utils.mathUtils.distanceBetween(srcPt,intersectPnt[1])
			if (nextDistance-intersectDist) < boundaryOffset:
				intersectDist = (intersectDist+nextDistance)/2
		
		# Offset Point
		mc.move(	srcPt[0] + (intersectVec[0]*(intersectDist+boundaryOffset)),
					srcPt[1] + (intersectVec[1]*(intersectDist+boundaryOffset)),
					srcPt[2] + (intersectVec[2]*(intersectDist+boundaryOffset)),
					proxyGeo+'.vtx['+str(i)+']',
					ws=True,
					a=True	)

def proxyFitMeshSel(boundaryOffset=-1.0):
	'''
	'''
	print 'NOT IMPLEMENTED YET!'

def splitGeoToProxies(proxyList,meshList=[],close=True,offset=0.0):
	'''
	Generate rig proxy (lores) geometry based on an input mesh list and a list of proxy bounds objects.
	@param proxyList: List of proxy bounds objects that will be used to cut the proxy geometry
	@type proxyList: list
	@param meshList: List of meshes that the proxy geometry will be extracted from
	@type meshList: list
	@param close: Close proxy mesh border edges. 
	@type close: bool
	@param offset: The amount of normal offset to apply before creating each cut.
	@type offset: float
	'''
	# =====================
	# - Combine Mesh List -
	# =====================
	
	combinedMesh = ''
	if len(meshList) == 1:
		# Duplicate Mesh
		meshDup = mc.duplicate(meshList[0],n='duplicateMesh')[0]
		meshIntShapes = glTools.utils.shape.listIntermediates(meshDup)
		if meshIntShapes: mc.delete(meshIntShapes)
		combinedMesh = meshDup
	else:
		# Duplicate All Meshes
		meshDupList = []
		for mesh in meshList:
			if not mc.objExists(mesh):
				raise Exception('Mesh "'+mesh+'" does not exist!')
			meshDup = mc.duplicate(mesh,n='proxyGeo_TMP')[0]
			meshIntShapes = glTools.utils.shape.listIntermediates(meshDup)
			if meshIntShapes: mc.delete(meshIntShapes)
			meshDupList.append(meshDup)
		
		# Combine Duplicated Meshes
		combinedMesh = mc.polyUnite(meshDupList,ch=False,mergeUVSets=True)[0]
	
	# ====================
	# - Split To Proxies -
	# ====================
	
	proxyShapeList = []
	for proxy in proxyList:
		
		# Duplicate Mesh
		cutMesh = mc.duplicate(combinedMesh,n=proxy+'Geo')[0]
		meshIntShapes = glTools.utils.shape.listIntermediates(cutMesh)
		if meshIntShapes: mc.delete(meshIntShapes)
		
		# Cut Mesh
		proxyMesh = cutToMesh(cutMesh,proxy,offset)
		
		# !!! - Boolean Method is Very SLOW, reverting back to cut method - !!! #
		#proxyDup = mc.duplicate(proxy,n=proxy+'_dup')[0]
		#proxyMesh = cutMeshBool(cutMesh,proxyDup)
		
		# Parent Shape to Joint
		proxyJoint = mc.getAttr(proxy+'.jointProxy')
		proxyShapes = proxyParent(proxyMesh,proxyJoint)
		
		# Encode Original Geometry
		proxyGeoAttr = 'proxyGeometry'
		for proxyShape in proxyShapes:
			if not mc.objExists(proxyShape+'.'+proxyGeoAttr):
				mc.addAttr(proxyShape,ln=proxyGeoAttr,dt='string')
				mc.setAttr(proxyShape+'.'+proxyGeoAttr,str(meshList),type='string',l=True)
		
		# Append Return List
		proxyShapeList.extend(proxyShapes)
	
	# ============
	# - Clean Up -
	# ============
	
	mc.delete(combinedMesh)
	
	# =================
	# - Return Result -
	# =================
	
	return proxyShapeList

def addGeoToProxies(proxyList,meshList=[]):
	'''
	Generate rig proxy (lores) geometry based on input "add" mesh list and a list of proxy bounds objects.
	@param proxyList: List of proxy bounds objects that will be used to cut the proxy geometry
	@type proxyList: list
	@param meshList: List of meshes that the proxy geometry will be duplicated from
	@type meshList: list
	'''
	# =====================
	# - Combine Mesh List -
	# =====================
	
	combinedMesh = None
	
	if len(meshList) == 1:
		# Duplicate Mesh
		meshDup = mc.duplicate(meshList[0],n='duplicateMesh')[0]
		meshIntShapes = glTools.utils.shape.listIntermediates(meshDup)
		if meshIntShapes: mc.delete(meshIntShapes)
		combinedMesh = meshDup
	else:
		# Duplicate All Meshes
		meshDupList = []
		for mesh in meshList:
			if not mc.objExists(mesh):
				raise Exception('Mesh "'+mesh+'" does not exist!')
			meshDup = mc.duplicate(mesh,n='proxyGeo_TMP')[0]
			meshIntShapes = glTools.utils.shape.listIntermediates(meshDup)
			if meshIntShapes: mc.delete(meshIntShapes)
			meshDupList.append(meshDup)
		
		# Combine Duplicated Meshes
		combinedMesh = mc.polyUnite(meshDupList,ch=False,mergeUVSets=True)[0]
	
	# ==================
	# - Add To Proxies -
	# ==================
	
	proxyShapeList = []
	for proxy in proxyList:
		
		# Duplicate Mesh
		proxyMesh = mc.duplicate(combinedMesh,n=proxy+'Geo')[0]
		
		# Parent Shape to Joint
		proxyJoint = mc.getAttr(proxy+'.jointProxy')
		proxyShapes = proxyParent(proxyMesh,proxyJoint)
		
		# Encode Original Geometry
		proxyGeoAttr = 'proxyGeometry'
		for proxyShape in proxyShapes:
			if not mc.objExists(proxyShape+'.'+proxyGeoAttr):
				mc.addAttr(proxyShape,ln=proxyGeoAttr,dt='string')
				mc.setAttr(proxyShape+'.'+proxyGeoAttr,str(meshList),type='string',l=True)
	
	# ============
	# - Clean Up -
	# ============
	
	mc.delete(combinedMesh)
	
	# =================
	# - Return Result -
	# =================
	
	return proxyShapeList

def applyProxies(proxyList,offset=0.0):
	'''
	Generate rig proxy (lores) geometry from a list of proxy bounds objects.
	@param proxyList: List of proxy bounds objects to generate lores rig geometry from
	@type proxyList: list
	@param offset: The amount of normal offset to apply before creating each cut.
	@type offset: float
	'''
	# Check proxy list
	if not proxyList: proxyList = mc.ls('*.jointProxy',o=True)
	if not proxyList: return
	
	# Initialize Return List
	proxyShapeList = []
	
	# Print Opening Message
	print '# --------- Applying Proxies (Cutting Geometry) -'
	
	# Build Each Proxy
	for proxy in proxyList:
		
		# Check Proxy
		if not mc.objExists(proxy):
			raise Exception('Proxy bound object "'+proxy+'" does not exist!')
		if not isProxyBound(proxy):
			print ('Object "'+proxy+'" is not a valid proxy bounds object! Skipping...')
			continue
		
		# Get Cut Geometry List
		cutGeo = mc.getAttr(proxy+'.cutGeometry')
		try: cutGeo = ast.literal_eval(cutGeo)
		except: pass
		if not cutGeo:
			raise Exception('No valid cut geometry list for proxy "'+proxy+'"!')
		
		# Get Add Geometry List
		addGeo = None
		if mc.attributeQuery('addGeometry',n=proxy,ex=True):
			addGeo = mc.getAttr(proxy+'.addGeometry')
		try: addGeo = ast.literal_eval(addGeo)
		except: pass
		
		# Get Joint Proxy
		joint = mc.getAttr(proxy+'.jointProxy')
		if not mc.objExists(joint):
			raise Exception('Joint "'+joint+'" does not exist!')
		
		print '# ------------ Generating Proxy Geometry for Joint "'+joint+'"'
		print '# --------------- Cutting Geometry: '+str(cutGeo)
		if addGeo: print '# --------------- Adding Geometry: '+str(addGeo)
		
		# Cut Geometry and Add Shapes to Joint
		proxyCutShapes = splitGeoToProxies([proxy],cutGeo,close=True,offset=offset)
		proxyShapeList.extend(proxyCutShapes)
		
		# Apply Initial Shading Group
		sgAttr = 'applyInitialShadingGroup'
		if mc.attributeQuery(sgAttr,n=proxy,ex=True):
			mc.sets(proxyCutShapes,fe='initialShadingGroup')
		
		# Add Geometry Shapes to Joint
		if addGeo:
			proxyAddShapes = addGeoToProxies([proxy],addGeo)
			proxyShapeList.extend(proxyAddShapes)
			
			if mc.attributeQuery(sgAttr,n=proxy,ex=True):
				mc.sets(proxyAddShapes,fe='initialShadingGroup')
	
	# Print Closing Message
	print '# --------- Proxy Geometry Generation Complete -'
	
	# Return Result
	return proxyShapeList

def proxySkinWeights(mesh,tolerance=0.001):
	'''
	Generate skinCluster weights for a specified mesh using the matching point positions of
	the lores mesh shapes parented to the skinCluster joints.
	@param mesh: The mesh to set skinCluster weights for
	@type mesh: str
	'''
	# Get mesh vertex list
	ptArray = glTools.utils.base.getMPointArray(mesh)
	ptCount = ptArray.length()
	
	# Get skinCluster
	skinCluster = glTools.utils.skinCluster.findRelatedSkinCluster(mesh)
	influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
	
	# =========================
	# - Generate Weights List -
	# =========================
	
	# Initialize progress bar
	interupt = False
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	mc.progressBar(	gMainProgressBar,
					edit=True,
					beginProgress=True,
					isInterruptable=True,
					status='Generating Skin Weights for skinCluster "'+skinCluster+'"...',
					maxValue=len(influenceList)	)
	
	# Initialize Weight Dict
	infWtList = {}
	pt = OpenMaya.MPointOnMesh()
	for influence in influenceList:
		
		# Check progress escape
		if mc.progressBar(gMainProgressBar,q=True,isCancelled=True):
			interupt = True
			break
		mc.progressBar(	gMainProgressBar,e=True,status='Generating Skin Weights for "'+skinCluster+'" influence: '+influence)
		
		# Find mesh shapes under influence
		infShapes = mc.listRelatives(influence,s=True,type='mesh',ni=True,pa=True)
		if not infShapes:
			print('No mesh shape found under influence joint "'+influence+'"!')
			mc.progressBar(gMainProgressBar,e=True,step=1)
			continue
		
		# Initialize influence weight array
		infWtList[influence] = [0.0 for i in range(ptCount)]
		
		# For Each Shape
		for infShape in infShapes:
			
			# Initialize influence shape intersector
			infIntersector = OpenMaya.MMeshIntersector()
			
			# Run Intersector create() method
			meshObj = glTools.utils.base.getMObject(infShape)
			meshMatrix = glTools.utils.matrix.getMatrix(influence)
			infIntersector.create(meshObj,meshMatrix)
			
			# Build influence weight array
			for p in range(ptCount):
				
				# Check weight
				if infWtList[influence][p]: continue
				
				# Get distance to closest vertex
				try: infIntersector.getClosestPoint(ptArray[p],pt,tolerance)
				except: continue
				
				# Set weight if below tolerance distance
				infWtList[influence][p] = 1.0
		
		# Update progress bar
		mc.progressBar(gMainProgressBar,e=True,step=1)
	
	# End pregress bar
	mc.progressBar(gMainProgressBar,e=True,endProgress=True)
	
	# ====================
	# - Set Skin Weights -
	# ====================
	
	if not interupt:
		
		# Get component list
		mc.select(mesh)
		componentList = glTools.utils.component.getComponentStrList(mesh)
		componentSel = glTools.utils.selection.getSelectionElement(componentList,0)
		
		# Build influence index array
		infIndexArray = OpenMaya.MIntArray()
		influenceSetList = [i for i in influenceList if infWtList.keys().count(i)]
		for i in range(len(influenceSetList)):
			infIndex = glTools.utils.skinCluster.getInfluencePhysicalIndex(skinCluster,influenceSetList[i])
			infIndexArray.append(infIndex)
		
		# Build master weight array
		wtArray = OpenMaya.MDoubleArray()
		oldWtArray = OpenMaya.MDoubleArray()
		for p in range(ptCount):
			for i in range(len(influenceSetList)):
				wtArray.append(infWtList[influenceSetList[i]][p])
		
		# Get skinCluster function set
		skinFn = glTools.utils.skinCluster.getSkinClusterFn(skinCluster)
		
		# Clear Weights
		glTools.utils.skinCluster.clearWeights(mesh)
		
		# Set skinCluster weights
		skinFn.setWeights(componentSel[0],componentSel[1],infIndexArray,wtArray,False,oldWtArray)
		
		# Normalize Weights
		mc.skinPercent(skinCluster,normalize=True)
	
	# =================
	# - Return Result -
	# =================
	
	return skinCluster

def proxySkinClusters(proxyList=[]):
	'''
	Create SkinClusters from a list of proxy objects. Skin weights generated based on proxy geometry.
	@param proxyList: List of proxy objects to generate skinClusters from. If empty, use all proxy objects in the current scene.
	@type proxyList: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Proxy List
	if not proxyList:
		proxyList = mc.ls('*.proxyJoint',o=True)
	
	if not proxyList:
		raise Exception('Invalid or empty proxy list!')
	
	# ====================================
	# - Build SkinCluster Influence List -
	# ====================================
	
	influenceList = {}
	
	for proxy in proxyList:
		
		# Get Influence from Proxy
		joint = mc.getAttr(proxy+'.proxyJoint')
		
		# Get Cut Geometry List
		proxyGeoAttr = 'proxyGeometry'
		proxyGeo = mc.getAttr(proxy+'.'+proxyGeoAttr)
		try: proxyGeo = ast.literal_eval(proxyGeo)
		except: pass
		if not proxyGeo:
			raise Exception('No valid proxy geometry list for proxy "'+proxy+'"!')
		
		# For Each Geometry
		for geo in proxyGeo:
			
			# Check Influence List for Geo
			if not influenceList.has_key(geo):
				influenceList[geo] = []
			
			# Append to Influence List
			influenceList[geo].append(str(joint))
	
	# ======================
	# - Build SkinClusters -
	# ======================
	
	# For Each Geometry
	for geo in influenceList.iterkeys():
		
		# Create SkinCluster
		mc.skinCluster(geo,influenceList[geo],tsb=True,mi=1,omi=False,n=geo+'_skinCluster')
		
		# Set Initial Weights
		proxySkinWeights(geo,tolerance=0.001)
	
	# ===========
	# - Cleanup -
	# ===========
	
	dagPose = mc.ls(type='dagPose')
	if dagPose: mc.delete(dagPose)

def setCutGeometry(proxyList,cutGeo=[]):
	'''
	Set the cut geometry for the specified proxy bounds objects
	@param proxyList: List of proxy objects to set cut geometry for.
	@type proxyList: list
	@param cutGeo: The cut geometry list to set for the specified proxy bounds objects. If empty, string dialog is provided.
	@type cutGeo: list
	'''
	# Check Proxy List
	if not proxyList: return
	for proxy in proxyList:
		if not isProxyBound(proxy):
			raise Exception('Invalid proxy object "'+proxy+'"!')
		if not mc.objExists(proxy+'.cutGeometry'):
			print('Adding "cutGeometry" attribute to proxy bounds object "'+proxy+'"')
			cutGeoAttr([proxy])
	
	# Check Cut Geometry List
	if not cutGeo:
		result = mc.promptDialog(	title='Set Cut Geometry',
									message='Cut Geometry:',
									button=['Set', 'Cancel'],
									defaultButton='Set',
									cancelButton='Cancel',
									dismissString='Cancel'	)
		
		if result == 'Set':
			cutGeo = mc.promptDialog(q=True,text=True)
		if not cutGeo:
			print('No valid cut geometry list provided!')
	
	# Set Cut Geometry List
	for proxy in proxyList:
		mc.setAttr(proxy+'.cutGeometry',str(cutGeo),type='string')

def setAddGeometry(proxyList,addGeo=[]):
	'''
	Set the add geometry for the specified proxy bounds objects
	@param proxyList: List of proxy objects to set add geometry for.
	@type proxyList: list
	@param addGeo: The add geometry list to set for the specified proxy bounds objects. If empty, string dialog is provided.
	@type addGeo: list
	'''
	# Check Proxy List
	if not proxyList: return
	for proxy in proxyList:
		if not isProxyBound(proxy):
			raise Exception('Invalid proxy object "'+proxy+'"!')
		if not mc.objExists(proxy+'.addGeometry'):
			print('Adding "addGeometry" attribute to proxy bounds object "'+proxy+'"')
			addGeoAttr([proxy])
	
	# Check Add Geometry List
	if not addGeo:
		result = mc.promptDialog(	title='Set Add Geometry',
									message='Add Geometry:',
									button=['Set', 'Cancel'],
									defaultButton='Set',
									cancelButton='Cancel',
									dismissString='Cancel'	)
		
		if result == 'Set':
			addGeo = mc.promptDialog(q=True,text=True)
		if not addGeo:
			print('No valid add geometry list provided!')
	
	# Set Add Geometry List
	for proxy in proxyList:
		mc.setAttr(proxy+'.addGeometry',str(addGeo),type='string')

def setCutGeoFromSel():
	'''
	Set the cut geometry for the specified proxy bounds objects based on the current selection.
	'''
	# Define Lists
	proxyList = []
	cutGeoList = []
	sel = mc.ls(sl=True)
	
	# For Each Object in Selection
	for obj in sel:
		# Check Proxy Bounds Object
		if isProxyBound(obj):
			proxyList.append(str(obj))
		else:
			# Check Mesh
			if glTools.utils.mesh.isMesh(obj):
				cutGeoList.append(str(obj))
			else:
				print ('WARNING: Object "'+obj+'" is not a proxy bounds object or a valid mesh!')
	
	# Set Cut Geometry
	setCutGeometry(proxyList,cutGeoList)
	
	# Return Result
	print ('Proxy List -')
	for proxy in proxyList: print ('\t'+proxy)
	print ('Cut Geometry List -')
	for cutGeo in cutGeoList: print ('\t'+cutGeo)

def setAddGeoFromSel():
	'''
	Set the "add" geometry for the specified proxy bounds objects based on the current selection.
	'''
	# Define Lists
	proxyList = []
	addGeoList = []
	sel = mc.ls(sl=True)
	
	# For Each Object in Selection
	for obj in sel:
		# Check Proxy Bounds Object
		if isProxyBound(obj):
			proxyList.append(str(obj))
		else:
			# Check Mesh
			if glTools.utils.mesh.isMesh(obj):
				addGeoList.append(str(obj))
			else:
				print ('WARNING: Object "'+obj+'" is not a proxy bounds object or a valid mesh!')
	
	# Set Cut Geometry
	setAddGeometry(proxyList,addGeoList)
	
	# Return Result
	print ('Proxy List -')
	for proxy in proxyList: print ('\t'+proxy)
	print ('Add Geometry List -')
	for addGeo in addGeoList: print ('\t'+addGeo)

def setApplyInitialSGFromSel():
	'''
	Set the "initialShadingGroup" attribute for the specified proxy bounds objects based on the current selection.
	'''
	# Define Lists
	proxyList = []
	addGeoList = []
	sel = mc.ls(sl=True)
	
	# For Each Object in Selection
	for obj in sel:
		# Check Proxy Bounds Object
		if isProxyBound(obj):
			proxyList.append(str(obj))
		else:
			# Check Mesh
			if glTools.utils.mesh.isMesh(obj):
				addGeoList.append(str(obj))
			else:
				print ('WARNING: Object "'+obj+'" is not a proxy bounds object or a valid mesh!')
	
	# Set Cut Geometry
	initialShadingGroupAttr(proxyList)
	
	# Return Result
	print ('Apply initialShadingGroup for -')
	for proxy in proxyList: print ('\t'+proxy)

def cutToBoundingBox(mesh,boundingObject,offset=0.0):
	'''
	Cut a specified mesh by another geometries bounding box.
	@param mesh: The mesh to cut based on a bounding box
	@type mesh: str
	@param boundingObject: The object to use as the cut bounding box
	@type boundingObject: str
	@param offset: The amount of offset to apply before creating each cut.
	@type offset: float
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!')
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	if not mc.objExists(boundingObject):
		raise Exception('Bounding object "'+boundingObject+'" does not exist!')
	
	# =========================
	# - Get Bounding Box Info -
	# =========================
	
	bBox = glTools.utils.base.getMBoundingBox(boundingObject)
	
	center = bBox.center()
	minPt = bBox.min()
	min = [minPt[0]-offset,minPt[1]-offset,minPt[2]-offset]
	maxPt = bBox.max()
	max = [maxPt[0]+offset,maxPt[1]+offset,maxPt[2]+offset]
	
	# ============
	# - Cut Mesh -
	# ============
	
	# -Z
	mc.polyCut(mesh,ch=False,df=True,pc=[center[0],center[1],min[2]],ro=[0,0,0])
	# +Z
	mc.polyCut(mesh,ch=False,df=True,pc=[center[0],center[1],max[2]],ro=[180,0,0])
	# -X
	mc.polyCut(mesh,ch=False,df=True,pc=[min[0],center[1],center[2]],ro=[0,90,0])
	# +X
	mc.polyCut(mesh,ch=False,df=True,pc=[max[0],center[1],center[2]],ro=[0,-90,0])
	# -Y
	mc.polyCut(mesh,ch=False,df=True,pc=[center[0],min[1],center[2]],ro=[-90,0,0])
	# +Y
	mc.polyCut(mesh,ch=False,df=True,pc=[center[0],max[1],center[2]],ro=[90,0,0])

def cutToMesh(mesh,boundingObject,offset=0.0):
	'''
	Cut a specified mesh by using the faces of another mesh object.
	Mesh cut planes are defined by each face center and normal of the bounding object.
	@param mesh: The mesh to cut based on a bounding box
	@type mesh: str
	@param boundingObject: The object to use as the cut bounding box
	@type boundingObject: str
	@param offset: The amount of normal offset to apply before creating each cut.
	@type offset: float
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Mesh
	if not mc.objExists(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!')
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check Bounding Mesh
	if not mc.objExists(boundingObject):
		raise Exception('Bounding object "'+boundingObject+'" does not exist!')
	if not glTools.utils.mesh.isMesh(boundingObject):
		raise Exception('Bounding object "'+boundingObject+'" is not a valid mesh!')
	
	# ============
	# - Cut Mesh -
	# ============
	
	# Undo OFF
	mc.undoInfo(state=False)
	
	# Get face iterator
	faceIt = glTools.utils.mesh.getMeshFaceIter(boundingObject)
	
	# Cut Mesh at each Face
	faceIt.reset()
	while not faceIt.isDone():
		
		# Get Face position and normal
		pt = faceIt.center(OpenMaya.MSpace.kWorld)
		n = OpenMaya.MVector()
		faceIt.getNormal(n,OpenMaya.MSpace.kWorld)
		
		faceIt.next()
		
		# Offset Cut Point
		n.normalize()
		pt += (n*offset)
		cutPt = [pt[0],pt[1],pt[2]]
		
		# ==============================
		# - Convert Normal to Rotation -
		# ==============================
		
		up = OpenMaya.MVector(0,1,0)
		# Check upVector
		if abs(n*up) > 0.9: up = OpenMaya.MVector(0,0,1)
		# Build Rotation
		rotateMatrix = glTools.utils.matrix.buildRotation(	aimVector = (n[0],n[1],n[2]),
															upVector = (up[0],up[1],up[2]),
															aimAxis = '-z',
															upAxis = 'y'	)
		rotate = glTools.utils.matrix.getRotation(rotateMatrix)
		
		# Cut Mesh
		mc.polyCut(mesh,ch=False,df=True,pc=cutPt,ro=rotate)
		mc.polyCloseBorder(mesh,ch=False)
		
		# Set Selection
		mc.select(mesh)
	
	# Undo ON
	mc.undoInfo(state=True)
	
	# =================
	# - Return Result -
	# =================
	
	return mesh

def cutMeshBool(mesh,boundingObject):
	'''
	Cut a specified mesh by applying a boolean intersect operation.
	@param mesh: The mesh to cut based on a bounding geometry
	@type mesh: str
	@param boundingObject: The object to intersect
	@type boundingObject: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Mesh
	if not mc.objExists(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!')
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check Bounding Mesh
	if not mc.objExists(boundingObject):
		raise Exception('Bounding object "'+boundingObject+'" does not exist!')
	if not glTools.utils.mesh.isMesh(boundingObject):
		raise Exception('Bounding object "'+boundingObject+'" is not a valid mesh!')
	
	# ============
	# - Cut Mesh -
	# ============
	
	# Get Prefix
	prefix = glTools.utils.stringUtils.stripSuffix(boundingObject)
	
	# Triangulate Bounding Mesh
	mc.polyTriangulate(boundingObject,ch=False)
	
	# Cut Mesh
	cutMesh = mc.polyBoolOp(mesh,boundingObject,op=3,n=prefix+'Cut')
	if not cutMesh: raise Exception('Boolean intersection failed!')
	cutMesh = mc.rename(cutMesh[0],prefix+'Geo')
	
	# Cleanup
	mc.polyCloseBorder(cutMesh,ch=False)
	
	# =================
	# - Return Result -
	# =================
	
	return cutMesh

def freezeToJoint(proxyGeo):
	'''
	Freeze the transforms of a proxy geometry to the target joint defined by the string value of its "jointProxy" attribute.
	@param proxyGeo: Proxy geometry to freeze transforms based on an associated joint.
	@type proxyMesh: str
	'''
	# Checks
	if not isProxyBound(proxyGeo):
		raise Exception('Object "'+proxyGeo+'" is not a valid proxy bounds object!')
	
	# Get Target Joint
	joint = mc.getAttr(proxyGeo+'.jointProxy')
	# Get Proxy Parent
	proxyGrp = mc.listRelatives(proxyGeo,p=True,pa=True)[0]
	
	# Match Joint Pivot
	piv = mc.xform(joint,q=True,ws=True,rp=True)
	mc.xform(proxyGrp,ws=True,piv=piv)
	mc.xform(proxyGeo,ws=True,piv=piv)
	
	# Freeze Transforms
	grpParent = mc.listRelatives(proxyGrp,p=True,pa=True)
	mc.parent(proxyGrp,joint)
	mc.makeIdentity(proxyGrp,apply=True,t=True,r=True,s=True)
	if grpParent: mc.parent(proxyGrp,grpParent[0])
	else: mc.parent(proxyGrp,w=True)
		
	# Return Result
	return joint

def mirrorProxy(proxy,axis='x'):
	'''
	Mirror specified proxy geometry across a given axis
	@param proxy: The proxy bounds mesh to mirror
	@type proxy: str
	@param axis: The world axis to mirror across
	@type axis: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(proxy):
		raise Exception('Proxy object "'+proxy+'" does not exist!')
	if not isProxyBound(proxy):
		raise Exception('Object "'+proxy+'" is not a vlid proxy bounds object!')
	# Check Side Prefix
	if not proxy.startswith('lf') and not proxy.startswith('rt'):
		raise Exception('Proxy object "'+proxy+'" does not have a valid side prefix! ("lf_" or "rt_")')
	
	# Check Axis
	axis = axis.lower()[0]
	if not ['x','y','z'].count(axis):
		raise Exception('Invalid mirror axis! ("'+axis+'")')
	
	# ===================
	# - Duplicate Proxy -
	# ===================
	
	search = ''
	replace = ''
	if proxy.startswith('lf'):
		search = 'lf'
		replace = 'rt'
	elif proxy.startswith('rt'):
		search = 'rt'
		replace = 'lf'
	else:
		raise Exception('Proxy object "'+proxy+'" does not have a valid side prefix! ("lf_" or "rt_")')
	
	# Duplicate Proxy
	mProxy = mc.duplicate(proxy)[0]
	
	# Duplicate Proxy Group
	proxyGrp = mc.listRelatives(proxy,p=True)[0]
	mProxyGrp = mc.duplicate(proxyGrp,po=True)[0]
	
	# Rename
	mProxyNew = proxy.replace(search,replace)
	if mc.objExists(mProxyNew): mc.delete(mProxyNew)
	mProxy = mc.rename(mProxy,mProxyNew)
	mProxyGrpNew = proxyGrp.replace(search,replace)
	if mc.objExists(mProxyGrpNew): mc.delete(mProxyGrpNew)
	mProxyGrp = mc.rename(mProxyGrp,mProxyGrpNew)
	
	# Retarget Joint
	joint = mc.getAttr(proxy+'.jointProxy')
	joint = joint.replace(search,replace)
	mc.setAttr(mProxy+'.jointProxy',joint,type='string')
	
	# Retarget Cut and Add Geo
	cutGeo = mc.getAttr(proxy+'.cutGeometry')
	addGeo = '[]'
	if mc.attributeQuery('addGeometry',n=proxy,ex=True):
		addGeo = mc.getAttr(proxy+'.addGeometry')
	try:
		cutGeo = ast.literal_eval(cutGeo)
		addGeo = ast.literal_eval(addGeo)
	except:
		pass
	else:
		cutGeo = [geo.replace(search,replace) for geo in cutGeo]
		addGeo = [geo.replace(search,replace) for geo in addGeo]
		if cutGeo: mc.setAttr(mProxy+'.cutGeometry',str(cutGeo),type='string')
		if addGeo: mc.setAttr(mProxy+'.addGeometry',str(addGeo),type='string')
	
	# ================
	# - Mirror Proxy -
	# ================
	
	# Position Proxy Grp to Joint
	if mc.objExists(joint):
		mirrorCon = mc.parentConstraint(joint,mProxyGrp)
		mc.delete(mirrorCon)
	
	# Mirror Proxy
	mProxy = mc.parent(mProxy,w=True)[0]
	mc.reorder(mProxy,f=True)
	mc.makeIdentity(mProxy,apply=True,t=True,r=True,s=True)#,n=True)
	mc.xform(mProxy,ws=True,piv=[0,0,0])
	mc.setAttr(mProxy+'.s'+axis,-1.0)
	mProxy = mc.parent(mProxy,mProxyGrp)[0]
	mc.makeIdentity(mProxy,apply=True,t=True,r=True,s=True)#,n=True)
	mc.setAttr(mProxy+'.opposite',0)
	piv = mc.xform(mProxyGrp,q=True,ws=True,sp=True)
	mc.xform(mProxy,ws=True,piv=piv)
	
	# Reverse Normal
	mc.polyNormal(mProxy,ch=0,normalMode=0)
	mc.polyNormalPerVertex(mProxy,unFreezeNormal=True)
	
	# Set Colour
	glTools.utils.colorize.setColour(mProxy)
	
	# Reconnect Shading Toggle
	mc.connectAttr(mProxy+'.shading',mProxy+'.overrideShading')
	
	# =================
	# - Return Result -
	# =================
	
	return mProxy

def activeProxy(geo,joint):
	'''
	Add an "active" proxy shape to the specified joint
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(geo):
		raise Exception('Geometry "'+geo+'" does not exist!')
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	
	# ======================
	# - Duplicate Geometry -
	# ======================
	
	geoName = geo.split(':')[-1]
	prxGeo = mc.duplicate(geo)[0]
	prxGeo = mc.rename(prxGeo,geoName+'_proxy')
	
	# Delete Intermediate Shapes
	intShapes = glTools.utils.shape.listIntermediates(prxGeo)
	if intShapes: mc.delete(intShapes)
	
	# Unlock Attrs
	attrList = glTools.utils.lib.xform_list()
	for attr in attrList: mc.setAttr(prxGeo+'.'+attr,l=False)
	
	# Reset Local Space to Joint
	mc.parent(prxGeo,joint)
	mc.makeIdentity(prxGeo,apply=True,t=True,r=True,s=True)
	mc.parent(prxGeo,w=True)
	
	# Delete History
	mc.delete(prxGeo,ch=True)
	
	# =======================
	# - Connect to Original -
	# =======================
	
	proxyBS = mc.blendShape(geo,prxGeo,origin='world',n=prxGeo+'_blendShape')[0]
	proxyTarget = mc.listAttr(proxyBS+'.w',m=True)[0]
	mc.setAttr(proxyBS+'.'+proxyTarget,1.0,l=True)
	
	# =========================
	# - Parent Shape to Joint -
	# =========================
	
	proxyShapes = glTools.utils.shape.getShapes(prxGeo)
	for i in range(len(proxyShapes)):
		proxyShapes[i] = mc.parent(proxyShapes[i],joint,s=True,r=True)[0]
		glTools.utils.base.displayOverride(proxyShapes[i],overrideEnable=1,overrideDisplay=2,overrideLOD=0)
	
	# Delete old transform
	mc.delete(prxGeo)
	
	# ======================
	# - Tag Proxy Geometry -
	# ======================
	
	# Proxy Joint
	proxyJntAttr = 'proxyJoint'
	for proxyShape in proxyShapes:
		if not mc.objExists(proxyShape+'.'+proxyJntAttr):
			mc.addAttr(proxyShape,ln=proxyJntAttr,dt='string')
			mc.setAttr(proxyShape+'.'+proxyJntAttr,joint,type='string',l=True)
	
	# Proxy Geometry
	proxyGeoAttr = 'proxyGeometry'
	for proxyShape in proxyShapes:
		if not mc.objExists(proxyShape+'.'+proxyGeoAttr):
			mc.addAttr(proxyShape,ln=proxyGeoAttr,dt='string')
			mc.setAttr(proxyShape+'.'+proxyGeoAttr,geo,type='string',l=True)
	
	# =================
	# - Return Result -
	# =================
	
	return proxyShapes
