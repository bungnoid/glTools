import maya.cmds as mc

import glTools.tools.controlBuilder

import glTools.nrig.module.fkChain
import glTools.nrig.module.ikChain

import autoModuleTemplate

import ast

def checkModuleTemplate(moduleTemplateGrp,moduleType,moduleAttrs):
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
	
	# Check Module Type
	moduleTemplateType = mc.getAttr(moduleTemplateGrp+'.moduleTemplate')
	if moduleTemplateType != moduleType:
		raise Exception('Expecting module type "'+moduleType+'", found "'+moduleTemplateType+'"!')
	
	# Check Module Attributes
	for attr in moduleAttrs:
		if not mc.attributeQuery(attr,n=moduleTemplateGrp,ex=True):
			raise Exception('Base module template attribute "'+moduleTemplateGrp+'.'+attr+'" does not exist!')

def moduleBuildAll():
	'''
	Build all module from the module template groups found in the current scene.
	Any node with a ".moduleTemplate" attribute will be considered as a module template group.
	'''
	# Find All Module Template Groups
	moduleTemplateList = mc.ls('*.moduleTemplate',o=True)
	
	# Build Modules
	resultList = []
	for moduleTemplateGrp in moduleTemplateList:
		result = moduleBuild( moduleTemplateGrp )
		resultList.append(result)
	
	# Return Result
	return resultList

def moduleBuild( moduleTemplateGrp ):
	'''
	Build a module based on the specified module template group.
	@param moduleTemplateGrp: The module template group to build the module from.
	@type moduleTemplateGrp: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Module Type
	if not mc.attributeQuery('moduleTemplate',n=moduleTemplateGrp,ex=True):
		raise Exception('Module template attribute "'+moduleTemplateGrp+'.moduleTemplate'+'" does not exist!')
	moduleType = mc.getAttr(moduleTemplateGrp+'.moduleTemplate')
	
	# ===================================
	# - Build Module From Template Data -
	# ===================================
	
	# Initialize Result
	result = None
	
	# Build Module
	if moduleType == 'base': result = baseModuleBuild(	moduleTemplateGrp )
	elif moduleType == 'fkChain': result = fkChainModuleBuild(	moduleTemplateGrp )
	elif moduleType == 'ikChain': result = ikChainModuleBuild(	moduleTemplateGrp )
	
	# =================
	# - Return Result -
	# =================
	
	return result

def baseModuleBuild( moduleTemplateGrp ):
	'''
	Build a Base module based on the specified module template group.
	@param moduleTemplateGrp: The module template group to build the FkChain module from.
	@type moduleTemplateGrp: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Define Attribute List
	attrList = [	'moduleName',
					'moduleParent',
					'overrides',
					'asset_name',
					'asset_type',
					'rigScale',
					'configCtrl',
					'followCtrl',
					'constraintCtrl',
					'labelText'	]
	
	# Check Module Template
	checkModuleTemplate(moduleTemplateGrp,moduleType='base',moduleAttrs=attrList)
	
	# =========================
	# - Get Raw Template Data -
	# =========================
	
	data = {}
	for attr in attrList: data[attr] = mc.getAttr(moduleTemplateGrp+'.'+attr)
	
	# Encode template override dictionary
	overrides = ast.literal_eval(data['overrides'])
	
	# ===================================
	# - Build Module From Template Data -
	# ===================================
	
	base = glTools.nrig.module.base.BaseModule()
	result = base.build(	name = data['asset_name'],
							type = data['asset_type'],
							scale = data['rigScale'],
							configCtrl = bool(data['configCtrl']),
							followCtrl = bool(data['followCtrl']),
							constraintCtrl = bool(data['constraintCtrl']),
							labelText = bool(data['labelText']),
							overrides = overrides,
							prefix = data['moduleName']	)
	
	# =================
	# - Return Result -
	# =================
	
	return result

