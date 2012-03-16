import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.curve
import glTools.utils.mesh
import glTools.utils.stringUtils
import glTools.utils.surface
import glTools.utils.transform

def attachToCurve(curve,transform,uValue=0.0,useClosestPoint=False,orient=False,tangentAxis='x',upAxis='y',upVector=(0,1,0),upType='none',upObject='',uAttr='uParam',prefix=''):
	'''
	Constrain a transform to a specified curve.
	@param curve: Curve to attach transform to
	@type curve: str
	@param transform: Transform to attach to curve
	@type transform: str
	@param uValue: U parameter of the point on curve to attach to
	@type uValue: float
	@param useClosestPoint: Use the closest point on the curve instead of the specified uValue
	@type useClosestPoint: bool
	@param orient: Orient transform object to curve tangent
	@type orient: bool
	@param tangentAxis: Constrained transform tangent aim axis
	@type tangentAxis: str
	@param upAxis: Constrained transform up vector axis
	@type upAxis: str
	@param upVector: Vector to use as for the constraint upVector
	@type upVector: tuple/list
	@param upType: Constraint upVector calculation method. Valid values - none, scene, vector, object, objectUp.
	@type upType: string
	@param upObject: Object whose local space will be used to calculate the orient upVector
	@type upObject: str
	@param uAttr: Attribute name on the constrained transform that will be connected to the target curve U parameter. 
	@type uAttr: str
	@param prefix: Name prefix for created nodes
	@type prefix: str
	'''
	# ===========================
	# - Build Data Dictionaries -
	# ===========================
	
	# Build axis dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	# Build upType dictionary
	upTypeDict = {'scene':0, 'object':1, 'objectUp':2, 'vector':3, 'none': 4}
	
	# ==========
	# - Checks -
	# ==========
	
	# Check curve
	if not glTools.utils.curve.isCurve(curve):
		raise Exception('Object '+curve+' is not a valid curve!!')
	
	# Check curve shape
	curveShape=''
	if mc.objectType(curve) == 'transform':
		curveShape = mc.listRelatives(curve,s=1,ni=1)[0]
	else:
		curveShape = curve
		curve = mc.listRelatives(curve,p=1)[0]
	
	# Check uValue
	minu = mc.getAttr(curve+'.minValue')
	maxu = mc.getAttr(curve+'.maxValue')
	if not useClosestPoint:
		if uValue < minu or uValue > maxu:
			raise Exception('U paramater '+str(uValue)+' is not within the parameter range for '+curve+'!!')
	
	# Check object
	if not mc.objExists(transform): raise Exception('Object '+transform+' does not exist!!')
	if not glTools.utils.transform.isTransform(transform): raise Exception('Object '+transform+' is not a valid transform!!')
	
	# Check constraint axis'
	if not axisDict.has_key(tangentAxis):
		raise Exception('Invalid tangent axis "'+tangentAxis+'"!')
	if not axisDict.has_key(upAxis):
		raise Exception('Invalid up axis "'+upAxis+'"!')
	
	# Check constraint upType
	if not upTypeDict.has_key(upType):
		raise Exception('Invalid upVector type "'+upType+'"!')
	
	# Check worldUp object
	if upObject:
		if not mc.objExists(upObject): raise Exception('WorldUp object '+upObject+' does not exist!!')
		if not glTools.utils.transform.isTransform(upObject): raise Exception('WorldUp object '+upObject+' is not a valid transform!!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(transform)
	
	# ===================
	# - Attach to Curve -
	# ===================
	
	# Get closest curve point
	if useClosestPoint:
		uPos = mc.xform(transform,q=True,ws=True,rp=True)
		uValue = glTools.utils.curve.closestPoint(curve,uPos)
	
	# Add U parameter attribute
	if not mc.objExists(transform+'.'+uAttr):
		mc.addAttr(transform,ln=uAttr,at='float',min=minu,max=maxu,dv=uValue,k=True)
	
	# Create pointOnCurveInfo node
	poc = prefix+'_pointOnCurveInfo'
	poc = mc.createNode('pointOnCurveInfo',n=poc)
	
	# Attach pointOnCurveInfo node
	mc.connectAttr(curve+'.worldSpace[0]',poc+'.inputCurve',f=True)
	mc.connectAttr(transform+'.'+uAttr,poc+'.parameter',f=True)
	
	# Create pointConstraint node
	pntCon = mc.createNode('pointConstraint',n=prefix+'_pointConstraint')
	
	# Attach pointConstraint node
	mc.connectAttr(poc+'.position',pntCon+'.target[0].targetTranslate',f=True)
	mc.connectAttr(transform+'.parentInverseMatrix[0]',pntCon+'.constraintParentInverseMatrix',f=True)
	mc.connectAttr(transform+'.rotatePivot',pntCon+'.constraintRotatePivot',f=True)
	mc.connectAttr(transform+'.rotatePivotTranslate',pntCon+'.constraintRotateTranslate',f=True)
	
	# Attach to constrained transform
	mc.connectAttr(pntCon+'.constraintTranslateX',transform+'.tx',f=True)
	mc.connectAttr(pntCon+'.constraintTranslateY',transform+'.ty',f=True)
	mc.connectAttr(pntCon+'.constraintTranslateZ',transform+'.tz',f=True)
	
	# Parent constraint node
	mc.parent(pntCon,transform)
	
	# ==========
	# - Orient -
	# ==========
	
	aimCon = ''
	if orient:
		
		# Create aimConstraint node
		aimCon = prefix+'aimConstraint'
		aimCon = mc.createNode('aimConstraint',n=aimCon)
		
		# Attach aimConstraint node
		mc.connectAttr(poc+'.tangent',aimCon+'.target[0].targetTranslate',f=True)
		mc.setAttr(aimCon+'.aimVector',*axisDict[tangentAxis])
		mc.setAttr(aimCon+'.upVector',*axisDict[upAxis])
		mc.setAttr(aimCon+'.worldUpVector',*upVector)
		mc.setAttr(aimCon+'.worldUpType',upTypeDict[upType])
		if upObject: mc.connectAttr(upObject+'.worldMatrix[0]',aimCon+'.worldUpMatrix',f=True)
		
		# Attach to constrained transform
		mc.connectAttr(aimCon+'.constraintRotateX',transform+'.rx',f=True)
		mc.connectAttr(aimCon+'.constraintRotateY',transform+'.ry',f=True)
		mc.connectAttr(aimCon+'.constraintRotateZ',transform+'.rz',f=True)
		
		# Parent constraint node
		mc.parent(aimCon,transform)
	
	# Return result
	return [poc,pntCon,aimCon]

def attachToMesh(mesh,transform,faceId=-1,useClosestPoint=False,orient=False,normAxis='x',tangentAxis='y',prefix=''):
	'''
	Attach a transform to a s[ecified mesh object
	@param mesh: Mesh to attach to
	@type mesh: str
	@param transform: Transform object to attach to surface
	@type transform: str
	@param faceId: Attach transform to this mesh face
	@type faceId: int
	@param useClosestPoint: Use the closest point on the mesh instead of the specified face
	@type useClosestPoint: bool
	@param orient: Orient transform object to mesh face normal
	@type orient: bool
	@param normAxis: Transform axis that will be aimed along the face normal
	@type normAxis: str
	@param tangentAxis: Transform axis that will be aligned with the face tangent
	@type tangentAxis: str
	@param prefix: Name prefix string for all builder created nodes
	@type prefix: str
	'''
	# Create axis value dictionary
	axis = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh): raise Exception('Object '+mesh+' is not a valid mesh!!')
	
	# Check transform
	if not mc.objExists(transform): raise Exception('Object '+transform+' does not exist!!')
	if not glTools.utils.transform.isTransform(transform): raise Exception('Object '+transform+' is not a valid transform!!')
	pos = mc.xform(transform,q=True,ws=True,rp=True)
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(transform)
	
	# Create int pointer for mesh iter classes
	indexUtil = OpenMaya.MScriptUtil()
	indexUtil.createFromInt(0)
	indexUtilPtr = indexUtil.asIntPtr()
	
	# Check closest face
	if useClosestPoint: faceId = glTools.utils.mesh.closestFace(mesh,pos)
	
	# Get MItMeshPolygon
	faceIter = glTools.utils.mesh.getMeshFaceIter(mesh)
	
	# Get face
	faceIter.setIndex(faceId,indexUtilPtr)
	
	# Get face edge list
	edgeIntList = OpenMaya.MIntArray()
	faceIter.getEdges(edgeIntList)
	edgeList = list(edgeIntList)
	
	# Get opposing edges
	edgeIter = glTools.utils.mesh.getMeshEdgeIter(mesh)
	edge1 = edgeList[0]
	edgeIter.setIndex(edge1,indexUtilPtr)
	edgePos = edgeIter.center(OpenMaya.MSpace.kWorld)
	# Find furthest edge
	edge2 = -1
	dist = 0.0
	for i in edgeList[1:]:
		edgeIter.setIndex(i,indexUtilPtr)
		eDist = edgePos.distanceTo(edgeIter.center(OpenMaya.MSpace.kWorld))
		if eDist > dist:
			edge2 = i
			dist = eDist
	
	# Check opposing edge
	if not (edge2+1): raise Exception('Unable to determine opposing face edges!!')
	
	# Create mesh edge loft
	edge1_cme = prefix+'_edge01_curveFromMeshEdge'
	edge1_cme = mc.createNode('curveFromMeshEdge',n=edge1_cme)
	mc.connectAttr(mesh+'.worldMesh[0]',edge1_cme+'.inputMesh',f=True)
	mc.setAttr(edge1_cme+'.edgeIndex[0]',edge1)
	edge2_cme = prefix+'_edge02_curveFromMeshEdge'
	edge2_cme = mc.createNode('curveFromMeshEdge',n=edge2_cme)
	mc.connectAttr(mesh+'.worldMesh[0]',edge2_cme+'.inputMesh',f=True)
	mc.setAttr(edge2_cme+'.edgeIndex[0]',edge2)
	mesh_lft = prefix+'_loft'
	mesh_lft = mc.createNode('loft',n=mesh_lft)
	mc.connectAttr(edge1_cme+'.outputCurve',mesh_lft+'.inputCurve[0]',f=True)
	mc.connectAttr(edge2_cme+'.outputCurve',mesh_lft+'.inputCurve[1]',f=True)
	mc.setAttr(mesh_lft+'.degree',1)
	
	# Create temporary surface
	tempSrf = mc.createNode('nurbsSurface')
	mc.connectAttr(mesh_lft+'.outputSurface',tempSrf+'.create')
	tempSrf = mc.listRelatives(tempSrf,p=True)[0]
	# Attach to lofted surface
	surfAttach = attachToSurface(surface=tempSrf,transform=transform,useClosestPoint=True,orient=orient,uAxis=tangentAxis,vAxis=normAxis,prefix=prefix)
	# Set aim constraint offset to orient to normal
	offsetVal = -90.0
	if len(tangentAxis)==2: offsetVal = 90.0
	offsetAx = str.upper(tangentAxis[-1])
	mc.setAttr(surfAttach[2]+'.offset'+offsetAx,offsetVal)
	
	# Bypass temporary nurbsSurface node
	mc.connectAttr(mesh_lft+'.outputSurface',surfAttach[0]+'.inputSurface',f=True)
	# Delete temporary surface
	mc.delete(tempSrf)
	
	# Return result
	return (surfAttach[0],surfAttach[1],surfAttach[2],mesh_lft,edge1_cme,edge2_cme)

