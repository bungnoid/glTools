import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.selection

componentFilter = [28,30,31,32,34,35,36,37,38,46,47]

meshFilter = [31,32,34,35]
subdFilter = [36,37,38]
nurbsFilter = [28,30]
curveFilter = [28,30,40]
surfaceFilter = [28,30,42]

meshVertFilter = 31
meshEdgeFilter = 32
meshFaceFilter = 34

latticeFilter = 46
particleFilter = 47

def isComponent(component):
	'''
	Return True if specified object is a valid shape component.
	Else return False.
	@param component: Object to test as component
	@type component: str
	'''
	# Check Components
	return bool(mc.filterExpand(component,ex=True,sm=componentFilter))

def isIntermediateShapeComponent(component):
	'''
	Return True if specified object is a valid component of an intermediate shape.
	Else return False.
	@param component: Object to test as intermediate shape component
	@type component: str
	'''
	# Check Component
	if not isComponent(component): return False
	
	# Check Object
	componentObj = mc.ls(component,o=True)[0]
	
	# Check Intermediate Object
	if mc.attributeQuery('intermediateObject',n=componentObj,ex=True):
		if mc.getAttr(componentObj+'.intermediateObject'):
			return True
	
	# Return Result
	return False

def getComponentCount(geometry):
	'''
	Returns the number of individual components for a given geometry.
	@param geometry: geometry to query
	@type geometry: str
	'''
	# Check geometry
	if not mc.objExists(geometry):
		raise Exception('Object '+geometry+' does not exist!')
	
	# Check shape
	geomObj = glTools.utils.base.getMObject(geometry)
	if geomObj.hasFn(OpenMaya.MFn.kTransform):
		geomShape = mc.listRelatives(geometry,s=True,ni=True,pa=True)[0]
	
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
	# Get component selection elelments
	comp = glTools.utils.selection.getSelectionElement(component,element=0)
	# Get index from component object
	indexList =  OpenMaya.MIntArray()
	componentFn = OpenMaya.MFnSingleIndexedComponent(comp[1])
	componentFn.getElements(indexList)
	# Return result
	return indexList[0]

def singleIndexList(componentList):
	'''
	Return a list of component indices for the specified component list.
	Only works for single indexed components, such as mesh vertices, faces, edges or NURBS curve CV's.
	All components should be from the same shape/geometry. If components of multiple shapes are selected, only components of the first shape will be used.
	@param componentList: The component list to return the indices for.
	@type componentList: list
	'''
	# Get Selection Elements
	sel = glTools.utils.selection.getSelectionElement(componentList,element=0)
	# Get Component Indices
	indexList =  OpenMaya.MIntArray()
	componentFn = OpenMaya.MFnSingleIndexedComponent(sel[1])
	componentFn.getElements(indexList)
	# Return result
	return list(indexList)

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
	if not componentList: componentList = mc.ls(sl=True,fl=True) or []
	if not componentList: return []
	
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
		
		# =======================
		# - Check Geometry Type -
		# =======================
		
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
	
	# Return Result
	return componentIndexList

def getSingleIndexComponentList(componentList=[]):
	'''
	Convert a 2 or 3 value component index to a single value index.
	Returns a flat list of integer component index values.
	@param componentList: A list of component names. if empty will default to selection.
	@type componentList: list
	'''
	# Check Component List
	if not componentList: componentList = mc.ls(sl=True)
	if not componentList: return singleIndexList
	
	# Initialize Result
	singleIndexList = {}
	
	# Get Component Selection
	componentSel = getComponentIndexList(componentList)
	
	# Iterate Through Shape Keys
	shapeList = componentSel.keys()
	for shape in shapeList:
		
		# Get Shape Component Indices
		indexList = componentSel[shape]
		
		# Check Transform
		if mc.objectType(shape) == 'transform':
			shape = mc.listRelatives(shape,ni=True,pa=True)[0]
		
		# Check Mesh or Curve
		if (mc.objectType(shape) == 'mesh') or (mc.objectType(shape) == 'nurbsCurve'):
			singleIndexList[shape] = indexList
			
		# Check Surface
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
			
		# Check Lattice
		elif (mc.objectType(shape) == 'lattice'):
			sDiv = mc.getAttr(shape+'.sDivisions')
			tDiv = mc.getAttr(shape+'.tDivisions')
			singleIndexList[shape] = [i[0]+(i[1]*sDiv)+(i[2]*sDiv*tDiv) for i in indexList]
	
	# Return Result
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
	# Get Shape
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
	
	# Return Result
	return None
	
