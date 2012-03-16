import clusterData

class ClusterBlendData( object ):
	'''
	ClusterBlendData class object.
	Contains functions to save, load and rebuild clusterBlend data.
	'''
	# INIT
	def __init__(self,clusterX='',clusterY='',clusterZ=''):
		'''
		ClusterBlendData class initializer.
		'''
		# Initialize class data members
		self.clusterXData = None
		self.clusterYData = None
		self.clusterZData = None
		
		# Check clusters
		if (not clusterX) and (not clusterY) and (not clusterZ): return
		if (not clusterX) or (not clusterY) or (not clusterZ):
			raise UserInputError('You must specify 3 valid clusters!')
		
		# Generate ClusterBlend Data
		self.clusterXData = clusterData.ClusterData(clusterX)
		self.clusterYData = clusterData.ClusterData(clusterY)
		self.clusterZData = clusterData.ClusterData(clusterZ)
	
	def rebuild(self):
		'''
		Rebuild clusterBlend from object data.
		'''
		# Rebuild ClusterBlend Deformers
		self.clusterXData.rebuild()
		self.clusterYData.rebuild()
		self.clusterZData.rebuild()
		
		# Set Cluster Translate Values
		if mc.getAttr(self.clusterXData.handle+'.tx',se=True): mc.setAttr(self.clusterXData.handle+'.tx',1.0)
		if mc.getAttr(self.clusterYData.handle+'.ty',se=True): mc.setAttr(self.clusterYData.handle+'.ty',1.0)
		if mc.getAttr(self.clusterZData.handle+'.tz',se=True): mc.setAttr(self.clusterZData.handle+'.tz',1.0)
	
	def loadWeights():
		'''
		Load clusterBlend weight values
		'''
		self.clusterXData.loadWeights()
		self.clusterYData.loadWeights()
		self.clusterZData.loadWeights()

