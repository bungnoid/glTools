import maya.mel as mm
import maya.cmds as mc

import glTools.nrig.rig.mocap
import glTools.nrig.rig.bipedMocap

import glTools.utils.characterSet
import glTools.utils.clip
import glTools.utils.reference

import os
import os.path

import ika.glob
import ika.fs.layout

# IKA Context Utility
import ika.maya.file
import ika.context.util as ctx_util

def exportMocapClipsFromScene(clipName,mocapNS='',char=None,targetDir=''):
	'''
	'''
	# Check Destination
	if not char and not targetDir:
		raise Exception('Unbale to determine output path! Supply a target character or target directory.')
	
	# Check Mocap NS
	if mocapNS: mocapNS+=':'
	
	# Determine Export Path
	if char:
		showPath = ika.fs.layout.getShowRoot()
		clipPath = showPath+'/vfx/asset/char/'+char+'/moc/workfile/trax/'+clipName+'.mb'
	elif targetDir:
		if not os.path.isdir(targetDir): raise Exception('Invalid target directory "'+targetDir+'"!')
		clipPath = targetDir+'/'+clipName+'.mb'
	
	# Create Character Set
	mocap = glTools.nrig.rig.bipedMocap.BipedMocapRigRoll()
	try: charSet = mocap.createCharSet('char','')
	except: raise Exception('ERROR: Problem creating characterSet!')
	
	# Get Start/End Frames
	keys = mc.keyframe(mocapNS+'Hips',q=True,tc=True)
	if not keys: raise Exception('No animation on Hips!')
	
	clip = glTools.utils.clip.createClip(charSet,startTime=keys[0],endTime=keys[-1],name=clipName)
	if not clip: raise Exception('Error creating clip!')
	
	# Export Clip
	export = glTools.utils.clip.exportClip(clip,clipPath,force=True)
	
	# Return Result
	return export

