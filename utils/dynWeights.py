import maya.cmds as mc

import glTools.utils.mesh
import glTools.utils.shape

def addPaintAttr(mesh,attr,attrType='doubleArray'):
	'''
	Add a paintable array attribute to the specified mesh geometry.
	@param mesh: Mesh to add paintable attr to
	@type mesh: str
	@param attr: Name for the new attribute
	@type attr: str
	@param attrType: Data type for the new attribute
	@type attrType: str
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!!')
	
	# Check attr
	if mc.objExists(mesh+'.'+attr):
		raise Exception('Attribute "'+mesh+'.'+attr+'" already exists!!')
		
	# Get shape
	meshShape = mc.listRelatives(mesh,s=True,ni=True,pa=True)
	if not meshShape: raise Exception('Unable to determine shape for mesh "'+mesh+'"!!')
	
	# Add attribute
	mc.addAttr(meshShape[0],ln=attr,dt=attrType)
	
	# Make paintable
	mc.makePaintable('mesh',attr,attrType=attrType)

def setPaintAttr(paintAttr,attrValue):
	'''
	Set the specified paintable attribute with the given array values
	@param paintAttr: Paintable attribute to set
	@type paintAttr: str
	@param attrValue: Array attribute values to set
	@type attrValue: list
	'''
	# Check paint attr
	if not mc.objExists(paintAttr):
		raise Exception('Attribute "'+paintAttr+'" does not exist!!')
	
	# Check multi
	paintNode = '.'.join(paintAttr.split('.')[:-1])
	paintAttr = paintAttr.split('.')[-1]
	paintMulti = mc.attributeQuery(paintAttr,node=paintNode,multi=True)
	
	# Set paint attribute value
	if paintMulti:
		
		# Set multi attribute values
		for i in range(len(attrValue)):
			mc.setAttr(paintNode+'.'+paintAttr+'['+str(i)+']',attrValue[i])
	
	else:
		
		# Set array attribute values
		mc.setAttr(paintNode+'.'+paintAttr,attrValue,type='doubleArray')

def copyPaintAttr(mesh,attr,sourceAttr,attrType='doubleArray'):
	'''
	Copy the value of one paintable attribute to another
	@param mesh: Mesh that contains the attribute to copy values to
	@type mesh: str
	@param attr: The name of the attribute to copy the values to
	@type attr: str
	@param sourceAttr: The attribute to copy values from
	@type sourceAttr: str
	@param attrType: The attribute type to set
	@type attrType: str
	'''
	# Check Mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!!')
	
	# Check Mesh Attribute
	if not mc.objExists(mesh+'.'+attr): addPaintAttr(mesh,attr,attrType)
	
	# Copy Attribute Values
	vtxCount = mc.polyEvaluate(mesh,v=True)
	attrVal = []
	for i in range(vtxCount):
		val = mc.getAttr(sourceAttr+'['+str(i)+']')
		attrVal.append(val)
	
	# Set Attribute Value
	mc.setAttr(mesh+'.'+attr,attrVal,type=attrType)

def connectVertexColour(mesh,colourData,prefix=''):
	'''
	Connect a specified doubleArray attribute to a given meshes vertex colour using the vertexColourArray node.
	@param mesh: Mesh to drive vertex colours for
	@type mesh: str
	@param colourData: DoubleArray attribute to drive the vertex colour
	@type colourData: str
	@param prefix: Name prefix for created nodes
	@type prefix: str
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!!')
	
	# Check colourData
	if not mc.objExists(colourData):
		raise Exception('Colour data attribute "'+colourData+'" does not exist!!')
	
	# Get mesh shape
	shape = glTools.utils.shape.getShapes(mesh,True,False)[0]
	
	# Check inMesh connection
	inMeshConn = mc.listConnections(shape+'.inMesh',p=True)
	if not inMeshConn:
		inputConn = glTools.utils.shape.createIntermediate(shape)+'.outMesh'
	else:
		inputConn = inMeshConn[0]
	
	# Check prefix
	if not prefix: prefix = mesh
	
	# Create vertexColourArray node
	vtxColourNode = mc.createNode('vertexColourArray',n=prefix+'_vertexColourArray')
	
	# Connect nodes
	mc.connectAttr(inputConn,vtxColourNode+'.inMesh',f=True)
	mc.connectAttr(colourData,vtxColourNode+'.inputArray',f=True)
	mc.connectAttr(vtxColourNode+'.outMesh',shape+'.inMesh',f=True)
	
	# Return result
	return vtxColourNode

