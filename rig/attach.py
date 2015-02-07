import maya.cmds as mc

import glTools.utils.channelState
import glTools.utils.constraint
import glTools.utils.transform

def switchConstraint(	attachType,
						transform,
						targetList,
						aliasList		= [],
						createTarget	= True,
						switchCtrl		= None,
						switchAttr		= None,
						prefix			= ''	):
	'''
	Setup a single or multi target switchable constraint based on the input arguments
	@param attachType: Attach constraint type. Accepted types are "point", "orient", "parent", "scale" and "all".
	@type attachType: str
	@param transform: The transform that will be the slave of the attach constraint.
	@type transform: str
	@param targetList: A list of transforms that will be the parent/master of the attach constraint.
	@type targetList: list
	@param aliasList: A list of name alias' for each item in targetList. Uses to populate the enum attr for constraint target switching.
	@type aliasList: list
	@param createTarget: If True, create a new null transform under the current target that will result in a zero offset constraint. If False, use the transform specified in targetList.
	@type createTarget: bool
	@param switchCtrl: The control object that will hold the constraint target switch attribute.
	@type switchCtrl: str
	@param switchAttr: Name of the constraint target switch attribute.
	@type switchAttr: str
	@param prefix: Name prefix for new nodes.
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Attach Type
	if not attachType in ['point','orient','parent','scale','all']:
		raise Exception('Invalid attach type! ("'+attachType+'")')
	
	# Prefix
	if not prefix: prefix = transform
	
	# Transform
	if not mc.objExists(transform):
		raise Exception('Transform "'+transform+'" does not exist!')
	
	# Target
	for target in targetList:
		if not mc.objExists(target):
			raise Exception('Target transform "'+target+'" does not exist!')
	
	# Target Alias List
	if not aliasList: aliasList = targetList
	
	# Switch Control
	if switchCtrl and not mc.objExists(switchCtrl):
		raise Exception('Switch control "'+switchCtrl+'" does not exist!')
	
	# =====================
	# - Switch Attributes -
	# =====================
	
	# Create Switch Attribute
	if switchCtrl:
		if not mc.objExists(switchCtrl+'.'+switchAttr):
			mc.addAttr(switchCtrl,ln=switchAttr,at='enum',en=':'.join(aliasList),k=True)
		
	# ============================
	# - Create Target Transforms -
	# ============================
	
	# Initialize new target list
	if createTarget:
		
		# For Each Target
		cTargetList = []
		for t in range(len(targetList)):
			
			# Duplicate transform to generate new target
			cTarget = mc.createNode('transform',n=prefix+'_'+aliasList[t]+'_target')
			glTools.utils.transform.match(cTarget,transform)
			
			# Parent Control Target to Current Constraint Target
			try: cTarget = mc.parent(cTarget,targetList[t])[0]
			except: raise Exception('Unable to parent target null "'+cTarget+'" to target transform "'+targetList[t]+'"!')
			
			# Target Display Override
			glTools.utils.base.displayOverride(cTarget,overrideEnable=1,overrideDisplay=2)
			
			# Append to Target List
			cTargetList.append(cTarget)
		
		# Update target list
		targetList = cTargetList
		
		# Set Channel States
		chStateUtil = glTools.utils.channelState.ChannelState()
		chStateUtil.setFlags([2,2,2,2,2,2,2,2,2,2],objectList=targetList)
	
	# =====================
	# - Create Constraint -
	# =====================
	
	# Initialize scale constraint valiables ("all" only)
	scaleConstraint = None
	scaleWtAlias = []
	
	if attachType == 'point':
		constraint = mc.pointConstraint(targetList,transform,mo=False,n=prefix+'_pointConstraint')[0]
		wtAlias = mc.pointConstraint(constraint,q=True,wal=True)
	if attachType == 'orient':
		constraint = mc.orientConstraint(targetList,transform,mo=False,n=prefix+'_orientConstraint')[0]
		wtAlias = mc.orientConstraint(constraint,q=True,wal=True)
	if attachType == 'parent':
		constraint = mc.parentConstraint(targetList,transform,mo=False,n=prefix+'_parentConstraint')[0]
		wtAlias = mc.parentConstraint(constraint,q=True,wal=True)
	if attachType == 'scale':
		constraint = mc.scaleConstraint(targetList,transform,mo=False,n=prefix+'_scaleConstraint')[0]
		wtAlias = mc.parentConstraint(constraint,q=True,wal=True)
	if attachType == 'all':
		constraint = mc.parentConstraint(targetList,transform,mo=False,n=prefix+'_parentConstraint')[0]
		wtAlias = mc.parentConstraint(constraint,q=True,wal=True)
		scaleConstraint = mc.scaleConstraint(targetList,transform,mo=False,n=prefix+'_scaleConstraint')[0]
		scaleWtAlias = mc.scaleConstraint(scaleConstraint,q=True,wal=True)
	
	# =============================
	# - Connect to Switch Control -
	# =============================
	
	if switchCtrl:
	
		# Initialize switch list
		switchNodes = []
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
			
			# Connect to scale constraint, if necessary ("all" only)
			if scaleConstraint:
				mc.connectAttr(switchNode+'.outColorR',scaleConstraint+'.'+scaleWtAlias[i])
			
			# Append switch list
			switchNodes.append(switchNode)
	
	# =================
	# - Return Result -
	# =================
	
	return constraint

def switchTargetVisibility(	switchConstraint,
							targetVisAttr	= None,
							targetLabels	= False	):
	'''
	Create a switch target visibility toggle for the specified switchConstraint.
	Optionally, add target label visibility.
	@param switchConstraint: Switch constraint node to create visibility toggle for.
	@type switchConstraint: str
	@param targetVisAttr: Switch toggle control attribute name.
	@type targetVisAttr: str
	@param targetLabels: Enable target label visibility.
	@type targetLabels: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Constraint
	if not glTools.utils.constraint.isConstraint(switchConstraint):
		raise Exception('Object "'+switchConstraint+'" is not a valid constraint!')
	
	# ===============================
	# - Get Switch Constraint Nodes -
	# ===============================
	
	# Get Switch Conditions from Constraint
	switchCond = mc.ls(mc.listConnections(switchConstraint,s=True,d=False),type='condition')
	
	# Get Switch Control from Conditions
	switchAttr = list(set(mc.listConnections(switchCond,s=True,d=False,p=True)))
	if len(switchAttr) > 1: raise Exception('Multiple input attributes driving switchConstraint "'+switchConstraint+'"!')
	switchCtrl = mc.ls(switchAttr[0],o=True)[0]
	switchAttr = switchAttr[0].split('.')[-1]
	
	# Get Switch Targets from Constraint
	switchTargets = glTools.utils.constraint.targetList(switchConstraint)
	switchAlias = mc.addAttr(switchCtrl+'.'+switchAttr,q=True,en=True).split(':')
	
	# =============================
	# - Connect Target Visibility -
	# =============================
	
	# Check Target Visibility Attribute
	if not targetVisAttr: targetVisAttr = switchAttr+'Vis'
	if not mc.objExists(switchCtrl+'.'+targetVisAttr):
		mc.addAttr(switchCtrl,ln=targetVisAttr,at='enum',en='Off:On')
		mc.setAttr(switchCtrl+'.'+targetVisAttr,cb=True,l=False)
	
	# Target Label Visibility
	labelVisChoice = None
	if targetLabels:
		mc.addAttr(switchCtrl+'.'+targetVisAttr,e=True,en='Off:On:Label')
		labelVisChoice = mc.createNode('choice',n=switchAttr+'_labelVis_choice')
		mc.connectAttr(switchCtrl+'.'+targetVisAttr,labelVisChoice+'.selector',f=True)
		mc.setAttr(labelVisChoice+'.input[0]',0)
		mc.setAttr(labelVisChoice+'.input[1]',0)
		mc.setAttr(labelVisChoice+'.input[2]',1)
	
	# For Each Target
	for t in range(len(switchTargets)):
		
		# Connect Display Handle Visibility
		mc.setAttr(switchTargets[t]+'.displayHandle',1,l=True)
		mc.connectAttr(switchCtrl+'.'+targetVisAttr,switchTargets[t]+'.v',f=True)
		
		# Connect Target Label Visibility
		if targetLabels:
			labelShape = mc.createNode('annotationShape',n=switchTargets[t]+'Shape',p=switchTargets[t])
			mc.connectAttr(labelVisChoice+'.output',labelShape+'.v',f=True)
			mc.setAttr(labelShape+'.text',switchAlias[t],type='string')
			mc.setAttr(labelShape+'.displayArrow',0,l=True)