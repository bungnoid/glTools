import maya.cmds as mc
import glTools.utils.geometry

def replaceGeometryFromUI():
	'''
	Execute replaceGeometry from the UI
	'''
	# Get selection
	sel = mc.ls(sl=True)
	if len(sel) != 2:
		print('Incorrect selection! First select the replacement geometry and then the geometry to be replaced!!')
		return
	
	# Replace geometry
	glTools.utils.geometry.replace(sel[0],sel[1])
