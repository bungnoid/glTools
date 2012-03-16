import maya.cmds as mc
import glTools.common.namingConvention
import glTools.utils.curve

def curveConstraint(transform,curve,parameter,useClosestPoint=True,normalizeParameter=True,tangentAxis='x',upAxis='y',upVector='y',upObject='',prefix=''):
	'''
	@param transform: Transform to constrain to curve
	@type transform: str
	@param curve: Target curve that drives the constraint
	@type curve: str
	@param parameter: Target curve parameter to constrain to
	@type parameter: float
	@param useClosestPoint: Use the closest curve parameter to the transform instead of the specified parameter
	@type useClosestPoint: bool
	@param tangentAxis: Transform axis to align to the curve tangent
	@type tangentAxis: str
	@param upAxis: Transform axis to align to the upVector of the constraint node
	@type upAxis: str
	@param upVector: The world or upObject vector to be used as the constraint upVector
	@type upVector: str
	@param upObject: Specifies the upVector object for the constraint
	@type upObject: str
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Build axis dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	# Check prefix
	nameUtil = glTools.common.namingConvention.NamingConvention()
	if not prefix: prefix = nameUtil.stripSuffix(transform)
	
	# Parameter
	pos = mc.xform(transform,q=True,ws=True,rp=True)
	if useClosestPoint: parameter = glTools.utils.curve.closestPoint(curve,pos)
	
	# PointOnCurveInfo
	poc = prefix+nameUtil.delineator+nameUtil.node['pointOnCurveInfo']
	poc = mc.createNode('pointOnCurveInfo',n=poc)
	mc.connectAttr(curve+'.worldSpace[0]',poc+'.inputCurve',f=True)
	if normalizeParameter:
		mc.setAttr(poc+'.turnOnPercentage',1)
		minParam = mc.getAttr(curve+'.minValue')
		maxParam = mc.getAttr(curve+'.maxValue')
		parameter = (parameter-minParam)/(maxParam-minParam)
	mc.setAttr(poc+'.parameter',parameter)
	
	# Point Constraint
	pntCon = prefix+nameUtil.delineator+nameUtil.node['pointConstraint']
	pntCon = mc.createNode('pointConstraint',n=pntCon)
	mc.connectAttr(poc+'.position',pntCon+'.target[0].targetTranslate',f=True)
	mc.connectAttr(transform+'.parentInverseMatrix[0]',pntCon+'.constraintParentInverseMatrix',f=True)
	mc.connectAttr(pntCon+'.constraintTranslate',transform+'.translate',f=True)
	
	# Aim Constraint
	aimCon = prefix+nameUtil.delineator+nameUtil.node['aimConstraint']
	aimCon = mc.createNode('aimConstraint',n=aimCon)
	mc.connectAttr(poc+'.tangent',aimCon+'.target[0].targetTranslate',f=True)
	aimVec = axisDict[tangentAxis]
	upVec = axisDict[upAxis]
	mc.setAttr(aimCon+'.aimVector',aimVec[0],aimVec[1],aimVec[2])
	mc.setAttr(aimCon+'.upVector',upVec[0],upVec[1],upVec[2])
	# UpVector
	wUpVec = axisDict[upVector]
	mc.setAttr(aimCon+'.worldUpVector',wUpVec[0],wUpVec[1],wUpVec[2])
	# UpObject
	if upObject:
		mc.connectAttr(upObject+'.worldMatrix[0]',aimCon+'.worldUpMatrix',f=True)
		mc.setAttr(aimCon+'.worldUpType',2) # Object Rotation Up
	# Connect
	mc.connectAttr(transform+'.parentInverseMatrix[0]',aimCon+'.constraintParentInverseMatrix',f=True)
	mc.connectAttr(aimCon+'.constraintRotate',transform+'.rotate',f=True)
	
	# Parent constraints
	mc.parent(pntCon,transform)
	mc.parent(aimCon,transform)
	
	# Add parameter attribute
	if not mc.objExists(transform+'.param'):
		if normalizeParameter: mc.addAttr(transform,ln='param',at='float',dv=parameter,min=0.0,max=1.0,k=True)
		else: mc.addAttr(transform,ln='param',at='float',dv=parameter,min=minParam,max=maxParam,k=True)
	mc.connectAttr(transform+'.param',poc+'.parameter',f=True)
	
	# Return result
	return(poc,pntCon,aimCon)
	
def curveAimConstraint(transform,curve,parameter,useClosestPoint=True,aimAxis='y',tangentAxis='x',prefix=''):
	'''
	@param transform: Transform to aim at point on curve
	@type transform: str
	@param curve: Target curve that drives the constraint
	@type curve: str
	@param parameter: Target curve parameter to aim at
	@type parameter: float
	@param useClosestPoint: Use the closest curve parameter to the transform instead of the specified parameter
	@type useClosestPoint: bool
	@param aimAxis: Transform axis to aim at the point on curve
	@type aimAxis: float
	@param tangentAxis: Transform axis to align to the curve tangent
	@type tangentAxis: str
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Build axis dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	# Check prefix
	nameUtil = glTools.common.namingConvention.NamingConvention()
	if not prefix: prefix = nameUtil.stripSuffix(transform)
	
	# Transform worldSpace position
	pmm = prefix+nameUtil.delineator+nameUtil.node['pointMatrixMult']
	pmm = mc.createNode('pointMatrixMult',n=pmm)
	mc.connectAttr(transform+'.translate',pmm+'.inPoint',f=True)
	mc.connectAttr(transform+'.parentMatrix[0]',pmm+'.inMatrix',f=True)
	mc.setAttr(pmm+'.vectorMultiply',1)
	
	# Parameter
	pos = mc.xform(transform,q=True,ws=True,rp=True)
	if useClosestPoint: paramater = glTools.utils.curve.closestPoint(curve,pos)
	
	# PointOnCurveInfo
	poc = prefix+nameUtil.delineator+nameUtil.node['pointOnCurveInfo']
	poc = mc.createNode('pointOnCurveInfo',n=poc)
	mc.connectAttr(curve+'.worldSpace[0]',poc+'.inputCurve',f=True)
	mc.setAttr(poc+'.parameter',paramater)
	
	# Offset
	pma = prefix+nameUtil.delineator+nameUtil.node['plusMinusAverage']
	pma = mc.createNode('plusMinusAverage',n=pma)
	mc.connectAttr(poc+'.position',pma+'.input3D[0]',f=True)
	mc.connectAttr(pmm+'.output',pma+'.input3D[1]',f=True)
	mc.setAttr(pma+'.operation',2) # Subtract
	
	# Aim Constraint
	aimCon = prefix+nameUtil.delineator+nameUtil.node['aimConstraint']
	aimCon = mc.createNode('aimConstraint',n=aimCon)
	mc.connectAttr(pma+'.output3D',aimCon+'.target[0].targetTranslate',f=True)
	mc.connectAttr(poc+'.tangent',aimCon+'.worldUpVector',f=True)
	mc.connectAttr(transform+'.parentInverseMatrix[0]',aimCon+'.constraintParentInverseMatrix',f=True)
	mc.setAttr(aimCon+'.worldUpType',3) # Vector
	mc.connectAttr(aimCon+'.constraintRotateX',transform+'.rotateX',f=True)
	mc.connectAttr(aimCon+'.constraintRotateY',transform+'.rotateY',f=True)
	mc.connectAttr(aimCon+'.constraintRotateZ',transform+'.rotateZ',f=True)
	aimVec = axisDict[aimAxis]
	tanVec = axisDict[tangentAxis]
	mc.setAttr(aimCon+'.aimVector',aimVec[0],aimVec[1],aimVec[2])
	mc.setAttr(aimCon+'.upVector',tanVec[0],tanVec[1],tanVec[2])
	mc.parent(aimCon,transform)
	
	# Add parameter attribute
	minU = mc.getAttr(curve+'.minValue')
	maxU = mc.getAttr(curve+'.maxValue')
	if not mc.objExists(transform+'.paramU'): mc.addAttr(transform,ln='paramU',at='float',min=minU,max=maxU,k=True)
	mc.setAttr(transform+'.paramU',parameter)
	mc.connectAttr(transform+'.paramU',poc+'.parameter',f=True)

