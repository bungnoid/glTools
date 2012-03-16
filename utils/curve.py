'''
@category Rigging @subcategory Curve
@tags Curve Nurbs Utility
@author gel
'''

import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.component
import glTools.utils.mathUtils
import glTools.utils.matrix
import glTools.utils.stringUtils

def isCurve(curve):
	'''
	Check if the specified object is a nurbs curve or transform parent of a curve
	
	@param curve: Object to query
	@type curve: str
	
	@return: Boolean value indicating if the input object is a valid nurbs curve
	@returnType: bool
	'''
	# Check object exists
	if not mc.objExists(curve): return False
	# Check shape
	if mc.objectType(curve) == 'transform': curve = mc.listRelatives(curve,s=True,ni=True,pa=True)[0]
	if mc.objectType(curve) != 'nurbsCurve': return False
	
	# Return result
	return True

def getCurveFn(curve):
	'''
	Create an MFnNurbsCurve class object from the specified nurbs curve
	
	@param curve: Curve to create function class for
	@type curve: str
	
	@return: An MFnNurnrsCurve function class initialized with the input curve
	@returnType: MFnNurnrsCurve
	'''
	# Checks
	if not isCurve(curve): raise Exception('Object '+curve+' is not a valid curve!')
	
	# Get shape
	if mc.objectType(curve) == 'transform':
		curve = mc.listRelatives(curve,s=True,ni=True)[0]
	
	# Get MFnNurbsCurve
	curveSel = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(curve,curveSel)
	curvePath = OpenMaya.MDagPath()
	curveSel.getDagPath(0,curvePath)
	curveFn = OpenMaya.MFnNurbsCurve(curvePath)
	
	# Return result
	return curveFn
	