def arrayToMulti(arrayAttr,prefix=''):
	'''
	Create an arrayToMulti node to convert a doubleArray value to a double multi
	that is compatible with deformer weight attribute.
	@param arrayAttr: Source array attribute to convert to a multi.
	@type arrayAttr: str
	@param prefix: Name prefix for created nodes.
	@type prefix: str
	'''
	# Check array attribute
	if not mc.objExists(arrayAttr):
		raise Exception('Array attribute "'+arrayAttr+'" does not exist!!')
	
	# Check prefix
	if not prefix: prefix = mc.ls(arrayAttr,o=True)[0]
	
	# Create node
	arrayToMultiNode = mc.createNode('arrayToMulti',n=prefix+'_arrayToMulti')
	mc.connectAttr(arrayAttr,arrayToMultiNode+'.inputArray',f=True)
	
	# Return result
	return arrayToMultiNode

def combineArray(arrayList,method,prefix):
	'''
	Create a combineArray node and connect the specified list of array attributes.
	@param arrayList: List of array attributes to combine.
	@type arrayList: list
	'''
	# Check Array List
	for array in arrayList:
		if not mc.objExists(array):
			raise Exception('Array attribute "'+array+'" does not exist!')
	
	# Check Method
	methodDict = {'sum':0,'subtract':1,'multiply':2,'divide':3,'average':4,'min':5,'max':6}
	if not methodDict.has_key(method):
		raise Exception('Invalid method - "'+method+'"!')
	methodVal = methodDict[method]
	
	# Create combineArray node and connect
	combineArrayNode = mc.createNode('combineArray',n=prefix+'_combineArray')
	mc.setAttr(combineArrayNode+'.method',methodVal)
	for i in range(len(arrayList)):
		mc.connectAttr(arrayList[i],combineArrayNode+'.inputArray['+str(i)+']',f=True)
	
	# Return Result
	return combineArrayNode+'.outputArray'

def meshDetailArray(mesh,refMesh,targetMesh='',detailType='stretch',useInMeshConnection=True,prefix=''):
	'''
	Create a meshDetailArray node connected to the specified mesh.
	@param mesh: Mesh to generate meshDetailArray from
	@type mesh: str
	@param refMesh: Reference mesh to generate meshDetailArray from
	@type refMesh: str
	@param targetMesh: Target mesh to generate meshDetailArray from
	@type targetMesh: str
	@param useInMeshConnection: Use incoming mesh connection if available
	@type useInMeshConnection: bool
	@param prefix: Name prefix for created nodes.
	@type prefix: str
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Mesh "'+mesh+'" is not a valid mesh!!')
	# Check refMesh
	if not glTools.utils.mesh.isMesh(refMesh):
		raise Exception('Reference mesh "'+refMesh+'" is not a valid mesh!!')
	
	# Check inMesh connections
	inMesh = mesh+'.outMesh'
	inMeshConn = mc.listConnections(mesh+'.inMesh',s=True,d=False,p=True)
	if inMeshConn and useInMeshConnection: inMesh = inMeshConn[0]
	
	# Check prefix
	if not prefix: prefix = mesh
	
	# Create node
	meshDetailArrayNode = mc.createNode('meshDetailArray',n=prefix+'_meshDetailArray')
	# Set Detail Attribute
	if detailType:
		
		# Define detail type mapping
		dtDict = {	'stretch':1,'compress':2,'stretch_abs':3,'stretch_raw':4,'stretch_norm':5,
					'concave':6,'convex':7,'curve_abs':8,'curve_raw':9,'curve_norm':10	}
		
		# Check detail type
		if not dtDict.has_key(detailType):
			raise Exception('Invalid detail type ("'+detailType+'")!')
		
		# Set detail type
		mc.setAttr(meshDetailArrayNode+'.detailMethod',dtDict[detailType])
	
	# Connect node attributes
	mc.connectAttr(inMesh,meshDetailArrayNode+'.inMesh',f=True)
	mc.connectAttr(refMesh+'.outMesh',meshDetailArrayNode+'.refMesh',f=True)
	if targetMesh: mc.connectAttr(targetMesh+'.outMesh',meshDetailArrayNode+'.targetMesh',f=True)
	
	# Return result
	return meshDetailArrayNode

def noiseArray(mesh,useInMeshConnection=True,prefix=''):
	'''
	Create a noiseArray node connected to the specified mesh.
	@param mesh: Mesh to generate noiseArray from
	@type mesh: str
	@param useInMeshConnection: Use incoming mesh connection if available
	@type useInMeshConnection: bool
	@param prefix: Name prefix for created nodes.
	@type prefix: str
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Mesh "'+mesh+'" is not a valid mesh!!')
	
	# Check inMesh connections
	inMesh = mesh+'.outMesh'
	inMeshConn = mc.listConnections(mesh+'.inMesh',p=True)
	if inMeshConn and useInMeshConnection: inMesh = inMeshConn[0]
	
	# Check prefix
	if not prefix: prefix = mesh
	
	# Create node
	noiseArrayNode = mc.createNode('noiseArray',n=prefix+'_noiseArray')
	# Connect node attributes
	mc.connectAttr(inMesh,noiseArrayNode+'.inMesh',f=True)
	mc.connectAttr(mesh+'.worldMatrix[0]',noiseArrayNode+'.inMatrix',f=True)
	
	# Return result
	return noiseArrayNode

