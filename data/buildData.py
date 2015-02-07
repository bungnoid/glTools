import maya.cmds as mc

import glTools.data.deformerData
import glTools.data.clusterData
import glTools.data.skinClusterData
import glTools.data.surfaceSkinData
import glTools.data.wireData

def buildDeformerData(deformer):
	'''
	Instantiate and Build a DeformerData object for the specified deformer node
	@param deformer: Deformer to build data object for
	@type deformer: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Deformer
	if not glTools.utils.deformer.isDeformer(deformer):
		raise Exception('Object "'+deformer+'" is not a valid deformer!')
	
	# Get Deformer Type
	deformerType = mc.objectType(deformer)
	
	# ============================
	# - Initialize Deformer Data -
	# ============================
	
	dData = glTools.data.deformerData.DeformerData()
	
	# Cluster
	if deformerType == 'cluster':
		dData = glTools.data.clusterData.ClusterData()
	
	# CurveTwist
	if deformerType == 'curveTwist':
		dData = glTools.data.clusterData.ClusterData()
	
	# DirectionalSmooth
	if deformerType == 'directionalSmooth':
		dData = glTools.data.deformerData.DirectionalSmoothData()
	
	# SkinCluster
	elif deformerType == 'skinCluster':
		dData = glTools.data.skinClusterData.SkinClusterData()
	
	# StrainRelaxer
	if deformerType == 'strainRelaxer':
		dData = glTools.data.deformerData.StrainRelaxerData()
		
	# SurfaceSkin
	elif deformerType == 'surfaceSkin':
		dData = glTools.data.surfaceSkinData.SurfaceSkinData()
	
	# Wire
	elif deformerType == 'wire':
		dData = glTools.data.wireData.WireData()
	
	# Unsupported Type !!
	else:
		print('Using base DeformerData class for "'+deformerType+'" deformer "'+deformer+'"!')
	
	# =======================
	# - Build Deformer Data -
	# =======================
	
	try:
		dData.buildData(deformer)
	except:
		raise Exception('DeformerData: Error building data object for deformer "'+deformer+'"!')
	
	# =================
	# - Return Result -
	# =================
	
	return dData
