import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base

def transferComponentSelection(sourceSelection,targetMesh,threshold=0.0001):
	'''
	'''
	# Check selection target mesh
	if not mc.objExists(targetMesh):
		raise Exception('Target mesh "'+targetMesh+'" does not exist!')
	
	# Flatten selection
	sourceSelection = mc.ls(sourceSelection,fl=True)
	
	# Get mesh points
	tPtArray = glTools.utils.base.getMPointArray(targetMesh)
	tPtLen = tPtArray.length()
	
	# Initialize component selection transfer list
	tPtBool = [False for i in range(tPtLen)]
	
	# Initialize selection list
	tSel = []
	
	# Transfer selection
	for sel in sourceSelection:
		
		# Get selection point
		pt = mc.pointPosition(sel)
		pt = OpenMaya.MPoint(pt[0],pt[1],pt[2],1.0)
		
		# Find closest component
		cDist = 99999
		cIndex = -1
		for i in range(tPtLen):
			
			# Check component selection transfer list
			if tPtBool[i]: continue
			
			# Check distance to current point
			dist = (pt-tPtArray[i]).length()
			if dist < cDist:
				cDist = dist
				cIndex = i
				# Test threshold
				if dist < threshold: break
		
		# Append selection
		tSel.append(targetMesh+'.vtx['+str(cIndex)+']')
		
		# Update component selection transfer list
		tPtBool[i] = True
	
	# Return result
	return tSel
