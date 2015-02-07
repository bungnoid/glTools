import maya.cmds as mc

def create(	switchObject,
			switchAttr,
			switchName = '',
			visTargetList = [],
			visEnumList = [],
			visIndexList = [],
			prefix = ''	):
	'''
	Create a enumerated visibility switch based on the input arguments
	@param switchObject: Object to add switch attribute to 
	@type switchObject: str
	@param switchAttr: Switch attribute name
	@type switchAttr: str
	@param switchName: Switch attribute nice name for UI.
	@type switchName: str
	@param visTargetList: List of objects lists that will have visibility toggled by the switch attr. ([ [], [], ...])
	@type visTargetList:
	@param visEnumList: List of switch enum lables
	@type visEnumList: list
	@param visIndexList: List of custom indices.
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
	
	# Compare target and enum list
	if not visTargetList or not visEnumList:
		raise Exception('Visibility target or enum list has zero elements!')
	if len(visTargetList) != len(visEnumList):
		raise Exception('Visibility target and enum list length mis-match!')
	# Check Visibility Index List
	if visIndexList:
		if len(visTargetList) != len(visIndexList):
			raise Exception('Visibility target and index list length mis-match!')
	
	# =================================
	# - Create Visibility Switch Attr -
	# =================================
	
	# Check Visibility Switch Attr
	if not mc.objExists(switchObject+'.'+switchAttr):
		
		# Build Enum Value
		visEnum = ''
		for i in visEnumList: visEnum += i+':'
		# Add switch attr
		mc.addAttr(switchObject,ln=switchAttr,nn=switchName,at='enum',en=visEnum)
		mc.setAttr(switchObject+'.'+switchAttr,e=True,cb=True)
	
	# Create Custom Visibility Index (choice)
	vis_choice = ''
	if visIndexList:
		vis_choice = mc.createNode('choice',n=prefix+'_vis_choice')
		mc.addAttr(vis_choice,ln='visIndex',at='long',dv=-1,m=True)
		mc.connectAttr(switchObject+'.'+switchAttr,vis_choice+'.selector',f=True)
		for i in range(len(visIndexList)):
			mc.setAttr(vis_choice+'.visIndex['+str(i)+']',visIndexList[i])
			mc.connectAttr(vis_choice+'.visIndex['+str(i)+']',vis_choice+'.input['+str(i)+']',f=True)
	
	# ======================
	# - Connect Visibility -
	# ======================
	
	for i in range(len(visEnumList)):
		
		# Check visTargetList
		if not visTargetList[i]: continue
		
		# Create Condition Node
		conditionNode = mc.createNode('condition',n=prefix+'_'+visEnumList[i]+'Vis_condition')
		mc.setAttr(conditionNode+'.firstTerm',i)
		mc.setAttr(conditionNode+'.colorIfTrue',1,0,1)
		mc.setAttr(conditionNode+'.colorIfFalse',0,1,0)
		
		# Connect Condition Node
		conditionInput = switchObject+'.'+switchAttr
		if visIndexList: conditionInput = vis_choice+'.output'
		mc.connectAttr(conditionInput,conditionNode+'.secondTerm',f=True)
		
		# Connect Each Item in List - Vis ON
		for obj in visTargetList[i]:
			
			# Check visibility attr
			if not mc.objExists(obj+'.v'):
				raise Exception('Object "'+obj+'" has no visibility attribute!')
			if not mc.getAttr(obj+'.v',se=True):
				raise Exception('Attribute "'+obj+'.v" is locked or has incoming connections!')
			
			# Connect attribute
			mc.connectAttr(conditionNode+'.outColorR',obj+'.v',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return (switchObject+'.'+switchAttr)

def createEmpty(	switchObject,
					switchAttr,
					switchName = '',
					visEnumList = [],
					prefix = ''	):
	'''
	Create a enumerated visibility switch based on the input arguments
	@param switchObject: Object to add switch attribute to 
	@type switchObject: str
	@param switchAttr: Switch attribute name
	@type switchAttr: str
	@param switchName: Switch attribute nice name for UI.
	@type switchName: str
	@param visEnumList: List of switch enum lables
	@type visEnumList: list
	@param prefix: Naming prefix for new nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check switchObject
	if not mc.objExists(switchObject):
		raise Exception('Switch object "'+switchObject+'" does not exist!')
	
	# =================================
	# - Create Visibility Switch Attr -
	# =================================
	
	# Check Visibility Switch Attr
	if not mc.objExists(switchObject+'.'+switchAttr):
		
		# Build Enum Value
		visEnum = ''
		for i in visEnumList: visEnum += i+':'
		# Add switch attr
		mc.addAttr(switchObject,ln=switchAttr,nn=switchName,at='enum',en=visEnum)
		mc.setAttr(switchObject+'.'+switchAttr,e=True,cb=True)
	
	# =================
	# - Return Result -
	# =================
	
	return (switchObject+'.'+switchAttr)
