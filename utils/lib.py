import maya.cmds as mc
import maya.OpenMaya as OpenMaya

def axis_list():
	'''
	Return a list of axis tuples
	'''
	return [(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)]

def axis_dict(neg=True):
	'''
	'''
	if neg:
		return {'x':[1,0,0],'y':[0,1,0],'z':[0,0,1],'-x':[-1,0,0],'-y':[0,-1,0],'-z':[0,0,-1]}
	else:
		return {'x':[1,0,0],'y':[0,1,0],'z':[0,0,1]}

def rotateOrder_list():
	'''
	'''
	return ['xyz','yzx','zxy','xzy','yxz','zyx']

def rotateOrder_dict():
	'''
	'''
	return {'xyz':0,'yzx':1,'zxy':2,'xzy':3,'yxz':4,'zyx':5}

def xform_list(translate=True,rotate=True,scale=True):
	'''
	'''
	xform = []
	if translate: xform += ['tx','ty','tz']
	if rotate: xform += ['rx','ry','rz']
	if scale: xform += ['sx','sy','sz']
	return xform
