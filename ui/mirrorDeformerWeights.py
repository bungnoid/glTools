import maya.cmds as mc

import glTools.tools.mirrorDeformerWeights

def ui():
	'''
	'''
	# 
	win = 'mirrorDeformerWeightsUI'
	if mc.window(win,q=True,ex=True):
		mc.deleteUI(win)
	win = mc.window(win,l=win)
	
	FL = mc.formLayout()
