import maya.cmds as mc

#import data

# Import Deformer Data
import deformerData
import clusterData
import latticeData
import pointToPointData
import skinClusterData
import surfaceSkinData
import wireData

# Import Constraint Data
import constraintData

# Import Geometry Data
import meshData
import nurbsCurveData
import nurbsSurfaceData

import setData
import channelData
import channelStateData

import glTools.utils.constraint
import glTools.utils.deformer
import glTools.utils.geometry

import types

def buildData(node):
	'''
	Build a data object for the specified node.
	@param node: Node to build data from.
	@type node: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Node
	if not mc.objExists(node):
		raise Exception('Node "'+node+'" does not exist! Unable to determine data type.')
	
	# =======================
	# - Determine Data Type -
	# =======================
	
	# Check Deformer
	if glTools.utils.deformer.isDeformer(node):
		return buildDeformerData(node)
	
	# Check Constraint
	if glTools.utils.constraint.isConstraint(node):
		return buildConstraintData(node)
	
	# Check Geometry
	if glTools.utils.geometry.isGeometry(node):
		return buildGeometryData(node)
	
	# Check Set
	if 'objectSet' in mc.nodeType(node,i=True):
		return setData.SetData(node)
	
	# =========================
	# - Unsupported Node Type -
	# =========================
	
	raise Exception('Unsupported node type! Unable to build data for "'+node+'" ('+mc.nodeType(node)+')')

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
	
	dDataObj = deformerData.DeformerData
	
	# BulgeSkinBasic
	if deformerType == 'bulgeSkinBasic':
		dDataObj = deformerData.BulgeSkinBasicData
	
	# BulgeSkinPrim
	elif deformerType == 'bulgeSkinPrim':
		dDataObj = deformerData.BulgeSkinPrimData
	
	# Cluster
	elif deformerType == 'cluster':
		dDataObj = clusterData.ClusterData
	
	# CurveTwist
	elif deformerType == 'curveTwist':
		dDataObj = clusterData.ClusterData
	
	# DirectionalSmooth
	elif deformerType == 'directionalSmooth':
		dDataObj = deformerData.DirectionalSmoothData
	
	# Lattice
	elif deformerType == 'ffd':
		dDataObj = latticeData.LatticeData
	
	# Peak
	elif deformerType == 'peakDeformer':
		dDataObj = deformerData.PeakDeformerData
	
	# SkinCluster
	elif deformerType == 'skinCluster':
		dDataObj = skinClusterData.SkinClusterData
	
	# StrainRelaxer
	elif deformerType == 'strainRelaxer':
		dDataObj = deformerData.StrainRelaxerData
		
	# SurfaceSkin
	elif deformerType == 'surfaceSkin':
		dDataObj = surfaceSkinData.SurfaceSkinData
	
	# Wire
	elif deformerType == 'wire':
		dDataObj = wireData.WireData
	
	# Unsupported Type !!
	else:
		print('Unsupported Deformer! Using base DeformerData class for '+deformerType+' "'+deformer+'"!')
	
	# =======================
	# - Build Deformer Data -
	# =======================
	
	dData = dDataObj()
	try: dData.buildData(deformer)
	except Exception, e:
		print(str(e))
		raise Exception('DeformerData: Error building data object for "'+deformer+'"!')
	
	# =================
	# - Return Result -
	# =================
	
	return dData

def buildConstraintData(constraint):
	'''
	Instantiate and Build a ConstraintData object for the specified constraint node
	@param constraint: Constraint to build data object for
	@type constraint: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not glTools.utils.constraint.isConstraint(constraint):
		raise Exception('Object "'+constraint+'" is not a valid constraint! Unable to build constraint data...')
	
	# Get Constraint Type
	constraintType = mc.objectType(constraint)
	
	# ==============================
	# - Initialize Constraint Data -
	# ==============================
	
	cDataObj = constraintData.ConstraintData
	
	if constraintType == 'aimConstraint':
		cDataObj = constraintData.AimConstraintData
	
	elif constraintType == 'pointConstraint':
		cDataObj = constraintData.PointConstraintData
	
	elif constraintType == 'orientConstraint':
		cDataObj = constraintData.OrientConstraintData
	
	elif constraintType == 'parentConstraint':
		cDataObj = constraintData.ParentConstraintData
	
	else:
		print('Unsupported Constraint! Using base ConstraintData class for '+constraintType+' "'+constraint+'"!')
	
	# =======================
	# - Build Deformer Data -
	# =======================
	
	cData = cDataObj()
	try: cData.buildData(constraint)
	except: raise Exception('ConstraintData: Error building data object for "'+constraint+'"!')
	
	# =================
	# - Return Result -
	# =================
	
	return cData

def buildGeometryData(geometry):
	'''
	Instantiate and Build a GeometryData object for the specified constraint node
	@param geometry: Geometry shape to build data object for
	@type geometry: str
	'''
	pass
