import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.curve
import glTools.utils.component
import glTools.utils.matrix
import glTools.utils.shape
import glTools.utils.stringUtils

import math

class UserInputError( Exception ): pass

def isSurface(surface):
	'''
	Check if the specified object is a nurbs surface or transform parent of a surface
	@param surface: Object to query
	@type surface: str
	'''
	# Check object exists
	if not mc.objExists(surface): return False
	# Check shape
	if mc.objectType(surface) == 'transform': surface = mc.listRelatives(surface,s=True,ni=True)[0]
	if mc.objectType(surface) != 'nurbsSurface': return False
	
	# Return result
	return True

def getSurfaceFn(surface):
	'''
	Create an MFnNurbsSurface class object from the specified nurbs surface
	@param surface: Surface to create function class for
	@type surface: str
	'''
	# Checks
	if not isSurface(surface): raise UserInputError('Object '+surface+' is not a valid surface!')
	if mc.objectType(surface) == 'transform':
		surface = mc.listRelatives(surface,s=True,ni=True)[0]
	
	# Get MFnNurbsSurface
	selection = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(surface,selection)
	surfacePath = OpenMaya.MDagPath()
	selection.getDagPath(0,surfacePath)
	surfaceFn = OpenMaya.MFnNurbsSurface()
	surfaceFn.setObject(surfacePath)
	
	# Return result
	return surfaceFn

def chordLength(surface,param=0.0,direction='u'):
	'''
	Return the length of a surface isoparm given a parameter and a direction
	@param surface: Surface to query closest point from
	@type surface: str
	@param param: The parameter on the surface to query length of
	@type param: float
	@param direction: Direction along the surface to measure length of
	@type direction: str
	'''
	# Check surface
	if not isSurface(surface): raise UserInputError('Object '+surface+' is not a valid surface!')
	# Duplicate surface curve
	curve = mc.duplicateCurve(surface+'.'+direction+'['+str(param)+']',ch=0,rn=0,local=0)
	# Measure curve length
	length = mc.arclen(curve[0])
	# Cleanup
	mc.delete(curve)
	# Return result
	return length

def closestPoint(surface,pos=(0,0,0)):
	'''
	Return closest point on surface to target position
	@param surface: Surface to query closest point from
	@type surface: str
	@param pos: Position to query surface from
	@type pos: tuple/list
	'''
	# Check surface
	if not isSurface(surface): raise UserInputError('Object '+surface+' is not a valid surface!')
	
	# Get surface point world position
	pos = OpenMaya.MPoint(pos[0],pos[1],pos[2],1.0)
	
	# Get surface function set
	surfFn = getSurfaceFn(surface)
	
	# Get uCoord and vCoord pointer objects
	uCoord = OpenMaya.MScriptUtil()
	uCoord.createFromDouble(0.0)
	uCoordPtr = uCoord.asDoublePtr()
	vCoord = OpenMaya.MScriptUtil()
	vCoord.createFromDouble(0.0)
	vCoordPtr = vCoord.asDoublePtr()
	
	# get closest uCoord to edit point position
	surfFn.closestPoint(pos,uCoordPtr,vCoordPtr,True,0.0001,OpenMaya.MSpace.kWorld)
	return (OpenMaya.MScriptUtil(uCoordPtr).asDouble(),OpenMaya.MScriptUtil(vCoordPtr).asDouble())

def snapPtsToSurface(surface,pointList):
	'''
	@param surface: Nurbs surface to snap points to
	@type surface: str
	@param pointList: Point to snap to the specified surface
	@type pointList: list
	'''
	# Check surface
	if not isSurface(surface): raise UserInputError('Object '+surface+' is not a valid surface!')
	
	# Check points
	pointList = mc.ls(pointList,fl=True)
	
	# Transform types
	transform = ['transform','joint','ikHandle','effector']
	
	# Snap points
	for pt in pointList:
		# Check Transform
		if transform.count(mc.objectType(pt)):
			snapToSurface(surface,pt,0.0,0.0,True,snapPivot=False)
			continue
		# Move Point
		pos = mc.pointPosition(pt)
		(uParam,vParam) = closestPoint(surface,pos)
		sPt = mc.pointOnSurface(surface,u=uParam,v=vParam,position=True)
		mc.move(sPt[0],sPt[1],sPt[2],pt,ws=True,a=True)
	