def createMocapClipsFromFbxWip(sourceDir,targetDir,skipUpToDate=False,skipExistsing=False):
	'''
	Generate trax clips from a directory of mocap anim files.
	@param sourceDir: Source directory to generate clips from.
	@type sourceDir: str
	@param targetDir: Target clip directory to export processed clips to.
	@type targetDir: str
	@param extList: List of file extensions to generate clips from
	@type extList: list
	@param skipUpToDate: Skip files that are up to date. Checks last modification date of source and destination files.
	@type skipUpToDate: bool
	@param skipExistsing: Skip existing files
	@type skipExistsing: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Source Directory
	if not os.path.isdir(sourceDir):
		raise Exception('Source directory "'+sourceDir+'" does not exist!')
	
	# =====================
	# - Get FBX File List -
	# =====================
	
	# Check Source Dir
	if not sourceDir.endswith('/'): sourceDir+='/'
	
	# Get All FBX Files
	clipFileList = ika.glob.glob(os.path.join(sourceDir+'*','*.fbx'))
	clipFileList.sort()
	clipFileList.reverse()
	
	# =================
	# - Process Clips -
	# =================
	
	clipPathList = []
	for clipFile in clipFileList:
		
		# Clear Scene
		mc.file(newFile=True,force=True,prompt=False)
		
		# Skip Directories
		if not os.path.isfile(clipFile):
			print('Invalid path "'+clipFile+'"! Skipping...')
			continue
		
		# Get Clip Name
		clipName = os.path.splitext(os.path.basename(clipFile))[0].split('.')[0]
		
		# Build New Clip Path
		clipPath = targetDir+'/'+clipName+'.mb'
		
		# Check Clip Path
		if os.path.isfile(clipPath):
			
			# Check Up To Date
			if skipUpToDate:
				if os.stat(clipFile).st_mtime < os.stat(clipPath).st_mtime:
					print ('"'+clipName+'" is up to date! Skipping file...')
					continue
				else:
					print ('"'+clipName+'" is out of date! Regenerating clip...')
			
			# Check Existing
			if skipExistsing:
				print (clipName+' already exists! Skipping file...')
				continue
		
		# Print Status
		print ('Generating Clip "'+clipName+'" from '+clipFile+'...')
			
		# Import Clip File
		mc.file(clipFile,i=True,type="FBX",defaultNamespace=True)
		
		# Create Character Set
		mocap = glTools.nrig.rig.bipedMocap.BipedMocapRigRoll()
		try:
			charSet = mocap.createCharSet('char','')
		except:
			print('ERROR: Problem creating characterSet for clip "'+clipName+'"!')
			continue
		
		# =========================
		# - Create Character Clip -
		# =========================
		
		keys = mc.keyframe('Hips',q=True,tc=True)
		if not keys:
			print ('No animation on Hips! Skipping...')
			continue
		
		start = keys[0]
		end = keys[-1]
		clip = glTools.utils.clip.createClip(charSet,startTime=start,endTime=end,name=clipName)
		if not clip: continue
		
		# Export Clip
		print 'Exporting: '+clipName
		export = glTools.utils.clip.exportClip(clip,clipPath,force=True)
		
		# Update Result
		clipPathList.append(clipPath)
	
	# =================
	# - Return Result -
	# =================
	
	return clipPathList

def createMocapClips(sourceDir,targetDir='',extList=['fbx'],skipUpToDate=False,skipExistsing=False):
	'''
	Generate trax clips from a directory of mocap anim files.
	@param sourceDir: Source directory to generate clips from.
	@type sourceDir: str
	@param targetDir: Target clip directory to export processed clips to.
	@type targetDir: str
	@param extList: List of file extensions to generate clips from
	@type extList: list
	@param skipUpToDate: Skip files that are up to date. Checks last modification date of source and destination files.
	@type skipUpToDate: bool
	@param skipExistsing: Skip existing files
	@type skipExistsing: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Source Directory
	if not os.path.isdir(sourceDir):
		raise Exception('Source directory "'+sourceDir+'" does not exist!')
	
	extTypeMap = {}
	extTypeMap['fbx'] = 'FBX'
	extTypeMap['ma'] = 'mayaAscii'
	extTypeMap['mb'] = 'mayaBinary'
	
	# =================
	# - Process Clips -
	# =================
	
	# New File
	mc.file(newFile=True,force=True,prompt=False)
	
	clipPathList = []
	clipFileList = os.listdir(sourceDir)
	clipFileList.sort()
	for clipFile in clipFileList:
		
		# Skip Directories
		if os.path.isdir(sourceDir+'/'+clipFile): continue
		
		# Get Clip Extension
		ext = os.path.splitext(clipFile)[1].lower()[1:]
		if not extList.count(ext): continue
		
		# Get Clip Name
		clipName = os.path.splitext(os.path.basename(clipFile))[0]
		
		# Build New Clip Path
		clipPath = targetDir+'/'+clipName+'.mb'
		
		# Check Clip Path
		if os.path.isfile(clipPath):
			
			# Check Up To Date
			if skipUpToDate:
				if os.stat(sourceDir+'/'+clipFile).st_mtime < os.stat(clipPath).st_mtime:
					print ('"'+clipName+'" is up to date! Skipping file...')
					continue
				else:
					print ('"'+clipName+'" is up out of date! Regenerating up to date clip.')
			
			# Check Existing
			if skipExistsing:
				print (clipName+' already exists! Skipping file...')
				continue
		
		# Print Status
		print ('Generating Clip "'+clipName+'"...')
			
		# Import Clip File
		mc.file(sourceDir+'/'+clipFile,i=True,type="FBX",defaultNamespace=True)
		
		# Create Character Set
		mocap = glTools.nrig.rig.bipedMocap.BipedMocapRigRoll()
		try: charSet = mocap.createCharSet('char','')
		except: print('ERROR: Problem creating characterSet for clip "'+clipName+'"!')
		
		# Create Character Clip
		start = mc.keyframe('Hips',q=True,tc=True)[0]
		end = mc.keyframe('Hips',q=True,tc=True)[-1]
		clip = glTools.utils.clip.createClip(charSet,startTime=start,endTime=end,name=clipName)
		if not clip: continue
		
		# Export Clip
		print 'Exporting: '+clipName
		export = glTools.utils.clip.exportClip(clip,clipPath,force=True)
		
		# Update Result
		clipPathList.append(clipPath)
		
		# Clear Scene
		mc.file(newFile=True,force=True,prompt=False)
	
	# =================
	# - Return Result -
	# =================
	
	return clipPathList

