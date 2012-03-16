import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.selection

def getComponentCount(geometry):
	'''
	Returns the number of individual components for a given geometry.
	@param geometry: geometry to query
	@type geometry: str
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise UserInputError('Object '+geometry+' does not exist!')
	
	# Check shape
	geomObj = glTools.utils.base.getMObject(geometry)
	if geomObj.hasFn(OpenMaya.MFn.kTransform):
		geomShape = mc.listRelatives(geometry,s=True,ni=True)[0]
	
	# Get geometry path
	geomPath = glTools.utils.base.getMDagPath(geometry)
	# Initialize MItGeometry
	geomIt = OpenMaya.MItGeometry(geomPath)
	
	# Return result
	return geomIt.count()

def getCenter(componentList=[]):
	'''
	Return the world center of the specified components
	@param componentList: List of components to find the center of
	@type componentList: list
	'''
	# Check componentList
	if not componentList: componentList = mc.ls(sl=True)
	componentList = mc.ls(componentList,fl=True)
	
	# Initialize position
	pos = [0.0,0.0,0.0]
	
	# Append component position
	for component in componentList:
		pnt = mc.pointPosition(component)
		pos[0] += pnt[0]
		pos[1] += pnt[1]
		pos[2] += pnt[2]
	
	# Average position
	if componentList:
		componentLen = len(componentList)
		pos[0] /= componentLen
		pos[1] /= componentLen
		pos[2] /= componentLen
	
	# Return result
	return (pos[0],pos[1],pos[2])

def index(component):
	'''
	Return the single index for the given component
	@param component: The component to return the index of
	@type component: str
	'''
	# Initialize wrapper objects
	compObj = OpenMaya.MObject()
	objPath = OpenMaya.MDagPath()
	indexList = OpenMaya.MIntArray()
	selectionList = OpenMaya.MSelectionList()
	# Get component as selection
	OpenMaya.MGlobal.getSelectionListByName(component,selectionList)
	selectionList.getDagPath(0,objPath,compObj)
	# Get index from component object
	componentFn = OpenMaya.MFnSingleIndexedComponent(compObj)
	componentFn.getElements(indexList)
	index = indexList[0]
	# Return result
	return index

def getComponentIndexList(componentList=[]):
	'''
	Return an list of integer component index values
	@param componentList: A list of component names. if empty will default to selection.
	@type componentList: list
	'''
	# Initialize return dictionary
	componentIndexList = {}
	
	# Check string input
	if type(componentList) == str or type(componentList) == unicode:
		componentList = [componentList]
	
	# Get selection if componentList is empty
	if not componentList: componentList = mc.ls(sl=1)
	if not componentList: return componentIndexList
	
	# Get MSelectionList
	selList = OpenMaya.MSelectionList()
	for i in componentList: selList.add(str(i))
	
	# Iterate through selection list
	selPath = OpenMaya.MDagPath()
	componentObj = OpenMaya.MObject()
	componentSelList = OpenMaya.MSelectionList()
	for i in range(selList.length()):
		# Check for valid component selection
		selList.getDagPath(i,selPath,componentObj)
		if componentObj.isNull():
			# Clear component MSelectionList
			componentSelList.clear()
			# Get current object name
			objName = selPath.partialPathName()
			
			# Transform
			if selPath.apiType() == OpenMaya.MFn.kTransform:
				numShapesUtil = OpenMaya.MScriptUtil()
				numShapesUtil.createFromInt(0)
				numShapesPtr = numShapesUtil.asUintPtr()
				selPath.numberOfShapesDirectlyBelow(numShapesPtr)
				numShapes = OpenMaya.MScriptUtil(numShapesPtr).asUint()
				selPath.extendToShapeDirectlyBelow(numShapes-1)
			
			# Mesh
			if selPath.apiType() == OpenMaya.MFn.kMesh:
				meshFn = OpenMaya.MFnMesh(selPath.node())
				vtxCount = meshFn.numVertices()
				componentSelList.add(objName+'.vtx[0:'+str(vtxCount-1)+']')
			# Curve
			elif selPath.apiType() == OpenMaya.MFn.kNurbsCurve:
				curveFn = OpenMaya.MFnNurbsCurve(selPath.node())
				componentSelList.add(objName+'.cv[0:'+str(curveFn.numCVs()-1)+']')
			# Surface
			elif selPath.apiType() == OpenMaya.MFn.kNurbsSurface:
				surfaceFn = OpenMaya.MFnNurbsSurface(selPath.node())
				componentSelList.add(objName+'.cv[0:'+str(surfaceFn.numCVsInU()-1)+'][0:'+str(surfaceFn.numCVsInV()-1)+']')
			# Lattice
			elif selPath.apiType() == OpenMaya.MFn.kLattice:
				sDiv = mc.getAttr(objName+'.sDivisions')
				tDiv = mc.getAttr(objName+'.tDivisions')
				uDiv = mc.getAttr(objName+'.uDivisions')
				componentSelList.add(objName+'.pt[0:'+str(sDiv - 1)+'][0:'+str(tDiv - 1)+'][0:'+str(uDiv - 1)+']')
			
			# Get object component MObject
			componentSelList.getDagPath(0,selPath,componentObj)
		
		# Check shape type
		#------------------
		# MESH / NURBS CURVE
		if (selPath.apiType() == OpenMaya.MFn.kMesh) or (selPath.apiType() == OpenMaya.MFn.kNurbsCurve):
			indexList = OpenMaya.MIntArray()
			componentFn = OpenMaya.MFnSingleIndexedComponent(componentObj)
			componentFn.getElements(indexList)
			componentIndexList[selPath.partialPathName()] = list(indexList)
		# NURBS SURFACE
		if selPath.apiType() == OpenMaya.MFn.kNurbsSurface:
			indexListU = OpenMaya.MIntArray()
			indexListV = OpenMaya.MIntArray()
			componentFn = OpenMaya.MFnDoubleIndexedComponent(componentObj)
			componentFn.getElements(indexListU,indexListV)
			componentIndexList[selPath.partialPathName()] = zip(list(indexListU),list(indexListV))
		# LATTICE
		if selPath.apiType() == OpenMaya.MFn.kLattice:
			indexListS = OpenMaya.MIntArray()
			indexListT = OpenMaya.MIntArray()
			indexListU = OpenMaya.MIntArray()
			componentFn = OpenMaya.MFnTripleIndexedComponent(componentObj)
			componentFn.getElements(indexListS,indexListT,indexListU)
			componentIndexList[selPath.partialPathName()] = zip(list(indexListS),list(indexListT),list(indexListU))
	
	# Return dictionary
	return componentIndexList

def getSingleIndexComponentList(componentList=[]):
	'''
	Convert a 2 or 3 value component index to a single value index.
	Returns a flat list of integer component index values.
	@param componentList: A list of component names. if empty will default to selection.
	@type componentList: list
	'''
	# Initialize return dictionary
	singleIndexList = {}
	
	# Get selection if componentList is empty
	if not componentList: componentList = mc.ls(sl=True)
	if not componentList: return singleIndexList
	
	# Get component selection
	componentSel = getComponentIndexList(componentList)
	
	# Iterate through shape keys
	shapeList = componentSel.keys()
	for shape in shapeList:
		indexList = componentSel[shape]
		# Check transform
		if mc.objectType(shape) == 'transform':
			shape = mc.listRelatives(shape,ni=True)[0]
		# Check mesh or curve
		if (mc.objectType(shape) == 'mesh') or (mc.objectType(shape) == 'nurbsCurve'):
			singleIndexList[shape] = indexList
		# Check surface
		elif mc.objectType(shape) == 'nurbsSurface':
			# Get nurbsSurface function set
			surfList = OpenMaya.MSelectionList()
			surfObj = OpenMaya.MObject()
			OpenMaya.MGlobal.getSelectionListByName(shape,surfList)
			surfList.getDependNode(0,surfObj)
			surfFn = OpenMaya.MFnNurbsSurface(surfObj)
			# CV count in V direction
			numV = surfFn.numCVsInV()
			# Check for periodic surface
			if surfFn.formInV() == surfFn.kPeriodic: numV -= surfFn.degreeV()
			singleIndexList[shape] = [(i[0]*numV)+i[1] for i in indexList]
		# Check lattice
		elif (mc.objectType(shape) == 'lattice'):
			sDiv = mc.getAttr(shape+'.sDivisions')
			tDiv = mc.getAttr(shape+'.tDivisions')
			singleIndexList[shape] = [i[0]+(i[1]*sDiv)+(i[2]*sdiv*tDiv) for i in indexList]
	
	# Return result
	return singleIndexList

def getSingleIndex(obj,index):
	'''
	Convert a 2 or 3 value index to a single value index.
	Returns the single element index of the given component.
	@param obj: Object parent of component.
	@type obj: str
	@param index: Multi element index of component.
	@type index: list
	'''
	# Get shape node
	if mc.objectType(obj) == 'transform': 
		obj = glTools.utils.selection.getShapes(obj,True,False)[0]
	# Mesh
	if mc.objectType(obj) == 'mesh': return index
	# Nurbs Curve
	if mc.objectType(obj) == 'nurbsCurve': return index
	# Nurbs Surface
	if mc.objectType(obj) == 'nurbsSurface':
		# Get nurbsSurface function set
		surfList = OpenMaya.MSelectionList()
		surfObj = OpenMaya.MObject()
		OpenMaya.MGlobal.getSelectionListByName(obj,surfList)
		surfList.getDependNode(0,surfObj)
		surfFn = OpenMaya.MFnNurbsSurface(surfObj)
		# CV count in U an V directions
		numV = surfFn.numCVsInV()
		# Check for periodic surface
		if surfFn.formInV() == surfFn.kPeriodic:
			numV -= surfFn.degreeV()
		# Get Single Index
		return (index[0] * numV) + index[1]
	# Lattice
	elif mc.objectType(obj) == 'lattice':
		sDiv = mc.getAttr(obj+'.sDivisions')
		tDiv = mc.getAttr(obj+'.tDivisions')
		return (index[0] + (index[1] * sDiv) + (index[2] * sdiv * tDiv) )

def getMultiIndex(obj,index):
	'''
	Convert a single element index to a 2 or 3 element index .
	Returns the multi element index of the given component.
	@param obj: Object parent of component.
	@type obj: str
	@param index: Single element index of component.
	@type index: list
	'''
	# Get shape node
	if mc.objectType(obj) == 'transform':
		obj = glTools.utils.selection.getShapes(obj,True,False)[0]
	
	# Mesh
	if mc.objectType(obj) == 'mesh': return [index]
	
	# Nurbs Curve
	if mc.objectType(obj) == 'nurbsCurve':return [index]
	
	# Nurbs Surface
	if mc.objectType(obj) == 'nurbsSurface':
		# Spans / Degree / Form
		spansV = mc.getAttr(obj+'.spansV')
		degreeV = mc.getAttr(obj+'.degreeV')
		formV = mc.getAttr(obj+'.formV')
		if formV: spansV -= degreeV
		# Get Multi Index
		uIndex = int(index/(spansV+degreeV))
		vIndex = index%(spansV+degreeV)
		return [uIndex,vIndex]
	
	# Lattice
	elif mc.objectType(obj) == 'lattice':
		sDiv = mc.getAttr(obj+'.sDivisions')
		tDiv = mc.getAttr(obj+'.tDivisions')
		uDiv = mc.getAttr(obj+'.uDivisions')
		sInd = int(index%sDiv)
		tInd = int((index/sDiv)%tDiv)
		uInd = int((index/(sDiv*tDiv))%uDiv)
		return [sInd,tInd,uInd]

def getComponentStrList(geometry,componentIndexList=[]):
	'''
	Return a string list containing all the component points of the specified geometry object
	@param geometry: Geometry whose components to return
	@type geometry: str
	@param componentIndexList: Component indices to return names for. If empty, all components will be returned
	@type componentIndexList: list
	'''
	# Check object
	if not mc.objExists(geometry):
		raise UserInputError('Object '+geometry+' does not exist!')
	
	# Check transform
	mObj = glTools.utils.base.getMObject(geometry)
	if mObj.hasFn(OpenMaya.MFn.kTransform):
		geometry = glTools.utils.selection.getShapes(geometry,True,False)
		if geometry: geometry = geometry[0]
		else: raise UserInputError('Object '+geometry+' is not a valid geometry object!')
	
	# Check type
	mObj = glTools.utils.base.getMObject(geometry)
	if not mObj.hasFn(OpenMaya.MFn.kShape):
		raise UserInputError('Object "'+geometry+'" is not a valid geometry object!')
	
	# Get component multiIndex list
	componentStrList = []
	componentList = []
	if not componentIndexList:
		componentList = getComponentIndexList(geometry)[geometry]
	else:
		for i in componentIndexList:
			index = getMultiIndex(geometry,i)
			if len(index) == 1: componentList.append( index[0] )
			else: componentList.append( index )
	
	objType = mc.objectType(geometry)
	for i in componentList:
		# Mesh
		if objType == 'mesh':
			componentStrList.append(geometry+'.vtx['+str(i)+']')
		# Curve
		if objType == 'nurbsCurve':
			componentStrList.append(geometry+'.cv['+str(i)+']')
		# Surface
		if objType == 'nurbsSurface':
			componentStrList.append(geometry+'.cv['+str(i[0])+']['+str(i[1])+']')
		# Lattice
		if objType == 'lattice':
			componentStrList.append(geometry+'.pt['+str(i[0])+']['+str(i[1])+']['+str(i[2])+']')
	
	# Return Component String List
	return componentStrList

def rotate(componentList=[],rotate=(0.0,0.0,0.0),pivot='center',userPivot=(0,0,0),worldSpace=False):
	'''
	Rotate a list of components based on the input arguments
	@param componentList: List of components to rotate
	@type componentList: list
	@param rotate: Rotation in degree to apply to the component list
	@type rotate: tuple
	@param pivot: Pivot option for rotation. Valid pivot options are "object", "center" and "user".
	@type pivot: str
	@param userPivot: Pivot position to use if the pivot option is set to "user".
	@type userPivot: tuple
	@param worldSpace: Perform rotation about global world-space axis.
	@type worldSpace: bool
	'''
	# Check componentList
	if not componentList: componentList = mc.ls(componentList,fl=True)
	
	# Determine rotation pivot
	piv = (0,0,0)
	if pivot == 'center':
		piv = getCenter(componentList)
	elif pivot == 'object':
		obj = componentList[0].split('.')[0]
		piv = mc.xform(obj,q=True,ws=True,rp=True)
	elif pivot == 'user':
		piv = userPivot
	else:
		raise UserInputError('Invalid pivot option - "'+pivot+'"! Specify "object", "center" or "user"!!')
	
	# Rotate components
	mc.rotate(rotate[0],rotate[1],rotate[2],componentList,p=piv,ws=worldSpace,os=not worldSpace)

def scale(componentList=[],scale=(1.0,1.0,1.0),pivot='center',userPivot=(0,0,0),worldSpace=False):
	'''
	@param componentList: List of components to scale
	@type componentList: list
	@param scale: Scale to apply to the component list
	@type scale: tuple
	@param pivot: Pivot option for scale. Valid pivot options are "object", "center" and "user".
	@type pivot: str
	@param userPivot: Pivot position to use if the pivot option is set to "user".
	@type userPivot: tuple
	@param worldSpace: Perform scaling about global world-space axis.
	@type worldSpace: bool
	'''
	# Check componentList
	if not componentList: componentList = mc.ls(componentList,fl=True)
	
	# Determine rotation pivot
	piv = (0,0,0)
	if pivot == 'center':
		piv = getCenter(componentList)
	elif pivot == 'object':
		shape = mc.listRelatives(componentList[0],p=True)[0]
		obj = mc.listRelatives(shape,p=True,type='transform')[0]
		piv = mc.xform(obj,q=True,ws=True,rp=True)
	elif pivot == 'user':
		piv = userPivot
	else:
		raise UserInputError('Invalid pivot option - "'+pivot+'"! Specify "object", "center" or "user"!!')
	
	# Scale components
	if worldSpace:
		for component in componentList:
			pnt = mc.pointPosition(component)
			offset = (pnt[0]-piv[0],pnt[1]-piv[1],pnt[2]-piv[2])
			pnt = (piv[0]+offset[0]*scale[0],piv[1]+offset[1]*scale[1],piv[2]+offset[2]*scale[2])
			mc.move(pnt[0],pnt[1],pnt[2],component,a=True,ws=True)
	else:
		mc.scale(scale[0],scale[1],scale[2],componentList,p=piv)
