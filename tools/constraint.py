import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.component
import glTools.utils.constraint
import glTools.utils.mathUtils
import glTools.utils.mesh
import glTools.utils.reference
import glTools.utils.stringUtils
import glTools.utils.transform

import types

def bake(	constraint,	
			start		= None,
			end			= None,
			sampleBy	= 1,
			simulation	= True	):
	'''
	Bake specified constraint
	@param constraint: Constraint to bake animation for.
	@type constraint: str
	@param start: Start frame of bake animation range
	@type start: float or None
	@param end: End frame of bake animation range
	@type end: float or None
	@param sampleBy: Sample every Nth frame
	@type sampleBy: int
	@param simulation: Simulation option for bakeResults
	@type simulation: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Constraint
	if not glTools.utils.constraint.isConstraint(constraint):
		raise Exception('Object "'+constraint+'" is not a valid constraint node!')
	
	# Check Start/End Frames
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	# ====================================
	# - Get Slave Transform and Channels -
	# ====================================
	
	# Get Slave Transform
	slave = glTools.utils.constraint.slave(constraint)
	
	# Get Slave Channels
	attrList = mc.listConnections(constraint,s=False,d=True,p=True) or []
	slaveAttrs = [i.split('.')[-1] for i in attrList if i.startswith(slave+'.')] or []
	if not slaveAttrs: raise Exception('No slave channels to bake!')
	
	# ===================
	# - Bake Constraint -
	# ===================
	
	mc.refresh(suspend=True)
	mc.bakeResults(	slave,
					at = slaveAttrs,
					time = (start,end),
					disableImplicitControl = True,
					simulation = simulation,
					sampleBy = sampleBy )
	mc.refresh(suspend=False)
	
	# =================
	# - Return Result -
	# =================
	
	return [slave+'.'+i for i in slaveAttrs]

def aimConstraint(	target,
					slave,
					aim='z',
					up='y',
					worldUpType='scene',
					worldUpObject=None,
					worldUpVector='y',
					offset=(0,0,0),
					mo=False	):
	'''
	Create an aim constraint between the specifiec master and slave transforms.
	Only constrains open, settable channels.
	@param master: Constraint master transform.
	@type master: str
	@param slave: Constraint slave transform.
	@type slave: str
	@param aim: Aim axis.
	@type aim: str
	@param aim: Up axis.
	@type aim: str
	@param worldUpType: World Up type. Options - "scene", "object", "objectrotation", "vector", or "none".
	@type worldUpType: str
	@param worldUpObject: World Up object.
	@type worldUpObject: str
	@param worldUpVector: World Up vector.
	@type worldUpVector: str
	@param mo: Maintain constraint offset
	@type mo: bool
	'''
	# Build Axis Dict
	axis = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	# ==========
	# - Checks -
	# ==========
	
	# Check Master
	if not mc.objExists(target):
		raise Exception('Constraint target "'+target+'" does not exist!')
	if not glTools.utils.transform.isTransform(target):
		raise Exception('Constraint target "'+target+'" is not a valid transform!')
	
	# Check Slave
	if not mc.objExists(slave):
		raise Exception('Constraint slave "'+slave+'" does not exist!')
	if not glTools.utils.transform.isTransform(slave):
		raise Exception('Constraint slave "'+slave+'" is not a valid transform!')
	
	# Check Settable Channels
	sk = []
	if not mc.getAttr(slave+'.rx',se=True): sk.append('x')
	if not mc.getAttr(slave+'.ry',se=True): sk.append('y')
	if not mc.getAttr(slave+'.rz',se=True): sk.append('z')
	if not sk: sk = 'none'
	
	# =====================
	# - Create Constraint -
	# =====================
	
	constraint = ''
	try:
		if worldUpObject:
			constraint = mc.aimConstraint(	target,
											slave,
											aim=axis[aim],
											u=axis[aim],
											worldUpType=worldUpType,
											worldUpObject=worldUpObject,
											worldUpVector=axis[worldUpVector],
											sk=sk,
											offset=offset,
											mo=mo)[0]
		else:
			constraint = mc.aimConstraint(	target,
											slave,
											aim=axis[aim],
											u=axis[aim],
											worldUpType=worldUpType,
											worldUpVector=axis[worldUpVector],
											sk=sk,
											offset=offset,
											mo=mo)[0]
	except Exception, e:
		raise Exception('Error creating constraint from "'+target+'" to "'+slave+'"! Exception msg: '+str(e))
	
	# =================
	# - Return Result -
	# =================
	
	return constraint

def pointConstraint(master,slave,mo=False,attrList=['tx','ty','tz']):
	'''
	Create a point constraint between the specifiec master and slave transforms.
	Only constrains open, settable channels.
	@param master: Constraint master transform.
	@type master: str
	@param slave: Constraint slave transform.
	@type slave: str
	@param mo: Maintain constraint offset
	@type mo: bool
	@param attrList: List of transform attributes to constrain.
	@type attrList: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target (Master)
	if isinstance(master,types.StringTypes):
		if not mc.objExists(master):
			raise Exception('Constraint target "'+master+'" does not exist!')
		if not glTools.utils.transform.isTransform(master):
			raise Exception('Constraint target "'+master+'" is not a valid transform!')
	elif isinstance(master,types.ListType):
		for target in master:
			if not mc.objExists(target):
				raise Exception('Constraint target "'+target+'" does not exist!')
			if not glTools.utils.transform.isTransform(target):
				raise Exception('Constraint target "'+target+'" is not a valid transform!')
	
	# Check Slave
	if not mc.objExists(slave):
		raise Exception('Constraint slave "'+slave+'" does not exist!')
	if not glTools.utils.transform.isTransform(slave):
		raise Exception('Constraint slave "'+slave+'" is not a valid transform!')
	
	# Check Settable Channels
	st = []
	if not 'tx' in attrList or not mc.getAttr(slave+'.tx',se=True): st.append('x')
	if not 'ty' in attrList or not mc.getAttr(slave+'.ty',se=True): st.append('y')
	if not 'tz' in attrList or not mc.getAttr(slave+'.tz',se=True): st.append('z')
	if not st: st = 'none'
	
	# Skip All Check
	if len(st) == 3:
		print('No axis to constrain! Unable to create constraint...')
		return None
	
	# =====================
	# - Create Constraint -
	# =====================
	
	constraint = ''
	try: constraint = mc.pointConstraint(master,slave,sk=st,mo=mo)[0]
	except Exception, e:
		raise Exception('Error creating constraint from "'+master+'" to "'+slave+'"! Exception msg: '+str(e))
	
	# =================
	# - Return Result -
	# =================
	
	return constraint

