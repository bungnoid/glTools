import maya.cmds as mc

import glTools.utils.attribute
import glTools.utils.deformer

def isTangentBlend(tangentBlend):
	'''
	Test if node is a valid tangentBlendDeformer
	@param tangentBlend: Name of tangentBlend node to query
	@type tangentBlend: str
	'''
	# Check blendShape exists
	if not mc.objExists(tangentBlend): return False
	# Check object type
	if mc.objectType(tangentBlend) != 'tangentBlendDeformer': return False
	# Return result
	return True

def unlockTransform(node):
	'''
	Unlock transform channels
	@param node: Transform to ulock channels for
	@type node: str
	'''
	# Define attribute list
	attrList = ['tx','ty','tz','t','rx','ry','rz','r','sx','sy','sz','s']
	# Unlock attributes
	for attr in attrList: mc.setAttr(node+'.'+attr, l=False)

def findTangentBlendDeformer(geo):
	'''
	Return the tangentBlend deformer attached to the specified geometry
	@param geo: Geometry to find attached tangentBlend deformer for
	@type geo: str
	'''
	# Get Geometry History
	tangentBlend = ''
	history = mc.listHistory(geo)
	
	# Check for tangentBlendDeformer
	for i in range(len(history)):
		if(mc.objectType(history[i],isAType='tangentBlendDeformer')):
			# Capture result
			tangentBlend = history[i]
	
	# Return result
	return tangentBlend
	
def findAffectedGeometry(tangentBlend):
	'''
	'''
	# Check deformer
	if not isTangentBlend(tangentBlend):
		raise Exception('Object "'+tangentBlend+'" is not a valid tangentBlend deformer node!')
	
	# Get affected geometry
	geometry = glTools.utils.deformer.getAffectedGeometry(tangentBlend).keys()[0]
	
	# Return result
	return geometry

def geomAttrName(shapeNode):
	'''
	'''
	# Get shape attribute based on geometry type
	attrType = mc.nodeType(shapeNode,api=True)
	if attrType == 'kNurbsCurve': return '.local'
	if attrType == 'kMesh': return '.outMesh'
	return '.'

def duplicateGeo(obj,name):
	'''
	'''
	# Duplicate Geometry
	dup = mc.duplicate(obj,name=name)[0]
	
	# Removed unused shapes
	dupShapes = mc.listRelatives(dup,s=True,ni=True)
	dupShapesAll = mc.listRelatives(dup,s=True)
	deleteShapes = list(set(dupShapesAll) - set(dupShapes))
	mc.delete(deleteShapes)
	
	# Unlock transforms
	unlockTransform(dup)
	
	# Return result
	return dup

def create(geo,name=''):
	'''
	'''
	# Load Plugin
	if not mc.pluginInfo('tangentBlendDeformer',q=True,l=True): mc.loadPlugin('tangentBlendDeformer')
	
	# Create Deformer
	if not name: name = geo+'_tangentBlendDeformer'
	tangentBlend = mc.deformer(geo,type='tangentBlendDeformer',n=name)[0]
	
	# Return Result
	return tangentBlend 

def connectPose(baseXForm,offsetXForm,deformer):
	'''
	'''
	# Get next available deformer index 
	index = glTools.utils.attribute.nextAvailableMultiIndex(deformer+'.pose',useConnectedOnly=False)
	
	# Get pose geometry shapes
	baseShape = mc.listRelatives(baseXForm,s=True,ni=True,pa=True)
	offsetShape = mc.listRelatives(offsetXForm,s=True,ni=True,pa=True)	
	
	# Connect pose base
	attrName = geomAttrName(baseShape[0])
	mc.connectAttr(baseShape[0]+attrName,deformer+'.pose['+str(index)+'].poseBaseMesh',f=True)
	# Connect pose offset
	attrName = geomAttrName(offsetShape[0])
	mc.connectAttr(offsetShape[0]+attrName,deformer+'.pose['+str(index)+'].poseOffsetMesh',f=True)
	
	# Return result
	return index

def addPose(tangentBlend,baseGeo='',offsetGeo='',poseName=''):
	'''
	'''
	# Define suffix tags
	tangentBlend_baseTag = '_poseBase'
	tangentBlend_offsetTag = '_poseOffset'
	
	# Get connected geometry
	geo = findAffectedGeometry(tangentBlend)
	
	# Check pose geometry
	if not baseGeo: baseGeo = duplicateGeo(geo,geo+tangentBlend_baseTag)
	if not offsetGeo: baseGeo = duplicateGeo(geo,geo+tangentBlend_offsetTag)
	
	# Connect to deformer
	poseIndex = connectPose(baseGeo,offsetGeo,tangentBlend)
	
	# Alias pose name and set keyable
	if poseName:
		mc.aliasAttr(poseName,tangentBlend+'.pose['+str(poseIndex)+'].poseWeight')
		mc.setAttr(tangentBlend+'.pose['+str(poseIndex)+'].poseWeight',cb=True)
		mc.setAttr(tangentBlend+'.pose['+str(poseIndex)+'].poseWeight',k=True)
	
	return [baseGeo,offsetGeo]