def createClipRig(char,srcSubtask='mocap',dstSubtask='clip',show='hbm'):
	'''
	'''
	# ==============================
	# - Get Source and Destination -
	# ==============================
	
	# Get current context
	currCtx = ika.maya.file.getContext()
	srcOverrides = dict(currCtx)
	
	# Set Source Overrides
	srcOverrides['assetTypeDir'] = 'char'
	srcOverrides['asset'] = char
	srcOverrides['task'] = 'rig'
	srcOverrides['subtask'] = srcSubtask
	
	# Set Destination Overrides
	dstOverrides = dict(srcOverrides)
	dstOverrides['subtask'] = dstSubtask
	
	# Set Clip Overrides
	clipOverrides = dict(srcOverrides)
	clipOverrides['task'] = 'moc'
	
	# Get Source Paths
	srcCtx = ctx_util.getLatestVersion(ctx_util.getContextByType('AssetWorkfile', overrides=srcOverrides))
	srcPath = os.path.normpath(srcCtx.getFullPath())
	if not os.path.isfile(srcPath):
		raise Exception('Source rig file "'+srcPath+'" doesnt exist!')
	
	# Get Destination Path
	dstCtx = ctx_util.getNewContextToSave(ctx_util.getContextByType('AssetWorkfile', overrides=dstOverrides))
	dstPath = os.path.normpath(dstCtx.getFullPath())
	
	# Get Clip Path
	clipCtx = ctx_util.getContextByType('AssetWorkfile', overrides=clipOverrides)
	clipDir = os.path.dirname(os.path.normpath(clipCtx.getFullPath()))+'/trax/'
	if not os.path.isdir(clipDir):
		raise Exception('Source clip directory "'+clipDir+'" does not exist!')
	
	# ===============
	# - Load Source -
	# ===============
	
	extTypeMap = {}
	extTypeMap['ma'] = 'mayaAscii'
	extTypeMap['mb'] = 'mayaBinary'
	
	# Open Source Rig
	mc.file(srcPath,o=True,force=True,prompt=False)
	
	# Create Character Set
	mocap = glTools.nrig.rig.bipedMocap.BipedMocapRigRoll()
	charSet = ''
	try: charSet = mocap.createCharSet('char','')
	except: raise Exception('Unable to create Character Set!')
	
	# ================
	# - Import Clips -
	# ================
	
	fileList = os.listdir(clipDir)
	for fileName in fileList:
		
		# Check File
		clipFile = clipDir+fileName
		if not os.path.isfile(clipFile): continue
		
		# Check Ext
		ext = os.path.splitext(clipFile)[1].lower()[1:]
		if not extTypeMap.has_key(ext): continue
		
		# Get Clip Name
		clipName = os.path.splitext(fileName)[0]
		print('Loading clip "'+clipName+'"...')
		
		# Import Clip File
		glTools.utils.clip.importClip(clipFile,toChar=charSet,toTrax=False)
		#mc.file(clipFile,i=True,type=extTypeMap[ext],defaultNamespace=True)
	
	# Rename Clip Lib and Scheduler
	if mc.objExists('charClips1'): charClips = mc.rename('charClips1','charClips')
	if mc.objExists('charScheduler1'): charClips = mc.rename('charScheduler1','charScheduler')
	
	# =========================
	# - Save Destination File -
	# =========================
	
	print('Saving rig file - "'+dstPath+'"')
	
	ext = os.path.splitext(dstPath)[1].lower()[1:]
	
	mc.file(rename=dstPath)
	mc.file(save=True,type=extTypeMap[ext])
	
	# =================
	# - Return Result -
	# =================
	
	return dstPath

def createSourceClipFile(sourceDir,setLatest=False):
	'''
	'''
	# ==========================
	# - Check Source Directory -
	# ==========================
	
	if not os.path.isdir(sourceDir):
		raise Exception('Source directory "'+sourceDir+'" does not exist!')
	
	# =================
	# - Get File List -
	# =================
	
	sourceFileList = os.listdir(sourceDir)
	sourceClipList = [i for i in sourceFileList if i.startswith('sourceClips')]
	sourceFileList = [i for i in sourceFileList if not i.startswith('sourceClips')]
	
	# Get Existing Source Clip Versions
	if sourceClipList:
		sourceClipVersions = [int(i.split('.')[-2]) for i in sourceClipList]
		sourceClipVersions.sort()
		newSourceVersion = '%03d' % (sourceClipVersions[-1] + 1)
	else:
		newSourceVersion = '001'
	
	# ======================
	# - Build Source Scene -
	# ======================
	
	# Clear Scene
	mc.file(newFile=True,force=True,prompt=False)
	
	# Import Source Files
	for sourceFile in sourceFileList:
		# Get Clip Name
		clipName = os.path.splitext(os.path.basename(sourceFile))[0]
		print clipName
		# Import Clip File
		mc.file(sourceDir+'/'+sourceFile,i=True,type="mayaAscii",defaultNamespace=True)
	
	# Save Scene
	mc.file(rename=sourceDir+'/sourceClips.'+newSourceVersion+'.mb')
	mc.file(save=True,type='mayaBinary')
	
	# Update Latest
	if setLatest:
		mc.file(rename=sourceDir+'/sourceClips.latest.mb')
		mc.file(save=True,type='mayaBinary')
	
	# =================
	# - Return Result -
	# =================
	
	return

