import maya.mel as mm
import maya.cmds as mc

import os

def init():
	'''
	Load required commands and plugins
	'''
	# Get Maya App Location
	MAYA_LOCATION = os.environ['MAYA_LOCATION']
	
	# Source Mel Files
	mm.eval('source "'+MAYA_LOCATION+'/scripts/others/hikGlobalUtils.mel"')
	mm.eval('source "'+MAYA_LOCATION+'/scripts/others/hikCharacterControlsUI.mel"')
	mm.eval('source "'+MAYA_LOCATION+'/scripts/others/hikDefinitionOperations.mel"')
	mm.eval('source "'+MAYA_LOCATION+'/scripts/others/CharacterPipeline.mel"')
	mm.eval('source "'+MAYA_LOCATION+'/scripts/others/characterSelector.mel"')
	
	# Load Plugins
	if not mc.pluginInfo('mayaHIK',q=True,l=True):
		mc.loadPlugin('mayaHIK')
	if not mc.pluginInfo('mayaCharacterization',q=True,l=True):
		mc.loadPlugin('mayaCharacterization')
	if not mc.pluginInfo('retargeterNodes',q=True,l=True):
		mc.loadPlugin('retargeterNodes')
	
	# HIK Character Controls Tool
	mm.eval('HIKCharacterControlsTool')

def isCharacterDefinition(char):
	'''
	'''
	# Check Node Exists
	if not mc.objExists(char): return False
	
	# Check Node Type
	if mc.objectType(char) != 'HIKCharacterNode': return False
	
	# Return Result
	return True

def isCharacterDefinitionLocked(char):
	'''
	'''
	# Check Character Definition
	if not isCharacterDefinition(char):
		raise Exception('Invalid character definition node! Object "'+char+'" does not exist or is not a valid HIKCharacterNode!')
	
	# Check Lock
	lock = mc.getAttr(char+'.InputCharacterizationLock')
	
	# Return Result
	return lock

def characterDefinitionLock(char,lockState=True,saveStance=True):
	'''
	'''
	# Check Character Definition
	if not isCharacterDefinition(char):
		raise Exception('Invalid character definition node! Object "'+char+'" does not exist or is not a valid HIKCharacterNode!')
	
	# Check Lock State
	isLocked = isCharacterDefinitionLocked(char)
	
	# Set Lock State
	if lockState != isLocked: mm.eval('hikToggleLockDefinition')
	#mm.eval('mayaHIKcharacterLock("'+char+'",'+str(int(lockState))+','+str(int(saveStance))+')')
	
	# Return State
	return int(lockState)