def createFromPointList(pointList,degree=3,prefix=''):
	'''
	Build a nurbs curve from a list of arbitrary positions
	
	@param pointList: List of CV positions
	@type pointList: list
	@param degree: Degree of the curve to create
	@type degree: int
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Build CV list
	cvList = [glTools.utils.base.getPosition(i) for i in pointList]
	
	# Build curve
	crv = mc.curve(p=cvList,k=range(len(cvList)),d=1,n=prefix+'_curve')
	
	# Rebuild curve
	if degree > 1:
		crv = mc.rebuildCurve(crv,d=degree,kcp=True,kr=0,ch=False,rpo=True)[0]
	
	# Return resulting curve
	return crv

def createFromEditPointList(pointList,degree=3,form=1,prefix='curve'):
	'''
	Build a nurbs curve from a list of edit point positions
	
	@param pointList: List of edit point positions
	@type pointList: list
	@param degree: Degree of the curve to create
	@type degree: int
	@param form: Form of the curve to create. 1 = Open, 2 = Closed, 3 = Periodic
	@type form: int
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	
	@return: The curve created based on input argument values
	@returnType: str
	'''
	# Creat degree 1 curve from point list
	curve = createFromPointList(pointList,1,prefix)
	# Fit degree 3 curve
	fitCurve = mc.fitBspline(curve,ch=0,tol=0.01)
	# Delete original curve
	mc.delete(curve)
	# Rename fit curve
	curve = mc.rename(fitCurve[0],curve)
	# Return curve
	return curve

def createFromLocators(locatorList,degree=3,attach=False,prefix='curve'):
	'''
	Create a curve from a list of locators. Optionally attach curve CVs to locator positions
	
	@param locatorList: List of CV positions
	@type locatorList: list
	@param degree: Degree of the curve to create
	@type degree: int
	@param attach: Attach curve CVs to locator positions
	@type attach: bool
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	
	@return: The curve created based on input argument values
	@returnType: str
	'''
	# Get list of locator positions
	locPosList = []
	for i in range(len(locatorList)):
		locPosList.append(mc.getAttr(locatorList[i]+'.worldPosition')[0])
	
	# Build curve
	curve = createFromPointList(locPosList,degree,prefix)
	
	# Rename Curve
	curveShape = mc.listRelatives(curve,s=True,pa=True)[0]
	curveShape = mc.rename(curveShape,curve+'Shape')
	
	# Attach curve
	if attach: curveToLocators(curve,locatorList)
	
	# Return result
	return curve

def locatorCurve(curve,controlPoints=[],locatorScale=0.05,local=False,freeze=True,prefix=''):
	'''
	Creates locators for each control point for the specified curve. Locator
	world positions are connected to the curves ".controlPoints[*]" attribute.
	
	@param curve: Curve to operate on
	@type curve: str
	@param controlPoints: List of control points to connect to locator positions
	@type controlPoints: list
	@param locatorScale: Control the relative scale of the locators to the length of curve
	@type locatorScale: float
	@param local: Use local translate values instead of worldPosition
	@type local: bool
	@param freeze: Freeze translate values. Only applicable when local mode is False.
	@type freeze: float
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	
	@return: A list containing the names of the locators driving the curve
	@returnType: list
	'''
	# Check curve
	if not isCurve(curve): raise Exception('Object '+curve+ ' is not a valid curve!')
	# Check curve shape
	curveShape=''
	if mc.objectType(curve) == 'transform':
		curveShape = mc.listRelatives(curve,s=1,ni=1)[0]
	else:
		curveShape = curve
		curve = mc.listRelatives(curve,p=1)[0]
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
	
	# Check control points
	controlPointList = []
	if controlPoints:
		controlPointList = glTools.utils.component.getComponentIndexList(controlPoints)[curveShape]
	else:
		controlPointList = range(glTools.utils.component.getComponentCount(curve))
	
	# Set locator scale
	locatorScale *= mc.arclen(curve)
	
	# Initialize return list
	locatorList=[]
	# Iterate over control points
	for i in controlPointList:
		# Generate string index
		ind = str( i + 1 )
		if i < 9 : ind = "0" + ind
		# Get component position
		pos = mc.pointPosition( curve+".cv["+ str(i) +"]" )
		# Create locator
		locator = mc.spaceLocator(n=prefix+'_cv'+ind+'_locator')[0]
		# Position Locator
		mc.xform(locator,ws=True,t=pos)
		mc.setAttr(locator+".localScale",locatorScale,locatorScale,locatorScale)
		# Connect locator position to curve control point
		if local:
			mc.connectAttr(locator+'.translate',curve+'.controlPoints['+str(i)+']')
		else:
			if freeze: mc.makeIdentity(locator,apply=True,t=1,r=1,s=1,n=0)
			mc.connectAttr(locator+'.worldPosition[0]',curve+'.controlPoints['+str(i)+']')
		# Append locator to return list
		locatorList.append(locator)
	
	# Return locator list
	return locatorList

def locatorEpCurve(curve,locatorScale=0.05,prefix=''):
	'''
	Creates locators for each edit point for the specified curve. Edit points
	are constrained to the locator world positions.
	
	@param curve: Curve to operate on
	@type curve: str
	@param locatorScale: Control the relative scale of the locators to the length of curve
	@type locatorScale: float
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	
	@return: A list containing the names of the locators driving the curve
	@returnType: list
	'''
	# Check curve
	if not isCurve(curve): raise Exception('Object '+curve+ ' is not a valid curve!')
	# Check curve shape
	curveShape=''
	if mc.objectType(curve) == 'transform':
		curveShape = mc.listRelatives(curve,s=1,ni=1)[0]
	else:
		curveShape = curve
		curve = mc.listRelatives(curve,p=1)[0]
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
	
	# Get curve information
	spans = mc.getAttr(curve+'.spans')
	openCrv = not mc.getAttr(curve+'.form')
	numPt = spans + openCrv
	
	# Set locator scale
	locatorScale *= mc.arclen(curve)
	
	# Initialize return list
	locatorList=[]
	# Iterate over edit points
	for i in range(numPt):
		# Create point on curve deformer
		curveCon = mc.pointCurveConstraint(curveShape+'.ep['+str(i)+']',ch=1,rpo=1,w=1)
		locatorList.append(curveCon[0])
		# Create standin locatorList entries for tangency points
		if openCrv:
			if not i:
				# Get start tangency point position
				pos = mc.pointPosition(curveShape+'.cv[1]')
				coord = closestPoint(curve,pos)
				# Create point on curve deformer
				curveCon = mc.pointCurveConstraint(curveShape+'.u['+str(coord)+']',ch=1,rpo=1,w=1)
				locatorList.append(curveCon[0])
			if i == (numPt-2):
				# Get end tangency point position
				pos = mc.pointPosition(curveShape+'.cv['+str(numPt)+']')
				coord = closestPoint(curve,pos)
				# Create point on curve deformer
				curveCon = mc.pointCurveConstraint(curveShape+'.u['+str(coord)+']',ch=1,rpo=1,w=1)
				locatorList.append(curveCon[0])
	
	for i in range(len(locatorList)):
		# Scale and Center Locator Pivots
		localOffset = mc.getAttr(locatorList[i]+'.localPosition')[0]
		mc.setAttr(locatorList[i]+'.translate',localOffset[0],localOffset[1],localOffset[2])
		mc.setAttr(locatorList[i]+'.localPosition',0,0,0)
		mc.setAttr(locatorList[i]+'.localScale',locatorScale,locatorScale,locatorScale)
		# Rename Locator
		ind = str(i+1)
		if i<9: ind = '0' + ind
		locatorList[i] = mc.rename(locatorList[i],prefix+'ep'+ind+'_locator')
	
	# Return locator list
	return locatorList

def curveToLocators(curve,locatorList,controlPoints=[]):
	'''
	Connect a list of existing locator positions to the control points of a specified curve
	
	@param curve: Curve to connect to locators
	@type curve: str
	@param locatorList: List of locators to connect to the curve control points
	@type locatorList: list
	@param controlPoints: List of control points or indices to connect
	@type controlPoints: list
	'''
	# Check curve
	if not isCurve(curve): raise Exception('Object "'+curve+'" is not a valid nurbs curve!!')
	# Check locator list
	for i in range(len(locatorList)):
		if not mc.objExists(locatorList[i]):
			raise Exception('Object "'+locatorList[i]+'" does not exist!!')
	
	# Get component list
	if controlPoints:
		if type(controlPoints[0]) == 'str':
			componentIndexList = glTools.utils.component.getComponentIndexList(controlPoints)
			controlPoints = componentIndexList[componentIndexList.keys()[0]]
	else:
		componentIndexList = glTools.utils.component.getComponentIndexList(curve)
		controlPoints = componentIndexList[componentIndexList.keys()[0]]
	
	# Check target count
	if len(locatorList) != len(controlPoints):
			raise Exception('LocatorList length is not equal to the control point count!!')
	
	# Connect control points to locators
	for i in range(len(controlPoints)):
		mc.connectAttr(locatorList[i]+'.worldPosition',curve+'.controlPoints['+str(controlPoints[i])+']',f=True)
	
def closestPoint(curve,pos=(0,0,0)):
	'''
	Return closest point on curve to target
	
	@param curve: Curve to query closest point from
	@type curve: str
	@param pos: Position to query curve from
	@type pos: tuple
	
	@return: The curve parameter value closest to the input point
	@returnType: float
	'''
	# Check curve
	if not isCurve(curve):
		raise Exception('Object '+curve+ ' is not a valid nurbs curve!!')
	
	# Get edit point world position
	pos = OpenMaya.MPoint(pos[0],pos[1],pos[2],1.0)
	
	# Get curve function set
	crvFn = getCurveFn(curve)
	
	# Get uCoord pointer object
	uCoord = OpenMaya.MScriptUtil()
	uCoord.createFromDouble(0.0)
	uCoordPtr = uCoord.asDoublePtr()
	
	# Get closest u coordinate to position
	crvFn.closestPoint(pos,uCoordPtr,0.0001,OpenMaya.MSpace.kWorld)
	return OpenMaya.MScriptUtil(uCoordPtr).asDouble()

def getParamFromLength(curve,length):
	'''
	Get the U parameter fro the specified curve at a given length
	@param curve: Curve to get parameter from
	@type curve: str
	@param curve: Length along curve to sample parameter
	@type curve: float
	'''
	# Check curve
	if not isCurve(curve):
		raise Exception('Object "'+curve+'" is not a valid nurbs curve!')
	
	# Check length
	max_len = arclen(curve)
	if length > max_len:
		print('Input length is greater than actual curve length. Returning maximum U value!')
		return mc.getAttr(curve+'.maxValue')
	
	# Get curve function set
	curveFn = getCurveFn(curve)
	
	# Get parameter from length
	param = curveFn.findParamFromLength(length)
	
	# Return result
	return param

def projectToSurface(curve,targetSurface,keepOriginal=False,prefix=''):
	'''
	Project the edit points of the specified nurbs curve to aa nurbs or polygon object
	
	@param curve: Curve to project
	@type curve: str
	@param targetSurface: Surface to project onto
	@type targetSurface: str
	@param keepOriginal: Create new curve or replace original
	@type keepOriginal: bool
	@param prefix: Name prefix for all created nodes
	@type prefix: str
	
	@return: The curve parameter value closest to the input point
	@returnType: float
	'''
	# Check curve
	if not mc.objExists(curve):
		raise Exception('Curve "'+curve+'" does not exist!!')
	if not isCurve(curve):
		raise Exception('Object "'+curve+'" is not a valid nurbs curve!!')
	
	# Check target surface
	if not mc.objExists(targetSurface):
		raise Exception('Target surface "'+targetSurface+'" does not exist!!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
	
	# Duplicate original curve
	if keepOriginal:
		curve = mc.duplicate(curve,rc=True,rr=True)[0]
		mc.delete(mc.listRelatives(curve,c=True,type=['transform'],pa=True))
	
	# Create curve group
	grp = mc.createNode('transform',n=prefix+'_group')
	curve = mc.parent(curve,grp)[0]
	# Generate curve locators
	curveLocList = locatorEpCurve(curve,locatorScale=0.05,prefix=prefix)
	curveLocList = mc.parent(curveLocList,grp)
	# Create geometry constraints
	geomConstraintList = []
	for loc in curveLocList:
		geomConstraint = mc.geometryConstraint(targetSurface,loc,n=prefix+'_geometryConstraint')
		geomConstraintList.append(geomConstraint[0])
	# Center group pivot
	mc.xform(grp,cp=True)
	
	# Return result
	return[curve,grp,curveLocList,geomConstraintList]

def snapToCurve(curve,obj,uValue=0.0,useClosestPoint=False,snapPivot=False):
	'''
	Snap an object (or transform pivot) to a specified point on a curve.
	@param curve: Curve to snap to
	@type curve: str
	@param obj: Object to move to point on curve
	@type obj: str
	@param uValue: Paramater value of the curve to snap to
	@type uValue: float
	@param useClosestPoint: Use the closest point on the curve instead of the specified uv parameter
	@type useClosestPoint: bool
	@param snapPivot: Move only the objects pivot to the curve point
	@type snapPivot: bool
	'''
	# Check curve
	if not isCurve(curve): raise Exception('Object '+curve+' is not a valid curve!!')
	# Check uValue
	minu = mc.getAttr(curve+'.minValue')
	maxu = mc.getAttr(curve+'.maxValue')
	# Closest Point
	if useClosestPoint:
		pos = mc.xform(obj,q=True,ws=True,rp=True)
		uValue = closestPoint(curve,pos)
	# Verify surface parameter
	if uValue < minu or uValue > maxu:
		raise Exception('U paramater '+str(uValue)+' is not within the parameter range for '+curve+'!!')
	
	# Get curve point position
	pnt = mc.pointPosition(curve+'.u['+str(uValue)+']')
	
	# Snap to Curve
	piv = mc.xform(obj,q=True,ws=True,rp=True)
	if snapPivot: mc.xform(obj,piv=pnt,ws=True)
	else: mc.move(pnt[0]-piv[0],pnt[1]-piv[1],pnt[2]-piv[2],obj,r=True,ws=True)

def orientToCurve(curve,obj,uValue=0.0,useClosestPoint=False,upVector=(0,1,0),tangentAxis='x',upAxis='y'):
	'''
	Orient object to a specified point on a curve.
	@param curve: Curve to orient object to
	@type curve: str
	@param obj: Object to orient
	@type obj: str
	@param uValue: Paramater value of the curve to orient to
	@type uValue: float
	@param useClosestPoint: Use the closest point on the curve instead of the specified uv parameter
	@type useClosestPoint: bool
	@param upVector: upVector needed to calculate rotation matrix
	@type upVector: tuple
	@param tangentAxis: Basis axis that will be derived from the tangent of the curve point
	@type tangentAxis: str
	@param upAxis: Basis axis that will be derived from the upVector
	@type upAxis: str
	'''
	# Check curve
	if not isCurve(curve): raise Exception('Object '+curve+' is not a valid curve!!')
	# Check uValue
	minu = mc.getAttr(curve+'.minValue')
	maxu = mc.getAttr(curve+'.maxValue')
	# Closest Point
	if useClosestPoint:
		pos = mc.xform(obj,q=True,ws=True,rp=True)
		uValue = closestPoint(curve,pos)
	# Verify surface parameter
	if uValue < minu or uValue > maxu:
		raise Exception('U paramater '+str(uValue)+' is not within the parameter range for '+curve+'!!')
	
	# Check object
	if not mc.objExists(obj): raise Exception('Object '+obj+' does not exist!!')
	rotateOrder = mc.getAttr(obj+'.ro')
	
	# Get tangent at curve point
	tan = mc.pointOnCurve(curve,pr=uValue,nt=True)
	
	# Build rotation matrix
	mat = glTools.utils.matrix.buildRotation(tan,upVector,tangentAxis,upAxis)
	rot = glTools.utils.matrix.getRotation(mat,rotateOrder)
	
	# Orient object to curve
	mc.rotate(rot[0],rot[1],rot[2],obj,a=True,ws=True)

def sampleParam(curve,samples,useDistance=False,minPercent=0.0,maxPercent=1.0,spacing=1.0):
	'''
	Return a list of parameter values distributed evenly along a curve
	@param curve: Curve to sample
	@type curve: str
	@param curve: Number of samples along curve
	@type curve: int
	@param useDistance: Use distance along curve instead of parametric length for sample distribution
	@type useDistance: bool
	@param minPercent: The percentage along the curve that the samples will begin from
	@type minPercent: float
	@param maxPercent: The percentage along the curve that the samples will stop
	@type maxPercent: float
	@param spacing: Incremental scale for each sample distance
	@type spacing: float
	'''
	# Check curve
	if not isCurve(curve): raise Exception('Object '+curve+' is not a valid curve!!')
	
	# Check percent
	if minPercent<0.0 or minPercent>1.0: raise Exception('Min percent argument is not within the valid range (0->1)!!')
	if maxPercent<0.0 or maxPercent>1.0: raise Exception('Max percent argument is not within the valid range (0->1)!!')
	# Get percent range
	percentList = glTools.utils.mathUtils.distributeValue(samples,1.0,minPercent,maxPercent)
	
	# Build parameter list
	paramList = []
	if useDistance:
		curveFn = getCurveFn(curve)
		dist = curveFn.length()
		for i in range(samples):
			paramList.append(curveFn.findParamFromLength(dist*percentList[i]))
	else:
		# Get parameter range
		minU = mc.getAttr(curve+'.minValue')
		maxU = mc.getAttr(curve+'.maxValue')
		uDist = maxU - minU
		for i in range(samples):
			paramList.append(minU+(uDist*percentList[i]))
	# Return result
	return paramList

def blendCurve(curve1,curve2,blend=0.5,keepHistory=False,prefix=''):
	'''
	Create a new curve which is the blended result of 2 input curves
	@param curve1: First curve to contribute to the curve blend
	@type curve1: str
	@param curve2: Second curve to contribute to the curve blend
	@type curve2: str
	@param blend: The amount to blend from the first curve to the second curve
	@type blend: float
	@param keepHistory: Maintain the history nodes that generate the blend result
	@type keepHistory: bool
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Check curves
	if not isCurve(curve1): raise Exception('Object '+curve1+' is not a valid curve!!')
	if not isCurve(curve2): raise Exception('Object '+curve2+' is not a valid curve!!')
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve1)
	# Create average curve node
	avgCrv = mc.createNode('avgCurves',n=prefix+'_avgCurves')
	# Connect curves
	mc.connectAttr(curve1+'.worldSpace[0]',avgCrv+'.inputCurve1',f=True)
	mc.connectAttr(curve2+'.worldSpace[0]',avgCrv+'.inputCurve2',f=True)
	mc.setAttr(avgCrv+'.weight1',1.0-blend)
	mc.setAttr(avgCrv+'.weight2',blend)
	mc.setAttr(avgCrv+'.automaticWeight',0)
	# Create target curve
	crv = prefix+'_curve'
	crvShape = mc.createNode('nurbsCurve',n=crv+'Shape')
	crvParent = mc.listRelatives(crvShape,p=True)[0]
	crv = mc.rename(crvParent,crv)
	# Connect output curve
	mc.connectAttr(avgCrv+'.outputCurve',crv+'.create',f=True)
	# Add blend control
	if keepHistory:
		# Create blend attribute
		if not mc.objExists(crv+'.blend'):
			mc.addAttr(crv,ln='blend',min=0.0,max=1.0,dv=0.5,k=True)
		mc.connectAttr(crv+'.blend',avgCrv+'.weight2',f=True)
		# Create reverse node
		rvs = mc.createNode('reverse',n=prefix+'_reverse')
		# Connect to average curve node
		mc.connectAttr(crv+'.blend',rvs+'.inputX',f=True)
		mc.connectAttr(rvs+'.outputX',avgCrv+'.weight1',f=True)
	else:
		# Delete History
		mc.delete(crv,ch=True)
	return crv