def locatorSurface(surface,controlPoints=[],locatorScale=0.075,prefix=''):
	'''
	Drive the control point positions of a surface with a set of control locators
	@param surface: Input surface to connect locators positions to
	@type surface: str
	@param controlPoints: List of control points to be driven by locators. If left as default (None), all control points will be connected.
	@type controlPoints: list
	@param locatorScale: Scale of the locators relative to the area of the surface
	@type locatorScale: float
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Check surface
	if not glTools.utils.surface.isSurface(surface):
		raise UserInputError('Object '+surface+' is not a valid surface!')
	if mc.objectType(surface) == 'transform':
		surface = mc.listRelatives(surface,s=True,ni=True)[0]
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(surface)
	
	# Calculate locator scale
	locatorScale *= math.sqrt(glTools.utils.surface.surfaceArea(surface))
	
	# Get Control Points
	if not controlPoints:
		controlPoints = glTools.utils.component.getComponentIndexList(surface)[surface]
	else:
		controlPoints = glTools.utils.component.getComponentIndexList(controlPoints)[surface]
	
	# Create locators and connect to control points
	locatorList = []
	for cv in controlPoints:
		# Get index (string)
		ind = glTools.utils.component.getSingleIndex(surface,cv)
		indStr = glTools.utils.stringUtils.stringIndex(ind,2)
		# Create locator
		loc = prefix+'_cv'+indStr+'_loc'
		loc = mc.spaceLocator(n=loc)[0]
		locatorList.append(loc)
		mc.setAttr(loc+'.localScale',locatorScale,locatorScale,locatorScale)
		
		# Get control point world position
		pos = mc.pointPosition(surface+'.cv['+str(cv[0])+']['+str(cv[1])+']')
		mc.setAttr(loc+'.t',pos[0],pos[1],pos[2])
		mc.makeIdentity(loc,apply=True,t=1,r=1,s=1,n=0)
		# Connect locator position to control point
		mc.connectAttr(loc+'.worldPosition[0]',surface+'.controlPoints['+str(ind)+']')
		
	return locatorList

def surfaceArea(surface,worldSpace=True):
	'''
	Calculates the surface area of a specified nurbs surface.
	@param surface: Nurbs surface to calculate the surface area for
	@type surface: str
	@param worldSpace: Calculate the surface area in world or local space units
	@type worldSpace: bool
	'''
	# Check Surface
	if not mc.objExists(surface): raise UserInputError('Object '+surface+' does not exist!')
	if mc.objectType(surface) == 'transform':
		surfaceShape = mc.listRelatives(surface,s=True,ni=True)[0]
		if mc.objectType(surfaceShape) != 'nurbsSurface':
			raise UserInputError('Object '+surface+' is not a valid nurbs surface!')
		surface = surfaceShape
	
	# Get MFnNurbsSurface
	surfaceFn = getSurfaceFn(surface)
	# Get surface area
	area = 0.0
	if worldSpace: area = surfaceFn.area(OpenMaya.MSpace.kWorld)
	else: area = surfaceFn.area(OpenMaya.MSpace.kObject)
	
	# Return result
	return area

def snapToSurface(surface,obj,uValue=0.0,vValue=0.0,useClosestPoint=False,snapPivot=False):
	'''
	Snap an object (or transform pivot) to a specified point on a surface.
	@param surface: Curve to snap to
	@type surface: str
	@param obj: Object to move to point on surface
	@type obj: str
	@param uValue: U Paramater value of the surface to snap to
	@type uValue: float
	@param vValue: V Paramater value of the surface to snap to
	@type vValue: float
	@param useClosestPoint: Use the closest point on the surface instead of the specified uv parameter
	@type useClosestPoint: bool
	@param snapPivot: Move only the objects pivot to the surface point
	@type snapPivot: bool
	'''
	# Check surface
	if not isSurface(surface): raise UserInputError('Object '+surface+' is not a valid surface!!')
	
	# Check uValue/vValue
	minu = mc.getAttr(surface+'.minValueU')
	maxu = mc.getAttr(surface+'.maxValueU')
	minv = mc.getAttr(surface+'.minValueV')
	maxv = mc.getAttr(surface+'.maxValueV')
	
	# Closest Point
	if useClosestPoint:
		pos = mc.xform(obj,q=True,ws=True,rp=True)
		(uValue,vValue) = closestPoint(surface,pos)
	# Verify surface parameter
	if uValue < minu or uValue > maxu: raise UserInputError('U paramater '+str(uValue)+' is not within the U parameter range for '+surface+'!!')
	if vValue < minv or vValue > maxv: raise UserInputError('V paramater '+str(vValue)+' is not within the V parameter range for '+surface+'!!')
	
	# Get surface point position
	pnt = mc.pointPosition(surface+'.uv['+str(uValue)+']['+str(vValue)+']')
	
	# Snap to Curve
	piv = mc.xform(obj,q=True,ws=True,rp=True)
	if snapPivot: mc.xform(obj,piv=pnt,ws=True)
	else: mc.move(pnt[0]-piv[0],pnt[1]-piv[1],pnt[2]-piv[2],obj,r=True,ws=True)

def orientToSurface(surface,obj,uValue=0.0,vValue=0.0,useClosestPoint=False,tangentUAxis='x',tangentVAxis='y',alignTo='u'):
	'''
	Orient object to a specified point on a surface.
	@param surface: Surface to orient object to
	@type surface: str
	@param obj: Object to orient
	@type obj: str
	@param uValue: U Paramater value of the surface to orient to
	@type uValue: float
	@param vValue: V Paramater value of the surface to orient to
	@type vValue: float
	@param useClosestPoint: Use the closest point on the surface instead of the specified uv parameter
	@type useClosestPoint: bool
	@param tangentUAxis: Basis axis that will be derived from the U tangent of the surface point
	@type tangentUAxis: str
	@param tangentVAxis: Basis axis that will be derived from the V tangent of the surface point
	@type tangentVAxis: str
	@param upAxis: Basis axis that will be derived from the upVector
	@type upAxis: str
	'''
	# Check surface
	if not isSurface(surface): raise UserInputError('Object '+surface+' is not a valid surface!!')
	# Check Obj
	transform = ['transform','joint','ikHandle','effector']
	if not transform.count(mc.objectType(obj)):
		raise UserInputError('Object '+obj+' is not a valid transform!!')
	# Check uValue/vValue
	minu = mc.getAttr(surface+'.minValueU')
	maxu = mc.getAttr(surface+'.maxValueU')
	minv = mc.getAttr(surface+'.minValueV')
	maxv = mc.getAttr(surface+'.maxValueV')
	# Closest Point
	if useClosestPoint:
		pos = mc.xform(obj,q=True,ws=True,rp=True)
		(uValue,vValue) = closestPoint(surface,pos)
	# Verify surface parameter
	if uValue < minu or uValue > maxu: raise UserInputError('U paramater '+str(uValue)+' is not within the U parameter range for '+surface+'!!')
	if vValue < minv or vValue > maxv: raise UserInputError('V paramater '+str(uValue)+' is not within the V parameter range for '+surface+'!!')
	
	# Check object
	if not mc.objExists(obj): raise UserInputError('Object '+obj+' does not exist!!')
	rotateOrder = mc.getAttr(obj+'.ro')
	
	# Get tangents at surface point
	tanU = mc.pointOnSurface(surface,u=uValue,v=vValue,ntu=True)
	tanV = mc.pointOnSurface(surface,u=uValue,v=vValue,ntv=True)
	
	# Build rotation matrix
	aimVector = tanU
	if alignTo == 'v': aimVector = tanV
	upVector = tanV
	if alignTo == 'v': upVector = tanU
	aimAxis = tangentUAxis
	if alignTo == 'v': aimAxis = tangentVAxis
	upAxis = tangentVAxis
	if alignTo == 'v': upAxis = tangentUAxis
	
	mat = glTools.utils.matrix.buildRotation(aimVector,upVector,aimAxis,upAxis)
	rot = glTools.utils.matrix.getRotation(mat,rotateOrder)
	
	# Orient object to surface
	mc.rotate(rot[0],rot[1],rot[2],obj,a=True,ws=True)

def rebuild(surface,spansU=0,spansV=0,fullRebuildU=False,fullRebuildV=False,rebuildUfirst=True,replaceOrig=False):
	'''
	Do brute force surface rebuild for even parameterization
	@param surface: Nurbs surface to rebuild
	@type surface: str
	@param spansU: Number of spans along U. If 0, keep original value.
	@type spansU: int
	@param spansV: Number of spans along V. If 0, keep original value.
	@type spansV: int
	@param replaceOrig: Replace original surface, or create new rebuilt surface.
	@type replaceOrig: bool
	'''
	# Check surface
	if not isSurface(surface):
		raise Exception('Object "'+surface+'" is not a valid surface!')
	
	# Check spans
	if not spansU: spansU = mc.getAttr(surface+'.spansU')
	if not spansV: spansV = mc.getAttr(surface+'.spansV')
	
	# -------------
	# - Rebuild U -
	
	# Get V range
	if rebuildUfirst:
		dir = 'u'
		opp = 'v'
		spans = spansU
		min = mc.getAttr(surface+'.minValueV')
		max = mc.getAttr(surface+'.maxValueV')
	else:
		dir = 'v'
		opp = 'u'
		spans = spansV
		min = mc.getAttr(surface+'.minValueU')
		max = mc.getAttr(surface+'.maxValueU')
	val = min + (max - min) * 0.5
	
	# Caluculate surface length
	iso_crv = mc.duplicateCurve(surface+'.'+opp+'['+str(val)+']',ch=0,rn=0,local=0)[0]
	iso_len = mc.arclen(iso_crv)
	iso_inc = iso_len / spans
	
	# Get spaced isoparm list
	curveFn = glTools.utils.curve.getCurveFn(iso_crv)
	iso_list = [surface+'.'+dir+'['+str(curveFn.findParamFromLength(iso_inc*i))+']' for i in range(spans+1)]
	mc.delete(iso_crv)
	
	# Check full rebuild
	if fullRebuildV:
		# Extract isoparm curves
		iso_crv_list = [mc.duplicateCurve(iso,ch=False,rn=False,local=False)[0] for iso in iso_list]
		# Rebuild isoparm curves
		for iso_crv in iso_crv_list:
			mc.rebuildCurve(iso_crv,ch=False,rpo=True,rt=0,end=1,kr=0,kcp=0,kep=1,kt=1,s=0,d=3,tol=0)
		# Loft final surface
		int_surface = mc.loft(iso_crv_list,ch=0,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0,rsn=True)[0]
		# Delete intermediate curves
		mc.delete(iso_crv_list)
	else:
		# Loft intermediate surface
		int_surface = mc.loft(iso_list,ch=0,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0,rsn=True)[0]
	
	# -------------
	# - Rebuild V -
	
	# Get V range (intermediate surface)
	if rebuildUfirst:
		dir = 'u'
		opp = 'v'
		spans = spansV
		min = mc.getAttr(int_surface+'.minValueU')
		max = mc.getAttr(int_surface+'.maxValueU')
	else:
		dir = 'v'
		opp = 'u'
		spans = spansU
		min = mc.getAttr(int_surface+'.minValueV')
		max = mc.getAttr(int_surface+'.maxValueV')
	val = min + (max - min) * 0.5
	
	# Caluculate surface length (intermediate surface)
	iso_crv = mc.duplicateCurve(int_surface+'.'+opp+'['+str(val)+']',ch=0,rn=0,local=0)[0]
	iso_len = mc.arclen(iso_crv)
	iso_inc = iso_len / spans
	
	# Get spaced isoparm list
	curveFn = glTools.utils.curve.getCurveFn(iso_crv)
	iso_list = [int_surface+'.'+dir+'['+str(curveFn.findParamFromLength(iso_inc*i))+']' for i in range(spans+1)]
	mc.delete(iso_crv)
	
	# Check full rebuild
	if fullRebuildU:
		# Extract isoparm curves
		iso_crv_list = [mc.duplicateCurve(iso,ch=False,rn=False,local=False)[0] for iso in iso_list]
		# Rebuild isoparm curves
		for iso_crv in iso_crv_list:
			mc.rebuildCurve(iso_crv,ch=False,rpo=True,rt=0,end=1,kr=0,kcp=0,kep=1,kt=1,s=0,d=3,tol=0)
		# Loft final surface
		rebuild_surface = mc.loft(iso_crv_list,ch=0,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0,rsn=True)[0]
		# Delete intermediate curves
		mc.delete(iso_crv_list)
	else:
		# Loft final surface
		rebuild_surface = mc.loft(iso_list,ch=0,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0,rsn=True)[0]
	
	# Rename rebuilt surface
	rebuild_surface = mc.rename(rebuild_surface,surface+'_rebuild')
	rebuild_surfaceShape = mc.listRelatives(surface,s=True,ni=True)[0]
	mc.delete(int_surface)
	
	# Re-parameterize 0-1
	mc.rebuildSurface(rebuild_surface,ch=False,rpo=True,dir=2,rt=0,end=1,kr=0,kcp=1,kc=1,tol=0,fr=0)
	
	# Initialize return value
	outputShape = rebuild_surfaceShape
	
	# --------------------
	# - Replace Original -
	
	if replaceOrig:
	
		"""
		# Get original shape
		shapes = glTools.utils.shape.getShapes(surface,nonIntermediates=True,intermediates=False)
		if not shapes:
			# Find Intermediate Shapes
			shapes = glTools.utils.shape.listIntermediates(surface)
		
		# Check shapes
		if not shapes:
			raise Exception('Unable to determine shape for surface "'+surface+'"!')
		# Check connections
		if mc.listConnections(shapes[0]+'.create',s=True,d=False):
			# Find Intermediate Shapes
			shapes = glTools.utils.shape.findInputShape(shapes[0])
		"""
	
		# Check history
		shapes = mc.listRelatives(surface,s=True,ni=True)
		if not shapes: raise Exception('Unable to determine shape for surface "'+surface+'"!')
		shape = shapes[0]
		shapeHist = mc.listHistory(shape)
		if shapeHist.count(shape): shapeHist.remove(shape)
		if shapeHist: print('Surface "" contains construction history, creating new shape!')
		
		# Override shape info and delete intermediate
		mc.connectAttr(rebuild_surfaceShape+'.local',shape+'.create',f=True)
		outputShape = shape
	
	# Return result
	return outputShape

def rebuild_old(surface,spansU=0,spansV=0,fullRebuildU=False,fullRebuildV=False,replaceOrig=False):
	'''
	Do brute force surface rebuild for even parameterization
	@param surface: Nurbs surface to rebuild
	@type surface: str
	@param spansU: Number of spans along U. If 0, keep original value.
	@type spansU: int
	@param spansV: Number of spans along V. If 0, keep original value.
	@type spansV: int
	@param replaceOrig: Replace original surface, or create new rebuilt surface.
	@type replaceOrig: bool
	'''
	# Check surface
	if not isSurface(surface):
		raise Exception('Object "'+surface+'" is not a valid surface!')
	
	# Check spans
	if not spansU: spansU = mc.getAttr(surface+'.spansU')
	if not spansV: spansV = mc.getAttr(surface+'.spansV')
	
	# -------------
	# - Rebuild V -
	
	# Get V range
	minu = mc.getAttr(surface+'.minValueU')
	maxu = mc.getAttr(surface+'.maxValueU')
	u = minu + (maxu - minu) * 0.5
	
	# Extract isoparm curve
	iso_crv = mc.duplicateCurve(surface+'.u['+str(u)+']',ch=0,rn=0,local=0)[0]
	iso_len = mc.arclen(iso_crv)
	iso_inc = iso_len / spansV
	curveFn = glTools.utils.curve.getCurveFn(iso_crv)
	iso_list = [surface+'.v['+str(curveFn.findParamFromLength(iso_inc*i))+']' for i in range(spansV+1)]
	mc.delete(iso_crv)
	
	# Check full rebuild
	if fullRebuildU:
		# Extract isoparm curves
		iso_crv_list = [mc.duplicateCurve(iso,ch=False,rn=False,local=False)[0] for iso in iso_list]
		# Rebuild isoparm curves
		for iso_crv in iso_crv_list:
			mc.rebuildCurve(iso_crv,ch=False,rpo=True,rt=0,end=1,kr=0,kcp=0,kep=1,kt=1,s=0,d=3,tol=0)
		# Loft final surface
		int_surface = mc.loft(iso_crv_list,ch=0,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0,rsn=True)[0]
		# Delete intermediate curves
		mc.delete(iso_crv_list)
	else:
		# Loft intermediate surface
		int_surface = mc.loft(iso_list,ch=0,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0,rsn=True)[0]
	
	# -------------
	# - Rebuild U -
	
	# Get V range (intermediate surface)
	minv = mc.getAttr(int_surface+'.minValueV')
	maxv = mc.getAttr(int_surface+'.maxValueV')
	v = minv + (maxv - minv) * 0.5
	
	# Extract isoparm curve (intermediate surface)
	iso_crv = mc.duplicateCurve(int_surface+'.v['+str(v)+']',ch=0,rn=0,local=0)[0]
	iso_len = mc.arclen(iso_crv)
	iso_inc = iso_len / spansU
	curveFn = glTools.utils.curve.getCurveFn(iso_crv)
	iso_list = [int_surface+'.u['+str(curveFn.findParamFromLength(iso_inc*i))+']' for i in range(spansU+1)]
	mc.delete(iso_crv)
	
	# Check full rebuild
	if fullRebuildV:
		# Extract isoparm curves
		iso_crv_list = [mc.duplicateCurve(iso,ch=False,rn=False,local=False)[0] for iso in iso_list]
		# Rebuild isoparm curves
		for iso_crv in iso_crv_list:
			mc.rebuildCurve(iso_crv,ch=False,rpo=True,rt=0,end=1,kr=0,kcp=0,kep=1,kt=1,s=0,d=3,tol=0)
		# Loft final surface
		rebuild_surface = mc.loft(iso_crv_list,ch=0,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0,rsn=True)[0]
		# Delete intermediate curves
		mc.delete(iso_crv_list)
	else:
		# Loft final surface
		rebuild_surface = mc.loft(iso_list,ch=0,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0,rsn=True)[0]
	
	rebuild_surface = mc.rename(rebuild_surface,surface+'_rebuild')
	rebuild_surfaceShape = mc.listRelatives(surface,s=True,ni=True)[0]
	mc.delete(int_surface)
	
	# Initialize return value
	outputShape = rebuild_surfaceShape
	
	# --------------------
	# - Replace Original -
	
	if replaceOrig:
	
		"""
		# Get original shape
		shapes = glTools.utils.shape.getShapes(surface,nonIntermediates=True,intermediates=False)
		if not shapes:
			# Find Intermediate Shapes
			shapes = glTools.utils.shape.listIntermediates(surface)
		
		# Check shapes
		if not shapes:
			raise Exception('Unable to determine shape for surface "'+surface+'"!')
		# Check connections
		if mc.listConnections(shapes[0]+'.create',s=True,d=False):
			# Find Intermediate Shapes
			shapes = glTools.utils.shape.findInputShape(shapes[0])
		"""
	
		# Check history
		shapes = mc.listRelatives(surface,s=True,ni=True)
		if not shapes: raise Exception('Unable to determine shape for surface "'+surface+'"!')
		shape = shapes[0]
		shapeHist = mc.listHistory(shape)
		if shapeHist.count(shape): shapeHist.remove(shape)
		if shapeHist: print('Surface "" contains construction history, creating new shape!')
		
		# Override shape info and delete intermediate
		mc.connectAttr(rebuild_surfaceShape+'.local',shape+'.create',f=True)
		outputShape = shape
	
	# Return result
	return outputShape

def intersect(surface,source,direction):
	'''
	Return the intersection point on a specified nurbs surface given a source point and direction
	@param surface: Nurbs surface to perform intersection on
	@type surface: str
	@param source: Source point for the intersection ray
	@type source: list or tuple or str
	@param direction: Direction of the intersection ray intersection
	@type direction: list or tuple
	'''
	# Get surfaceFn
	surfaceFn = getSurfaceFn(surface)
	# Get source point
	source = glTools.utils.base.getMPoint(source)
	# Get direction vector
	direction = OpenMaya.MVector(direction[0],direction[1],direction[2])
	
	# Calculate intersection
	hitPt = OpenMaya.MPoint()
	hit = surfaceFn.intersect(source,direction,None,None,hitPt,0.0001,OpenMaya.MSpace.kWorld,False,None,None)
	if not hit:
		print 'No intersection found!'
		hitPt = OpenMaya.MPoint.origin
	
	# Return intersection hit point
	return [hitPt[0],hitPt[1],hitPt[2]]

def projectToSurface(surface,targetSurface,direction='u',keepOriginal=False,prefix=''):
	'''
	Project the edit points of the specified nurbs surface to another nurbs or polygon object
	@param surface: Surface to project
	@type surface: str
	@param targetSurface: Surface to project onto
	@type targetSurface: str
	@param direction: Surface direction to extract isoparm curves from
	@type direction: str
	@param keepOriginal: Create new surface or replace original
	@type keepOriginal: bool
	@param prefix: Name prefix for all created nodes
	@type prefix: str
	'''
	# Check surface
	if not mc.objExists(surface):
		raise UserInputError('Surface "'+surface+'" does not exist!!')
	if not isSurface(surface):
		raise UserInputError('Object "'+surface+'" is not a valid nurbs surface!!')
	
	# Check target surface
	if not mc.objExists(targetSurface):
		raise UserInputError('Target surface "'+targetSurface+'" does not exist!!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(surface)
	
	# Check direction
	direction = direction.upper()
	if (direction != 'U') and (direction != 'V'):
		raise UserInputError('Invalid surface direction specified! Must specify either "u" or "v"!!')
	
	# Get surface information
	spans = mc.getAttr(surface+'.spans'+direction)
	minVal = mc.getAttr(surface+'.minValue'+direction)
	maxVal = mc.getAttr(surface+'.maxValue'+direction)
	
	# Create main surface group
	mainGrp = mc.createNode('transform',n=prefix+'_grp')
	
	# Extract curves
	curveList = []
	curveGrpList = []
	curveLocList = []
	geomConstraintList = []
	spanInc = (maxVal - minVal)/spans
	for i in range(spans+1):
		# Curve prefix
		strInd = glTools.utils.stringUtils.stringIndex(i,2)
		crvPrefix = prefix+'_crv'+strInd
		# Create curve group
		curveGrp = crvPrefix+'_grp'
		curveGrp = mc.createNode('transform',n=curveGrp)
		curveGrp = mc.parent(curveGrp,mainGrp)[0]
		curveGrpList.append(curveGrp)
		# Get surface curve
		srfCurveName = crvPrefix+'_crv'
		srfCurve = mc.duplicateCurve(surface+'.'+direction.lower()+'['+str(i*spanInc)+']',ch=0,rn=0,local=0,n=srfCurveName)
		srfCurve = mc.parent(srfCurve[0],curveGrp)[0]
		curveList.append(srfCurve)
		# Generate curve locators
		curveLocatorList = glTools.utils.curve.locatorEpCurve(srfCurve,locatorScale=0.05,prefix=crvPrefix)
		curveLocatorList = mc.parent(curveLocatorList,curveGrp)
		curveLocList.append(curveLocatorList)
		# Create geometry constraints
		for loc in curveLocatorList:
			geomConstraint = crvPrefix+'_geometryConstraint'
			geomConstraint = mc.geometryConstraint(targetSurface,loc,n=geomConstraint)
			geomConstraintList.append(geomConstraint[0])
		# Center group pivot
		mc.xform(curveGrp,cp=True)
	
	# Delete original surface
	surfaceName = prefix+'_surface'
	if not keepOriginal:
		surfaceName = surface
		mc.delete(surface)
	
	# Loft new surface
	surfaceLoft = mc.loft(curveList,ch=1,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0,rsn=True)
	surface = mc.rename(surfaceLoft[0],surface)
	surface = mc.parent(surface,mainGrp)[0]
	mc.reorder(surface,f=True)
	loft = mc.rename(surfaceLoft[1],prefix+'_loft')
	
	# Return result
	return[surface,loft,curveList,curveGrpList,curveLocList,geomConstraintList]
	
def rebuildFromExistingIsoparms(surface,direction='u',degree=3,close=False,keepHistory=False):
	'''
	Build a new nurbs surface from an existing surfaces isoparms
	@param surface: Surface to build from
	@type surface: str
	@param direction: Surface direction to build from
	@type direction: str
	@param degree: Degree to build new surface to
	@type degree: int
	@param close: Close lofted surface
	@type close: bool
	@param keepHistory: Keep loft surface history
	@type keepHistory: bool
	'''
	# Check surface
	if not mc.objExists(surface):
		raise Exception('Surface "'+surface+'" does not exist!!')
	if not isSurface(surface):
		raise Exception('Object "'+surface+'" is not a valid nurbs surface!!')
	
	# Check direction
	direction = direction.lower()
	if not direction == 'u' and not direction == 'v':
		raise Exception('Invalid surface direction! Accepted values are "u" and "v"!')
	
	# Get surface details
	surfFn = getSurfaceFn(surface)
	spans = mc.getAttr(surface+'.spans'+direction.upper())
	degree = mc.getAttr(surface+'.degree'+direction.upper())
	form = mc.getAttr(surface+'.form'+direction.upper())
	knots = OpenMaya.MDoubleArray()
	if direction == 'u': surfFn.getKnotsInU(knots)
	if direction == 'v': surfFn.getKnotsInV(knots)
	
	# Build iso list for surface rebuild
	if degree > 1: knots = knots[(degree-1):-(degree-1)]
	isoList = [surface+'.'+direction+'['+str(i)+']' for i in knots]
	if not close and form:
		#isoList.append(isoList[0])
		isoList[-1] = isoList[-1] - 0.0001
	
	# Loft new rebuild surface
	rebuild = mc.loft(isoList,ch=keepHistory,u=True,c=close,ar=False,d=degree,ss=1,rn=False,po=False,rsn=(direction=='v'))
	rebuild = mc.rename(rebuild[0],surface+'_rebuild')
	
	# Return result
	return rebuild

def rebuildFromIsoparms(surface,spansU=0,spansV=0,degree=3,keepHistory=False):
	'''
	Build a new nurbs surface from an existing surfaces isoparms
	@param surface: Surface to build from
	@type surface: str
	@param direction: Surface direction to build from
	@type direction: str
	@param degree: Degree to build new surface to
	@type degree: int
	@param keepHistory: Keep loft surface history
	@type keepHistory: bool
	'''
	# Check surface
	if not mc.objExists(surface):
		raise Exception('Surface "'+surface+'" does not exist!!')
	if not isSurface(surface):
		raise Exception('Object "'+surface+'" is not a valid nurbs surface!!')
	
	# Initialize function pointers
	uMinPtr = OpenMaya.MScriptUtil().asDoublePtr()
	uMaxPtr = OpenMaya.MScriptUtil().asDoublePtr()
	vMinPtr = OpenMaya.MScriptUtil().asDoublePtr()
	vMaxPtr = OpenMaya.MScriptUtil().asDoublePtr()
	
	# Get surface details
	surfFn = getSurfaceFn(surface)
	surfFn.getKnotDomain(uMinPtr,uMaxPtr,vMinPtr,vMaxPtr)
	uMin = OpenMaya.MScriptUtil(uMinPtr).asDouble()
	uMax = OpenMaya.MScriptUtil(uMaxPtr).asDouble()
	vMin = OpenMaya.MScriptUtil(vMinPtr).asDouble()
	vMax = OpenMaya.MScriptUtil(vMaxPtr).asDouble()
	uDif = uMax - uMin
	vDif = vMax - vMin
	
	# Get surface form
	closeU = bool(mc.getAttr(surface+'.formU'))
	closeV = bool(mc.getAttr(surface+'.formV'))
	
	# Check spans
	if not spansU: spansU = surfFn.numKnotsInU()
	if not spansV: spansV = surfFn.numKnotsInV()
	
	# Get new knot values
	uList = []
	vList = []
	uInc = uDif/(spansU-int(not closeU))
	vInc = vDif/(spansV-int(not closeV))
	for u in range(spansU): uList.append(uMin+(uInc*u))
	for v in range(spansV): vList.append(vMin+(vInc*v))
	
	# Rebuild in U
	uLoft = mc.loft([surface+'.u['+str(i)+']' for i in uList],close=closeU,degree=degree)
	uSurface = uLoft[0]
	
	# Rebuld in V
	vLoft = mc.loft([uSurface+'.v['+str(i)+']' for i in vList],close=closeV,degree=degree)
	rebuildSurface = vLoft[0]
	
	# Return result
	return rebuildSurface
