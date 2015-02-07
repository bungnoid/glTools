import maya.cmds as mc

import glTools.utils.mesh

class MissingPluginError(Exception): pass

def addRmanPrimVar(mesh,attrName,attrType='float',paintable=False):
	'''
	Add a prman primVar attribute to the specified mesh shape.
	@param mesh: Mesh shape to add primVar attribute to.
	@type mesh: str
	@param attrName: Base primVar attribute name. The correct primVar prefix will be added to the final attribute name.
	@type attrName: str
	@param attrType: PrimVar attribute type. Accepted values are: "float", "vector", "color" and "string"
	@type attrType: str
	@param paintable: Paintable state of the primVar attribute.
	@type paintable: bool
	'''
	# Prefix attr
	attr = ''
	
	# Data type
	if attrType == 'float':
		dataType = 'doubleArray'
		attr = 'rmanF'+attrName
	elif attrType == 'vector':
		dataType = 'vectorArray'
		attr = 'rmanV'+attrName
	elif attrType == 'string':
		dataType = 'stringArray'
		attr = 'rmanS'+attrName
	elif attrType == 'color':
		dataType = 'vectorArray'
		attr = 'rmanC'+attrName
	else:
		raise Exception('Invalid attribute type! Accepted values are: "float", "vector", "color" and "string".')
	
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

def addAbcPrimVar(geo,attrName,attrType=None,dataType='long',keyable=False,paintable=False,geoIsMesh=False):
	'''
	Add an alembic primVar attribute to the specified geometry.
	@param geo: Geometry to add primVar attribute to.
	@type geo: str
	@param attrName: Base primVar attribute name. The correct primVar prefix will be added to the final attribute name.
	@type attrName: str
	@param attrType: PrimVar attribute type. Accepted values are: <None> (per object), "var" (varying per face), "vtx" (varying per vertex), "uni" (uniform) and "fvr" (?)
	@type attrType: str
	@param dataType: The data type for the attribute. Only used when attrType=''. If empty, default to "long" (int). Alternative is "float".
	@type dataType: str
	@param keyable: Keyable state of the primVar attribute.
	@type keyable: bool
	@param paintable: Paintable state of the primVar attribute.
	@type paintable: bool
	@param geoIsMesh: Check if the specified geo node is a mesh, if not raise an exception.
	@type geoIsMesh: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Geometry
	if not mc.objExists(geo):
		raise Exception('Geometry "'+geo+'" does not exist!!')
	if geoIsMesh and not glTools.utils.mesh.isMesh(geo):
		raise Exception('Geometry "'+geo+'" is not a valid mesh!!')
	
	# Check Attribute
	attr = 'ABC_'+attrName
	if mc.objExists(geo+'.'+attr):
		# mc.deleteAttr(geo+'.'+attr)
		raise Exception('Attribute "'+geo+'.'+attr+'" already exists!!')
	
	# Check Attribute Type
	typeList = ['var','vtx','uni','fvr']
	if attrType and  not typeList.count(attrType):
		raise Exception('Invalid attribute type! Accepted values are: "var", "vtx", "uni" and "fvr" (or <None> for per object attribute).')
	
	# =================
	# - Add Attribute -
	# =================
	
	# Data type
	if not attrType:
		
		# Check Data Type
		if not dataType: dataType = 'long'
		
		# Add primVar attribute
		mc.addAttr(geo,ln=attr,at=dataType,k=keyable)
		
	else:
		
		# Set Attribute Data Type
		dataType = 'doubleArray'
		
		# Add primVar attribute
		mc.addAttr(geo,ln=attr,dt=dataType)
		
		# Set Geometey Scope Value
		attrTypeAttr = 'ABC_'+attrName+'_AbcGeomScope'
		mc.addAttr(geo,ln=attrTypeAttr,dt='string')
		mc.setAttr(geo+'.'+attrTypeAttr,attrType,type='string',l=True)
		
		# Make paintable
		if paintable: mc.makePaintable('mesh',attr,attrType=dataType)
		
	# =================
	# - Return Result -
	# =================
	
	return geo+'.'+attr

def addAbcPrimVarStr(geo,attrName,stringVal='',lock=False):
	'''
	Add an alembic primVar string attribute to the specified geometry.
	@param geo: Geometry to add primVar attribute to.
	@type geo: str
	@param attrName: Base primVar attribute name. The correct primVar prefix will be added to the final attribute name.
	@type attrName: str
	@param stringVal: Default string value for primvar attribute.
	@type stringVal: str
	@param lock: Lock the attribute
	@type lock: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Geometry
	if not mc.objExists(geo):
		raise Exception('Geometry "'+geo+'" does not exist!!')
		
	# Check Attribute
	attr = 'ABC_'+attrName
	if mc.objExists(geo+'.'+attr):
		# mc.deleteAttr(geo+'.'+attr)
		raise Exception('Attribute "'+geo+'.'+attr+'" already exists!!')
	
	# =================
	# - Add Attribute -
	# =================
	
	# Add primVar attribute
	mc.addAttr(geo,ln=attr,dt='string')
	
	# Set String Value
	if stringVal: mc.setAttr(geo+'.'+attr,stringVal,type='string')
	
	# Lock Attr
	if lock: mc.setAttr(geo+'.'+attr,l=True)
		
	# =================
	# - Return Result -
	# =================
	
	return geo+'.'+attr

def addStepSeedAttr(geo,attrNode='',prefix=''):
	'''
	Add the stepSeed alembic primVar attribute to the specified geometry (mesh).
	@param geo: Geometry to add primVar attribute to.
	@type geo: str
	@param attrNode: The node to create the stepSeed attribute on. If empty, use geo node.
	@type attrNode: str
	@param prefix: Node naming prefix
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Plugin
	if not mc.pluginInfo('meshRandomSeed.py',q=True,l=True):
		try: mc.loadPlugin('meshRandomSeed.py')
		except: raise MissingPluginError('Unable to load "meshRandomSeed" plugin!!')
	
	# Check Prefix
	if not prefix: prefix = geo
	
	# Check Geometry
	if not mc.objExists(geo):
		raise Exception('Geometry "'+geo+'" does not exist!!')
	if not glTools.utils.mesh.isMesh(geo):
		raise Exception('Geometry "'+geo+'" is not a valid mesh!!')
	
	# Check Attribute Node
	if not attrNode: attrNode = geo
	
	# Check Attribute
	attrType = None
	attrName = 'stepSeed'
	attr = 'ABC_'+attrName
	if mc.objExists(attrNode+'.'+attr):
		raise Exception('Attribute "'+attrNode+'.'+attr+'" already exists!!')
	
	# =================
	# - Add Attribute -
	# =================
	
	attr = addAbcPrimVar(attrNode,attrName,attrType,keyable=True)
	
	# ===================
	# - Connect To Mesh -
	# ===================
	
	# Get Geometry Shape
	geoShape = mc.listRelatives(geo,s=True,ni=True,pa=True)
	if not geoShape:
		raise Exception('Unable to determine geometry shape from transform "'+geo+'"!')
	
	# Connect to meshRandomSeed Node
	meshRandomSeed = mc.createNode('meshRandomSeed',n=prefix+'_meshRandomSeed')
	mc.connectAttr(geoShape[0]+'.outMesh',meshRandomSeed+'.inputMesh',f=True)
	
	# =========================
	# - Connect StepSeed Attr -
	# =========================
	
	mc.connectAttr(meshRandomSeed+'.outputSeed',attr,f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return attr

