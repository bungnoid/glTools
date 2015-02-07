import maya.cmds as mc

import glTools.utils.base
import glTools.utils.joint
import glTools.utils.stringUtils

def buildChain(ptList,orient=None,secondaryAxisAim='yup'):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if orient:
		orientList = ['xyz', 'yzx', 'zxy', 'zyx', 'yxz', 'xzy']
		aimAxisList = ['xup', 'xdown', 'yup', 'ydown', 'zup', 'zdown']
		if not orientList.count(orient):
			raise Exception('Invalid joint orient order ('+orient+')!')
		if not aimAxisList.count(secondaryAxisAim):
			raise Exception('Invalid secondary aim orient ('+secondaryAxisAim+')!')
	
	# =====================
	# - Build Joint Chain -
	# =====================
	
	# Clear Selection
	mc.select(cl=True)
	
	# Build Each Joint from Point List
	jointList = []
	for pt in ptList:
		
		# Get Point Position
		pos = glTools.utils.base.getPosition(pt)
		
		# Create Joint
		joint = mc.joint(p=pos)
		
		# Check Orient
		if jointList and orient:
			
			# Orient Joint
			mc.joint(jointList[-1],oj=orient,sao=secondaryAxisAim)
		
		# Append Joint List
		jointList.append(joint)
	
	# Orient End Joint
	if jointList and orient: mc.setAttr(jointList[-1]+'.jo',0,0,0)
	
	# =================
	# - Return Result -
	# =================
	
	return jointList
