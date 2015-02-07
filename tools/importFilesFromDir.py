import os

import maya.cmds as mc

def importFilesFromDir(path,ext='ma',reference=False,importWithNamespace=True):
	'''
	Import files from the specified directory path.
	@param path: Source directory to import files from.
	@type path: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Directory
	if not os.path.isdir(path): raise Exception('Invalid path!!')
	
	# Build File Extention Map
	extTypeMap = {}
	extTypeMap['fbx'] = 'FBX'
	extTypeMap['ma'] = 'mayaAscii'
	extTypeMap['mb'] = 'mayaBinary'
	extTypeMap['obj'] = 'OBJ'
	
	# Check Extension
	if not extTypeMap.has_key(ext):
		raise Exception('Unsupported file extention!')
	
	# =================
	# - Get File List -
	# =================
	
	fileList = os.listdir(path)
	fileList = [i for i in fileList if i.endswith(ext)]
	if not fileList: return []
	fileList.sort()
	
	# ================
	# - Import Files -
	# ================
	
	for fileName in fileList:
		
		# Import File
		filePath = path+'/'+fileName
		namespace = os.path.splitext(fileName)[0]
		basename = os.path.splitext(fileName)[0]
		
		# Check File (isfile)
		if not os.path.isfile(filePath): continue
		
		if reference: # REFERENCE ========
			
			try:
				mc.file(filePath,r=True,type=extTypeMap[ext],namespace=namespace,prompt=False,force=True)
			except:
				print('Error importing file! ('+filePath+')')
				continue
				
		else:		 # IMPORT ========
			
			if importWithNamespace:
				try:
					mc.file(filePath,i=True,type=extTypeMap[ext],namespace=namespace,preserveReferences=True,prompt=False,force=True)
				except:
					print('Error importing file! ('+filePath+')')
					continue
			else:
				try:
					mc.file(filePath,i=True,type=extTypeMap[ext],preserveReferences=True,prompt=False,force=True)
				except:
					print('Error importing file! ('+filePath+')')
					continue
	
	# =================
	# - Return Result -
	# =================
	
	return fileList

def importOBJsFromDir(path):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	ext = 'obj'
	
	if not os.path.isdir(path): raise Exception('Invalid path!!')
	
	# =================
	# - Get File List -
	# =================
	
	fileList = os.listdir(path)
	if not fileList: return []
	fileList.sort()
	
	# Get Current Scene List
	sceneList = mc.ls(assemblies=True)
	
	# ================
	# - Import Files -
	# ================
	
	for fileName in fileList:
		
		# Check File Extension
		fileExt = os.path.splitext(fileName)[-1].lower()
		if fileExt != ext: continue
		
		# Build Full Path
		filePath = path+'/'+fileName
		
		# Import
		try:
			mc.file(filePath,i=True,type='OBJ',prompt=False,force=True)
		except:
			print('Error importing file! ('+filePath+')')
			continue
		
		# Rename Object
		basename = os.path.splitext(fileName)[0].replace('.','_')
		newObjList = list(set(mc.ls(assemblies=True)) - set(sceneList))
		if len(newObjList) > 1:
			for i in range(len(newObjList)):
				try:
					mc.rename(newObjList[i],basename+'_'+str(i))
				except:
					print('Unable to rename "'+newObjList[i]+'" to "'+basename+'_'+str(i)+'"!')
		else:
			try:
				mc.rename(newObjList[0],basename)
			except:
				print('Unable to rename "'+newObjList[0]+'" to "'+basename+'"!')
			
		# Upate scene list
		sceneList = mc.ls(assemblies=True)

	# =================
	# - Return Result -
	# =================
	
	return fileList
