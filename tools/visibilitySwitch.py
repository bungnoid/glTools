import maya.cmds as mc

def create(switchObject,switchAttr,visTargetList,visEnumList,connectIntermediateObject=False,prefix=''):
	'''
	Create a enumerated visibility switch based on the input arguments
	@param switchObject: Object to add switch attribute to 
	@type switchObject: str
	@param switchAttr: Switch attribute name
	@type switchAttr: str
	@param visTargetList:  
	@type visTargetList:
	@param visEnumList:  
	@type visEnumList:
	@param prefix:
	@type prefix:
	'''
	# Check switchObject
	if not mc.objExists(switchObject):
		raise Exception('Switch object "'+switchObject+'" does not exist!')
	
	# Compare target and enum list
	if len(visTargetList) != len(visEnumList):
		raise Exception('Visibility target and enum list length mis-match!')
	
	# Create visibility switch attr
	if not mc.objExists(switchObject+'.'+switchAttr):
		# Build enum value
		visEnum = ''
		for i in visEnumList: visEnum += i+':'
		# Add switch attr
		mc.addAttr(switchObject,ln=switchAttr,at='enum',en=visEnum)
		mc.setAttr(switchObject+'.'+switchAttr,e=True,cb=True)
	
	# Connect to visibility
	for i in range(len(visEnumList)):
		
		# Create condition node
		conditionNode = mc.createNode('condition',n=prefix+'_'+visEnumList[i]+'Vis_condition')
		mc.setAttr(conditionNode+'.firstTerm',i)
		mc.connectAttr(switchObject+'.'+switchAttr,conditionNode+'.secondTerm',f=True)
		mc.setAttr(conditionNode+'.colorIfTrue',1,0,1)
		mc.setAttr(conditionNode+'.colorIfFalse',0,1,0)
		
		# Connect each object in list
		for obj in visTargetList[i]:
			
			# Check visibility attr
			if not mc.objExists(obj+'.v'):
				raise Exception('Object "'+obj+'" has no visibility attribute!')
			if not mc.getAttr(obj+'.v',se=True):
				raise Exception('Attribute "'+obj+'.v" is locked or has incoming connections!')
			
			# Connect attribute
			mc.connectAttr(conditionNode+'.outColorR',obj+'.v',f=True)
			
			if connectIntermediateObject:
				mc.connectAttr(conditionNode+'.outColorG',obj+'.intermediateObject',f=True)
	
	# Return result
	return (switchObject+'.'+switchAttr)
		