def create(charNS,charName,lock=True):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if charNS: charNS+=':'
	
	# ===============================
	# - Create Character Definition -
	# ===============================
	
	charDef = mm.eval('CreateHIKCharacterWithName "'+charName+'"')
	setCurrentCharacter(charDef)
	
	try:
		mm.eval('hikUpdateCharacterList()')
		mm.eval('hikSelectDefinitionTab()')
	except:
		pass
	
	# Apply Temmplate
	setCharacterObject(charDef,charNS+'Hips',1,0)
	setCharacterObject(charDef,charNS+'Head',15,0)
	setCharacterObject(charDef,charNS+'LeftArm',9,0)
	setCharacterObject(charDef,charNS+'LeftArmRoll',45,0)
	setCharacterObject(charDef,charNS+'LeftFoot',4,0)
	setCharacterObject(charDef,charNS+'LeftForeArm',10,0)
	setCharacterObject(charDef,charNS+'LeftForeArmRoll',46,0)
	setCharacterObject(charDef,charNS+'LeftHand',11,0)
	setCharacterObject(charDef,charNS+'LeftHandIndex1',54,0)
	setCharacterObject(charDef,charNS+'LeftHandIndex2',55,0)
	setCharacterObject(charDef,charNS+'LeftHandIndex3',56,0)
	setCharacterObject(charDef,charNS+'LeftHandMiddle1',58,0)
	setCharacterObject(charDef,charNS+'LeftHandMiddle2',59,0)
	setCharacterObject(charDef,charNS+'LeftHandMiddle3',60,0)
	setCharacterObject(charDef,charNS+'LeftHandPinky1',66,0)
	setCharacterObject(charDef,charNS+'LeftHandPinky2',67,0)
	setCharacterObject(charDef,charNS+'LeftHandPinky3',68,0)
	setCharacterObject(charDef,charNS+'LeftHandRing1',62,0)
	setCharacterObject(charDef,charNS+'LeftHandRing2',63,0)
	setCharacterObject(charDef,charNS+'LeftHandRing3',64,0)
	setCharacterObject(charDef,charNS+'LeftHandThumb1',50,0)
	setCharacterObject(charDef,charNS+'LeftHandThumb2',51,0)
	setCharacterObject(charDef,charNS+'LeftHandThumb3',52,0)
	setCharacterObject(charDef,charNS+'LeftInHandIndex',147,0)
	setCharacterObject(charDef,charNS+'LeftInHandMiddle',148,0)
	setCharacterObject(charDef,charNS+'LeftInHandPinky',150,0)
	setCharacterObject(charDef,charNS+'LeftInHandRing',149,0)
	setCharacterObject(charDef,charNS+'LeftLeg',3,0)
	setCharacterObject(charDef,charNS+'LeftLegRoll',42,0)
	setCharacterObject(charDef,charNS+'LeftShoulder',18,0)
	setCharacterObject(charDef,charNS+'LeftToeBase',16,0)
	setCharacterObject(charDef,charNS+'LeftUpLeg',2,0)
	setCharacterObject(charDef,charNS+'LeftUpLegRoll',41,0)
	setCharacterObject(charDef,charNS+'Neck',20,0)
	setCharacterObject(charDef,charNS+'Reference',0,0)
	setCharacterObject(charDef,charNS+'RightArm',12,0)
	setCharacterObject(charDef,charNS+'RightArmRoll',47,0)
	setCharacterObject(charDef,charNS+'RightFoot',7,0)
	setCharacterObject(charDef,charNS+'RightForeArm',13,0)
	setCharacterObject(charDef,charNS+'RightForeArmRoll',48,0)
	setCharacterObject(charDef,charNS+'RightHand',14,0)
	setCharacterObject(charDef,charNS+'RightHandIndex1',78,0)
	setCharacterObject(charDef,charNS+'RightHandIndex2',79,0)
	setCharacterObject(charDef,charNS+'RightHandIndex3',80,0)
	setCharacterObject(charDef,charNS+'RightHandMiddle1',82,0)
	setCharacterObject(charDef,charNS+'RightHandMiddle2',83,0)
	setCharacterObject(charDef,charNS+'RightHandMiddle3',84,0)
	setCharacterObject(charDef,charNS+'RightHandPinky1',90,0)
	setCharacterObject(charDef,charNS+'RightHandPinky2',91,0)
	setCharacterObject(charDef,charNS+'RightHandPinky3',92,0)
	setCharacterObject(charDef,charNS+'RightHandRing1',86,0)
	setCharacterObject(charDef,charNS+'RightHandRing2',87,0)
	setCharacterObject(charDef,charNS+'RightHandRing3',88,0)
	setCharacterObject(charDef,charNS+'RightHandThumb1',74,0)
	setCharacterObject(charDef,charNS+'RightHandThumb2',75,0)
	setCharacterObject(charDef,charNS+'RightHandThumb3',76,0)
	setCharacterObject(charDef,charNS+'RightInHandIndex',153,0)
	setCharacterObject(charDef,charNS+'RightInHandMiddle',154,0)
	setCharacterObject(charDef,charNS+'RightInHandPinky',156,0)
	setCharacterObject(charDef,charNS+'RightInHandRing',155,0)
	setCharacterObject(charDef,charNS+'RightLeg',6,0)
	setCharacterObject(charDef,charNS+'RightLegRoll',44,0)
	setCharacterObject(charDef,charNS+'RightShoulder',19,0)
	setCharacterObject(charDef,charNS+'RightToeBase',17,0)
	setCharacterObject(charDef,charNS+'RightUpLeg',5,0)
	setCharacterObject(charDef,charNS+'RightUpLegRoll',43,0)
	setCharacterObject(charDef,charNS+'Spine',8,0)
	setCharacterObject(charDef,charNS+'Spine1',23,0)
	setCharacterObject(charDef,charNS+'Spine2',24,0)
	
	# =======================================
	# - Set Character Definition Properties -
	# =======================================
	
	# Get Character Definition Properties Node
	propertyNode = getPropertiesNode(charDef)
	
	# Match Source
	mc.setAttr(propertyNode+'.ForceActorSpace',0) # OFF
	# Action Space Comp Mode
	mc.setAttr(propertyNode+'.ScaleCompensationMode',1) # AUTO
	# Mirror Animation
	mc.setAttr(propertyNode+'.Mirror',0) # OFF
	# Hips Level Mode
	mc.setAttr(propertyNode+'.HipsHeightCompensationMode',1) # AUTO
	# Feet Spacing Mode
	mc.setAttr(propertyNode+'.AnkleProximityCompensationMode',1) # AUTO
	# Ankle Height Compensation
	mc.setAttr(propertyNode+'.AnkleHeightCompensationMode',0) # OFF
	# Mass Center Comp Mode
	mc.setAttr(propertyNode+'.MassCenterCompensationMode',1) # ON
	
	# ===================
	# - Lock Definition -
	# ===================
	
	if lock:
		#characterDefinitionLock(charDef,lockState=True,saveStance=True)
		mm.eval('hikToggleLockDefinition')
	
	# =================
	# - Return Result -
	# =================
	
	return charDef

