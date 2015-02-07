import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.ui.utils

from glTools.nrig.rig.rig import Rig
from glTools.data.data import Data

import os.path

def importDataUI():
	'''
	UI for selectively loading Rig data.
	'''
	rig = Rig()
	dataPath = rig.setDataPath()
	
	# Build Window
	window = rig.IMPORT_DATA_UI
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='RIG: Import Data')
	
	# Layout
	FL = mc.formLayout()
	
	# UI Elements
	dataPathTBG = mc.textFieldButtonGrp(rig.IMPORT_PATH_TBG,label='Data Path',buttonLabel='...',text=dataPath)
	filterTFG = mc.textFieldGrp(rig.IMPORT_FILTER_TFG,label='Filter',text='')
	fileListTSL = mc.textScrollList(rig.IMPORT_LIST_TSL,ams=True)
	importB = mc.button('rigImportData_importB',label='Import',c='glTools.rig.ui.importDataFromUI()')
	cancelB = mc.button('rigImportData_cancelB',label='Close',c='mc.deleteUI("'+window+'")')
	
	# UI Callbacks
	mc.textFieldButtonGrp(dataPathTBG,e=True,bc='glTools.ui.utils.importFolderBrowser("'+dataPathTBG+'")')
	mc.textFieldButtonGrp(dataPathTBG,e=True,cc='glTools.ui.utils.loadFileList("'+fileListTSL+'","'+mc.textFieldButtonGrp(dataPathTBG,q=True,text=True)+'",filesOnly=True,filterStr=".pkl")')
	
	# Form Layout
	mc.formLayout(FL,e=True,af=[(dataPathTBG,'top',5),(dataPathTBG,'left',5),(dataPathTBG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(filterTFG,'top',5,dataPathTBG)],af=[(filterTFG,'left',5),(filterTFG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(fileListTSL,'top',5,filterTFG),(fileListTSL,'bottom',5,importB)],af=[(fileListTSL,'left',5),(fileListTSL,'right',5)])
	mc.formLayout(FL,e=True,ac=[(importB,'bottom',5,cancelB)],af=[(importB,'left',5),(importB,'right',5)])
	mc.formLayout(FL,e=True,af=[(cancelB,'left',5),(cancelB,'right',5),(cancelB,'bottom',5)])
	
	# Load Data files
	if dataPath: glTools.ui.utils.loadFileList(fileListTSL,dataPath,filesOnly=True,filterStr='.pkl',sort=True)
	
	# Show Window
	mc.showWindow(window)

def importDataFromUI():
	'''
	Import selected Rig data from UI.
	'''
	rig = Rig()
	
	# Check Window
	window = rig.IMPORT_DATA_UI
	if not mc.window(window,q=True,ex=1):
		raise Exception('Rig import data UI does not exist!')
		
	# Get Data Path
	dataPath =  mc.textFieldButtonGrp(rig.IMPORT_PATH_TBG,q=True,text=True)
	# Get Data Selection
	fileList = mc.textScrollList(rig.IMPORT_LIST_TSL,q=True,si=True)
	
	# Import Selected Data
	for dataFile in fileList:
		
		# Build Data Object
		data = Data().load(os.path.join(dataPath,dataFile))
		# Rebuild Data
		try: data.rebuild()
		except: print('IMPORT DATA FAILED: Unable to load data from file "'+dataFile+'"!')
	
	# Return Result
	return fileList

def exportDataUI():
	'''
	UI for selectively saving Rig data.
	'''
	rig = Rig()
	dataPath = rig.setDataPath()
	
	# Build Window
	window = rig.EXPORT_DATA_UI
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='RIG: Export Data')
	
	# Layout
	FL = mc.formLayout()
	
	# UI Elements
	dataPathTBG = mc.textFieldButtonGrp(rig.EXPORT_PATH_TBG,label='Data Path',buttonLabel='...',text=dataPath)
	dataListTSL = mc.textScrollList(rig.EXPORT_LIST_TSL,ams=True)
	reloadB = mc.button('rigExportData_reloadB',label='Reload',c='glTools.rig.ui.reloadDataUIList()')
	exportB = mc.button('rigExportData_exportB',label='Export',c='glTools.rig.ui.exportDataFromUI()')
	cancelB = mc.button('rigExportData_cancelB',label='Close',c='mc.deleteUI("'+window+'")')
	
	# UI Callbacks
	mc.textFieldButtonGrp(dataPathTBG,e=True,bc='glTools.ui.utils.exportFolderBrowser("'+dataPathTBG+'")')
	mc.textFieldButtonGrp(dataPathTBG,e=True,cc='glTools.ui.utils.loadFileList("'+dataListTSL+'","'+mc.textFieldButtonGrp(dataPathTBG,q=True,text=True)+'",filesOnly=True,filterStr=".pkl")')
	
	# Form Layout
	mc.formLayout(FL,e=True,af=[(dataPathTBG,'top',5),(dataPathTBG,'left',5),(dataPathTBG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(dataListTSL,'top',5,dataPathTBG),(dataListTSL,'bottom',5,reloadB)],af=[(dataListTSL,'left',5),(dataListTSL,'right',5)])
	mc.formLayout(FL,e=True,ac=[(reloadB,'bottom',5,exportB)],af=[(reloadB,'left',5),(reloadB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(exportB,'bottom',5,cancelB)],af=[(exportB,'left',5),(exportB,'right',5)])
	mc.formLayout(FL,e=True,af=[(cancelB,'left',5),(cancelB,'right',5),(cancelB,'bottom',5)])
	
	# Load Deformer List
	reloadDataUIList()
	
	# Show Window
	mc.showWindow(window)

def exportDataFromUI():
	'''
	Export selected Rig data from UI.
	'''
	rig = Rig()
	
	# Check Window
	window = rig.EXPORT_DATA_UI
	if not mc.window(window,q=True,ex=1):
		raise Exception('Rig export data UI does not exist!')
		
	# Get Data Path
	dataPath =  mc.textFieldButtonGrp(rig.EXPORT_PATH_TBG,q=True,text=True)
	# Get Data Selection
	deformerList = mc.textScrollList(rig.EXPORT_LIST_TSL,q=True,si=True)
	
	# Import Selected Data
	rig.rigData['dataPath'] = dataPath
	rig.exportData(exportDeformerList=deformerList,exportSetList=None,exportCrvList=None,force=True)
	
	# Return Result
	return deformerList

def reloadDataUIList():
	'''
	List deformers in export data UI.
	'''
	rig = Rig()
	
	# Check Window
	window = rig.EXPORT_DATA_UI
	if not mc.window(window,q=True,ex=1): return []
	
	# Get Deformers from Selection
	sel = mc.ls(sl=1,dag=True)
	if sel: deformerList = mc.ls(mc.listHistory(sel),type='geometryFilter')
	else: deformerList = mc.ls(type='geometryFilter')
	deformerList = [i for i in deformerList if mc.objectType(i) != 'tweak']
	deformerList = sorted(list(set(deformerList)))
	
	# Update List
	mc.textScrollList(rig.EXPORT_LIST_TSL,e=True,ra=True)
	for deformer in deformerList:
		mc.textScrollList(rig.EXPORT_LIST_TSL,e=True,a=deformer)
	
	# Return Result
	return deformerList
