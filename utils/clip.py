import maya.mel as mm
import maya.cmds as mc

import glTools.utils.characterSet
import glTools.utils.namespace
import glTools.utils.reference

import os.path

def isClip(clip):
	'''
	Check if specified object is a valid anim clip
	@param clip: Object to check as anim clip
	@type clip: str
	'''
	# Check Object Exists
	if not mc.objExists(clip): return False
	# Check Object Type
	if not mc.objectType(clip) == 'animClip': return False
	# Return Result
	return True

def createClip(charSet,startTime=None,endTime=None,name=''):
	'''
	Create a clip from the specified character set
	@param charSet: Object to check as anim clip
	@type charSet: str
	@param startTime: Start time for clip. If None, use timeline start frame.
	@type startTime: int
	@param endTime: End time for clip. If None, use timeline end frame.
	@type endTime: int
	@param name: Clip name
	@type name: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Character Set
	if not glTools.utils.characterSet.isCharSet(charSet):
		raise Exception('Object "'+charSet+'" is not a valid character set!')
	
	# Check Name
	if not name: name = 'clip'
	
	# Check Start/End Time
	if (startTime == None) or (endTime == None):
		charList = mc.sets(charSet,q=True)
		charKeys = mc.keyframe(charList,q=True,tc=True)
		charKeys.sort()
	if startTime == None:
		startTime = charKeys[0]
	if endTime == None:
		endTime = charKeys[-1]
	
	# ===============
	# - Create Clip -
	# ===============
	
	clip = ['']
	try: clip = mc.clip(charSet, startTime=startTime, endTime=endTime, name=name )
	except: print('Error creating clip "'+name+'"!')
	else: print('Clip "'+name+'" successfully created!')
	
	# =================
	# - Return Result -
	# =================
	
	return str(clip[0])

def exportClip(clip,clipPath,force=False):
	'''
	Export clip to file
	@param clip: Clip to export to file
	@type clip: str
	@param clipPath: Clip file destination path
	@type clipPath: str
	@param force: Overwrite existing clip file.
	@type force: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Clip
	if not isClip(clip):
		raise Exception('Object "'+clip+'" is not a valid animation clip!')
	
	# Check Directory Path
	dirpath = os.path.dirname(clipPath)
	if not os.path.isdir(dirpath): os.makedirs(dirpath)
	
	# Check File Path
	if os.path.isfile(clipPath):
		if not force:
			raise Exception('File "'+clipPath+'" already exists! Use "force=True" to overwrite the existing file.')
		else:
			try: os.remove(clipPath)
			except: pass
	
	
	# Check Extension
	ext = os.path.splitext(clipPath)[1].lower()[1:]
	if not (ext == 'ma') and not (ext == 'mb'):
		raise Exception('Invalid file extension "'+ext+'"!')
	
	# =======================
	# - Source Required MEL -
	# =======================
	
	scriptsPath = mm.eval('getenv MAYA_LOCATION')+'/scripts/others'
	mm.eval('source "'+scriptsPath+'/doExportClipArgList.mel"')
	
	# ===============
	# - Export Clip -
	# ===============
	
	mc.select(clip)
	result = mm.eval('clipEditorExportClip("'+clipPath+'", "'+ext+'")')
	
	# =================
	# - Return Result -
	# =================
	
	return result

def importClip(clipPath,toChar='',toTrax=False):
	'''
	Export clip to file
	@param clipPath: Clip file source path
	@type clipPath: str
	@param toChar: Load clip to character. If empty, will be imported without character association
	@type toChar: str
	@param toTrax: Load clip directly to Trax Editor.
	@type toTrax: bool
	'''
	# Check File Path
	if not os.path.isfile(clipPath):
		raise Exception('No file exists at path "'+clipPath+'"!')
	
	# Check Extension
	ext = os.path.splitext(clipPath)[1].lower()[1:]
	if not (ext == 'ma') and not (ext == 'mb'):
		raise Exception('Invalid file extension "'+ext+'"!')
	
	# Check To Character
	if toChar:
		
		if not glTools.utils.characterSet.isCharSet(toChar):
			raise Exception('Object "'+toChar+'" is not a valid character set!')
		
		# Set Current Character
		glTools.utils.characterSet.setCurrent(toChar)
	
	else:
		
		# Get Current Character Set
		currChar = glTools.utils.characterSet.getCurrent()
		if currChar: toChar = currChar
	
	# =======================
	# - Source Required MEL -
	# =======================
	
	scriptsPath = mm.eval('getenv MAYA_LOCATION')+'/scripts/others'
	mm.eval('source "'+scriptsPath+'/doImportClipArgList.mel"')
		
	# ===============
	# - Import Clip -
	# ===============
	
	# Set Global MEL variables
	if toChar:
		mm.eval('global int $gImportClipToCharacter = 1;')
		mm.eval('global string $gImportToCharacter = "'+toChar+'";')
	if toTrax:
		mm.eval('global int $gScheduleClipOnCharacter = 1;')
	
	# Import Clip
	result = mm.eval('clipEditorImportClip("'+clipPath+'", "'+ext+'")')
	
	# Print Result
	if result: print ('Imported Clip: '+clipPath)
	
	# =================
	# - Return Result -
	# =================
	
	return result

