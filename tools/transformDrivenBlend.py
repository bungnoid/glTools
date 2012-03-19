import maya.cmds as mc

def driveShape(blendShape,target,driveAttr,minValue=-1.5,maxValue=1.5,prefix=''):
	'''
	@param blendShape: The blendShape node to drive
	@type blendShape: str
	@param target: The blendShape target that will be driven
	@type target: str
	@param driveAttr: The object.attribute that will drive the blendShape target
	@type driveAttr: str
	@param minValue: Minimum value for the blendShape target
	@type minValue: float
	@param maxValue: Maximum value for the blendShape target
	@type maxValue: float
	@param prefix: Name prefix for all created nodes
	@type prefix: str
	'''
	# Check drive object
	driveObj = mc.ls(driveAttr,o=True)
	if not driveObj: raise Exception('Invalid drive attribute "driveAttr"!')
	else: driveObj = driveObj[0]
	# Check drive attribute
	driveAttr = driveAttr.replace(driveObj+'.','')
	if not mc.objExists(driveObj+'.'+driveAttr):
		mc.addAttr(driveObj,ln=driveAttr,min=minValue,max=maxValue,dv=0,k=True)
	
	# Create remapValue node
	remapNode = mc.createNode('remapValue',n=prefix+'_remapValue')
	
	# Connect drive attribute
	mc.connectAttr(driveObj+'.'+driveAttr,remapNode+'.inputValue')
	
	# Remap input value to target limits
	mc.setAttr(remapNode+'.inputMin',minValue)
	mc.setAttr(remapNode+'.inputMax',maxValue)
	mc.setAttr(remapNode+'.outputMin',minValue)
	mc.setAttr(remapNode+'.outputMax',maxValue)
	
	# Connect to blendShape target attributes
	mc.connectAttr(remapNode+'.outValue',blendShape+'.'+target)
	
	# Return result
	return remapNode

def drive2Shapes(blendShape,target1,target2,driveAttr,minValue=-1.5,maxValue=1.5,overlap=0.0,prefix=''):
	'''
	@param blendShape: The blendShape node to drive
	@type blendShape: str
	@param target1: The blendShape target that will be driven with negative value
	@type target1: str
	@param target2: The blendShape target that will be driven with positive value
	@type target2: str
	@param driveAttr: The object.attribute that will drive the blendShape targets
	@type driveAttr: str
	@param minValue: Minimum value to drive target1
	@type minValue: float
	@param maxValue: Maximum value to drive target2
	@type maxValue: float
	@param overlap: The amount that the 2 blendShape target will overlap at a neutral drive value
	@type overlap: float
	@param prefix: Name prefix for all created nodes
	@type prefix: str
	'''
	# Check drive object
	driveObj = mc.ls(driveAttr,o=True)
	if not driveObj: raise Exception('Invalid drive attribute "driveAttr"!')
	else: driveObj = driveObj[0]
	# Check drive attribute
	driveAttr = driveAttr.replace(driveObj+'.','')
	if not mc.objExists(driveObj+'.'+driveAttr):
		mc.addAttr(driveObj,ln=driveAttr,min=minValue,max=maxValue,dv=0,k=True)
	
	# Create remapValue nodes
	remapNode1 = mc.createNode('remapValue',n=prefix+'_target1neg_remapValue')
	remapNode2 = mc.createNode('remapValue',n=prefix+'_target2pos_remapValue')
	
	# Connect drive attribute
	mc.connectAttr(driveObj+'.'+driveAttr,remapNode1+'.inputValue')
	mc.connectAttr(driveObj+'.'+driveAttr,remapNode2+'.inputValue')
	
	# Remap input value to target limits
	mc.setAttr(remapNode1+'.inputMin',minValue)
	mc.setAttr(remapNode1+'.inputMax',overlap)
	mc.setAttr(remapNode1+'.outputMin',-minValue)
	mc.setAttr(remapNode1+'.outputMax',0.0)
	
	mc.setAttr(remapNode2+'.inputMin',-overlap)
	mc.setAttr(remapNode2+'.inputMax',maxValue)
	mc.setAttr(remapNode2+'.outputMin',0.0)
	mc.setAttr(remapNode2+'.outputMax',maxValue)
	
	# Connect to blendShape target attributes
	mc.connectAttr(remapNode1+'.outValue',blendShape+'.'+target1)
	mc.connectAttr(remapNode2+'.outValue',blendShape+'.'+target2)
	
	# Return result
	return [remapNode1,remapNode2]

