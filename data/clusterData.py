import maya.cmds as mc

import glTools.utils.base

import deformerData

class ClusterData( deformerData.DeformerData ):
	'''
	ClusterData class object.
	'''
	def __init__(self):
		'''
		ClusterData class initializer.
		'''
		# Execute Super Class Initilizer
		super(ClusterData, self).__init__()
		
		# Initialize Cluster Handle Data
		self._data['clusterHandle'] = ''
		
		# Deformer Attribute Connections
		#self._data['attrConnectionList'].append('matrix')
		self._data['attrConnectionList'].append('bindPreMatrix')
		self._data['attrConnectionList'].append('geomMatrix')
	
	def buildData(self,cluster):
		'''
		Build ClusterData class data.
		@param cluster: Cluster deformer to initialize data for
		@type cluster: str
		'''
		# Verify node
		glTools.utils.base.verifyNode(cluster,'cluster')
		
		# Reset Data Object
		self.reset()
		
		# Buid Data
		super(ClusterData, self).buildData(cluster)
		
		# Store ClusterHandle Data
		clsHandle = mc.listConnections(cluster+'.matrix',s=True,d=False,sh=True)
		if clsHandle: self._data['clusterHandle'] = clsHandle[0]
		
		# Return Result
		return cluster
	
	def rebuild(self,overrides={}):
		'''
		Rebuild the cluster deformer from the recorded deformerData
		@param overrides: Dictionary of data overrides to apply 
		@type overrides: dict
		'''
		# Apply Overrides
		self._data.update(overrides)
		
		# ==========
		# - Checks -
		# ==========
		
		# Check target geometry
		for obj in self._data['affectedGeometry']:
			if not mc.objExists(obj):
				raise Exception('Deformer affected object "'+obj+'" does not exist!')
		
		# ====================
		# - Rebuild Deformer -
		# ====================
		
		# Build Cluster Deformer and Handle
		if not mc.objExists(self._data['name']):
			# Create New Cluster
			cluster = mc.cluster(self.getMemberList(),n=self._data['name'])
			self._data['name'] = cluster[0]
		else:
			# Check Cluster
			if mc.objectType(self._data['name']) != 'cluster':
				raise Exception('Object "'+self._data['name']+'" is not a valid cluster deformer!')
		
		# Rebuild Deformer
		result = super(ClusterData, self).rebuild(overrides)
		
		# Restore ClusterHandle Data
		if self._data['clusterHandle']:
			if not mc.objExists(self._data['clusterHandle']):
				raise Exception('Weighted Node "'+self._data['clusterHandle']+'" does not exist!')
			try:
				mc.cluster(self._data['name'],edit=True,bindState=True,wn=(self._data['clusterHandle'],self._data['clusterHandle']))
			except:
				pass
		
		# =================
		# - Return Result -
		# =================
		
		return result
		
