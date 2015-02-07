import maya.cmds as mc

import glTools.utils.mesh

import glTools.rig.utils

def checkNonReferenceInputShapes(root,verbose=False):
	'''
	Check nonReference input shapes for all geometry under the given root node.
	@param root: Root node to check referenced input shape under.
	@type root: str
	@param verbose: Print progress messages.
	@type verbose: bool
	'''
	# Check Root Exists
	if not mc.objExists(root):
		raise Exception('Root node "'+root+'" does not exist!')
	
	# Get Transform Descendants (Geometry Only)
	xforms = mc.ls(mc.listRelatives(root,ad=True),transforms=True)
	geoList = [geo for geo in xforms if mc.listRelatives(geo,s=True)]
	
	# Check Non Referenced Input Shapes
	nonRefInputs = []
	hasNonRefInput = False
	for geo in geoList:
		try:
			hasNonRefInput = glTools.rig.utils.checkNonReferencedInputShape(geo)
		except Exception, e:
			print str(e)
		else:
			if hasNonRefInput:
				nonRefInputs.append(geo)
	
	# Print Result
	if verbose:
		if nonRefInputs:
			print('======================================')
			print('Found '+str(len(nonRefInputs))+' nonReference input geometries!')
			print('======================================')
			for geo in nonRefInputs: print geo
			print('======================================\n')
		else:
			print('==========================================')
			print('No nonReference input geometries found...')
			print('==========================================\n')
	
	# Return Result
	return nonRefInputs

def fixNonReferenceInputShapes(root,verbose=False):
	'''
	Fix nonReference input shapes for all geometry under the given root node.
	@param root: Root node to fix referenced input shape under.
	@type root: str
	@param verbose: Print progress messages.
	@type verbose: bool
	'''
	# Check Root
	if not mc.objExists(root):
		raise Exception('Root node "'+root+'" does not exist!')
	
	# Get Non Reference Input Geometry
	nonRefInputs = checkNonReferenceInputShapes(root,verbose=verbose)
	
	# Fix Non Referenced Input Shapes
	for geo in nonRefInputs:
		if verbose:	print('# ==== Fixing nonReference input shape for geometry "'+geo+'"!')
		try: glTools.rig.utils.fixNonReferencedInputShape(geo)
		except Exception, e: print(e)
	if verbose:
		print('======================================')
		print('Fixed '+str(len(nonRefInputs))+' nonReference input geometries!')
		print('======================================')
