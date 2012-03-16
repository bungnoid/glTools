import maya.cmds as mc

import glTools.tools.meshCache
import glTools.utils.mesh

def meshCacheUI():
	'''
	Main UI for the meshCache module
	'''
	# Get current frame range 
	startFrame = mc.playbackOptions(q=True,min=True)
	endFrame = mc.playbackOptions(q=True,max=True)
	
	# Window
	window = 'meshCacheUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,t='Export Mesh Cache',s=True)
	
	# Layout
	CL = mc.columnLayout(adj=True)
	
	# UI Elements
	pathTBG = mc.textFieldButtonGrp('meshCache_pathTBG',label='Path',buttonLabel='...')
	nameTFG = mc.textFieldGrp('meshCache_nameTFG',label='Combine Cache Name',text='')
	rangeIFG = mc.intFieldGrp('meshCache_rangeIFG',nf=2,label='Frame Range',v1=startFrame,v2=endFrame)
	paddingIFG = mc.intFieldGrp('meshCache_paddingIFG',nf=1,label='Frame Padding',v1=4)
	uvSetTFG = mc.textFieldGrp('meshCache_uvSetTFG',label='UV Set',text='default')
	spaceRBG = mc.radioButtonGrp('meshCache_spaceRBG',label='Output Mode', labelArray2=['Local','World'],numberOfRadioButtons=2,sl=2)
	gzipCBG = mc.checkBoxGrp('meshCache_gzipCBG',numberOfCheckBoxes=1,label='gzip',v1=False)
	exportGeoB = mc.button('meshCache_exportGeoB',label='Export GEO',c='glTools.ui.meshCache.exportGeoFromUI()')
	exportGeoCombineB = mc.button('meshCache_exportGeoCombineB',label='Export GEO Combined',c='glTools.ui.meshCache.exportGeoCombinedFromUI()')
	exportObjB = mc.button('meshCache_exportObjB',label='Export OBJ',c='glTools.ui.meshCache.exportObjFromUI()')
	exportObjCombineB = mc.button('meshCache_exportObjCombineB',label='Export OBJ Combined',c='glTools.ui.meshCache.exportObjCombinedFromUI()')
	closeB = mc.button('meshCache_closeB',label='Close',c='mc.deleteUI("'+window+'")')
	
	# UI Callbacks
	mc.textFieldButtonGrp(pathTBG,e=True,bc='glTools.ui.utils.exportFolderBrowser("'+pathTBG+'")')
	
	# Show Window
	mc.window(window,e=True,w=450,h=262)
	mc.showWindow(window)

def exportGeoFromUI():
	'''
	writeGeoCache from UI 
	'''
	# Get UI info
	path = mc.textFieldButtonGrp('meshCache_pathTBG',q=True,text=True)
	start = mc.intFieldGrp('meshCache_rangeIFG',q=True,v1=True)
	end = mc.intFieldGrp('meshCache_rangeIFG',q=True,v2=True)
	pad = mc.intFieldGrp('meshCache_paddingIFG',q=True,v1=True)
	uvSet = mc.textFieldGrp('meshCache_uvSetTFG',q=True,text=True)
	worldSpace = bool(mc.radioButtonGrp('meshCache_spaceRBG',q=True,sl=True)-1)
	gz = mc.checkBoxGrp('meshCache_gzipCBG',q=True,v1=True)
	
	# Check UV Set
	if uvSet == 'default': uvSet = ''
	
	# Get selection
	sel = [i for i in mc.ls(sl=True,fl=True,o=True) if glTools.utils.mesh.isMesh(i)]
	if not sel:
		print 'No valid mesh objects selected for export!!'
		return
	
	# Export each mesh
	for mesh in sel:
		
		# Generate file name
		mesh_name = mesh.replace(':','_')
		
		# Export
		glTools.tools.meshCache.writeGeoCache(path,mesh_name,mesh,start,end,pad,uvSet,worldSpace,gz)

