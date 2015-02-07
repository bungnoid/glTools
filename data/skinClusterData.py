import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.utils.deformer
import glTools.utils.skinCluster

import data
import deformerData

import meshData

class SkinClusterData( deformerData.MultiInfluenceDeformerData ):
	'''
	SkinCluster Data Class Object
	Contains functions to save, load and rebuild basic skinCluster data.
	'''
	def __init__(self,skinCluster=''):
		'''
		SkinCluster Data Class Initializer
		'''
		# Execute Super Class Initilizer
		super(SkinClusterData, self).__init__()
		
		# SkinCluster Custom Attributes
		self._data['attrValueList'].append('skinningMethod')
		self._data['attrValueList'].append('useComponents')
		self._data['attrValueList'].append('normalizeWeights')
		self._data['attrValueList'].append('deformUserNormals')
		
		# Build SkinCluster Data
		if skinCluster: self.buildData(skinCluster)
	
	def verifySkinCluster(self,skinCluster):
		'''
		'''
		# Check skinCluster
		if not glTools.utils.skinCluster.isSkinCluster(skinCluster):
			raise Exception('Object "'+skinCluster+'" is not a valid skinCluster!')
	
	def buildData(self,skinCluster):
		'''
		Build skinCluster data and store as class object dictionary entries
		@param skinCluster: SkinCluster deformer to store data for.
		@type skinCluster: list
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Check skinCluster
		self.verifySkinCluster(skinCluster)
		
		# Clear Data
		self.reset()
		
		# =======================
		# - Build Deformer Data -
		# =======================
		
		# Start Timer
		timer = mc.timerX()
		
		self._data['name'] = skinCluster
		self._data['type'] = 'skinCluster'
		
		# Get affected geometry
		skinGeoShape = mc.skinCluster(skinCluster,q=True,g=True)
		if len(skinGeoShape) > 1: raise Exception('SkinCluster "'+skinCluster+'" output is connected to multiple shapes!')
		if not skinGeoShape: raise Exception('Unable to determine affected geometry for skinCluster "'+skinCluster+'"!')
		skinGeo = mc.listRelatives(skinGeoShape[0],p=True,pa=True)
		if not skinGeo: raise Exception('Unable to determine geometry transform for object "'+skinGeoShape+'"!')
		self._data['affectedGeometry'] = skinGeo
		skinGeo = skinGeo[0]
		
		skinClusterSet = glTools.utils.deformer.getDeformerSet(skinCluster)
		
		self._data[skinGeo] = {}
		self._data[skinGeo]['index'] = 0
		self._data[skinGeo]['geometryType'] = str(mc.objectType(skinGeoShape))
		self._data[skinGeo]['membership'] = glTools.utils.deformer.getDeformerSetMemberIndices(skinCluster,skinGeo)
		self._data[skinGeo]['weights'] = []
		
		if self._data[skinGeo]['geometryType'] == 'mesh':
				self._data[skinGeo]['mesh'] = meshData.MeshData(skinGeo)
		
		# ========================
		# - Build Influence Data -
		# ========================
		
		# Get skinCluster influence list
		influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
		if not influenceList: raise Exception('Unable to determine influence list for skinCluster "'+skinCluster+'"!')
		
		# Get Influence Wieghts
		weights = glTools.utils.skinCluster.getInfluenceWeightsAll(skinCluster)
		
		# For each influence
		for influence in influenceList:
			
			# Initialize influence data
			self._influenceData[influence] = {}
			
			# Get influence index
			infIndex = glTools.utils.skinCluster.getInfluenceIndex(skinCluster,influence)
			self._influenceData[influence]['index'] = infIndex
			
			# Get Influence BindPreMatrix
			bindPreMatrix = mc.listConnections(skinCluster+'.bindPreMatrix['+str(infIndex)+']',s=True,d=False,p=True)
			if bindPreMatrix: self._influenceData[influence]['bindPreMatrix'] = bindPreMatrix[0]
			else: self._influenceData[influence]['bindPreMatrix'] = ''
			
			# Get Influence Type (Transform/Geometry)
			infGeomConn = mc.listConnections(skinCluster+'.driverPoints['+str(infIndex)+']')
			if infGeomConn:
				self._influenceData[influence]['type'] = 1
				self._influenceData[influence]['polySmooth'] = mc.skinCluster(skinCluster,inf=influence,q=True,ps=True)
				self._influenceData[influence]['nurbsSamples'] = mc.skinCluster(skinCluster,inf=influence,q=True,ns=True)
			else:
				self._influenceData[influence]['type'] = 0
			
			# Get Influence Weights
			pInd = glTools.utils.skinCluster.getInfluencePhysicalIndex(skinCluster,influence)
			self._influenceData[influence]['wt'] = weights[pInd]
		
		# =========================
		# - Custom Attribute Data -
		# =========================
		
		# Add Pre-Defined Custom Attributes
		self.getDeformerAttrValues()
		self.getDeformerAttrConnections()
		
		# =================
		# - Return Result -
		# =================
		
		skinTime = mc.timerX(st=timer)
		print('SkinClusterData: Data build time for "'+skinCluster+'": '+str(skinTime))

	def rebuild(self):
		'''
		Rebuild the skinCluster using stored data
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Check geometry
		skinGeo = self._data['affectedGeometry'][0]
		if not mc.objExists(skinGeo):
			raise Exception('SkinCluster geometry "'+skinGeo+'" does not exist! Use remapGeometry() to load skinCluster data for a different geometry!')
		
		# =======================
		# - Rebuild SkinCluster -
		# =======================
		
		# Start timer
		timer = mc.timerX()
		
		# Initialize Temp Joint
		tempJnt = ''
		
		# Unlock Influences
		influenceList = self._influenceData.keys()
		for influence in influenceList:
			if mc.objExists(influence+'.liw'):
				if mc.getAttr(influence+'.liw',l=True):
					try: mc.setAttr(influence+'.liw',l=False)
					except: print('Error unlocking attribute "'+influence+'.liw"! This could problems when rebuilding the skinCluster...')
				if mc.getAttr(influence+'.liw'):
					try: mc.setAttr(influence+'.liw',False)
					except: print('Error setting attribute "'+influence+'.liw" to False! This could problems when rebuilding the skinCluster...')
		
		# Check SkinCluster
		skinCluster = self._data['name']
		if not mc.objExists(skinCluster):
			
			# Get Transform Influences
			jointList = [inf for inf in influenceList if not self._influenceData[inf]['type']]
			
			# Check Transform Influences
			if not jointList:
				
				# Create Temporary Bind Joint
				mc.select(cl=1)
				tempJnt = mc.joint(n=skinCluster+'_tempJoint')
				print('No transform influences specified for skinCluster "'+skinCluster+'"! Creating temporary bind joint "'+tempJnt+'"!')
				jointList = [tempJnt]
			
			else:
				
				# Get Surface Influences
				influenceList = [inf for inf in influenceList if self._influenceData[inf]['type']]
			
			# Create skinCluster
			skinCluster = mc.skinCluster(jointList,skinGeo,tsb=True,n=skinCluster)[0]
		
		else:
			
			# Check Existing SkinCluster
			affectedGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster)
			if affectedGeo.keys()[0] != skinGeo:
				raise Exception('SkinCluster "'+skinCluster+'" already exists, but is not connected to the expeced geometry "'+skinGeo+'"!')
		
		# Add skinCluster influences
		for influence in influenceList:
			
			# Check influence
			if not mc.objExists(influence):
				raise Exception('Influence "'+influence+'" does not exist! Use remapInfluence() to apply data to a different influence!')
			
			# Check existing influence connection
			if not mc.skinCluster(skinCluster,q=True,inf=True).count(influence):
			
				# Add influence
				if self._influenceData[influence]['type']:
					# Geometry
					polySmooth = self._influenceData[influence]['polySmooth']
					nurbsSamples = self._influenceData[influence]['nurbsSamples']
					mc.skinCluster(skinCluster,e=True,ai=influence,ug=True,ps=polySmooth,ns=nurbsSamples,wt=0.0,lockWeights=True)
					
				else:
					# Transform
					mc.skinCluster(skinCluster,e=True,ai=influence,wt=0.0,lockWeights=True)
				
				# Bind Pre Matrix
				if self._influenceData[influence]['bindPreMatrix']:
					infIndex = glTools.utils.skinCluster.getInfluenceIndex(skinCluster,influence)
					mc.connectAttr(self._influenceData[influence]['bindPreMatrix'],skinCluster+'.bindPreMatrix['+str(infIndex)+']',f=True)
		
		# Load skinCluster weights
		mc.setAttr(skinCluster+'.normalizeWeights',0)
		glTools.utils.skinCluster.clearWeights(skinGeo)
		self.loadWeights()
		mc.setAttr(skinCluster+'.normalizeWeights',1)
		
		# Restore Custom Attribute Values and Connections
		self.setDeformerAttrValues()
		self.setDeformerAttrConnections()
		
		# Clear Selection
		mc.select(cl=True)
		
		# =================
		# - Return Result -
		# =================
		
		# Print Timed Result
		totalTime = mc.timerX(st=timer)
		print('SkinClusterData: Rebuild time for skinCluster "'+skinCluster+'": '+str(totalTime))
		
		return skinCluster
	
	def setWeights(self,componentList=[]):
		'''
		Apply the stored skinCluster weights to the specified skinCluster.
		@param componentList: The list of components to apply skinCluster weights to.
		@type componentList: str
		'''
		print('!!! - DEPRICATED: skinClusterData.setWeights()! Use loadWeights() method instead - !!!')
		
		# ==========
		# - Checks -
		# ==========
		
		# Check SkinCluster
		skinCluster = self._data['name']
		self.verifySkinCluster(skinCluster)
		
		# Check Geometry
		skinGeo = self._data['affectedGeometry'][0]
		if not mc.objExists(skinGeo):
			raise Exception('SkinCluster geometry "'+skinGeo+'" does not exist! Use remapGeometry() to load skinCluster data to a different geometry!')
		
		# Check Component List
		if not componentList: componentList = glTools.utils.component.getComponentStrList(skinGeo)
		componentSel = glTools.utils.selection.getSelectionElement(componentList,0)
		
		# Get Component Index List
		indexList =  OpenMaya.MIntArray()
		componentFn = OpenMaya.MFnSingleIndexedComponent(componentSel[1])
		componentFn.getElements(indexList)
		componentIndexList = list(indexList)
		
		# ===========================
		# - Set SkinCluster Weights -
		# ===========================
		
		# Build influence index array
		infIndexArray = OpenMaya.MIntArray()
		influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
		[infIndexArray.append(i) for i in range(len(influenceList))]
		
		# Build master weight array
		wtArray = OpenMaya.MDoubleArray()
		oldWtArray = OpenMaya.MDoubleArray()
		for c in componentIndexList:
			for i in range(len(influenceList)):
				if self._influenceData.has_key(influenceList[i]):
					wtArray.append(self._influenceData[influenceList[i]]['wt'][c])
				else:
					wtArray.append(0.0)
		
		# Get skinCluster function set
		skinFn = glTools.utils.skinCluster.getSkinClusterFn(skinCluster)
		
		# Set skinCluster weights
		skinFn.setWeights(componentSel[0],componentSel[1],infIndexArray,wtArray,False,oldWtArray)
		
		# =================
		# - Return Result -
		# =================
		
		return influenceList
	
	def loadWeights(	self,
						skinCluster		= None,
						influenceList	= None,
						componentList	= None,
						normalize		= True ):
		'''
		Apply the stored skinCluster weights.
		@param skinCluster: The list of components to apply skinCluster weights to.
		@type skinCluster: str
		@param influenceList: The list of skinCluster influences to apply weights for.
		@type influenceList: list or None
		@param componentList: The list of components to apply skinCluster weights to.
		@type componentList: list or None
		@param normalize: Normalize influence weights.
		@type normalize: bool
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Check SkinCluster
		if not skinCluster: skinCluster = self._data['name']
		self.verifySkinCluster(skinCluster)
		
		# Check Geometry
		skinGeo = self._data['affectedGeometry'][0]
		if not mc.objExists(skinGeo):
			raise Exception('SkinCluster geometry "'+skinGeo+'" does not exist! Use remapGeometry() to load skinCluster data to a different geometry!')
		
		# Check Influence List
		if not influenceList: influenceList = self._influenceData.keys() or []
		for influence in influenceList:
			if not influence in mc.skinCluster(skinCluster,q=True,inf=True) or []:
				raise Exception('Object "'+influence+'" is not a valid influence of skinCluster "'+skinCluster+'"! Unable to load influence weights...')
			if not self._influenceData.has_key(influence):
				raise Exception('No influence data stored for "'+influence+'"! Unable to load influence weights...')
		
		# Check Component List
		if not componentList:
			componentList = glTools.utils.component.getComponentStrList(skinGeo)
		componentSel = glTools.utils.selection.getSelectionElement(componentList,0)
		
		# Get Component Index List
		#indexList =  OpenMaya.MIntArray()
		#componentFn = OpenMaya.MFnSingleIndexedComponent(componentSel[1])
		#componentFn.getElements(indexList)
		#componentIndexList = list(indexList)
		componentIndexList = glTools.utils.component.getSingleIndexComponentList(componentList)
		componentIndexList = componentIndexList[componentIndexList.keys()[0]]
		
		# =====================================
		# - Set SkinCluster Influence Weights -
		# =====================================
		
		# Get Influence Index
		infIndexArray = OpenMaya.MIntArray()
		for influence in influenceList:
			infIndex = glTools.utils.skinCluster.getInfluencePhysicalIndex(skinCluster,influence)
			infIndexArray.append(infIndex)
		
		# Build Weight Array
		wtArray = OpenMaya.MDoubleArray()
		oldWtArray = OpenMaya.MDoubleArray()
		for c in componentIndexList:
			for i in range(len(influenceList)):
				if self._influenceData.has_key(influenceList[i]):
					wtArray.append(self._influenceData[influenceList[i]]['wt'][c])
				else:
					wtArray.append(0.0)
		
		# Get skinCluster function set
		skinFn = glTools.utils.skinCluster.getSkinClusterFn(skinCluster)
		
		# Set skinCluster weights
		skinFn.setWeights(componentSel[0],componentSel[1],infIndexArray,wtArray,normalize,oldWtArray)
		
		# =================
		# - Return Result -
		# =================
		
		return list(wtArray)
	
	def swapWeights(self,inf1,inf2):
		'''
		Swap influence weight values between 2 skinCluster influeneces.
		@param inf1: First influence to swap weights for
		@type inf1: str
		@param inf2: Second influence to swap weights for
		@type inf2: str
		'''
		# Check Influences
		if not self._influenceData.has_key(inf1):
			raise Exception('No influence data for "'+inf1+'"! Unable to swap weights...')
		if not self._influenceData.has_key(inf2):
			raise Exception('No influence data for "'+inf2+'"! Unable to swap weights...')
		
		# Swap Weights
		self._influenceData[inf1]['wt'][:], self._influenceData[inf2]['wt'][:] = self._influenceData[inf2]['wt'][:], self._influenceData[inf1]['wt'][:]
		
		# Return Result
		print('SkinClusterData: Swap Weights Complete - "'+inf1+'" <> "'+inf2+'"')
	
	def moveWeights(self,sourceInf,targetInf,mode='add'):
		'''
		Move influence weight values from one skinCluster influenece to another.
		@param sourceInf: First influence to swap weights for
		@type sourceInf: str
		@param targetInf: Second influence to swap weights for
		@type targetInf: str
		@param mode: Move mode for the weights. Avaiable options are "add" and "replace".
		@type mode: str
		'''
		# Check Influences
		if not self._influenceData.has_key(sourceInf):
			raise Exception('No influence data for source influence "'+sourceInf+'"! Unable to move weights...')
		if not self._influenceData.has_key(targetInf):
			raise Exception('No influence data for target influence "'+targetInf+'"! Unable to move weights...')
		
		# Check Mode
		if not ['add','replace'].count(mode):
			raise Exception('Invalid mode value ("'+mode+'")!')
		
		# Move Weights
		sourceWt = self._influenceData[sourceInf]['wt']
		targetWt = self._influenceData[targetInf]['wt']
		if mode == 'add':
			self._influenceData[targetInf]['wt'] = [i[0]+i[1] for i in zip(sourceWt,targetWt)]
		elif mode == 'replace':
			self._influenceData[targetInf]['wt'] = [i for i in sourceWt]
		self._influenceData[sourceInf]['wt'] = [0.0 for i in sourceWt]
		
		# Return Result
		print('SkinClusterData: Move Weights Complete - "'+sourceInf+'" >> "'+targetInf+'"')
	
	def remapInfluence(self,oldInfluence,newInfluence):
		'''
		Remap stored skinCluster influence data from one influence to another
		@param oldInfluence: The influence to remap from. Source influence
		@type oldInfluence: str
		@param newInfluence: The influence to remap to. Target influence
		@type newInfluence: str
		'''
		# Check influence
		if not self._influenceData.has_key(oldInfluence):
			print ('No data stored for influence "'+oldInfluence+'" in skinCluster "'+self._data['name']+'"! Skipping...')
			return 
			#raise Exception('No data stored for influence "'+oldInfluence+'" in skinCluster "'+self._data['name']+'"!')
		
		# Update influence data
		self._influenceData[newInfluence] = self._influenceData[oldInfluence]
		self._influenceData.pop(oldInfluence)
		
		# Print message
		print('Remapped influence "'+oldInfluence+'" to "'+newInfluence+'" for skinCluster "'+self._data['name']+'"!')
	
	def combineInfluence(self,sourceInfluenceList,targetInfluence,removeSource=False):
		'''
		Combine stored skinCluster influence data from a list of source influences to a single target influence.
		Source influences data will be removed.
		@param sourceInfluenceList: The list influence data to combine
		@type sourceInfluenceList: str
		@param targetInfluence: The target influence to remap the combined data to.
		@type targetInfluence: str
		'''
		# ===========================
		# - Check Source Influences -
		# ===========================
		
		skipSource = []
		for i in range(len(sourceInfluenceList)):
			
			# Check influence
			if not self._influenceData.has_key(sourceInfluenceList[i]):
				print('No data stored for influence "'+sourceInfluenceList[i]+'" in skinCluster "'+self._data['name']+'"! Skipping...')
				skipSource.append(sourceInfluenceList[i])
		
		# =============================
		# - Initialize Influence Data -
		# =============================
		
		if list(set(sourceInfluenceList)-set(skipSource)):
			if not self._influenceData.has_key(targetInfluence):
				self._influenceData[targetInfluence] = {'index':0,'type':0,'bindPreMatrix':''}
		else:
			return
		
		# ==========================
		# - Combine Influence Data -
		# ==========================
		
		wtList = []
		for i in range(len(sourceInfluenceList)):
			
			# Get Source Influence
			sourceInfluence = sourceInfluenceList[i]
			
			# Check Skip Source
			if skipSource.count(sourceInfluence): continue
			
			# Get Basic Influence Data from first source influence
			if not i:
				
				# Index
				self._influenceData[targetInfluence]['index'] = self._influenceData[sourceInfluence]['index']
				
				# Type
				self._influenceData[targetInfluence]['type'] = self._influenceData[sourceInfluence]['type']
				
				# Poly Smooth
				if self._influenceData[sourceInfluence].has_key('polySmooth'):
					self._influenceData[targetInfluence]['polySmooth'] = self._influenceData[sourceInfluence]['polySmooth']
				else:
					if self._influenceData[targetInfluence].has_key('polySmooth'):
						self._influenceData[targetInfluence].pop('polySmooth')
				
				# Nurbs Samples
				if self._influenceData[sourceInfluence].has_key('nurbsSamples'):
					self._influenceData[targetInfluence]['nurbsSamples'] = self._influenceData[sourceInfluence]['nurbsSamples']
				else:
					if self._influenceData[targetInfluence].has_key('nurbsSamples'):
						self._influenceData[targetInfluence].pop('nurbsSamples')
			
				# Get Source Influence Weights 
				wtList = self._influenceData[sourceInfluence]['wt']
			
			else:
				
				if wtList:
				
					# Combine Source Influence Weights
					wtList = [(x+y) for x,y in zip(wtList,self._influenceData[sourceInfluence]['wt'])]
				
				else:
					
					wtList = self._influenceData[sourceInfluence]['wt']
		
		# ==================================
		# - Assign Combined Source Weights -
		# ==================================
		
		self._influenceData[targetInfluence]['wt'] = wtList
		
		# =======================================
		# - Remove Unused Source Influence Data -
		# =======================================
		
		if removeSource:
		
			# For Each Source Influence
			for sourceInfluence in sourceInfluenceList:
				
				# Check Skip Source
				if skipSource.count(sourceInfluence): continue
				
				# Check Source/Target
				if sourceInfluence != targetInfluence:
					
					# Remove Unused Source Influence
					self._influenceData.pop(sourceInfluence)
	
	def remapGeometry(self,geometry):
		'''
		Remap the skinCluster data for one geometry to another
		@param geometry: The geometry to remap to the skinCluster
		@type geometry: str
		'''
		# Checks
		oldGeometry = self._data['affectedGeometry'][0]
		if geometry == oldGeometry: return geometry
			
		# Check Skin Geo Data
		if not self._data.has_key(oldGeometry):
			raise Exception('SkinClusterData: No skin geometry data for affected geometry "'+oldGeometry+'"!')
		
		# Remap Geometry
		self._data['affectedGeometry'] = [geometry]
		
		# Update Skin Geo Data
		self._data[geometry] = self._data[oldGeometry]
		self._data.pop(oldGeometry)
		
		# Print Message
		print('Geometry for skinCluster "'+self._data['name']+'" remaped from "'+oldGeometry+'" to "'+geometry+'"')
		
		# Return result
		return self._data['affectedGeometry']
	
	def rebuildWorldSpaceData(self,targetGeo='',method='closestPoint'):
		'''
		Rebuild the skinCluster deformer membership and weight arrays for the specified geometry using the stored world space geometry data.
		@param targetGeo: Geometry to rebuild world space deformer data for. If empty, use sourceGeo.
		@type targetGeo: str
		@param method: Method for worldSpace transfer. Valid options are "closestPoint" and "normalProject".
		@type method: str
		'''
		# Start timer
		timer = mc.timerX()
		
		# Display Progress
		glTools.utils.progressBar.init(status=('Rebuilding world space skinCluster data...'),maxValue=100)
		
		# ==========
		# - Checks -
		# ==========
		
		# Get Source Geometry
		sourceGeo = self._data['affectedGeometry'][0]
		
		# Target Geometry
		if not targetGeo: targetGeo = sourceGeo
		
		# Check Deformer Data
		if not self._data.has_key(sourceGeo):
			glTools.utils.progressBar.end()
			raise Exception('No deformer data stored for geometry "'+sourceGeo+'"!')
		
		# Check Geometry
		if not mc.objExists(targetGeo):
			glTools.utils.progressBar.end()
			raise Exception('Geometry "'+targetGeo+'" does not exist!')
		if not glTools.utils.mesh.isMesh(targetGeo):
			glTools.utils.progressBar.end()
			raise Exception('Geometry "'+targetGeo+'" is not a valid mesh!')
		
		# Check Mesh Data
		if not self._data[sourceGeo].has_key('mesh'):
			glTools.utils.progressBar.end()
			raise Exception('No world space mesh data stored for mesh geometry "'+sourceGeo+'"!')
		
		# =====================
		# - Rebuild Mesh Data -
		# =====================
		
		meshData = self._data[sourceGeo]['mesh']._data
		
		meshUtil = OpenMaya.MScriptUtil()
		numVertices = len(meshData['vertexList'])/3
		numPolygons = len(meshData['polyCounts'])
		polygonCounts = OpenMaya.MIntArray()
		polygonConnects = OpenMaya.MIntArray()
		meshUtil.createIntArrayFromList(meshData['polyCounts'],polygonCounts)
		meshUtil.createIntArrayFromList(meshData['polyConnects'],polygonConnects)
		
		# Rebuild Vertex Array
		vertexArray = OpenMaya.MFloatPointArray(numVertices,OpenMaya.MFloatPoint.origin)
		vertexList = [vertexArray.set(i,meshData['vertexList'][i*3],meshData['vertexList'][i*3+1],meshData['vertexList'][i*3+2],1.0) for i in xrange(numVertices)]
		
		# Rebuild Mesh
		meshFn = OpenMaya.MFnMesh()
		meshDataFn = OpenMaya.MFnMeshData().create()
		meshObj = meshFn.create(numVertices,numPolygons,vertexArray,polygonCounts,polygonConnects,meshDataFn)
		
		# Create Mesh Intersector
		meshPt = OpenMaya.MPointOnMesh()
		meshIntersector = OpenMaya.MMeshIntersector()
		if method == 'closestPoint': meshIntersector.create(meshObj)
		
		# ========================================
		# - Rebuild Weights and Membership List -
		# ========================================
		
		# Initialize Influence Weights and Membership
		influenceList = self._influenceData.keys()
		influenceWt = [[] for inf in influenceList]
		membership = set([])
		
		# Get Target Mesh Data
		targetMeshFn = glTools.utils.mesh.getMeshFn(targetGeo)
		targetMeshPts = targetMeshFn.getRawPoints()
		numTargetVerts = targetMeshFn.numVertices()
		targetPtUtil = OpenMaya.MScriptUtil()
		
		# Initialize Float Pointers for Barycentric Coords
		uUtil = OpenMaya.MScriptUtil(0.0)
		vUtil = OpenMaya.MScriptUtil(0.0)
		uPtr = uUtil.asFloatPtr()
		vPtr = vUtil.asFloatPtr()
		
		# Get Progress Step
		progressInd = int(numTargetVerts*0.01)
		if progressInd < 1: progressInd = 1 
		
		for i in range(numTargetVerts):
			
			# Get Target Point
			targetPt = OpenMaya.MPoint(	targetPtUtil.getFloatArrayItem(targetMeshPts,(i*3)+0),
										targetPtUtil.getFloatArrayItem(targetMeshPts,(i*3)+1),
										targetPtUtil.getFloatArrayItem(targetMeshPts,(i*3)+2)	)
			
			# Get Closest Point Data
			meshIntersector.getClosestPoint(targetPt,meshPt)
			
			# Get Barycentric Coords
			meshPt.getBarycentricCoords(uPtr,vPtr)
			u = OpenMaya.MScriptUtil(uPtr).asFloat()
			v = OpenMaya.MScriptUtil(vPtr).asFloat()
			baryWt = [u,v,1.0-(u+v)]
			
			# Get Triangle Vertex IDs
			idUtil = OpenMaya.MScriptUtil([0,1,2])
			idPtr = idUtil.asIntPtr()
			meshFn.getPolygonTriangleVertices(meshPt.faceIndex(),meshPt.triangleIndex(),idPtr)
			triId = [OpenMaya.MScriptUtil().getIntArrayItem(idPtr,n) for n in range(3)]
			memId = [self._data[sourceGeo]['membership'].count(t) for t in triId]
			wtId = [self._data[sourceGeo]['membership'].index(t) for t in triId]
			
			# For Each Influence
			for inf in range(len(influenceList)):
				
				# Calculate Weight and Membership
				wt = 0.0
				isMember = False
				for n in range(3):
					
					# Check Against Source Membership
					if memId[n]:
						wt += self._influenceData[influenceList[inf]]['wt'][wtId[n]] * baryWt[n]
						isMember = True
				
				# Check Member
				if isMember:
					# Append Weight Value
					influenceWt[inf].append(wt)
					# Append Membership
					membership.add(i)
			
			# Update Progress Bar
			if not i % progressInd: glTools.utils.progressBar.update(step=1)
		
		# ========================
		# - Update Deformer Data -
		# ========================
		
		# Remap Geometry
		self.remapGeometry(targetGeo)
		
		# Rename SkinCluster
		targetSkinCluster = glTools.utils.skinCluster.findRelatedSkinCluster(targetGeo)
		if targetSkinCluster:
			self._data['name'] = targetSkinCluster
		else:
			prefix = targetGeo.split(':')[-1]
			self._data['name'] = prefix+'_skinCluster'
		
		# Update Membership and Weights
		self._data[sourceGeo]['membership'] = list(membership)
		for inf in range(len(influenceList)):
			self._influenceData[influenceList[inf]]['wt'] = influenceWt[inf]
		
		# =================
		# - Return Result -
		# =================
		
		# End Progress
		glTools.utils.progressBar.end()	
		
		# Print Timed Result
		buildTime = mc.timerX(st=timer)
		print('SkinClusterData: Rebuild world space data for skinCluster "'+self._data['name']+'": '+str(buildTime))
		
		# Return Weights
		return
	
	def mirror(self,search='lf',replace='rt'):
		'''
		Mirror SkinCluster Data using search and replace for naming.
		This method doesn not perform closest point on surface mirroring.
		@param search: Search for this string in skinCluster, geometry and influence naming and replace with the "replace" string.
		@type search: str
		@param replace: The string to replace all instances of the "search" string for skinCluster, geometry and influence naming.
		@type replace: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		# ===========================
		# - Search and Replace Name -
		# ===========================
		
		if self._data['name'].count(search):
			self._data['name'] = self._data['name'].replace(search,replace)
		
		# ===============================
		# - Search and Replace Geometry -
		# ===============================
		
		for i in range(len(self._data['affectedGeometry'])):
			
			if self._data['affectedGeometry'][i].count(search):
				# Get 'mirror' geometry
				mirrorGeo = self._data['affectedGeometry'][i].replace(search,replace)
				# Check 'mirror' geometry
				if not mc.objExists(mirrorGeo):
					print ('WARNING: Mirror geoemtry "'+mirrorGeo+'" does not exist!')
				# Assign 'mirror' geometry
				self.remapGeometry(mirrorGeo)
				#self._data['affectedGeometry'][i] = mirrorGeo
		
		# Search and Replace Inlfuences
		influenceList = self._influenceData.keys()
		for i in range(len(influenceList)):
			
			if influenceList[i].count(search):
				# Get 'mirror' influence
				mirrorInfluence = influenceList[i].replace(search,replace)
				# Check 'mirror' influence
				if not mc.objExists(mirrorInfluence):
					print ('WARNING: Mirror influence "'+mirrorInfluence+'" does not exist!')
				# Assign 'mirror' influence
				self.remapInfluence(influenceList[i],mirrorInfluence)

