import maya.mel as mm
import maya.cmds as mc

def isCharacterDefinition(char,verbose=False):
	'''
	Check if the specified object is a valid HIK character definition.
	@param char: Object to query
	@type char: str
	@param verbose: Verbosity of feedback from command
	@type verbose: str
	'''
	# Check Object Exists
	if not mc.objExists(char):
		if verbose:
			print('Object "'+char+'" does not exist!')
		return False
	
	# Check Object Type
	if mc.objectType(char) != 'HIKCharacterNode':
		if verbose:
			print('Object "'+char+'" is not a valid "HIKCharacterNode"!')
		return False
	
	# Return Result
	return True

def characterDefinitionList():
	'''
	Return a list of character definition in the current scene.
	'''
	charList = mc.ls(type='HIKCharacterNode')
	return charList

def createCharacterDefinition(characterName=''):
	'''
	Create a new HIK character definition
	@param characterName: Name for the new character definition
	@type characterName: str
	'''
	# Check Character Name
	if characterName and isCharacterDefinition(characterName,False):
		raise Exception('Character definition "'+characterName+'" already exists!')
	if not characterName: characterName = 'Character1'
	
	# Create New Definition
	charStr = mm.eval('newCharacterWithName("'+characterName+'")')
	# Extract Definition Name from Return String - WTF!!
	char = charStr.split("'")[1]
	
	# Return Result
	return char

def getCurrentCharacter():
	'''
	Get the current active character definition.
	'''
	# get Current Character
	char = mm.eval('hikGetCurrentCharacter();')
	# Return Result
	return char

def setCurrentCharacter(char):
	'''
	Set the specified character definition as the current character.
	@param char: Character definition to set as current
	@type char: str
	'''
	# Check Character Definition
	if not isCharacterDefinition(char,verbose=True):
		raise Exception('"'+char+'" is not a valid "HIKCharacterNode"!')
	
	# Set Current Character
	mc.optionMenuGrp('hikCharacterList',e=True,v=char)
	mm.eval('hikUpdateCurrentCharacterFromUI();')
	
	# Return Result
	current_char = getCurrentCharacter()
	return current_char

def setCharacterLock(char,lock=True):
	'''
	'''
	# Check Character Definition
	if not isCharacterDefinition(char,verbose=True):
		raise Exception('"'+char+'" is not a valid "HIKCharacterNode"!')
	
	# Set Character Current
	activeChar = getCurrentCharacter()
	setCurrentCharacter(char)

def setCharacterSource(char,source):
	'''
	'''
	# Check Character Definition
	if not isCharacterDefinition(char,verbose=True):
		raise Exception('"'+char+'" is not a valid "HIKCharacterNode"!')
	
	# Set Character Source
	mm.eval('hikSetCurrentSource("'+source+'");')
	mm.eval('hikUpdateSourceList();')
	mm.eval('hikUpdateSkeletonUI();')
	
	# Return Result
	return source
