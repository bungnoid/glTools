import maya.cmds as mc
import glTools.utils.stringUtils

def isConstraint(constraint):
	'''
	Check if the specified node is a valid constraint
	@param constraint: The constraint node to query
	@type constraint: str
	'''
	if not mc.objExists(constraint): return False
	if not mc.ls(constraint,type='constraint'): return False
	return True

def isBaked(constraint):
	'''
	Check if the specified constraint has been baked
	@param constraint: The constraint node to query
	@type constraint: str
	'''
	# Check Constraint
	if not isConstraint(constraint):
		raise Exception('Constraint "'+constraint+'" does not exist!!')
	
	# Get Constraint Slave
	cSlave = slave(constraint)
	
	# Get Slave Channels
	cSlaveAttrs = mc.listConnections(constraint,s=False,d=True,p=True) or []
	slaveAttrs = [i.split('.')[-1] for i in attrList if i.startswith(slave+'.')] or []
	
	# Check Slave Channels
	if slaveAttrs: return False
	
	# Return Result
	return False

def targetList(constraint):
	'''
	Return a list of targets (drivers) for the specified constraint node
	@param constraint: The constraint node whose targets will be returned
	@type constraint: str
	'''
	# Check Constraint
	if not isConstraint(constraint):
		raise Exception('Constraint "'+constraint+'" does not exist!!')
	
	# Get Target List
	targetList = []
	constraintType = mc.objectType(constraint)
	if constraintType == 'aimConstraint': targetList = mc.aimConstraint(constraint,q=True,tl=True)
	elif constraintType == 'geometryConstraint': targetList = mc.geometryConstraint(constraint,q=True,tl=True)
	elif constraintType == 'normalConstraint': targetList = mc.normalConstraint(constraint,q=True,tl=True)
	elif constraintType == 'orientConstraint': targetList = mc.orientConstraint(constraint,q=True,tl=True)
	elif constraintType == 'parentConstraint': targetList = mc.parentConstraint(constraint,q=True,tl=True)
	elif constraintType == 'pointConstraint': targetList = mc.pointConstraint(constraint,q=True,tl=True)
	elif constraintType == 'poleVectorConstraint': targetList = mc.poleVectorConstraint(constraint,q=True,tl=True)
	elif constraintType == 'scaleConstraint': targetList = mc.scaleConstraint(constraint,q=True,tl=True)
	elif constraintType == 'tangentConstraint': targetList = mc.tangentConstraint(constraint,q=True,tl=True)
	
	# Check Target List
	if not targetList: targetList = []
	
	# Return Result
	return targetList

def targetIndex(constraint,target):
	'''
	Return the target index of the specified target of a constraint
	@param constraint: The constraint to return the target index for
	@type constraint: str
	@param constraint: The constraint target to return the input index for
	@type constraint: str
	'''
	# Get Target List
	targetList = targetList(constraint)
	# Get Target List
	targetIndex = targetList.index(target)
	# Return Result
	return targetIndex

def targetAliasList(constraint):
	'''
	Return a list of targets (drivers) attribute aliases for the specified constraint node
	@param constraint: The constraint node whose targets will be returned
	@type constraint: str
	'''
	# Check Constraint
	if not isConstraint(constraint):
		raise Exception('Constraint "'+constraint+'" does not exist!!')
	
	# Get Target List
	targetList = []
	constraintType = mc.objectType(constraint)
	if constraintType == 'aimConstraint': targetList = mc.aimConstraint(constraint,q=True,weightAliasList=True)
	elif constraintType == 'geometryConstraint': targetList = mc.geometryConstraint(constraint,q=True,weightAliasList=True)
	elif constraintType == 'normalConstraint': targetList = mc.normalConstraint(constraint,q=True,weightAliasList=True)
	elif constraintType == 'orientConstraint': targetList = mc.orientConstraint(constraint,q=True,weightAliasList=True)
	elif constraintType == 'parentConstraint': targetList = mc.parentConstraint(constraint,q=True,weightAliasList=True)
	elif constraintType == 'pointConstraint': targetList = mc.pointConstraint(constraint,q=True,weightAliasList=True)
	elif constraintType == 'poleVectorConstraint': targetList = mc.poleVectorConstraint(constraint,q=True,weightAliasList=True)
	elif constraintType == 'scaleConstraint': targetList = mc.scaleConstraint(constraint,q=True,weightAliasList=True)
	elif constraintType == 'tangentConstraint': targetList = mc.tangentConstraint(constraint,q=True,weightAliasList=True)
	
	# Check Target List
	if not targetList: targetList = []
	
	# Return Result
	return targetList

def targetAlias(constraint,target):
	'''
	Return the target alias fo the specified constraint and target transform
	@param constraint: The constraint to get the target alias from
	@type constraint: str
	@param target: The constraint target transform to get the target alias from
	@type target: str
	'''
	# Check Constraint
	if not isConstraint(constraint):
		raise Exception('Object "'+constraint+'" is not a valid constraint node!')
	
	# Get Target List 
	conTargetList = targetList(constraint)
	if not conTargetList.count(target):
		raise Exception('Constraint "'+constraint+'" has no target "'+target+'"!')
	
	# Get Target Alias List
	conTargetAliasList = targetAliasList(constraint)
	
	# Get Target Index
	targetIndex = conTargetList.index(target)
	
	# Get Target Alias
	targetAlias = conTargetAliasList[targetIndex]
	
	# Return Result
	return targetAlias

