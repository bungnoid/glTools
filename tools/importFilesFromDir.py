import os

import maya.cmds as mc

def importFilesFromDir(path,suffix='obj'):
	'''
	'''
	# Check path
	if not os.path.isdir(path): raise Exception('Invalid path!!')
	
	# Get dir list
	fileList = os.listdir(path)
	fileList.sort()
	
	# Import
	sceneList = mc.ls(assemblies=True)
	for file in fileList:
		if file.endswith('.'+suffix):
			
			# Import file
			mc.file(path+'/'+file,i=True,type="OBJ",rpr="tesla",options="mo=1",pr=True,loadReferenceDepth='all')
			
			# Rename object
			basename = file.replace('.'+suffix,'').replace('.','_')
			newObjList = list(set(mc.ls(assemblies=True)) - set(sceneList))
			if len(newObjList) > 1:
				for i in range(len(newObjList)):
					mc.rename(newObjList[i],basename+'_'+str(i))
			else:
				mc.rename(newObjList[0],basename)
				
			# Upate scene list
			sceneList = mc.ls(assemblies=True)

	# Return result
	return fileList