def getSingleIndexFromComponent(component):
	'''
	Convert a 2 or 3 value index to a single value index.
	Returns the single element index of the given component.
	@param component: Component to get single index from.
	@type component: str
	'''
	# Check component
	if not mc.objExists(component):
		raise Exception('Component "'+component+'" does not exist!')
	
	# Get selection elements
	comp = glTools.utils.selection.getSelectionElement(component)
	shape = comp[0].partialPathName()
	shapeType = mc.objectType(shape)
	
	# Check Mesh
	if shapeType == 'mesh':
		indexList = OpenMaya.MIntArray()
		componentFn = OpenMaya.MFnSingleIndexedComponent(comp[1])
		componentFn.getElements(indexList)
		# Return Index
		return indexList[0]
		
	# Nurbs Curve
	if shapeType == 'nurbsCurve':
		indexList = OpenMaya.MIntArray()
		componentFn = OpenMaya.MFnSingleIndexedComponent(comp[1])
		componentFn.getElements(indexList)
		# Return Index
		return indexList[0]
	
	# Nurbs Surface
	if shapeType == 'nurbsSurface':
		indexListU = OpenMaya.MIntArray()
		indexListV = OpenMaya.MIntArray()
		componentFn = OpenMaya.MFnDoubleIndexedComponent(comp[1])
		componentFn.getElements(indexListU,indexListV)
		# Get Surface Info
		surfFn = OpenMaya.MFnNurbsSurface(comp[0])
		numV = surfFn.numCVsInV()
		if surfFn.formInV() == surfFn.kPeriodic:
			numV -= surfFn.degreeV()
		# Return Index
		return (indexListU[0] * numV) + indexListV[0]
	
	# Lattice
	if shapeType == 'lattice':
		indexListS = OpenMaya.MIntArray()
		indexListT = OpenMaya.MIntArray()
		indexListU = OpenMaya.MIntArray()
		componentFn = OpenMaya.MFnTripleIndexedComponent(comp[1])
		componentFn.getElements(indexListS,indexListT,indexListU)
		# Get Lattice Info
		sDiv = mc.getAttr(shape+'.sDivisions')
		tDiv = mc.getAttr(shape+'.tDivisions')
		# Return Index
		return (indexListS[0] + (indexListT[0] * sDiv) + (indexListU[0] * sdiv * tDiv) )

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
	if mc.objectType(obj) == 'mesh':
		print('Component specified is a mesh vertex! No multi index information for single element indices!!')
		return [index]
	
	# Nurbs Curve
	if mc.objectType(obj) == 'nurbsCurve':
		print('Component specified is a curve CV! No multi index information for single element indices!!')
		return [index]
	
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
	@param geometry: Geometry to return components for
	@type geometry: str
	@param componentIndexList: Component indices to return names for. If empty, all components will be returned
	@type componentIndexList: list
	'''
	# Check object
	if not mc.objExists(geometry):
		raise Exception('Object '+geometry+' does not exist!')
	
	# Check transform
	mObj = glTools.utils.base.getMObject(geometry)
	if mObj.hasFn(OpenMaya.MFn.kTransform):
		geometry = glTools.utils.selection.getShapes(geometry,True,False)
		if geometry: geometry = geometry[0]
		else: raise Exception('Object '+geometry+' is not a valid geometry object!')
	
	# Check type
	mObj = glTools.utils.base.getMObject(geometry)
	if not mObj.hasFn(OpenMaya.MFn.kShape):
		raise Exception('Object "'+geometry+'" is not a valid geometry object!')
	
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
		raise Exception('Invalid pivot option - "'+pivot+'"! Specify "object", "center" or "user"!!')
	
	# Rotate Components
	mc.rotate(rotate[0],rotate[1],rotate[2],componentList,p=piv,ws=worldSpace,os=not worldSpace)

def scale(componentList=[],scale=(1.0,1.0,1.0),pivot='center',userPivot=(0,0,0),worldSpace=False):
	'''
	Scale the specified components based on the input argument values.
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
		shape = mc.listRelatives(componentList[0],p=True,pa=True)[0]
		obj = mc.listRelatives(shape,p=True,type='transform',pa=True)[0]
		piv = mc.xform(obj,q=True,ws=True,rp=True)
	elif pivot == 'user':
		piv = userPivot
	else:
		raise Exception('Invalid pivot option - "'+pivot+'"! Specify "object", "center" or "user"!!')
	
	# Scale Components
	if worldSpace:
		for component in componentList:
			pnt = mc.pointPosition(component)
			offset = (pnt[0]-piv[0],pnt[1]-piv[1],pnt[2]-piv[2])
			pnt = (piv[0]+offset[0]*scale[0],piv[1]+offset[1]*scale[1],piv[2]+offset[2]*scale[2])
			mc.move(pnt[0],pnt[1],pnt[2],component,a=True,ws=True)
	else:
		mc.scale(scale[0],scale[1],scale[2],componentList,p=piv)

