import maya.cmds as mc

import glTools.utils.attribute

def create(	switchObject,
			switchAttr,
			switchName = '',
			targetAttrList = [],
			targetEnumList = [],
			targetIndexList = [],
			prefix = ''	):
	'''
	Create a enumerated attribute switch based on the input arguments
	@param switchObject: Object to add switch attribute to
	@type switchObject: str
	@param switchAttr: Switch attribute name
	@type switchAttr: str
	@param switchName: Switch attribute nice name for UI.
	@type switchName: str
	@param targetAttrList: List of target attribute lists that will have visibility toggled by the switch attr. ([ [], [], ...])
	@type targetAttrList:
	@param targetEnumList: List of switch enum lables
	@type targetEnumList: list
	@param targetIndexList: List of custom indices.
							The index (value) of the visibility enum attr will be used to look up an index from this list.
							If empty, visibility enum attr index (value) will be used directly.
	@param prefix: Naming prefix for new nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check switchObject
	if not mc.objExists(switchObject):
		raise Exception('Switch object "'+switchObject+'" does not exist!')
	
	# Compare Target and Enum List
	if not targetAttrList or not targetEnumList:
		raise Exception('Visibility target or enum list has zero elements!')
	if len(targetAttrList) != len(targetEnumList):
		raise Exception('Visibility target and enum list length mis-match!')
	# Check Visibility Index List
	if targetIndexList:
		if len(targetAttrList) != len(targetIndexList):
			raise Exception('Visibility target and index list length mis-match!')
	
	# =================================
	# - Create Visibility Switch Attr -
	# =================================
	
	# Check Visibility Switch Attr
	if not mc.objExists(switchObject+'.'+switchAttr):
		
		# Build Enum Value
		targetEnum = ''
		for i in targetEnumList: targetEnum += i+':'
		# Add switch attr
		mc.addAttr(switchObject,ln=switchAttr,nn=switchName,at='enum',en=targetEnum)
		mc.setAttr(switchObject+'.'+switchAttr,e=True,cb=True)
	
	# Create Custom Visibility Index (choice)
	target_choice = ''
	if targetIndexList:
		target_choice = mc.createNode('choice',n=prefix+'_target_choice')
		mc.addAttr(target_choice,ln='targetIndex',at='long',dv=-1,m=True)
		mc.connectAttr(switchObject+'.'+switchAttr,target_choice+'.selector',f=True)
		for i in range(len(targetIndexList)):
			mc.setAttr(target_choice+'.targetIndex['+str(i)+']',targetIndexList[i])
			mc.connectAttr(target_choice+'.targetIndex['+str(i)+']',target_choice+'.input['+str(i)+']',f=True)
	
	# ======================
	# - Connect Visibility -
	# ======================
	
	for i in range(len(targetEnumList)):
		
		# Check targetAttrList
		if not targetAttrList[i]: continue
		
		# Create Condition Node
		conditionNode = mc.createNode('condition',n=prefix+'_'+targetEnumList[i]+'Target_condition')
		mc.setAttr(conditionNode+'.firstTerm',i)
		mc.setAttr(conditionNode+'.colorIfTrue',1,0,1)
		mc.setAttr(conditionNode+'.colorIfFalse',0,1,0)
		
		# Connect Condition Node
		conditionInput = switchObject+'.'+switchAttr
		if targetIndexList: conditionInput = target_choice+'.output'
		mc.connectAttr(conditionInput,conditionNode+'.secondTerm',f=True)
		
		# Connect Each Item in List - Vis ON
		for targetAttr in targetAttrList[i]:
			
			# Check Target Attribute
			if not mc.objExists(targetAttr):
				raise Exception('Attribute "'+targetAttr+'" does not exist!')
			if not glTools.utils.attribute.isAttr(targetAttr):
				raise Exception('Object "'+targetAttr+'" is not a valid attribute!')
			if not mc.getAttr(targetAttr,se=True):
				raise Exception('Attribute "'+targetAttr+'" is locked or has incoming connections!')
			
			# Connect attribute
			mc.connectAttr(conditionNode+'.outColorR',targetAttr,f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return (switchObject+'.'+switchAttr)

