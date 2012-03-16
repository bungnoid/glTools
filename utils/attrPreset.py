import maya.mel as mm
import maya.cmds as mc

import os

def presetExists(nodeType,preset):
	'''
	Check if a specified preset exists for a certain node type
	@param nodeType: Node type to check preset for
	@type nodeType: str
	@param preset: Preset to ckeck for
	@type preset: str
	'''
	# Create temp node
	node = mc.createNode(nodeType,n='temp_'+nodeType)
	
	# Check if preset is available
	try:
		mm.eval('applyAttrPreset '+node+' '+preset+' 1.0')
		p = mc.listRelatives(node,p=True)
		if p: mc.delete(p)
		else: mc.delete(node)
	except:
		print 
		return False
	else:
		return True

def listNodePreset(nodeType):
	'''
	'''
	# Get MAYA_PRESET_PATH
	presetPathList = []
	presetPathList.extend(os.getenv('MAYA_PRESET_PATH').split(':'))
	presetPathList.extend(os.getenv('MAYA_SCRIPT_PATH').split(':'))
	
	# Check available presets
	presetList = []
	for presetPath in presetPathList:
		
		# Get attrPreset subdirectory
		path = presetPath+'/attrPresets/'
		if not os.path.isdir(path): continue
		
		# Get node type subdirectories
		nodeDirList = os.listdir(path)
		if nodeDirList.count(nodeType):
			
			# Get nodeType subdirectory
			path += '/'+nodeType+'/'
			if not  os.path.isdir(path): continue
			
			# Get attrPreset file list
			attrPresetList = os.listdir(path)
			for attrPreset in attrPresetList:
				if attrPreset.endswith('.mel'):
					presetList.append(attrPreset.replace('.mel',''))
	
	# Return result
	return list(set(presetList))

def apply(nodeList,preset,amount=1.0):
	'''
	'''
	# Check nodeList argument type
	if type(nodeList) == str or type(nodeList) == unicode: nodeList = [nodeList]
	
	# Check nodes exist
	nodeTypeList = []
	for node in nodeList:
		if not mc.objExists(node):
			raise Exception('Node "'+node+'" does not exist!!')
		nodeTypeList.append(mc.objectType(node))
	
	# Check preset is available for node types
	nodeTypeList = list(set(nodeTypeList))
	for nodeType in nodeTypeList:
		if not presetExists(nodeType,preset):
			raise Exception('No preset "'+preset+'" available for nodeType "'+nodeType+'"!')
	
	# Apply preset
	for node in nodeList:
		#mm.eval('applyPresetToNode "'+node+'" "" "" "'+preset+'" '+str(amount))
		mm.eval('applyAttrPreset '+node+' '+preset+' '+str(amount))
	
	# Select nodeList
	mc.select(nodeList)

def save(node,preset,replaceExisting=False):
	'''
	'''
	# Check node
	if not mc.objExists(node):
		raise Exception('Node "'+node+'" does not exist!')
	
	# Get ndoe type
	nodeType = mc.objectType(node)
	
	# Check preset
	if presetExists(nodeType,preset):
		if not replaceExisting:
			raise Exception('Attr preset "'+preset+'" for node type "'+nodeType+'" already exists! Set replaceExisting=True to overwrite!')
		else:
			print('Overwritting existing "'+preset+'" preset for node type "'+nodeType+'"!')
	
	# Save preset
	mm.eval('saveAttrPreset '+node+' '+preset+' false')
	
	# Return result
	return preset
