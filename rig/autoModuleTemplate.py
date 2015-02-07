import maya.cmds as mc

import glTools.rig.module.base
import glTools.rig.module.fkChain
import glTools.rig.module.ikChain

import glTools.tools.controlBuilder

def moduleTemplateDialog( buildMethod ):
	'''
	Create a basic prompt dialog to allow the user to provide a name for the module
	'''
	# Raise Prompt Dialog - Get Module Name
	result = mc.promptDialog(	title='Module Name',
								message='Enter Module Name:',
								button=['Create', 'Cancel'],
								defaultButton='Create',
								cancelButton='Cancel',
								dismissString='Cancel'	)
	
	
	if result == 'Create':
		moduleName = mc.promptDialog(q=True,text=True)
		if moduleName: buildMethod(moduleName)

def moduleTemplate(	moduleName,
					moduleType,
					moduleNodes=[]	):
	'''
	Create base module template group
	@param moduleName: Module name
	@type moduleName: str
	@param moduleType: Module name
	@type moduleType: str
	@param moduleNodes: Existing module nodes to parent to module template group
	@type moduleNodes: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	moduleTemplateName = moduleName+'_moduleTemplate'
	if mc.objExists(moduleTemplateName):
		raise Exception('Module template group "'+moduleTemplateName+'" already exists!!')
	
	# ================================
	# - Create Module Template Group -
	# ================================
	
	moduleTemplateGrp = mc.group(em=True,n=moduleTemplateName)
	
	# ==================================
	# - Add Module Template Attributes -
	# ==================================
	
	# Module Type
	mc.addAttr(moduleTemplateGrp,ln='moduleTemplate',dt='string')
	mc.setAttr(moduleTemplateGrp+'.moduleTemplate',moduleType,type='string')
	mc.setAttr(moduleTemplateGrp+'.moduleTemplate',l=True)
	
	# Module Name
	mc.addAttr(moduleTemplateGrp,ln='moduleName',dt='string')
	mc.setAttr(moduleTemplateGrp+'.moduleName',moduleName,type='string')
	
	# Module Parent
	mc.addAttr(moduleTemplateGrp,ln='moduleParent',dt='string')
	mc.setAttr(moduleTemplateGrp+'.moduleParent','module',type='string')
	
	# Module Scale (allScale)
	mc.addAttr(moduleTemplateGrp,ln='allScale',dt='string')
	mc.setAttr(moduleTemplateGrp+'.allScale','all.uniformScale',type='string')
	
	# Template Overrides
	mc.addAttr(moduleTemplateGrp,ln='overrides',dt='string')
	mc.setAttr(moduleTemplateGrp+'.overrides','{}',type='string')
	
	# =======================
	# - Parent Module Nodes -
	# =======================
	
	if moduleNodes:
		moduleNodes = mc.ls(moduleNodes,dag=True)
		mc.parent(moduleNodes,moduleTemplateGrp)
	
	# =================
	# - Return Result -
	# =================
	
	return moduleTemplateGrp

def moduleTemplateOverrideNotes(moduleTemplateGrp,templateData):
	'''
	Add template override default value reference to the module template group notes attribute.
	@param moduleTemplateGrp: The module template group to add override notes to
	@type moduleTemplateGrp: str
	@param templateData: Module template overrides dictionary
	@type templateData: dict
	'''
	# ============================
	# - Template Overrides Notes -
	# ============================
	
	# Add Notes Attribute
	if not mc.objExists(moduleTemplateGrp+'.notes'):
		mc.addAttr(moduleTemplateGrp,ln='notes',sn='nts',dt='string',hidden=True)
	
	# Template Overrides - Notes
	templateNotes = ''
	templateNotes += '# ==============================\n'
	templateNotes += '# - Template Override Defaults -\n'
	templateNotes += '# ==============================\n'
	templateNotes += '\n'
	templateNotes += 'overrides = {\n'
	
	# Add Key/Value Notes
	keyList = templateData.keys()
	keyList.sort()
	for key in keyList:
		templateNotes += '\t'+str(key)+':'+str(templateData[key])+'\n'
	
	# Close Notes
	templateNotes += '}\n'
	
	# Set Notes value
	mc.setAttr(moduleTemplateGrp+'.notes',templateNotes,type='string')
	
	# Return Result
	return templateNotes

def checkModuleTemplate( moduleTemplateGrp ):
	'''
	Check for standard module template elements.
	Raise Exception if anything is missing or incorrect.
	@param moduleTemplateGrp: The module template group to perform checks on
	@type moduleTemplateGrp: str
	'''
	# Check Module Template Group
	if not mc.objExists(moduleTemplateGrp):
		raise Exception('Module template group "'+moduleTemplateGrp+'" does not exist!')
	if not mc.attributeQuery('moduleTemplate',n=moduleTemplateGrp,ex=True):
		raise Exception('Module template attribute "'+moduleTemplateGrp+'.moduleTemplate'+'" does not exist!')
	
	# Check Module Template Attributes
	if not mc.attributeQuery('moduleName',n=moduleTemplateGrp,ex=True):
		raise Exception('Module template attribute "'+moduleTemplateGrp+'.moduleName'+'" does not exist!')
	if not mc.attributeQuery('moduleParent',n=moduleTemplateGrp,ex=True):
		raise Exception('Module template attribute "'+moduleTemplateGrp+'.moduleParent'+'" does not exist!')
	if not mc.attributeQuery('allScale',n=moduleTemplateGrp,ex=True):
		raise Exception('Module template attribute "'+moduleTemplateGrp+'.allScale'+'" does not exist!')
	if not mc.attributeQuery('overrides',n=moduleTemplateGrp,ex=True):
		raise Exception('Module template attribute "'+moduleTemplateGrp+'.overrides'+'" does not exist!')

def baseModuleTemplate(		moduleName,
							moduleNodes	=	[],
							asset_name = '',
							asset_type = 'char',
							scale = 10.0,
							configCtrl = False,
							followCtrl = False,
							constraintCtrl = False,
							labelText = False ):
	'''
	Create base module template group
	@param moduleName: Module name
	@type moduleName: str
	@param moduleNodes: Existing module nodes to parent to module template group
	@type moduleNodes: list
	@param attachParent: Attach joint parent. If empty, use module influence group.
	@type attachParent: str
	@param asset_name: Asset name
	@type asset_name: str
	@param asset_type: Asset type
	@type asset_type: str
	@param scale: Base rig scale
	@type scale: str
	@param configCtrl: Add config control to base module
	@type configCtrl: str
	@param followCtrl: Add follow control to base module
	@type followCtrl: bool
	@param constraintCtrl: Add constraint control to base module
	@type constraintCtrl: bool
	@param labelText: Add label shape to base module
	@type labelText: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	#
	
	# ================================
	# - Create Module Template Group -
	# ================================
	
	moduleTemplateGrp = moduleTemplate(	moduleName = moduleName,
										moduleType = 'base',
										moduleNodes = moduleNodes	)
	
	# ==================================
	# - Add Module Template Attributes -
	# ==================================
	
	# Asset Name
	mc.addAttr(moduleTemplateGrp,ln='asset_name',dt='string')
	mc.setAttr(moduleTemplateGrp+'.asset_name',asset_name,type='string')
	
	# Asset Type
	mc.addAttr(moduleTemplateGrp,ln='asset_type',dt='string')
	mc.setAttr(moduleTemplateGrp+'.asset_type',asset_type,type='string')
	
	# Scale
	mc.addAttr(moduleTemplateGrp,ln='rigScale',at='float',min=0.0,dv=1.0)
	mc.setAttr(moduleTemplateGrp+'.rigScale',scale)
	mc.setAttr(moduleTemplateGrp+'.rigScale',cb=False)
	
	# Config Control
	mc.addAttr(moduleTemplateGrp,ln='configCtrl',at='bool')
	mc.setAttr(moduleTemplateGrp+'.configCtrl',configCtrl)
	mc.setAttr(moduleTemplateGrp+'.configCtrl',cb=False)
	
	# Follow Control
	mc.addAttr(moduleTemplateGrp,ln='followCtrl',at='bool')
	mc.setAttr(moduleTemplateGrp+'.followCtrl',followCtrl)
	mc.setAttr(moduleTemplateGrp+'.followCtrl',cb=False)
	
	# Constraint Control
	mc.addAttr(moduleTemplateGrp,ln='constraintCtrl',at='bool')
	mc.setAttr(moduleTemplateGrp+'.constraintCtrl',constraintCtrl)
	mc.setAttr(moduleTemplateGrp+'.constraintCtrl',cb=False)
	
	# Label
	mc.addAttr(moduleTemplateGrp,ln='labelText',at='bool')
	mc.setAttr(moduleTemplateGrp+'.labelText',labelText)
	mc.setAttr(moduleTemplateGrp+'.labelText',cb=False)
	
	# Template Overrides
	templateData = glTools.rig.module.base.BaseModule().templateData
	moduleTemplateOverrideNotes(moduleTemplateGrp,templateData)
	mc.setAttr(moduleTemplateGrp+'.overrides',str(templateData),type='string')
	
	# =================
	# - Return Result -
	# =================
	
	return moduleTemplateGrp

