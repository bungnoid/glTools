import maya.cmds as mc

import glTools.utils.base
import glTools.utils.shape

def softBody(geometry,prefix=''):
	'''
	'''
	# Check prefix
	if not prefix: prefix = geometry
	
	# Check geometry
	geometryType = mc.objectType(geometry)
	if geometryType == 'transform':
		geometryTransform = geometry
		geometryShapes = glTools.utils.shape.getShapes(geometry,nonIntermediates=True,intermediates=False)
		if not geometryShapes: raise Exception('No valid geometry shapes found!')
		geometryShape = geometryShapes[0]
	else:
		geometryTransform = mc.listRelatives(geometry,p=True)[0]
		geometryShape = geometry
	
	# Check geometry type
	geometryType = mc.objectType(geometryShape)
	if geometryType == 'mesh': geometryAttribute = 'inMesh'
	elif geometryType == 'nurbsCurve': geometryAttribute = 'create'
	elif geometryType == 'nurbsSurface': geometryAttribute = 'create'
	else: raise Exception('Invalid geometry type ('+geometryType+')!')
	
	# Get geometry points
	mPtList = glTools.utils.base.getMPointArray(geometry)
	ptList = [(i[0],i[1],i[2]) for i in mPtList]
	
	# Create nParticles
	nParticle = mc.nParticle(p=ptList,n=prefix+'_nParticle')
	
	# Connect to geometry
	mc.connectAttr(geometryTransform+'.worldMatrix[0]',nParticle+'.targetGeometryWorldMatrix',f=True)
	mc.connectAttr(nParticle+'.targetGeometry',geometryShape+'.'+geometryAttribute,f=True)
	
	# Return result
	return nParticle
