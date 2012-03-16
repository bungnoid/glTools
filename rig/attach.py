import maya.cmds as mc

import glTools.utils.channelState

def switchConstraint(attachType,transform,targetList,aliasList=[],createTarget=False,switchCtrl='',switchAttr='',prefix=''):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Prefix
	if not prefix: prefix = transform
	
	# Transform
	if not mc.objExists(transform):
		raise Exception('Transform "'+transform+'" does not exist!')
	
	# Target
	for target in targetList:
		if not mc.objExists(target):
			raise Exception('Target transform "'+target+'" does not exist!')
	
	# Switch Control
	if switchCtrl and not mc.objExists(switchCtrl):
		raise Exception('Switch control "'+switchCtrl+'" does not exist!')
	
	# Switch Attribute
	if switchCtrl and not mc.objExists(switchCtrl+'.'+switchAttr):
		if not aliasList: aliasList = targetlist
		aliasStr = ':'.join(aliasList)+':'
		mc.addAttr(switchCtrl,ln=switchAttr,at='enum',en=aliasStr,k=True)
		
	# Target Alias List
	if not aliasList: aliasList = targetList
	
	# ============================
	# - Create Target Transforms -
	# ============================
	
	# Initialize new target list
	cTargetList = []
	if createTarget:
		
		for t in range(len(targetList)):
			
			# Duplicate transform to generate new target
			cTarget = mc.duplicate(transform,po=True,n=prefix+'_'+aliasList[t]+'_target')[0]
			cTarget = mc.parent(cTarget,targetList[t])[0]
			
			# Attach joint display
			mc.setAttr(cTarget+'.overrideEnabled',1)
			mc.setAttr(cTarget+'.overrideLevelOfDetail',1)
			mc.setAttr(cTarget+'.v',0)
			
			# Append new target list
			cTargetList.append(cTarget)
		
		# Update target list
		targetList = cTargetList
		
		# Set Channel States
		chStateUtil = glTools.utils.channelState.ChannelState()
		chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,1],objectList=targetList)
	
	# =====================
	# - Create Constraint -
	# =====================
	
	if attachType == 'point':
		constraint = mc.pointConstraint(targetList,transform,mo=False,n=prefix+'_pointConstraint')[0]
		wtAlias = mc.pointConstraint(constraint,q=True,wal=True)
	if attachType == 'orient':
		constraint = mc.orientConstraint(targetList,transform,mo=False,n=prefix+'_orientConstraint')[0]
		wtAlias = mc.orientConstraint(constraint,q=True,wal=True)
	if attachType == 'parent':
		constraint = mc.parentConstraint(targetList,transform,mo=False,n=prefix+'_parentConstraint')[0]
		wtAlias = mc.parentConstraint(constraint,q=True,wal=True)
	
	# ==========================
	# - Connect to Switch Attr -
	# ==========================
	
	if switchCtrl:
	
		# Initialize switch list
		pointSwitchNodes = []
		for i in range(len(targetList)):
			
			# Create Switch Node
			switchNode = mc.createNode('condition',n=prefix+'_'+wtAlias[i]+'_condition')
			
			# Connect to switch attr
			mc.connectAttr(switchCtrl+'.'+switchAttr,switchNode+'.firstTerm',f=True)
			mc.setAttr(switchNode+'.secondTerm',i)
			mc.setAttr(switchNode+'.operation',0) # Equal
			mc.setAttr(switchNode+'.colorIfTrue',1,0,0)
			mc.setAttr(switchNode+'.colorIfFalse',0,1,1)
			
			# Connect to constraint target weight
			mc.connectAttr(switchNode+'.outColorR',constraint+'.'+wtAlias[i])
			
			# Append switch list
			pointSwitchNodes.append(switchNode)
	
	# =================
	# - Return Result -
	# =================
	
	return constraint