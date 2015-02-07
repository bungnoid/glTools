import maya.mel as mm
import maya.cmds as mc

import glTools.utils.clip

import os.path

def isCharSet(charSet):
	'''
	Check if the specified object is a valid character set
	@param charSet: Character set to check.
	@type charSet: str
	'''
	# Check Object Exists
	if not mc.objExists(charSet): return False
	# Check Object Type
	if not mc.objectType(charSet) == 'character': return False
	# Return Result
	return True

def create(	objectList,
			name,
			root='',
			excludeTranslate=False,
			excludeRotate=False,
			excludeScale=False,
			excludeDynamic=False,
			excludeVisibility=False ):
	'''
	Create a character set.
	@param objectList: List of objects to add to the character set.
	@type objectList: list
	@param name: Character set name.
	@type name: str
	@param root: Character set root object.
	@type root: str
	@param excludeTranslate: Character set to exclude translate channels.
	@type excludeTranslate: bool
	@param excludeRotate: Character set to exclude rotate channels.
	@type excludeRotate: bool
	@param excludeScale: Character set to exclude scale channels.
	@type excludeScale: bool
	@param excludeDynamic: Character set to exclude dynamic channels.
	@type excludeDynamic: bool
	@param excludeVisibility: Character set to exclude visibility channels.
	@type excludeVisibility: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Character Set
	if isCharSet(name):
		raise Exception('Character set "'+name+'" already exists!')
	
	# Check Root
	if root and not mc.objExists(root):
		raise Exception('Root object "'+root+'" does not exists!')
	
	# ========================
	# - Create Character Set -
	# ========================
	
	# Initialize Character Var
	char = ''
	
	if root:
		# Create With Root Node
		char = mc.character(	objectList,
								n=name,
								root=root,
								excludeTranslate=excludeTranslate,
								excludeRotate=excludeRotate,
								excludeScale=excludeScale,
								excludeDynamic=excludeDynamic,
								excludeVisibility=excludeVisibility )
	else:
		# Create Without Root Node
		char = mc.character(	objectList,
								n=name,
								excludeTranslate=excludeTranslate,
								excludeRotate=excludeRotate,
								excludeScale=excludeScale,
								excludeDynamic=excludeDynamic,
								excludeVisibility=excludeVisibility )
	
	# =================
	# - Return Result -
	# =================
	
	return char

def setCurrent(charSet):
	'''
	Set the specified character set as current.
	@param charSet: Character set to set as current.
	@type charSet: str
	'''
	# Check Character Set
	if not isCharSet(charSet):
		raise Exception('Object "'+charSet+'" is not a valid character set!')
	
	# Set Current
	mm.eval('setCurrentCharacters({"'+charSet+'"})')
	
	# Return Result
	return charSet

def getCurrent():
	'''
	Get the current character set.
	'''
	char = mm.eval('currentCharacters')
	if not char: return ''
	else: return char[0]

def bakeCharacterChannels(charSet,start=None,end=None,attrList=[]):
	'''
	Bake character set channels.
	Used to bake trax animation directly to channels
	@param charSet: Character set to bake channels for.
	@type charSet: str
	@param start: Start frame of bake results range. If empty, use timeline start frame.
	@type start: int or None
	@param end: End frame of bake results range. If empty, use timeline end frame.
	@type end: int or None
	@param attrList: Override the list of character character set attributes to bake. If empty, use attribute list from character set.
	@type attrList: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not isCharSet(charSet):
		raise Exception('Object "'+charSet+'" is not a valid character set!')
	
	# Start/End
	if start == None: start = mc.playbackOptions(min=True)
	if end == None: end = mc.playbackOptions(max=True)
	
	# =========================
	# - Character Set Details -
	# =========================
	
	# Get Character Set Channels
	charChannels = mc.sets(charSet,q=True)
	
	# Get Character Set Objects
	charObjList = mc.ls(charChannels,o=True)
	
	# Get Character Set Channel Names
	if not attrList:
		attrList = []
		for ch in charChannels:
			attr = mc.attributeName(ch,s=True)
			if not attrList.count(attr):
				attrList.append(attr)
	
	# ================
	# - Bake Results -
	# ================
	
	mc.bakeResults(charObjList,t=(1,600),at=attrList,simulation=True)
	
	# =================
	# - Return Result -
	# =================
	
	return charObjList

def removeTimelineClips(charSet):
	'''
	Remove all clip from the trax timeline for the specified character.
	@param charSet: Character set to bake channels for.
	@type charSet: str
	'''
	scheduler = mc.character(charSet,q=True,scheduler=True)
	scheduleList = mc.clipSchedule(scheduler,q=True)
	for schedule in scheduleList:
		clipInd = str(schedule).split(',')[1]
		mc.clipSchedule(scheduler,ci=int(clipInd),remove=True)

def printTimelineClips(charSet):
	'''
	'''
	scheduler = mc.character(charSet,q=True,scheduler=True)
	scheduleList = mc.clipSchedule(clip,q=True)
	for schedule in scheduleList: print schedule
