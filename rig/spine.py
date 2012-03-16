import maya.cmds as mc

import glTools.utils.base
import glTools.utils.curve
import glTools.utils.joint
import glTools.utils.shape

import glTools.tools.controlBuilder
import glTools.tools.createAlongCurve
import glTools.tools.ikHandle
import glTools.tools.stretchyIkSpline

import glTools.rig.utils

def build(startJoint,endJoint,ikSwitchCtrl='',ikSwitchAttr='spineIk',ctrlScale=1.0,prefix='cn_spine'):
	'''
	Build spine rig base.
	@param startJoint: Start joint of the FK spine
	@type startJoint: str
	@param endJoint: End joint of the FK spine
	@type endJoint: str
	@param ikSwitchCtrl: Control to store the IK switch attribute
	@type ikSwitchCtrl: str
	@param ikSwitchAttr: IK switch attribute
	@type ikSwitchAttr: str
	@param prefix: Name prefix for new nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(startJoint):
		raise Exception('Start joint "'+startJoint+'" does not exist!')
	if not mc.objExists(endJoint):
		raise Exception('End joint "'+endJoint+'" does not exist!')
	if ikSwitchCtrl and not mc.objExists(ikSwitchCtrl):
		raise Exception('IK switch control "'+ikSwitchCtrl+'" does not exist!')
	
	# ===================
	# - Configure Spine -
	# ===================
	
	# Control Scale
	fkCtrlScale = 1.5 * ctrlScale
	spineCtrlScale = 1 * ctrlScale
	
	# ==========================
	# - Build Module Structure -
	# ==========================
	
	# Create control group
	ctrl_grp = mc.group(em=True,n=prefix+'_ctrl_grp',w=True)
	
	# Create rig group
	rig_grp = mc.group(em=True,n=prefix+'_rig_grp',w=True)
	
	# Create skel group
	skel_grp = mc.group(em=True,n=prefix+'_skel_grp',w=True)
	
	# Create module group
	module = mc.group(em=True,n=prefix+'_module')
	mc.parent([ctrl_grp,rig_grp,skel_grp],module)
	
	# - Uniform Scale -
	mc.addAttr(module,ln='uniformScale',min=0.001,dv=1.0)
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleX')
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleY')
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleZ')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleX')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleY')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleZ')
	
	# =========================
	# - Determine Joint Scale -
	# =========================
	
	# Get joint list
	spineJnts = glTools.utils.joint.getJointList(startJoint,endJoint)
	jntLen = 0.0
	for jnt in spineJnts:
		cJntLen = glTools.utils.joint.length(jnt)
		if cJntLen > jntLen: jntLen = cJntLen
	
	# =====================
	# - Create FK Joints -
	# =====================
	
	# Create Joints
	fkJnts = glTools.utils.joint.duplicateChain(startJoint,endJoint,prefix=prefix+'_fk')
	
	# Create Control Shapes
	fkJntGrps = []
	fkJntShapes = []
	for i in range(len(fkJnts)-1):
		# Add control shape
		jntShape = glTools.tools.controlBuilder.controlShape(fkJnts[i],'circle',rotate=[0,90,0],scale=jntLen*fkCtrlScale)
		# Add joint buffer
		jntGrp = glTools.utils.joint.group(fkJnts[i])
		# Tag controls
		glTools.rig.utils.tagCtrl(fkJnts[i],'primary')
		# Append arrays
		fkJntGrps.append(jntGrp)
		fkJntShapes.extend(jntShape)
	
	# =======================
	# - Create Spine Joints -
	# =======================
	
	# For each joint
	spineJntGrps = []
	spineJntShapes = []
	for i in range(len(spineJnts)):
		# Add control curves
		jntShape = glTools.tools.controlBuilder.controlShape(spineJnts[i],'square',rotate=[0,90,0],scale=jntLen*spineCtrlScale)
		# Add joint buffer
		jntGrp = glTools.utils.joint.group(spineJnts[i])
		# Tag controls
		glTools.rig.utils.tagCtrl(spineJnts[i],'primary')
		# Append arrays
		spineJntGrps.append(jntGrp)
		spineJntShapes.extend(jntShape)
	
	# =======================
	# - Parent Spine Joints -
	# =======================
	
	for i in range(len(spineJnts)): mc.parent(spineJntGrps[i],fkJnts[i])
	
	# =======================
	# - Create Attach Joint -
	# =======================
	
	mc.select(cl=True)
	
	# Create attach
	attachJoint = mc.joint(n=prefix+'_attachA_jnt')
	attachJointGrp = glTools.utils.joint.group(attachJoint)
	mc.delete(mc.parentConstraint(spineJnts[0],attachJointGrp))
	
	# Attach joint display
	mc.setAttr(attachJoint+'.overrideEnabled',1)
	mc.setAttr(attachJoint+'.overrideLevelOfDetail',1)
	
	# Parent attach joint
	mc.parent(fkJntGrps[0],attachJoint)
	mc.parent(attachJointGrp,skel_grp)
	
	# ========================
	# - Setup IK Mode Switch -
	# ========================
	
	if ikSwitchCtrl:
		
		# Check switch attribute
		if not ikSwitchAttr: ikSwitchAttr = 'spineIk'
		if not mc.objExists(ikSwitchCtrl+'.'+ikSwitchAttr):
			mc.addAttr(ikSwitchCtrl,ln=ikSwitchAttr,at='long',min=0,max=1,dv=0,k=True)
		
		# Create Parent Constraints
		ikConstraint1 = mc.parentConstraint([spineJnts[0],spineJnts[-1]],spineJntGrps[1],mo=True)[0]
		ikConstraint2 = mc.parentConstraint([spineJnts[0],spineJnts[-1]],spineJntGrps[2],mo=True)[0]
		
		# Connect to switch
		ikWeightMult1 = mc.createNode('multDoubleLinear',n=prefix+'_ikWeight1_multDoubleLinear')
		ikWeightMult2 = mc.createNode('multDoubleLinear',n=prefix+'_ikWeight1_multDoubleLinear')
		mc.connectAttr(ikSwitchCtrl+'.'+ikSwitchAttr,ikWeightMult1+'.input1')
		mc.connectAttr(ikSwitchCtrl+'.'+ikSwitchAttr,ikWeightMult2+'.input1')
		mc.setAttr(ikWeightMult1+'.input2',0.666)
		mc.setAttr(ikWeightMult2+'.input2',0.333)
		
		# Connect to constraint
		ikWeightAlias1 = mc.parentConstraint(ikConstraint1,q=True,wal=True)
		ikWeightAlias2 = mc.parentConstraint(ikConstraint2,q=True,wal=True)
		mc.connectAttr(ikWeightMult1+'.output',ikConstraint1+'.'+ikWeightAlias1[0],f=True)
		mc.connectAttr(ikWeightMult2+'.output',ikConstraint1+'.'+ikWeightAlias1[1],f=True)
		mc.connectAttr(ikWeightMult1+'.output',ikConstraint2+'.'+ikWeightAlias1[1],f=True)
		mc.connectAttr(ikWeightMult2+'.output',ikConstraint2+'.'+ikWeightAlias1[0],f=True)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=spineJnts)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=spineJntGrps)
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=fkJnts)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=fkJntGrps)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[attachJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=[attachJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[module,ctrl_grp,rig_grp,skel_grp])
	
	# =================
	# - Return Result -
	# =================
	
	return [module,attachJoint]

def initializeRibbonSpine(startJoint,endJoint,numJoints,spans,prefix='cn_spine'):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(startJoint):
		raise Exception('Start joint "'+startJoint+'" does not exist!')
	if not mc.objExists(endJoint):
		raise Exception('End joint "'+endJoint+'" does not exist!')
	
	# =====================
	# - Build Spine Curve -
	# =====================
	
	# Get Spine Joint List
	spineJnts = glTools.utils.joint.getJointList(startJoint,endJoint)
	
	# Build Spine Locators
	locList = []
	for i in range(len(spineJnts)):
		
		pt = glTools.utils.base.getPosition(spineJnts[i])
		strInd = glTools.utils.stringUtils.alphaIndex(i)
		loc = mc.spaceLocator(p=(0,0,0),n=prefix+strInd+'_loc')[0]
		mc.move(pt[0],pt[1],pt[2],loc,ws=True,a=True)
		mc.parent(loc,spineJnts[i])
		locList.append(loc)
	
	# Build Spine Curve
	spineCurve = glTools.utils.curve.createFromLocators(locList,degree=1,attach=True,prefix=prefix)
	spineCurveShape = mc.listRelatives(spineCurve,s=True,pa=True)[0]
	glTools.utils.shape.createIntermediate(spineCurveShape)
	
	# Rebuild Spine Curve
	if not spans: spans = len(spineJnts) - 1
	rebuildCrv = mc.rebuildCurve(spineCurve,ch=1,rpo=1,rt=0,end=1,kr=0,kcp=0,kep=1,kt=1,s=spans,d=3,tol=0)
	rebuildCrv = mc.rename(rebuildCrv[1],prefix+'A_rebuildCurve')
	
	# ================================
	# - Attach Joints to Spine Curve -
	# ================================
	
	ribbonJoints = []
	inc = 1.0 / (numJoints - 1)
	for i in range(numJoints):
		mc.select(cl=1)
		strInd = glTools.utils.stringUtils.alphaIndex(i)
		joint = mc.joint(n=prefix+'Ribbon'+strInd+'_jnt')
		glTools.utils.attach.attachToCurve(spineCurve,joint,uValue=inc*i,orient=False,prefix=prefix+'Ribbon'+strInd)
		ribbonJoints.append(joint)
	
	# =================
	# - Return Result -
	# =================
	
	return ribbonJoints

def buildRibbonSpine(startJoint,endJoint,ribbonJoints,spans=0,ikSwitchCtrl='',ikSwitchAttr='spineIk',ctrlScale=1.0,prefix='cn_spine'):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Ribbon Joints
	for jnt in ribbonJoints:
		if not mc.objExists(jnt):
			raise Exception('Ribbon joint "'+jnt+'" does not exist!')
		
	# ====================
	# - Build Spine Base -
	# ====================
	
	# Get Joint List
	spineJnts = glTools.utils.joint.getJointList(startJoint,endJoint)
	
	spine = build(startJoint,endJoint,ikSwitchCtrl,ikSwitchAttr,ctrlScale,prefix)
	spine_module = spine[0]
	spine_attach = spine[1]
	spine_rig_grp = prefix+'_rig_grp'
	
	# =========================
	# - Process Ribbon Joints -
	# =========================
	
	for ribbonJoint in ribbonJoints:
		
		# Delete incoming connections
		mc.delete(mc.listConnections(ribbonJoint,s=True,d=False))
	
	# ======================
	# - Build Spine Ribbon -
	# ======================
	
	locList = []
	lfLocList = []
	rtLocList = []
	
	# Create Ribbon Locators
	for i in range(len(spineJnts)):
		
		pt = glTools.utils.base.getPosition(spineJnts[i])
		strInd = glTools.utils.stringUtils.alphaIndex(i)
		loc = mc.spaceLocator(p=(0,0,0),n=prefix+strInd+'_loc')[0]
		lfLoc = mc.spaceLocator(p=(0.5,0,0),n=prefix+'_lf'+strInd+'_loc')[0]
		rtLoc = mc.spaceLocator(p=(-0.5,0,0),n=prefix+'_rt'+strInd+'_loc')[0]
		
		# Parent and position locators
		mc.parent([lfLoc,rtLoc],loc)
		mc.move(pt[0],pt[1],pt[2],loc,ws=True,a=True)
		mc.parent(loc,spineJnts[i])
		mc.setAttr(loc+'.v',0)
		
		# Append Lists
		locList.append(loc)
		lfLocList.append(lfLoc)
		rtLocList.append(rtLoc)
	
	# Create Loft Curves
	lfCurve = glTools.utils.curve.createFromLocators(lfLocList,degree=1,attach=True,prefix=prefix+'A')
	rtCurve = glTools.utils.curve.createFromLocators(rtLocList,degree=1,attach=True,prefix=prefix+'B')
	lfCurveShape = mc.listRelatives(lfCurve,s=True,pa=True)[0]
	rtCurveShape = mc.listRelatives(rtCurve,s=True,pa=True)[0]
	glTools.utils.shape.createIntermediate(lfCurveShape)
	glTools.utils.shape.createIntermediate(rtCurveShape)
	
	# Rebuild Loft Curves
	if not spans: spans = len(spineJnts) - 1
	lfRebuildCrv = mc.rebuildCurve(lfCurve,ch=1,rpo=1,rt=0,end=1,kr=0,kcp=0,kep=1,kt=1,s=spans,d=3,tol=0)
	rtRebuildCrv = mc.rebuildCurve(rtCurve,ch=1,rpo=1,rt=0,end=1,kr=0,kcp=0,kep=1,kt=1,s=spans,d=3,tol=0)
	lfRebuildCrv = mc.rename(lfRebuildCrv[1],prefix+'A_rebuildCurve')
	rtRebuildCrv = mc.rename(rtRebuildCrv[1],prefix+'B_rebuildCurve')
	
	# Generate Loft Surface
	loft = mc.loft([lfCurve,rtCurve],d=1,n=prefix+'_surface')
	loftNode = mc.rename(loft[1],prefix+'_loft')
	spineSurface = loft[0]
	rebuildSrf = mc.rebuildSurface(spineSurface,ch=True,rpo=True,end=True,rt=0,kr=0,kcp=True,dir=2,du=1,dv=3)
	rebuildSrf = mc.rename(rebuildSrf[1],prefix+'_rebuildSurface')
	
	# Parent to rig group
	ribbonParts = [lfCurve,rtCurve,spineSurface]
	for ribbonPart in ribbonParts:
		mc.setAttr(ribbonPart+'.v',0)
		mc.parent(ribbonPart,spine_rig_grp)
	
	# ========================
	# - Attach Ribbon Joints -
	# ========================
	
	inc = 1.0 / (len(ribbonJoints) - 1)
	ribbonJointGrps = []
	for i in range(len(ribbonJoints)):
		
		# Create Joint Buffer Group
		strInd = glTools.utils.stringUtils.alphaIndex(i)
		prefix = glTools.utils.stringUtils.stripSuffix(ribbonJoints[i])
		mc.select(cl=True)
		ribbonJointGrp = mc.joint(n=prefix+'ConA_jnt')
		mc.delete(mc.pointConstraint(ribbonJoints[i],ribbonJointGrp))
		ribbonJointGrps.append(ribbonJointGrp)
		
		# Attach Joint Buffer Group
		glTools.utils.attach.attachToSurface(spineSurface,ribbonJointGrp,useClosestPoint=True,orient=True,uAxis='y',vAxis='x',uAttr='uCoord',vAttr='vCoord',alignTo='v',prefix=prefix+strInd)
		
		# Parent Ribbon Joint
		mc.parent(ribbonJoints[i],ribbonJointGrp)
		mc.parent(ribbonJointGrp,spine_rig_grp)
		
		# Connect Module Scale
		mc.connectAttr(spine_module+'.uniformScale',ribbonJoints[i]+'.sx',f=True)
		mc.connectAttr(spine_module+'.uniformScale',ribbonJoints[i]+'.sy',f=True)
		mc.connectAttr(spine_module+'.uniformScale',ribbonJoints[i]+'.sz',f=True)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=locList)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=lfLocList)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=rtLocList)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[lfCurve,rtCurve,spineSurface])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=ribbonJoints)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=ribbonJointGrps)
	
	# =================
	# - Return Result -
	# =================
	
	return [spine_module,spine_attach]
	
def build_fkik(startJoint,endJoint,numJoints=6,scaleAttr='',blendCtrl='',blendAttr='stretchScale',prefix='cn_spine'):
	'''
	Build a hybrid FK/IK spine rig
	@param startJoint: Start joint of the FK spine
	@type startJoint: str
	@param endJoint: End joint of the FK spine
	@type endJoint: str
	@param numJoints: Number of IK spine joints
	@type numJoints: int
	@param scaleAttr: Global character scale attribute
	@type scaleAttr: str
	@param blendCtrl: Control to store the spine stretch scale attribute
	@type blendCtrl: str
	@param blendAttr: Spine stretch scale attribute name
	@type blendAttr: str
	@param prefix: Name prefix for new nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(startJoint):
		raise Exception('Start joint "'+startJoint+'" does not exist!')
	if not mc.objExists(endJoint):
		raise Exception('End joint "'+endJoint+'" does not exist!')
	if scaleAttr and not mc.objExists(scaleAttr):
		raise Exception('Scale attribute "'+scaleAttr+'" does not exist!')
	if blendCtrl and not mc.objExists(blendCtrl):
		raise Exception('Blend control "'+blendCtrl+'" does not exist!')
	
	# ===================
	# - Configure Spine -
	# ===================
	
	# IK curve
	fitRebuild = True
	curveSpans = 2
	rebuildSpans = numJoints
	
	# Joint orient
	sideVector = [1,0,0]
	
	# IK stretch
	parametric = True
	scaleAxis = 'x'
	crvMin = 0.0
	crvMax = 1.0
	
	# IK twist
	ikTwistUpVec = 3 # Positive Z
	
	# Control scale
	fkCtrlScale = 1
	ikCtrlScale = 0.5
	
	# ==========================
	# - Build Module Structure -
	# ==========================
	
	# Create control group
	ctrl_grp = mc.group(n=prefix+'_ctrl_grp',w=True)
	
	# Create rig group
	rig_grp = mc.group(n=prefix+'_rig_grp',w=True)
	
	# Create skel group
	skel_grp = mc.group(n=prefix+'_skel_grp',w=True)
	
	# Create module group
	module = mc.group([ctrl_grp,rig_grp,skel_grp],n=prefix+'_module')
	
	# - Uniform Scale -
	mc.addAttr(module,ln='uniformScale',min=0.001,dv=1.0)
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleX')
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleY')
	mc.connectAttr(module+'.uniformScale',ctrl_grp+'.scaleZ')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleX')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleY')
	mc.connectAttr(module+'.uniformScale',skel_grp+'.scaleZ')
	
	# =====================
	# - Create FK Joints -
	# =====================
	
	# Get joint list
	spineJnts = glTools.utils.joint.getJointList(startJoint,endJoint)
	
	# For each joint
	spineJntGrps = []
	for i in range(len(spineJnts)-1):
		# Calculate joint length
		jntLen = glTools.utils.joint.length(spineJnts[i])
		# Add control curves
		glTools.tools.controlBuilder.controlShape(spineJnts[i],'square',rotate=[0,90,0],scale=jntLen*fkCtrlScale)
		# Add joint buffer
		jntGrp = glTools.utils.joint.group(spineJnts[i])
		# Tag controls
		glTools.rig.utils.tagCtrl(spineJnts[i],'primary')
		# Append list
		spineJntGrps.append(jntGrp)
	
	# Parent to ctrl grp
	mc.parent(spineJntGrps,ctrl_grp)
	
	# ===================
	# - Create IK Curve -
	# ===================
	
	# Build curve
	spineCurve = glTools.utils.curve.createFromPointList(spineJnts,degree=3,prefix=prefix)
	spineCurve = mc.rebuildCurve(spineCurve,ch=False,d=3,s=curveSpans,fr=fitRebuild,rpo=True,kr=0)[0]
	
	# Create curve locators
	spineLocs = glTools.utils.curve.locatorCurve(spineCurve,controlPoints=[],locatorScale=0.05,local=False,freeze=True,prefix=prefix)
	
	# Create rebuild curve
	ikRebuildCrv = mc.rebuildCurve(spineCurve,ch=True,d=3,s=rebuildSpans,rpo=False,kr=0)
	ikCurve = mc.rename(ikRebuildCrv[0],prefix+'_ik_curve')
	ikRebuild = mc.rename(ikRebuildCrv[1],prefix+'_ik_rebuildCurve')
	
	# Get Spine Length
	spineLen = mc.arclen(ikCurve)
	
	# Parent Spine Curve
	mc.parent(spineCurve,ikCurve,rig_grp)
	
	# =========================
	# - Create Curve Controls -
	# =========================
	
	# Initialize control builder
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	
	# - Create controls -
	
	# Base
	baseCtrl = ctrlBuilder.create('circle',prefix+'_base_ctrl',rotate=[90,0,0],scale=spineLen*ikCtrlScale)
	baseCtrlGrp = glTools.utils.base.group(baseCtrl,name=prefix+'_base_ctrlGrp')
	glTools.rig.utils.tagCtrl(baseCtrl,'primary')
	
	# Mid
	midCtrl = ctrlBuilder.create('circle',prefix+'_mid_ctrl',rotate=[90,0,0],scale=spineLen*ikCtrlScale)
	midCtrlGrp = glTools.utils.base.group(midCtrl,name=prefix+'_mid_ctrlGrp')
	glTools.rig.utils.tagCtrl(midCtrl,'primary')
	
	# Top
	topCtrl = ctrlBuilder.create('circle',prefix+'_top_ctrl',rotate=[90,0,0],scale=spineLen*ikCtrlScale)
	topCtrlGrp = glTools.utils.base.group(topCtrl,name=prefix+'_top_ctrlGrp')
	glTools.rig.utils.tagCtrl(topCtrl,'primary')
	
	# Position controls
	pt = glTools.utils.base.getPosition(spineLocs[0])
	mc.move(pt[0],pt[1],pt[2],baseCtrl,ws=True,a=True)
	pt = glTools.utils.base.getPosition(spineLocs[2])
	mc.move(pt[0],pt[1],pt[2],midCtrl,ws=True,a=True)
	pt = glTools.utils.base.getPosition(spineLocs[-1])
	mc.move(pt[0],pt[1],pt[2],topCtrl,ws=True,a=True)
	
	# Parent curve locators to controls
	mc.parent(spineLocs[:2],baseCtrl)
	mc.parent(spineLocs[2],midCtrl)
	mc.parent(spineLocs[3:],topCtrl)
	
	# Parent controls
	mc.parent(baseCtrlGrp,spineJnts[0])
	mc.parent(midCtrlGrp,spineJnts[1])
	mc.parent(topCtrlGrp,spineJnts[2])
	
	# ====================
	# - Create IK Joints -
	# ====================
	
	# Create spine joints
	ikJnts = glTools.tools.createAlongCurve.create(curve=ikCurve,objType='joint',objCount=numJoints,parent=True,useDistance=True,minPercent=0.0,maxPercent=1.0,prefix=prefix+'_ik',suffix='jnt')
	# Orient Joints
	for jnt in ikJnts: glTools.utils.joint.orient(jnt,aimAxis='x',upAxis='z',upVec=sideVector)
	
	# ==========================
	# - Create Spine Top Joint -
	# ==========================
	
	# Create joint
	spineTopJoint = mc.joint(n=prefix+'_topA_jnt')
	spineTopJointGrp = glTools.utils.joint.group(spineTopJoint)
	
	# Attach joint
	mc.pointConstraint(ikJnts[-1],spineTopJointGrp,mo=False)
	mc.orientConstraint(topCtrl,spineTopJointGrp,mo=False)
	
	# =======================
	# - Create Attach Joint -
	# =======================
	
	mc.select(cl=True)
	
	# Create attach
	attachJoint = mc.joint(n=prefix+'_attachA_jnt')
	attachJointGrp = glTools.utils.joint.group(attachJoint)
	mc.delete(mc.parentConstraint(spineJnts[0],attachJointGrp))
	
	# Attach joint display
	mc.setAttr(attachJoint+'.overrideEnabled',1)
	mc.setAttr(attachJoint+'.overrideLevelOfDetail',1)
	
	# Parent attach joint
	mc.parent([ikJnts[0],spineTopJointGrp],attachJoint)
	mc.parent(attachJointGrp,skel_grp)
	
	# ====================
	# - Create IK Handle -
	# ====================
	
	# Create ikHandle
	ikHandle = glTools.tools.ikHandle.build(ikJnts[0],ikJnts[-1],solver='ikSplineSolver',curve=ikCurve,ikSplineOffset=0.0,prefix=prefix)
	ikStretch = glTools.tools.stretchyIkSpline.stretchyIkSpline(ikHandle,parametric=parametric,scaleAxis=scaleAxis,scaleAttr=scaleAttr,blendControl=blendCtrl,blendAttr=blendAttr,minPercent=crvMin,maxPercent=crvMax,prefix=prefix)
	ikHandleGrp = glTools.utils.base.group(ikHandle,name=ikHandle+'Grp')
	
	# Setup ikHandle Twist
	mc.setAttr(ikHandle+'.dTwistControlEnable',1)
	mc.setAttr(ikHandle+'.dWorldUpType',4) # Object Rotation Up
	mc.setAttr(ikHandle+'.dWorldUpAxis',ikTwistUpVec)
	mc.connectAttr(baseCtrl+'.worldMatrix[0]',ikHandle+'.dWorldUpMatrix',f=True)
	mc.connectAttr(topCtrl+'.worldMatrix[0]',ikHandle+'.dWorldUpMatrixEnd',f=True)
	mc.setAttr(ikHandle+'.dWorldUpVector',sideVector[0],sideVector[1],sideVector[2])
	mc.setAttr(ikHandle+'.dWorldUpVectorEnd',sideVector[0],sideVector[1],sideVector[2])
	
	# Parent ikHandle
	mc.parent(ikHandleGrp,rig_grp)
	
	# ======================
	# - Set Channel States -
	# ======================
	
	chStateUtil = glTools.utils.channelState.ChannelState()
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=spineJnts)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=spineJntGrps)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=spineLocs)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[spineCurve,ikCurve])
	chStateUtil.setFlags([0,0,0,0,0,0,0,0,0,1],objectList=[baseCtrl,midCtrl,topCtrl])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[baseCtrlGrp,midCtrlGrp,topCtrlGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=ikJnts)
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[attachJointGrp])
	chStateUtil.setFlags([1,1,1,1,1,1,1,1,1,1],objectList=[attachJoint])
	chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=[module,ctrl_grp,rig_grp,skel_grp])
	
	# =================
	# - Return Result -
	# =================
	
	# Define control list
	ctrlList = spineJnts[:-1]
	ctrlList.append(baseCtrl)
	ctrlList.append(midCtrl)
	ctrlList.append(topCtrl)
	
	return [module,attachJoint]
