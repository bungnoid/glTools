import maya.cmds as mc
import maya.mel as mm

import glTools.utils.base
import glTools.utils.mesh

def createBasicMeasure(mesh,vtxId1,vtxId2,prefix):
	'''
	Create a basic measure curve. The measure curve will not be constrained to the mesh or contain any measurement attributes.
	@param mesh: The mesh to generate the measure from
	@type mesh: str
	@param vtxId1: The first vertex to generate the measure curve from
	@type vtxId1: int
	@param vtxId2: The second vertex to generate the measure curve from
	@type vtxId2: int
	'''
	# Check prefix
	if not prefix: prefix = 'measureMeshDistance'
	
	# Check baseMesh
	if not mc.objExists(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!!')
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# Create nulls
	pt1 = mc.spaceLocator(n=prefix+'_pt1')[0]
	pt2 = mc.spaceLocator(n=prefix+'_pt2')[0]
	
	# Position nulls
	pos1 = glTools.utils.base.getPosition(mesh+'.vtx['+str(vtxId1)+']')
	pos2 = glTools.utils.base.getPosition(mesh+'.vtx['+str(vtxId2)+']')
	mc.setAttr(pt1+'.t',pos1[0],pos1[1],pos1[2])
	mc.setAttr(pt2+'.t',pos2[0],pos2[1],pos2[2])
	
	# Create measure curve
	measureCrv = mc.curve(d=1,p=[pos1,pos2],k=[0,1])
	measureCrv = mc.rename(measureCrv,prefix+'_measure')
	mc.parent([pt1,pt2],measureCrv)
	
	# Connect to measurement null control points
	mc.connectAttr(pt1+'.t',measureCrv+'.controlPoints[0]')
	mc.connectAttr(pt2+'.t',measureCrv+'.controlPoints[1]')
	
	# Add vtx attrs
	mc.addAttr(pt1,ln='vtx',at='long',dv=vtxId1,k=True)
	mc.addAttr(pt2,ln='vtx',at='long',dv=vtxId2,k=True)
	
	# Return result
	return measureCrv
	
def getMeasureDistance(measure,mesh):
	'''
	Calculate the measure distance based on a reference mesh
	@param measure: The measure to calculate a distance for
	@type measure: str
	@param mesh: The mesh to calculate the distance from
	@type mesh: str
	'''
	# Get measure points
	pts = mc.listRelatives(measure,c=True,type='transform')
	pt1 = pts[0]
	pt2 = pts[1]
	
	# Get measure vtxIds
	vtxId1 = mc.getAttr(pt1+'.vtx')
	vtxId2 = mc.getAttr(pt2+'.vtx')
	
	# Get mesh vertex positions
	vtxPt1 = glTools.utils.base.getMPoint(mesh+'.vtx['+str(vtxId1)+']')
	vtxPt2 = glTools.utils.base.getMPoint(mesh+'.vtx['+str(vtxId2)+']')
	
	# Get distance
	dist = (vtxPt1 - vtxPt2).length()
	
	# Return result
	return dist

def addDistanceAttrs(measure,baseMesh):
	'''
	Add the default distance and current distance (dynamic) measure attributes
	@param measure: The measure to create distance attributes for
	@type measure: str
	@param mesh: The mesh to calculate the base distance from
	@type mesh: str
	'''
	# Get prefix
	prefix = measure.replace(measure.split('_')[-1],'')
	
	# Get measure points
	pts = mc.listRelatives(measure,c=True,type='transform')
	pt1 = pts[0]
	pt2 = pts[1]
	
	# Create distance node
	distanceNode = mc.createNode('distanceBetween',n=prefix+'distanceBetween')
	mc.connectAttr(pt1+'.worldMatrix[0]',distanceNode+'.inMatrix1',f=True)
	mc.connectAttr(pt2+'.worldMatrix[0]',distanceNode+'.inMatrix2',f=True)
	
	# Add distance attr
	if not mc.objExists(measure+'.distance'):
		mc.addAttr(measure,ln='distance',k=True)
	mc.connectAttr(distanceNode+'.distance',measure+'.distance',f=True)
	
	# Add base distance attr
	if not mc.objExists(measure+'.baseDistance'):
		mc.addAttr(measure,ln='baseDistance',k=True)
	# Get base distance
	dist = getMeasureDistance(measure,baseMesh)
	# Set base distance value
	mc.setAttr(measure+'.baseDistance',dist,l=True)
	
	# Return result
	return (measure+'.distance')
	
def addMeasureAttrs(measure,targetMesh,targetName):
	'''
	Add target distance measure attributes
	@param measure: The measure to create target distance attributes for
	@type measure: str
	@param mesh: The mesh to calculate the target distance from
	@type mesh: str
	@param targetName: The name of the distance target
	@type targetName: str
	'''
	# Get prefix
	prefix = measure.replace(measure.split('_')[-1],'')
	
	# Add measure attributes
	if not mc.objExists(measure+'.'+targetName):
		mc.addAttr(measure,ln=targetName,min=0.0,max=1.0,dv=0.0,k=True)
	if not mc.objExists(measure+'.'+targetName+'Length'):
		mc.addAttr(measure,ln=targetName+'Length',dv=0.0,k=True)
	if not mc.objExists(measure+'.'+targetName+'Envelope'):
		mc.addAttr(measure,ln=targetName+'Envelope',min=0.0,max=2.0,dv=1.0,k=True)
	if not mc.objExists(measure+'.'+targetName+'Offset'):
		mc.addAttr(measure,ln=targetName+'Offset',dv=0.0,k=True)
		
	# Create remapValue node
	remapNode = mc.createNode('remapValue',n=prefix+targetName+'_remapValue')
	mc.setAttr(remapNode+'.outputMin',0.0)
	mc.setAttr(remapNode+'.outputMax',1.0)
	mc.setAttr(remapNode+'.value[0].value_Interp',3)
	
	# Connect measure distance to remap input
	if not mc.objExists(measure+'.distance'):
		raise Exception('Measure "'+measure+'" has no distance attribute! Run addDistanceAttrs() to add necessary attributes!!')
	mc.connectAttr(measure+'.distance',remapNode+'.inputValue',f=True)
	
	# Get base distance - minimum input value
	if not mc.objExists(measure+'.baseDistance'):
		raise Exception('Measure "'+measure+'" has no baseDistance attribute! Run addDistanceAttrs() to add necessary attributes!!')
	mc.connectAttr(measure+'.baseDistance',remapNode+'.inputMin',f=True)
		
	# Get target length - maximum input value
	if not mc.objExists(targetMesh):
		raise Exception('Target mesh "'+targetMesh+'" does not exist!')
	targetDist = getMeasureDistance(measure,targetMesh)
	mc.setAttr(measure+'.'+targetName+'Length',targetDist,l=True)
	mc.connectAttr(measure+'.'+targetName+'Length',remapNode+'.inputMax',f=True)
	
	# Connect target envelope
	envelopeNode = mc.createNode('multDoubleLinear',n=prefix+targetName+'Envelope_multDoubleLinear')
	mc.connectAttr(remapNode+'.outValue',envelopeNode+'.input1',f=True)
	mc.connectAttr(measure+'.'+targetName+'Envelope',envelopeNode+'.input2',f=True)
	
	# Connect target offset
	offsetNode = mc.createNode('addDoubleLinear',n=prefix+targetName+'Offset_addDoubleLinear')
	mc.connectAttr(envelopeNode+'.output',offsetNode+'.input1',f=True)
	mc.connectAttr(measure+'.'+targetName+'Offset',offsetNode+'.input2',f=True)
	
	# Connect to measure target value
	mc.connectAttr(offsetNode+'.output',measure+'.'+targetName,f=True)
	
	# Return result
	return (measure+'.'+targetName)

def addMeasureAttrs_old(measure,targetMesh,targetName):
	'''
	Add target distance measure attributes
	@param measure: The measure to create target distance attributes for
	@type measure: str
	@param mesh: The mesh to calculate the target distance from
	@type mesh: str
	@param targetName: The name of the distance target
	@type targetName: str
	'''
	# Get prefix
	prefix = measure.replace(measure.split('_')[-1],'')
	
	# Add measure attributes
	if not mc.objExists(measure+'.'+targetName):
		mc.addAttr(measure,ln=targetName,min=0.0,max=1.0,dv=0.0,k=True)
	if not mc.objExists(measure+'.'+targetName+'Length'):
		mc.addAttr(measure,ln=targetName+'Length',dv=0.0,k=True)
	if not mc.objExists(measure+'.'+targetName+'Envelope'):
		mc.addAttr(measure,ln=targetName+'Envelope',min=0.0,max=2.0,dv=1.0,k=True)
		
	# Create remapValue node
	remapNode = mc.createNode('remapValue',n=prefix+targetName+'_remapValue')
	mc.setAttr(remapNode+'.outputMin',0.0)
	mc.setAttr(remapNode+'.outputMax',1.0)
	mc.setAttr(remapNode+'.value[0].value_Interp',3)
	
	# Connect measure distance to remap input
	if not mc.objExists(measure+'.distance'):
		raise Exception('Measure "'+measure+'" has no distance attribute! Run addDistanceAttrs() to add necessary attributes!!')
	mc.connectAttr(measure+'.distance',remapNode+'.inputValue',f=True)
	
	# Get base distance - minimum input value
	if not mc.objExists(measure+'.baseDistance'):
		raise Exception('Measure "'+measure+'" has no baseDistance attribute! Run addDistanceAttrs() to add necessary attributes!!')
	mc.connectAttr(measure+'.baseDistance',remapNode+'.inputMin',f=True)
		
	# Get target length - maximum input value
	if not mc.objExists(targetMesh):
		raise Exception('Target mesh "'+targetMesh+'" does not exist!')
	targetDist = getMeasureDistance(measure,targetMesh)
	mc.setAttr(measure+'.'+targetName+'Length',targetDist,l=True)
	mc.connectAttr(measure+'.'+targetName+'Length',remapNode+'.inputMax',f=True)
	
	# Connect target envelope to ramp
	mc.connectAttr(measure+'.'+targetName+'Envelope',remapNode+'.value[1].value_FloatValue',f=True)
	
	# Connect to measure target value
	mc.connectAttr(remapNode+'.outValue',measure+'.'+targetName,f=True)
	
	# Return result
	return (measure+'.'+targetName)

def addCustomMeasureAttrs(measure,targetName,min=0.0,max=1.0):
	'''
	Add custom target distance measure attributes
	@param measure: The measure to create target distance attributes for
	@type measure: str
	@param targetName: The name of the distance target
	@type targetName: str
	@param min: Minimum input value for custom measure distance.
	@type min: float
	@param max: Maximum input value for custom measure distance.
	@type max: float
	'''
	# Get prefix
	prefix = measure.replace(measure.split('_')[-1],'')
	
	# Add custom measure attributes
	if not mc.objExists(measure+'.'+targetName):
		mc.addAttr(measure,ln=targetName,min=0.0,max=1.0,dv=0.0,k=True)
	if not mc.objExists(measure+'.'+targetName+'MinLength'):
		mc.addAttr(measure,ln=targetName+'MinLength',dv=min,k=True)
	if not mc.objExists(measure+'.'+targetName+'MaxLength'):
		mc.addAttr(measure,ln=targetName+'MaxLength',dv=max,k=True)
	if not mc.objExists(measure+'.'+targetName+'Envelope'):
		mc.addAttr(measure,ln=targetName+'Envelope',min=0.0,max=2.0,dv=1.0,k=True)
	if not mc.objExists(measure+'.'+targetName+'Offset'):
		mc.addAttr(measure,ln=targetName+'Offset',dv=0.0,k=True)
	
	# Create remapValue node
	remapNode = mc.createNode('remapValue',n=prefix+targetName+'_remapValue')
	mc.setAttr(remapNode+'.outputMin',0.0)
	mc.setAttr(remapNode+'.outputMax',1.0)
	mc.setAttr(remapNode+'.value[0].value_Interp',3)
	
	# Connect measure distance to remap input
	if not mc.objExists(measure+'.distance'):
		raise Exception('Measure "'+measure+'" has no distance attribute! Run addDistanceAttrs() to add necessary attributes!!')
	mc.connectAttr(measure+'.distance',remapNode+'.inputValue',f=True)
	
	# Connect min/max custom measure inputs
	mc.connectAttr(measure+'.'+targetName+'MinLength',remapNode+'.inputMin',f=True)
	mc.connectAttr(measure+'.'+targetName+'MaxLength',remapNode+'.inputMax',f=True)
	
	# Connect target envelope
	envelopeNode = mc.createNode('multDoubleLinear',n=prefix+targetName+'Envelope_multDoubleLinear')
	mc.connectAttr(remapNode+'.outValue',envelopeNode+'.input1',f=True)
	mc.connectAttr(measure+'.'+targetName+'Envelope',envelopeNode+'.input2',f=True)
	
	# Connect target offset
	offsetNode = mc.createNode('addDoubleLinear',n=prefix+targetName+'Offset_addDoubleLinear')
	mc.connectAttr(envelopeNode+'.output',offsetNode+'.input1',f=True)
	mc.connectAttr(measure+'.'+targetName+'Offset',offsetNode+'.input2',f=True)
	
	# Connect to measure target value
	mc.connectAttr(offsetNode+'.output',measure+'.'+targetName,f=True)
	
	# Return result
	return (measure+'.'+targetName)

def addRigAttrs(measure,rigAttr,targetName,remap=False,inputMin=0.0,inputMax=1.0,outputMin=0.0,outputMax=1.0):
	'''
	Add rig attribute to measure curve with the option to remap the incoming value.
	@param measure: The measure to add rig attributes to
	@type measure: str
	@param rigAttr: The rig attribute to add to the measure
	@type rigAttr: str
	@param targetName: The name of the rig attribute target
	@type targetName: str
	@param remap: Remap the rig attribute to 0.0 -> 1.0
	@type remap: bool
	@param inputMin: Minimum input value for rig attribute. Only used if remap=True.
	@type inputMin: float
	@param inputMax: Maximum input value for rig attribute. Only used if remap=True.
	@type inputMax: float
	@param outputMin: Minimum output value for rig attribute. Only used if remap=True.
	@type outputMin: float
	@param outputMax: Maximum output value for rig attribute. Only used if remap=True.
	@type outputMax: float
	'''
	# Check measure
	if not mc.objExists(measure):
		raise Exception('Measure "'+measure+'" does not exist!!')
	# Check rig attr
	if not mc.objExists(rigAttr):
		raise Exception('Rig attribute "'+rigAttr+'" does not exist!!')
	
	# Get prefix
	prefix = measure.replace(measure.split('_')[-1],'')
	
	# Add compression attributes
	if mc.objExists(measure+'.'+targetName):
		raise Exception('Attribute "'+targetName+'" already exists on measure "'+measure+'"!')
	mc.addAttr(measure,ln=targetName,min=0.0,max=1.0,dv=0.0,k=True)
	
	# Check remap
	if remap:
		
		# Add min/max remap attributes
		mc.addAttr(measure,ln=targetName+'InputMin',dv=inputMin,k=True)
		mc.addAttr(measure,ln=targetName+'InputMax',dv=inputMax,k=True)
		mc.addAttr(measure,ln=targetName+'OutputMin',dv=outputMin,k=True)
		mc.addAttr(measure,ln=targetName+'OutputMax',dv=outputMax,k=True)
		
		# Create remapValue node
		remapNode = mc.createNode('remapValue',n=prefix+targetName+'_remapValue')
		mc.setAttr(remapNode+'.value[0].value_Interp',3)
		
		# Connect rig attr to ramp input
		mc.connectAttr(rigAttr,remapNode+'.inputValue',f=True)
		
		# Set input/output min and max values
		mc.connectAttr(measure+'.'+targetName+'InputMin',remapNode+'.inputMin',f=True)
		mc.connectAttr(measure+'.'+targetName+'InputMax',remapNode+'.inputMax',f=True)
		mc.connectAttr(measure+'.'+targetName+'OutputMin',remapNode+'.outputMin',f=True)
		mc.connectAttr(measure+'.'+targetName+'OutputMax',remapNode+'.outputMax',f=True)
		
		# Connect to measure target value
		mc.connectAttr(remapNode+'.outValue',measure+'.'+targetName,f=True)
	
	else:
		
		# Connect rig attribute to measure target value
		mc.connectAttr(rigAttr,measure+'.'+targetName,f=True)
	
	# Return result
	return (measure+'.'+targetName)
	
def snapMeasure(measure,mesh):
	'''
	Snap the measure points to the vertices of the specified mesh.
	The vertex id to snap to is determined by the ".vtx" attribute contained on the measure point
	@param measure: The measure to snap
	@type measure: str
	@param mesh: The mesh to snap to
	@type mesh: str
	'''
	# Checks
	if not mc.objExists(measure):
		raise Exception('Measure "'+measure+'" does not exist!!')
	if not mc.objExists(mesh):
		raise Exception('Mesh "'+mesh+'" does not exist!!')
	if not glTools.utils.mesh.isMesh(mesh):
		raise Exception('Object "'+mesh+'" is not a valid mesh!!')
	
	# Get measure points
	pts = mc.listRelatives(measure,c=True,type='transform')
	
	# Snap measure points
	for pt in pts:
		vtxId = mc.getAttr(pt+'.vtx')
		glTools.utils.mesh.snapToVertex(mesh,pt,vtxId)
	
	# Retrun result
	return pts
	
def constrainMeasure(measure,mesh):
	'''
	Constrain the measure points to the vertices of the specified mesh.
	The vertex id to constrain to is determined by the ".vtx" attribute contained on the measure point.
	@param measure: The measure to constrain
	@type measure: str
	@param mesh: The mesh to constrain to
	@type mesh: str
	'''
	# Get prefix
	prefix = measure.replace(measure.split('_')[-1],'')
	
	# Snap measure
	snapMeasure(measure,mesh)
	
	# Get measure points
	pts = mc.listRelatives(measure,c=True,type='transform')
	pt1 = pts[0]
	pt2 = pts[1]
	
	# Constrain measurment nulls
	pt1Con = mc.dnMeshConstraint(mesh,pt1,kr=True,n=prefix+'pt1_dnMeshConstraint')[0]
	pt2Con = mc.dnMeshConstraint(mesh,pt2,kr=True,n=prefix+'pt2_dnMeshConstraint')[0]
	
	# Return result
	return [pt1Con,pt2Con]

def measureMeshDistanceMulti(baseMesh,vtxId1,vtxId2,inputTargetList,prefix):
	'''
	'''
	# ----------
	# - Checks -
	# ----------
	
	# Check prefix
	if not prefix: prefix = 'measureMeshDistance'
	
	# Check baseMesh
	if not mc.objExists(baseMesh):
		raise Exception('Base mesh "'+baseMesh+'" does not exist!!')
	
	# Check inputTargetList
	for target in inputTargetList:
		if not mc.objExists(target):
			raise Exception('target mesh "'+target+'" does not exist!!')
	
	# ------------------------
	# - Get vertex distances -
	# ------------------------
	
	# Base distance
	basePt1 = glTools.utils.base.getMPoint(baseMesh+'.vtx['+str(vtxId1)+']')
	basePt2 = glTools.utils.base.getMPoint(baseMesh+'.vtx['+str(vtxId2)+']')
	basePos1 = [basePt1.x,basePt1.y,basePt1.z]
	basePos2 = [basePt2.x,basePt2.y,basePt2.z]
	baseDist = (basePt1-basePt2).length()
	
	# ------------------------
	# - Get target distances -
	# ------------------------
	
	# Initialize target distance arrays
	inputTargetDist = [(baseDist,'base')]
	
	# For each target
	for target in inputTargetList:
		# Get target distance
		targetPt1 = glTools.utils.base.getMPoint(target+'.vtx['+str(vtxId1)+']')
		targetPt2 = glTools.utils.base.getMPoint(target+'.vtx['+str(vtxId2)+']')
		targetDist = (targetPt1-targetPt2).length()
		inputTargetDist.append((targetDist,target))
	
	# Sort according to target distance
	inputTargetDist.sort()
	
	# Generate input target data
	inputTargetData = {}
	for i in range(len(inputTargetDist)):
		# Get current target and distance
		inputDist = inputTargetDist[i][0]
		inputTarget = inputTargetDist[i][1]
		
		# Skip base distance
		if inputTarget == 'base': continue
		
		# Add target and distance to inputTargetData
		inputTargetData[inputTarget] = []
		inputTargetData[inputTarget].append(inputDist)
		
		# Determine bracket values
		targetBracket = []
		if i: targetBracket.append(inputTargetDist[i-1][0])
		targetBracket.append(inputDist)
		if i < (len(inputTargetDist)-1): targetBracket.append(inputTargetDist[i+1][0])
		
		# Append bracket values to inputTargetData
		inputTargetData[inputTarget].append(targetBracket)
	
	# ----------------------------
	# - Create Measurement Nulls -
	# ----------------------------
	
	# Create nulls
	grp = mc.group(em=True,n=prefix+'_grp')
	pt1 = mc.group(em=True,n=prefix+'_pt1_null')
	pt2 = mc.group(em=True,n=prefix+'_pt2_null')
	
	# Position nulls
	mc.setAttr(pt1+'.t',basePt1.x,basePt1.y,basePt1.z)
	mc.setAttr(pt2+'.t',basePt2.x,basePt2.y,basePt2.z)
	
	# Constrain measurment nulls
	mc.select(baseMesh,pt1)
	pt1Con = mm.eval('dnMeshConstraint')
	mc.rename(pt1Con,prefix+'_pt1_dnMeshConstraint')
	mc.select(baseMesh,pt2)
	pt2Con = mm.eval('dnMeshConstraint')
	mc.rename(pt2Con,prefix+'_pt2_dnMeshConstraint')
	
	# Create measure curve
	measureCrv = mc.curve(d=1,p=[basePos1,basePos2],k=[0,1])
	measureCrv = mc.rename(measureCrv,prefix+'_measure')
	mc.parent([measureCrv,pt1,pt2],grp)
	# Connect to measurement null control points
	mc.connectAttr(pt1+'.t',measureCrv+'.controlPoints[0]')
	mc.connectAttr(pt2+'.t',measureCrv+'.controlPoints[1]')
	
	# ----------------------
	# - Calculate distance -
	# ----------------------
	
	# Create distance node
	distanceNode = mc.createNode('distanceBetween',n=prefix+'_distanceBetween')
	mc.connectAttr(pt1+'.worldMatrix[0]',distanceNode+'.inMatrix1',f=True)
	mc.connectAttr(pt2+'.worldMatrix[0]',distanceNode+'.inMatrix2',f=True)
	
	# ---------------------------
	# - Add distance attributes -
	# ---------------------------
	
	# Current distance
	mc.addAttr(measureCrv,ln='distance',k=True)
	mc.connectAttr(distanceNode+'.distance',measureCrv+'.distance',f=True)
	
	# Base distance
	mc.addAttr(measureCrv,ln='baseDistance',dv=baseDist,k=True)
	mc.setAttr(measureCrv+'.baseDistance',l=True)
	
	# Target distance
	for target in inputTargetList:
		targetAttr = target+'TargetDistance'
		mc.addAttr(measureCrv,ln=targetAttr,dv=inputTargetData[target][0],k=True)
		mc.setAttr(measureCrv+'.'+targetAttr,l=True)
	
	# -------------------------------------------
	# - Add normalized target weight attributes -
	# -------------------------------------------
	
	for target in inputTargetList:
		
		# Get input target data
		targetData = inputTargetData[target]
		targetDist = targetData[0]
		targetBracket = targetData[1]
		
		# Add target attributes
		mc.addAttr(measureCrv,ln=target,k=True)
		mc.addAttr(measureCrv,ln=target+'Weight',min=0,max=1,dv=1,k=True)
		
		# Remap target distance
		targetRemapNode = mc.createNode('remapValue',n=prefix+'_'+target+'_remapValue')
		mc.connectAttr(distanceNode+'.distance',targetRemapNode+'.inputValue',f=True)
		
		# Set input limits
		mc.setAttr(targetRemapNode+'.outputMin',0.0)
		mc.setAttr(targetRemapNode+'.outputMax',1.0)
		if targetDist > baseDist:
			mc.setAttr(targetRemapNode+'.inputMin',targetBracket[0])
			mc.setAttr(targetRemapNode+'.inputMax',targetBracket[-1])
		else:
			mc.setAttr(targetRemapNode+'.inputMax',targetBracket[0])
			mc.setAttr(targetRemapNode+'.inputMin',targetBracket[-1])
		
		# Set ramp attributes
		mc.setAttr(targetRemapNode+'.value[0].value_Position',0)
		mc.setAttr(targetRemapNode+'.value[0].value_FloatValue',0)
		mc.setAttr(targetRemapNode+'.value[0].value_Interp',2)
		mc.setAttr(targetRemapNode+'.value[1].value_Position',1)
		mc.setAttr(targetRemapNode+'.value[1].value_FloatValue',1)
		mc.setAttr(targetRemapNode+'.value[1].value_Interp',2)
		
		# Check target fade out
		if len(targetBracket) == 3:
			
			print ('bracketed ramp on "'+prefix+'" for target "'+target+'"')
			
			# Calculate normalized bracket mid point
			midWeight = (targetBracket[1]-targetBracket[0])/(targetBracket[2]-targetBracket[0])
			
			print ('midWeight = '+str(midWeight))
			
			# Set ramp attributes
			mc.setAttr(targetRemapNode+'.value[1].value_Position',midWeight)
			mc.setAttr(targetRemapNode+'.value[1].value_FloatValue',1)
			mc.setAttr(targetRemapNode+'.value[1].value_Interp',2)
			mc.setAttr(targetRemapNode+'.value[2].value_Position',1)
			mc.setAttr(targetRemapNode+'.value[2].value_FloatValue',0)
			mc.setAttr(targetRemapNode+'.value[2].value_Interp',2)
			
		# Connect target weight to ramp
		mc.connectAttr(measureCrv+'.'+target+'Weight',targetRemapNode+'.value[1].value_FloatValue',f=True)
		
		# Connect to target attribute
		mc.connectAttr(targetRemapNode+'.outValue',measureCrv+'.'+target,f=True)
		
	# -----------------
	# - Return result -
	# -----------------
	
	return measureCrv
