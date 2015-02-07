import maya.cmds as mc

import glTools.utils.base
import glTools.utils.curve
import glTools.utils.stringUtils
import glTools.utils.transform

def create(	curve,
			objType='locator',
			objCount=0,
			parent=False,
			useDistance=False,
			minPercent=0.0,
			maxPercent=1.0,
			spacing=1.0,
			prefix='',
			suffix=''	):
	'''
	Create objects along a curve
	@param curve: Input nurbs curve curve
	@type curve: str
	@param objType: Type of objects to create and place along curve
	@type objType: str
	@param objCount: Number of objects to create along curve. If objCount=0, number of edit points will be used.
	@type objCount: int
	@param parent: Parent each new object to the previously created object. eg. Joint chain
	@type parent: bool
	@param useDistance: Use distance along curve instead of parametric length for sample distribution
	@type useDistance: bool
	@param minPercent: Percent along the curve to start placing objects
	@type minPercent: float
	@param maxPercent: Percent along the curve to stop placing objects
	@type maxPercent: float
	@param spacing: Incremental scale for each sample distance
	@type spacing: float
	@param prefix: Name prefix for builder created nodes. If left at default ("") prefix will be derived from curve name.
	@type prefix: str
	'''
	
	# Check Path
	if not glTools.utils.curve.isCurve(curve):
		raise Exception('Object "'+curve+'" is not a valid nurbs curve!')
	
	# Check Naming
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
	if not suffix: suffix = objType
	
	# Check Object Count
	if not objCount: objCount = mc.getAttr(curve+'.spans') + 1
	
	# Get Curve Sample Params
	paramList = glTools.utils.curve.sampleParam(	curve = curve,
												samples = objCount,
												useDistance = useDistance,
												minPercent = minPercent,
												maxPercent = maxPercent,
												spacing = spacing )
	
	# Create Objects Along Curve
	objList = []
	for i in range(objCount):
		
		# Create Object
		ind = glTools.utils.stringUtils.alphaIndex(i)
		obj = createAtParam(	curve,
								param	= paramList[i],
								objType	= objType,
								name	= prefix+ind+'_'+suffix	)
		
		# Parent
		if parent and i: obj = mc.parent(obj,objList[-1])[0]
		
		# Append Result
		objList.append(str(obj))
	
	# Return result
	return objList

def createAtParam(	curve,
					param	= 0.0,
					objType	= 'locator',
					name	= None	):
	'''
	Create an object at the specified point on a curve.
	@param curve: Input nurbs curve curve
	@type curve: str
	@param param: Curve parameter to create object at.
	@type param: str or tuple or list
	@param objType: Type of object to create and place along curve
	@type objType: str
	@param name: New object name
	@type name: str or None
	'''
	# Check Curve
	if not glTools.utils.curve.isCurve(curve):
		raise Exception('Object "'+curve+'" is not a valid nurbs curve!')
	
	# Check Name
	if not name: name = glTools.utils.stringUtils.stripSuffix(curve)+'_'+objType
	
	# Create Object
	obj = mc.createNode(objType)
	if not glTools.utils.transform.isTransform(obj):
		obj = mc.listRelatives(obj,p=True,pa=True)[0]
	obj = mc.rename(obj,name)
	
	# Position Object
	pos = mc.pointOnCurve(curve,pr=param)
	mc.xform(obj,t=pos,ws=True)
	
	# Return Result
	return obj

def createAtPoint(	curve,
					point,
					objType	= 'locator',
					name	= None	):
	'''
	Create an object at the closest point a curve to the specifies position.
	@param curve: Input nurbs curve curve
	@type curve: str
	@param point: Find the closest curve point to this position
	@type point: str or tuple or list
	@param objType: Type of object to create and place along curve
	@type objType: str
	@param name: New object name
	@type name: str or None
	'''
	# Check Curve
	if not glTools.utils.curve.isCurve(curve):
		raise Exception('Object "'+curve+'" is not a valid nurbs curve!')
	
	# Get Param at Point
	point = glTools.utils.base.getPosition(point)
	param = glTools.utils.curve.closestPoint(curve,pos=point)
	
	# Create Object
	obj = createAtParam(	curve,
							param	= param,
							objType	= objType,
							name	= None	)
	
	# Return Result
	return obj