def expandVertexSelection(vtxSel,useFace=False):
	'''
	Expand the specified vertex selection list.
	@param vtxSel: Vertex selection list to expand.
	@type vtxSel: list
	@param useFace: Expand the selection using face connection instead of edge connection.
	@type useFace: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Vertex Selection
	vtxSel = mc.filterExpand(vtxSel,sm=31)
	if not vtxSel: raise Exception('Invalid vertex selection!')
	
	# ====================
	# - Expand Selection -
	# ====================
	
	conSel = []
	if useFace:
		# Convert To Faces
		conSel = mc.polyListComponentConversion(vtxSel,fv=True,tf=True,internal=False)
	else:
		# Convert To Faces
		conSel = mc.polyListComponentConversion(vtxSel,fv=True,te=True,internal=False)
	# Convert To Vertex
	newSel = mc.polyListComponentConversion(conSel,ff=True,fe=True,tv=True,internal=False)
	
	# =================
	# - Return Result -
	# =================
	
	return newSel

def shrinkVertexSelection(vtxSel):
	'''
	Shrink the specified vertex selection list.
	@param vtxSel: Vertex selection list to expand.
	@type vtxSel: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Vertex Selection
	vtxSel = mc.filterExpand(vtxSel,sm=31)
	if not vtxSel: raise Exception('Invalid vertex selection!')
	
	# ====================
	# - Shrink Selection -
	# ====================
	
	# Convert To Faces
	conSel = mc.polyListComponentConversion(vtxSel,fv=True,tf=True,internal=True)
	# Convert To Vertex
	newSel = mc.polyListComponentConversion(conSel,ff=True,fe=True,tv=True,internal=True)
	
	# =================
	# - Return Result -
	# =================
	
	return newSel

def removeIntermediateShapeComponents(componentList):
	'''
	Return a copy of the specified component list with all intermediate shape components removed.
	@param componentList: List of components to remove intermediate shape components from.
	@type componentList: list
	'''
	# Check Component List
	if not componentList: return []
	
	# Remove Intermediate Shape Components
	outComponentList = [i for i in componentList if not isIntermediateShapeComponent(i)]
	
	# Return Result
	return outComponentList

def getNonIntermediateShapeComponent(component):
	'''
	Return the coresponding non-intermediate shape components for the spceified intermediate shape component.
	@param component: Intermediate shape component to get non-intermediate equivalent from.
	@type component: str
	'''
	# Check Component
	if not isComponent(component):
		raise Exception('Object "'+component+'" is not a valid shape component!')
	
	# Check Intermediate Shape Component
	if not isIntermediateShapeComponent(component):
		return component
	
	# Get Non-Intermediate Equivalent
	componentObj = mc.ls(component,o=True)[0]
	componentShape = componentObj
	componentObj = mc.listRelatives(componentShape,p=True,pa=True)[0]
	componentOut = mc.listRelatives(componentObj,s=True,ni=True,pa=True)
	if not componentOut:
		raise Exception('Unable to determine non-intermediate equivalent component!')
	nonIntComponent = component.replace(componentShape,componentOut[0])
	
	# Return Result
	return nonIntComponent

def replaceIntermediateShapeComponents(componentList):
	'''
	Return a copy of the specified component list with all intermediate shape components replaced with non-intermediate equivalents.
	@param componentList: List of components to replace intermediate shape components from.
	@type componentList: list
	'''
	# Check Component List
	if not componentList: return []
	
	# Replace Intermediate Shape Components
	outComponentList = []
	for i in componentList:
		if isIntermediateShapeComponent(i):
			nonIntComponent = getNonIntermediateShapeComponent(i)
			if not nonIntComponent in outComponentList:
				outComponentList.append(nonIntComponent)
		else:
			if not i in outComponentList:
				outComponentList.append(i)
	
	# Return Result
	return outComponentList
