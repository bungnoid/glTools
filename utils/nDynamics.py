import maya.cmds as mc
import maya.mel as mm

import glTools.utils.attribute
import glTools.utils.base
import glTools.utils.mesh
import glTools.utils.stringUtils

import os.path

# ----------
# - Checks -
# ----------

def isNDynamicsNode(nNode):
	'''
	Check if the specified object is a valid nDynamics node
	@param node: Node to query
	@type node: str
	'''
	# Check object exists
	if not mc.objExists(nNode): return False
	# Check shape
	if mc.objectType(nNode) == 'transform': nNode = mc.listRelatives(nNode,s=True,ni=True,pa=True)[0]
	
	# Check nucleus
	if mc.objectType(nNode) == 'nucleus': return True
	# Check nCloth
	if mc.objectType(nNode) == 'nCloth': return True
	# Check nRigid
	if mc.objectType(nNode) == 'nRigid': return True
	# Check nParticle
	if mc.objectType(nNode) == 'nParticle': return True
	# Check nComponent
	if mc.objectType(nNode) == 'nComponent': return True
	# Check dynamicConstraint
	if mc.objectType(nNode) == 'dynamicConstraint': return True
	
	# Return result
	return False

def isNType(nNode,nType):
	'''
	Check if the specified object is a nucleus compatible nDynamics node
	@param nNode: Object or node to query
	@type nNode: str
	@param nType: Nucleus compatible node type to check for
	@type nType: str
	'''
	# Check object exists
	if not mc.objExists(nNode): return False
	# Check shape
	if mc.objectType(nNode) == 'transform': nNode = mc.listRelatives(nNode,s=True,ni=True,pa=True)[0]
	if mc.objectType(nNode) != nType: return False
	
	# Return result
	return True
	
def isNucleus(nucleus):
	'''
	Check if the specified object is a nucleus node
	@param nucleus: Object to query
	@type nucleus: str
	'''
	return isNType(nucleus,'nucleus')

def isNCloth(nCloth):
	'''
	Check if the specified object is an nCloth node
	@param nCloth: Object to query
	@type nCloth: str
	'''
	return isNType(nCloth,'nCloth')

def isNRigid(nRigid):
	'''
	Check if the specified object is an nRigid node
	@param nRigid: Object to query
	@type nRigid: str
	'''
	return isNType(nRigid,'nRigid')

def isNParticle(nParticle):
	'''
	Check if the specified object is an nParticle node
	@param nParticle: Object to query
	@type nParticle: str
	'''
	return isNType(nParticle,'nParticle')

def isNComponent(nComponent):
	'''
	Check if the specified object is an nComponent node
	@param nComponent: Object to query
	@type nComponent: str
	'''
	return isNType(nComponent,'nComponent')

def isNConstraint(nConstraint):
	'''
	Check if the specified object is an nConstraint node
	@param nConstraint: Object to query
	@type nConstraint: str
	'''
	return isNType(nConstraint,'dynamicConstraint')

def getConnectedNucleus(object):
	'''
	Get the nucleus node connected to the specified nDynamics object
	@param name: Name for nucleus node
	@type name: str
	'''
	# Check nNode
	if mc.objectType(object) == 'transform':
		object = mc.listRelatives(object,s=True,ni=True,pa=True)[0]
	if not isNDynamicsNode(object):
		nNode = getConnectedNNode(object)
		if not nNode: raise Exception('No valid nDynamics node connected to "'+object+'"!')
		nNode = nNode[0]
	else:
		nNode = object
	
	# Check nucleus connections
	nucleusConn = mc.listConnections(nNode,type='nucleus')
	
	# Return result
	if nucleusConn: return nucleusConn[0]
	else: return ''

