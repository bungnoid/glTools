import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.utils.skinCluster

import cPickle
import os.path

class SkinClusterData( object ):
	'''
	'''
	def __init__(self):
		'''
		'''
		self.data = {}
	
	def buildData(self,skinClusterList=[]):
		'''
		Build skinCluster data and store as class object dictionary entries
		@param skinClusterList: List of scene skinClusters to store data for. If empty, use all existing skinClusters.
		@type skinClusterList: list
		'''
		# Check skinCluster list
		if not skinClusterList:
			skinClusterList = mc.ls(type='skinCluster')
		
		# Reset data
		self.data = {}
		
		# Start global timer
		gTimer = mc.timerX()
		
		# For each skinCluster
		for skinCluster in skinClusterList:
			
			# Start timer
			timer = mc.timerX()
			
			# Add skinCluster data entry
			self.data[skinCluster] = {}
			
			# Get affected geometry
			skinGeo = mc.skinCluster(skinCluster,q=True,g=True)
			if not skinGeo: raise Exception('Unable to determine affected geometry for skinCluster "'+skinCluster+'"!')
			skinGeo = mc.listRelatives(skinGeo[0],p=True,pa=True)
			if not skinGeo: raise Exception('Unable to determine geometry transform for object "'+skinGeo+'"!')
			self.data[skinCluster]['geo'] = skinGeo[0]
			
			# Get Use Components Value
			self.data[skinCluster]['useComponents'] = mc.getAttr(skinCluster+'.useComponents')
			
			# Get skinCluster influence list
			infList = mc.skinCluster(skinCluster,q=True,inf=True)
			if not infList: raise Exception('Unable to determine influence list for skinCluster "'+skinCluster+'"!')
			self.data[skinCluster]['inf'] = infList
			
			# For each influence
			for influence in infList:
				
				# Initialize influence data
				self.data[skinCluster][influence] = {}
				
				# Get influence index
				infIndex = glTools.utils.skinCluster.getInfluenceIndex(skinCluster,influence)
				self.data[skinCluster][influence]['index'] = infIndex
				
				# Get influence type (transform/geometry)
				infGeomConn = mc.listConnections(skinCluster+'.driverPoints['+str(infIndex)+']')
				if infGeomConn:
					self.data[skinCluster][influence]['type'] = 1
					self.data[skinCluster][influence]['polySmooth'] = mc.skinCluster(skinCluster,inf=influence,q=True,ps=True)
					self.data[skinCluster][influence]['nurbsSamples'] = mc.skinCluster(skinCluster,inf=influence,q=True,ns=True)
				else:
					self.data[skinCluster][influence]['type'] = 0
				
				# Get influence weights
				try:
					influenceWt = glTools.utils.skinCluster.getInfluenceWeights(skinCluster,influence)
				except:
					print('Using alternate save method for influence "'+influence+'"!')
					influenceWt = glTools.utils.skinCluster.getInfluenceWeightsSlow(skinCluster,influence)
					
				self.data[skinCluster][influence]['wt'] = influenceWt
			
			skinTime = mc.timerX(st=timer)
			print('Data build time for "'+skinCluster+'": '+str(skinTime))
		
		# Print timed result
		totalTime = mc.timerX(st=gTimer)
		print('Total data build time: '+str(totalTime))

	def rebuild(self,skinClusterList=[]):
		'''
		Rebuild a list of skinClusters using the data stored in the class member dictionaries.
		@param skinClusterList: List of scene skinClusters to rebuild. If empty, use all saved skinClusters.
		@type skinClusterList: list
		'''
		# Check skinClusterList
		if not skinClusterList: skinClusterList = self.data.keys()
		
		# Start timer
		print('Rebuilding skinClusters...')
		timer = mc.timerX()
		
		# Rebuild each skinCluster
		for skinCluster in skinClusterList:
			
			# Check skinCluster
			if not self.data.has_key(skinCluster):
				raise Exception('No data stored for skinCluster "'+skinCluster+'"!')
			
			# Rebuild skinCluster
			self.rebuildSkinCluster(skinCluster)
		
		# Print timed result
		totalTime = mc.timerX(st=timer)
		print('Total rebuild time: '+str(totalTime))
	
	def rebuildSkinCluster(self,skinCluster):
		'''
		Rebuild the specified skinCluster using stored data
		@param skinCluster: The skinCluster to rebuild.
		@type skinCluster: str
		'''
		# Check skinClusterData
		if not self.data.has_key(skinCluster):
			raise Exception('No data stored for skinCluster "'+skinCluster+'"!')
		skinData = self.data[skinCluster]
		
		# Check geometry
		skinGeo = skinData['geo']
		if not mc.objExists(skinGeo):
			raise Exception('SkinCluster geometry "'+skinGeo+'" does not exist! Use remapGeometry() to load skinCluster data for a different geometry!')
		
		# Start timer
		timer = mc.timerX()
		
		# Check skinCluster
		tempJnt = ''
		if not mc.objExists(skinCluster):
		
			# Create temporary bind joint
			mc.select(cl=1)
			tempJnt = mc.joint(n='tempJoint')
			
			# Create skinCluster
			skinCluster = mc.skinCluster(tempJnt,skinGeo,n=skinCluster)[0]
		
		# Add skinCluster influences
		infList = skinData['inf']
		for influence in infList:
			
			# Check influence
			if not mc.objExists(influence):
				raise Exception('Influence "'+influence+'" does not exist! Use remapInfluence() to apply data to a different influence!')
			
			# Check existing influence connection
			if not mc.skinCluster(skinCluster,q=True,inf=True).count(influence):
			
				# Add influence
				if self.data[skinCluster][influence]['type']:
					polySmooth = self.data[skinCluster][influence]['polySmooth']
					nurbsSamples = self.data[skinCluster][influence]['nurbsSamples']
					mc.skinCluster(skinCluster,e=True,ai=influence,ug=True,ps=polySmooth,ns=nurbsSamples)
				else:
					mc.skinCluster(skinCluster,e=True,ai=influence)
		
		# Remove temporary influence
		if mc.objExists(tempJnt):
			try: mc.skinCluster(skinCluster,e=True,ri=tempJnt)
			except: pass
			mc.delete(tempJnt)
			
		# Load skinCluster weights
		mc.setAttr(skinCluster+'.normalizeWeights',0)
		glTools.utils.skinCluster.clearWeights([skinGeo])
		self.setWeights(skinCluster)
		mc.setAttr(skinCluster+'.normalizeWeights',1)
		
		# Set Use Components Value
		if self.data[skinCluster].has_key('useComponents'):
			mc.setAttr(skinCluster+'.useComponents',self.data[skinCluster]['useComponents'])
		
		# Clear selection
		mc.select(cl=True)
		
		# Print timed result
		totalTime = mc.timerX(st=timer)
		print('Rebuild time for skinCluster "'+skinCluster+'": '+str(totalTime))
	
	def setWeights(self,skinCluster):
		'''
		'''
		# Check skinClusterData
		if not self.data.has_key(skinCluster):
			raise Exception('No data stored for skinCluster "'+skinCluster+'"!')
		skinData = self.data[skinCluster]
		
		# Check geometry
		skinGeo = skinData['geo']
		if not mc.objExists(skinGeo):
			raise Exception('SkinCluster geometry "'+skinGeo+'" does not exist! Use remapGeometry() to load skinCluster data for a different geometry!')
		
		# Check component list
		componentList = glTools.utils.component.getComponentStrList(skinGeo)
		componentSel = glTools.utils.selection.getSelectionElement(componentList,0)
		
		# Build influence index array
		infIndexArray = OpenMaya.MIntArray()
		influenceList = skinData['inf']
		[infIndexArray.append(i) for i in range(len(influenceList))]
		
		# Build master weight array
		wtArray = OpenMaya.MDoubleArray()
		oldWtArray = OpenMaya.MDoubleArray()
		for c in range(len(componentList)):
			for i in range(len(influenceList)):
				wtArray.append(skinData[influenceList[i]]['wt'][c])
		
		# Get skinCluster function set
		skinFn = glTools.utils.skinCluster.getSkinClusterFn(skinCluster)
		
		# Set skinCluster weights
		skinFn.setWeights(componentSel[0],componentSel[1],infIndexArray,wtArray,False,oldWtArray)
	
	def remapInfluence(self,oldInfluence,newInfluence,skinClusterList=[]):
		'''
		Remap stored skinCluster influence data from one influence to another
		@param oldInfluence: The influence to remap from. Source influence
		@type oldInfluence: str
		@param newInfluence: The influence to remap to. Target influence
		@type newInfluence: str
		@param skinClusterList: List of scene skinClusters to remap influences for. If empty, use all saved skinClusters.
		@type skinClusterList: list
		'''
		# Check skinClusterList
		if not skinClusterList: skinClusterList = self.data.keys()
		
		# For each skinCluster
		for skinCluster in skinClusterList:
			
			# Check skinCluster
			if not self.data.has_key(skinCluster):
				raise Exception('No data stored for skinCluster "'+skinCluster+'"!')
			
			# Get influence list
			infList = self.data[skinCluster]['inf']
			
			# Check influence
			if not infList.count(oldInfluence): continue
			if not self.data[skinCluster].has_key(oldInfluence):
				raise Exception('No data stored for influence "'+oldInfluence+'" in skinCluster "'+skinCluster+'"!')
			
			# Replace item in influence list
			infIndex = infList.index(oldInfluence)
			infList[infIndex] = newInfluence
			
			# Update influence data
			self.data[skinCluster][newInfluence] = self.data[skinCluster][oldInfluence]
			self.data[skinCluster].pop[oldInfluence]
	
	def remapGeometry(self,skinCluster,geometry):
		'''
		Remap the skinCluster data for one geometry to another
		@param skinCluster: The skinCluster to remap geometry for
		@type skinCluster: str
		@param geometry: The geometry to remap to the specified skinCluster
		@type geometry: str
		'''
		# Check skinCluster
		if not self.data.has_key(skinCluster):
			raise Exception('No data stored for skinCluster "'+skinCluster+'"!')
		
		# Remap geometry
		oldGeometry = self.data[skinCluster]['geo']
		self.data[skinCluster]['geo'] = geometry
		
		# Print message
		print('Geometry for skinCluster "'+skinCluster+'" remaped from "'+oldGeometry+'" to "'+geometry+'"')
		
		# Return result
		return geometry
		
	def save(self,filePath):
		'''
		Save skinCluster data object to file.
		@param filePath: Target file path
		@type filePath: str
		'''
		# Check filePath
		dirpath = filePath.replace(filePath.split('/')[-1],'')
		if not os.path.isdir(dirpath): os.makedirs(dirpath)
		
		# Export data to file
		fileOut = open(filePath,'wb')
		cPickle.dump(self,fileOut)
		fileOut.close()
		
		# Return result
		return filePath
		
	def load(self,filePath):
		'''
		Load control curve data object from file.
		@param filePath: Target file path
		@type filePath: str
		'''
		# Check filePath
		if not os.path.isfile(filePath):
			raise Exception('Invalid path "'+filePath+'"!')
		
		# Load file data
		fileIn = open(filePath,'rb')
		return cPickle.load(fileIn)