def multiCurveAimConstraint(transform,curve1,curve2,toggleAttr,aimAxis='y',tangentAxis='x',prefix=''):
	'''
	@param transform: Transforms to aim at point on curve
	@type transform: list
	@param curve1: First curve aim target
	@type curve1: str
	@param curve2: Second curve aim target
	@type curve2: str
	@param toggleAttr: Attribute to toggle between the constraint targets
	@type toggleAttr: str
	@param aimAxis: Transform axis to aim at the point on curve
	@type aimAxis: float
	@param tangentAxis: Transform axis to align to the curve tangent
	@type tangentAxis: str
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Build axis dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	# Check prefix
	nameUtil = glTools.common.namingConvention.NamingConvention()
	if not prefix: prefix = nameUtil.stripSuffix(transform)
	
	# Transform worldSpace position
	pmm = prefix+nameUtil.delineator+nameUtil.node['pointMatrixMult']
	pmm = mc.createNode('pointMatrixMult',n=pmm)
	mc.connectAttr(transform+'.translate',pmm+'.inPoint',f=True)
	mc.connectAttr(transform+'.parentMatrix[0]',pmm+'.inMatrix',f=True)
	mc.setAttr(pmm+'.vectorMultiply',1)
	
	# PointOnCurveInfo
	poc1 = prefix+nameUtil.delineator+'pc01'+nameUtil.delineator+nameUtil.node['pointOnCurveInfo']
	poc1 = mc.createNode('pointOnCurveInfo',n=poc1)
	mc.connectAttr(curve1+'.worldSpace[0]',poc1+'.inputCurve',f=True)
	poc2 = prefix+nameUtil.delineator+'pc02'+nameUtil.delineator+nameUtil.node['pointOnCurveInfo']
	poc2 = mc.createNode('pointOnCurveInfo',n=poc2)
	mc.connectAttr(curve2+'.worldSpace[0]',poc2+'.inputCurve',f=True)
	
	pos = mc.xform(transform,q=True,ws=True,rp=True)
	param = glTools.utils.curve.closestPoint(curve1,pos)
	mc.setAttr(poc1+'.parameter',param)
	pos = mc.pointOnCurve(curve1,pr=param,p=True)
	param = glTools.utils.curve.closestPoint(curve2,pos)
	mc.setAttr(poc2+'.parameter',param)
	
	# Offset
	pma1 = prefix+nameUtil.delineator+'pc01'+nameUtil.delineator+nameUtil.node['plusMinusAverage']
	pma1 = mc.createNode('plusMinusAverage',n=pma1)
	mc.connectAttr(poc1+'.position',pma1+'.input3D[0]',f=True)
	mc.connectAttr(pmm+'.output',pma1+'.input3D[1]',f=True)
	mc.setAttr(pma1+'.operation',2) # Subtract
	
	pma2 = prefix+nameUtil.delineator+'pc02'+nameUtil.delineator+nameUtil.node['plusMinusAverage']
	pma2 = mc.createNode('plusMinusAverage',n=pma2)
	mc.connectAttr(poc2+'.position',pma2+'.input3D[0]',f=True)
	mc.connectAttr(pmm+'.output',pma2+'.input3D[1]',f=True)
	mc.setAttr(pma2+'.operation',2) # Subtract
	
	# Blend Offset
	pos_bcn = prefix+nameUtil.delineator+'ps01'+nameUtil.delineator+nameUtil.node['blendColors']
	pos_bcn = mc.createNode('blendColors',n=pos_bcn)
	mc.connectAttr(pma1+'.output3D',pos_bcn+'.color1',f=True)
	mc.connectAttr(pma2+'.output3D',pos_bcn+'.color2',f=True)
	mc.connectAttr(toggleAttr,pos_bcn+'.blender',f=True)
	
	# Blend Tangent
	tan_bcn = prefix+nameUtil.delineator+'rt01'+nameUtil.delineator+nameUtil.node['blendColors']
	tan_bcn = mc.createNode('blendColors',n=tan_bcn)
	mc.connectAttr(poc1+'.tangent',tan_bcn+'.color1',f=True)
	mc.connectAttr(poc2+'.tangent',tan_bcn+'.color2',f=True)
	mc.connectAttr(toggleAttr,tan_bcn+'.blender',f=True)
	
	# Aim Constraint
	aimCon = prefix+nameUtil.delineator+nameUtil.node['aimConstraint']
	aimCon = mc.createNode('aimConstraint',n=aimCon)
	mc.connectAttr(pos_bcn+'.output',aimCon+'.target[0].targetTranslate',f=True)
	mc.connectAttr(tan_bcn+'.output',aimCon+'.worldUpVector',f=True)
	mc.setAttr(aimCon+'.worldUpType',3) # Vector
	mc.connectAttr(transform+'.parentInverseMatrix[0]',aimCon+'.constraintParentInverseMatrix',f=True)
	mc.connectAttr(aimCon+'.constraintRotateX',transform+'.rotateX',f=True)
	mc.connectAttr(aimCon+'.constraintRotateY',transform+'.rotateY',f=True)
	mc.connectAttr(aimCon+'.constraintRotateZ',transform+'.rotateZ',f=True)
	aimVec = axisDict[aimAxis]
	tanVec = axisDict[tangentAxis]
	mc.setAttr(aimCon+'.aimVector',aimVec[0],aimVec[1],aimVec[2])
	mc.setAttr(aimCon+'.upVector',tanVec[0],tanVec[1],tanVec[2])
	mc.parent(aimCon,transform)
	
	# Add parameter attribute
	minU = mc.getAttr(curve1+'.minValue')
	maxU = mc.getAttr(curve1+'.maxValue')
	if not mc.objExists(transform+'.param1'):
		mc.addAttr(transform,ln='param1',at='float',min=minU,max=maxU,k=True)
	mc.setAttr(transform+'.param1',mc.getAttr(poc1+'.parameter'))
	mc.connectAttr(transform+'.param1',poc1+'.parameter',f=True)
	
	minU = mc.getAttr(curve2+'.minValue')
	maxU = mc.getAttr(curve2+'.maxValue')
	if not mc.objExists(transform+'.param2'):
		mc.addAttr(transform,ln='param2',at='float',min=minU,max=maxU,k=True)
	mc.setAttr(transform+'.param2',mc.getAttr(poc2+'.parameter'))
	mc.connectAttr(transform+'.param2',poc2+'.parameter',f=True)
	
	# Return result
	return (aimCon,poc1,poc2)