def proximityArray(mesh,proximityGeo,useInMeshConnection=True,prefix=''):
	'''
	Create a proximityArray node connected to the specified mesh.
	@param mesh: Mesh to generate proximityArray from
	@type mesh: str
	@param proximityGeo: Proximity geometry to generate proximityArray from
	@type proximityGeo: str
	@param useInMeshConnection: Use incoming mesh connection if available
	@type useInMeshConnection: bool
	@param prefix: Name prefix for created nodes.
	@type prefix: str
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Mesh "'+mesh+'" is not a valid mesh!!')
	
	# Check proximityGeo
	if not mc.objExists(proximityGeo):
		raise Exception('Proximity geometry "'+proximityGeo+'" does not exist!!')
	
	# Check inMesh connections
	inMesh = mesh+'.outMesh'
	inMeshConn = mc.listConnections(mesh+'.inMesh',p=True)
	if inMeshConn and useInMeshConnection: inMesh = inMeshConn[0]
	
	# Check prefix
	if not prefix: prefix = mesh
	
	# Create node
	proximityArrayNode = mc.createNode('proximityArray',n=prefix+'_proximityArray')
	# Connect node attributes
	mc.connectAttr(inMesh,proximityArrayNode+'.inMesh',f=True)
	mc.connectAttr(mesh+'.worldMatrix[0]',proximityArrayNode+'.inMatrix',f=True)
	mc.connectAttr(proximityGeo+'.outMesh',proximityArrayNode+'.proximityGeometry',f=True)
	mc.connectAttr(proximityGeo+'.worldMatrix[0]',proximityArrayNode+'.proximityMatrix',f=True)
	
	# Return result
	return proximityArrayNode
	
def velocityArray(mesh,useInMeshConnection=True,prefix=''):
	'''
	Create a velocityArray node connected to the specified mesh.
	@param mesh: Mesh to generate velocityArray from
	@type mesh: str
	@param useInMeshConnection: Use incoming mesh connection if available
	@type useInMeshConnection: bool
	@param prefix: Name prefix for created nodes.
	@type prefix: str
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Mesh "'+mesh+'" is not a valid mesh!!')
	
	# Check inMesh connections
	inMesh = mesh+'.outMesh'
	inMeshConn = mc.listConnections(mesh+'.inMesh',p=True)
	if inMeshConn and useInMeshConnection: inMesh = inMeshConn[0]
	
	# Check prefix
	if not prefix: prefix = mesh
	
	# Create node
	velocityArrayNode = mc.createNode('velocityArray',n=prefix+'_velocityArray')
	# Connect node attributes
	mc.connectAttr(inMeshConn,velocityArrayNode+'.inMesh',f=True)
	mc.connectAttr('time1.outTime',velocityArrayNode+'.inTime',f=True)
	
	# Return result
	return velocityArrayNode

def volumeArray(mesh,volume,center='',useInMeshConnection=True,prefix=''):
	'''
	Create an volumeArray node connected to the specified mesh.
	Optionally, connect the resulting multi to a destination attribute.
	@param mesh: Mesh to generate volumeArray from
	@type mesh: str
	@param volume: Volume mesh to generate volumeArray from
	@type volume: str
	@param center: Volume center locator
	@type center: str
	@param useInMeshConnection: Use incoming mesh connection if available
	@type useInMeshConnection: bool
	@param prefix: Name prefix for created nodes.
	@type prefix: str
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Mesh "'+mesh+'" is not a valid mesh!!')
		
	# Check volume
	if not glTools.utils.mesh.isMesh(volume):
		raise Exception('Volume mesh "'+volume+'" is not a valid mesh!!')
	
	# Check inMesh connections
	inMesh = mesh+'.outMesh'
	inMeshConn = mc.listConnections(mesh+'.inMesh',p=True)
	if inMeshConn and useInMeshConnection: inMesh = inMeshConn[0]
	
	# Check prefix
	if not prefix: prefix = mesh
	
	# Create node
	volumeArrayNode = mc.createNode('volumeArray',n=prefix+'_volumeArray')
	# Connect node attributes
	mc.connectAttr(inMeshConn,volumeArrayNode+'.inMesh',f=True)
	mc.connectAttr(mesh+'.worldMatrix[0]',volumeArrayNode+'.inMatrix',f=True)
	mc.connectAttr(volume+'.outMesh',volumeArrayNode+'.volumeMesh',f=True)
	mc.connectAttr(volume+'.worldMatrix[0]',volumeArrayNode+'.volumeMatrix',f=True)
	if center: mc.connectAttr(center+'.worldPosition[0]',volumeArrayNode+'.volumeCenter',f=True)
	
	# Return result
	return volumeArrayNode

def meshDrivenAttr(mesh,refMesh,targetMesh): pass
