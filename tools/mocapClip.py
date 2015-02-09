import maya.mel as mm
import maya.cmds as mc

import glTools.nrig.rig.mocap
import glTools.nrig.rig.bipedMocap

import glTools.utils.characterSet
import glTools.utils.clip
import glTools.utils.reference

import os
import os.path

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
	clipFileList = None ####!!!
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