def fkChainModuleBuild(	moduleTemplateGrp ):
	'''
	Build an FkChain module based on the specified module template group.
	@param moduleTemplateGrp: The module template group to build the FkChain module from.
	@type moduleTemplateGrp: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Define Attribute List
	attrList = [	'moduleName',
					'moduleParent',
					'allScale',
					'overrides',
					'attachParent',
					'startJoint',
					'endJoint',
					'controlShape',
					'endControl',
					'controlPositionOffset',
					'controlRotateOffset',
					'controlOrient',
					'controlScale',
					'controlLod'	]
	
	# Check Module Template
	checkModuleTemplate(moduleTemplateGrp,moduleType='fkChain',moduleAttrs=attrList)
	
	# =========================
	# - Get Raw Template Data -
	# =========================
	
	data = {}
	for attr in attrList: data[attr] = mc.getAttr(moduleTemplateGrp+'.'+attr)
	
	# Encode template override dictionary
	overrides = ast.literal_eval(data['overrides'])
	
	# Control Offset
	controlPosition = data['controlPositionOffset'][0]
	controlRotate = data['controlRotateOffset'][0]
	
	# Get control shape
	ctrlShapeList = glTools.tools.controlBuilder.ControlBuilder().controlType
	controlShape = ctrlShapeList[data['controlShape']]
	
	# Get control LOD
	controlLod = ['primary','secondary','tertiary'][data['controlLod']]
	
	# ===================================
	# - Build Module From Template Data -
	# ===================================
	
	fkChain = glTools.nrig.module.fkChain.FkChainModule()
	result = fkChain.build(	startJoint = 	data['startJoint'],
							endJoint = 		data['endJoint'],
							controlShape = 	controlShape,
							endCtrl = 		data['endControl'],
							ctrlPosition = 	controlPosition,
							ctrlRotate = 	controlRotate,
							ctrlOrient = 	data['controlOrient'],
							ctrlScale = 	data['controlScale'],
							ctrlLod = 		controlLod,
							moduleGrp = 	data['moduleParent'],
							attachParent = 	data['attachParent'],
							allScale = 		data['allScale'],
							overrides = 	overrides,
							prefix = 		data['moduleName']	)
	
	# =================
	# - Return Result -
	# =================
	
	return result

def ikChainModuleBuild(	moduleTemplateGrp ):
	'''
	Build an IkChain module based on the specified module template group.
	@param moduleTemplateGrp: The module template group to build the IkChain module from.
	@type moduleTemplateGrp: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Define Attribute List
	attrList = [	'moduleName',
					'moduleParent',
					'allScale',
					'overrides',
					'attachParent',
					'startJoint',
					'endJoint',
					'ikSolver',
					'poleVectorTransform',
					'orientIkControl',
					'enableFKToggle',
					'ikFkBlendAttribute',
					'controlLod'	]
	
	# Check Module Template
	checkModuleTemplate(moduleTemplateGrp,moduleType='ikChain',moduleAttrs=attrList)
	
	# =========================
	# - Get Raw Template Data -
	# =========================
	
	data = {}
	for attr in attrList: data[attr] = mc.getAttr(moduleTemplateGrp+'.'+attr)
	
	# Encode template override dictionary
	overrides = ast.literal_eval(data['overrides'])
	
	# Get control LOD
	controlLod = ['primary','secondary','tertiary'][data['controlLod']]
	
	# Get ikSolver
	ikSolver = ['ikSCsolver','ikRPsolver'][data['ikSolver']]
	
	# ===================================
	# - Build Module From Template Data -
	# ===================================
	
	ikChain = glTools.nrig.module.ikChain.IkChainModule()
	result = ikChain.build(	startJoint =	data['startJoint'],
							endJoint =		data['endJoint'],
							ikSolver =		ikSolver,
							poleVecPos =	data['poleVectorTransform'],
							orientIkCtrl =	data['orientIkControl'],
							fkToggle = 		data['enableFKToggle'],
							blendAttr = 	data['ikFkBlendAttribute'],
							ctrlLod =		controlLod,
							moduleGrp =		data['moduleParent'],
							attachParent =	data['attachParent'],
							allScale = 		data['allScale'],
							overrides =		overrides,
							prefix =		data['moduleName']	)
	
	# =================
	# - Return Result -
	# =================
	
	return result
