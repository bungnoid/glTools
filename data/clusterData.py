import maya.cmds as mc

import deformerData

# Create exception class
class UserInputError(Exception): pass

class ClusterData( deformerData.DeformerData ):
	'''
	ClusterData class object.
	Contains functions to save, load and rebuild cluster deformer data.
	'''
	
	# INIT
	def __init__(self,cluster=''):
		
		# Escape
		if not cluster: return
		
		# Verify node
		if not mc.objExists(cluster):
			raise UserInputError('Cluster '+cluster+' does not exists! No influence data recorded!!')
		if mc.objectType(cluster) != 'cluster':
			raise UserInputError('Object '+cluster+' is not a vaild cluster deformer! Incorrect class for node type '+self.type+'!!')
		
		# Execute super class initilizer
		super(ClusterData, self).__init__(cluster)
		
		# Get clusterHandle name
		self.handle = mc.listConnections(cluster+'.matrix',s=True,d=False)[0]
		# Get bindPreMatrix connection
		self.bindPreMatrix = mc.listConnections(cluster+'.bindPreMatrix',s=True,d=False,p=True)
		# Get geomMatrix connection list
		self.geomMatrix = self.connectionUtils.connectionListToAttr(cluster,'geomMatrix')
	
	def rebuild(self):
		'''
		Rebuild the cluster deformer from the recorded deformerData
		'''
		# Check target geometry
		for obj in self.deformerData.iterkeys():
			if not mc.objExists(obj): raise UserInputError('Object '+obj+' does not exist!')
		# Check deformer
		if mc.objExists(self.deformerName):
			raise UserInputError('Cluster '+self.deformerName+' already exists!')
		
		# Rebuild deformer
		cluster = None
		if mc.objExists(self.handle):
			cluster = mc.cluster(self.getMemberList(),n=self.deformerName,wn=(self.handle,self.handle))
		else:
			cluster = mc.cluster(self.getMemberList(),n=self.deformerName)
			if cluster[1] != self.handle: mc.rename(cluster[1],self.handle)
		deformer = cluster[0]
		
		# Connect bindPreMatrix
		if self.bindPreMatrix:
			if mc.objExists(self.bindPreMatrix[0]):
				mc.connectAttr(self.bindPreMatrix[0],cluster+'.bindPreMatrix')
		
		# Connect geomMatrix
		for conn in self.geomMatrix.iterkeys():
			if mc.objExists(conn):
				mc.connectAttr(conn+'.'+self.geomMatrix[conn][0],cluster+'.geomMatrix['+str(self.geomMatrix[conn][1])+']')
		
		# Set cluster weights
		self.loadWeights()
		
		# Return result
		return deformer
