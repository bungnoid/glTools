import maya.cmds as mc

import glTools.data.deformerData
import glTools.utils.deformer

import os
import os.path

def export(exportPath,deformerList,force=False):
	'''
	'''
	# Check export path
	if not os.path.isdir(exportPath):
		
		# Create directories if they dont exist
		os.makedirs(exportPath)
	
	# Export Deformers
	for deformer in deformerList:
		
		# Check deformer
		if not glTools.utils.deformer.isDeformer(deformer):
			print('Object "'+deformer+'" is not a valid deformer! Skipping...')
			continue
		
		# Initialize Deformer Data
		deformerData = glTools.data.deformerData.DeformerData(deformer)
		
		# Build export file path
		deformerDataPath = (exportPath+'/'+deformer+'.pkl')
		
		# Check file exists
		if os.path.isfile(deformerDataPath) and not force:
			print('File path "'+deformerDataPath+'" exists! Use force=True to overwrite.')
			continue
		
		# Export Deformer Data
		print('Exporting deformer data for "'+deformer+'" to - '+deformerDataPath)
		deformerData.save(deformerDataPath)
	
	# Return Result
	print('Exporting deformers complete!')
	return 1

def importData(importPath):
	'''
	'''
	# Check import path
	if not os.path.isdir(importPath):
		raise Exception('Path "'+importPath+'" does not exist!')
	
	# Import Deformer Data
	deformerData = glTools.data.deformerData.DeformerData().load(importPath)
	deformerData.rebuild()

def exportUI():
	'''
	'''
	# Window
	window = 'exportDeformerDataUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,t='Export Deformer Data',s=True)
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	pathTBG = mc.textFieldButtonGrp('exportDeformer_pathTBG',label='Export Path',buttonLabel='...',h=30)
	deformerTSL = mc.textScrollList('exportDeformer_deformerTSL',allowMultiSelection=True)
	exportB = mc.button('exportDeformer_exportB',label='Export',c='glTools.tools.exportDeformerData.exportFromUI()')
	closeB = mc.button('exportDeformer_closeB',label='Close',c='mc.deleteUI("'+window+'")')
	
	# Populate deformer list
	deformerList = mc.ls(type='weightGeometryFilter')
	deformerList.sort()
	for deformer in deformerList:
		mc.textScrollList(deformerTSL,e=True,a=deformer)
	
	# UI Callbacks
	mc.textFieldButtonGrp(pathTBG,e=True,bc='glTools.ui.utils.exportFolderBrowser("'+pathTBG+'")')
	
	# Form LAYOUT
	mc.formLayout(FL,e=True,af=[(pathTBG,'top',5),(pathTBG,'left',5),(pathTBG,'right',5)]) # ,ap=[(pathTBG,'bottom',5,10)])
	mc.formLayout(FL,e=True,af=[(closeB,'bottom',5),(closeB,'left',5),(closeB,'right',5)])
	mc.formLayout(FL,e=True,af=[(exportB,'left',5),(exportB,'right',5)],ac=[(exportB,'bottom',5,closeB)])
	mc.formLayout(FL,e=True,af=[(deformerTSL,'left',5),(deformerTSL,'right',5)],ac=[(deformerTSL,'top',5,pathTBG),(deformerTSL,'bottom',5,exportB)])
	
	# Show Window
	mc.window(window,e=True,w=450,h=262)
	mc.showWindow(window)

def exportFromUI():
	'''
	'''
	# Get export path
	exportPath = mc.textFieldButtonGrp('exportDeformer_pathTBG',q=True,text=True)
	deformerList = mc.textScrollList('exportDeformer_deformerTSL',q=True,si=True)
	
	# Export Deformer Data
	export(exportPath,deformerList,force=True)

def importUI():
	'''
	'''
	# Window
	window = 'importDeformerDataUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,t='Import Deformer Data',s=True)
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	pathTBG = mc.textFieldButtonGrp('importDeformer_pathTBG',label='Import Path',buttonLabel='...',h=30)
	deformerTSL = mc.textScrollList('importDeformer_deformerTSL',allowMultiSelection=True)
	exportB = mc.button('importDeformer_exportB',label='Import',c='glTools.tools.exportDeformerData.exportFromUI()')
	closeB = mc.button('importDeformer_closeB',label='Close',c='mc.deleteUI("'+window+'")')
	
	# UI Callbacks
	mc.textFieldButtonGrp(pathTBG,e=True,bc='glTools.ui.utils.exportFolderBrowser("'+pathTBG+'")')
	mc.textFieldButtonGrp(pathTBG,e=True,cc='glTools.tools.exportDeformerData.updateImportList()')
	
	# Form LAYOUT
	mc.formLayout(FL,e=True,af=[(pathTBG,'top',5),(pathTBG,'left',5),(pathTBG,'right',5)]) # ,ap=[(pathTBG,'bottom',5,10)])
	mc.formLayout(FL,e=True,af=[(closeB,'bottom',5),(closeB,'left',5),(closeB,'right',5)])
	mc.formLayout(FL,e=True,af=[(exportB,'left',5),(exportB,'right',5)],ac=[(exportB,'bottom',5,closeB)])
	mc.formLayout(FL,e=True,af=[(deformerTSL,'left',5),(deformerTSL,'right',5)],ac=[(deformerTSL,'top',5,pathTBG),(deformerTSL,'bottom',5,exportB)])
	
	# Show Window
	mc.window(window,e=True,w=450,h=262)
	mc.showWindow(window)

def importFromUI():
	'''
	'''
	# Get import path
	importPath = mc.textFieldButtonGrp('importDeformer_pathTBG',q=True,text=True)
	deformerList = mc.textScrollList('importDeformer_deformerTSL',q=True,si=True)
	
	# Import Deformer Data
	for deformer in deformerList: importData(importPath+'/'+deformer+'.pkl')

def updateImportList():
	'''
	'''
	# Get import path
	importPath = mc.textFieldButtonGrp('importDeformer_pathTBG',q=True,text=True)
	deformerList = [i.split('.')[0] for i in os.listdir(importPath) if i.endswith('.pkl')]
	
	# Clear deformer list
	mc.textScrollList('importDeformer_deformerTSL',e=True,ra=True)
	
	# Populate deformer list
	for deformer in deformerList:
		mc.textScrollList('importDeformer_deformerTSL',e=True,a=deformer)
