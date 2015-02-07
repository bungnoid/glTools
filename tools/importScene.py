import maya.cmds as mc

import glTools.utils.namespace
import glTools.utils.reference

import os.path

def safeImportScene(sceneFile=None):
	'''
	Safely import a scene containing namespaced references.
	No support for importing scenes with nested namespaces.
	@param sceneFile: Path to scene file to import. If None, opens file browser dialog for user based file selection.
	@type sceneFile: str or None
	'''
	# ===========================
	# - Open Scene File Browser -
	# ===========================
	
	if sceneFile == None:
		startDir = mc.workspace(q=True,dir=True)
		sceneFile = mc.fileDialog2(	fileFilter='Maya Files (*.ma *.mb)',
									dialogStyle=2,
									fileMode=1,
									caption='Import Scene File (SAFE)',
									okCaption='Import',
									startingDirectory=startDir )[0]
	
	# ===============================
	# - Import Scene (into safe NS) -
	# ===============================
	
	# Check Scene File Exists
	if not os.path.isfile(sceneFile):
		raise Exception('Invalid file path "'+sceneFile+'"! (File not found)')
	
	# Get File Type
	fileType = {'.ma':'mayaAscii','.mb':'mayaBinary'}
	fileName, fileExtension = os.path.splitext(sceneFile)
		
	# Determine Import Namespace
	importNS = 'safeImportNS'
	importNSinc = ''
	while mc.namespace(ex=importNS+str(importNSinc)):
		if not importNSinc: importNSinc = 0
		importNSinc += 1
	importNS = importNS+str(importNSinc)
	
	# Import Scene File
	importNodes = mc.file(sceneFile,i=True,type=fileType[fileExtension],namespace=importNS,preserveReferences=True,returnNewNodes=True)
	
	# =========================
	# - Check Namespace Clash -
	# =========================
	
	# Get Nested Namespace
	importNsList = mc.namespaceInfo(importNS,listOnlyNamespaces=True) or []
	
	# Check Nested Namespaces
	mergeNsList = []
	for nestedNS in importNsList:
		
		# Check Namespace Clash
		NS = nestedNS.split(':')[-1]
		if mc.namespace(ex=NS):
			
			# Build Safe Namespace
			safeNS = NS
			safeNSsuffix = safeNS.split('_')[-1]
			try: safeNSind = int(safeNSsuffix)
			except: safeNSind = 1
			else: safeNS = safeNS.replace('_'+safeNSsuffix,'')
			while mc.namespace(ex=safeNS+'_%03d' % safeNSind): safeNSind += 1
			safeNS = safeNS+'_%03d' % safeNSind
			
			# Rename Clashing Namespace
			print('Renaming clashing namespace "'+NS+'" to "'+safeNS+'"...')
			try:
				#glTools.utils.namespace.renameNS(nestedNS,safeNS,parentNS=importNS)
				refNode = glTools.utils.reference.getReferenceFromNamespace(NS,parentNS=importNS)
				refFile = glTools.utils.reference.getReferenceFile(refNode,withoutCopyNumber=False)
				mc.file(refFile,e=True,namespace=safeNS)
			except Exception, e:
				raise Exception('Error renaming namespace "'+nestedNS+'"!')
			print('Rename namespace complete!')
			
			# Append Output List
			mergeNsList.append(safeNS)
	
	# Delete Import Namespace
	glTools.utils.namespace.deleteNS(importNS)
	
	# =================
	# - Return Result -
	# =================
	
	return mergeNsList

def fixNamespaceClashes():
	'''
	Attempt to fix clashing namespaces in current scene.
	It is assumed you have imported an external scene file into your existing scene (using an import namespace)
	This method will attempt to make sure all "imported" namespaces are unique and will try to rename clashing namespaces.
	'''
	NSlist = [ x for x in mc.namespaceInfo(listOnlyNamespaces=True,recurse=True) if not x in ['UI','shared'] ]
	NSshortList = [ x.split(':')[-1] for x in NSlist ]
	for i in range(len(NSlist)):
		
		# Check Multiple Instances of Current Namespace
		NS = NSshortList[i]
		parentNS = None
		if ':' in NSlist[i]:
			parentNS = NSlist[i].replace(NS,'')
		if NSshortList.count(NS) > 1:
			
			# Build Safe Namespace
			safeNS = NS
			safeNSsuffix = safeNS.split('_')[-1]
			try: safeNSind = int(safeNSsuffix)
			except: safeNSind = 1
			else: safeNS = safeNS.replace('_'+safeNSsuffix,'')
			while (safeNS+'_%03d' % safeNSind) in NSshortList: safeNSind += 1
			safeNS = safeNS+'_%03d' % safeNSind
			
			# =============================
			# - Rename Clashing Namespace -
			# =============================
			
			# Attempting to move a namespace containing referenced nodes will result in an error
			# Use the 'file -e -namespace' command to change a reference namespace.
			
			print('Renaming clashing namespace "'+NS+'" to "'+safeNS+'"...')
			if parentNS:
				try:
					glTools.utils.namespace.renameNS(NSlist[i],safeNS,parentNS=parentNS)
				except Exception, e:
					print('Error renaming namespace "'+NSlist[i]+'"! '+str(e))
					#raise Exception('Error renaming namespace "'+NSlist[i]+'"! '+str(e))
			else:
				try:
					glTools.utils.namespace.renameNS(NSlist[i],safeNS)
				except Exception, e:
					print('Error renaming namespace "'+NSlist[i]+'"! '+str(e))
					#raise Exception('Error renaming namespace "'+NSlist[i]+'"! '+str(e))
			print('Rename namespace complete!')
		
			# Update NS List
			NSshortList[i] = safeNS
			NSlist[i] = NSlist[i].replace(NS,safeNS)
	
	# Return Result
	return NSshortList
