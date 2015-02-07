import maya.cmds as mc

import glTools.utils.channelState
import glTools.utils.defaultAttrState

import glTools.utils.attribute
import glTools.utils.base
import glTools.utils.cleanup
import glTools.utils.colorize
import glTools.utils.component
import glTools.utils.connection
import glTools.utils.deformer
import glTools.utils.joint
import glTools.utils.mathUtils
import glTools.utils.matrix
import glTools.utils.mesh
import glTools.utils.namespace
import glTools.utils.primvar
import glTools.utils.reference
import glTools.utils.selection
import glTools.utils.shape
import glTools.utils.skinCluster
import glTools.utils.stringUtils
import glTools.utils.transform

import types
import ast

def tagCtrl(control,ctrlLod='primary',module=None,category=None):
	'''
	Tag transform with control data. Also sets the "rotateOrder" attribute as keyable.
	@param control: Control to tag
	@type control: str
	@param ctrlLod: Control LOD. Valid values include "primary", "secondary", "tertiary" and "costume".
	@type ctrlLod: str
	@param module: Control module. If empty, module attribute is skipped.
	@type module: str or None
	@param category: Control category classification. Used to specify general purpose multi module class groupings (ie "face"). If empty, module attribute is skipped.
	@type category: str or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Control
	if not mc.objExists(control):
		raise Exception('Control object "'+control+'" does not exist!')
		
	# Check Control LOD
	ctrlLodList = ['primary','secondary','tertiary','allTrans','face','costume','hair','prop','misc']
	if not ctrlLod in ctrlLodList: raise Exception('Invalid control LOD "'+ctrlLod+'"!')
	ctrlLodIndex = ctrlLodList.index(ctrlLod)
	
	# ===================
	# - Tag Control LOD -
	# ===================
	
	lodAttr = 'ctrlLod'
	if not mc.objExists(control+'.'+lodAttr):
		mc.addAttr(control,ln=lodAttr,at='enum',en=':'.join(ctrlLodList))
	mc.setAttr(control+'.'+lodAttr,ctrlLodIndex)
	
	# ======================
	# - Tag Control Module -
	# ======================
	
	if module:
		moduleAttr = 'ctrlModule'
		if not mc.objExists(control+'.'+moduleAttr):
			mc.addAttr(control,ln=moduleAttr,dt='string')
		else:
			mc.setAttr(control+'.'+moduleAttr,l=False)
		mc.setAttr(control+'.'+moduleAttr,module,type='string')
		mc.setAttr(control+'.'+moduleAttr,l=True)
	
	# ========================
	# - Tag Control Category -
	# ========================
	
	if category:
		categoryAttr = 'ctrlCategory'
		if not mc.objExists(control+'.'+categoryAttr):
			mc.addAttr(control,ln=categoryAttr,dt='string')
		mc.setAttr(control+'.'+categoryAttr,category,type='string')
		mc.setAttr(control+'.'+categoryAttr,l=True)
	
	# =================
	# - Clean Control -
	# =================
	
	# Set Rotate Order Keyable
	try: mc.setAttr(control+'.ro',cb=True)
	except: pass
	
	# Hide Joint Attrs
	if mc.objExists(control+'.radius'): mc.setAttr(control+'.radius',k=False,cb=False)
	if mc.objExists(control+'.liw'): mc.setAttr(control+'.liw',k=False,cb=False)
	
	# =================
	# - Return Result -
	# =================
	
	return control

def tagBindJoint(joint,bind=True):
	'''
	Tag joint as a skinCluster influence.
	@param joint: Joint to tag and bind influence
	@type joint: str
	@param bind: Bind state.
	@type bind: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	if mc.objectType(joint) != 'joint':
		raise Exception('Object "'+joint+'" is not a valid joint!')
	
	# =============
	# - Tag Joint -
	# =============
	
	if not mc.objExists(joint+'.bindJoint'):
		mc.addAttr(joint,ln='bindJoint',at='bool',dv=True)
	
	# ===============
	# - Clean Joint -
	# ===============
	
	if mc.objExists(joint+'.radius'):
		mc.setAttr(joint+'.radius',k=False,cb=False)
	if mc.objExists(joint+'.liw'):
		mc.setAttr(joint+'.liw',k=False,cb=False)

