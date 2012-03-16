import maya.cmds as mc
import copy

def setDrivenKeyToRemapValue(animCurve,remapValueNode='',interpType=3,deleteAnimCurve=True,lockPosition=True,lockValue=False):
	'''
	Convert a set driven key setup to a remapValue node.
	Each key on the animCurve node is represented as widget on the remapValue ramp control.
	Incoming and outgoing curve connections will be replaced with equivalent remapVlue connections.
	@param animCurve: The animCurve to convert to a remapValue node
	@type animCurve: str
	@param remapValueNode: Name an existing remapValue node to use instead of creating a new one.
	@type remapValueNode: str
	@param interpType: Default ramp interpolation type.
	@type interpType: int
	@param deleteAnimCurve: Delete animCurve node after disconnection
	@type deleteAnimCurve: bool
	@param lockPosition: Lock ramp widget position values
	@type lockPosition: bool
	@param lockValue: Lock ramp widget float values
	@type lockValue: bool
	'''
	# Checks
	if not mc.objExists(animCurve):
		raise Exception('AnimCurve node "'+animCurve+'" does not exist!!')
	if remapValueNode and not mc.objExists(remapValueNode):
		raise Exception('RemapValue node "'+remapValueNode+'" does not exist!!')
	
	# Get connections to animCurve
	inConn = mc.listConnections(animCurve+'.input',s=True,d=False,p=True)
	outConn = mc.listConnections(animCurve+'.output',s=False,d=True,p=True)
	
	# Get keyframe data
	valList = mc.keyframe(animCurve,q=True,vc=True)
	floatList = mc.keyframe(animCurve,q=True,fc=True)
	
	# Get min/max input and output values
	orderValList = copy.deepcopy(valList)
	orderFloatList = copy.deepcopy(floatList)
	orderValList.sort()
	orderFloatList.sort()
	minVal = orderValList[0]
	maxVal = orderValList[-1]
	minFloat = orderFloatList[0]
	maxFloat = orderFloatList[-1]
	
	# Create remapValue node
	if not remapValueNode:
		remapValueNode = mc.createNode('remapValue',n=animCurve+'_remapValue')
	
	# Set Remap attribute values
	mc.setAttr(remapValueNode+'.inputMin',minFloat)
	mc.setAttr(remapValueNode+'.inputMax',maxFloat)
	mc.setAttr(remapValueNode+'.outputMin',minVal)
	mc.setAttr(remapValueNode+'.outputMax',maxVal)
	
	# Remove existing ramp widgets
	indexList = range(mc.getAttr(remapValueNode+'.value',s=True))
	indexList.reverse()
	for i in indexList:
		mc.removeMultiInstance(remapValueNode+'.value['+str(i)+']',b=True)
		
	# Set ramp widgets based on keys
	valRange = maxVal - minVal
	floatRange = maxFloat - minFloat
	# Check zero values
	if valRange < 0.0001: valRange = 0.0001
	if floatRange < 0.0001: floatRange = 0.0001
	# Iterate through keys
	for i in range(len(valList)):
		val = (valList[i] - minVal)/valRange
		flt = (floatList[i] - minFloat)/floatRange
		mc.setAttr(remapValueNode+'.value['+str(i)+'].value_Position',flt)
		mc.setAttr(remapValueNode+'.value['+str(i)+'].value_FloatValue',val)
		mc.setAttr(remapValueNode+'.value['+str(i)+'].value_Interp',interpType)
		if lockPosition:
			mc.setAttr(remapValueNode+'.value['+str(i)+'].value_Position',l=True)
		if lockValue:
			mc.setAttr(remapValueNode+'.value['+str(i)+'].value_FloatValue',l=True)
	
	# Replace animCurve connections
	mc.connectAttr(inConn[0],remapValueNode+'.inputValue',f=True)
	mc.connectAttr(remapValueNode+'.outValue',outConn[0],f=True)
	
	# Delete unused animCurve
	if deleteAnimCurve: mc.delete(animCurve)
	
	# Return result
	return remapValueNode