def slaveList(constraint):
	'''
	Return a list of slave transforms for the specified constraint node
	@param constraint: The constraint node whose slaves will be returned
	@type constraint: str
	'''
	# Check constraint
	if not mc.objExists(constraint): raise Exception('Constraint '+constraint+' does not exist!!')
	constraintType = mc.objectType(constraint)
	
	# Get slave list
	#targetList = []
	#[targetList.append(i) for i in mc.listConnections(constraint,s=False,d=True) if not targetList.count(i)]
	#if targetList.count(constraint): targetList.remove(constraint)
	targetList = mc.listConnections(constraint+'.constraintParentInverseMatrix',s=True,d=False) or []
	
	# Return result
	return targetList

def slave(constraint):
	'''
	Return a the slave transforms for the specified constraint node
	@param constraint: The constraint node to query
	@type constraint: str
	'''
	# Get Slave Transform
	slaves = slaveList(constraint)
	if not slaves: raise Exception('Unable to determine slave transform for constraint "'+constraint+'"!')
	# Return Result
	return slaves[0]

def blendConstraint(targetList,slave,blendNode='',blendAttr='bias',maintainOffset=True,prefix=''):
	'''
	Create a parent constraint that can be blended between 2 (more later) constraint targets
	@param targetList: 2 target transforms to constrain to
	@type targetList: list
	@param slave: Transform to constrain
	@type slave: str
	@param blendNode: Node that will contain the constraint blend attribute. If empty, use slave.
	@type blendNode: str
	@param blendAttr: Constraint blend attribute name.
	@type blendAttr: str
	@param maintainOffset: Maintain relative offsets between slave and targets.
	@type maintainOffset: bool
	@param prefix: Name prefix for created nodes
	@type prefix: str
	'''
	# Check prefix
	if not prefix: prefix = slave
	
	# Check targets
	if len(targetList) != 2: raise Exception('Target list must contain 2 target transform!')
	for target in targetList:
		if not mc.objExists(target):
			raise Exception('Target transform "'+target+'" does not exist!')
	
	# Check slave
	if not mc.objExists(slave):
		raise Exception('Slave transform "'+slave+'" does not exist!')
	
	# Check blendNode
	if not blendNode: blendNode = slave
	
	# Create constraint
	constraint = mc.parentConstraint(targetList,slave,mo=maintainOffset,n=prefix+'_parentConstraint')[0]
	constraintAlias = mc.parentConstraint(constraint,q=True,wal=True)
	
	# Create blend
	mc.addAttr(blendNode,ln=blendAttr,min=0,max=1,dv=0.5,k=True)
	blendSub = mc.createNode('plusMinusAverage',n=prefix+'_plusMinusAverage')
	mc.setAttr(blendSub+'.operation',2) # Subtract
	mc.setAttr(blendSub+'.input1D[0]',1.0)
	mc.connectAttr(blendNode+'.'+blendAttr,blendSub+'.input1D[1]',f=True)
	
	# Connect Blend
	mc.connectAttr(blendSub+'.output1D',constraint+'.'+constraintAlias[0],f=True)
	mc.connectAttr(blendNode+'.'+blendAttr,constraint+'.'+constraintAlias[1],f=True)
	
	# Return result
	return blendNode+'.'+blendAttr

def rounding(transformList,control,attr='round',prefix=''):
	'''
	Create rounding constraint.
	
	Given 5 transforms [1,2,3,4,5]:
		Transform 2 will be constrainted between 1 and 3.
		Transform 4 will be constrainted between 3 and 5.
	
	The attribute control.attr controls the weights of the constraint.
	
	@param transformList: Specify 5 transforms used for constraint
	@type transformList: list
	@param control: Control that contains attribute for controlling constraint weight
	@type control: str
	@param attr: Attribute for controlling constraint weight
	@type attr: str
	@param prefix: Name prefix for nodes created by function
	@type prefix: str
	'''
	# Check size of transformList list
	if len(transformList) != 5: raise Exception('Supply exactly 5 valid transforms to the transformList list argument!')
	# Check control
	if not mc.objExists(control): raise Exception('Object "'+control+'" does not exist!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(control)
	
	# Ensure attr exists and in keyable
	if not mc.objExists(control+'.'+attr):
		mc.addAttr(control,ln=attr,at='double',min=0.0,max=1.0,dv=0.5,k=True)
	
	# Create point constraints
	pointConstraint1 = prefix+'_round_01_pointConstraint'
	pointConstraint1 = mc.pointConstraint([transformList[2],transformList[0]],transformList[1],w=1,mo=False,n=pointConstraint1)[0]
	pointConstraint2 = prefix+'_round_02_pointConstraint'
	pointConstraint2 = mc.pointConstraint([transformList[2],transformList[4]],transformList[3],w=1,mo=False,n=pointConstraint2)[0]
	
	# Get target alias lists
	targetAliasList1 = targetAliasList(pointConstraint1)
	targetAliasList2 = targetAliasList(pointConstraint2)
	
	# Setup constraint weight control
	mc.connectAttr(control+'.'+attr,pointConstraint1+'.'+targetAliasList1[1],force=True)
	mc.connectAttr(control+'.'+attr,pointConstraint2+'.'+targetAliasList2[1],force=True)
	# Setup reverse connection
	reverseNode = mc.createNode('reverse',n=prefix+'_rd01_rvn')
	mc.connectAttr(control+'.'+attr, reverseNode+'.inputX',force=True)
	mc.connectAttr(reverseNode+'.outputX',pointConstraint1+'.'+targetAliasList1[0],force=True)
	mc.connectAttr(reverseNode+'.outputX',pointConstraint2+'.'+targetAliasList2[0],force=True)
	
	# Return point constraints
	return [pointConstraint1,pointConstraint2]