def exportGeoCombinedFromUI():
	'''
	writeGeoCombineCache from UI
	'''
	# Get UI info
	path = mc.textFieldButtonGrp('meshCache_pathTBG',q=True,text=True)
	name = mc.textFieldGrp('meshCache_nameTFG',q=True,text=True)
	start = mc.intFieldGrp('meshCache_rangeIFG',q=True,v1=True)
	end = mc.intFieldGrp('meshCache_rangeIFG',q=True,v2=True)
	pad = mc.intFieldGrp('meshCache_paddingIFG',q=True,v1=True)
	uvSet = mc.textFieldGrp('meshCache_uvSetTFG',q=True,text=True)
	worldSpace = bool(mc.radioButtonGrp('meshCache_spaceRBG',q=True,sl=True)-1)
	gz = mc.checkBoxGrp('meshCache_gzipCBG',q=True,v1=True)
	
	# Check Name
	if not name:
		print 'Provide valid cache name and try again!'
		return
	
	# Check UV Set
	if uvSet == 'default': uvSet = ''
	
	# Get selection
	sel = [i for i in mc.ls(sl=True,fl=True,o=True) if glTools.utils.mesh.isMesh(i)]
	if not sel:
		print 'No valid mesh objects selected for export!!'
		return
	
	# Write Combine Cache
	glTools.tools.meshCache.writeGeoCombineCache(path,name,sel,start,end,pad,uvSet,worldSpace,gz)

def exportObjFromUI():
	'''
	writeObjCache from UI
	'''
	# Get UI info
	path = mc.textFieldButtonGrp('meshCache_pathTBG',q=True,text=True)
	start = mc.intFieldGrp('meshCache_rangeIFG',q=True,v1=True)
	end = mc.intFieldGrp('meshCache_rangeIFG',q=True,v2=True)
	pad = mc.intFieldGrp('meshCache_paddingIFG',q=True,v1=True)
	uvSet = mc.textFieldGrp('meshCache_uvSetTFG',q=True,text=True)
	worldSpace = bool(mc.radioButtonGrp('meshCache_spaceRBG',q=True,sl=True)-1)
	gz = mc.checkBoxGrp('meshCache_gzipCBG',q=True,v1=True)
	
	# Check UV Set
	if uvSet == 'default': uvSet = ''
	
	# Get selection
	sel = [i for i in mc.ls(sl=True,fl=True,o=True) if glTools.utils.mesh.isMesh(i)]
	if not sel:
		print 'No valid mesh objects selected for export!!'
		return
	
	# Export each mesh
	for mesh in sel:
		
		# Generate file name
		mesh_name = mesh.replace(':','_')
		
		# Export
		glTools.tools.meshCache.writeObjCache(path,mesh_name,mesh,start,end,pad,uvSet,worldSpace,gz)

def exportObjCombinedFromUI():
	'''
	writeObjCombineCache from UI
	'''
	# Get UI info
	path = mc.textFieldButtonGrp('meshCache_pathTBG',q=True,text=True)
	name = mc.textFieldGrp('meshCache_nameTFG',q=True,text=True)
	start = mc.intFieldGrp('meshCache_rangeIFG',q=True,v1=True)
	end = mc.intFieldGrp('meshCache_rangeIFG',q=True,v2=True)
	pad = mc.intFieldGrp('meshCache_paddingIFG',q=True,v1=True)
	uvSet = mc.textFieldGrp('meshCache_uvSetTFG',q=True,text=True)
	worldSpace = bool(mc.radioButtonGrp('meshCache_spaceRBG',q=True,sl=True)-1)
	gz = mc.checkBoxGrp('meshCache_gzipCBG',q=True,v1=True)
	
	# Check Name
	if not name:
		print 'Provide valid cache name and try again!'
		return
	
	# Check UV Set
	if uvSet == 'default': uvSet = None
	
	# Get selection
	sel = [i for i in mc.ls(sl=True,fl=True,o=True) if glTools.utils.mesh.isMesh(i)]
	if not sel:
		print 'No valid mesh objects selected for export!!'
		return
	
	# Write Combine Cache
	glTools.tools.meshCache.writeObjCombineCache(path,name,sel,start,end,pad,uvSet,worldSpace,gz)