def attachToSurface(surface,transform,uValue=0.0,vValue=0.0,useClosestPoint=False,orient=False,uAxis='x',vAxis='y',uAttr='uCoord',vAttr='vCoord',alignTo='u',prefix=''):
	'''
	Constrain a transform to a specified surface.
	@param surface: Nurbs surface to attach to
	@type surface: str
	@param transform: Transform object to attach to surface
	@type transform: str
	@param uValue: U parameter of the point on surface to attach to
	@type uValue: float
	@param vValue: V parameter of the point on surface to attach to
	@type vValue: float
	@param useClosestPoint: Use the closest point on the surface instead of the specified uv parameter
	@type useClosestPoint: bool
	@param orient: Orient transform object to surface tangents
	@type orient: bool
	@param uAxis: Transform axis that will be aligned to the surface U direction
	@type uAxis: str
	@param vAxis: Transform axis that will be aligned to the surface V direction
	@type vAxis: str
	@param uAttr: Attribute name that will control the target uCoordinate for the constraint
	@type uAttr: str
	@param vAttr: Attribute name that will control the target vCoordinate for the constraint
	@type vAttr: str
	@param alignTo: Select which tangent direction the constrained transform will align to
	@type alignTo: str
	@param prefix: Name prefix string for all builder created nodes
	@type prefix: str
	'''
	# Create axis value dictionary
	axis = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	# Check surface
	if not glTools.utils.surface.isSurface(surface):
		raise Exception('Surface '+surface+' is not a valid nurbsSurface!!')
	# Check surface shape
	surfaceShape = ''
	if mc.objectType(surface) == 'transform':
		surfaceShape = mc.listRelatives(surface,s=1,ni=1)[0]
	else:
		surfaceShape = surface
		surface = mc.listRelatives(surface,p=1)[0]
	
	# Check uValue
	minu = mc.getAttr(surface+'.minValueU')
	maxu = mc.getAttr(surface+'.maxValueU')
	minv = mc.getAttr(surface+'.minValueV')
	maxv = mc.getAttr(surface+'.maxValueV')
	if not useClosestPoint:
		if uValue < minu or uValue > maxu: raise Exception('U paramater '+str(uValue)+' is not within the parameter range for '+surface+'!!')
		if vValue < minv or vValue > maxv: raise Exception('V paramater '+str(vValue)+' is not within the parameter range for '+surface+'!!')
	
	# Check transform
	if not mc.objExists(transform): raise Exception('Object '+transform+' does not exist!!')
	if not glTools.utils.transform.isTransform(transform): raise Exception('Object '+transform+' is not a valid transform!!')
	# Check closest point
	if useClosestPoint: 
		uv = glTools.utils.surface.closestPoint(surface,mc.xform(transform,q=True,ws=True,rp=True))
		uValue = uv[0]
		vValue = uv[1]
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(transform)
	
	# Attach to surface
	# ==
	
	# Add parameter attributes
	if not mc.objExists(transform+'.'+uAttr):
		mc.addAttr(transform,ln=uAttr,at='float',min=minu,max=maxu,dv=uValue,k=True)
	if not mc.objExists(transform+'.'+vAttr):
		mc.addAttr(transform,ln=vAttr,at='float',min=minv,max=maxv,dv=vValue,k=True)
	
	# Create pointOnSurfaceInfo node
	pos = mc.createNode('pointOnSurfaceInfo',n=prefix+'_pointOnSurfaceInfo')
	# Attach pointOnSurfaceInfo node
	mc.connectAttr(surface+'.worldSpace[0]',pos+'.inputSurface',f=True)
	mc.connectAttr(transform+'.'+uAttr,pos+'.parameterU',f=True)
	mc.connectAttr(transform+'.'+vAttr,pos+'.parameterV',f=True)
	
	# Create pointConstraint node
	pntCon = mc.createNode('pointConstraint',n=prefix+'_pointConstraint')
	# Attach pointConstraint node
	mc.connectAttr(pos+'.position',pntCon+'.target[0].targetTranslate',f=True)
	mc.connectAttr(transform+'.parentInverseMatrix[0]',pntCon+'.constraintParentInverseMatrix',f=True)
	mc.connectAttr(transform+'.rotatePivot',pntCon+'.constraintRotatePivot',f=True)
	mc.connectAttr(transform+'.rotatePivotTranslate',pntCon+'.constraintRotateTranslate',f=True)
	mc.connectAttr(pntCon+'.constraintTranslateX',transform+'.tx',f=True)
	mc.connectAttr(pntCon+'.constraintTranslateY',transform+'.ty',f=True)
	mc.connectAttr(pntCon+'.constraintTranslateZ',transform+'.tz',f=True)
	mc.parent(pntCon,transform)
	
	# Orient
	aimCon = ''
	if orient:
		# Get axis vaules
		uAx = axis[uAxis]
		vAx = axis[vAxis]
		# Create aimConstraint node
		aimCon = mc.createNode('aimConstraint',n=prefix+'_aimConstraint')
		# Attach aimConstraint node
		if alignTo == 'u':
			mc.connectAttr(pos+'.tangentU',aimCon+'.target[0].targetTranslate',f=True)
			mc.connectAttr(pos+'.tangentV',aimCon+'.worldUpVector',f=True)
			mc.setAttr(aimCon+'.aimVector',uAx[0],uAx[1],uAx[2])
			mc.setAttr(aimCon+'.upVector',vAx[0],vAx[1],vAx[2])
		else:
			mc.connectAttr(pos+'.tangentV',aimCon+'.target[0].targetTranslate',f=True)
			mc.connectAttr(pos+'.tangentU',aimCon+'.worldUpVector',f=True)
			mc.setAttr(aimCon+'.aimVector',vAx[0],vAx[1],vAx[2])
			mc.setAttr(aimCon+'.upVector',uAx[0],uAx[1],uAx[2])
		mc.connectAttr(aimCon+'.constraintRotateX',transform+'.rx',f=True)
		mc.connectAttr(aimCon+'.constraintRotateY',transform+'.ry',f=True)
		mc.connectAttr(aimCon+'.constraintRotateZ',transform+'.rz',f=True)
		mc.parent(aimCon,transform)
	
	# Return result
	return [pos,pntCon,aimCon]
