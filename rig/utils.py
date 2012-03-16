import maya.cmds as mc

import glTools.utils.base
import glTools.utils.channelState
import glTools.utils.joint
import glTools.utils.mathUtils
import glTools.utils.matrix
import glTools.utils.stringUtils

def tagCtrl(control,ctrlLod='primary'):
	'''
	'''
	# Check Control
	if not mc.objExists(control):
		raise Exception('Control object "'+control+'" does not exist!')
		
	# Check Control LOD
	ctrlLodDict = {'primary':0,'secondary':1,'tertiary':2}
	if not ctrlLodDict.has_key(ctrlLod):
		raise Exception('Invalid control LOD "'+ctrlLod+'"!')
	
	# Tag control
	if not mc.objExists(control+'.ctrlLod'):
		mc.addAttr(control,ln='ctrlLod',at='enum',en='primary:secondary:tertiary:')
	mc.setAttr(control+'.ctrlLod',ctrlLodDict[ctrlLod])
	
	# Get Channel State
	mc.setAttr(control+'.ro',k=True,cb=True)

def toggleCons(state):
	'''
	Toggle the display state of all joint buffers ('Con') in the scene
	@param state: The display state to set the joint buffers to
	@type state: bool
	'''
	# Get list of Con joints
	conList = mc.ls('*Con*_jnt',type='joint')
	
	# Toggle state
	if state:
		for con in conList:
			mc.setAttr(con+'.overrideEnabled',1)
			mc.setAttr(con+'.overrideLevelOfDetail',1)
	else:
		for con in conList:
			mc.setAttr(con+'.overrideEnabled',1)
			mc.setAttr(con+'.overrideLevelOfDetail',0)

def toggleEnds(state):
	'''
	Toggle the display state of all joint buffers ('Con') in the scene
	@param state: The display state to set the joint buffers to
	@type state: bool
	'''
	# Get list of End joints
	endList = mc.ls('*End_jnt',type='joint')
	
	# Toggle state
	if state:
		for end in endList:
			mc.setAttr(end+'.overrideEnabled',1)
			mc.setAttr(end+'.overrideLevelOfDetail',1)
	else:
		for end in endList:
			mc.setAttr(end+'.overrideEnabled',1)
			mc.setAttr(end+'.overrideLevelOfDetail',0)

def setToDefault(ctrl):
	'''
	Set the attributes of the specified control to default values
	@param ctrl: The control to set default attribute values for
	@type ctrl: str
	'''
	# Check control
	if not mc.objExists(ctrl):
		raise Exception('Control "'+ctrl+'" does not exist!')
	
	# Define standard transform controls
	tAttr = ['tx','ty','tz']
	rAttr = ['rx','ry','rz']
	sAttr = ['sx','sy','sz']
	
	# Get user defined attrs
	udAttr = mc.listAttr(ctrl,ud=True)
	
	# Reset to defaults
	for attr in tAttr:
		if mc.getAttr(ctrl+'.'+attr,se=True):
			mc.setAttr(ctrl+'.'+attr,0.0)
	for attr in rAttr:
		if mc.getAttr(ctrl+'.'+attr,se=True):
			mc.setAttr(ctrl+'.'+attr,0.0)
	for attr in sAttr:
		if mc.getAttr(ctrl+'.'+attr,se=True):
			mc.setAttr(ctrl+'.'+attr,1.0)
	for attr in udAttr:
		dv = mc.addAttr(ctrl+'.'+attr,q=True,dv=True)
		if mc.getAttr(ctrl+'.'+attr,se=True):
			mc.setAttr(ctrl+'.'+attr,dv)

