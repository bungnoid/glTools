import maya.cmds as mc
import maya.mel as mm
import glTools.utils.base
import glTools.utils.curve
import glTools.utils.stringUtils
import glTools.utils.transform

def create(curve,objType,objCount=0,parent=False,useDistance=False,minPercent=0.0,maxPercent=1.0,prefix='',suffix=''):
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
	@param prefix: Name prefix for builder created nodes. If left at default ("") prefix will be derived from curve name.
	@type prefix: str
	'''
	
	# Check Path
	if not glTools.utils.curve.isCurve(curve):
		raise Exception('Object "'+curve+'" is not a valid nurbs curve!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
	# Check suffix
	if not suffix: suffix = objType
	
	# Check object count
	if not objCount: objCount = mc.getAttr(curve+'.spans') + 1
	
	# Get curve sample points
	paramList = glTools.utils.curve.sampleParam(curve,objCount,useDistance,minPercent,maxPercent)
	
	# Create object along curve
	objList = []
	for i in range(objCount):
		
		# Create object
		obj = mc.createNode(objType)
		if not glTools.utils.transform.isTransform(obj):
			obj = mc.listRelatives(obj,p=True,pa=True)[0]
		ind = glTools.utils.stringUtils.stringIndex(i+1)
		obj = mc.rename(obj,prefix+ind+'_'+suffix)
		
		# Position object
		pos = mc.pointOnCurve(curve,pr=paramList[i])
		mc.xform(obj,t=pos,ws=True)
		
		# Parent
		if parent and i: obj = mc.parent(obj,objList[-1])[0]
		
		# Append result
		objList.append(str(obj))
	
	# Return result
	return objList
