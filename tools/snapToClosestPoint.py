import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.mesh

def snapToClosestPoint(ptList,targetGeo,threshold=0.0001):
	'''
	Snap a list of points to the closest point component of a target geometry
	@param ptList: List of points to snap to target geometry. Can be transforms or components.
	@type ptList: list
	@param targetGeo: Target mesh to snap points to
	@type targetGeo: str
	@param threshold: If a point is closer to the target mesh than this distance, it will snap point.
	@type threshold: float
	'''
	# Check target mesh
	if not mc.objExists(targetGeo):
		raise Exception('Target geoemetry "'+targetGeo+'" does not exist!!')
	
	# Get target point array
	targetPtArray = glTools.utils.base.getMPointArray(targetGeo)
	
	# Flatten input point list
	ptList = mc.ls(ptList,fl=True)
	
	# Iterate through input points
	for pt in ptList:
		
		# Initialize distance values
		dist = 0
		minDist = 99999
		
		# Initialize point values
		mPt = glTools.utils.base.getMPoint(pt)
		tPt = mPt
		
		# Find closest point
		for i in range(targetPtArray.length()):
			
			# Get distance to point
			dist = (mPt - targetPtArray[i]).length()
			if dist < minDist:
				minDist = dist
				tPt = targetPtArray[i]
			
			# Check thrshold distance
			if (threshold > 0.0) and (dist < threshold): break
		
		# Move to target point
		mc.move(tPt[0],tPt[1],tPt[2],pt,ws=True)
