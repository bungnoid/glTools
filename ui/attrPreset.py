import maya.cmds as mc

import glTools.utils.attrPreset

def ui():
	'''
	'''
	# Window
	win = 'attrPresetUI'
	if mc.window(win,ex=True): mc.deleteUI(win)
	win = mc.window(win,t='Attribute Presets',s=True,mb=False,wh=[570,330])
	
	# ---------------
	# - Main Window -
	# ---------------
	
	# FormLayout
	fl = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements 
	nodeListTXT = mc.text(l='Node List:',al='left')
	nodeListTSL = mc.textScrollList('attrPreset_nodeListTSL', allowMultiSelection=True )
	
	nodeList_addB = mc.button(label='Add', c='glTools.ui.attrPreset.nodeListAddFromUI()' )
	nodeList_delB = mc.button(label='Remove', c='glTools.ui.attrPreset.nodeListDelFromUI()' )
	
	presetListTXT = mc.text(l='Preset List:',al='left')
	presetListTSL = mc.textScrollList('attrPreset_presetListTSL', allowMultiSelection=False )
	
	presetAmountFSG = mc.floatSliderGrp('attrPreset_amountFSG',label='Amount',field=True,minValue=0.0,maxValue=1.0,fieldMinValue=0.0,fieldMaxValue=1.0,value=1.0,cw=[1,60])
	
	presetApplySelB = mc.button(label='Apply to Selected', c='glTools.ui.attrPreset.presetApplyFromUI(1)' )
	presetApplyAllB = mc.button(label='Apply to All', c='glTools.ui.attrPreset.presetApplyFromUI(0)' )
	
	sep = mc.separator(style='in',hr=False)
	
	# ---------------
	# - Form Layout -
	# ---------------
	
	mc.formLayout(fl,e=True,af=[(nodeListTXT,'left',5),(nodeListTXT,'top',5)],ap=[(nodeListTXT,'right',5,40)])
	mc.formLayout(fl,e=True,af=[(nodeListTSL,'left',5)],ap=[(nodeListTSL,'right',5,40)],ac=[(nodeListTSL,'top',5,nodeListTXT),(nodeListTSL,'bottom',5,nodeList_addB)])
	mc.formLayout(fl,e=True,af=[(nodeList_addB,'left',5),(nodeList_addB,'bottom',5)],ap=[(nodeList_addB,'right',5,20)])
	mc.formLayout(fl,e=True,af=[(nodeList_delB,'bottom',5)],ap=[(nodeList_delB,'right',5,40)],ac=[(nodeList_delB,'left',5,nodeList_addB)])
	
	mc.formLayout(fl,e=True,af=[(presetListTXT,'right',5),(presetListTXT,'top',5)],ap=[(presetListTXT,'left',5,45)])
	mc.formLayout(fl,e=True,af=[(presetListTSL,'right',5)],ap=[(presetListTSL,'left',5,45)],ac=[(presetListTSL,'top',5,presetListTXT),(presetListTSL,'bottom',5,presetAmountFSG)])
	mc.formLayout(fl,e=True,af=[(presetAmountFSG,'right',5)],ap=[(presetAmountFSG,'left',5,45)],ac=[(presetAmountFSG,'bottom',5,presetApplySelB)])
	mc.formLayout(fl,e=True,af=[(presetApplySelB,'bottom',5)],ap=[(presetApplySelB,'left',5,45),(presetApplySelB,'right',5,74)])
	mc.formLayout(fl,e=True,af=[(presetApplyAllB,'right',5),(presetApplyAllB,'bottom',5)],ac=[(presetApplyAllB,'left',5,presetApplySelB)])
	
	mc.formLayout(fl,e=True,af=[(sep,'top',5),(sep,'bottom',5)],ac=[(sep,'left',5,nodeListTSL),(sep,'right',5,presetListTSL)])
	
	# ----------------
	# - UI Callbacks -
	# ----------------
	
	mc.textScrollList(nodeListTSL,e=True,dcc='glTools.ui.utils.selectFromTSL("'+nodeListTSL+'")')
	mc.textScrollList(nodeListTSL,e=True,dkc='glTools.ui.utils.removeFromTSL("'+nodeListTSL+'")')
	
	# --------------
	# - Popup Menu -
	# --------------
	
	nodeListPUM = mc.popupMenu(parent=nodeListTSL)
	mc.menuItem(l='Add Selected',c='glTools.ui.attrPreset.nodeListAddFromUI()')
	mc.menuItem(l='Remove Hilited',c='glTools.ui.attrPreset.nodeListDelFromUI()')
	mc.menuItem(l='Clear List',c='glTools.ui.attrPreset.nodeListClearFromUI()')
	mc.menuItem(l='Select Hilited',c='glTools.ui.utils.selectFromTSL("'+nodeListTSL+'")')
	
	# --------------
	# - Display UI -
	# --------------
	
	mc.showWindow(win)

def updatePresetList():
	'''
	'''
	# Clear preset list
	mc.textScrollList('attrPreset_presetListTSL',e=True,ra=True)
	
	# Get list of nodes
	nodes = mc.textScrollList('attrPreset_nodeListTSL',q=True,ai=True)
	if not nodes: return
	
	# Get node types
	nodeTypes = [mc.objectType(node) for node in nodes]
	nodeTypes = list(set(nodeTypes))
	
	# Get list of available presets
	presets = []
	for nodeType in nodeTypes:
		presets.extend(glTools.utils.attrPreset.listNodePreset(nodeType))
	presets = list(set(presets))
	
	# Update preset list
	for preset in presets:
		mc.textScrollList('attrPreset_presetListTSL',e=True,a=preset)
	
	# Select first item in list
	if presets:
		mc.textScrollList('attrPreset_presetListTSL',e=True,sii=1)

def nodeListAddFromUI():
	'''
	'''
	# Add selected items to TSL
	glTools.ui.utils.addToTSL('attrPreset_nodeListTSL')
	
	# Select first item in list
	if mc.textScrollList('attrPreset_presetListTSL',q=True,ni=1):
		mc.textScrollList('attrPreset_presetListTSL',e=True,sii=1)
	
	# Update preset list
	updatePresetList()

def nodeListDelFromUI():
	'''
	'''
	# Removed selected items from TSL
	glTools.ui.utils.removeFromTSL('attrPreset_nodeListTSL')
	
	# Select first item in list
	if mc.textScrollList('attrPreset_presetListTSL',q=True,ni=1):
		mc.textScrollList('attrPreset_presetListTSL',e=True,sii=1)
	
	# Update preset list
	updatePresetList()
	
def nodeListClearFromUI():
	'''
	'''
	# Clear node list
	mc.textScrollList('attrPreset_nodeListTSL',e=True,ra=True)
	
	# Update preset list
	updatePresetList()

def presetApplyFromUI(selectedOnly):
	'''
	'''
	# Get list of nodes
	if selectedOnly:
		nodes = mc.textScrollList('attrPreset_nodeListTSL',q=True,si=True)
	else:
		nodes = mc.textScrollList('attrPreset_nodeListTSL',q=True,ai=True)
	
	# Get selected preset
	preset = mc.textScrollList('attrPreset_presetListTSL',q=True,si=True)
	if not preset: raise Exception('No preset specified!')
	
	# Apply preset
	glTools.utils.attrPreset.apply(nodes,preset[0],1.0)