def poleVectorPosition(startJoint,midJoint,endJoint,distance=1.0):
	'''
	Calculate the pole vector position based on input arguments
	@param startJoint: The start joint of the ik chain
	@type startJoint: str
	@param midJoint: The middle joint of the ik chain
	@type midJoint: str
	@param endJoint: The end joint of the ik chain
	@type endJoint: str
	@param distance: The distance factor for the pole vector position based on chain length
	@type distance: float
	'''
	# Check joint
	if not mc.objExists(startJoint):
		raise Exception('Start joint "'+startJoint+'" does not exist!')
	if not mc.objExists(midJoint):
		raise Exception('Middle joint "'+midJoint+'" does not exist!')
	if not mc.objExists(endJoint):
		raise Exception('End joint "'+endJoint+'" does not exist!')
	
	# Get joint positions
	stPt = glTools.utils.base.getPosition(startJoint)
	mdPt = glTools.utils.base.getPosition(midJoint)
	enPt = glTools.utils.base.getPosition(endJoint)
	
	# Get Joint lengths
	stLen = glTools.utils.joint.length(startJoint)
	mdLen = glTools.utils.joint.length(midJoint)
	pvLen = glTools.utils.mathUtils.distanceBetween(stPt,enPt) * distance
	
	# Calculate center point
	wt = stLen/(stLen+mdLen)
	ctPt = glTools.utils.mathUtils.averagePosition(stPt,enPt,wt)
	
	# Calculate poleVector
	poleVec = glTools.utils.mathUtils.normalizeVector(glTools.utils.mathUtils.offsetVector(ctPt,mdPt))
	
	# Calculate poleVector position
	pvPt = [ctPt[0]+(poleVec[0]*pvLen),ctPt[1]+(poleVec[1]*pvLen),ctPt[2]+(poleVec[2]*pvLen)]
	
	# Return result
	return pvPt