def getConnectedNNode(object,nType=''):
	'''
	@param object: Object to find connected nNode for
	@type object: str
	@param nType: nDynamics node to check for. If empty, search for any valid nDynamics node
	@type nType: str
	'''
	# Check object exists
	if not mc.objExists(object): raise Exception('Object "'+object+'" does not exist!')
	
	# Check nNode
	nNode = object
	if mc.objectType(object) == 'transform':
		nNodeShape = mc.listRelatives(object,s=True,ni=True,pa=True)
		if nNodeShape: nNode = nNodeShape[0]
	if isNDynamicsNode(nNode):
		if not nType or nType == mc.objectType(nNode):
			return [nNode]
		
	# Check nCloth
	if not nType or nType == 'nCloth':
		nNodeConn = mc.listConnections(nNode,type='nCloth',shapes=True)
		if nNodeConn: return list(set(nNodeConn))
	
	# Check nRigid
	if not nType or nType == 'nRigid':
		nNodeConn = mc.listConnections(nNode,type='nRigid',shapes=True)
		if nNodeConn: return list(set(nNodeConn))
	
	# Check nParticle
	if not nType or nType == 'nParticle':
		nNodeConn = mc.listConnections(nNode,type='nParticle',shapes=True)
		if nNodeConn: return list(set(nNodeConn))
	
	# No nNode found, return empty result
	return []

def getConnectedNCloth(object):
	'''
	Return the nCloth node connected to the specified object
	@param object: Object to find connected nNode for
	@type object: str
	'''
	return getConnectedNNode(object,'nCloth') 

def getConnectedNRigid(object):
	'''
	Return the nRigid node connected to the specified object
	@param object: Object to find connected nNode for
	@type object: str
	'''
	return getConnectedNNode(object,'nRigid')

def getConnectedNParticle(object):
	'''
	Return the nParticle node connected to the specified object
	@param object: Object to find connected nNode for
	@type object: str
	'''
	return getConnectedNNode(object,'nParticle')

def getConnectedMesh(nNode,returnShape=False):
	'''
	Find the mesh shape or transform nodes connected to the specified nDynamics node
	@param nNode: The nDynamics node to find the connected meshes for
	@type nNode: str
	@param returnShape: Return the mesh shape instead of the mesh transform
	@type returnShape: bool
	'''
	# Check nNode node
	if not isNDynamicsNode(nNode):
		nNode = getConnectedNNode(nNode)
	
	# Check outgoing connections
	meshConn = mc.listConnections(nNode,s=False,d=True,sh=returnShape,type='mesh')
	if meshConn: return meshConn[0]
	
	# Check incoming connections
	meshConn = mc.listConnections(nNode,s=True,d=False,sh=returnShape,type='mesh')
	if meshConn: return meshConn[0]
	
	# No mesh connections found, return empty result
	return ''

# --------------------------
# - Get/Set Active Nucleus -
# --------------------------

def getActiveNucleus():
	'''
	Query the active nucleus node
	'''
	# Query active nucleus
	nucleus = mm.eval('getActiveNucleusNode(true,false)')
	# Return result
	return nucleus

def setActiveNucleus(nucleus):
	'''
	Set the active nucleus node
	@param nucleus: Nucleus node to set as current active nucleus
	@type nucleus: str
	'''
	# Check nucleus
	if not isNucleus(nucleus):
		raise Exception('Object "'+nucleus+'" is not a valid nucleus node!')
	
	# Set active nucleus
	mm.eval('source getActiveNucleusNode')
	mm.eval('setActiveNucleusNode("'+nucleus+'")')

# ----------------
# - Create Nodes -
# ----------------

def createNucleus(name='',setActive=True):
	'''
	Create nucleus node and make necessary connections
	@param name: Name for nucleus node
	@type name: str
	@param setActive: Set the created nucleus as the current active nucleus
	@type setActive: str
	'''
	# Check nucleus name
	if not name: name = 'nucleus#'
	
	# Create nucleus node
	nucleus = mc.createNode('nucleus',n=name)
	mc.connectAttr('time1.outTime',nucleus+'.currentTime')
	
	# Set active nucleus
	if setActive: setActiveNucleus(nucleus)
	
	# Return result
	return nucleus