def edgeLoopCrv(meshEdgeList,rebuild=False,rebuildSpans=0,form=2,keepHistory=True,prefix=''):
	'''
	Generate a curve from a mesh edge loop.
	@param meshEdgeList: List of mesh edges to generate curve from
	@type meshEdgeList: list
	@param rebuild: Rebuild curve to degree 3
	@type rebuild: bool
	@param rebuildSpans: Number of spans to rebuild the resulting curve to
	@type rebuildSpans: int
	@param form: Form of the resulting curve. 0 = Open, 1 = Periodic, 2 = Best Guess.
	@type form: str
	@param keepHistory: Maintain construction history
	@type keepHistory: bool
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Check edge list
	if not meshEdgeList:
		raise Exception('Invalid mesh edge list provided!!')
	meshEdgeList = mc.ls(meshEdgeList,fl=True)
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(meshEdgeList[0].split('.')[0])
	# Convert edge selection to nurbs curve
	crvDegree = 1
	if rebuild: crvDegree = 3
	curve = mc.polyToCurve(ch=keepHistory,form=form,degree=crvDegree)[0]
	# Rebuild as degree 3
	if rebuild and rebuildSpans:
		curve = mc.rebuildCurve(curve,ch=keepHistory,rpo=1,rt=0,end=1,kr=0,kcp=1,kep=1,kt=1,s=rebuildSpans,d=3,tol=0.01)[0]
	# Rename curve
	curve = mc.rename(curve,prefix+'_curve')
	
	# Return result
	return curve

def tubeFromCurve(curve,spans=6,radius=1,upVector=(0,1,0),prefix=''):
	'''
	Project a tubular surface from the specified path curve to the target geometry.
	@param curve: Path curve used to build the tube surface
	@type curve: str
	@param spans: Number of radial spans around the surface
	@type spans: int
	@param radius: Circular radius of the tube surface
	@type radius: float
	@param upVector: Up vector used to calculate the radial orientation of the tube surface
	@type upVector: tuple
	@param prefix: Name prefix for all created nodes
	@type prefix: str
	'''
	# Check curve
	if not isCurve(curve):
		raise Exception('Object "'+curve+'" is not a valid nurbs curve!!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
	
	# Get curve info
	crvMin = mc.getAttr(curve+'.minValue')
	crvMax = mc.getAttr(curve+'.maxValue')
	crvSpan = mc.getAttr(curve+'.spans')
	crvInc = (crvMax - crvMin) / (crvSpan + 1)
	
	# Increment over curve edit points
	crvList = []
	crvGrpList = []
	for i in range(crvSpan + 2):
		strInd = glTools.utils.stringUtils.stringIndex(i+1,2)
		crvPrefix = prefix+'crv'+strInd
		crvCirc = mc.circle(r=radius,s=spans,degree=3,n=crvPrefix+'_curve')
		crvGrp = mc.group(crvCirc[0],n=crvPrefix+'_group')
		snapToCurve(curve,crvGrp,(crvInc*i),False,False)
		orientToCurve(curve,crvGrp,(crvInc*i),False,upVector,'z','y')
		crvList.append(crvCirc[0])
		crvGrpList.append(crvGrp)
	
	# Loft surface between curves
	surface = mc.loft(crvList,ch=1,u=1,c=0,ar=1,d=3,ss=1,rn=0,po=0,rsn=True,n=prefix+'_surface')[0]
	
	# Return result
	return[surface,crvList,crvGrpList]
	
def buildCmd(curve,round=True):
	'''
	Generate and return the python command to rebuild the specified curve in world space
	@param curve: The curve to generate the build command for
	@type curve: str
	@param round: Position float precision
	@type round: bool
	'''
	# Check curve
	if not isCurve(curve):
		raise Exception('Object "'+curve+'" is not a valid nurbs curve!!')
	
	# Initialize command
	cmd = 'mc.curve('
	
	# Get curve function set
	curveFn = getCurveFn(curve)
	
	# Get curve degree
	degree = curveFn.degree()
	cmd += 'd='+str(degree)+','
	
	# Get points
	points = OpenMaya.MPointArray()
	curveFn.getCVs(points,OpenMaya.MSpace.kWorld)
	cmd += 'p=['
	for i in range(points.length()):
		if i: cmd += ','
		if round: cmd += '('+('%.3f' % points[i][0])+','+('%.3f' % points[i][1])+','+('%.3f' % points[i][2])+')'
		else: cmd += '('+str(points[i][0])+','+str(points[i][1])+','+str(points[i][2])+')'
	cmd += '],'
	
	# Get knots
	knots = OpenMaya.MDoubleArray()
	curveFn.getKnots(knots)
	cmd += 'k=['
	for i in range(knots.length()):
		if i: cmd += ','
		cmd += str(knots[i])
	cmd += '],'
	
	# Finalize command
	cmd += 'n="'+str(curve)+'")'
	
	# Return result
	return cmd

def mirrorCurve(srcCrv,dstCrv,axis='x',space='world'):
	'''
	Set the shape of a destination curve based on the mirror of a source curve
	@param srcCrv: Source curve
	@type srcCrv: str
	@param dstCrv: Destination curve
	@type dstCrv: str
	@param axis: Mirror axis
	@type axis: str
	@param space: Space to sample and set curves in
	@type space: str
	'''
	# Check curves
	if not isCurve(srcCrv):
		raise Exception('Object "'+srcCrv+'" is not a valid nurbs curve!!')
	if not isCurve(dstCrv):
		raise Exception('Object "'+dstCrv+'" is not a valid nurbs curve!!')
	
	# Get curve funtion sets
	srcCrvFn = getCurveFn(srcCrv)
	dstCrvFn = getCurveFn(dstCrv)
	
	# Check curve CV counts
	if srcCrvFn.numCVs() != dstCrvFn.numCVs():
		raise Exception('Source and destination curves are not compatible! Different CV counts.')
	
	# Get space
	if space=='world': mSpace = OpenMaya.MSpace.kWorld
	elif space=='object': mSpace = OpenMaya.MSpace.kObject
	else: raise Exception('Invalid Space "'+space+'"!')
	
	# Get source point array
	ptArray = OpenMaya.MPointArray()
	srcCrvFn.getCVs(ptArray,mSpace)
	
	# Determine mirror axis
	axis = axis.lower()
	axisDict = {'x':0,'y':1,'z':2}
	if not axisDict.keys().count(axis):
		raise Exception('Invalid axis "'+axis+'"!')
	axisInd = axisDict[axis]
	
	# Mirror Points
	for i in range(ptArray.length()):
		pt = [ptArray[i].x,ptArray[i].y,ptArray[i].z]
		pt[axisInd] *= -1
		ptArray.set(OpenMaya.MPoint(pt[0],pt[1],pt[2],1.0),i)
	
	# Set mirror points
	dstCrvFn.setCVs(ptArray,mSpace)
	dstCrvFn.updateCurve()

def uniformRebuild(curve,spans=6,replaceOriginal=True,prefix=''):
	'''
	Rebuild curve using uniformRebuild node.
	
	@param curve: Original curve to operate on
	@type curve: str
	@param spans: Number of spans for the rebuilt curve
	@type spans: int
	@param replaceOriginal: Replace original curve, or create a new one.
	@type replaceOriginal: bool
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	
	@return: A list containing the curve and uniformRebuild node
	@returnType: list
	'''
	# Check plugin in loaded
	if not mc.pluginInfo('uniformRebuild',q=True,l=True):
		try: mc.loadPlugin('uniformRebuild')
		except:	raise MissingPluginError('Unable to load uniformRebuild!')
	
	# Check curve
	if not isCurve(curve): raise Exception('Object "'+curve+'" is not a valid nurbs curve!')
	# Check curve shape
	curveShape=''
	if mc.objectType(curve) == 'transform':
		curveShape = mc.listRelatives(curve,s=1,ni=1)[0]
	else:
		curveShape = curve
		curve = mc.listRelatives(curve,p=1)[0]
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
	
	# Create uniformRebuild node
	uniformRebuildNode = mc.createNode('uniformRebuild',n=prefix+'_uniformRebuild')
	mc.setAttr(uniformRebuildNode+'.spans',spans)
	
	# Duplicate curve
	rebuildCurve = mc.duplicate(curve,rr=True,rc=True,n=prefix+'_rebuild_curve')[0]
	rebuildCurveShape = mc.listRelatives(rebuildCurve,ni=True,s=True)[0]
	
	# Connect to uniformRebuild
	mc.connectAttr(curveShape+'.local',uniformRebuildNode+'.inputCurve',f=True)
	mc.connectAttr(uniformRebuildNode+'.outputCurve',rebuildCurveShape+'.create')
	
	# Replace original
	if replaceOriginal:
		rebuildCurveShape = mc.parent(rebuildCurveShape,curve,s=True,r=True)[0]
		mc.setAttr(curveShape+'.intermediateObject',1)
		mc.rename(curveShape,curveShape+'Orig')
		mc.rename(rebuildCurveShape,curveShape)
		mc.delete(rebuildCurve)
		rebuildCurve = curve
	
	# Return result
	return [rebuildCurve,uniformRebuildNode]
