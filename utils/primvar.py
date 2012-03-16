import maya.cmds as mc

import glTools.utils.mesh 

def addRmanPrimVar(mesh,attrName,attrType='float',paintable=False):
	'''
	'''
	# Prefix attr
	attr = 'rmanF'+attrName
	
	# Data type
	if attrType == 'float': dataType = 'doubleArray'
	if attrType == 'vector': dataType = 'vectorArray'
	if attrType == 'string': dataType = 'stringArray'
	
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!!')
	
	# Check attr
	if mc.objExists(mesh+'.'+attr):
		raise Exception('Attribute "'+mesh+'.'+attr+'" already exists!!')
	
	# Get shape
	meshShape = mc.listRelatives(mesh,s=True,ni=True,pa=True)
	if not meshShape:
		raise Exception('Unable to determine shape for mesh "'+mesh+'"!!')
	
	# Add attribute
	mc.addAttr(meshShape[0],ln=attr,dt=dataType)
	
	# Make paintable
	if paintable: mc.makePaintable('mesh',attr,attrType=dataType)