def offsetGroup(	ctrl,
					pivot		= None,
					orientTo	= None,
					prefix		= None ):
	'''
	Create offset group node.
	Optionally, set custom pivot and orientation.
	@param ctrl: Control or control group to create offset group for.
	@type ctrl: str
	@param pivot: Transform for pivot match. If None, use control pivot.
	@type pivot: str or None
	@param orientTo: Transform for orient match. If None, use world orientation.
	@type orientTo: str or None
	@param prefix: Naming prefix.
	@type prefix: str or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Control
	if not mc.objExists(ctrl):
		raise Exception('Control "'+ctrl+'" does not exist!')
	
	# Pivot
	if not pivot: pivot = ctrl
	if not mc.objExists(pivot):
		raise Exception('Pivot "'+pivot+'" does not exist!')
	
	# Orient To
	if orientTo:
		if not mc.objExists(orientTo):
			raise Exception('Orient target "'+orientTo+'" does not exist!')
	
	# Prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(ctrl)
	
	# ======================
	# - Build Offset Group -
	# ======================
	
	# Create Offset Group
	offsetGrp = mc.group(em=True,n=prefix+'_offsetGrp')
	
	# Set Pivot
	piv = mc.xform(pivot,q=True,ws=True,rp=True)
	mc.xform(offsetGrp,ws=True,piv=piv)
	
	# Orient Offset Group
	if orientTo: mc.delete(mc.orientConstraint(orientTo,offsetGrp))
	
	# Parent Control
	mc.parent(ctrl,offsetGrp)
	
	# =================
	# - Return Result -
	# =================
	
	return offsetGrp

def negateTransform(	ctrl,
						negateGrp	= None,
						translate	= False,
						rotate		= False,
						scale		= False,
						prefix		= None ):
	'''
	Setup transform negation node network.
	@param ctrl: Control to create transform negation for.
	@type ctrl: str
	@param negateGrp: Negate transform. If None, create group from control.
	@type negateGrp: str or None
	@param translate: Negate transform translate.
	@type translate: bool
	@param rotate: Negate transform rotate.
	@type rotate: bool
	@param scale: Negate transform scale.
	@type scale: bool
	@param prefix: Naming prefix.
	@type prefix: str or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Control
	if not mc.objExists(ctrl):
		raise Exception('Control "'+ctrl+'" does not exist!')
	
	# Negate Group
	if negateGrp:
		if not mc.objExists(negateGrp):
			raise Exception('Control "'+ctrl+'" does not exist!')
	
	# Prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(ctrl)
	
	# ======================
	# - Build Negate Group -
	# ======================
	
	if not negateGrp:
		negateGrp = mc.duplicate(ctrl,po=True,n=prefix+'_negate')[0]
		glTools.utils.attribute.deleteUserAttrs(negateGrp)
		mc.parent(ctrl,negateGrp)
	
	# ======================
	# - Build Negate Nodes -
	# ======================
	
	if translate:
		tNegate = mc.createNode('multiplyDivide',n=prefix+'_translateNegate_multiplyDivide')
		mc.connectAttr(ctrl+'.t',tNegate+'.input1',f=True)
		mc.setAttr(tNegate+'.input2',-1,-1,-1)
		mc.connectAttr(tNegate+'.output',negateGrp+'.t',f=True)
	
	if rotate:
		rNegate = mc.createNode('multiplyDivide',n=prefix+'_rotateNegate_multiplyDivide')
		mc.connectAttr(ctrl+'.r',rNegate+'.input1',f=True)
		mc.setAttr(rNegate+'.input2',-1,-1,-1)
		mc.connectAttr(rNegate+'.output',negateGrp+'.r',f=True)
		
		# Reverse Rotate Order
		rotOrderMap = [5,3,4,1,2,0]
		mc.setAttr(negateGrp+'.ro',rotOrderMap[mc.getAttr(ctrl+'.ro')])
	
	if scale:
		sNegate = mc.createNode('multiplyDivide',n=prefix+'_scaleNegate_multiplyDivide')
		mc.connectAttr(ctrl+'.s',sNegate+'.input2',f=True)
		mc.setAttr(sNegate+'.input1',1,1,1)
		mc.setAttr(sNegate+'.operation',2) # Divide
		mc.connectAttr(sNegate+'.output',negateGrp+'.s',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return negateGrp

def lockJointAttrs(jointList=[]):
	'''
	Lock joint attributes on the specified list of joints
	@param jointList: List of joints to lock joint attributes on.
	@type jointList: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not jointList: jointList = mc.ls(type='joint') or []
	
	# =========================
	# - Lock Joint Attributes -
	# =========================
	
	for joint in jointList:
		
		# Lock Joint Orient
		if mc.getAttr(joint+'.jointOrient',se=True):
			mc.setAttr(joint+'.jointOrient',l=True)
		
		# Lock Preferred Angle Attr
		if mc.getAttr(joint+'.preferredAngle',se=True):
			mc.setAttr(joint+'.preferredAngle',l=True)
	
	# =================
	# - Return Result -
	# =================
	
	return jointList

def setToDefault(ctrl):
	'''
	Set the attributes of the specified control to default values
	@param ctrl: The control to set default attribute values for
	@type ctrl: str
	'''
	# =================
	# - Check Control -
	# =================
	
	if not mc.objExists(ctrl):
		raise Exception('Control "'+ctrl+'" does not exist!')
	
	# ==============================
	# - Define Transform Constants -
	# ==============================
	
	tAttr = ['tx','ty','tz']
	rAttr = ['rx','ry','rz']
	sAttr = ['sx','sy','sz']
	
	# =======================
	# - Get User Attributes -
	# =======================
	
	udAttr = mc.listAttr(ctrl,ud=True,k=True)
	if not udAttr: udAttr = []
	cbAttr = mc.listAttr(ctrl,ud=True,cb=True)
	if not cbAttr: cbAttr = []
	
	# =====================
	# - Reset to Defaults -
	# =====================
	
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
	for attr in cbAttr:
		dv = mc.addAttr(ctrl+'.'+attr,q=True,dv=True)
		if mc.getAttr(ctrl+'.'+attr,se=True):
			mc.setAttr(ctrl+'.'+attr,dv)

def isCtrlZeroed(ctrl,tol=0.00001,skipLocked=True,skipNonkeyable=False,verbose=False):
	'''
	Check the attributes of the specified control are set to default values.
	@param ctrl: The control to check default attribute values on.
	@type ctrl: str
	@param tol: The tolerance within which the current value must be to the default value to be considered as zeroed.
	@type tol: float
	@param skipLocked: Skip locked or connected channels.
	@type skipLocked: bool
	@param skipNonkeyable: Skip non-keyable channels.
	@type skipNonkeyable: bool
	@param verbose: Print details of which attribute was determined an not zeroed.
	@type verbose: bool
	'''
	# Check Control
	if not mc.objExists(ctrl):
		raise Exception('Control "'+ctrl+'" does not exist!')
	
	# Define standard transform controls
	tAttr = ['tx','ty','tz']
	rAttr = ['rx','ry','rz']
	sAttr = ['sx','sy','sz']
	
	# Get user defined attrs
	udAttr = mc.listAttr(ctrl,ud=True,k=True)
	if not udAttr: udAttr = []
	cbAttr = mc.listAttr(ctrl,ud=True,cb=True)
	if not cbAttr: cbAttr = []
	
	# ============================
	# - Check Attribute Defaults -
	# ============================
	
	# Translate
	for attr in tAttr:
		if not mc.getAttr(ctrl+'.'+attr,se=True) and skipLocked: continue
		if not mc.getAttr(ctrl+'.'+attr,k=True) and skipNonkeyable: continue
		if not glTools.utils.mathUtils.isEqual(mc.getAttr(ctrl+'.'+attr),0.0,tol):
			if verbose: print ('Attribute "'+ctrl+'.'+attr+'" is not zeroed ('+str(mc.getAttr(ctrl+'.'+attr))+')!')
			return False
	
	# Rotate
	for attr in rAttr:
		if not mc.getAttr(ctrl+'.'+attr,se=True) and skipLocked: continue
		if not mc.getAttr(ctrl+'.'+attr,k=True) and skipNonkeyable: continue
		if not glTools.utils.mathUtils.isEqual(mc.getAttr(ctrl+'.'+attr),0.0,tol):
			if verbose: print ('Attribute "'+ctrl+'.'+attr+'" is not zeroed ('+str(mc.getAttr(ctrl+'.'+attr))+')!')
			return False
	
	# Scale
	for attr in sAttr:
		if not mc.getAttr(ctrl+'.'+attr,se=True) and skipLocked: continue
		if not mc.getAttr(ctrl+'.'+attr,k=True) and skipNonkeyable: continue
		if not glTools.utils.mathUtils.isEqual(mc.getAttr(ctrl+'.'+attr),1.0,tol):
			if verbose: print ('Attribute "'+ctrl+'.'+attr+'" is not zeroed ('+str(mc.getAttr(ctrl+'.'+attr))+')!')
			return False
	
	# User Defined (Keyable)
	for attr in udAttr:
		if not mc.getAttr(ctrl+'.'+attr,se=True) and skipLocked: continue
		dv = mc.addAttr(ctrl+'.'+attr,q=True,dv=True)
		if not glTools.utils.mathUtils.isEqual(mc.getAttr(ctrl+'.'+attr),dv,tol):
			if verbose: print ('Attribute "'+ctrl+'.'+attr+'" is not zeroed ('+str(mc.getAttr(ctrl+'.'+attr))+')!')
			return False
	
	# Channel Box (Non-Keyable)
	if not skipNonkeyable:
		for attr in cbAttr:
			if not mc.getAttr(ctrl+'.'+attr,se=True) and skipLocked: continue
			dv = mc.addAttr(ctrl+'.'+attr,q=True,dv=True)
			if not glTools.utils.mathUtils.isEqual(mc.getAttr(ctrl+'.'+attr),dv,tol):
				if verbose: print ('Attribute "'+ctrl+'.'+attr+'" is not zeroed ('+str(mc.getAttr(ctrl+'.'+attr))+')!')
				return False
	
	# =================
	# - Return Result -
	# =================
	
	return True

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
	wt = stLen/(stLen+mdLen)
	
	# Calculate Center Point
	ctPt = glTools.utils.mathUtils.averagePosition(stPt,enPt,wt)
	
	# Calculate Pole Vector Offset
	pvOffset = glTools.utils.mathUtils.offsetVector(ctPt,mdPt)
	
	# Check Center Point Offset
	if glTools.utils.mathUtils.mag(pvOffset) < 0.001:
		stRotate = [i/abs(i) if (abs(i)>0) else 0 for i in mc.getAttr(startJoint+'.preferredAngle')[0]]
		mdRotate = [i/abs(i) if (abs(i)>0) else 0 for i in mc.getAttr(midJoint+'.preferredAngle')[0]]
		mc.setAttr(startJoint+'.r',*stRotate)
		mc.setAttr(midJoint+'.r',*mdRotate)
		mdPt = glTools.utils.base.getPosition(midJoint)
		enPt = glTools.utils.base.getPosition(endJoint)
		cnPt = glTools.utils.mathUtils.averagePosition(stPt,enPt,wt)
		pvOffset = glTools.utils.mathUtils.offsetVector(cnPt,mdPt)
		mc.setAttr(startJoint+'.r',0,0,0)
		mc.setAttr(midJoint+'.r',0,0,0)
	
	# Calculate poleVector
	poleVec = glTools.utils.mathUtils.normalizeVector(pvOffset)
	
	# Calculate poleVector position
	pvPt = [ctPt[0]+(poleVec[0]*pvLen),ctPt[1]+(poleVec[1]*pvLen),ctPt[2]+(poleVec[2]*pvLen)]
	
	# Return result
	return pvPt

def ikFkBlend(	blendJoints,
				fkJoints,
				ikJoints,
				blendAttr,
				translate = True,
				rotate = True,
				scale = True,
				skipEnd = True,
				useConstraints = False,
				prefix = ''):
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
	@param useConstraints: Use blended constraints instead of blendColor nodes for rotations
	@type useConstraints: bool
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
	
	# Blend Attribute Reverse
	blendRevNode = ''
	if useConstraints:
		blendRevNode = mc.createNode('reverse',n=prefix+'_blendAttr_reverse')
		mc.connectAttr(blendAttr,blendRevNode+'.inputX',f=True)
		mc.connectAttr(blendAttr,blendRevNode+'.inputY',f=True)
		mc.connectAttr(blendAttr,blendRevNode+'.inputZ',f=True)
	
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
			
			if useConstraints:
				
				# Create orientConstraint node
				rBlendNode = mc.orientConstraint(fkJoints[i],ikJoints[i],blendJoints[i],n=prefix+'_rt'+ind+'_orientConstraint')[0]
				rBlendAlias = mc.orientConstraint(rBlendNode,q=True,wal=True)
				mc.connectAttr(blendAttr,rBlendNode+'.'+rBlendAlias[0],f=True)
				mc.connectAttr(blendRevNode+'.outputY',rBlendNode+'.'+rBlendAlias[1],f=True)
				
			else:
				
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
			
			#if useConstraints:
			#	
			#	# Create scaleConstraint node
			#	sBlendNode = mc.scaleConstraint(fkJoints[i],ikJoints[i],blendJoints[i],n=prefix+'_sc'+ind+'_scaleConstraint')[0]
			#	sBlendAlias = mc.scaleConstraint(sBlendNode,q=True,wal=True)
			#	mc.connectAttr(blendAttr,sBlendNode+'.'+sBlendAlias[0],f=True)
			#	mc.connectAttr(blendRevNode+'.outputZ',sBlendNode+'.'+sBlendAlias[1],f=True)
			#	
			#else:
				
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
	Add a multi string attribute to a specified node to store a list of all rig control names
	@param all: The node to add the control name list atribute to. Generally, the top node of the rig. ("all") 
	@type all: str
	@param ctrlList: The list of control names to add to the multi string attribute.
	@type ctrlList: list
	@param append: Append to the mulit string attribute, if it already exists. Oterwise, replace.
	@type append: bool
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

def connectControlVisOld(ctrlLodAttr=['all.primaryCtrlVis','all.secondaryCtrlVis','all.tertiaryCtrlVis']):
	'''
	Connect tagged control shape visibility based on the specified list of source attributes.
	The control ".ctrlLod" attribute value is used as an index into the incoming source attribute list.
	@param ctrlLodAttr: List of visibility control source attributes.
	@type ctrlLodAttr: list
	'''
	# Get Control LOD node
	ctrlLodNode = mc.ls(ctrlLodAttr[0],o=True)[0]
	
	# Get Control List
	ctrlList = mc.ls('*.ctrlLod',o=True)
	ctrlList.sort()
	
	# Connect Control Visibility
	for ctrl in ctrlList:
		
		# Get Control Shapes
		ctrlShapes = mc.listRelatives(ctrl,s=True,ni=True,pa=True,type='nurbsCurve')
		if not ctrlShapes: continue
		
		# Get Control Lod
		ctrlLod = mc.getAttr(ctrl+'.ctrlLod')
		
		# Connect to Visibility
		for ctrlShape in ctrlShapes:
			
			# Check Existing Connections
			shapeVisConn = mc.listConnections(ctrlShape+'.v',s=True,d=False,skipConversionNodes=True)
			if shapeVisConn and not (shapeVisConn[0] == ctrlLodNode):
				
				# Double check intermediate visibility connection
				# !! This is a little more messy than I would like. But will keep until it breaks !! - (10/15/12)
				shapeVisConnCheck = mc.listConnections(shapeVisConn[0],s=True,d=False,skipConversionNodes=True,p=True)
				if not shapeVisConnCheck: shapeVisConnCheck = []
				for shapeVisNodeCheck in shapeVisConnCheck:
					if ctrlLodAttr.count(shapeVisNodeCheck):
						mc.delete(shapeVisConn[0])
				
				# Get connections with plug information
				shapeVisConn = mc.listConnections(ctrlShape+'.v',s=True,d=False,p=True)
				
				# Merge visibility inputs
				shapePrefix = glTools.utils.stringUtils.stripSuffix(ctrlShape)
				shapeVisNode = mc.createNode('multDoubleLinear',n=shapePrefix+'_allVis_multDoubleLinear')
				mc.connectAttr(shapeVisConn[0],shapeVisNode+'.input1',f=True)
				mc.connectAttr(ctrlLodAttr[ctrlLod],shapeVisNode+'.input2',f=True)
				mc.connectAttr(shapeVisNode+'.output',ctrlShape+'.v',f=True)
				
			else:
				
				# No existing connection - Direct connection 
				try: mc.connectAttr(ctrlLodAttr[ctrlLod],ctrlShape+'.v',f=True)
				except: pass

def connectControlVis(	ctrlList	= None,
						ctrlLodNode	= 'all',
						ctrlLodAttr	= ['primaryCtrlVis','secondaryCtrlVis','tertiaryCtrlVis'] ):
	'''
	Connect tagged control LOD visibility based on the specified list of source attributes.
	The control ".ctrlLod" attribute value is used as an index into the incoming source attribute list.
	@param ctrlList: List of controls to connect visibility for. If None, select by "ctrlLod" attribute.
	@type ctrlList: list
	@param ctrlLodNode: Control LOD toggle node.
	@type ctrlLodNode: str
	@param ctrlLodAttr: List of control LOD toggle attributes.
	@type ctrlLodAttr: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Control LOD Toggle Node
	if not mc.objExists(ctrlLodNode):
		raise Exception('Control LOD toggle node "'+ctrlLodNode+'" does not exist!')
	
	# Control List
	if not ctrlList: ctrlList = mc.ls('*.ctrlLod',o=True,r=True)
	
	# ==============================
	# - Connect Control Visibility -
	# ==============================
	
	for ctrl in ctrlList:
		
		# Get Control Lod
		if not mc.attributeQuery('ctrlLod',n=ctrl,ex=True): continue
		ctrlLod = mc.getAttr(ctrl+'.ctrlLod')
		if ctrlLod >= len(ctrlLodAttr): continue
		
		# Get Control Shapes
		ctrlShapes = mc.listRelatives(ctrl,s=True,ni=True,pa=True,type='nurbsCurve')
		
		# -------------------------------------------------------------------------------
		# !!! If No Shapes, Show Display Handle and LOD Override (Normal/BoundingBox) !!!
		# -------------------------------------------------------------------------------
		if not ctrlShapes:
			
			# Show Display Handle
			mc.setAttr(ctrl+'.displayHandle',True)
			
			# Get/Create LOD Switch Reverse Node
			rev = mc.ls(mc.listConnections(ctrlLodNode+'.'+ctrlLodAttr[ctrlLod],s=False,d=True) or [],type='reverse') or []
			if not rev:
				rev = mc.createNode('reverse',n=ctrlLodAttr[ctrlLod]+'_reverse')
				mc.connectAttr(ctrlLodNode+'.'+ctrlLodAttr[ctrlLod],rev+'.inputX',f=True)
			else: rev = rev[0]
			
			# Set/Connect Display Overrides
			mc.setAttr(ctrl+'.overrideEnabled',1)
			mc.connectAttr(rev+'.outputX',ctrl+'.overrideLevelOfDetail',f=True)
		
		# Connect Control Shape Visibility
		else:
			for ctrlShape in ctrlShapes:
				
				# Check Existing Connections
				lodVisConn = mc.listConnections(ctrlShape+'.lodVisibility',s=True,d=False)
				if lodVisConn:
					
					# Disconnect Attribute
					lodVisConn = mc.listConnections(ctrlShape+'.lodVisibility',s=True,d=False,p=True)
					mc.disconnectAttr(lodVisConn[0],ctrlShape+'.lodVisibility')
					
				# Connect LOD Visibility
				try: mc.connectAttr(ctrlLodNode+'.'+ctrlLodAttr[ctrlLod],ctrlShape+'.lodVisibility',f=True)
				except: print('Error connecting ctrl LOD attr to "'+ctrlShape+'.lodVisibility"!')
	
	# =================
	# - Return Result -
	# =================
	
	return ctrlList

def connectCostumeCtrlVis(	ctrlList	= None,
							ctrlVisNode	= 'all',
							ctrlVisAttr	= 'costumeCtrlVis',
							useCategory	= True ):
	'''
	Connect costume control visibility.
	@param ctrlList: List of controls to connect visibility for.
	@type ctrlList: list
	@param ctrlLodNode: Control LOD toggle node.
	@type ctrlLodNode: str
	@param ctrlLodAttr: List of control LOD toggle attributes.
	@type ctrlLodAttr: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Control Vis Toggle Node
	if not mc.objExists(ctrlVisNode):
		raise Exception('Visibility control toggle node "'+ctrlVisNode+'" does not exist!')
	
	# Control List
	if not ctrlList:
		if useCategory: ctrlList = mc.ls('*.ctrlCategory',o=True,r=True)
		else: ctrlList = mc.ls('*.ctrlLod',o=True,r=True)
	
	# ======================================
	# - Connect Costume Control Visibility -
	# ======================================
	
	# Add Control Attribute
	if not mc.attributeQuery(ctrlVisAttr,n=ctrlVisNode,ex=True):
		mc.addAttr(ctrlVisNode,ln=ctrlVisAttr,at='enum',en='Off:On',dv=0)
		mc.setAttr(ctrlVisNode+'.'+ctrlVisAttr,cb=True)
	
	# Connect Control Visibility
	for ctrl in ctrlList:
		
		ctrlTag = mc.getAttr(ctrl+'.ctrlLod')
		if useCategory: ctrlTag = mc.getAttr(ctrl+'.ctrlCategory')
		if ctrlTag != 'costume': continue
		
		# Connect Control Shapes
		ctrlShapes = mc.listRelatives(ctrl,s=True,ni=True,pa=True,type='nurbsCurve')
		for ctrlShape in ctrlShapes:
				
			# Check Existing Connections
			lodVisConn = mc.listConnections(ctrlShape+'.lodVisibility',s=True,d=False)
			if lodVisConn:
				# Disconnect Attribute
				lodVisConn = mc.listConnections(ctrlShape+'.lodVisibility',s=True,d=False,p=True)
				mc.disconnectAttr(lodVisConn[0],ctrlShape+'.lodVisibility')
				
			# Connect LOD Visibility
			try: mc.connectAttr(ctrlVisNode+'.'+ctrlVisAttr,ctrlShape+'.lodVisibility',f=True)
			except: print('Error connecting ctrl LOD attr to "'+ctrlShape+'.lodVisibility"!')
			
			# Print Msg
			print('Costume Control Shape "'+ctrlShape+'" connected to "'+ctrlVisNode+'.'+ctrlVisAttr+'"...')

def connectLoresVis(toggleAttr='all.loGeoVis'):
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

def connectVisOld(objList=[],toggleAttr='all.hiGeoVis',attrName='',defaultValue=0):
	'''
	Connect node visibility to the specified visibility toggle attribute
	@param objList: List of objects to toggle visibility for
	@type objList: list
	@param toggleAttr: Visibility toggle attribute
	@type toggleAttr: str
	@param attrName: Attribute nice name for UI
	@type attrName: str
	@param defaultValue: Default value for the visibility toggle attribute
	@type defaultValue: int
	'''
	#### DEPRECATED WARNING
	print('#### - DEPRECATED (glTools.rig.utils.connectVisOld) - ####')
	
	# Check Object List
	if type(objList) == str or type(objList) == unicode:
		objList = [str(objList)]
	for obj in objList:
		if not mc.objExists(obj):
			raise Exception('Object "'+obj+'" does not exist!')
	
	# Check Visibility Toggle Attribute
	if not mc.objExists(toggleAttr):
		node = toggleAttr.split('.')[0]
		if not mc.objExists(node):
			raise Exception('Visibility control node "'+node+'" does not exist!')
		attr = toggleAttr.split('.')[-1]
		mc.addAttr(node,ln=attr,nn=attrName,at='enum',en='Off:On',dv=defaultValue)
		mc.setAttr(node+'.'+attr,cb=True)
	else:
		mc.addAttr(toggleAttr,e=True,dv=defaultValue)
	
	# Connect Visibility
	for obj in objList:
		visConn = mc.listConnections(obj+'.v',s=True,d=False,p=True)
		if not visConn: visConn = []
		if not visConn.count(toggleAttr):
			try: mc.connectAttr(toggleAttr,obj+'.v',f=True)
			except: print 'Unable to connect "'+obj+'" visibility!'
	
	# Return Result
	return toggleAttr

def connectVis(	objList,
				toggleNode,
				toggleAttr,
				toggleName='',
				defaultValue=0,
				force=True,
				enumStr='Off:On'	):
	'''
	Connect node visibility to the specified visibility toggle node and attribute.
	If toggle attribute doesn't exist, a new enum attr of the specified name will be created.
	@param objList: List of objects to toggle visibility for
	@type objList: list
	@param toggleNode: Visibility toggle attribute
	@type toggleNode: str
	@param toggleAttr: Visibility toggle attribute
	@type toggleAttr: str
	@param toggleName: Attribute nice name for UI
	@type toggleName: str
	@param defaultValue: Default value for the visibility toggle attribute
	@type defaultValue: int
	@param force: Force visibility connection if incoming connection already exists.
	@type force: bool
	@param enumStr: Visibility toggle enum string.
	@type enumStr: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not objList: raise Exception('Invalid or empty object list argument! (objList)')
	if not toggleNode: raise Exception('Invalid or empty toggle node argument! (toggleNode)')
	if not toggleAttr: raise Exception('Invalid or empty toggle attribute argument! (toggleAttr)')
	
	# Check Object List
	if isinstance(objList,types.StringTypes):
		objList = [str(objList)]
	if not isinstance(objList,types.ListType):
		raise Exception('Invalid object list!')
	for obj in objList:
		if not mc.objExists(obj):
			raise Exception('Object "'+obj+'" does not exist!')
	
	# Check Toggle Node
	if not mc.objExists(toggleNode):
		raise Exception('Visibility control node "'+obj+'" does not exist!')
	
	# Check Toggle Name
	if not toggleName: toggleName = toggleAttr
	
	# Check Visibility Toggle Attribute
	if not mc.attributeQuery(toggleAttr,n=toggleNode,ex=True):
		mc.addAttr(toggleNode,ln=toggleAttr,nn=toggleName,at='enum',en=enumStr,dv=defaultValue)
		mc.setAttr(toggleNode+'.'+toggleAttr,cb=True)
	else:
		mc.addAttr(toggleNode+'.'+toggleAttr,e=True,nn=toggleName,dv=defaultValue)
	toggleNodeAttr = toggleNode+'.'+toggleAttr
	
	# ======================
	# - Connect Visibility -
	# ======================
	
	for obj in objList:
		
		# Check Incoming Connections
		nodeVisConn = mc.listConnections(obj+'.v',s=True,d=False)
		if nodeVisConn:
			if force:
				# Connect Visibility (Force Override)
				try: mc.connectAttr(toggleNodeAttr,obj+'.v',f=True)
				except: pass # print('Problem overriding visibility connection! ('+toggleNodeAttr+' >> '+obj+'.v)')
			else:
				raise Exception('Existing visibility connection already exists! Use force=True to override...')
		else:
			# Connect Visibility
			try: mc.connectAttr(toggleNodeAttr,obj+'.v',f=True)
			except: raise Exception('Problem connecting visibility! ('+toggleNodeAttr+' >> '+obj+'.v)')
	
	# =================
	# - Return Result -
	# =================
	
	return toggleNodeAttr

def connectDisplayTypeOld(objList,toggleAttr='all.meshDisplayType',defaultValue=0):
	'''
	Connect object display type to the specified enum attribute
	@param objList: List of objects to toggle display type for
	@type objList: list
	@param toggleAttr: Display type toggle attribute
	@type toggleAttr: str
	@param defaultValue: Default value for the visibility toggle attribute
	@type defaultValue: int
	'''
	#### DEPRECATED WARNING
	print('#### - DEPRECATED (glTools.rig.utils.connectDisplayTypeOld) - ####')
	
	# Check Object List
	if type(objList) == str or type(objList) == unicode:
		objList = [str(objList)]
	for obj in objList:
		if not mc.objExists(obj):
			raise Exception('Object "'+obj+'" does not exist!')
	
	# Check visibility toggle attribute
	if not mc.objExists(toggleAttr):
		node = toggleAttr.split('.')[0]
		if not node:
			raise Exception('Visibility control node "'+node+'" does not exist!')
		attr = toggleAttr.split('.')[-1]
		mc.addAttr(node,ln=attr,at='enum',en=':Normal:Template:Reference:',dv=defaultValue)
		mc.setAttr(node+'.'+attr,cb=True)
	else:
		mc.addAttr(toggleAttr,e=True,dv=defaultValue)
	
	# Connect Display Type
	for obj in objList:
		mc.setAttr(obj+'.overrideEnabled',1)
		try: mc.connectAttr(toggleAttr,obj+'.overrideDisplayType',f=True)
		except:
			objConn = mc.listConnections(obj+'.overrideDisplayType',s=True,d=False,p=True)
			if objConn.count(toggleAttr):
				print('Attribute "'+toggleAttr+'" is already connect to "'+obj+'.overrideDisplayType"! Skipping connectAttr...')
			else:
				print('Unable to connect "'+toggleAttr+'" to "'+obj+'.overrideDisplayType"!')
	
	# Return Result
	return toggleAttr

def connectDisplayType(	objList,
						toggleNode,
						toggleAttr,
						toggleName='',
						defaultValue=0,
						force=True,
						enumStr='Normal:Template:Reference'	):
	'''
	Connect object display type to the specified enum attribute
	@param objList: List of objects to toggle display type for
	@type objList: list
	@param toggleNode: Display type toggle node
	@type toggleNode: str
	@param toggleAttr: Display type toggle attribute name
	@type toggleAttr: str
	@param toggleName: Display type toggle attribute nice name for UI
	@type toggleName: str
	@param defaultValue: Default value for the display type toggle attribute
	@type defaultValue: int
	@param force: Force display type connection if incoming connection already exists.
	@type force: bool
	@param enumStr: Display type toggle enum string.
	@type enumStr: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not objList: raise Exception('Invalid or empty object list argument! (objList)')
	if not toggleNode: raise Exception('Invalid or empty toggle node argument! (toggleNode)')
	if not toggleAttr: raise Exception('Invalid or empty toggle attribute argument! (toggleAttr)')
	
	# Check Object List
	if isinstance(objList,types.StringTypes):
		objList = [str(objList)]
	if not isinstance(objList,types.ListType):
		raise Exception('Invalid object list!')
	for obj in objList:
		if not mc.objExists(obj):
			raise Exception('Object "'+obj+'" does not exist!')
	
	# Check Toggle Node
	if not mc.objExists(toggleNode):
		raise Exception('Display type control node "'+obj+'" does not exist!')
	
	# Check Toggle Name
	if not toggleName: toggleName = toggleAttr
	
	# Check Visibility Toggle Attribute
	if not mc.attributeQuery(toggleAttr,n=toggleNode,ex=True):
		mc.addAttr(toggleNode,ln=toggleAttr,nn=toggleName,at='enum',en=enumStr,dv=defaultValue)
		mc.setAttr(toggleNode+'.'+toggleAttr,cb=True)
	else:
		mc.addAttr(toggleNode+'.'+toggleAttr,e=True,nn=toggleName,dv=defaultValue)
	toggleNodeAttr = toggleNode+'.'+toggleAttr
	
	# ========================
	# - Connect Display Type -
	# ========================
	
	for obj in objList:
		
		# Enable Display Overrides
		mc.setAttr(obj+'.overrideEnabled',1)
		
		# Check Incoming Connections
		nodeDispAttr = 'overrideDisplayType'
		nodeDispConn = mc.listConnections(obj+'.'+nodeDispAttr,s=True,d=False)
		if nodeDispConn:
			if force:
				# Connect Display Type (Force Override)
				try: mc.connectAttr(toggleNodeAttr,obj+'.'+nodeDispAttr,f=True)
				except: pass # print('Problem overriding visibility connection! ('+toggleNodeAttr+' >> '+obj+'.'+nodeDispAttr+')')
			else:
				raise Exception('Existing display type connection already exists! Use force=True to override...')
		else:
			# Connect Visibility
			try: mc.connectAttr(toggleNodeAttr,obj+'.'+nodeDispAttr,f=True)
			except: raise Exception('Problem connecting visibility! ('+toggleNodeAttr+' >> '+obj+'.'+nodeDispAttr+')')
	
	# =================
	# - Return Result -
	# =================
	
	return toggleNodeAttr

def connectAttr(targetNode,targetAttr,sourceNode,sourceAttr,force=True):
	'''
	Connect specified source and target attributes
	@param targetNode: Target node
	@type targetNode: str
	@param targetAttr: Target attribute
	@type targetAttr: str
	@param sourceNode: Source node
	@type sourceNode: str
	@param sourceAttr: Source attribute
	@type sourceAttr: str
	@param force: Force connection if incoming connection already exists
	@type force: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not targetNode: raise Exception('Invalid or empty target node argument! (targetNode)')
	if not targetAttr: raise Exception('Invalid or empty target attribute argument! (targetAttr)')
	if not sourceNode: raise Exception('Invalid or empty source node argument! (sourceNode)')
	if not sourceAttr: raise Exception('Invalid or empty source attribute argument! (sourceAttr)')
	
	if not mc.objExists(targetNode): raise Exception('Target node "'+targetNode+'" does not exist!')
	if not mc.objExists(sourceNode): raise Exception('Source node "'+targetNode+'" does not exist!')
	if not mc.attributeQuery(targetAttr,n=targetNode,ex=True): raise Exception('Target attribute "'+targetNode+'.'+targetAttr+'" does not exist!')
	if not mc.attributeQuery(sourceAttr,n=sourceNode,ex=True): raise Exception('Source attribute "'+sourceNode+'.'+sourceAttr+'" does not exist!')
	
	sourceNodeAttr = sourceNode+'.'+sourceAttr
	targetNodeAttr = targetNode+'.'+targetAttr
	
	# Check Existing Connection to Target
	existingConn = mc.listConnections(targetNodeAttr,s=True,d=False,p=True) or []
	if existingConn:
		for srcConn in existingConn:
			print('Breaking existing connection - "'+srcConn+'" >< "'+targetNodeAttr+'"...')
			mc.disconnectAttr(srcConn,targetNodeAttr)
	
	# =====================
	# - Connect Attribute -
	# =====================
	
	try: mc.connectAttr(sourceNodeAttr,targetNodeAttr,f=force)
	except Exception, e:
		raise Exception('Error connecting attribute "'+sourceNodeAttr+'" >> "'+targetNodeAttr+'"! Exception Msg: '+str(e))
	else: print('Connecting attributes - "'+sourceNodeAttr+'" >> "'+targetNodeAttr+'"...')
	
	# =================
	# - Return Result -
	# =================
	
	return sourceNodeAttr,targetNodeAttr

def nonRenderableFaceSet(facelist,buildStandin=False):
	'''
	Define a list of faces to be ignored/deleted at render time.
	Creates a nonRenderable preview mesh with the specified polygon faces deleted.
	The original mesh is unchanged except for an ABC primvar attr that lists the face IDs to be ignored at render time.
	@param facelist: List of faces to ignore during render.
	@type facelist: list
	@param buildStandin: Build standin geometry with faces removed, set original visibility off.
	@type buildStandin: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	facelist = mc.filterExpand(facelist,sm=34)
	if not facelist: raise Exception('Invalid face list!')
	
	# ===================
	# - Get Set Members -
	# ===================
	
	# Sort Faces by Object
	faceObjList = glTools.utils.selection.componentListByObject(facelist)
	
	# For Each Object in Set
	meshPreviewList = []
	for faceList in faceObjList:
		
		# Get Mesh
		faceMesh = mc.ls(faceList[0],o=True)[0]
		if not glTools.utils.transform.isTransform(faceMesh):
			faceMesh = mc.listRelatives(faceMesh,p=True,pa=True)[0]
		
		# Get Face Id List
		faceIdList = glTools.utils.component.singleIndexList(faceList)
		faceIdStr = str(faceIdList)[1:-1]
		
		# ========================
		# - Add ABC PrimVar Attr -
		# ========================
		
		attrName = 'deleteFaceSet'
		if mc.objExists(faceMesh+'.ABC_'+attrName):
			try: mc.setAttr(faceMesh+'.ABC_'+attrName,l=False)
			except: pass
			mc.deleteAttr(faceMesh+'.ABC_'+attrName)
		
		glTools.utils.primvar.addAbcPrimVarStr(	geo = faceMesh,
												attrName = attrName,
												stringVal = faceIdStr,
												lock = False )
		
		# =================
		# - Build Standin -
		# =================
		
		if buildStandin:
			
			# Duplicate Original (with Connections)
			meshPreview = mc.polyDuplicateAndConnect(faceMesh)[0]
			meshPreview = mc.rename(meshPreview,faceMesh+'_standin')
			
			# Reparent Object
			try: mc.parent(meshPreview,w=True)
			except: pass
			
			# Delete Unused Shapes
			meshPreviewShapes = mc.listRelatives(meshPreview,s=True,pa=True)
			if meshPreviewShapes:
				meshPreviewIntShapes = mc.ls(meshPreviewShapes,intermediateObjects=True)
				if meshPreviewIntShapes: mc.delete(meshPreviewIntShapes)
			
			# Rename Shape
			meshPreviewShapes = mc.listRelatives(meshPreview,s=True,pa=True)
			if meshPreviewShapes: meshPreviewShape = mc.rename(meshPreviewShapes[0],meshPreview+'Shape')
			
			# Delete Faces
			mc.delete([meshPreview+'.f['+str(i)+']' for i in faceIdList])
			
			# Append Output List
			meshPreviewList.append(meshPreview)
	
	# =================
	# - Return Result -
	# =================
	
	return meshPreviewList

def selectNonRenderableFaces(geo):
	'''
	Select non-renderable faces for selected geometry
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Mesh
	if not glTools.utils.mesh.isMesh(geo):
		mc.warning('Object "'+geo+'" is not a valid mesh! Unable to select non-renderable faces...')
		return []
	
	# Check Attribute
	attrName = 'ABC_deleteFaceSet'
	if not mc.attributeQuery(attrName,n=geo,ex=True):
		mc.warning('Attribute "'+geo+'.'+attrName+'" does not exist! Unable to select non-renderable faces...')
		return []
	
	# ================
	# - Select Faces -
	# ================
	
	faceIdStr = mc.getAttr(geo+'.'+attrName)
	faceIdList = ast.literal_eval(faceIdStr)
	faceList = [geo+'.f['+str(i)+']' for i in faceIdList]
	
	try: mc.select(faceList)
	except: mc.warning('Problem selecting face list! '+str(faceList))
	
	# =================
	# - Return Result -
	# =================
	
	return faceList

def checkNonReferencedInputShape(geo):
	'''
	Check if the input shape on the specified referenced geometry is a referenced node.
	@param geo: Geometry to check referenced input shape on.
	@type geo: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Geometry Exists
	if not mc.objExists(geo):
		raise Exception('Geometry "'+geo+'" does not exist!')
	# Check Geometry is Referenced
	if not glTools.utils.reference.isReferenced(geo):
		raise Exception('Geometry "'+geo+'" is not referenced! No referenced shapes under nonReference parent...')
	
	# Get Geometry Shapes
	shapes = mc.listRelatives(geo,s=True,pa=True)
	if not shapes:
		raise Exception('No shapes found under geometry "'+geo+'"!')
	if len(shapes) == 1:
		print('Geometry "'+geo+'" has only one shape! Nothing to do here, skipping...')
		return False
	
	# Check for Referenced Shapes
	refShapes = [shape for shape in shapes if glTools.utils.reference.isReferenced(shape)]
	if not refShapes:
		raise Exception('No referenced shapes found under geometry "'+geo+'"!')
	
	# Get Output Shape
	resultShape = mc.listRelatives(geo,s=True,ni=True,pa=True)
	if not resultShape:
		raise Exception('No non-intermediate shapes under geometry "'+geo+'"!')
	if len(resultShape) != 1:
		print('Multiple non-intermediate shapes! Checking first shape ("'+resultShape[0]+'") for input connections... ')
	
	# Get Input Shape
	inputShape = glTools.utils.shape.findInputShape(resultShape[0],recursive=True)
	if not inputShape:
		raise Exception('Unable to determine input shape for "'+resultShape[0]+'"!')
	if inputShape == resultShape[0]:
		if mc.listHistory(inputShape):
			print('WARNING: Input shape is same as output shape for geometry "'+geo+'"! Check graph for cyclic dependancy...')
		else:
			print('Output shape "'+resultShape[0]+'" has no incoming connections! Nothing to do, skipping...')
		return False
	
	# Check Input Shape is Referenced
	return not glTools.utils.reference.isReferenced(inputShape)

def fixNonReferencedInputShape(geo):
	'''
	Ensure the input shape on the specified referenced geometry is a referenced shape node.
	@param geo: Geometry to fix referenced input shape on.
	@type geo: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Geometry Exists
	if not mc.objExists(geo):
		raise Exception('Geometry "'+geo+'" does not exist!')
	# Check Geometry is Referenced
	if not glTools.utils.reference.isReferenced(geo):
		raise Exception('Geometry "'+geo+'" is not referenced! No referenced shapes under nonReference parent...')
	
	# Get Geometry Shapes
	shapes = mc.listRelatives(geo,s=True,pa=True)
	if not shapes:
		raise Exception('No shapes found under geometry "'+geo+'"!')
	if len(shapes) == 1:
		print('Geometry "'+geo+'" has only one shape! Nothing to do here, skipping...')
		return ''
	
	# Check for Referenced Shapes
	refShapes = [shape for shape in shapes if glTools.utils.reference.isReferenced(shape)]
	if not refShapes:
		raise Exception('No referenced shapes found under geometry "'+geo+'"!')
	if len(refShapes) > 1:
		print('Found multiple referenced shapes under geometry transform "'+geo+'"! Using first shape "'+refShapes[0]+'" for input connections...')
	
	# Get Output Shape
	resultShape = mc.listRelatives(geo,s=True,ni=True,pa=True)
	if not resultShape:
		raise Exception('No non-intermediate shapes found under geometry "'+geo+'"!')
	if len(resultShape) != 1:
		print('Found multiple non-intermediate shapes! Using first shape "'+resultShape[0]+'" for input connections...')
	
	# Get Input Shape
	inputShape = glTools.utils.shape.findInputShape(resultShape[0],recursive=True)
	if not inputShape:
		raise Exception('No input shape found for "'+resultShape[0]+'"!')
	if inputShape == resultShape[0]:
		if mc.listHistory(inputShape):
			print('WARNING: Input shape is same as output shape for geometry "'+geo+'"! Check graph for cyclic dependancy...')
		else:
			print('Output shape "'+resultShape[0]+'" has no incoming connections! Nothing to do, skipping...')
		return ''
	
	# Check Input Shape is Referenced
	if glTools.utils.reference.isReferenced(inputShape):
		print('Input shape is referenced! Skipping...')
		return ''
	
	# =============================================
	# - Replace Input Shape with Referenced Shape -
	# =============================================
	
	# Check Reference Shape is Output
	if resultShape[0] == refShapes[0]:
		
		# Swap Input/Output Node Conections
		print('References shape is output (result) shape! Rearranging geometry graph...')
		glTools.utils.connection.swap(inputShape,refShapes[0])
		
		# Set Intermediate Object Status
		mc.setAttr(inputShape+'.intermediateObject',0)
		mc.setAttr(refShapes[0]+'.intermediateObject',1)
		
		# Fix Shape Names
		if 'Orig' in inputShape:
			if 'Deformed' in inputShape:
				inputShape = mc.rename(inputShape,inputShape.replace('Orig',''))
			else:
				inputShape = mc.rename(inputShape,inputShape.replace('Orig','Deformed'))
	else:
		
		# Check inMesh Connections to Referenced Shape
		if mc.listConnections(refShapes[0]+'.inMesh',s=True,d=False):
			
			# Swap Input/Output Node Conections
			glTools.utils.connection.swap(inputShape,refShapes[0])
		
		else:
			
			# Replace Input/Output Node Conections
			glTools.utils.connection.replace(inputShape,refShapes[0],inputs=True,outputs=True)
		
	# =================
	# - Return Result -
	# =================
	
	return refShapes[0]

def cleanUnusedIntermediateShapes(geo):
	'''
	'''
	# Check Geometry Exists
	if not mc.objExists(geo):
		raise Exception('Geometry "'+geo+'" does not exist!')
	
	# Get Geometry Shapes
	shapes = mc.listRelatives(geo,s=True,pa=True)
	if not shapes:
		raise Exception('No shapes found under geometry "'+geo+'"!')
	if len(shapes) == 1:
		print('Geometry "'+geo+'" has only one shape! Nothing to do here, skipping...')
		return None
	
	# Get Output Shape
	resultShapes = mc.listRelatives(geo,s=True,ni=True,pa=True)
	if not resultShapes:
		raise Exception('No non-intermediate shapes found under geometry "'+geo+'"!')
	if len(resultShapes) != 1:
		print('Found multiple non-intermediate shapes!')
	
	# For Each Output Shape
	for resultShape in resultShapes:
	
		# Get Input Shape
		inputShape = glTools.utils.shape.findInputShape(resultShape,recursive=True)
		if not inputShape:
			print('No input shape found for "'+resultShape+'"! Skipping')
			continue
		if inputShape == resultShape:
			if mc.listHistory(inputShape):
				print('WARNING: Input shape is same as output shape for geometry "'+geo+'"! Check graph for cyclic dependancy...')
			else:
				print('Output shape "'+resultShape+'" has no incoming connections! Nothing to do, skipping...')
			continue
		
		# Replace Unused Intermediate Shapes Connections
		intermediateShape = glTools.utils.shape.findInputShape(resultShape)
		while(intermediateShape != inputShape):
			
			# Store Next Intermediate Shape
			intShape = intermediateShape
			intermediateShape = glTools.utils.shape.findInputShape(intShape)
			
			# MESH
			if mc.objectType(intShape) == 'mesh':
				inMeshConn = mc.listConnections(intShape+'.inMesh',s=True,d=False,p=True)
				if inMeshConn:
					outMeshConn = mc.listConnections([intShape+'.outMesh',intShape+'.worldMesh'],s=False,d=True,p=True) or []
					for outConn in outMeshConn: mc.connectAttr(inMeshConn[0],outConn,f=True)
			
			# NURBS
			elif mc.objectType(intShape) in ['nurbsCurve','nurbsSurface']:
				inNurbConn = mc.listConnections(intShape+'.create',s=True,d=False,p=True)
				if inNurbConn:
					outNurbConn = mc.listConnections([intShape+'.local',intShape+'.worldSpace'],s=False,d=True,p=True) or []
					for outConn in outNurbConn: mc.connectAttr(inNurbConn[0],outConn,f=True)
			
			# UNSUPPORTED
			else:
				print('Unsupported shape type! ('+mc.objectType(intShape)+')! Skipping geometry...')
				break
			
			# Replace Generic Connections
			#glTools.utils.connection.replace(intShape,inputShape,inputs=True,outputs=True)
			
			# Delete Unused Intermediate Shape
			mc.delete(intShape)
			
			# Print Shape Result
			print('# DELETED Intermediate Shape: '+intShape)
