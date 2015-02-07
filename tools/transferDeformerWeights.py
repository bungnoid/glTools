import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.component
import glTools.utils.deformer
import glTools.utils.mesh
import glTools.utils.transform

def closestPointWeights(pts,mesh,tol=0.001):
	'''
	Build closest point weights array.
	@param pts: List of input points to calculate weights from
	@type pts: list
	@param mesh: Reference mesh to calculate weights from
	@type mesh: str
	@param tol: Weight value tolerance. Values below this amount will be ignored.
	@type tol: float
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	if glTools.utils.transform.isTransform(mesh):
		meshShape = mc.listRelatives(mesh,s=True,ni=True,pa=True)
		if not meshShape: raise Exception('Unable to get shape from mesh!')
		meshShape = meshShape[0]
	else:
		meshShape = mesh
		mesh = mc.listRelatives(meshShape,p=True)[0]
	
	# =========================
	# - Build MeshIntersector -
	# =========================
	
	meshPt = OpenMaya.MPointOnMesh()
	meshIntersector = OpenMaya.MMeshIntersector()
	meshObj = glTools.utils.base.getMObject(meshShape)
	meshMat = glTools.utils.transform.getMatrix(mesh)
	meshFn = OpenMaya.MFnMesh(meshObj)
	meshIntersector.create(meshObj,meshMat)
	
	# =======================
	# - Build Point Weights -
	# =======================
	
	# Initialize Float Pointers for Barycentric Coords
	uUtil = OpenMaya.MScriptUtil()
	vUtil = OpenMaya.MScriptUtil()
	uPtr = uUtil.asFloatPtr()
	vPtr = vUtil.asFloatPtr()
	
	wt = []
	for i in range(len(pts)):
		
		# Get Target Point
		pt = glTools.utils.base.getMPoint(pts[i])
		
		# Get Closest Point Data
		meshIntersector.getClosestPoint(pt,meshPt)
		meshPt.getBarycentricCoords(uPtr,vPtr)
		u = OpenMaya.MScriptUtil(uPtr).asFloat()
		v = OpenMaya.MScriptUtil(vPtr).asFloat()
		baryWt = [u,v,1.0-(u+v)]
		
		# Get Triangle Vertex IDs
		idUtil = OpenMaya.MScriptUtil()
		idPtr = idUtil.asIntPtr()
		meshFn.getPolygonTriangleVertices(meshPt.faceIndex(),meshPt.triangleIndex(),idPtr)
		
		# Remove Small Values (Tolerance)
		for n in range(3):
			if baryWt[n] > (1.0-tol):
				baryWt[n] = 1.0
				baryWt[n-1] = 0.0
				baryWt[n-2] = 0.0
				break
			if baryWt[n] < tol:
				if baryWt[n-1] > baryWt[n-2]: baryWt[n-1] += baryWt[n]
				else: baryWt[n-2] += baryWt[n]
				baryWt[n] = 0.0
		
		# Build Point Weights
		ptWt = {}
		for n in range(3):
			if baryWt[n] > tol:
				ptWt[OpenMaya.MScriptUtil().getIntArrayItem(idPtr,n)] = baryWt[n]
		wt.append(ptWt)
	
	# =================
	# - Return Result -
	# =================
	
	return wt

def mirrorWeights(	wts,
					mesh,
					axis		= 'x',
					flip		= False,
					posToNeg	= True,
					deformer	= None,
					deformedGeo	= None ):
	'''
	Mirror weights values on a specified mesh.
	@param wts: Weight values to mirror
	@type wts: list
	@param mesh: Mesh to mirror weights
	@type mesh: str
	@param axis: Mirror axis
	@type axis: str
	@param flip: Flip weights
	@type flip: bool
	@param posToNeg: Mirror from positive to negative position across axis
	@type posToNeg: bool
	@param deformer: Deformer to apply weights to.
	@type deformer: str on None
	@param deformedGeo: Deformed mesh to apply weights to
	@type deformedGeo: str on None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object '+mesh+' is not a polygon mesh!')
	
	# Check Axis
	if not axis in 'xyz': raise Exception('Invalid axis value!')
	
	# ===================
	# - Get Mesh Points -
	# ===================
	
	pts = glTools.utils.mesh.getPoints(mesh)
	
	# Check Point Count
	if len(pts) != len(wts):
		raise Exception('Weights/points mis-match!')
	
	# Mirror Points
	if axis == 'x': pts = [[-i[0],i[1],i[2]] for i in pts]
	if axis == 'y': pts = [[i[0],-i[1],i[2]] for i in pts]
	if axis == 'z': pts = [[i[0],i[1],-i[2]] for i in pts]
	
	# ==================
	# - Mirror Weights -
	# ==================
	
	m_wts = []
	pt_wts = closestPointWeights(pts,mesh,tol=0.001)
	for i in range(len(wts)):
		
		# Check Skipped Mirror Weights
		if not flip:
			axisVal = pts['xyz'.index(axis)]*-1
			if posToNeg and (axisVal > 0):
				m_wts.append(wts[i])
				continue
			if not posToNeg and (axisVal < 0):
				m_wts.append(wts[i])
				continue
		
		# Calculate Mirror Weight
		m_wts.append(0.0)
		for n in pt_wts[i]:
			m_wts[-1] += wts[n] * pt_wts[i][n]
	
	# =================
	# - Apply Weights -
	# =================
	
	if deformer: glTools.utils.deformer.setWeights(deformer,m_wts,deformedGeo)
	
	# =================
	# - Return Result -
	# =================
	
	return m_wts

def transferWeights(	wts,
						srcGeo,
						dstGeo,
						deformer	= None,
						deformedGeo	= None ):
	'''
	Transfer weights from a source geometry to a destination geometry.
	@param wts: Weight values to mirror
	@type wts: list
	@param srcGeo: The geometry that you want to transfer weights from
	@type srcGeo: str
	@param dstGeo: The geometry that you want to transfer weights to.
	@type dstGeo: str
	@param deformer: Deformer to apply weights to.
	@type deformer: str on None
	@param deformedGeo: Deformed mesh to apply weights to
	@type deformedGeo: str on None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Mesh
	if not glTools.utils.mesh.isMesh(srcGeo):
		raise Exception('Source geometry '+srcGeo+' is not a polygon mesh!')
	if not glTools.utils.mesh.isMesh(dstGeo):
		raise Exception('Destination geometry '+dstGeo+' is not a polygon mesh!')
		
	# ===================
	# - Get Mesh Points -
	# ===================
	
	pts = glTools.utils.mesh.getPoints(dstGeo)
	
	# ====================
	# - Transfer Weights -
	# ====================
	
	t_wts = []
	pt_wts = closestPointWeights(pts,srcGeo,tol=0.001)
	for i in range(len(pt_wts)):
		t_wts.append(0)
		for n in pt_wts[i]:
			t_wts[-1] += wts[n] * pt_wts[i][n]
	
	# =================
	# - Apply Weights -
	# =================
	
	if deformer: glTools.utils.deformer.setWeights(deformer,t_wts,deformedGeo)
	
	# =================
	# - Return Result -
	# =================
	
	return t_wts

