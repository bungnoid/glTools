import maya.cmds as mc
import maya.mel as mm

import glTools.utils.base
import glTools.utils.curve
import glTools.utils.mesh
import glTools.utils.stringUtils
import glTools.utils.surface

def isHairSystem(hairSystem):
	'''
	'''
	# Check object exists
	if not mc.objExists(hairSystem): return False
	
	# Check transform
	if mc.objectType(hairSystem) == 'transform':
		hairSystemShape = mc.listRelatives(hairSystem,s=True,pa=True)
		if not hairSystemShape: return False
		hairSystem = hairSystemShape[0]
	
	# Check hairSystem
	if mc.objectType(hairSystem) == 'hairSystem': return True
	
	# Return result
	return False

def isFollicle(follicle):
	'''
	'''
	# Check object exists
	if not mc.objExists(follicle): return False
	
	# Check transform
	if mc.objectType(follicle) == 'transform':
		follicleShape = mc.listRelatives(follicle,s=True,pa=True)
		if not follicleShape: return False
		follicle = follicleShape[0]
	
	# Check hairSystem
	if mc.objectType(follicle) == 'follicle': return True
	
	# Return result
	return False

def getConnectedHairSystem(hair):
	'''
	'''
	# Check object exists
	if not mc.objExists(hair): raise Exception('Object "'+hair+'" does not exist!')
	
	# Find connected follicle
	if not isFollicle():
		follicle = getConnectedFollicle(hair)
	else:
		follicle = hair
	
	# Check follicle
	if isFollicle(follicle):
		hairSystem = mc.listConnections(hair+'.outHair',s=True,d=False,type='hairSystem')
		if not hairSystem: raise Exception('Unable to determine hairSystem from follicle "'+hair+'"!')
		return hairSystem[0]
	
	# Unable to determine hair system
	raise Exception('Unable to determine hairSystem from object "'+hair+'"!')

def getConnectedFollicle(hair):
	'''
	'''
	# Check object exists
	if not mc.objExists(hair): raise Exception('Object "'+hair+'" does not exist!')
	
	# Initialize output list
	follicles = []
	
	# Check hairSystem
	if isHairSystem(hair):
		follicles = mc.listConnections(hair,s=True,d=False,type='follicle')
		
	# Check curve
	if glTools.utils.curve.isCurve(hair):
		follicles = mc.listConnections(hair,s=True,d=True,type='follicle')
		
	# Return result
	return follicles

def createHairSystem(name=''):
	'''
	Create a new hair system
	@param name: Name for the new hair system
	@type name: str
	'''
	# Check name
	if not name: name = 'hairSystem#'
	
	# Create hair system
	hairSystemShape = mc.createNode('hairSystem')
	mc.connectAttr('time1.outTime',hairSystemShape+'.currentTime',f=True)
	hairSystem = mc.listRelatives(hairSystemShape,p=True,pa=True)[0]
	hairSystem = mc.rename(hairSystem,name)
	
	# Return result
	return hairSystem

def createFollicle(surface,u,v,prefix=''):
	'''
	Create a follicle node attached to a specified nurbs surface (or polygon mesh)
	@param surface: Surface to attach follicle to
	@type surface: str
	@param u: U parameter of the surface to attach to
	@type u: float
	@param v: V parameter of the surface to attach to
	@type v: float
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Checks
	surfaceType = ''
	if glTools.utils.surface.isSurface(surface):
		surfaceType = 'nurbsSurface'
	elif glTools.utils.mesh.isMesh(surface):
		surfaceType = 'mesh'
	else: raise Exception('Invalid surface "'+surface+'"!')
	
	# Create follicle
	follicleShape = mc.createNode('follicle')
	follicle = mc.listRelatives(follicleShape,p=True,pa=True)[0]
	follicle = mc.rename(follicle,prefix+'_follicle')
	
	# Connect to surface
	mc.connectAttr(surface+'.worldMatrix[0]',follicle+'.inputWorldMatrix',f=True)
	if surfaceType == 'nurbsSurface':
		mc.connectAttr(surface+'.local',follicle+'.inputSurface',f=True)
	elif surfaceType == 'mesh':
		mc.connectAttr(surface+'.outMesh',follicle+'.inputMesh',f=True)
	
	# Set parameter values
	mc.setAttr(follicle+'.parameterU',u)
	mc.setAttr(follicle+'.parameterV',v)
	
	# Connect Translate/Rotate
	mc.connectAttr(follicle+'.outTranslate',follicle+'.translate',f=True)
	mc.connectAttr(follicle+'.outRotate',follicle+'.rotate',f=True)
	
	# Return result
	return follicle

def createFollicles(ptList,childList,follicleSurface,prefix):
	'''
	Create follicles attached to a spcified surface/mesh based on a set of input points
	@param ptList: List of point to create follicles from
	@type ptList: list
	@param childList: List of transforms to parent to follicles
	@type childList: list
	@param follicleSurface: The surface or mesh to attach the follicles to
	@type follicleSurface: str
	@param prefix: Name prefix for follicles
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Point List
	if not ptList:
		raise Exception('Invalid input point list!')
	
	# Child List
	if childList:
		if len(ptList) != len(childList):
			raise Exception('Input point and child lists have a different number of elements!')
	
	# Determine surface type
	srfType = ''
	if glTools.utils.mesh.isMesh(follicleSurface):
		srfType = 'mesh'
	elif glTools.utils.surface.isSurface(follicleSurface):
		srfType = 'nurbsSurface'
	else:
		raise Exception('Invalid surface type!')
	
	# ====================
	# - Create Follicles -
	# ====================
	
	follicleList = []
	for i in range(len(ptList)):
		
		# Get follicle position
		pt = glTools.utils.base.getPosition(ptList[i])
		
		# Determine closest surface uv
		if srfType == 'mesh':
			u,v =  glTools.utils.mesh.closestUV(follicleSurface,pt,uvSet='')
		elif srfType == 'nurbsSurface':
			u,v =  glTools.utils.surface.closestPoint(follicleSurface,pt)
		else:
			raise Exception('Invalid surface type!')
		
		# Create Follicle
		ind = glTools.utils.stringUtils.stringIndex(i+1,padding=2)
		follicle = createFollicle(follicleSurface,u,v,prefix+'_'+ind)
		follicleList.append(follicle)
		
		# Parent to follicle
		if childList: mc.parent(childList[i],follicle)
	
	# Return Result
	return follicleList

