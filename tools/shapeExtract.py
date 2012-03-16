import maya.cmds as mc
import maya.mel as mm

import glTools.utils.deformer
import glTools.utils.blendShape
import glTools.utils.skinCluster

def shapeExtract_skinCluster(baseGeo,targetGeo,skinCluster,influenceList=[],deleteHistory=True,prefix=''):
	'''
	'''
	# ---------
	# - Check -
	# ---------
	
	suffix = ''
	if prefix: suffix = '_'+prefix
	
	# Check base geo
	if not mc.objExists(baseGeo):
		raise Exception('Base geometry "'+baseGeo+'" does not exist!')
		
	# Check target geo
	if not mc.objExists(targetGeo):
		raise Exception('Target geometry "'+targetGeo+'" does not exist!')
	
	# Check skinCluster
	if not mc.objExists(skinCluster):
		raise Exception('SkinCluster "'+skinCluster+'" does not exist!')
	
	# ---------------------------
	# - Get skinCluster details -
	# ---------------------------
	
	# Get geometry affected by skinCluster
	skinGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]
	
	# Get skinClusterInfluence list
	if not influenceList:
		influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
	
	# ------------------------------
	# - Iterate through influences -
	# ------------------------------
	
	returnList = []
	for inf in influenceList:
		
		# Print progress
		print('Extracting region: '+inf+suffix)
		
		# Duplicate shape base
		dupGeo = mc.duplicate(baseGeo)[0]
		
		# Create blendShape to target
		blendShape = mc.blendShape(targetGeo,dupGeo)[0]
		mc.setAttr(blendShape+'.'+targetGeo,1)
		
		# Get skinCluster influence weights
		wt = glTools.utils.skinCluster.getInfluenceWeights(skinCluster,inf)
		
		# Set belndShape target weights
		glTools.utils.blendShape.setTargetWeights(blendShape,targetGeo,wt,dupGeo)
		
		# Delete history on duplicated geometry
		if deleteHistory: mc.delete(dupGeo,constructionHistory=True)
			
		# Rename extracted target
		dupGeo = mc.rename(dupGeo,inf+suffix)
		
		# Append to return list
		returnList.append(dupGeo)
		
	# Create shape group
	grp = mc.group(returnList,n=prefix+'_extract_grp',w=True)
	
	# -----------------
	# - Return result -
	# -----------------
	
	return returnList
