import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as OpenMaya

import glTools.utils.deformer
import glTools.utils.surface
import glTools.utils.mathUtils

import glTools.utils.arrayUtils
import glTools.utils.component
import glTools.utils.connection
import glTools.utils.selection

# Create exception class
class UserInputError(Exception): pass
class MissingPluginError(Exception): pass

class SurfaceSkinUtilities( object ):
	'''
	Utility Class for working with surfaceSkin deformers
	'''
	def __init__(self):
		'''
		Initialize SurfaceSkinUtilities class object
		'''
		# Valid transform list
		self.validTransformList = ['transform','joint']
		# Modes
		self.mode = {'replace':0,'add':1,'set':2,'remove':3}
		# Supported shape types
		self.supportedShapes = ['mesh','nurbsSurface','nurbsCurve']
		
	def verifyNode(self,surfaceSkin):
		"""
		Check the validity of the SurfaceSkin node named as an argument
		@param surfaceSkin: SurfaceSkin node to verify
		@type surfaceSkin: str
		"""
		# Check valid surfaceSkin input argument
		if not surfaceSkin: return False
		# Check object exists
		if not mc.objExists(surfaceSkin): return False
		# Check object is of type surfaceSkin
		if not mc.objectType(surfaceSkin) == 'surfaceSkin': return False
		# Return result
		return True
		
	#===============================================================
	# CREATION / MODIFICATION METHODS ==============================
	#===============================================================
	
	def create(self,targetList,influenceList,defaultWeightVal=1.0,maxDist=0.0,name='surfaceSkin1'):
		"""
		Create surfaceSkin deformer for the given target list or selection
		@param targetList: list of shapes to bind using surfaceSkin
		@type targetList: list
		@param influenceList: list of influences to affect surfaceSkin
		@type influenceList: list
		@param defaultWeightVal: Default influence weight value assigned to components
		@type defaultWeightVal: float
		@param maxDist: Maximum distance to search for components to affect, from the influence surface
		@type maxDist: float
		@param name: Name for new surfaceSkin node
		@type name str
		"""
		# Load plugin
		if not mc.pluginInfo('isoMuscle',l=1,q=1):
			try: mc.loadPlugin('isoMuscle')
			except: raise MissingPluginError('Unable to load surfaceSkin (isoMuscle) plugin!!')
		
		# Create Deformer
		surfaceSkin = mc.deformer(targetList,type='surfaceSkin',n=name)[0]
		# Add influences
		self.addInfluence(influenceList,surfaceSkin,defaultWeightVal,maxDist,calculatePrebind=False)
		# Ensure surfaceSkin::paintWeight and surfaceSkin::weights are paintable attrs
		self.makePaintable()
		# Return result
		return surfaceSkin
	
	def addInfluence(self,influenceList,surfaceSkin,defaultWeightVal=1.0,maxDist=0.0,calculatePrebind=False):
		'''
		Add surface influence(s) to an existing surfaceSkin deformer
		@param influenceList: List of surface influences to add to the surfaceSkin deformer
		@type influenceList: list
		@param surfaceSkin: Existing surfaceSkin deformer to add influences to
		@type surfaceSkin str
		@param defaultWeightVal: Default influence weight value for affected components
		@type defaultWeightVal: float
		@param maxDist: Maximum distance to search from the influence surface for components to affect
		@type maxDist: float
		@param calculatePrebind: Calculate surface coordinates from surface/component prebind positions
		@type calculatePrebind: bool
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		
		# Get affected geometry list
		affectedGeometry = glTools.utils.arrayUtils.dict_orderedKeyListFromValues(self.getAffectedGeometry(surfaceSkin))
		if not affectedGeometry: raise UserInputError('No geometry connected to deformer!')
		# Get next available influence index
		infIndex = self.getNextInfluenceIndex(surfaceSkin)
		
		# Iterate over influenceList
		for i in range(len(influenceList)):
			
			# Get Influence Shape
			influenceShape = self.getInfluenceShapes(influenceList[i],True,False)[0]
			# Generate Influence Base
			baseGeo = self.createInfluenceBase(influenceList[i])
			# Add Influence Attributes
			self.addInfluenceAttrs(influenceList[i])
			# Connect influence data to deformer
			self.makeInfluenceConnections(influenceList[i],surfaceSkin,transformInfluence=False,index=infIndex)
			# Connect influence base to deformer
			self.makeInfluenceBaseConnections(baseGeo,surfaceSkin,transformInfluence=False)
			# Set influence surface coordinates
			for geo in range(len(affectedGeometry)):
				self.setSurfaceCoordArray(affectedGeometry[geo],[],influenceList[i],surfaceSkin,maxDist,defaultWeightVal,calculatePrebind,'set')
			# Increment influence index
			infIndex += 1
	
	def addTransformInfluence(self,influenceList,surfaceSkin,defaultWeightVal=1.0,maxDist=0.0,calculatePrebind=False,createPrebindMatrix=True):
		'''
		Add transform influence(s) to an existing surfaceSkin deformer
		@param influenceList: List of transform influences to add to the surfaceSkin deformer
		@type influenceList: list
		@param surfaceSkin: Existing surfaceSkin deformer to add influences to
		@type surfaceSkin str
		@param defaultWeightVal: Default influence weight value for affected components
		@type defaultWeightVal: float
		@param maxDist: Maximum distance to search from the influence surface for components to affect
		@type maxDist: float
		@param calculatePrebind: Calculate surface coordinates from surface/component prebind positions
		@type calculatePrebind: bool
		@param createPrebindMatrix: Create a preBind matrix transform fro each influence
		@type createPrebindMatrix: bool
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		
		# Query affected geometry
		affectedGeometry = glTools.utils.arrayUtils.dict_orderedKeyListFromValues(self.getAffectedGeometry(surfaceSkin))
		if not affectedGeometry: raise UserInputError('No geometry connected to deformer!')
		# Get next available influence index
		infIndex = self.getNextInfluenceIndex(surfaceSkin)
		
		# Iterate influenceList
		for i in range(len(influenceList)):
			
			# Connect influence data to deformer
			self.makeInfluenceConnections(influenceList[i],surfaceSkin,transformInfluence=True,index=infIndex)
			# Set Prebind Matrix
			if createPrebindMatrix:
				# Create influence base
				baseInfluence = self.createTransformInfluenceBase(influenceList[i])
				# Connect influence base to deformer
				self.makeInfluenceBaseConnections(baseInfluence,surfaceSkin,transformInfluence=True)
			else:
				# Set BindPreMatrix from influence world matrix
				#mc.setAttr(surfaceSkin+'.influenceBaseMatrix['+str(infIndex)+']',mc.xform(influenceList[i],q=True,ws=True,m=True),type='matrix')
				cmd = 'setAttr '+surfaceSkin+'.influenceBaseMatrix['+str(infIndex)+'] -type "matrix"'
				for n in mc.getAttr(influenceList[i]+'.worldMatrix[0]'): cmd += ' '+str(n)
				mm.eval(cmd)
			
			# Set influence surface coordinates
			for geo in range(len(affectedGeometry)):
				self.setSurfaceCoordArray(affectedGeometry[geo],[],influenceList[i],surfaceSkin,maxDist,defaultWeightVal,calculatePrebind,self.mode['set'])
			
			# Increment influence index
			infIndex += 1
	
	def removeInfluence(self,influence,surfaceSkin):
		'''
		Remove an influence from an existing surfaceSkin deformer
		@param influence: The influences to remove from the surfaceSkin deformer
		@type influence: str
		@param surfaceSkin: The surfaceSkin deformer to remove the influence from
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		
		# Get affected geometry
		affectedGeometry = self.getAffectedGeometry(surfaceSkin)
		if not affectedGeometry: raise UserInputError('No geometry connected to deformer!')
		
		# Get Influence Info
		transformInf = self.isTransformInfluence(influence,surfaceSkin)
		influenceIndex = self.getInfluenceIndex(influence,surfaceSkin)
		influenceBase = self.getInfluenceBase(influence)
		
		# Iterate over affectedGeometry
		for geo in affectedGeometry.keys():
			# Clear surface data
			self.setIndexArray(geo,influence,surfaceSkin,[])
			self.setWeightArray(geo,influence,surfaceSkin,[])
			self.setCoordArray(geo,influence,surfaceSkin,[],[])
		
		# Break Influence Connections
		#--------------------------------
		if transformInf:
			# Influence Matrix
			mc.disconnectAttr(influence+'.worldMatrix[0]',surfaceSkin+'.influenceMatrix['+str(influenceIndex)+']')
			# Influence Base Matrix
			if influenceBase:
				mc.disconnectAttr(influenceBase+'.worldMatrix[0]',surfaceSkin+'.influenceBaseMatrix['+str(influenceIndex)+']')
		else:
			# Get influence shape
			influenceShape = self.getInfluenceShapes(influence,True,False)[0]
			# Get influence base shape
			influenceBaseShape = self.getInfluenceShapes(influenceBase,True,False)[0]
			
			# Surface Samples / Tangent Align
			mc.disconnectAttr(influenceShape+'.samplesU',surfaceSkin+'.surfaceSamplesU['+str(influenceIndex)+']')
			mc.disconnectAttr(influenceShape+'.samplesV',surfaceSkin+'.surfaceSamplesV['+str(influenceIndex)+']')
			mc.disconnectAttr(influenceShape+'.tangentAlign',surfaceSkin+'.tangentAlign['+str(influenceIndex)+']')
			
			# Influence Geometry
			mc.disconnectAttr(influenceShape+'.worldSpace[0]',surfaceSkin+'.influenceGeometry['+str(influenceIndex)+']')
			# Influence Matrix
			mc.disconnectAttr(influenceShape+'.parentMatrix[0]',surfaceSkin+'.influenceMatrix['+str(influenceIndex)+']')
			
			# Influence Base Geometry
			mc.disconnectAttr(influenceBaseShape+'.worldSpace[0]',surfaceSkin+'.influenceBase['+str(influenceIndex)+']')
			# InflGeometryuence Base Matrix
			mc.disconnectAttr(influenceBaseShape+'.parentMatrix[0]',surfaceSkin+'.influenceBaseMatrix['+str(influenceIndex)+']')
		
		# Delete influence base if no out-going connections exist
		if influenceBase:
			influenceBaseShape = self.getInfluenceShapes(influenceBase,True,False)[0]
			if not mc.listConnections(influenceBase,s=True,d=False) and not mc.listConnections(influenceBaseShape,s=True,d=False):
				mc.delete(influenceBase)
		else:
			mm.eval('setAttr '+surfaceSkin+'.influenceBaseMatrix['+str(influenceIndex)+'] -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
		
		# PaintTrans
		influenceList = self.getInfluenceList(surfaceSkin)
		if not influenceList:
			mc.disconnectAttr(influenceShape+'.message',surfaceSkin+'.paintTrans')
		else:
			for inf in influenceList:
				if inf == influence: continue
				paintTransConn = mc.listConnections(surfaceSkin+'.paintTrans',s=1,d=0,sh=1)
				if not paintTransConn.count(inf):
					mc.connectAttr(inf+'.message',surfaceSkin+'.paintTrans',f=1)
					break
	
	def addInfluenceAttrs(self,influence):
		'''
		Add common surface influence attributes
		@param influence: The surface influences to add attributes to
		@type influence: str
		'''
		# Get influence shape
		influenceShape = self.getInfluenceShapes(influence,True,False)[0] # Get first shape in list
		# Samples U
		if not mc.objExists(influenceShape+'.samplesU'):
			mc.addAttr(influenceShape, ln='samplesU', at='long', min=1, dv=5)
		mc.setAttr(influenceShape+'.samplesU', k=1)
		# Samples V
		if not mc.objExists(influenceShape+'.samplesV'):
			mc.addAttr(influenceShape, ln='samplesV', at='long', min=1, dv=5)
		mc.setAttr(influenceShape+'.samplesV', k=1)
		# Tanget Align
		if not mc.objExists(influenceShape+'.tangentAlign'):
			mc.addAttr(influenceShape, ln='tangentAlign', at='enum', en='Off:U:V')
		mc.setAttr(influenceShape+'.tangentAlign', k=1)
	
	def makeInfluenceConnections(self,influence,surfaceSkin,transformInfluence=False,index=-1):
		'''
		Make all neccessary influence connections to an existing surfaceSkin deformer
		@param influence: The influences to connect to the surfaceSkin node
		@type influence: str
		@param surfaceSkin: The surfaceSkin node to connect the influence to
		@type surfaceSkin: str
		@param transformInfluence: Specifies if the influence is a transform or surface influence
		@type transformInfluence: bool
		@param index: The input index to connect to. If left default will use the next available index.
		@type index: int
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Check index
		if index < 0: index = self.getNextInfluenceIndex(surfaceSkin)
		# Make connections
		if transformInfluence:
			mc.connectAttr(influence+'.worldMatrix[0]', surfaceSkin+'.influenceMatrix['+str(index)+']',f=1)
			mc.connectAttr(influence+'.message', surfaceSkin+'.paintTrans',f=1)
		else:
			influenceShape = self.getInfluenceShapes(influence)[0] # Get first shape in list
			mc.connectAttr(influenceShape+'.samplesU', surfaceSkin+'.surfaceSamplesU['+str(index)+']',f=1)
			mc.connectAttr(influenceShape+'.samplesV', surfaceSkin+'.surfaceSamplesV['+str(index)+']',f=1)
			mc.connectAttr(influenceShape+'.tangentAlign', surfaceSkin+'.tangentAlign['+str(index)+']',f=1)
			mc.connectAttr(influenceShape+'.parentMatrix[0]', surfaceSkin+'.influenceMatrix['+str(index)+']',f=1)
			mc.connectAttr(influenceShape+'.worldSpace[0]', surfaceSkin+'.influenceGeometry['+str(index)+']',f=1)
			mc.connectAttr(influenceShape+'.message', surfaceSkin+'.paintTrans',f=1)
		
	def makeInfluenceBaseConnections(self,influenceBase,surfaceSkin,transformInfluence=False):
		'''
		Make all neccessary influence base connections to an existing surfaceSkin deformer
		@param influenceBase: The influences base to connect to the surfaceSkin node
		@type influenceBase: str
		@param surfaceSkin: The surfaceSkin node to connect the influence to
		@type surfaceSkin: str
		@param transformInfluence: Specifies if the influence base is for a transform or surface influence
		@type transformInfluence: bool
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Get Influence Index
		infIndex = -1
		try:
			influence = self.getInfluenceFromBase(influenceBase)
			infIndex = self.getInfluenceIndex(influence,surfaceSkin)
		except:
			raise UserInputError('Unable to determine influence index!! Influence base "'+influenceBase+'" is not connected to a valid influence of surfaceSkin deformer "'+surfaceSkin+'"!!')
			#infIndex = self.getNextInfluenceIndex(surfaceSkin)
			#print('Cant find influence index for influence base! Determining index based on next available input index!!')
		
		# Make connections
		if transformInfluence:
			mc.connectAttr(influenceBase+'.worldMatrix[0]', surfaceSkin+'.influenceBaseMatrix['+str(infIndex)+']',f=1)
		else:
			influenceShape = self.getInfluenceShapes(influenceBase)[0] # Get first shape in list
			mc.connectAttr(influenceShape+'.parentMatrix[0]', surfaceSkin+'.influenceBaseMatrix['+str(infIndex)+']',f=1)
			mc.connectAttr(influenceShape+'.worldSpace[0]', surfaceSkin+'.influenceBase['+str(infIndex)+']',f=1)
	
	def createInfluenceBase(self,influence):
		'''
		Create influence base for surfaceSkin surface influence.
		@param influence: Name of influence object to create a base for
		@type influence: str
		'''
		# Check for existing influence base geometry
		influenceBase = self.getInfluenceBase(influence)
		if influenceBase: return influenceBase
		
		# Duplicate influence to create base
		influenceBase = mc.duplicate(influence,rr=1,rc=1,n=influence+'Base')[0]
		# Delete intermediate shapes
		influenceBaseDel = self.getInfluenceShapes(influenceBase,False,True,True)
		if influenceBaseDel: mc.delete(influenceBaseDel)
		# Delete unwanted base children
		baseChild = mc.listRelatives(influenceBase,c=True,type='transform')
		if baseChild: mc.delete(baseChild)
		
		# Turn off visibilty for influenceBase
		mc.setAttr(influenceBase+'.v',0)
		
		# Add influence base connection to influence
		self.connectBase(influence,influenceBase)
		
		# Return result
		return influenceBase
	
	def createTransformInfluenceBase(self,influence):
		'''
		Create influence base for surfaceSkin transform influence.
		@param influence: Name of influence transform to create a base for
		@type influence: str
		'''
		# Check for existing influence base transform
		infBase = self.getInfluenceBase(influence)
		if infBase: return infBase
		
		# Create empty transform node
		infBase = mc.createNode('transform',n=influence+'Base')
		# Match transforms
		mc.parent(infBase,influence)
		mc.makeIdentity(infBase,apply=True,t=1,r=1,s=1,n=0)
		# Match pivot
		piv = mc.xform(influence,q=1,ws=1,rp=1)
		mc.xform(infBase,ws=1,rp=piv,sp=piv)
		# Add influence base connection to influence
		self.connectBase(influence,infBase)
		# Parent to world
		mc.parent(infBase,w=1)
		# Return result
		return infBase
	
	def connectBase(self,influence,base):
		'''
		Connect a specified influence base to an influence
		@param influence: Name of influence to connect the base to
		@type influence: str
		@param base: Name of influence base to connect to the influence
		@type base: str
		'''
		# Add influence base connection to influence
		if not mc.objExists(influence+'.influenceBase'):
			mc.addAttr(influence, ln='influenceBase', at='message')
		mc.connectAttr(base+'.message',influence+'.influenceBase')
	
	def getInfluenceBase(self,influence):
		'''
		Return the name of the influence base connected to the specified influence
		@param influence: Name of influence to to query base information from
		@type influence: str
		'''
		if mc.objectType(influence) == 'nurbsSurface':
			influence = mc.listRelatives(influence,p=1)[0]
		if not self.validTransformList.count(mc.objectType(influence)):
			raise UserInputError('Object '+influence+' is not a valid surfaceSkin influence!')
		if not mc.objExists(influence+'.influenceBase'):
			print('Influence '+influence+' has no ".influenceBase" attribute! So it is assumed there is no influence base connection!!')
			return ''
		
		# Get connection list to influence.influenceBase attribute
		influenceBaseConnections = mc.listConnections(influence+'.influenceBase',s=1,d=0)
		if not influenceBaseConnections: return ''
		influenceBase = influenceBaseConnections[0]
		# Return result
		return influenceBase
		
	def getInfluenceFromBase(self,influenceBase):
		'''
		Return the surfaceSkin influence connected to the specified influence base
		@param influenceBase: Name of influence base to query influence information from
		@type influenceBase: str
		'''
		# Check influence type
		if mc.objectType(influenceBase) == 'nurbsSurface':
			influenceBase = mc.listRelatives(influence,p=1)[0] # Get element[0] from parent list
		# Check valid transform
		if not self.validTransformList.count(mc.objectType(influenceBase)):
			raise UserInputError('Object '+influenceBase+' is not a valid influenceBase type (nurbsSurface or transform)!')
		# Check influence connections
		influenceConnections = mc.listConnections(influenceBase+'.message',s=0,d=1)
		if not influenceConnections:
			raise UserInputError('No connections to '+influenceBase+'.message attribute!')
		influence = influenceConnections[0]
		# Return result
		return influence
	
	#===============================================================
	# SURFACE COORD CALCULATION METHODS ============================
	#===============================================================
	
	def getSurfaceCoordArray(self,geometry,componentList,surface,maxDist=0.0,calculatePreBind=False,tol=0.001):
		"""
		Calculate surface coordinates for a given object and list of components
		@param geometry: object to calculate surface coordinates for
		@type geometry: str
		@param componentList: list of component indices to calculate surface coordinates for
		@type componentList: list
		@param surface: Influences surface to calculate surface coordinates from
		@type surface: str
		@param maxDist: The maximum distance to search for a closest point on the specified surface. If left at default, maxDist will be ignored.
		@type maxDist: float
		@param calculatePreBind: Calculate coordinates based on pre or post bind geometry
		@type calculatePreBind: bool
		@param tol: Surface edge coordinate precision
		@type tol: float
		"""
		# Check geometry
		if not mc.objExists(geometry): raise UserInputError('Object '+geometry+' does not exist!')
		# Check componentList
		if not componentList: raise UserInputError('Component list contains no valid elements!')
		# Check surface
		if not mc.objExists(surface): raise UserInputError('Surface '+surface+' does not exist!')
		# Get Influence Shape
		if calculatePreBind: surface = self.getInfluenceBase(surface)
		if mc.objectType(surface) == 'transform':
			surface = mc.listRelatives(surface,s=1,ni=1)[0] # Get first non-intermediate shape
		# Ensure influence is a nurbs surface
		if not mc.objectType(surface) == 'nurbsSurface':
			raise UserInputError('Object '+surface+' is not a valid nurbsSurface!')
		
		# Initialize method variables
		coordArray = {}
		pos = []
		
		# Get Geometry Shape
		geoShape = self.getInfluenceShapes(geometry,not(calculatePreBind),calculatePreBind)[0] # Get first shape in list
		# Get Geometry Type
		geoType = mc.objectType(geoShape)
		
		# Get surface parameter domain
		minU = mc.getAttr(surface+'.minValueU')
		maxU = mc.getAttr(surface+'.maxValueU')
		minV = mc.getAttr(surface+'.minValueV')
		maxV = mc.getAttr(surface+'.maxValueV')
		
		# Iterate through componentList
		for i in range(len(componentList)):
			
			# Get pointPosition
			if geoType == 'mesh': pos = mc.pointPosition(geoShape+'.vtx['+str(componentList[i])+']')
			if geoType == 'nurbsCurve': pos = mc.pointPosition(geoShape+'.cv['+str(componentList[i])+']')
			if geoType == 'nurbsSurface':
				cv = glTools.utils.component.getMultiIndex(geoShape,componentList[i])
				pos = mc.pointPosition(geoShape+'.cv['+str(cv[0])+']['+str(cv[1])+']')
			
			# Get closest point on surface
			[u,v] = glTools.utils.surface.closestPoint(surface,pos)
			
			# Clamp coordinate values
			if u<(minU+tol): u = minU+tol
			if u>(maxU-tol): u = maxU-tol
			if v<(minV+tol): v = minV+tol
			if v>(maxV-tol): v = maxV-tol
			
			# Check maxDist
			distance = glTools.utils.mathUtils.distanceBetween(pos,mc.pointPosition(surface+'.uv['+str(u)+']['+str(v)+']'))
			if maxDist and (distance > maxDist): continue
			
			# Append to coordArray
			coordArray[componentList[i]] = [u,v]
		
		# Return result
		return coordArray
	
	def setSurfaceCoordArray(self,geometry,componentList,influence,surfaceSkin,maxDist=0.0,defaultWeight=0.0,calculatePreBind=False,mode=0):
		"""
		Calculate surface coordinates for a given object and list of components
		@param geometry: Geometry to calculate surface coordinates for
		@type geometry: str
		@param componentList: List of component indices to calculate surface coordinates for
		@type componentList: list
		@param influence: Influences surface to calculate surface coordinates from
		@type influence: str
		@param surfaceSkin: SurfaceSkin node to set surface coordinates for
		@type surfaceSkin: str
		@param maxDist: Maximum distance to search for point on surface
		@type maxDist: float
		@param calculatePreBind: Calculate coordinates based on pre or post bind geometry
		@type calculatePreBind: bool
		@param mode: 0 = REPLACE, 1 = ADD, 2 = SET, 3 = REMOVE
		@type mode: int
		"""
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		
		# Check for empty componentList
		if not componentList:
			compIndexList = glTools.utils.component.getSingleIndexComponentList([geometry])
			componentList = compIndexList[self.getInfluenceShapes(geometry)[0]] # Get first shape in list
		
		# Check Transform Influence
		transformInf = self.isTransformInfluence(influence,surfaceSkin)
		
		# Get current influence data values
		indexArray = self.getIndexArray(geometry,influence,surfaceSkin)
		weightArray = self.getWeightArray(geometry,influence,surfaceSkin)
		coordUArray = self.getCoordUArray(geometry,influence,surfaceSkin)
		coordVArray = self.getCoordVArray(geometry,influence,surfaceSkin)
		
		# Validate influence data arrays
		if not indexArray or not weightArray or not coordUArray or not coordVArray:
			indexArray = weightArray = coordUArray = coordVArray = []
			
		# Initialize dictionary variables
		coordArray = {}
		calcCoordArray = {}
		
		# Build Coordinate Dictionary from current coord values
		if mode != self.mode['set']:
			if (len(indexArray) != len(weightArray)) or \
			(len(indexArray) != len(coordUArray)) or \
			(len(indexArray) != len(coordVArray)):
				raise UserInputError('Surface coordinate array length inconsistency!!')
			for i in range(len(indexArray)):
				coordArray[indexArray[i]] = [coordUArray[i],coordVArray[i],weightArray[i]]
		
		# Remove unnecessary indices from componentList (ADD only!)
		if mode == self.mode['add']:
			[componentList.remove(i) for i in indexArray if componentList.count(i)]
		
		# Calculate Coordinate Dictionary for new coord values
		if mode != self.mode['remove'] and not transformInf:
			calcCoordArray = self.getSurfaceCoordArray(geometry,componentList,influence,maxDist,calculatePreBind)
		# Build dummy coord array for transform influence
		if transformInf:
			for i in componentList: calcCoordArray[i]=[0.0,0.0]
		
		# Merge Coord Dictionaries
		#--------------------------
		# SET
		if mode == self.mode['set']:
			for key in calcCoordArray.keys():
				if coordArray.has_key(key): calcCoordArray[key].append(coordArray[key][2])
				else: calcCoordArray[key].append(defaultWeight)
			coordArray = calcCoordArray
		# REMOVE
		elif mode == self.mode['remove']:
			for key in componentList:
				if coordArray.has_key(key):
					coordArray.pop(key)
		# ADD and REPLACE
		else:
			for key in calcCoordArray.keys():
				if coordArray.has_key(key):
					if (mode == self.mode['add']): continue
					calcCoordArray[key].append(coordArray[key][2])
				else:
					calcCoordArray[key].append(defaultWeight)
				coordArray[key] = calcCoordArray[key]
		
		# Update class arrays
		indexArray = coordArray.keys()
		indexArray.sort()
		paramU = []
		paramV = []
		weightArray = []
		for ind in indexArray:
			paramU.append(coordArray[ind][0])
			paramV.append(coordArray[ind][1])
			weightArray.append(coordArray[ind][2])
		
		# Pass new coordinate values to surfaceSkin node
		self.setIndexArray(geometry,influence,surfaceSkin,indexArray)
		self.setWeightArray(geometry,influence,surfaceSkin,weightArray)
		self.setCoordArray(geometry,influence,surfaceSkin,paramU,paramV)
	
	#===============================================================
	# INFO / QUERY METHODS =========================================
	#===============================================================
	
	def getAffectedGeometry(self,surfaceSkin,getShapes=False):
		'''
		Returns a dictionary containing information regarding geometry affected by the specified surfaceSkin deformer
		@param surfaceSkin: The surfaceSkin deformer to query affected geometery from
		@type surfaceSkin: str
		@param getShapes: Return the shape names instead of the transform
		@type getShapes: bool
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin provided!')
		# Get deformer affected geometry dictionary
		affectedGeometry = glTools.utils.deformer.getAffectedGeometry(surfaceSkin,getShapes)
		return affectedGeometry
	
	def getGeometryIndex(self,targetGeometry,surfaceSkin):
		'''
		Returns the input/output index to the specified surfaceSkin deformer for a named geometry
		@param targetGeometry: The geometry to query input/output index to the surfaceSkin deformer
		@type targetGeometry: str
		@param surfaceSkin: The surfaceSkin deformer to query input/output index from
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Return Geometry Index
		return glTools.utils.deformer.getGeomIndex(targetGeometry,surfaceSkin)
	
	def getInfluenceShapes(self,influence,nonIntermediate=True,intermediate=False,allowEmptyList=False):
		'''
		Return a list of shapes of the speficied influence object. Raise an Exception if no shapes are found.
		@param influence: The influence to return shape list for
		@type influence: str
		@param nonIntermediate: Include nonIntermediate shapes to return shape list
		@type nonIntermediate: bool
		@param intermediate: Include intermediate shapes to return shape list
		@type intermediate: bool
		'''
		influenceShapes = glTools.utils.selection.getShapes(influence,nonIntermediate,intermediate)
		if not influenceShapes and not allowEmptyList: raise Exception('No valid shapes found for influence(Base) "'+influence+'"!')
		if not influenceShapes: influenceShapes = []
		return influenceShapes
		
	def getInfluenceDict(self,surfaceSkin):
		'''
		Return a dictionary containing influence information for the specified surfaceSkin node
		@param surfaceSkin: The surfaceSkin deformer to query input/output index from
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Get influence list (transforms) from connections
		return glTools.utils.connection.connectionListToAttr(surfaceSkin,'influenceMatrix')
	
	def getInfluenceList(self,surfaceSkin):
		'''
		Return an ordered influence list for the specified surfaceSkin node
		@param surfaceSkin: The surfaceSkin deformer to list influences for
		@type surfaceSkin: str
		'''
		# Get influence dictionary
		influenceDict = self.getInfluenceDict(surfaceSkin)
		# Build intermediate influence dict for sort
		intInfluenceDict = {}
		for key in influenceDict.iterkeys(): intInfluenceDict[influenceDict[key][1]] = key
		# Return ordered influence list
		return glTools.utils.arrayUtils.dict_orderedValueListFromKeys(intInfluenceDict)
	
	def getInfluenceIndex(self,influence,surfaceSkin):
		'''
		Returns the input index of the specified influence for the named surfaceSkin deformer
		@param influence: The influence to query input index for
		@type influence: str
		@param surfaceSkin: The surfaceSkin deformer to query influence index for
		@type surfaceSkin: str
		'''
		# Get influence dictionary
		influenceDict = self.getInfluenceDict(surfaceSkin)
		# Check correct infulence type is being passed
		if self.isTransformInfluence(influence,surfaceSkin):
			if not self.validTransformList.count(mc.objectType(influence)):
				influence = mc.listRelatives(influence,p=True)[0]
		else:
			if self.validTransformList.count(mc.objectType(influence)):
				influence = self.getInfluenceShapes(influence)[0] # Get first shape from list
		# Check influence affects surfaceSkin
		if not influenceDict.has_key(influence):
			raise UserInputError('Object "'+influence+'" is not a valid influence of surfaceSkin deformer "'+surfaceSkin+'"!!')
		# Return result
		return influenceDict[influence][1] # Element[1] = element index, [0] = connected attribute
	
	def getInfluenceMembership(self,influence,surfaceSkin,affectedGeometryList=[],indexOnly=False):
		'''
		Return a string array of all component names affected by a specified influence of a surfaceSkin node.
		@param influence: The influence of the surfaceSkin node to query influence membership for
		@type influence: str
		@param surfaceSkin: The surfaceSkin nodeto query influence membership for
		@type surfaceSkin: str
		@param affectedGeometryList: List of affected geometry to limit the influence membership query to
		@type affectedGeometryList: list
		@param indexOnly: Return only the influence membership component indices
		@type indexOnly: bool
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		
		# Check affectedGeometry list
		if not affectedGeometryList:
			affectedGeometryList = self.getAffectedGeometry(surfaceSkin).keys()
		
		memberList = []
		# Get membership of influence for current geometry
		for geo in affectedGeometryList:
			memberIndexList = self.getIndexArray(geo,influence,surfaceSkin)
			if not memberIndexList: memberIndexList = []
			if indexOnly:
				memberList.extend(memberIndexList)
				continue
			geoType = mc.objectType(self.getInfluenceShapes(geo)[0])
			for index in memberIndexList:
				if geoType == 'mesh':
					memberList.append(geo+'.vtx['+str(index)+']')
				elif geoType == 'nurbsCurve':
					memberList.append(geo+'.cv['+str(index)+']')
				elif geoType == 'nurbsSurface':
					multiIndex = glTools.utils.component.getMultiIndex(geo,index)
					memberList.append(geo+'.cv['+str(multiIndex[0])+']['+str(multiIndex[1])+']')
		
		# Return membership list
		return memberList
	
	def getNextInfluenceIndex(self,surfaceSkin):
		'''
		Return the next available influence input index
		@param surfaceSkin: The surfaceSkin deformer to query next available influence index for
		@type surfaceSkin: str
		'''
		infIndex = 0
		# Get next available influence index
		influenceList = self.getInfluenceList(surfaceSkin)
		if influenceList: infIndex = self.getInfluenceIndex(influenceList[-1],surfaceSkin)+1
		# Return result
		return infIndex
	
	def isInfluence(self,influence,surfaceSkin):
		'''
		Check in specified influence affects a named surfaceSkin node
		@param influence: Influence to query
		@type influence: str
		@param surfaceSkin: SurfaceSkin node to query
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Check influence
		if self.getInfluenceList(surfaceSkin).count(influence):
			return True
		else:
			try: influenceShape = mc.listRelatives(influence)[0]
			except: return False
			return bool(self.getInfluenceList(surfaceSkin).count(influenceShape))
	
	def isTransformInfluence(self,influence,surfaceSkin):
		'''
		Determine if a given influence is a transformInfluence for the specified surfaceSkin
		@param influence: Influence to query
		@type influence: str
		@param surfaceSkin: SurfaceSkin node to query
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Check influence
		if not self.validTransformList.count(mc.objectType(influence)):
			influence = mc.listRelatives(influence,p=True)[0]
		influenceMatrixConn = mc.listConnections(surfaceSkin+'.influenceMatrix',s=True,d=False)
		if not influenceMatrixConn:
			raise UserInputError('SurfaceSkin deformer "'+surfaceSkin+'" has no valid influences!!')
		if not influenceMatrixConn.count(influence):
			raise UserInputError('Object "'+influence+'" is not a valid influence of surfaceSkin deformer "'+surfaceSkin+'"!!')
		# Check influence connections
		infGeomConn = mc.listConnections(surfaceSkin+'.influenceGeometry')
		if not infGeomConn: return True
		if not infGeomConn.count(influence): return True
		else: return False
	
	def printInfluenceData(self,influence,surfaceSkin):
		'''
		Print influence data for the specified surfaceSkin node
		@param influence: Influence to print information for
		@type influence: str
		@param surfaceSkin: SurfaceSkin deformer to print information for
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Print info header
		print('\n\n--\nInfluence Data:\n--\n\n')
		print(surfaceSkin+': '+influence+'-\n\n')
		# Get affected geometry
		affectedGeo = self.getAffectedGeometry(surfaceSkin)
		# Get influence data
		influenceIndex = self.getInfluenceIndex(influence,surfaceSkin)
		for geo in affectedGeo.keys():
			geoIndex = affectedGeo[geo]
			print('Geometry: '+geo+' - '+str(geoIndex)+'\n\n')
			indexList = self.getIndexArray(geo,influence,surfaceSkin)
			weightList = self.getWeightArray(geo,influence,surfaceSkin)
			paramUList = self.getCoordUArray(geo,influence,surfaceSkin)
			paramVList = self.getCoordVArray(geo,influence,surfaceSkin)
			for i in range(len(indexList)):
				print(str(indexList[i])+': ('+str(paramUList[i])+','+str(paramVList[i])+') - ' + str(weightList[i]))
	
	def getPaintInfluence(self,surfaceSkin):
		'''
		Return the influence index that is currently set as paintable
		@param surfaceSkin: The surfaceSkin node that you want to query the paintable influence of
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Return the current paintable influence
		return mc.listConnections(surfaceSkin+'.paintTrans',s=1,d=0)[0]
	
	def getIndexArray(self,geometry,influence,surfaceSkin=''):
		'''
		Return the index array for the specified surfaceSkin node, influence and geometery
		@param geometry: The affected geometery that you want to get the array value for
		@type geometry: str
		@param influence: The influence that you want to get the array value for
		@type influence: str
		@param surfaceSkin: The surfaceSkin node that you want to get the array value for
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Get index array
		geometryIndex = self.getGeometryIndex(geometry,surfaceSkin)
		influenceIndex = self.getInfluenceIndex(influence,surfaceSkin)
		return mc.getAttr(surfaceSkin+'.influenceDataList['+str(geometryIndex)+'].influenceData['+str(influenceIndex)+'].index')
	
	def getWeightArray(self,geometry,influence,surfaceSkin):
		'''
		Return the weight array for the specified surfaceSkin node, influence and geometery
		@param geometry: The affected geometery that you want to get the array value for
		@type geometry: str
		@param influence: The influence that you want to get the array value for
		@type influence: str
		@param surfaceSkin: The surfaceSkin node that you want to get the array value for
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Get weight array
		geometryIndex = self.getGeometryIndex(geometry,surfaceSkin)
		influenceIndex = self.getInfluenceIndex(influence,surfaceSkin)
		return mc.getAttr(surfaceSkin+'.influenceDataList['+str(geometryIndex)+'].influenceData['+str(influenceIndex)+'].influenceWeight')
	
	def getCoordUArray(self,geometry,influence,surfaceSkin):
		'''
		Return the U coordinate array for the specified surfaceSkin node, influence and geometery
		@param geometry: The affected geometery that you want to get the array value for
		@type geometry: str
		@param influence: The influence that you want to get the array value for
		@type influence: str
		@param surfaceSkin: The surfaceSkin node that you want to get the array value for
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Get coord U array
		geometryIndex = self.getGeometryIndex(geometry,surfaceSkin)
		influenceIndex = self.getInfluenceIndex(influence,surfaceSkin)
		return mc.getAttr(surfaceSkin+'.influenceDataList['+str(geometryIndex)+'].influenceData['+str(influenceIndex)+'].uCoord')
		
	def getCoordVArray(self,geometry,influence,surfaceSkin):
		'''
		Return the V coordinate array for the specified surfaceSkin node, influence and geometery
		@param geometry: The affected geometery that you want to get the array value for
		@type geometry: str
		@param influence: The influence that you want to get the array value for
		@type influence: str
		@param surfaceSkin: The surfaceSkin node that you want to get the array value for
		@type surfaceSkin: str
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Get coord V array
		geometryIndex = self.getGeometryIndex(geometry,surfaceSkin)
		influenceIndex = self.getInfluenceIndex(influence,surfaceSkin)
		return mc.getAttr(surfaceSkin+'.influenceDataList['+str(geometryIndex)+'].influenceData['+str(influenceIndex)+'].vCoord')
		
	def setIndexArray(self,geometry,influence,surfaceSkin,indexArray=[]):
		'''
		Set the index array attribute on a specified surfaceSkin deformer for a named influence
		@param geometry: The affected geometery that you want to set the array value for
		@type geometry: str
		@param influence: The influence that you want to set the array value for
		@type influence: str
		@param surfaceSkin: The surfaceSkin node that you want to set the array value for
		@type surfaceSkin: str
		@param indexArray: The array value to set for the surfaceSkin deformer
		@type indexArray: list
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Get geometery index
		geometryIndex = self.getGeometryIndex(geometry,surfaceSkin)
		# Get influence index
		influenceIndex = self.getInfluenceIndex(influence,surfaceSkin)
		# Set array value
		mc.setAttr(surfaceSkin+'.influenceDataList['+str(geometryIndex)+'].influenceData['+str(influenceIndex)+'].index',indexArray,type='Int32Array')
	
	def setWeightArray(self,geometry,influence,surfaceSkin,weightArray=[]):
		'''
		Set the weight array attribute on a specified surfaceSkin deformer for a named influence
		@param geometry: The affected geometery that you want to set the array value for
		@type geometry: str
		@param influence: The influence that you want to set the array value for
		@type influence: str
		@param surfaceSkin: The surfaceSkin node that you want to set the array value for
		@type surfaceSkin: str
		@param weightArray: The array value to set for the surfaceSkin deformer
		@type weightArray: list
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Get geometery index
		geometryIndex = self.getGeometryIndex(geometry,surfaceSkin)
		# Get influence index
		influenceIndex = self.getInfluenceIndex(influence,surfaceSkin)
		# Set array value
		mc.setAttr(surfaceSkin+'.influenceDataList['+str(geometryIndex)+'].influenceData['+str(influenceIndex)+'].influenceWeight',weightArray,type='doubleArray')
	
	def setCoordArray(self,geometry,influence,surfaceSkin,uCoordArray=[],vCoordArray=[]):
		'''
		Set the coordinate array attribute on a specified surfaceSkin deformer for a named influence
		@param geometry: The affected geometery that you want to set the array value for
		@type geometry: str
		@param influence: The influence that you want to set the array value for
		@type influence: str
		@param surfaceSkin: The surfaceSkin node that you want to set the array value for
		@type surfaceSkin: str
		@param uCoordArray: The u coordinate array value to set for the surfaceSkin deformer
		@type uCoordArray: list
		@param vCoordArray: The v coordinate array value to set for the surfaceSkin deformer
		@type vCoordArray: list
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		# Get geometery index
		geometryIndex = self.getGeometryIndex(geometry,surfaceSkin)
		# Get influence index
		influenceIndex = self.getInfluenceIndex(influence,surfaceSkin)
		# Set array values
		mc.setAttr(surfaceSkin+'.influenceDataList['+str(geometryIndex)+'].influenceData['+str(influenceIndex)+'].uCoord',uCoordArray,type='doubleArray')
		mc.setAttr(surfaceSkin+'.influenceDataList['+str(geometryIndex)+'].influenceData['+str(influenceIndex)+'].vCoord',vCoordArray,type='doubleArray')
	
	def pruneSmallWeights(self,surfaceSkin,affectedGeometryList=[],influenceList=[],threshold=0.001):
		'''
		Prune influence membership with weight values below a specified threshold
		@param surfaceSkin: The surfaceSkin node that you want to prune weights from
		@type surfaceSkin: str
		@param affectedGeometryList: A specific list of affected geometry to prune weights on. If left at default, all affected geometery wil be used
		@type affectedGeometryList: list
		@param influenceList: A specific list of influences to prune weights on. If left at default, all influences wil be used
		@type influenceList: list
		@param threshold: The threshold that will determine which weights will be pruned
		@type threshold: float
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		
		# Check affectedGeometry list
		if not affectedGeometryList:
			affectedGeometryList = self.getAffectedGeometry(surfaceSkin)
		if not affectedGeometryList:
			raise UserInputError('No affected geometry found for '+surfaceSkin)
		
		# Check influence list
		if not influenceList:
			influenceList = self.getInfluenceList(surfaceSkin)
		if not influenceList:
			raise UserInputError('No influences attached to surfaceSkin node "'+surfaceSkin+'"!!')
		
		# Iterate over affected geometry
		for geo in affectedGeometryList.keys():
			# Get geometry index
			geoIndex = affectedGeometryList[geo]
			# Iterate over influences
			for inf in influenceList.keys():
				# Get influence index
				infIndex = influenceList[inf][1] # Element: [1] = index, [0] = attribute
				influenceWeights = self.getWeightArray(geo,inf,surfaceSkin)
				# Iterate over weight array
				for w in range(len(influenceWeights)):
					# Prune small weight
					if influenceWeights[w] < threshold:
						influenceWeights[w] = 0.0
				self.setWeightArray(geo,inf,surfaceSkin,influenceWeights)
	
	def pruneMembershipByWeights(self,surfaceSkin,affectedGeometryList=[],influenceList=[],threshold=0.001):
		'''
		'''
		# Verify node
		if not self.verifyNode(surfaceSkin):
			raise UserInputError('No valid surfaceSkin node provided!')
		
		# Check affectedGeometry list
		if not affectedGeometryList:
			affectedGeometryList = self.getAffectedGeometry(surfaceSkin)
			if not affectedGeometryList:
				raise UserInputError('No affected geometry found for '+surfaceSkin)
		# Check influence list
		if not influenceList:
			influenceList = self.getInfluenceList(surfaceSkin)
			if not influenceList:
				raise UserInputError('No influences attached to '+surfaceSkin)
		
		# Iterate over affected geometry
		for geo in affectedGeometryList.keys():
			# Get geometry index
			geoIndex = affectedGeometryList[geo]
			# Iterate over influences
			for inf in influenceList:
				# Get influence index
				infIndex = self.getInfluenceIndex(inf,surfaceSkin)
				
				# Get influence data for current geo
				indexArray = self.getIndexArray(geo,inf,surfaceSkin)
				weightArray = self.getWeightArray(geo,inf,surfaceSkin)
				
				# Prune member with below threshold weights
				pruneMemberList = [indexArray[i] for i in range(len(indexArray)) if weightArray[i] < threshold]
				
				# Prune membership
				if pruneMemberList:
					self.setSurfaceCoordArray(geo,pruneMemberList,inf,surfaceSkin,mode=self.mode['remove'])
	
	def makePaintable(self):
		'''
		Sets up the surfaceSkin weight attributes to be paintable with the artisan paint attribute tool.
		'''
		# Remove paintable status of surfaceSkin weights attributes
		mc.makePaintable( 'surfaceSkin', 'weights', rm=True )
		mc.makePaintable( 'surfaceSkin', 'paintWeight', rm=True )
		# Make surfaceSkin weights attributes paintable 
		mc.makePaintable( 'surfaceSkin', 'weights', attrType='multiFloat', sm='deformer' )
		mc.makePaintable( 'surfaceSkin', 'paintWeight', attrType='multiFloat', sm='deformer' )