def createNCloth(mesh,nucleus='',worldSpace=False,prefix=''):
	'''
	Create an nCloth object from the specified mesh.
	@param mesh: Mesh to create nCloth from
	@type mesh: str
	@param nucleus: nucleus to attach nCloth to
	@type nucleus: str
	@param worldSpace: nCloth deformations in local or world space
	@type worldSpace: str
	@param prefix: Name prefix for created nodes
	@type prefix: str
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check prefix
	if not prefix:
		if mesh.count('_'): prefix = glTools.utils.stringUtils.stripSuffix(mesh)
		else: prefix = mesh
	
	# Check nucleus
	if nucleus:
		if not isNucleus(nucleus):
			print('Object "'+nucleus+'" is not a valid nucleus. Using current active nucleus!')
			getActiveNucleus(nucleus)
		
		# Set active nucleus
		setActiveNucleus(nucleus)
	
	# Create nCloth from mesh
	mc.select(mesh)
	nClothShape = mm.eval('createNCloth '+str(int(worldSpace)))
	nCloth = mc.listRelatives(nClothShape,p=True)[0]
	
	# Rename nCloth
	nCloth = mc.rename(nCloth,prefix+'_nCloth')
	nClothShape = mc.listRelatives(nCloth,s=True)[0]
	
	# Get outMesh
	outMesh = mc.listConnections(nClothShape+'.outputMesh',s=False,d=True,sh=True)[0]
	outMesh = mc.rename(outMesh,mesh+'ClothShape')
	
	# return result
	return nCloth
	

def createNRigid(mesh,nucleus='',prefix=''):
	'''
	Create an nRigid object from the specified mesh.
	@param mesh: Mesh to create nRigid from
	@type mesh: str
	@param nucleus: nucleus to attach nRigid to
	@type nucleus: str
	@param prefix: Name prefix for created nodes
	@type prefix: str
	'''
	# Check mesh
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check prefix
	if not prefix:
		if mesh.count('_'): prefix = glTools.utils.stringUtils.stripSuffix(mesh)
		else: prefix = mesh
		
	# Check nucleus
	if nucleus:
		if not isNucleus(nucleus):
			print('Object "'+nucleus+'" is not a valid nucleus. Using current active nucleus!')
			getActiveNucleus(nucleus)
		
		# Set active nucleus
		setActiveNucleus(nucleus)
	
	# Create nRigid from mesh
	mc.select(mesh)
	nRigidShape = mm.eval('makeCollideNCloth')
	nRigid = mc.listRelatives(nRigidShape,p=True,pa=True)[0]
	
	# Rename nCloth
	nRigid = mc.rename(nRigid,prefix+'_nRigid')
	
	# Return result
	return nRigid

def createNParticle(ptList=[],nucleus='',prefix=''):
	'''
	Create an nParticle object.
	@param ptList: Mesh to create nCloth from
	@type ptList: str
	@param nucleus: nucleus to attach nCloth to
	@type nucleus: str
	@param prefix: Name prefix for created nodes
	@type prefix: str
	'''
	# Check prefix
	if prefix: nParticle = prefix+'_nParticle'
	else: nParticle = 'nParticle#'
	
	# Check nucleus
	if nucleus:
		if not isNucleus(nucleus):
			print('Object "'+nucleus+'" is not a valid nucleus. Using current active nucleus!')
			getActiveNucleus(nucleus)
		
		# Set active nucleus
		setActiveNucleus(nucleus)
	
	# Create nParticles
	nParticle = mc.nParticle(p=ptList,n=nParticle)

def softBody(geometry,nucleus='',prefix=''):
	'''
	Create an nParticle softBody from the specified geoemtry
	@param geometry: Mesh to create nRigid from
	@type geometry: str
	@param nucleus: nucleus to attach nRigid to
	@type nucleus: str
	@param prefix: Name prefix for created nodes
	@type prefix: str
	'''
	# Check prefix
	if not prefix: prefix = geometry
	
	# Check geometry
	geometryType = mc.objectType(geometry)
	if geometryType == 'transform':
		geometryTransform = geometry
		geometryShapes = glTools.utils.shape.getShapes(geometry,nonIntermediates=True,intermediates=False)
		if not geometryShapes: raise Exception('No valid geometry shapes found!')
		geometryShape = geometryShapes[0]
	else:
		geometryTransform = mc.listRelatives(geometry,p=True)[0]
		geometryShape = geometry
	
	# Check geometry type
	geometryType = mc.objectType(geometryShape)
	if geometryType == 'mesh': geometryAttribute = 'inMesh'
	elif geometryType == 'nurbsCurve': geometryAttribute = 'create'
	elif geometryType == 'nurbsSurface': geometryAttribute = 'create'
	else: raise Exception('Invalid geometry type ('+geometryType+')!')
	
	# Get geometry points
	mPtList = glTools.utils.base.getMPointArray(geometry)
	ptList = [(i[0],i[1],i[2]) for i in mPtList]
	
	# Create nParticles
	nParticle = mc.nParticle(p=ptList,n=prefix+'_nParticle')
	
	# Connect to geometry
	mc.connectAttr(geometryTransform+'.worldMatrix[0]',nParticle+'.targetGeometryWorldMatrix',f=True)
	mc.connectAttr(nParticle+'.targetGeometry',geometryShape+'.'+geometryAttribute,f=True)
	
	# Return result
	return nParticle

# -----------------
# - Connect Nodes -
# -----------------

def connectToNucleus(object,nucleus):
	'''
	Connect the specified nDynamics node to an existing nucleus node
	@param object: nDynamics node to connect to the nucleus solver
	@type object: str
	@param nucleus: nucleus solver to connect to
	@type nucleus: str
	'''
	# Check nucleus
	if not isNucleus(nucleus):
		preNucleusList = mc.ls(type='nucleus')
	
	# Check nDynamics node
	if isNDynamicsNode(object):
		nNode = object
	else:
		nNode = getConnectedNNode(nNode)
		if not nNode: raise Exception('Object "'+object+'" is not a valid nDynamics node, or connected to a valid nDynamics node!')
		nNode = nNode[0]
	
	# Check nRigid
	if isNRigid(nNode): connectNRigidToNucleus(nNode,nucleus,True)
	
	# Assign nNode to nucleus solver
	mc.select(nNode)
	mm.eval('assignNSolver '+nucleus)
	
	# Rename new nucleus node
	if not mc.objExists(nucleus):
		postNucleusList = mc.ls(type='nucleus')
		newNucleus = list(set(postNucleusList) - set(preNucleusList))
		if not newNucleus: raise Exception('Unable to determine new nucleus node attached to "'+object+'"!')
		nucleus = mc.rename(newNucleus[0],nucleus)
	
	# Return result
	mc.select(nucleus)
	return nucleus

def connectNRigidToNucleus(nRigid,nucleus,createNucleus=True):
	'''
	Connect the named nRigid (passive collision mesh) to the specified nucleus node
	while maintaining existing connections to other nucleus nodes.
	@param nRigid: nRigid node to attach
	@type nRigid: str
	@param nucleus: nucleus node to attach to
	@type nucleus: str
	@param createNucleus: Create a new nucleus node if the specified node doesn't exist
	@type createNucleus: str
	'''
	# Check nRigid node
	if not isNRigid(nRigid):
		nRigid = getConnectedNRigid(nRigid)
		if not nRigid: raise Exception('Object "'+nRigid+'" is not a valid nRigid node!')
		nRigid = nRigid[0]
	
	# Check nucleus
	if not isNucleus(nucleus):
		if createNucleus: nucleus = createNucleus(nucleus)
		else: raise Exception('Object "'+nucleus+'" is not a valid nucleus node!')
	
	# Get next available index
	nIndex = glTools.utils.attribute.nextAvailableMultiIndex(nucleus+'.inputPassive',0)
	
	# Connect to nucleus
	mc.connectAttr(nRigid+'.currentState',nucleus+'.inputPassive['+str(nIndex)+']')
	mc.connectAttr(nRigid+'.startState',nucleus+'.inputPassiveStart['+str(nIndex)+']')
	
	# Return result
	return nIndex

# ----------------
# - Delete Nodes -
# ----------------

def deleteUnusedNucleusNodes():
	'''
	Delete all nucleus nodes that have no valid outgoing connections
	'''
	# Get existsing nucleus nodes
	nucleusList = mc.ls(type=nucleus)
	
	# Initialize return list
	nucleusDel = []
	
	# Iterate over nodes
	for nucleus in nucleusList:
		
		# Check outgoing connections
		nConn = mc.listConnections(nucleus,s=False,d=True)
		if not nConn: nucleusDel.append(nucleus)
	
	# Delete unused nucleus nodes
	mc.delete(nucleusDel)
	
	# Return result
	return nucleusDel

def deleteNCloth(nCloth):
	'''
	Delete nCloth nodes and connections form a specified nCloth or nRigid mesh
	@param nCloth: nCloth or nRigid mesh to delete nDynamics nodes and connections from
	@type nCloth: str
	'''
	# Checks nCloth
	connNCloth = getConnectedNCloth(nCloth)
	if not connNCloth: raise Exception('Object "'+nCloth+'" is not a valid nCloth object!')
	nCloth = connNCloth[0]
	
	# Get connected mesh 
	nClothMesh = getConnectedMesh(nCloth)
	mc.select(nClothMesh)
	
	# Remove nCloth
	mm.eval('nClothRemove')

# -----------
# - Weights -
# -----------

def getVertexWeights(nCloth,attr):
	'''
	Return the nCloth attribute weight array for the specified nCloth object.
	@param nCloth: nCloth oobject to get attribute weights for
	@type nCloth: str
	@param attr: nCloth attributes to get weights for
	@type attr: str
	'''
	# Checks nCloth
	connNCloth = getConnectedNCloth(nCloth)
	if not connNCloth: raise Exception('Object "'+nCloth+'" is not a valid nCloth object!')
	nCloth = connNCloth[0]
		
	# Get vertex weights
	wt = mc.getAttr(nCloth+'.'+attr+'PerVertex')
	
	# Return Result
	return wt

def setVertexWeights(nCloth,attr,wt):
	'''
	Set the specified nCloth attribute weight array using the input array values.
	@param nCloth: nCloth object to set attribute weights for
	@type nCloth: str
	@param attr: nCloth attributes to set weights for
	@type attr: str
	@param wt: Weight array values to set
	@type wt: str
	'''
	# Checks nCloth
	connNCloth = getConnectedNCloth(nCloth)
	if not connNCloth: raise Exception('Object "'+nCloth+'" is not a valid nCloth object!')
	nCloth = connNCloth[0]
	
	# Set vertex weights
	mc.setAttr(nCloth+'.'+attr+'PerVertex',wt,type='doubleArray')

def loadWeightMap(nCloth,attr,filePath,loadAsVertexMap=False):
	'''
	Load nCloth attribute weight map from file.
	Optionally, load the weight values to a vertex map as opposed to a texture map
	@param nCloth: nCloth object to load attribute weights for.
	@type nCloth: str
	@param attr: nCloth attributes to load weights for
	@type attr: str
	@param filePath: File path to the attribute weight map.
	@type filePath: str
	@param loadAsVertexMap: Load the attribute weight values to a vertex map instead of a texture map.
	@type loadAsVertexMap: bool
	'''
	# Checks nCloth
	connNCloth = getConnectedNCloth(nCloth)
	if not connNCloth: raise Exception('Object "'+nCloth+'" is not a valid nCloth object!')
	nCloth = connNCloth[0]
	
	# Check file path
	if not os.path.isfile(filePath):
		raise Exception('Weight map file path "'+filePath+'" does not exist!')
	
	# Create file node
	fileName = os.path.basename(filePath)
	fileName = fileName.replace('.'+fileName.split('.')[-1],'')
	fileNode = mc.shadingNode('file',asTexture=True,n=fileName)
	mc.setAttr(fileNode+'.fileTextureName',filePath,type='string')
	
	# Connect to nCloth
	mc.connectAttr(fileNode+'.outAlpha',nCloth+'.'+attr+'Map',f=True)
	mc.setAttr(nCloth+'.'+attr+'MapType',2) # Texture Map
	
	# Convert to vertex map
	if loadAsVertexMap:
		mc.nBase(nCloth,e=True,textureToVertex=attr+'Map')
		mc.setAttr(nCloth+'.'+attr+'MapType',1) # Per-vertex
		mc.delete(fileNode)