def fkChainModuleTemplate(	moduleName,
							moduleNodes	=	[],
							attachParent=	'',
							startJoint	=	'',
							endJoint	=	'',
							controlShape =	'circle',
							endCtrl 	=	False,
							ctrlPosition =	[0,0,0],
							ctrlRotate 	=	[0,0,0],
							ctrlOrient 	=	True,
							ctrlScale 	=	1.0,
							ctrlLod 	=	'primary'	):
	'''
	Create fkChain module template group node
	@param moduleName: Module name
	@type moduleName: str
	@param moduleNodes: Existing module nodes to parent to module template group
	@type moduleNodes: list
	@param attachParent: Attach joint parent. If empty, use module influence group.
	@type attachParent: str
	@param startJoint: Start joint of chain
	@type startJoint: str
	@param endJoint: End joint of chain
	@type endJoint: str
	@param controlShape: Control shape type
	@type controlShape: str
	@param endCtrl: Create control shape for end joint
	@type endCtrl: bool
	@param ctrlPosition: Controls shape position offset
	@type ctrlPosition: list or tuple
	@param ctrlRotate: Controls shape rotation offset
	@type ctrlRotate: list or tuple
	@param ctrlOrient: Orient control shape to joint
	@type ctrlOrient: bool
	@param ctrlScale: Controls shape scale
	@type ctrlScale: float
	@param ctrlLod: Control level of detail (LOD)
	@type ctrlLod: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Control Shape
	ctrlShapeList = glTools.tools.controlBuilder.ControlBuilder().controlType
	if not ctrlShapeList.count(controlShape):
		raise Exception('Unsupported control shape! ("'+controlShape+'")')
	
	# ================================
	# - Create Module Template Group -
	# ================================
	
	moduleTemplateGrp = moduleTemplate(	moduleName = moduleName,
										moduleType = 'fkChain',
										moduleNodes = moduleNodes	)
	
	# ==================================
	# - Add Module Template Attributes -
	# ==================================
	
	# Attach Parent
	mc.addAttr(moduleTemplateGrp,ln='attachParent',dt='string')
	mc.setAttr(moduleTemplateGrp+'.attachParent',attachParent,type='string')
	
	# Start Joint
	mc.addAttr(moduleTemplateGrp,ln='startJoint',dt='string')
	mc.setAttr(moduleTemplateGrp+'.startJoint',startJoint,type='string')
	
	# End Joint
	mc.addAttr(moduleTemplateGrp,ln='endJoint',dt='string')
	mc.setAttr(moduleTemplateGrp+'.endJoint',startJoint,type='string')
	
	# Control Shape
	mc.addAttr(moduleTemplateGrp,ln='controlShape',at='enum',en=':'.join(ctrlShapeList))
	mc.setAttr(moduleTemplateGrp+'.controlShape',ctrlShapeList.index(controlShape))
	
	# End Control
	mc.addAttr(moduleTemplateGrp,ln='endControl',at='bool')
	mc.setAttr(moduleTemplateGrp+'.endControl',endCtrl)
	mc.setAttr(moduleTemplateGrp+'.endControl',cb=False)
	
	# Control Position Offset
	mc.addAttr(moduleTemplateGrp,ln='controlPositionOffset',at='double3')
	mc.addAttr(moduleTemplateGrp,ln='controlPositionOffsetX',at='double',parent='controlPositionOffset')
	mc.addAttr(moduleTemplateGrp,ln='controlPositionOffsetY',at='double',parent='controlPositionOffset')
	mc.addAttr(moduleTemplateGrp,ln='controlPositionOffsetZ',at='double',parent='controlPositionOffset')
	mc.setAttr(moduleTemplateGrp+'.controlPositionOffset',*ctrlPosition)
	mc.setAttr(moduleTemplateGrp+'.controlPositionOffset',cb=False)
	
	# Control Rotate Offset
	mc.addAttr(moduleTemplateGrp,ln='controlRotateOffset',at='double3')
	mc.addAttr(moduleTemplateGrp,ln='controlRotateOffsetX',at='double',parent='controlRotateOffset')
	mc.addAttr(moduleTemplateGrp,ln='controlRotateOffsetY',at='double',parent='controlRotateOffset')
	mc.addAttr(moduleTemplateGrp,ln='controlRotateOffsetZ',at='double',parent='controlRotateOffset')
	mc.setAttr(moduleTemplateGrp+'.controlRotateOffset',*ctrlRotate)
	mc.setAttr(moduleTemplateGrp+'.controlRotateOffset',cb=False)
	
	# Control Orient
	mc.addAttr(moduleTemplateGrp,ln='controlOrient',at='bool')
	mc.setAttr(moduleTemplateGrp+'.controlOrient',ctrlOrient)
	mc.setAttr(moduleTemplateGrp+'.controlOrient',cb=False)
	
	# Control Scale
	mc.addAttr(moduleTemplateGrp,ln='controlScale',at='float',min=0.0,dv=1.0)
	mc.setAttr(moduleTemplateGrp+'.controlScale',ctrlScale)
	mc.setAttr(moduleTemplateGrp+'.controlScale',cb=False)
	
	# Control LOD
	ctrlLodList = ['primary','secondary','tertiary']
	mc.addAttr(moduleTemplateGrp,ln='controlLod',at='enum',en=':primary:secondary:tertiary:')
	mc.setAttr(moduleTemplateGrp+'.controlLod',ctrlLodList.index(ctrlLod))
	mc.setAttr(moduleTemplateGrp+'.controlLod',cb=False)
	
	# Template Override Defaults - Notes
	templateData = glTools.rig.module.fkChain.FkChainModule().templateData
	moduleTemplateOverrideNotes(moduleTemplateGrp,templateData)
	
	# =================
	# - Return Result -
	# =================
	
	return moduleTemplateGrp

def ikChainModuleTemplate(	moduleName,
							moduleNodes		=	[],
							attachParent	=	'',
							startJoint		=	'',
							endJoint		=	'',
							ikSolver 		=	'ikSCsolver',
							poleVectorPos 	=	'',
							orientIkCtrl 	=	False,
							fkToggle	 	=	False,
							blendAttr		=	'',
							ctrlLod			=	'primary'	):
	'''
	Create fkChain module template group
	@param moduleName: Module name
	@type moduleName: str
	@param moduleNodes: Existing module nodes to parent to module template group
	@type moduleNodes: list
	@param attachParent: Attach joint parent. If empty, use module influence group.
	@type attachParent: str
	@param startJoint: Start joint of chain
	@type startJoint: str
	@param endJoint: End joint of chain
	@type endJoint: str
	@param ikSolver: Ik solver to apply to chain
	@type ikSolver: str
	@param poleVectorPos: Transform for IK pole vector position
	@type poleVectorPos: str
	@param orientIkCtrl: Orient IK control to joint
	@type orientIkCtrl: bool
	@param fkToggle: Enable IK/FK toggle
	@type fkToggle: bool
	@param blendAttr: IK/FK blend attribute
	@type blendAttr: str
	@param ctrlLod: Control level of detail (LOD)
	@type ctrlLod: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# IK Solver
	ikSolverList = ['ikSCsolver','ikRPsolver']
	if not ikSolverList.count(ikSolver):
		raise Exception('Invalid IkSolver - "'+ikSolver+'"!')
		
	# ================================
	# - Create Module Template Group -
	# ================================
	
	moduleTemplateGrp = moduleTemplate(	moduleName = moduleName,
										moduleType = 'ikChain',
										moduleNodes = moduleNodes	)
	
	# ==================================
	# - Add Module Template Attributes -
	# ==================================
	
	# Attach Parent
	mc.addAttr(moduleTemplateGrp,ln='attachParent',dt='string')
	mc.setAttr(moduleTemplateGrp+'.attachParent',attachParent,type='string')
	
	# Start Joint
	mc.addAttr(moduleTemplateGrp,ln='startJoint',dt='string')
	mc.setAttr(moduleTemplateGrp+'.startJoint',startJoint,type='string')
	
	# End Joint
	mc.addAttr(moduleTemplateGrp,ln='endJoint',dt='string')
	mc.setAttr(moduleTemplateGrp+'.endJoint',startJoint,type='string')
	
	# Control Shape
	mc.addAttr(moduleTemplateGrp,ln='ikSolver',at='enum',en=':'.join(ikSolverList))
	mc.setAttr(moduleTemplateGrp+'.ikSolver',ikSolverList.index(ikSolver))
	mc.setAttr(moduleTemplateGrp+'.ikSolver',cb=False)
	
	# Pole Vector
	mc.addAttr(moduleTemplateGrp,ln='poleVectorTransform',dt='string')
	mc.setAttr(moduleTemplateGrp+'.poleVectorTransform',poleVectorPos,type='string')
	
	# Orient IK Control
	mc.addAttr(moduleTemplateGrp,ln='orientIkControl',at='bool')
	mc.setAttr(moduleTemplateGrp+'.orientIkControl',orientIkCtrl)
	mc.setAttr(moduleTemplateGrp+'.orientIkControl',cb=False)
	
	# FK Toggle
	mc.addAttr(moduleTemplateGrp,ln='enableFKToggle',at='bool')
	mc.setAttr(moduleTemplateGrp+'.enableFKToggle',fkToggle)
	mc.setAttr(moduleTemplateGrp+'.enableFKToggle',cb=False)
	
	# IK/FK Blend Attribute
	mc.addAttr(moduleTemplateGrp,ln='ikFkBlendAttribute',dt='string')
	mc.setAttr(moduleTemplateGrp+'.ikFkBlendAttribute',blendAttr,type='string')
	
	# Control LOD
	ctrlLodList = ['primary','secondary','tertiary']
	mc.addAttr(moduleTemplateGrp,ln='controlLod',at='enum',en=':primary:secondary:tertiary:')
	mc.setAttr(moduleTemplateGrp+'.controlLod',ctrlLodList.index(ctrlLod))
	mc.setAttr(moduleTemplateGrp+'.controlLod',cb=False)
	
	# Template Overrides
	templateData = glTools.rig.module.ikChain.IkChainModule().templateData
	moduleTemplateOverrideNotes(moduleTemplateGrp,templateData)
	#overrideStr = "{'ikCtrlScale': 0.2, 'ikCtrlShape': 'box', 'ikCtrlRotate': [0, 0, 0], 'fkCtrlShape': 'circle','fkCtrlScale': 0.3,'fkCtrlRotate': [0, 90, 0], 'blendAttr': 'ikFkBlend'}"
	mc.setAttr(moduleTemplateGrp+'.overrides',str(templateData),type='string')
	
	# =================
	# - Return Result -
	# =================
	
	return moduleTemplateGrp

