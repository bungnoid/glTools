import maya.cmds as mc

import glTools.utils.base
import glTools.utils.mesh
import glTools.utils.surface

def isFollicle(follicle):
	'''
	Test if node is a valid follicle
	@param follicle: Name of follicle to query
	@type follicle: str
	'''
	# Check Object Exists
	if not mc.objExists(follicle): return False
	
	# Check Shape
	if 'transform' in mc.nodeType(follicle,i=True):
		follicleShape = mc.ls(mc.listRelatives(follicle,s=True,ni=True,pa=True) or [],type='follicle')
		if not follicleShape: return False
		follicle = follicleShape[0]
	
	# Check Follicle
	if mc.objectType(follicle) != 'follicle': return False
	
	# Return Result
	return True

def create(	targetGeo,
			parameter	= (0.5,0.5),
			uvSet		= None,
			translate   = True,
			rotate      = True,
			prefix		= None ):
	'''
	Create a new follicle attached to the specified target geometry UV point.
	@param targetGeo: Target geometry to attach follicle to
	@type targetGeo: str
	@param parameter: UV parameter to attach to
	@type parameter: list or tuple
	@param uvSet: UV set to attach to
	@type uvSet: str or None
	@param prefix: Naming prefix
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not prefix: prefix = targetGeo
	
	# Check Target Geo Type
	validType = False
	targetIsMesh = False
	targetIsSurface = False
	if glTools.utils.mesh.isMesh(targetGeo):
		validType = True
		targetIsMesh = True
	if glTools.utils.surface.isSurface(targetGeo):
		validType = True
		targetIsSurface = True
	if not validType: raise Exception('Invalid target geometry type! ('+targetGeo+')')
	
	# UV Set
	if uvSet and targetIsMesh:
		if not uvSet in mc.polyUVSet(targetGeo,q=True,auv=True):
			raise Exception('Target geometry has no UV set "'+uvSet+'"!')
	
	# ===================
	# - Create Follicle -
	# ===================
	
	follicleShape = mc.createNode('follicle')
	follicle = mc.listRelatives(follicleShape,p=True)[0]
	follicle = mc.rename(follicle,prefix+'_follicle')
	
	# Connect Translate/Rotate
	if translate:
		mc.connectAttr(follicle+'.outTranslate',follicle+'.translate',f=True)
	if rotate:
		mc.connectAttr(follicle+'.outRotate',follicle+'.rotate',f=True)
	
	# Set Parameter
	mc.setAttr(follicle+'.parameterU',parameter[0])
	mc.setAttr(follicle+'.parameterV',parameter[1])
	
	# UV Set
	if uvSet: mc.setAttr(follicle+'.mapSetName',uvSet,type='string')
	
	# ==============================
	# - Connect to Target Geometry -
	# ==============================
	
	# Connect Geometry
	if targetIsMesh: mc.connectAttr(targetGeo+'.outMesh',follicle+'.inputMesh',f=True)
	if targetIsSurface: mc.connectAttr(targetGeo+'.localSpace[0]',follicle+'.inputSurface',f=True)
	
	# Connect WorldSpace
	mc.connectAttr(targetGeo+'.worldMatrix[0]',follicle+'.inputWorldMatrix',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return follicle

def buildAtPoint(	pt,
					geo,
					uvSet		= None,
					overrideU	= None,
					overrideV	= None,
					translate   = True,
					rotate      = True,
					prefix		= None ):
	'''
	Build a follicle at the closest UV point on the specified mesh to the input point.
	@param pt: Point to create the follicle at
	@type pt: str or list
	@param geo: Geometry to attach follicle to.
	@type geo: str
	@param uvSet: UV set to attach follicle to.
	@type uvSet: str or None
	@param overrideU: Override follicle U value.
	@type overrideU: float or None
	@param overrideV: Override follicle V value.
	@type overrideV: float or None
	@param prefix: Naming prefix
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not prefix: prefix = geo
	
	# Check Target Geo Type
	validType = False
	targetIsMesh = False
	targetIsSurface = False
	if glTools.utils.mesh.isMesh(geo):
		validType = True
		targetIsMesh = True
	if glTools.utils.surface.isSurface(geo):
		validType = True
		targetIsSurface = True
	if not validType: raise Exception('Invalid target geometry type! ('+geo+')')
	
	# UV Set
	if uvSet and targetIsMesh:
		if not uvSet in mc.polyUVSet(geo,q=True,auv=True):
			raise Exception('Target geometry has no UV set "'+uvSet+'"!')
	
	# =====================================
	# - Get Point Position and Closest UV -
	# =====================================
	
	# Get Point Position
	pos = glTools.utils.base.getPosition(pt)
	
	# Get Closest UV
	parameter = [0,0]
	if targetIsMesh: parameter = list(glTools.utils.mesh.closestUV(geo,point=pos))
	if targetIsSurface: parameter = list(glTools.utils.surface.closestPoint(geo,pos))
	
	# Override UV
	if overrideU != None: parameter[0] = overrideU
	if overrideV != None: parameter[1] = overrideV
	
	# ==================
	# - Build Follicle -
	# ==================
	
	follicle = create(	geo,
						parameter	= parameter,
						uvSet		= uvSet,
						translate   = translate,
						rotate      = rotate,
						prefix		= prefix )
	
	# =================
	# - Return Result -
	# =================
	
	return follicle