class SkinClusterListData( data.Data ):
	'''
	SkinCluster List Data Class Object
	Contains functions to save, load and rebuild multiple skinCluster data.
	'''
	def __init__(self):
		'''
		SkinClusterListData class initializer.
		'''
		# Execute Super Class Initilizer
		super(SkinClusterListData, self).__init__()
	
	def buildData(self,skinClusterList):
		'''
		Build SkinClusterList data.
		@param skinClusterList: List of skinClusters to build data for
		@type skinClusterList: str
		'''
		# For Each SkinCluster
		for skinCluster in skinClusterList:
			
			# Check skinCluster
			if not mc.objExists(skinCluster):
				raise Exception('SkinCluster "'+skinCluster+'" does not exist!')
			if not glTools.utils.skinCluster.isSkinCluster(skinCluster):
				raise Exception('"'+skinCluster+'" is not a valid skinCluster!')
			
			# Build SkinCLuster Data
			self._data[skinCluster] = SkinClusterData()
			self._data[skinCluster].buildData(skinCluster)
	
	def rebuild(self,skinClusterList):
		'''
		Rebuild a list of skinClusters from the stored SkinClusterListData
		@param skinClusterList: List of skinClusters to rebuild
		@type skinClusterList: dict
		'''
		# Start timer
		timer = mc.timerX()
		
		# For Each SkinCluster
		for skinCluster in skinClusterList:
			
			# Check skinClusterData
			if not self._data.has_key(skinCluster):
				print('No data stored for skinCluster "'+skinCluster+'"! Skipping...')
			
			# Rebuild SkinCluster
			self._data[skinCluster].rebuild()
		
		# Print timed result
		totalTime = mc.timerX(st=timer)
		print('SkinClusterListData: Total build time for skinCluster list: '+str(skinTime))