def makeDynamic(curveList,hairSystem='',connectRestPosition=True,follicleDegree=0,autoParentFollicle=False,prefix=''):
	'''
	Create dynamic curves from a list of input curves
	@param curveList: List of curves to make dynamic 
	@type curveList: list
	@param hairSystem: Hair system to attach the dynamic curve follicles to. 
	@type hairSystem: str
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Check prefix
	if prefix and not prefix.endswith('_'): prefix += '_'
		
	# Check hair system
	if not hairSystem:
		hairSystem = createHairSystem()
	else:
		if not isHairSystem(hairSystem):
			hairSystem = createHairSystem(hairSystem)
	
	# Check curves
	for curve in curveList:
		if not glTools.utils.curve.isCurve(curve):
			raise Exception('Object "'+curve+'" is not a valid nurbs curve!')
	
	# Initialize MEL variable
	mm.eval('int $ind[1] = {0};')
	
	# Create hierarchy
	hairGrp = mc.group(hairSystem,n=prefix+'grp')
	hSysGrp = mc.createNode('transform',n=prefix+'follicle_grp',p=hairGrp)
	hOutGrp = mc.createNode('transform',n=prefix+'dynCurve_grp',p=hairGrp)
	
	# Iterate over curves
	follicleList = []
	dynCurveList = []
	for curve in curveList:
		
		# Check curve
		if not mc.objectType(curve) == 'nurbsCurve':
			curveShape = mc.listRelatives(curve,s=True,ni=True,type='nurbsCurve')
			if not curveShape: raise Exception('Unable to determine curve shape from "'+curve+'"!')
			curveShape = curveShape[0]
		
		# Input Argument Values
		surface = ''
		u = 0.0
		v = 0.0
		numCVs = 0
		length = 0.0
		dynamic = 1
		
		# Create dynamic curve
		follicle = mm.eval('createHairCurveNode("'+hairSystem+'","'+surface+'",'+str(u)+','+str(v)+','+str(numCVs)+',true,true,false,false,"'+curveShape+'",'+str(length)+', $ind,"'+hSysGrp+'","'+hOutGrp+'",'+str(dynamic)+')')
		follicle = mc.rename(follicle,prefix+curve+'_follicle')
		
		# Connect Rest Position
		if connectRestPosition:
			mc.connectAttr(curve+'.worldSpace[0]',follicle+'.restPosition',f=True)
			mc.setAttr(follicle+'.restPose',3)
		
		# Follicle Degree
		if follicleDegree: mc.setAttr(follicle+'.degree',follicleDegree)
		
		# Parent Follicle
		if autoParentFollicle: follicle = mc.parent(follicle,hSysGrp)[0]
		
		# Rename dynamic curve
		dynCurve = mc.listConnections(follicle+'.outCurve',s=False,d=True)[0]
		dynCurve = mc.rename(dynCurve,prefix+curve+'_dynCurve')
		
		# Append output list
		follicleList.append(follicle)
		dynCurveList.append(dynCurve)
	
	# Return result
	return [hairGrp,follicleList,dynCurveList,hairSystem]