def orientConstraint(master,slave,mo=False,attrList=['rx','ry','rz']):
	'''
	Create a point constraint between the specifiec master and slave transforms.
	Only constrains open, settable channels.
	@param master: Constraint master transform.
	@type master: str
	@param slave: Constraint slave transform.
	@type slave: str
	@param mo: Maintain constraint offset
	@type mo: bool
	@param attrList: List of transform attributes to constrain.
	@type attrList: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target (Master)
	if isinstance(master,types.StringTypes):
		if not mc.objExists(master):
			raise Exception('Constraint target "'+master+'" does not exist!')
		if not glTools.utils.transform.isTransform(master):
			raise Exception('Constraint target "'+master+'" is not a valid transform!')
	elif isinstance(master,types.ListType):
		for target in master:
			if not mc.objExists(target):
				raise Exception('Constraint target "'+target+'" does not exist!')
			if not glTools.utils.transform.isTransform(target):
				raise Exception('Constraint target "'+target+'" is not a valid transform!')
	
	# Check Slave
	if not mc.objExists(slave):
		raise Exception('Constraint slave "'+slave+'" does not exist!')
	if not glTools.utils.transform.isTransform(slave):
		raise Exception('Constraint slave "'+slave+'" is not a valid transform!')
	
	# Check Settable Channels
	sr = []
	if not 'rx' in attrList or not mc.getAttr(slave+'.rx',se=True): sr.append('x')
	if not 'ry' in attrList or not mc.getAttr(slave+'.ry',se=True): sr.append('y')
	if not 'rz' in attrList or not mc.getAttr(slave+'.rz',se=True): sr.append('z')
	if not st: st = 'none'
	
	# Skip All Check
	if len(sr) == 3:
		print('No axis to constrain! Unable to create constraint...')
		return None
	
	# =====================
	# - Create Constraint -
	# =====================
	
	constraint = ''
	try: constraint = mc.orientConstraint(master,slave,sk=sr,mo=mo)[0]
	except Exception, e:
		raise Exception('Error creating constraint from "'+master+'" to "'+slave+'"! Exception msg: '+str(e))
	
	# =================
	# - Return Result -
	# =================
	
	return constraint

def parentConstraint(master,slave,mo=False,attrList=['tx','ty','tz','rx','ry','rz']):
	'''
	Create a parent constraint between the specifiec master and slave transforms.
	Only constrains open, settable channels.
	@param master: Constraint master transform.
	@type master: str or list
	@param slave: Constraint slave transform.
	@type slave: str
	@param mo: Maintain constraint offset
	@type mo: bool
	@param attrList: List of transform attributes to constrain.
	@type attrList: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target (Master)
	if isinstance(master,types.StringTypes):
		if not mc.objExists(master):
			raise Exception('Constraint target "'+master+'" does not exist!')
		if not glTools.utils.transform.isTransform(master):
			raise Exception('Constraint target "'+master+'" is not a valid transform!')
	elif isinstance(master,types.ListType):
		for target in master:
			if not mc.objExists(target):
				raise Exception('Constraint target "'+target+'" does not exist!')
			if not glTools.utils.transform.isTransform(target):
				raise Exception('Constraint target "'+target+'" is not a valid transform!')
	
	# Check Slave
	if not mc.objExists(slave):
		raise Exception('Constraint slave "'+slave+'" does not exist!')
	if not glTools.utils.transform.isTransform(slave):
		raise Exception('Constraint slave "'+slave+'" is not a valid transform!')
	
	# Check Settable Channels
	st = []
	sr = []
	if not 'tx' in attrList or not mc.getAttr(slave+'.tx',se=True): st.append('x')
	if not 'ty' in attrList or not mc.getAttr(slave+'.ty',se=True): st.append('y')
	if not 'tz' in attrList or not mc.getAttr(slave+'.tz',se=True): st.append('z')
	if not 'rx' in attrList or not mc.getAttr(slave+'.rx',se=True): sr.append('x')
	if not 'ry' in attrList or not mc.getAttr(slave+'.ry',se=True): sr.append('y')
	if not 'rz' in attrList or not mc.getAttr(slave+'.rz',se=True): sr.append('z')
	if not st: st = 'none'
	if not sr: sr = 'none'
	
	# =====================
	# - Create Constraint -
	# =====================
	
	constraint = ''
	try: constraint = mc.parentConstraint(master,slave,st=st,sr=sr,mo=mo)[0]
	except Exception, e:
		raise Exception('Error creating constraint from "'+master+'" to "'+slave+'"! Exception msg: '+str(e))
	
	# =================
	# - Return Result -
	# =================
	
	return constraint