def setCharacterObject(charDef,charBone,boneId,deleteBone=False):
	'''
	'''
	mm.eval('setCharacterObject("'+charBone+'","'+charDef+'",'+str(boneId)+','+str(int(deleteBone))+')')

def getCurrentCharacter():
	'''
	'''
	char = mm.eval('hikGetCurrentCharacter()')
	return char

def setCurrentCharacter(char):
	'''
	'''
	mm.eval('hikSetCurrentCharacter("'+char+'")')
	mm.eval('hikUpdateCharacterList()')
	mm.eval('hikSetCurrentSourceFromCharacter("'+char+'")')
	mm.eval('hikUpdateSourceList()')

def getCharacterNodes(char):
	'''
	'''
	# Check Node
	if not isCharacterDefinition(char):
		raise Exception('Invalid character definition node! Object "'+char+'" does not exist or is not a valid HIKCharacterNode!')
	
	# Get Character Nodes
	charNodes = mm.eval('hikGetSkeletonNodes "'+char+'"')
	
	# Return Result
	return charNodes

def setCharacterSource(char,source):
	'''
	'''
	# HIK Character Controls Tool
	mm.eval('HIKCharacterControlsTool')
	
	# Get Current Character
	currChar = getCurrentCharacter()
	
	# Set Current Character
	setCurrentCharacter(char)
	
	# Set Character Source
	mm.eval('hikSetCurrentSource("'+source+'")')
	mm.eval('hikUpdateSourceList()')
	mm.eval('hikUpdateCurrentSourceFromUI()')
	mm.eval('hikUpdateContextualUI()')
	mm.eval('hikControlRigSelectionChangedCallback')
	
	# Restore Current Character
	if char != currChar: setCurrentCharacter(currChar)

def getPropertiesNode(char):
	'''
	'''
	# Check Node
	if not isCharacterDefinition(char):
		raise Exception('Invalid character definition node! Object "'+char+'" does not exist or is not a valid HIKCharacterNode!')
			
	propertyNode = ''
	try:
		propertyNode = mm.eval('getProperty2StateFromCharacter("'+char+'")')
	except:
	
		# Get propertyState Connections
		conn = mc.listConnections(char+'.propertyState',s=True,d=False)
		if not conn:
			raise Exception('Unable to determine HIKProperty2State node from character definition node "'+char+'"!')
		
		# Check Number of Results
		if len(conn) > 1:
			print('Multiple HIKProperty2State nodes found for character definition "'+char+'"! Returning first item only...')
		
		# Assign Property Node
		propertyNode = conn[0]
	
	# Return Result
	return propertyNode

def getSolverNode(char):
	'''
	'''
	# Check Node
	if not isCharacterDefinition(char):
		raise Exception('Invalid character definition node! Object "'+char+'" does not exist or is not a valid HIKCharacterNode!')
	
	# Get OutputPropertySetState Connections
	conn = mc.ls(mc.listConnections(char+'.OutputPropertySetState',d=True,s=False) or [],type='HIKSolverNode')
	if not conn:
		raise Exception('Unable to determine HIKSolverNode node from character definition node "'+char+'"!')
	
	# Check Number of Results
	if len(conn) > 1:
		print('Multiple HIKSolverNode nodes found for character definition "'+char+'"! Returning first item only...')
	
	# Return Result
	return conn[0]

def getRetargetNode(char):
	'''
	'''
	# Check Node
	if not isCharacterDefinition(char):
		raise Exception('Invalid character definition node! Object "'+char+'" does not exist or is not a valid HIKCharacterNode!')
	
	# Get OutputPropertySetState Connections
	conn = mc.ls(mc.listConnections(char+'.OutputPropertySetState',d=True,s=False) or [],type='HIKRetargeterNode')
	if not conn:
		raise Exception('Unable to determine HIKRetargeterNode node from character definition node "'+char+'"!')
	
	# Check Number of Results
	if len(conn) > 1:
		print('Multiple HIKRetargeterNode nodes found for character definition "'+char+'"! Returning first item only...')
	
	# Return Result
	return conn[0]

def bakeAnim(char):
	'''
	'''
	# Get Character Bones
	bones = getCharacterNodes(char)
	
	# Bake Animation
	mc.bakeResults(	bones,
					simulation=True,
					t=[1,55],
					sampleBy=1,
					disableImplicitControl=True,
					preserveOutsideKeys=False,
					sparseAnimCurveBake=False,
					removeBakedAttributeFromLayer=False,
					bakeOnOverrideLayer=False,
					minimizeRotation=False,
					at=['tx','ty','tz','rx','ry','rz'] )
	
	# Return Result
	return bones

