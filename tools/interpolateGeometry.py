import maya.cmds as mc

import random

def interpolateGeometry(geoList,numGeo,prefix='interpGeo'):
	'''
	'''
	# Initialize outoput list
	dupGeoList = []
	
	# Generate base Geo
	baseGeo = mc.duplicate(geoList[0],n=prefix+'_baseGeo')[0]
	baseTargetList = geoList[1:]
	baseBlendShape = mc.blendShape(baseTargetList,baseGeo)[0]
	baseBlendAlias = mc.listAttr(baseBlendShape+'.w',m=True)
	baseBlendCount = len(baseBlendAlias)
	baseBlendWeight = 1.0/baseBlendCount
	for i in range(baseBlendCount): mc.setAttr(baseBlendShape+'.'+baseBlendAlias[i],baseBlendWeight)
	
	# Generate interpolated geometry
	for i in range(numGeo):
		
		# Duplicate Geo as blended
		intGeo = mc.duplicate(baseGeo,n=prefix+'#')[0]
		mc.parent(intGeo,w=True)
		
		# Blend to source geometry
		intBlendShape = mc.blendShape(geoList,intGeo)[0]
		intBlendAlias = mc.listAttr(intBlendShape+'.w',m=True)
		intBlendCount = len(intBlendAlias)
		
		# Generate blend weights
		wt = []
		wtTotal = 0.0
		for i in range(intBlendCount):
			wt.append(random.random())
			wtTotal += wt[-1]
		for i in range(len(wt)):
			wt[i] /= wtTotal
		
		# Assign blend weights
		for i in range(intBlendCount):
			mc.setAttr(intBlendShape+'.'+intBlendAlias[i],wt[i])
		
		# Append output list
		dupGeoList.append(intGeo)
	
	# Delete base Geo
	mc.delete(baseGeo)
	
	# Return result
	return dupGeoList