def scaleConstraint(master,slave,mo=False,force=False,attrList=['sx','sy','sz']):
	'''
	Create a scale constraint between the specified master and slave transforms.
	Only constrains open, settable channels.
	@param master: Constraint master transform.
	@type master: str
	@param slave: Constraint slave transform.
	@type slave: str
	@param mo: Maintain constraint offset
	@type mo: bool
	@param force: Force constraint by deleteing scale channel keys. Use with caution!
	@type force: bool
	@param attrList: List of transform attributes to constrain.
	@type attrList: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Master
	if not mc.objExists(master):
		raise Exception('Constraint master "'+master+'" does not exist!')
	if not glTools.utils.transform.isTransform(master):
		raise Exception('Constraint master "'+master+'" is not a valid transform!')
	
	# Check Slave
	if not mc.objExists(slave):
		raise Exception('Constraint slave "'+slave+'" does not exist!')
	if not glTools.utils.transform.isTransform(slave):
		raise Exception('Constraint slave "'+slave+'" is not a valid transform!')
	
	# Check Settable Channels
	sk = []
	if not 'sx' in attrList or not mc.getAttr(slave+'.sx',se=True): sk.append('x')
	if not 'sy' in attrList or not mc.getAttr(slave+'.sy',se=True): sk.append('y')
	if not 'sz' in attrList or not mc.getAttr(slave+'.sz',se=True): sk.append('z')
	if not sk: st = 'none'
	
	# Check All
	if len(sk) == 3:
		print('All scale channels locked! Unable to add constraint')
		return None
	
	# =====================
	# - Create Constraint -
	# =====================
	
	if force: mc.cutKey(slave,at=attrList)
	
	constraint = ''
	try: constraint = mc.scaleConstraint(master,slave,sk=sk,mo=mo)[0]
	except Exception, e:
		#raise Exception('Error creating constraint from "'+master+'" to "'+slave+'"! Exception msg: '+str(e))
		print('Error creating constraint from "'+master+'" to "'+slave+'"! Exception msg: '+str(e))
		constraint = None
	
	# =================
	# - Return Result -
	# =================
	
	return constraint

def nonReferencedConstraints(slaveNSfilter=None,targetNSfilter=None):
	'''
	Return a list of non referenced constraint nodes in the current scene.
	Optionally, filter results by slave and/or target namespace.
	@param slaveNSfilter: Constraint slave transform namespace filter list.
	@type slaveNSfilter: list
	@param targetNSfilter: Constraint target transform namespace filter list.
	@type targetNSfilter: list
	'''
	# =========================
	# - Get Scene Constraints -
	# =========================
	
	sceneConstraints = mc.ls(type='constraint')
	if not sceneConstraints: return []
	
	# Filter Nonreferenced Constraints
	nonRefConstraints = []
	for constraint in sceneConstraints:
		if not glTools.utils.reference.isReferenced(constraint):
			if not constraint in nonRefConstraints:
				nonRefConstraints.append(constraint)
	
	# =================
	# - Filter Result -
	# =================
	
	# Slave Namespace Filter
	if slaveNSfilter:
		for constraint in nonRefConstraints:
			filterOut = True
			constraintSlave = glTools.utils.constraint.slaveList(constraint)
			for slave in constraintSlave:
				if not ':' in slave: slave = ':'+slave
				slaveNS = slave.split(':')[0]
				if slaveNS in slaveNSfilter: filterOut = False
			if filterOut:
				nonRefConstraints.remove(constraint)
			
	# Master Namespace Filter
	if targetNSfilter:
		for constraint in nonRefConstraints:
			filterOut = True
			constraintTarget = glTools.utils.constraint.targetList(constraint)
			for target in constraintTarget:
				if not ':' in target: target = ':'+target
				targetNS = target.split(':')[0]
				if targetNS in targetNSfilter: filterOut = False
			if filterOut:
				nonRefConstraints.remove(constraint)
	
	# =================
	# - Return Result -
	# =================
	
	return nonRefConstraints

def listReferenceDependents():
	'''
	'''
	pass

def listReferenceDependencies():
	'''
	'''
	pass

def translateOffsetTarget(target,offset,slave,prefix=None):
	'''
	Create a translate offset target constraint (parentConstraint).
	The slave will follow the target in rotation only and the offset in translation.
	Used mainly for specific IK pole vector target setup.
	@param target: Constraint target.
	@type target: str
	@param offset: Offset target to follow in translation.
	@type offset: str
	@param slave: Slave transform to create constraint for.
	@type slave: str
	@param prefix: Naming prefix.
	@type prefix: str or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Target
	if not mc.objExists(target):
		raise Exception('Target transform "'+target+'" does not exist!')
	if not glTools.utils.transform.isTransform(target):
		raise Exception('Target object "'+target+'" is not a valid tranform!')
	
	# Offset
	if not mc.objExists(offset):
		raise Exception('Offset transform "'+offset+'" does not exist!')
	if not glTools.utils.transform.isTransform(offset):
		raise Exception('Offset object "'+offset+'" is not a valid tranform!')
	
	# Slave
	if not mc.objExists(slave):
		raise Exception('Slave transform "'+slave+'" does not exist!')
	if not glTools.utils.transform.isTransform(slave):
		raise Exception('Slave object "'+slave+'" is not a valid tranform!')
	
	# Prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(slave)
	
	# ====================
	# - Build Constraint -
	# ====================
	
	# Parent Slave to Target
	mc.delete(parentConstraint(target,slave))
	mc.parent(slave,target)
	
	# Create Offset Constraint
	offsetConstraint = mc.pointConstraint(offset,slave,mo=True)[0]
	offsetConstraint = mc.rename(offsetConstraint,prefix+'_offset_pointConstraint')
	
	# =================
	# - Return Result -
	# =================
	
	return offsetConstraint

