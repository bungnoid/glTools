import maya.cmds as mc
import glTools.utils.skinCluster

class UserInputError(Exception): pass

def makeRelativeUI():
	'''
	User Interface for skinCluster.makeRelative()
	'''
	# Window
	win = 'makeRelativeUI'
	if mc.window(win,q=True,ex=True): mc.deleteUI(win)
	win = mc.window(win,t='SkinCluster - Make Relative')
	# Form Layout
	makeRelativeFL = mc.formLayout(numberOfDivisions=100)
	
	# SkinCluster option menu
	skinClusterOMG = mc.optionMenuGrp('makeRelativeSkinClusterOMG',label='SkinCluster')
	for skin in mc.ls(type='skinCluster'): mc.menuItem(label=skin)
	
	# Relative To TextField
	makeRelativeTFB = mc.textFieldButtonGrp('makeRelativeToTFB',label='RelativeTo',text='',buttonLabel='Load Selected')
	
	# Button
	makeRelativeBTN = mc.button(l='Make Relative',c='glTools.ui.skinCluster.makeRelativeFromUI()')
	
	# UI Callbacks
	mc.textFieldButtonGrp(makeRelativeTFB,e=True,bc='glTools.ui.utils.loadTypeSel("'+makeRelativeTFB+'","transform")')
	
	# Form Layout - MAIN
	mc.formLayout(makeRelativeFL,e=True,af=[(skinClusterOMG,'left',5),(skinClusterOMG,'top',5),(skinClusterOMG,'right',5)])
	mc.formLayout(makeRelativeFL,e=True,af=[(makeRelativeTFB,'left',5),(makeRelativeTFB,'right',5)])
	mc.formLayout(makeRelativeFL,e=True,ac=[(makeRelativeTFB,'top',5,skinClusterOMG)])
	mc.formLayout(makeRelativeFL,e=True,af=[(makeRelativeBTN,'left',5),(makeRelativeBTN,'right',5),(makeRelativeBTN,'bottom',5)])
	mc.formLayout(makeRelativeFL,e=True,ac=[(makeRelativeBTN,'top',5,makeRelativeTFB)])
	
	# Open window
	mc.showWindow(win)

def makeRelativeFromUI():
	'''
	Execute makeRelative from the UI
	'''
	# Window
	win = 'makeRelativeUI'
	if not mc.window(win,q=True,ex=True):
		raise UserInputError('Make Relative UI is not currently open!!')
	# Get UI values
	skinCluster = mc.optionMenuGrp('makeRelativeSkinClusterOMG',q=True,v=True)
	relativeTo = mc.textFieldButtonGrp('makeRelativeToTFB',q=True,text=True)
	# Check UI values
	if not mc.objExists(skinCluster):
		raise UserInputError('SkinCluster "'+skinCluster+'" does not exist!!')
	if not mc.objExists(relativeTo):
		raise UserInputError('Object "'+relativeTo+'" does not exist!!')
	# Make Relative
	glTools.utils.skinCluster.makeRelative(skinCluster,relativeTo)

def resetFromUI():
	'''
	Execute skinCluster.reset() from the UI
	'''
	# Get Selection
	sel = mc.ls(sl=True,type=['transform','mesh','nurbsSurface','nurbsCurve'])
	# Reset skinCluster
	for item in sel:
		try: glTools.utils.skinCluster.reset(item)
		except: pass


