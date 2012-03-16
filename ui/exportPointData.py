import maya.mel as mm
import maya.cmds as mc

import glTools.tools.exportPointData

import os.path

def exportPointDataUI():
	'''
	Main UI for the exportPointData module
	'''
	# Get current frame range 
	startFrame = mc.playbackOptions(q=True,min=True)
	endFrame = mc.playbackOptions(q=True,max=True)
	
	# Window
	window = 'exportPointDataUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,t='Export Point Data',s=False)
	
	# Layout
	CL = mc.columnLayout(adj=True)
	
	# UI Elements
	pathTBG = mc.textFieldButtonGrp('exportPoint_pathTBG',label='Path',buttonLabel='...')
	camTBG = mc.textFieldButtonGrp('exportPoint_camTBG',label='Camera (2D only)',buttonLabel='Select')
	rangeIFG = mc.intFieldGrp('exportPoint_rangeIFG',nf=2,label='Frame Range',v1=startFrame,v2=endFrame)
	resIFG = mc.intFieldGrp('exportPoint_resIFG',nf=2,label='Resolution',v1=2348,v2=1152)
	refIFG = mc.intFieldGrp('exportPoint_refIFG',nf=1,label='Offset Base Frame',v1=startFrame)
	resOMG = mc.optionMenuGrp('exportPoint_resOMG',label='Resolution Preset')
	export2DB = mc.button('exportPoint_export2DB',label='Export 2D Point Data',c='glTools.ui.exportPointData.export2DFromUI()')
	export2DOffsetB = mc.button('exportPoint_export2DOffsetB',label='Export 2D Offset Data',c='glTools.ui.exportPointData.export2DOffsetFromUI()')
	export3DB = mc.button('exportPoint_export3DB',label='Export 3D Point Data',c='glTools.ui.exportPointData.export3DFromUI()')
	export3DRotB = mc.button('exportPoint_export3DRotB',label='Export 3D Rotate Data',c='glTools.ui.exportPointData.export3DRotationFromUI()')
	closeB = mc.button('exportPoint_closeB',label='Close',c='mc.deleteUI("'+window+'")')
	
	# Resolution presets
	mc.setParent(resOMG)
	mc.menuItem(label='WIDE(full)')
	mc.menuItem(label='WIDE(half)')
	mc.menuItem(label='WIDE(quarter)')
	
	# UI Callbacks
	mc.textFieldButtonGrp(pathTBG,e=True,bc='glTools.ui.utils.exportFolderBrowser("'+pathTBG+'")')
	mc.textFieldButtonGrp(camTBG,e=True,bc='glTools.ui.utils.loadTypeSel("'+camTBG+'",selType="transform")')
	mc.optionMenuGrp(resOMG,e=True,cc='glTools.tools.exportPointData.setResolution()')
	
	# Popup menu
	mc.popupMenu(parent=camTBG)
	for cam in mc.ls(type='camera'):
		if mc.camera(cam,q=True,orthographic=True): continue
		camXform = mc.listRelatives(cam,p=True,pa=True)[0]
		mc.menuItem(l=camXform,c='mc.textFieldButtonGrp("exportPoint_camTBG",e=True,text="'+camXform+'")')
	
	# Show Window
	mc.window(window,e=True,w=435,h=275)
	mc.showWindow(window)

def setResolution():
	'''
	Toggle 2D output resolution from UI
	'''
	preset = mc.optionMenuGrp('exportPoint_resOMG',q=True,sl=True)
	if preset == 1: mc.intFieldGrp('exportPoint_resIFG',e=True,v1=2348,v2=1152)
	if preset == 2: mc.intFieldGrp('exportPoint_resIFG',e=True,v1=1174,v2=576)
	if preset == 3: mc.intFieldGrp('exportPoint_resIFG',e=True,v1=587,v2=288)

def export2DFromUI():
	'''
	export2DPointData from UI
	'''
	# Get selection
	sel = mc.ls(sl=True,fl=True)
	if not sel:
		print 'No points selected for export!!'
		return
	
	# Get UI data
	path = mc.textFieldButtonGrp('exportPoint_pathTBG',q=True,text=True)
	cam = mc.textFieldButtonGrp('exportPoint_camTBG',q=True,text=True)
	start = mc.intFieldGrp('exportPoint_rangeIFG',q=True,v1=True)
	end = mc.intFieldGrp('exportPoint_rangeIFG',q=True,v2=True)
	xRes = mc.intFieldGrp('exportPoint_resIFG',q=True,v1=True)
	yRes = mc.intFieldGrp('exportPoint_resIFG',q=True,v2=True)
	
	# Check UI data
	if not cam or not mc.objExists(cam):
		print('No valid camera specified!')
		return
	if start > end:
		print('Invalid range specified!')
		return
	if not path.endswith('/'): path += '/'
	
	# For each point
	for pt in sel:
		
		# Generate export file path
		sel_name = pt.split(':')[-1].replace('.','_').replace('[','_').replace(']','')
		filepath = path + sel_name + '_2D.txt'
		
		# Check path
		if os.path.isfile(filepath):
			chk = mc.confirmDialog(t='Warning: File exists',message='File "'+filepath+'" already exist! Overwrite?',button=['Yes','No'],defaultButton='Yes',cancelButton='No',dismissString='No')
			if chk == 'No': continue
		
		# Isolate Select - ON
		setIsolateSelect(pt,1)
		
		# Export data
		glTools.tools.exportPointData.export2DPointData(filepath,pt,cam,start,end,xRes,yRes)
		
		# Isolate Select - OFF
		setIsolateSelect(pt,0)