def ikFkBlend(blendJoints,fkJoints,ikJoints,blendAttr,translate=True,rotate=True,scale=True,skipEnd=True,prefix=''):
	'''
	Setup IK/FK joint blending using blendColor nodes
	@param blendJoints: The joint chain to blend between IK and FK chains
	@type blendJoints: list
	@param fkJoints: Target FK joint chain
	@type fkJoints: list
	@param ikJoints: Target IK joint chain
	@type ikJoints: list
	@param blendAttr: FK to IK blend attribute
	@type blendAttr: str
	@param translate: Blend translate channels
	@type translate: bool
	@param rotate: Blend rotate channels
	@type rotate: bool
	@param scale: Blend scale channels
	@type scale: bool
	@param skipEnd: Skip chain end joint
	@type skipEnd: bool
	@param prefix: Name prefix for created nodes
	@type prefix: str
	'''
	# Check blend attribute
	if not mc.objExists(blendAttr):
		ctrl = blendAttr.split('.')[0]
		attr = blendAttr.split('.')[-1]
		if not mc.objExists(ctrl): raise Exception('Blend control "'+ctrl+'" does not exist!')
		mc.addAttr(ctrl,ln=attr,min=0,max=1,dv=0,k=True)
	
	# Check joint chains
	if (len(blendJoints) != len(fkJoints)) or (len(blendJoints) != len(ikJoints)):
		raise Exception('Chain length mis-match!!')
	
	# Check Skip End
	if skipEnd:
		blendJoints = blendJoints[:-1]
		fkJoints = fkJoints[:-1]
		ikJoints = ikJoints[:-1]
	
	# Blend Joint Translate/Rotate/Scale
	tBlendNode = ''
	rBlendNode = ''
	sBlendNode = ''
	
	for i in range(len(blendJoints)):
		
		# Naming index
		ind = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		
		# Translate
		if translate:
			
			# Create blend node
			tBlendNode = mc.createNode('blendColors',n=prefix+'_tr'+ind+'_blendColors')
			
			# Connect blend node
			mc.connectAttr(fkJoints[i]+'.tx',tBlendNode+'.color1R',f=True)
			mc.connectAttr(fkJoints[i]+'.ty',tBlendNode+'.color1G',f=True)
			mc.connectAttr(fkJoints[i]+'.tz',tBlendNode+'.color1B',f=True)
			mc.setAttr(tBlendNode+'.color2',0,0,0)
			mc.connectAttr(blendAttr,tBlendNode+'.blender',f=True)
			
			# Connect to joint
			mc.connectAttr(tBlendNode+'.outputR',blendJoints[i]+'.tx',f=True)
			mc.connectAttr(tBlendNode+'.outputG',blendJoints[i]+'.ty',f=True)
			mc.connectAttr(tBlendNode+'.outputB',blendJoints[i]+'.tz',f=True)
			
		# Rotate
		if rotate:
			
			# Create blend node
			rBlendNode = mc.createNode('blendColors',n=prefix+'_rt'+ind+'_blendColors')
			
			# Connect blend node
			mc.connectAttr(fkJoints[i]+'.rx',rBlendNode+'.color1R',f=True)
			mc.connectAttr(fkJoints[i]+'.ry',rBlendNode+'.color1G',f=True)
			mc.connectAttr(fkJoints[i]+'.rz',rBlendNode+'.color1B',f=True)
			mc.connectAttr(ikJoints[i]+'.rx',rBlendNode+'.color2R',f=True)
			mc.connectAttr(ikJoints[i]+'.ry',rBlendNode+'.color2G',f=True)
			mc.connectAttr(ikJoints[i]+'.rz',rBlendNode+'.color2B',f=True)
			mc.connectAttr(blendAttr,rBlendNode+'.blender',f=True)
			
			# Connect to joint
			mc.connectAttr(rBlendNode+'.outputR',blendJoints[i]+'.rx',f=True)
			mc.connectAttr(rBlendNode+'.outputG',blendJoints[i]+'.ry',f=True)
			mc.connectAttr(rBlendNode+'.outputB',blendJoints[i]+'.rz',f=True)
		
		# Scale
		if scale:
			
			# Create blend node
			sBlendNode = mc.createNode('blendColors',n=prefix+'_sc'+ind+'_blendColors')
			
			# Connect blend node
			mc.connectAttr(fkJoints[i]+'.sx',sBlendNode+'.color1R',f=True)
			mc.connectAttr(fkJoints[i]+'.sy',sBlendNode+'.color1G',f=True)
			mc.connectAttr(fkJoints[i]+'.sz',sBlendNode+'.color1B',f=True)
			mc.connectAttr(ikJoints[i]+'.sx',sBlendNode+'.color2R',f=True)
			mc.connectAttr(ikJoints[i]+'.sy',sBlendNode+'.color2G',f=True)
			mc.connectAttr(ikJoints[i]+'.sz',sBlendNode+'.color2B',f=True)
			mc.connectAttr(blendAttr,sBlendNode+'.blender',f=True)
			
			# Connect to joint
			mc.connectAttr(sBlendNode+'.outputR',blendJoints[i]+'.sx',f=True)
			mc.connectAttr(sBlendNode+'.outputG',blendJoints[i]+'.sy',f=True)
			mc.connectAttr(sBlendNode+'.outputB',blendJoints[i]+'.sz',f=True)
	
	# Return Result
	return [tBlendNode,rBlendNode,sBlendNode]

def ikFkMatch(ikFkAttr,limbEnd,prefix):
	'''
	'''
	# Get Current limb state
	ikFkState = mc.getAttr(ikFkAttr)
	
	# Get limb end details
	limbEndMatrix = glTools.utils.matrix.getMatrix(limbEnd,local=False)
	limbEndParent = mc.listRelatives(limbEnd,p=True,pa=True)[0]
	limbEndRotateOrder = mc.getAttr(limbEnd+'.ro')
	rotateOrderList = ['xyz','yzx','zxy','xzy','yxz','zyx']
	
	# Match IK/FK
	if ikFkState:
		
		# ==================
		# - Match IK to FK -
		# ==================
		
		# Calculate IK positions
		wristPt = glTools.utils.base.getPosition(prefix+'_fkEnd_jnt')
		poleVec = poleVectorPosition(prefix+'_fkA_jnt',prefix+'_fkB_jnt',prefix+'_fkEnd_jnt',distance=1.0)
		
		# Switch limb to FK
		mc.setAttr(ikFkAttr,1-ikFkState)
		
		# Set IK control positions
		mc.move(wristPt[0],wristPt[1],wristPt[2],prefix+'_ik_ctrl',ws=True,a=True)
		mc.move(poleVec[0],poleVec[1],poleVec[2],prefix+'_pv_ctrl',ws=True,a=True)
		
	else:
		
		# ==================
		# - Match FK to IK -
		# ==================
		
		# Get IK chain rotations
		rotA = mc.getAttr(prefix+'_ikA_jnt.r')[0]
		rotB = mc.getAttr(prefix+'_ikB_jnt.r')[0]
		
		# Switch limb to IK
		mc.setAttr(ikFkAttr,1-ikFkState)
		
		# Set FK chain rotations
		mc.setAttr(prefix+'_fkA_jnt.r',rotA[0],rotA[1],rotA[2])
		mc.setAttr(prefix+'_fkB_jnt.r',rotB[0],rotB[1],rotB[2])
		
	# Set limb end rotation
	limbEndParentMatrix = glTools.utils.matrix.getMatrix(limbEndParent,local=False)
	limbEndTargetMatrix = limbEndMatrix * limbEndParentMatrix.inverse()
	limbEndRotate = glTools.utils.matrix.getRotation(limbEndTargetMatrix,rotateOrderList[limbEndRotateOrder])
	mc.setAttr(limbEnd+'.r',limbEndRotate[0],limbEndRotate[1],limbEndRotate[2])
	
	# Reurn Result
	return 1-ikFkState