def importClips(charSet='',clips=[],toTrax=False):
	'''
	Import trax clips to the specified character
	@param charSet: The character set to import clips to. If empty, use current character set if set.
	@type charSet: str
	@param clips: The trax clip file paths to import. If empty, select from a dialog.
	@type clips: str
	@param toTrax: Load clips directly to Trax Editor.
	@type toTrax: bool
	'''
	# Check Character Set
	if not charSet:
		charSet = glTools.utils.characterSet.getCurrent()
	if charSet:
		glTools.utils.characterSet.setCurrent(charSet)
	
	# Get Asset from Character Set
	charSetNS = glTools.utils.namespace.getNS(charSet,topOnly=True)
	charCtx = glTools.utils.reference.contextFromNsReferencePath(charSetNS)
	char = charCtx['asset']
	
	# Get Starting Directory
	assetPath = ''
	
	# Get Clips
	if not clips:
		clips = mc.fileDialog2(dir=assetPath,fileFilter='Maya Files (*.ma *.mb)',dialogStyle=2,fileMode=4,okCaption='Import',caption='Load Clip')
	
	# Import Clips
	for clipPath in clips:
		
		# Check Clip
		if not os.path.isfile(clipPath):
			print('Clip "'+clipPath+'" is not a valid file! Skipping...')
			continue
		
		# Import 
		importClip(clipPath,toChar=charSet,toTrax=toTrax)

def importCharClips(charSet='',clips=[],toTrax=False):
	'''
	Import a list of trax clips (by name as opposed to file path) to a specified character
	@param charSet: The character set to import clips to. If empty, use current character set if set.
	@type charSet: str
	@param clips: The trax clips to import (by name).
	@type clips: str
	@param toTrax: Load clips directly to Trax Editor.
	@type toTrax: bool
	'''
	# Get Asset from Character Set
	charSetNS = glTools.utils.namespace.getNS(charSet,topOnly=True)
	charCtx = glTools.utils.reference.contextFromNsReferencePath(charSetNS)
	char = charCtx['asset']
	
	# Import Clips
	for clip in clips:
		
		# Determine Clip File Path
		clipFile = clipPath+clip+'.mb'
		
		# Check Clip File Path
		if not os.path.isfile(clipFile):
			clipFile = clipPath+clip+'.ma'
		if not os.path.isfile(clipFile):
			print('Clip file "'+clipFile+'" does not exist! Unable to import clip...')
			continue
		
		# Import Clip
		glTools.utils.clip.importClip(clipFile,toChar=charSet,toTrax=toTrax)

def importClipsForAllChars(clips=[],toTrax=False):
	'''
	Import a list of trax clips (by name as opposed to file path) to all available characters
	@param charSet: The character set to import clips to. If empty, use current character set if set.
	@type charSet: str
	@param clips: The trax clips to import (by name). If empty, select from a dialog.
	@type clips: str
	@param toTrax: Load clips directly to Trax Editor.
	@type toTrax: bool
	'''
	# Get Clips
	if not clips:
		
		# Get Starting Directory
		assetPath = '/'
		
		# Select Clips
		clipList = mc.fileDialog2(dir=assetPath,fileFilter='Maya Files (*.ma *.mb)',dialogStyle=2,fileMode=4,okCaption='Import',caption='Load Clip')
		clips = [os.path.splitext(os.path.basename(clip))[0] for clip in clipList]
	
	# Import Clips
	for charSet in mc.ls(type='character'):
		
		importCharClips(charSet=charSet,clips=clips,toTrax=toTrax)