def export2DOffsetFromUI():
	'''
	export2DOffsetData from UI
	'''
	# Get selection
	sel = mc.ls(sl=True,fl=True)
	if not sel:
		print 'No points selected for export!!'
		return
	
	# Get UI data
	path = mc.textFieldButtonGrp('exportPoint_pathTBG',q=True,text=True)
	cam = mc.textFieldButtonGrp('exportPoint_camTBG',q=True,text=True)
	start = mc.intFieldGrp('exportPoint_rangeIFG',q=True,v1=True)
	end = mc.intFieldGrp('exportPoint_rangeIFG',q=True,v2=True)
	ref = mc.intFieldGrp('exportPoint_refIFG',q=True,v1=True)
	xRes = mc.intFieldGrp('exportPoint_resIFG',q=True,v1=True)
	yRes = mc.intFieldGrp('exportPoint_resIFG',q=True,v2=True)
	
	# Check UI data
	if not cam or not mc.objExists(cam):
		print('No valid camera specified!')
		return
	if start > end:
		print('Invalid range specified!')
		return
	if not path.endswith('/'): path += '/'
	
	# For each point
	for pt in sel:
		
		# Generate export file path
		sel_name = pt.split(':')[-1].replace('.','_').replace('[','_').replace(']','')
		filepath = path + sel_name + '_2DOffset.txt'
		
		# Check path
		if os.path.isfile(filepath):
			chk = mc.confirmDialog(t='Warning: File exists',message='File "'+filepath+'" already exist! Overwrite?',button=['Yes','No'],defaultButton='Yes',cancelButton='No',dismissString='No')
			if chk == 'No': continue
		
		# Isolate Select - ON
		setIsolateSelect(pt,1)
		
		# Export data
		glTools.tools.exportPointData.export2DOffsetData(filepath,pt,cam,start,end,xRes,yRes,ref)
		
		# Isolate Select - OFF
		setIsolateSelect(pt,0)
	
def export3DFromUI():
	'''
	export3DPointData from UI
	'''
	# Get selection
	sel = mc.ls(sl=True,fl=True)
	if not sel:
		print 'No points selected for export!!'
		return
	
	# Get UI data
	path = mc.textFieldButtonGrp('exportPoint_pathTBG',q=True,text=True)
	start = mc.intFieldGrp('exportPoint_rangeIFG',q=True,v1=True)
	end = mc.intFieldGrp('exportPoint_rangeIFG',q=True,v2=True)
	
	# Check UI data
	if start > end:
		print('Invalid range specified!')
		return
	if not path.endswith('/'): path += '/'
	
	# For each point
	for pt in sel:
		
		# Generate export file path
		sel_name = pt.split(':')[-1].replace('.','_').replace('[','_').replace(']','')
		filepath = path + sel_name + '_3D.txt'
		
		# Check path
		if os.path.isfile(filepath):
			chk = mc.confirmDialog(t='Warning: File exists',message='File "'+filepath+'" already exist! Overwrite?',button=['Yes','No'],defaultButton='Yes',cancelButton='No',dismissString='No')
			if chk == 'No': continue
		
		# Isolate Select - ON
		setIsolateSelect(pt,1)
		
		# Export data
		glTools.tools.exportPointData.export3DPointData(filepath,pt,start,end)
		
		# Isolate Select - OFF
		setIsolateSelect(pt,0)

def export3DRotationFromUI():
	'''
	export3DRotationData from UI
	'''
	# Get selection
	sel = mc.ls(sl=True,fl=True,type=['transform','joint'])
	if not sel:
		print 'No valid transform selected for export!!'
		return
	
	# Get UI data
	path = mc.textFieldButtonGrp('exportPoint_pathTBG',q=True,text=True)
	start = mc.intFieldGrp('exportPoint_rangeIFG',q=True,v1=True)
	end = mc.intFieldGrp('exportPoint_rangeIFG',q=True,v2=True)
	
	# Check UI data
	if start > end:
		print('Invalid range specified!')
		return
	if not path.endswith('/'): path += '/'
	
	# For each point
	for pt in sel:
		
		# Generate export file path
		sel_name = pt.split(':')[-1].replace('.','_').replace('[','_').replace(']','')
		filepath = path + sel_name + '_3Drot.txt'
		
		# Check path
		if os.path.isfile(filepath):
			chk = mc.confirmDialog(t='Warning: File exists',message='File "'+filepath+'" already exist! Overwrite?',button=['Yes','No'],defaultButton='Yes',cancelButton='No',dismissString='No')
			if chk == 'No': continue
		
		# Isolate Select - ON
		setIsolateSelect(pt,1)
		
		# Export data
		glTools.tools.exportPointData.export3DRotationData(filepath,pt,start,end,rotateOrder='zxy')
		
		# Isolate Select - OFF
		setIsolateSelect(pt,0)

def setIsolateSelect(pt,state):
	'''
	'''
	# Check point
	if not mc.objExists(pt):
		raise Exception('Object "'+pt+'" does not exist!')
	
	# Select point
	mc.select(pt)
	
	# Get panel list
	panelList = mc.getPanel(type='modelPanel')
	
	# For each panel
	for panel in panelList: mc.isolateSelect(panel,state=state)


