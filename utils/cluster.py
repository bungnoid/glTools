import maya.cmds as mc

import glTools.utils.stringUtils

import types

def create(	geo,
			group			= True,
			bindPreMatrix	= None,
			prefix			= None ):
	'''
	Create cluster defomer
	@param geo: Geometry to deform
	@type geo: str or list
	@param group: Group cluster handle
	@type group: bool
	@param bindPreMatrix: Bind pre matrix transform. Or specify "parent" to connect cluster handle parentInverseMatrix.
	@type bindPreMatrix: str or None
	@param prefix: Naming prefix
	@type prefix: str or None
	'''
	# Check Geometry
	if isinstance(geo,types.ListType):
		prefix_geo = geo[0]
		for obj in geo:
			if not mc.objExists(obj):
				raise Exception('Geometry "'+obj+'" does not exist!')
	elif isinstance(geo,types.StringTypes):
		prefix_geo = geo
		if not mc.objExists(geo):
			raise Exception('Geometry "'+geo+'" does not exist!')
	
	# Check Prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(prefix_geo)
	
	# Create Cluster
	cluster = mc.cluster(geo,n=prefix+'_cluster')
	clusterHandle = cluster[1]
	clusterDeformer = cluster[0]
	
	# Group
	clusterGrp = None
	if group:
		clusterGrp = mc.duplicate(clusterHandle,po=True,n=prefix+'_clusterGrp')[0]
		mc.parent(clusterHandle,clusterGrp)
	
	# Bind Pre Matrix
	if bindPreMatrix:
		
		if bindPreMatrix == 'parent':
			# BindPreMatrix - ParentInverseMatrix
			mc.connectAttr(clusterHandle+'.parentInverseMatrix[0]',clusterDeformer+'.bindPreMatrix',f=True)
		else:
			# BindPreMatrix - Specified Transform
			if not mc.objExists(bindPreMatrix):
				raise Exception('Bind pre matrix transform "'+bindPreMatrix+'" does not exist!')
			if not glTools.utils.transform.isTransform(bindPreMatrix):
				raise Exception('Bind pre matrix transform "'+bindPreMatrix+'" is not a valid transform!')
			mc.connectAttr(bindPreMatrix+'.worldInverseMatrix[0]',clusterDeformer+'.bindPreMatrix',f=True)
	
	# Return Result
	return [clusterDeformer,clusterHandle,clusterGrp]
