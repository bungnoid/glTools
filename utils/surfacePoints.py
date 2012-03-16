import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import glTools.utils.surface
import glTools.utils.mathUtils
import glTools.common.namingConvention

class UserInputError( Exception ): pass

def add(surface,targetList,surfacePointsNode='',alignTo='u',rotate=True,tangentUAxis='x',tangentVAxis='y',prefix=''):
	'''
	@param surface: Nurbs surface to constrain to
	@type surface: str
	@param targetList: List of target transforms/positions/coordinates
	@type targetList: list
	@param surfacePointsNode: Name for a new or existing surfacePoints node
	@type surfacePointsNode: str
	@param alignTo: Surface direction to align to. This option is ignored if the specified surface points node already exists
	@type alignTo: str
	@param rotate: Calculate rotation
	@type rotate: bool
	@param tangentUAxis: Transform axis to align with the surface U tangent
	@type tangentUAxis: str
	@param tangentVAxis: Transform axis to align with the surface V tangent
	@type tangentVAxis: str
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Check surface
	if not glTools.utils.surface.isSurface(surface):
		raise UserInputError('Object "" is not a valid nurbs surface!!')
	
	# Check prefix
	nameUtil = glTools.common.namingConvention.NamingConvention()
	if not prefix: prefix = nameUtil.stripSuffix(surface)
	
	# Check targetList
	if not targetList: raise UserInputError('Invalid target list!!')
	
	# Check surfacePoints node
	if not surfacePointsNode:
		surfacePointsNode = nameUtil.appendName(prefix,nameUtil.node['surfacePoints'],stripNameSuffix=False)
	if mc.objExists(surfacePointsNode):
		if not mc.objectType(surfacePointsNode) == 'surfacePoints':
			raise UserInputError('Object "'+surfacePointsNode+'" is not a valid surfacePoints node!!')
	else:
		# Create new surface points node
		surfacePointsNode = mc.createNode('surfacePoints',n=surfacePointsNode)
		mc.connectAttr(surface+'.worldSpace[0]',surfacePointsNode+'.inputSurface')
		# Apply settings
		mc.setAttr(surfacePointsNode+'.calculateRotation',rotate)
		if alignTo=='u': mc.setAttr(surfacePointsNode+'.alignTo',0)
		else: mc.setAttr(surfacePointsNode+'.alignTo',1)
		# Tangent Axis
		axisDict = {'x':0,'y':1,'z':2,'-x':3,'-y':4,'-z':5}
		mc.setAttr(surfacePointsNode+'.tangentUAxis',axisDict[tangentUAxis])
		mc.setAttr(surfacePointsNode+'.tangentVAxis',axisDict[tangentVAxis])
	
	# Find next available input index
	nextIndex = getNextAvailableIndex(surfacePointsNode)
	
	# Create surface constraints
	transformList = []
	for i in range(len(targetList)):
		
		# Get current input index
		ind = str(nextIndex + i)
		if int(ind)<10: ind = '0'+ind
		
		# Initialize UV parameter variable
		uv = (0.0,0.0)
		pos = (0.0,0.0,0.0)
		# Get target surface point for current target
		if type(targetList[i])==str or type(targetList[i])==unicode:
			if not mc.objExists(targetList[i]): raise UserInputError('Target list object "'+targetList[i]+'" does not exist')
			pos = mc.pointPosition(targetList[i])
			uv = glTools.utils.surface.closestPoint(surface,pos)
		elif type(targetList[i])==tuple or type(targetList[i])==list:
			if len(targetList[i]) == 3:
				pos = targetList[i]
				uv = glTools.utils.surface.closestPoint(surface,pos)
			elif len(targetList[i]) == 2:
				uv = targetList[i]
				pos = mc.pointOnSurface(surface,u=uv[0],v=uv[1],p=True)
		paramU = uv[0]
		paramV = uv[1]
		
		# Get surface point information
		pnt = mc.pointOnSurface(surface,u=paramU,v=paramV,p=True)
		normal = mc.pointOnSurface(surface,u=paramU,v=paramV,nn=True)
		tangentU = mc.pointOnSurface(surface,u=paramU,v=paramV,ntu=True)
		tangentV = mc.pointOnSurface(surface,u=paramU,v=paramV,ntv=True)
		
		# Clamp param to safe values
		minU = mc.getAttr(surface+'.minValueU')
		maxU = mc.getAttr(surface+'.maxValueU')
		minV = mc.getAttr(surface+'.minValueV')
		maxV = mc.getAttr(surface+'.maxValueV')
		if paramU < (minU+0.001): paramU = minU
		elif paramU > (maxU-0.001): paramU = maxU
		if paramV < (minV+0.001): paramV = minV
		elif paramV > (maxV-0.001): paramV = maxV
		
		# Create constraint transform
		transform = nameUtil.appendName(prefix,nameUtil.subPart['surfacePoint']+ind+nameUtil.delineator+nameUtil.node['transform'],stripNameSuffix=False)
		transform = mc.createNode('transform',n=transform)
		transformList.append(transform)
		
		# Add param attributes
		mc.addAttr(transform,ln='param',at='compound',numberOfChildren=2)
		mc.addAttr(transform,ln='paramU',at='double',min=minU,max=maxU,dv=paramU,k=True,p='param')
		mc.addAttr(transform,ln='paramV',at='double',min=minV,max=maxV,dv=paramV,k=True,p='param')
		
		# Connect to surfacePoints node
		#mc.setAttr(surfacePointsNode+'.offset['+ind+']',offsetU,offsetV,offsetN)
		mc.connectAttr(transform+'.param',surfacePointsNode+'.param['+ind+']',f=True)
		mc.connectAttr(transform+'.parentMatrix',surfacePointsNode+'.targetMatrix['+ind+']',f=True)
		
		# Connect to transform
		mc.connectAttr(surfacePointsNode+'.outTranslate['+ind+']',transform+'.translate',f=True)
		if rotate: mc.connectAttr(surfacePointsNode+'.outRotate['+ind+']',transform+'.rotate',f=True)
	
	# Return result
	return (surfacePointsNode,transformList)

def getNextAvailableIndex(surfacePointsNode):
	'''
	@param surfacePointsNode: SurfacePoints node to query
	@type surfacePointsNode: str
	'''
	# Get MObject
	sel = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(surfacePointsNode,sel)
	obj = OpenMaya.MObject()
	sel.getDependNode(0,obj)
	
	# Get param plug
	paramPlug = OpenMaya.MFnDependencyNode(obj).findPlug('param')
	
	# Get valid index list
	indexList = OpenMaya.MIntArray()
	paramPlug.getExistingArrayAttributeIndices(indexList)
	
	# Determine next available index
	nextIndex = 0
	if indexList.length(): nextIndex = indexList[-1] + 1
	
	# Return next available index
	return nextIndex
