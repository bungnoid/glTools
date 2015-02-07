import maya.cmds as mc

import glTools.tools.match

def mirror(rootList=[],locList=[],leftToRight=True):
	'''
	Mirror rig template components
	@param rootList: List of template root joints to mirror. 
	@type rootList: list
	@param locList: List of template locators to mirror.
	@type locList: list
	@param leftToRight: Mirror from left to right if True. Mirror from right to left if False.
	@type leftToRight: bool
	'''
	# ==============
	# - Check Side -
	# ==============
	
	src = 'lf_'
	dst = 'rt_'
	if not leftToRight:
		src = 'rt_'
		dst = 'lf_'
	
	# ========================================
	# - Removed Existing Desitination Joints -
	# ========================================
	
	for root in rootList:
		if root.startswith(dst):
			mc.delete(root)
	
	# ======================
	# - Mirror Root Joints -
	# ======================
	
	# Mirror Joints
	for root in rootList:
		
		# Check Side
		if root.startswith(src):
		
			# Mirror Joint
			mirrorJoint = mc.mirrorJoint(root,mirrorYZ=True,mirrorBehavior=True,searchReplace=[src,dst])
			
			# Colour Hierarchy
			glTools.utils.colorize.colourHierarchy(root)
			glTools.utils.colorize.colourHierarchy(mirrorJoint[0])
	
	# ===================
	# - Mirror Locators -
	# ===================
	
	# Mirror Locator using Match()
	for loc in locList:
		
		# Check Side
		if loc.startswith(src):
			
			# Mirror Locator
			glTools.tools.match.Match().twin(loc)