def pointOnPolyConstraintCmd(pt):
	'''
	Generate a pointOnPolyConstraint setup command string.
	@param pt: Mesh point to generate pointOnPolyConstraint command for.
	@type pt: str
	'''
	# ==================
	# - Initialize Cmd -
	# ==================
	
	cmd = ''
	
	# ===============================
	# - Get Mesh from Point on Poly -
	# ===============================
	
	fullname = mc.ls(pt,o=True)[0]
	mesh = fullname.split(':')[-1]
	meshSN = mesh.split('|')[-1]
	
	# Get Mesh Component ID
	meshID = glTools.utils.component.index(pt)
	
	prevID = OpenMaya.MScriptUtil()
	prevID.createFromInt(0)
	prevIDPtr = prevID.asIntPtr()
	
	# =======================
	# - Constrain to Vertex -
	# =======================
	
	if '.vtx[' in pt:
		
		# Initialize MItMeshVertex
		meshIt = glTools.utils.mesh.getMeshVertexIter(mesh)
		meshIt.setIndex(meshID,prevIDPtr)
		
		# Get Vertex UV
		uv = OpenMaya.MScriptUtil()
		uv.createFromDouble(0.0)
		uvPtr = uv.asFloat2Ptr()
		meshIt.getUV(uvPtr)
		uv = [ OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPtr,0,j) for j in [0,1] ]
		cmd += '; setAttr ($constraint[0]+".%sU%d") %f; setAttr ($constraint[0]+".%sV%d") %f' % ( meshSN, 0, uv[0], meshSN, 0, uv[1] )
	
	# =====================
	# - Constrain to Edge -
	# =====================
	
	elif '.e[' in pt:
		
		# Initialize MItMeshEdge
		meshIt = glTools.utils.mesh.getMeshEdgeIter(mesh)
		meshIt.setIndex(meshID,prevIDPtr)
		
		# Get Edge/Vertices UV
		vtx = [ meshIt.index( j ) for j in [0,1] ]
		vtxIt = glTools.utils.mesh.getMeshVertexIter(mesh)
		uvs = []
		for v in vtx:
			vtxIt.setIndex(v,prevIDPtr)
			uv = OpenMaya.MScriptUtil()
			uv.createFromDouble( 0.0 )
			uvPtr = uv.asFloat2Ptr()
			vtxIt.getUV(uvPtr)
			uvs.append( [ OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPtr,0,j) for j in [0,1] ] )
		uv = [ 0.5*(uvs[0][j]+uvs[1][j]) for j in [0,1] ]
		cmd += '; setAttr ($constraint[0]+".%sU%d") %f; setAttr ($constraint[0]+".%sV%d") %f' % ( meshSN, 0, uv[0], meshSN, 0, uv[1] )
			
	# =====================
	# - Constrain to Face -
	# =====================
	
	elif '.f[' in pt:
		
		# Initialize MItMeshface
		meshIt = glTools.utils.mesh.getMeshFaceIter(mesh)
		meshIt.setIndex(meshID,prevIDPtr)
		
		# Get Face UV
		u, v = OpenMaya.MFloatArray(), OpenMaya.MFloatArray()
		meshIt.getUVs( u, v )
		uv = ( sum(u)/len(u), sum(v)/len(v) )
		cmd += '; setAttr ($constraint[0]+".%sU%d") %f; setAttr ($constraint[0]+".%sV%d") %f' % ( meshSN, 0, uv[0], meshSN, 0, uv[1] )
	
	# =================
	# - Return Result -
	# =================
	
	return cmd