def createTwistJoints(joint,numTwistJoints,offsetAxis='x',prefix=''):
	'''
	'''
	# Check joint
	if not mc.objExists(joint):
		raise Exception('Joint '+joint+' does not exist!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(joint)
	
	# Get joint length
	jointEnd = mc.listRelatives(joint,c=True)[0]
	jointLen = mc.getAttr(jointEnd+'.t'+offsetAxis)
	jointOffset = jointLen/(numTwistJoints-1)
	
	# Create twist joints
	twistJoints = []
	for i in range(numTwistJoints):
		
		alphaInd = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		
		# Duplicate joint
		twistJoint = mc.duplicate(joint,po=True,n=prefix+'_twist'+alphaInd+'_jnt')[0]
		mc.parent(twistJoint,joint)
		
		# Position joint
		mc.setAttr(twistJoint+'.t'+offsetAxis,jointOffset*i)
		
		# Append twist joint list
		twistJoints.append(twistJoint)
	
	# Return result
	return twistJoints
	
def getAllCtrls(all='all'):
	'''
	'''
	# Check all exists
	if not mc.objExists(all):
		raise Exception('All node '+all+' does not exist!')
	
	# Get comtrols list
	return mc.getAttr(all+'.allCtrls')

def setAllCtrls(all='all',ctrlList=[],append=False):
	'''
	'''
	# Check all exists
	if not mc.objExists(all):
		raise Exception('All node '+all+' does not exist!')
	
	# Check All Controls Attribute
	if not mc.objExists(all+'.allCtrls'):
		mc.addAttr(all,ln='allCtrls',dt='string',multi=True,hidden=True)
	
	# Check append
	if append:
		allCtrls = getAllCtrls(all)
		allCtrls.extend(ctrlList)
		ctrlList = allCtrls
	
	# Set all controls attribute array values
	for i in range(len(ctrlList)):
		mc.setAttr(all+'.allCtrls['+str(i)+']',ctrlList[i],type='string')

def connectControlVis(ctrlLodAttr=['allTransA_ctrl.primaryCtrlVis','allTransA_ctrl.secondaryCtrlVis','allTransA_ctrl.tertiaryCtrlVis']):
	'''
	'''
	# Get Control List
	ctrlList = mc.ls('*.ctrlLod',o=True)
	ctrlList.sort()
	
	# Connect Control Visibility
	for ctrl in ctrlList:
		
		# Get Control Shapes
		ctrlShapes = mc.listRelatives(ctrl,s=True,type='nurbsCurve')
		if not ctrlShapes: continue
		
		# Get Control Lod
		ctrlLod = mc.getAttr(ctrl+'.ctrlLod')
		
		# Connect to Visibility
		for ctrlShape in ctrlShapes:
			
			# Check Existing Connections
			shapeVisConn = mc.listConnections(ctrlShape+'.v',s=True,d=False,p=True)
			if shapeVisConn:
				
				# Merge visibility inputs
				shapePrefix = glTools.utils.stringUtils.stripSuffix(ctrlShape)
				shapeVisNode = mc.createNode('multDoubleLinear',n=shapePrefix+'_allVis_multDoubleLinear')
				mc.connectAttr(shapeVisConn[0],shapeVisNode+'.input1',f=True)
				mc.connectAttr(ctrlLodAttr[ctrlLod],shapeVisNode+'.input2',f=True)
				mc.connectAttr(shapeVisNode+'.output',ctrlShape+'.v',f=True)
				
			else:
				
				# No existing connection - Direct connection 
				mc.connectAttr(ctrlLodAttr[ctrlLod],ctrlShape+'.v',f=True)

def connectLoresVis(toggleAttr='allTransA_ctrl.loGeoVis'):
	'''
	Connect lores geometry visibility to the specified visibility toggle attribute
	@param toggleAttr: Visibility toggle attribute
	@type toggleAttr: str
	'''
	# Check visibility toggle attribute
	if not mc.objExists(toggleAttr):
		raise Exception('Visibility toggle attribute "'+toggleAttr+'" does not exist!')
	
	# Get all joint list
	jointList = mc.ls(type='joint')
	if not jointList: return
	
	# Iterate over all joints
	for joint in jointList:
		
		# Get all joint mesh shapes
		allShapes = mc.listRelatives(joint,s=True,pa=True)
		if not allShapes: continue
		meshShapes = mc.ls(allShapes,type='mesh')
		if not meshShapes: continue
		
		# Connect mesh shape visibility to vis toggle attr
		for meshShape in meshShapes:
			mc.connectAttr(toggleAttr,meshShape+'.v',f=True)

def connectHiresVis(geo='geo_grp',toggleAttr='allTransA_ctrl.hiGeoVis'):
	'''
	Connect hires geometry visibility to the specified visibility toggle attribute
	@param toggleAttr: Visibility toggle attribute
	@type toggleAttr: str
	@param geo: Geometry (group) to toggle visibility for
	@type geo: str
	'''
	# Check geometry
	if not mc.objExists(geo):
		raise Exception('Geometry (group) "'+geo+'" does not exist!')
	
	# Check visibility toggle attribute
	if not mc.objExists(toggleAttr):
		raise Exception('Visibility toggle attribute "'+toggleAttr+'" does not exist!')
	
	# Connect Visibility
	mc.connectAttr(toggleAttr,geo+'.v',f=True)

def colourLoresGeo():
	'''
	Set default colouring for lores geometry,
	'''
	# Get all joint list
	jointList = mc.ls(type='joint')
	if not jointList: return
	
	# Iterate over all joints
	for joint in jointList:
		
		# Get all joint mesh shapes
		allShapes = mc.listRelatives(joint,s=True,pa=True)
		if not allShapes: continue
		meshShapes = mc.ls(allShapes,type='mesh')
		if not meshShapes: continue
		
		# Colour mesh shape
		for meshShape in meshShapes:
			
			mc.setAttr(meshShape+'.overrideEnabled',1)
			if joint.startswith('cn_'): mc.setAttr(meshShape+'.overrideColor',24)
			if joint.startswith('lf_'): mc.setAttr(meshShape+'.overrideColor',15)
			if joint.startswith('rt_'): mc.setAttr(meshShape+'.overrideColor',4)

def referenceLoresGeo():
	'''
	Set display type for lores geometry to referenced.
	'''
	# Get all joint list
	jointList = mc.ls(type='joint')
	if not jointList: return
	
	# Iterate over all joints
	for joint in jointList:
		
		# Get all joint mesh shapes
		allShapes = mc.listRelatives(joint,s=True,pa=True)
		if not allShapes: continue
		meshShapes = mc.ls(allShapes,type='mesh')
		if not meshShapes: continue
		
		# Colour mesh shape
		for meshShape in meshShapes:
			mc.setAttr(meshShape+'.overrideEnabled',1)
			mc.setAttr(meshShape+'.overrideDisplayType',2)
