import maya.mel as mm
import maya.cmds as mc

import glTools.utils.clip
import glTools.utils.characterSet
import glTools.utils.namespace

def charSetSelectUI():
	'''
	'''
	# Window
	window = 'charSetSelectUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Character Set Selector',wh=[350,500])
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# ===============
	# - UI Elements -
	# ===============
	
	# Create Character Set List
	charList = mc.ls(type='character') or []
	charListTSL = mc.textScrollList('charSetSelect_charListTSL',ams=False)
	for char in charList: mc.textScrollList(charListTSL,e=True,a=char)
	
	# Create List Callback
	mc.textScrollList(charListTSL,e=True,sc='import glTools.tools.characterSet;reload(glTools.tools.characterSet);glTools.tools.characterSet.setCurrentFromUI()')
	
	# Pop-up Menu
	mc.popupMenu(p=charListTSL)
	mc.menuItem('Set from Selection',c='glTools.tools.characterSet.setCurrentFromSelection()')
	
	# ===============
	# - Form Layout -
	# ===============
	mc.formLayout(FL,e=True,af=[(charListTSL,'top',5),(charListTSL,'left',5),(charListTSL,'right',5),(charListTSL,'bottom',5)])
		
	# ===============
	# - Show Window -
	# ===============
	
	mc.showWindow(window)
	
def setCurrentFromUI():
	'''
	'''
	# Get Selected Character Set From UI
	char = mc.textScrollList('charSetSelect_charListTSL',q=True,si=True)[0]
	glTools.utils.characterSet.setCurrent(char)

def setCurrentFromSelection():
	'''
	'''
	# Get Selected Character Set From Scene
	sel = mc.ls(sl=1)
	NSlist = glTools.utils.namespace.getNSList(sel,topOnly=True)
	if not NSlist:
		print('No selected namespaces! Unable to set current character set...')
	
	# Find Character Sets in Selected Namespace
	char = mc.ls(NSlist[0]+':*',type='character')
	if not char:
		print('No character set in selected namespace! Unable to set current character set...')
	
	# Get UI Character Set List
	charListTSL = mc.textScrollList('charSetSelect_charListTSL',q=True,ai=True)
	if char[0] in charListTSL:
		mc.textScrollList('charSetSelect_charListTSL',e=True,si=char[0])
	else:
		print('Character set "'+char[0]+'" not found in UI list! Skipping UI selection...')
	
	# Set Current Character Set
	glTools.utils.characterSet.setCurrent(char[0])
