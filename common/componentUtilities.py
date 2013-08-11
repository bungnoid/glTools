import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import selectionUtilities

# Create exception class
class UserInputError(Exception): pass

class ComponentUtilities(object):
	
	def __init__(self):
		self.selectionUtils = selectionUtilities.SelectionUtilities()
		self.geometry = ['mesh','nurbsCurve','nurbsSurface','lattice']
	
	def getComponentIndexList(self,componentList=[]):
		'''
		getComponentIndex(componentList=[]): return an list of integer component index values
		@param componentList: A list of component names. if empty will default to selection.
		@type componentList: list
		'''
		
		# Clear componentIndexList
		componentIndexList = {}
		
		# Store original selection list
		originalSel = mc.ls(sl=1)
		mc.select(cl=1)
		
		# Get selection if componentList is empty
		if not componentList: componentList = originalSel
		
		# Set active selection
		if componentList:
			try: mc.select(componentList)
			except: raise UserInputError('Input list invalid! Object(s) does not exist!!')
		else:
			return componentIndexList
		
		# Get MSelectionList
		selList = OpenMaya.MSelectionList()
		OpenMaya.MGlobal.getActiveSelectionList(selList)
		
		# Iterate through selection list
		selPath = OpenMaya.MDagPath()
		componentObj = OpenMaya.MObject()
		for i in range(selList.length()):
			
			selList.getDagPath(i,selPath,componentObj)
			
			# Check for valid component selection
			if componentObj.isNull():
				
				# Create new MSelectionList
				componentSelList = OpenMaya.MSelectionList()
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
					mc.select(objName+'.vtx[0:'+str(vtxCount-1)+']')
					OpenMaya.MGlobal.getActiveSelectionList(componentSelList)
				
				# Curve
				elif selPath.apiType() == OpenMaya.MFn.kNurbsCurve:
					curveFn = OpenMaya.MFnNurbsCurve(selPath.node())
					cvCount = curveFn.numCVs()
					mc.select(objName+'.cv[0:'+str(cvCount-1)+']')
					OpenMaya.MGlobal.getActiveSelectionList(componentSelList)
				
				# Surface
				elif selPath.apiType() == OpenMaya.MFn.kNurbsSurface:
					surfaceFn = OpenMaya.MFnNurbsSurface(selPath.node())
					uCvCount = surfaceFn.numCVsInU()
					vCvCount = surfaceFn.numCVsInV()
					mc.select(objName+'.cv[0:'+str(uCvCount-1)+'][0:'+str(vCvCount-1)+']')
					OpenMaya.MGlobal.getActiveSelectionList(componentSelList)
				
				# Lattice
				elif selPath.apiType() == OpenMaya.MFn.kLattice:
					sDiv = mc.getAttr(objName+'.sDivisions')
					tDiv = mc.getAttr(objName+'.tDivisions')
					uDiv = mc.getAttr(objName+'.uDivisions')
					mc.select(objName+'.pt[0:'+str(sDiv - 1)+'][0:'+str(tDiv - 1)+'][0:'+str(uDiv - 1)+']')
					OpenMaya.MGlobal.getActiveSelectionList(componentSelList)
					
				componentSelList.getDagPath(0,selPath,componentObj)
			
			# Check shape type
			#------------------
			
			# MESH / NURBS CURVE
			if (selPath.apiType() == OpenMaya.MFn.kMesh) or (selPath.apiType() == OpenMaya.MFn.kNurbsCurve):
				indexList = OpenMaya.MIntArray()
				componentFn = OpenMaya.MFnSingleIndexedComponent(componentObj)
				componentFn.getElements(indexList)
				if indexList.length():
					componentIndexList[selPath.partialPathName()] = []
					for i in range(indexList.length()):
						componentIndexList[selPath.partialPathName()].append(indexList[i])
			# NURBS SURFACE
			if selPath.apiType() == OpenMaya.MFn.kNurbsSurface: # Mesh
				indexListU = OpenMaya.MIntArray()
				indexListV = OpenMaya.MIntArray()
				componentFn = OpenMaya.MFnDoubleIndexedComponent(componentObj)
				componentFn.getElements(indexListU,indexListV)
				if indexListU.length() and indexListV.length():
					componentIndexList[selPath.partialPathName()] = []
					for i in range(indexListU.length()):
						componentIndexList[selPath.partialPathName()].append([indexListU[i],indexListV[i]])
			# LATTICE
			if selPath.apiType() == OpenMaya.MFn.kLattice: # Mesh
				indexListS = OpenMaya.MIntArray()
				indexListT = OpenMaya.MIntArray()
				indexListU = OpenMaya.MIntArray()
				componentFn = OpenMaya.MFnTripleIndexedComponent(componentObj)
				componentFn.getElements(indexListS,indexListT,indexListU)
				if indexListS.length() and indexListT.length() and indexListU.length():
					componentIndexList[selPath.partialPathName()] = []
					for i in range(indexListS.length()):
						componentIndexList[selPath.partialPathName()].append([indexListS[i],indexListT[i],indexListU[i]])
		
		# Restore original selection
		mc.select(cl=1)
		if type(originalSel) == list:
			if len(originalSel): mc.select(originalSel)
		
		# Return dictionary
		return componentIndexList
		
	
	def getSingleIndexComponentList(self,componentList=[]):
		'''
		Convert a 2 or 3 value index to a single value index.
		getSingleIndexComponentList(componentList=[]): Returns a flat list of integer component index values.
		
		@param componentList: A list of component names. if empty will default to selection.
		@type componentList: list
		'''
		
		# Clear flattenedIndexList
		singleIndexList = {}
		
		# Get selection if componentList is empty
		if not componentList: componentList = mc.ls(sl=True,fl=True)
		
		# Set active selection
		#if componentList: mc.select(componentList)
		#else: return {}
		if not componentList: return singleIndexList
		
		# Get component selection
		componentSel = self.getComponentIndexList(componentList)
		
		# Iterate through shape keys
		shapes = componentSel.keys()
		for shape in shapes:
			indexList = componentSel[shape]
			
			if mc.objectType(shape) == 'transform':
				shape = self.selectionUtils.getShapes(shape)[0]
			
			if (mc.objectType(shape) == 'mesh') or (mc.objectType(shape) == 'nurbsCurve'):
				singleIndexList[shape] = indexList
			
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
				if surfFn.formInV() == surfFn.kPeriodic:
					numV -= surfFn.degreeV()
				singleIndexList[shape] = []
				for i in range(len(indexList)):
					singleIndexList[shape].append((indexList[i][0] * numV) + indexList[i][1])
				
			elif (mc.objectType(shape) == 'lattice'):
				sDiv = mc.getAttr(shape+'.sDivisions')
				tDiv = mc.getAttr(shape+'.tDivisions')
				singleIndexList[shape] = []
				for i in range(len(indexList)):
					singleIndexList[shape].append(indexList[i][0] + (indexList[i][1] * sDiv) + (indexList[i][2] * sdiv * tDiv) )
		
		# Return result
		return singleIndexList
	
	def getSingleIndex(self,obj,index):
		'''
		Convert a 2 or 3 value index to a single value index.
		getSingleIndex(obj,index=[]): Returns the single element index of the given component.
		
		@param obj: Object parent of component.
		@type obj: str
		@param index: Multi element index of component.
		@type index: list
		'''
		
		# Get shape node
		if mc.objectType(obj) == 'transform': 
			obj = self.selectionUtils.getShapes(obj)[0]
		
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
	
	
	def getMultiIndex(self,obj,index):
		'''
		Convert a single element index to a 2 or 3 element index .
		getMultiIndex(obj,index): Returns the multi element index of the given component.
		
		@param obj: Object parent of component.
		@type obj: str
		@param index: Single element index of component.
		@type index: list
		'''
		
		# Get shape node
		if mc.objectType(obj) == 'transform':
			obj = self.selectionUtils.getShapes(obj)[0]
		
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
	
	
	def getComponentCount(self,obj):
		'''
		getComponentCount(obj): Returns the number of individual components for a given object.
		@param obj: Object to query
		@type componentList: str
		'''
		# Get component index list
		componentIndexList = self.getComponentIndexList([obj])
		# return component list length
		return len(componentIndexList[componentIndexList.keys()[0]])
	
	
	def getComponentStrList(self,obj,componentIndexList=[]):
		'''
		Return a string list containing all the component points of the specified geometry object
		@param obj: Object whose components to return
		@type obj: str
		@param componentIndexList: Component indices to return names for. If empty, all components will be returned
		@type componentIndexList: list
		'''
		# Check object
		if not mc.objExists(obj): raise UserInputError('Object '+obj+' does not exist!')
		# Check transform
		if mc.objectType(obj) == 'transform':
			try: obj = str(mc.listRelatives(obj,s=True,ni=True)[0])
			except: raise UserInputError('Object '+obj+' is not a valid geometry object!')
		
		objType = mc.objectType(obj)
		if not self.geometry.count(objType):
			raise UserInputError('Object '+obj+' is not a valid geometry object!')
		
		# Get component multiIndex list
		componentStrList = []
		componentList = []
		if not componentIndexList:
			componentList = self.getComponentIndexList(obj)[obj]
		else:
			for i in componentIndexList:
				index = self.getMultiIndex(obj,i)
				if len(index) == 1: componentList.append( index[0] )
				else: componentList.append( index )
		
		for i in componentList:
			# Mesh
			if objType == 'mesh':
				componentStrList.append(obj+'.vtx['+str(i)+']')
			# Curve
			if objType == 'nurbsCurve':
				componentStrList.append(obj+'.cv['+str(i)+']')
			# Surface
			if objType == 'nurbsSurface':
				componentStrList.append(obj+'.cv['+str(i[0])+']['+str(i[1])+']')
			# Lattice
			if objType == 'lattice':
				componentStrList.append(obj+'.pt['+str(i[0])+']['+str(i[1])+']['+str(i[2])+']')
		
		# Return Component String List
		return componentStrList