import maya.cmds as mc
import maya.mel as mm

import glTools.utils.component
import glTools.utils.selection
import glTools.surfaceSkin.coordinateUtilities
import surfaceSkinEditInfMembershipCTX
import utilities

class UIError(Exception): pass
class UserInputError(Exception): pass

class SurfaceSkinUI(object):
	
	def __init__(self):
		self.surfaceSkinUtils = utilities.SurfaceSkinUtilities()
		
		self.createWin = 'surfaceSkin_createUI'
		self.addInfluenceWin = 'surfaceSkin_addInfUI'
		self.addTransInfluenceWin = 'surfaceSkin_addTransInfUI'
		self.addRemInfluenceWin = 'surfaceSkin_removeInfUI'
		
	#==========================================================
	# UI Creation Methods
	#==========================================================
	
	def menu(self):
		'''
		Create surfaceSkin menu in main Maya window.
		'''
		# Load plugin
		if not mc.pluginInfo('isoMuscle',l=1,q=1): mc.loadPlugin('isoMuscle')
		
		# Ensure surfaceSkin weights attributes are paintable
		self.surfaceSkinUtils.makePaintable()
		
		# Get Main UI
		mainUI = 'MayaWindow'
		mc.setParent(mainUI)
		
		# Create Menu
		ssMenu = 'surfaceSkinMenu'
		if mc.menu(ssMenu,q=1,ex=1): mc.deleteUI(ssMenu)
		ssMenu = mc.menu(ssMenu,label="surfaceSkin",tearOff=1)
		
		# Add Menu Items
		#----------------
		# create
		mc.menuItem(l='Create',c='glTools.surfaceSkin.SurfaceSkinUI().createUI()')
		# edit
		mc.menuItem(l='Add Influence',c='glTools.surfaceSkin.SurfaceSkinUI().addInfluenceUI()')
		mc.menuItem(l='Add Transform Influence',c='glTools.surfaceSkin.SurfaceSkinUI().addTransformInfluenceUI()')
		mc.menuItem(l='Remove Influence',c='glTools.surfaceSkin.SurfaceSkinUI().removeInfluenceUI()')
		mc.separator(style='single')
		# membership
		mc.menuItem(l='Influence Membership',subMenu=1,tearOff=1)
		mc.menuItem(l='Edit Influence Membership',c='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembershipUI()')
		mc.menuItem(l='Interactive Membership Tool',c='glTools.surfaceSkin.SurfaceSkinUI().editMembershipToolUI()')
		mc.menuItem(l='Prune Membership by Weights',c='glTools.surfaceSkin.SurfaceSkinUI().pruneMembershipByWeightsUI()')
		# weights
		mc.setParent( '..',menu=1 )
		mc.menuItem(l='Influence Weights',subMenu=1,tearOff=1)
		mc.menuItem(l='Paint Influence Weights',c='glTools.surfaceSkin.SurfaceSkinUI().paintInfluenceWeightsUI()')
		mc.menuItem(l='Prune non-Member Weights',c='glTools.surfaceSkin.SurfaceSkinUI().pruneWeightsByMembershipUI()')
		# coordinate utilities
		mc.setParent( '..',menu=1 )
		mc.menuItem(l='Coordinate Utilities',subMenu=1,tearOff=1)
		mc.menuItem(l='Coordinate Utilities',c='glTools.surfaceSkin.SurfaceSkinUI().coordinateUtilitiesUI()')
		# info
		mc.setParent( '..',menu=1 )
		mc.menuItem(l='Info',subMenu=1,tearOff=1)
		mc.menuItem(l='Print Info')
		# Reload
		mc.setParent( '..',menu=1 )
		mc.menuItem(l='Reload Menu',c='glTools.surfaceSkin.SurfaceSkinUI().menu()')
	
	def createUI(self):
		'''
		Generate the UI for surfaceSkin deformer creation.
		'''
		#Initialize UI variables
		cw1 = 100
		cw2 = 40
		
		# Get user selection
		sel = mc.ls(sl=1)
		
		# Window
		if mc.window(self.createWin,ex=1): mc.deleteUI(self.createWin)
		mc.window(self.createWin,t='Surface Skin: Create',mb=1,w=450,h=250)
		
		# Menu
		mc.menu(label='Edit',tearOff=1)
		mc.menuItem(label='Reset Settings',c='surfaceSkinUI_create()')
		
		# FormLayout
		ssCreate_FRM = mc.formLayout('surfaceSkinCreate_FRM')
		
		# Create options
		ssCreateName_TFG = mc.textFieldGrp('ssCreateName_TFG',label='Name',text='surfaceSkin1',editable=1,cw=(1,cw1))
		ssCreateWeight_FSG = mc.floatSliderGrp('ssCreateWeight_FSG',label='Default Weight',f=1,min=0,max=1,fmn=0,fmx=1,v=0,cw=[(1,cw1),(2,cw2)])
		ssCreateMaxDist_FSG = mc.floatSliderGrp('ssCreateMaxDist_FSG',label='Max Distance',f=1,min=0,max=10,fmn=0,fmx=100,v=0,cw=[(1,cw1),(2,cw2)])
		
		# Influences
		ssCreateInf_TXT = mc.text(l='Influences')
		ssCreateInf_TSL = mc.textScrollList('ssCreateInf_TSL',numberOfRows=8,allowMultiSelection=True)
		mc.textScrollList(ssCreateInf_TSL,e=1,dkc='glTools.surfaceSkin.SurfaceSkinUI().removeFromInfList("'+ssCreateInf_TSL+'")')
		ssCreateAddInf_BTN = mc.button(l='Add',c='glTools.surfaceSkin.SurfaceSkinUI().addToInfList("'+ssCreateInf_TSL+'","nurbsSurface")')
		ssCreateRemInf_BTN = mc.button(l='Remove',c='glTools.surfaceSkin.SurfaceSkinUI().removeFromInfList("'+ssCreateInf_TSL+'")')
		
		# Create button
		ssCreate_BTN = mc.button(l='Create Surface Skin',c='glTools.surfaceSkin.SurfaceSkinUI().createFromUI()')
		
		# Form Layout:============================
		
		# ssCreateInf_TXT
		mc.formLayout(ssCreate_FRM,e=1,af=[(ssCreateInf_TXT,'top',5),(ssCreateInf_TXT,'left',5)])
		
		# ssCreateInf_TSL
		mc.formLayout(ssCreate_FRM,e=1,ac=[(ssCreateInf_TSL,'top',5,ssCreateInf_TXT),(ssCreateInf_TSL,'bottom',5,ssCreateAddInf_BTN)])
		mc.formLayout(ssCreate_FRM,e=1,af=[(ssCreateInf_TSL,'left',5)])
		mc.formLayout(ssCreate_FRM,e=1,ap=[(ssCreateInf_TSL,'right',0,40)])
		
		# ssCreateAddInf_BTN
		mc.formLayout(ssCreate_FRM,e=1,af=[(ssCreateAddInf_BTN,'left',5),(ssCreateAddInf_BTN,'bottom',5)])
		mc.formLayout(ssCreate_FRM,e=1,ap=[(ssCreateAddInf_BTN,'right',0,20)])
		
		# ssCreateRemInf_BTN
		mc.formLayout(ssCreate_FRM,e=1,af=[(ssCreateRemInf_BTN,'bottom',5)])
		mc.formLayout(ssCreate_FRM,e=1,ap=[(ssCreateRemInf_BTN,'left',5,20),(ssCreateRemInf_BTN,'right',0,40)])
		
		# ssCreateName_TFG
		mc.formLayout(ssCreate_FRM,e=1,af=[(ssCreateName_TFG,'top',5),(ssCreateName_TFG,'right',5)])
		mc.formLayout(ssCreate_FRM,e=1,ac=[(ssCreateName_TFG,'left',20,ssCreateInf_TSL)])
		
		# ssCreateWeight_FSG
		mc.formLayout(ssCreate_FRM,e=1,ac=[(ssCreateWeight_FSG,'top',5,ssCreateName_TFG),(ssCreateWeight_FSG,'left',20,ssCreateInf_TSL)])
		mc.formLayout(ssCreate_FRM,e=1,af=[(ssCreateWeight_FSG,'right',5)])
		
		# ssCreateMaxDist_FSG
		mc.formLayout(ssCreate_FRM,e=1,ac=[(ssCreateMaxDist_FSG,'top',5,ssCreateWeight_FSG),(ssCreateMaxDist_FSG,'left',20,ssCreateInf_TSL)])
		mc.formLayout(ssCreate_FRM,e=1,af=[(ssCreateMaxDist_FSG,'right',5)])
		
		# ssCreate_BTN
		mc.formLayout(ssCreate_FRM,e=1,af=[(ssCreate_BTN,'right',5),(ssCreate_BTN,'bottom',5)])
		mc.formLayout(ssCreate_FRM,e=1,ac=[(ssCreate_BTN,'left',5,ssCreateInf_TSL)])
		
		# Add selected influences to list
		self.addToInfList(ssCreateInf_TSL,'nurbsSurface')
		
		# show window
		mc.showWindow(self.createWin)
	
	def addInfluenceUI(self):
		'''
		addInfluenceUI()
		Generate the UI for the addition of surface influences to an existing surfaceSkin deformer
		
		import glTools.surfaceSkin.ui
		glTools.surfaceSkin.ui.addInfluenceUI()
		'''
		
		#Initialize UI variables
		cw1 = 100
		cw2 = 40
		
		# Get user selection
		sel = mc.ls(sl=1)
		# Get scene surfaceSkin list
		surfSkinList = mc.ls(type='surfaceSkin')
		
		# Window
		if mc.window(self.addInfluenceWin,ex=1): mc.deleteUI(self.addInfluenceWin)
		mc.window(self.addInfluenceWin,t='Surface Skin: Add Influence',mb=1,w=450,h=250)
		
		# Menu
		mc.menu(label='Edit',tearOff=1)
		mc.menuItem(label='Reset Settings',c='glTools.surfaceSkin.SurfaceSkinUI().addInfluenceUI()')
		
		# FormLayout
		ssAddInf_FRM = mc.formLayout('surfaceSkinAddInf_FRM')
		
		# influences
		ssAddInf_TXT = mc.text(l='Influences')
		ssAddInf_TSL = mc.textScrollList('ssAddInf_TSL',numberOfRows=8,allowMultiSelection=True)
		mc.textScrollList(ssAddInf_TSL,e=1,dkc='glTools.surfaceSkin.SurfaceSkinUI().removeFromInfList("'+ssAddInf_TSL+'")')
		ssAddInfAddInf_BTN = mc.button(l='Add',c='glTools.surfaceSkin.SurfaceSkinUI().addToInfList("'+ssAddInf_TSL+'","nurbsSurface")')
		ssAddInfRemInf_BTN = mc.button(l='Remove',c='glTools.surfaceSkin.SurfaceSkinUI().removeFromInfList("'+ssAddInf_TSL+'")')
		
		# add influence options
		ssAddInfSurfSkin_OMG = mc.optionMenuGrp('ssAddInfSurfSkin_OMG',label='SurfaceSkin',cw=(1,cw1))
		for node in surfSkinList: mc.menuItem(node)
		ssAddInfWeight_FSG = mc.floatSliderGrp('ssAddInfWeight_FSG',label='Default Weight',f=1,min=0,max=1,fmn=0,fmx=1,v=0,cw=[(1,cw1),(2,cw2)])
		ssAddInfMaxDist_FSG = mc.floatSliderGrp('ssAddInfMaxDist_FSG',label='Max Distance',f=1,min=0,max=10,fmn=0,fmx=100,v=0,cw=[(1,cw1),(2,cw2)])
		ssAddInfPreBind_CBG = mc.checkBoxGrp('ssAddInfPreBind_CBG',label='Calculate Pre-bind',numberOfCheckBoxes=1,v1=0,cw=(1,cw1+20))
		
		# add influences
		ssAddInf_BTN = mc.button(l='Add Influences',c='glTools.surfaceSkin.SurfaceSkinUI().addInfluenceFromUI()')
		
		# Form Layout:============================
		
		# ssAddInf_TXT
		mc.formLayout(ssAddInf_FRM,e=1,af=[(ssAddInf_TXT,'top',5),(ssAddInf_TXT,'left',5)])
		
		# ssAddInf_TSL
		mc.formLayout(ssAddInf_FRM,e=1,ac=[(ssAddInf_TSL,'top',5,ssAddInf_TXT),(ssAddInf_TSL,'bottom',5,ssAddInfAddInf_BTN)])
		mc.formLayout(ssAddInf_FRM,e=1,af=[(ssAddInf_TSL,'left',5)])
		mc.formLayout(ssAddInf_FRM,e=1,ap=[(ssAddInf_TSL,'right',0,40)])
		
		# ssAddInfAddInf_BTN
		mc.formLayout(ssAddInf_FRM,e=1,af=[(ssAddInfAddInf_BTN,'left',5),(ssAddInfAddInf_BTN,'bottom',5)])
		mc.formLayout(ssAddInf_FRM,e=1,ap=[(ssAddInfAddInf_BTN,'right',0,20)])
		
		# ssAddInfRemInf_BTN
		mc.formLayout(ssAddInf_FRM,e=1,af=[(ssAddInfRemInf_BTN,'bottom',5)])
		mc.formLayout(ssAddInf_FRM,e=1,ap=[(ssAddInfRemInf_BTN,'left',5,20),(ssAddInfRemInf_BTN,'right',0,40)])
		
		# ssAddInfName_TFG
		mc.formLayout(ssAddInf_FRM,e=1,af=[(ssAddInfSurfSkin_OMG,'top',5),(ssAddInfSurfSkin_OMG,'right',5)])
		mc.formLayout(ssAddInf_FRM,e=1,ac=[(ssAddInfSurfSkin_OMG,'left',20,ssAddInf_TSL)])
		
		# ssAddInfWeight_FSG
		mc.formLayout(ssAddInf_FRM,e=1,ac=[(ssAddInfWeight_FSG,'top',5,ssAddInfSurfSkin_OMG),(ssAddInfWeight_FSG,'left',20,ssAddInf_TSL)])
		mc.formLayout(ssAddInf_FRM,e=1,af=[(ssAddInfWeight_FSG,'right',5)])
		
		# ssAddInfMaxDist_FSG
		mc.formLayout(ssAddInf_FRM,e=1,ac=[(ssAddInfMaxDist_FSG,'top',5,ssAddInfWeight_FSG),(ssAddInfMaxDist_FSG,'left',20,ssAddInf_TSL)])
		mc.formLayout(ssAddInf_FRM,e=1,af=[(ssAddInfMaxDist_FSG,'right',5)])
		
		# ssAddInfPreBind_CBG
		mc.formLayout(ssAddInf_FRM,e=1,ac=[(ssAddInfPreBind_CBG,'top',5,ssAddInfMaxDist_FSG),(ssAddInfPreBind_CBG,'left',20,ssAddInf_TSL)])
		mc.formLayout(ssAddInf_FRM,e=1,af=[(ssAddInfPreBind_CBG,'right',5)])
		
		# ssAddInf_BTN
		mc.formLayout(ssAddInf_FRM,e=1,af=[(ssAddInf_BTN,'right',5),(ssAddInf_BTN,'bottom',5)])
		mc.formLayout(ssAddInf_FRM,e=1,ac=[(ssAddInf_BTN,'left',5,ssAddInf_TSL)])
		
		# Add selected influences to list
		self.addToInfList(ssAddInf_TSL,'nurbsSurface')
		
		# show window
		mc.showWindow(self.addInfluenceWin)
	
	def addTransformInfluenceUI(self):
		'''
		addTransformInfluenceUI()
		Generate the UI for the addition of transform influences to an existing surfaceSkin deformer.
		
		import glTools.surfaceSkin.ui
		glTools.surfaceSkin.ui.addTransformInfluenceUI()
		'''
		
		# Initialize UI variables
		cw1 = 100
		cw2 = 40
		
		# Get user selection
		sel = mc.ls(sl=1)
		# Get scene surfaceSkin list
		surfSkinList = mc.ls(type='surfaceSkin')
		
		# Window
		if mc.window(self.addTransInfluenceWin,ex=1): mc.deleteUI(self.addTransInfluenceWin)
		mc.window(self.addTransInfluenceWin,t='Surface Skin: Add Transform Influence',mb=1,w=450,h=250)
		
		# Menu
		mc.menu(label='Edit',tearOff=1)
		mc.menuItem(label='Reset Settings',c='glTools.surfaceSkin.SurfaceSkinUI().addTransformInfluenceUI()')
		
		# FormLayout
		ssAddTransInf_FRM = mc.formLayout('surfaceSkinAddTransInf_FRM')
		
		# Influence List
		ssAddTransInf_TXT = mc.text(l='Transfrom Influences')
		ssAddTransInf_TSL = mc.textScrollList('ssAddTransInf_TSL',numberOfRows=8,allowMultiSelection=True)
		mc.textScrollList(ssAddTransInf_TSL,e=1,dkc='glTools.surfaceSkin.SurfaceSkinUI().removeFromInfList("'+ssAddTransInf_TSL+'")')
		ssAddTransInfAddInf_BTN = mc.button(l='Add',c='glTools.surfaceSkin.SurfaceSkinUI().addToInfList("'+ssAddTransInf_TSL+'")')
		ssAddTransInfRemInf_BTN = mc.button(l='Remove',c='glTools.surfaceSkin.SurfaceSkinUI().removeFromInfList("'+ssAddTransInf_TSL+'")')
		
		# Add transform influence options
		ssAddTransInfSurfSkin_OMG = mc.optionMenuGrp('ssAddTransInfSurfSkin_OMG',label='SurfaceSkin',cw=(1,cw1))
		for node in surfSkinList: mc.menuItem(node)
		ssAddTransInfWeight_FSG = mc.floatSliderGrp('ssAddTransInfWeight_FSG',label='Default Weight',f=1,min=0,max=1,fmn=0,fmx=1,v=0,cw=[(1,cw1),(2,cw2)])
		ssAddTransInfMaxDist_FSG = mc.floatSliderGrp('ssAddTransInfMaxDist_FSG',label='Max Distance',f=1,min=0,max=10,fmn=0,fmx=100,v=0,cw=[(1,cw1),(2,cw2)])
		ssAddTransInfPreBind_CBG = mc.checkBoxGrp('ssAddTransInfPreBind_CBG',label='Calculate Pre-bind',numberOfCheckBoxes=1,v1=1,cw=(1,cw1+20))
		ssAddTransInfCreateBase_CBG = mc.checkBoxGrp('ssAddTransInfCreateBase_CBG',label='Create Base',numberOfCheckBoxes=1,v1=1,cw=(1,cw1+20))
		
		# Add transform influences
		ssAddTransInf_BTN = mc.button(l='Add Transform Influences',c='glTools.surfaceSkin.SurfaceSkinUI().addTransformInfluenceFromUI()')
		
		# Form Layout:============================
		
		# ssAddTransInf_TXT
		mc.formLayout(ssAddTransInf_FRM,e=1,af=[(ssAddTransInf_TXT,'top',5),(ssAddTransInf_TXT,'left',5)])
		
		# ssAddTransInf_TSL
		mc.formLayout(ssAddTransInf_FRM,e=1,ac=[(ssAddTransInf_TSL,'top',5,ssAddTransInf_TXT),(ssAddTransInf_TSL,'bottom',5,ssAddTransInfAddInf_BTN)])
		mc.formLayout(ssAddTransInf_FRM,e=1,af=[(ssAddTransInf_TSL,'left',5)])
		mc.formLayout(ssAddTransInf_FRM,e=1,ap=[(ssAddTransInf_TSL,'right',0,40)])
		
		# ssAddTransInfAddTransInf_BTN
		mc.formLayout(ssAddTransInf_FRM,e=1,af=[(ssAddTransInfAddInf_BTN,'left',5),(ssAddTransInfAddInf_BTN,'bottom',5)])
		mc.formLayout(ssAddTransInf_FRM,e=1,ap=[(ssAddTransInfAddInf_BTN,'right',0,20)])
		
		# ssAddTransInfRemInf_BTN
		mc.formLayout(ssAddTransInf_FRM,e=1,af=[(ssAddTransInfRemInf_BTN,'bottom',5)])
		mc.formLayout(ssAddTransInf_FRM,e=1,ap=[(ssAddTransInfRemInf_BTN,'left',5,20),(ssAddTransInfRemInf_BTN,'right',0,40)])
		
		# ssAddTransInfName_TFG
		mc.formLayout(ssAddTransInf_FRM,e=1,af=[(ssAddTransInfSurfSkin_OMG,'top',5),(ssAddTransInfSurfSkin_OMG,'right',5)])
		mc.formLayout(ssAddTransInf_FRM,e=1,ac=[(ssAddTransInfSurfSkin_OMG,'left',20,ssAddTransInf_TSL)])
		
		# ssAddTransInfWeight_FSG
		mc.formLayout(ssAddTransInf_FRM,e=1,ac=[(ssAddTransInfWeight_FSG,'top',5,ssAddTransInfSurfSkin_OMG),(ssAddTransInfWeight_FSG,'left',20,ssAddTransInf_TSL)])
		mc.formLayout(ssAddTransInf_FRM,e=1,af=[(ssAddTransInfWeight_FSG,'right',5)])
		
		# ssAddTransInfMaxDist_FSG
		mc.formLayout(ssAddTransInf_FRM,e=1,ac=[(ssAddTransInfMaxDist_FSG,'top',5,ssAddTransInfWeight_FSG),(ssAddTransInfMaxDist_FSG,'left',20,ssAddTransInf_TSL)])
		mc.formLayout(ssAddTransInf_FRM,e=1,af=[(ssAddTransInfMaxDist_FSG,'right',5)])
		
		# ssAddTransInfPreBind_CBG
		mc.formLayout(ssAddTransInf_FRM,e=1,ac=[(ssAddTransInfPreBind_CBG,'top',5,ssAddTransInfMaxDist_FSG),(ssAddTransInfPreBind_CBG,'left',20,ssAddTransInf_TSL)])
		mc.formLayout(ssAddTransInf_FRM,e=1,af=[(ssAddTransInfPreBind_CBG,'right',5)])
		
		# ssAddTransInfCreateBase_CBG
		mc.formLayout(ssAddTransInf_FRM,e=1,ac=[(ssAddTransInfCreateBase_CBG,'top',5,ssAddTransInfPreBind_CBG),(ssAddTransInfCreateBase_CBG,'left',20,ssAddTransInf_TSL)])
		mc.formLayout(ssAddTransInf_FRM,e=1,af=[(ssAddTransInfCreateBase_CBG,'right',5)])
		
		# ssAddTransInf_BTN
		mc.formLayout(ssAddTransInf_FRM,e=1,af=[(ssAddTransInf_BTN,'right',5),(ssAddTransInf_BTN,'bottom',5)])
		mc.formLayout(ssAddTransInf_FRM,e=1,ac=[(ssAddTransInf_BTN,'left',5,ssAddTransInf_TSL)])
		
		# Add selected influences to list
		self.addToInfList(ssAddTransInf_TSL)
		
		# show window
		mc.showWindow(self.addTransInfluenceWin)
	
	def removeInfluenceUI(self):
		'''
		Generate the UI for the removal of surfaceSkin influences
		'''
		# Initialize UI variables
		cw1 = 100
		
		# Get user selection
		sel = mc.ls(sl=1)
		# Get scene surfaceSkin list
		surfSkinList = mc.ls(type='surfaceSkin')
		
		# Window
		win = self.addRemInfluenceWin
		if mc.window(win,ex=1): mc.deleteUI(win)
		mc.window(win,t='Surface Skin: Remove Influences',mb=1,w=450,h=250)
		
		# Menu
		mc.menu(label='Edit',tearOff=1)
		mc.menuItem(label='Reset Settings',c='glTools.surfaceSkin.SurfaceSkinUI().removeInfluenceUI()')
		
		# FormLayout
		ssRemoveInf_FRM = mc.formLayout('surfaceSkinRemoveInf_FRM')
		
		# Influences
		ssRemoveInf_TXT = mc.text(l='Influences')
		ssRemoveInf_TSL = mc.textScrollList('ssRemoveInf_TSL',numberOfRows=8,allowMultiSelection=True)
		mc.textScrollList(ssRemoveInf_TSL,e=1,dkc='glTools.surfaceSkin.SurfaceSkinUI().removeFromInfList("'+ssRemoveInf_TSL+'")')
		
		# Remove influence options
		ssRemoveInfSurfSkin_OMG = mc.optionMenuGrp('ssRemoveInfSurfSkin_OMG',label='SurfaceSkin',cw=(1,cw1))
		mc.optionMenuGrp(ssRemoveInfSurfSkin_OMG,e=1,cc='glTools.surfaceSkin.SurfaceSkinUI().updateInfList("'+ssRemoveInf_TSL+'","'+ssRemoveInfSurfSkin_OMG+'")')
		for node in surfSkinList: mc.menuItem(node)
			
		# Remove influences
		ssRemoveInf_BTN = mc.button(l='Remove Influences',c='glTools.surfaceSkin.SurfaceSkinUI().removeInfluenceFromUI()')
		
		# Form Layout:============================
		
		# ssRemoveInf_TXT
		mc.formLayout(ssRemoveInf_FRM,e=1,af=[(ssRemoveInf_TXT,'top',5),(ssRemoveInf_TXT,'left',5)])
		
		# ssRemoveInf_TSL
		mc.formLayout(ssRemoveInf_FRM,e=1,ac=[(ssRemoveInf_TSL,'top',5,ssRemoveInf_TXT)])
		mc.formLayout(ssRemoveInf_FRM,e=1,af=[(ssRemoveInf_TSL,'left',5),(ssRemoveInf_TSL,'bottom',5)])
		mc.formLayout(ssRemoveInf_FRM,e=1,ap=[(ssRemoveInf_TSL,'right',0,40)])
		
		# ssRemoveInfSurfSkin_OMG
		mc.formLayout(ssRemoveInf_FRM,e=1,af=[(ssRemoveInfSurfSkin_OMG,'top',5),(ssRemoveInfSurfSkin_OMG,'right',5)])
		mc.formLayout(ssRemoveInf_FRM,e=1,ac=[(ssRemoveInfSurfSkin_OMG,'left',20,ssRemoveInf_TSL)])
		
		# ssRemoveInf_BTN
		mc.formLayout(ssRemoveInf_FRM,e=1,af=[(ssRemoveInf_BTN,'right',5),(ssRemoveInf_BTN,'bottom',5)])
		mc.formLayout(ssRemoveInf_FRM,e=1,ac=[(ssRemoveInf_BTN,'left',5,ssRemoveInf_TSL)])
		
		# Update influence list
		self.updateInfList(ssRemoveInf_TSL,ssRemoveInfSurfSkin_OMG)
		
		# show window
		mc.showWindow(win)
	
	def editInfluenceMembershipUI(self):
		'''
		Generate the UI for the manipulation of surfaceSkin influence membership
		'''
		# Initialize UI variables
		cw1 = 100
		
		# Window
		win = 'surfaceSkin_editMembershipUI'
		if mc.window(win,ex=1): mc.deleteUI(win)
		mc.window(win,t='Surface Skin: Edit Influence Membership',mb=1,w=750,h=250)
		
		# Menu
		mc.menu(label='Settings',tearOff=1)
		mc.menuItem(label='Reset',c='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembershipUI()')
		mc.menuItem('ssEditMemberCalcPreBind',label='Calculate Pre-bind',checkBox=True)
		
		# FormLayout
		ssEditInfMember_FRM = mc.formLayout('surfaceSkinEditInfMember_FRM',numberOfDivisions=100)
		
		# surfaceSkin list
		ssEditInfMemberSurfSkin_TXT = mc.text(l='surfaceSkin node:')
		ssEditInfMemberSurfSkin_TSL = mc.textScrollList('ssEditInfMemberSurfSkin_TSL',numberOfRows=8,allowMultiSelection=0)
		surfSkinList = mc.ls(type='surfaceSkin')
		mc.textScrollList(ssEditInfMemberSurfSkin_TSL,e=1,a=surfSkinList)
		mc.textScrollList(ssEditInfMemberSurfSkin_TSL,e=1,sc='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_switchSurfaceSkin()')
		
		# influence list
		ssEditInfMemberInf_TXT = mc.text(l='influence:')
		ssEditInfMemberInf_TSL = mc.textScrollList('ssEditInfMemberInf_TSL',numberOfRows=8,allowMultiSelection=True)
		mc.textScrollList(ssEditInfMemberInf_TSL,e=1,sc='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_switchInfluence()')
		
		# membership list
		ssEditInfMemberMember_TXT = mc.text(l='membership:')
		ssEditInfMemberMember_TSL = mc.textScrollList('ssEditInfMemberMember_TSL',numberOfRows=8,allowMultiSelection=1)
		mc.textScrollList(ssEditInfMemberMember_TSL,e=1,sc='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_selectMembersInList()')
		
		# calculate prebind checkbox
		#ssEditInfMemberPrebind_CBG = mc.checkBoxGrp('ssEditInfMemberPrebind_CBG',label='Calculate Pre-bind',numberOfCheckBoxes=1,v1=1,cw=(1,cw1))
		
		# Buttons
		ssEditInfMemberAdd_BTN = mc.button(l='ADD',c='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_add()')
		ssEditInfMemberRemove_BTN = mc.button(l='REMOVE',c='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_remove()')
		ssEditInfMemberSet_BTN = mc.button(l='SET',c='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_set()')
		ssEditInfMemberReset_BTN = mc.button(l='RESET',c='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_reset()')
		ssEditInfMemberBtn_SEP = mc.separator(style='single',height=10)
		ssEditInfMemberAll_BTN = mc.button(l='Select All Members',c='glTools.surfaceSkin.SurfaceSkinUI().selectAllInList("'+ssEditInfMemberMember_TSL+'")')
		ssEditInfMemberTool_BTN = mc.button(l='Interactive Membership Tool',c='glTools.surfaceSkin.SurfaceSkinUI().editMembershipToolUI()')
		
		# popup menu
		ssEditInfMemberMember_PUM = mc.popupMenu('ssEditInfMemberMember_PUM',parent=ssEditInfMemberMember_TSL)
		mc.menuItem(l='Select All',c='glTools.surfaceSkin.SurfaceSkinUI().selectAllInList("'+ssEditInfMemberMember_TSL+'")')
		mc.separator(style='single')
		mc.menuItem(l='Add Selected',c='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_add()')
		mc.menuItem(l='Remove Selected',c='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_remove()')
		mc.menuItem(l='Set from Selected',c='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_set()')
		mc.menuItem(l='Reset Selected',c='glTools.surfaceSkin.SurfaceSkinUI().editInfluenceMembership_reset()')
		
		# Form Layout:============================
		
		# ssEditInfMemberSurfSkin_TXT
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberSurfSkin_TXT,'top',5),(ssEditInfMemberSurfSkin_TXT,'left',5)])
		# ssEditInfMemberInf_TSL
		mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberSurfSkin_TSL,'top',5,ssEditInfMemberSurfSkin_TXT)])
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberSurfSkin_TSL,'left',5),(ssEditInfMemberSurfSkin_TSL,'bottom',5)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ap=[(ssEditInfMemberSurfSkin_TSL,'right',5,25)])
		
		# ssEditInfMemberInf_TXT
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberInf_TXT,'top',5)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ap=[(ssEditInfMemberInf_TXT,'left',5,25)])
		# ssEditInfMemberInf_TSL
		mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberInf_TSL,'top',5,ssEditInfMemberInf_TXT)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ap=[(ssEditInfMemberInf_TSL,'left',5,25),(ssEditInfMemberInf_TSL,'right',5,50)])
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberInf_TSL,'bottom',5)])
		
		# ssEditInfMemberMember_TXT
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberMember_TXT,'top',5)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ap=[(ssEditInfMemberMember_TXT,'left',5,50)])
		# ssEditInfMemberMember_TSL
		mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberMember_TSL,'top',5,ssEditInfMemberMember_TXT)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ap=[(ssEditInfMemberMember_TSL,'left',5,50),(ssEditInfMemberMember_TSL,'right',5,75)])
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberMember_TSL,'bottom',5)])
		
		# ssEditInfMemberPrebind_CBG
		#mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberPrebind_CBG,'right',5),(ssEditInfMemberPrebind_CBG,'top',5)])
		#mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberPrebind_CBG,'left',5,ssEditInfMemberMember_TSL)])
		
		# ssEditInfMemberAdd_BTN
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberAdd_BTN,'right',5)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberAdd_BTN,'top',5,ssEditInfMemberMember_TXT),(ssEditInfMemberAdd_BTN,'left',5,ssEditInfMemberMember_TSL)])
		
		# ssEditInfMemberRemove_BTN
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberRemove_BTN,'right',5)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberRemove_BTN,'left',5,ssEditInfMemberMember_TSL),(ssEditInfMemberRemove_BTN,'top',5,ssEditInfMemberAdd_BTN)])
		
		# ssEditInfMemberSet_BTN
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberSet_BTN,'right',5)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberSet_BTN,'left',5,ssEditInfMemberMember_TSL),(ssEditInfMemberSet_BTN,'top',5,ssEditInfMemberRemove_BTN)])
		
		# ssEditInfMemberReset_BTN
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberReset_BTN,'right',5)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberReset_BTN,'left',5,ssEditInfMemberMember_TSL),(ssEditInfMemberReset_BTN,'top',5,ssEditInfMemberSet_BTN)])
		
		# ssEditInfMemberBtn_SEP
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberBtn_SEP,'right',5)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberBtn_SEP,'left',5,ssEditInfMemberMember_TSL),(ssEditInfMemberBtn_SEP,'top',5,ssEditInfMemberReset_BTN)])
		
		# ssEditInfMemberAll_BTN
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberAll_BTN,'right',5)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberAll_BTN,'left',5,ssEditInfMemberMember_TSL),(ssEditInfMemberAll_BTN,'top',5,ssEditInfMemberBtn_SEP)])
		
		# ssEditInfMemberTool_BTN
		mc.formLayout(ssEditInfMember_FRM,e=1,af=[(ssEditInfMemberTool_BTN,'right',5),(ssEditInfMemberTool_BTN,'bottom',5)])
		mc.formLayout(ssEditInfMember_FRM,e=1,ac=[(ssEditInfMemberTool_BTN,'left',5,ssEditInfMemberMember_TSL)])
		
		# showWindow
		mc.showWindow(win)
	
	def editMembershipToolUI(self):
		'''
		Generate the UI for the editing influence membership
		'''
		#Initialize UI variables
		cw1 = 100
		
		# window
		win = 'surfaceSkin_editMembershipToolUI'
		if mc.window(win,ex=1): mc.deleteUI(win)
		mc.window(win,t='Surface Skin: Edit Influence Membership Tool',mb=1,w=370,h=250,s=0)
		
		# Menu
		mc.menu(label='Edit',tearOff=1)
		mc.menuItem(label='Reset Settings',c='glTools.surfaceSkin.SurfaceSkinUI().editMembershipToolUI()')
		
		# FormLayout
		ssEditInfMemberTool_FRM = mc.formLayout('surfaceSkin_editInfMemberTool_FRM',numberOfDivisions=100)
		
		# SurfaceSkin drop-down menu
		ssEditInfMemberToolSurfaceSkin_OMG = mc.optionMenuGrp('ssEditInfMemberToolSurfaceSkin_OMG',label='SurfaceSkin',cw=(1,cw1))
		for node in mc.ls(type='surfaceSkin'): mc.menuItem(node)
		
		# SurfaceSkin Influence List
		ssEditInfMemberToolInfluence_TSL = mc.textScrollList('ssEditInfMemberToolInfluence_TSL',numberOfRows=8,allowMultiSelection=0,w=160)
		mc.textScrollList(ssEditInfMemberToolInfluence_TSL,e=1,sc='ssEditInfluenceMembershipCTX.hiliteMembers()')
		
		# Add change command for optionMenuGrp
		mc.optionMenuGrp(ssEditInfMemberToolSurfaceSkin_OMG,e=1,cc='glTools.surfaceSkin.SurfaceSkinUI().updateInfList("'+ssEditInfMemberToolInfluence_TSL+'","'+ssEditInfMemberToolSurfaceSkin_OMG+'")')
		
		# calculate prebind checkbox
		ssEditInfMemberToolPrebind_CBG = mc.checkBoxGrp('ssEditInfMemberToolPrebind_CBG',label='Calculate Pre-bind',numberOfCheckBoxes=1,v1=1,cw=(1,150))
		
		# set default weight checkbox/float field
		ssEditInfMemberToolSetWeight_CBG = mc.checkBoxGrp('ssEditInfMemberToolSetWeight_CBG',label='Set Default Weights',numberOfCheckBoxes=1,v1=1,cw=(1,150))
		ssEditInfMemberToolSetWeight_FFG = mc.floatFieldGrp('ssEditInfMemberToolSetWeight_FFG',numberOfFields=1,l='Default Weight',v1=1.0,cw=(1,100))
		
		# separator
		ssEditInfMemberToolBtn_SEP = mc.separator(style='single',h=10)
		
		# Buttons
		ssEditInfMemberToolStart_BTN = mc.button(l='Start',c='ssEditInfluenceMembershipCTX.enable()')
		ssEditInfMemberToolStop_BTN = mc.button(l='Stop',c='ssEditInfluenceMembershipCTX.disable()')
		
		# Form Layout:============================
		
		# ssEditInfMemberToolSurfaceSkin_OMG
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,af=[(ssEditInfMemberToolSurfaceSkin_OMG,'left',5),(ssEditInfMemberToolSurfaceSkin_OMG,'top',5)])
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,ap=[(ssEditInfMemberToolSurfaceSkin_OMG,'right',5,50)])
		
		# ssEditInfMemberToolInfluence_TSL
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,ac=[(ssEditInfMemberToolInfluence_TSL,'top',5,ssEditInfMemberToolSurfaceSkin_OMG)])
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,af=[(ssEditInfMemberToolInfluence_TSL,'left',5),(ssEditInfMemberToolInfluence_TSL,'bottom',5)])
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,ap=[(ssEditInfMemberToolInfluence_TSL,'right',5,50)])
		
		# ssEditInfMemberToolPrebind_CBG
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,af=[(ssEditInfMemberToolPrebind_CBG,'right',5)])
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,ac=[(ssEditInfMemberToolPrebind_CBG,'left',5,ssEditInfMemberToolInfluence_TSL),(ssEditInfMemberToolPrebind_CBG,'top',5,ssEditInfMemberToolSurfaceSkin_OMG)])
		
		# ssEditInfMemberToolSetWeight_CBG
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,af=[(ssEditInfMemberToolSetWeight_CBG,'right',5)])
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,ac=[(ssEditInfMemberToolSetWeight_CBG,'left',5,ssEditInfMemberToolInfluence_TSL),(ssEditInfMemberToolSetWeight_CBG,'top',5,ssEditInfMemberToolPrebind_CBG)])
		# ssEditInfMemberToolSetWeight_FFG
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,af=[(ssEditInfMemberToolSetWeight_FFG,'right',5)])
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,ac=[(ssEditInfMemberToolSetWeight_FFG,'left',5,ssEditInfMemberToolInfluence_TSL),(ssEditInfMemberToolSetWeight_FFG,'top',5,ssEditInfMemberToolSetWeight_CBG)])
		
		# ssEditInfMemberToolBtn_SEP
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,af=[(ssEditInfMemberToolBtn_SEP,'right',5)])
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,ac=[(ssEditInfMemberToolBtn_SEP,'left',5,ssEditInfMemberToolInfluence_TSL),(ssEditInfMemberToolBtn_SEP,'top',5,ssEditInfMemberToolSetWeight_FFG)])
		
		#ssEditInfMemberToolStart_BTN
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,af=[(ssEditInfMemberToolStart_BTN,'right',5)])
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,ac=[(ssEditInfMemberToolStart_BTN,'left',5,ssEditInfMemberToolInfluence_TSL),(ssEditInfMemberToolStart_BTN,'bottom',5,ssEditInfMemberToolStop_BTN)])
		#ssEditInfMemberToolStop_BTN
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,af=[(ssEditInfMemberToolStop_BTN,'right',5),(ssEditInfMemberToolStop_BTN,'bottom',5)])
		mc.formLayout(ssEditInfMemberTool_FRM,e=1,ac=[(ssEditInfMemberToolStop_BTN,'left',5,ssEditInfMemberToolInfluence_TSL)])
		
		# Update influence list
		self.updateInfList(ssEditInfMemberToolInfluence_TSL,ssEditInfMemberToolSurfaceSkin_OMG)
		mc.textScrollList(ssEditInfMemberToolInfluence_TSL,e=1,sii=1)
		
		# showWindow
		mc.window(win,e=1,w=370,h=250)
		mc.showWindow(win)
	
	def paintInfluenceWeightsUI(self):
		'''
		Generate the UI for painting influence weights
		'''
		#Initialize UI variables
		cw1 = 100
		
		# Check paint context exists
		if not mc.artAttrCtx('artAttrContext',q=1,ex=1): mc.artAttrCtx('artAttrContext')
		
		# window
		win = 'surfaceSkin_paintInfluenceWeightsUI'
		if mc.window(win,ex=1): mc.deleteUI(win)
		mc.window(win,t='Surface Skin: Paint Influences Weight',mb=1,w=430,h=350,s=0)
		
		# Menu
		mc.menu(label='Edit',tearOff=1)
		mc.menuItem(label='Reset Settings',c='glTools.surfaceSkin.SurfaceSkinUI().paintInfluenceWeightsUI()')
		
		# FormLayout
		ssPaintInfWeights_FRM = mc.formLayout('surfaceSkin_paintInfluenceWeights_FRM',numberOfDivisions=100)
		
		# SurfaceSkin drop-down menu
		ssPaintInfWeightsSurfaceSkin_OMG = mc.optionMenuGrp('ssPaintInfWeightsSurfaceSkin_OMG',label='SurfaceSkin',cw=(1,70))
		for node in mc.ls(type='surfaceSkin'): mc.menuItem(node)
		
		# SurfaceSkin Influence List
		ssPaintInfWeightsInfluence_TSL = mc.textScrollList('ssPaintInfWeightsInfluence_TSL',numberOfRows=8,allowMultiSelection=0)
		mc.textScrollList(ssPaintInfWeightsInfluence_TSL,e=1,sc='glTools.surfaceSkin.SurfaceSkinUI().paintInfWeights_switchInf()')
		
		# Add change command for SurfaceSkin drop-down
		mc.optionMenuGrp(ssPaintInfWeightsSurfaceSkin_OMG,e=1,cc='glTools.surfaceSkin.SurfaceSkinUI().updateInfList("'+ssPaintInfWeightsInfluence_TSL+'","'+ssPaintInfWeightsSurfaceSkin_OMG+'")')
		
		# Brush Profile Buttons
		#-----------------------
		# Text label
		ssPaintInfWeightsProfile_TXT = mc.text('ssPaintInfWeightsProfile_TXT',l='Brush Type',fn='boldLabelFont',al='right')
		# Icon Radio Buttons
		ssPaintInfWeightsProfile_IRC = mc.iconTextRadioCollection('ssPaintInfWeightsProfile_IRC',p=ssPaintInfWeights_FRM)
		ssPaintInfWeightsGaussianBrush_IRB = mc.iconTextRadioButton('ssPaintInfWeightsGaussianBrush_IRB',st='iconOnly',w=35,h=36,i1='circleGaus.xpm')
		ssPaintInfWeightsPolyBrush_IRB = mc.iconTextRadioButton('ssPaintInfWeightsPolyBrush_IRB',st='iconOnly',w=35,h=36,i1='circlePoly.xpm')
		ssPaintInfWeightsSolidBrush_IRB = mc.iconTextRadioButton('ssPaintInfWeightsSolidBrush_IRB',st='iconOnly',w=35,h=36,i1='circleSolid.xpm')
		ssPaintInfWeightsSquareBrush_IRB = mc.iconTextRadioButton('ssPaintInfWeightsSquareBrush_IRB',st='iconOnly',w=35,h=36,i1='rect.xpm')
		# Set change commands
		mc.iconTextRadioButton('ssPaintInfWeightsGaussianBrush_IRB',e=1,onc='mc.artAttrCtx("artAttrContext",e=1,stP="gaussian")')
		mc.iconTextRadioButton('ssPaintInfWeightsPolyBrush_IRB',e=1,onc='mc.artAttrCtx("artAttrContext",e=1,stP="soft")')
		mc.iconTextRadioButton('ssPaintInfWeightsSolidBrush_IRB',e=1,onc='mc.artAttrCtx("artAttrContext",e=1,stP="solid")')
		mc.iconTextRadioButton('ssPaintInfWeightsSquareBrush_IRB',e=1,onc='mc.artAttrCtx("artAttrContext",e=1,stP="square")')
		# Set default
		paintProfile = mc.artAttrCtx('artAttrContext',q=1,stP=1)
		if paintProfile == 'gaussian': mc.iconTextRadioButton(ssPaintInfWeightsGaussianBrush_IRB,e=1,sl=1)
		elif paintProfile == 'soft': mc.iconTextRadioButton(ssPaintInfWeightsPolyBrush_IRB,e=1,sl=1)
		if paintProfile == 'solid': mc.iconTextRadioButton(ssPaintInfWeightsSolidBrush_IRB,e=1,sl=1)
		if paintProfile == 'square': mc.iconTextRadioButton(ssPaintInfWeightsSquareBrush_IRB,e=1,sl=1)
		else: 
			mc.iconTextRadioButton(ssPaintInfWeightsSolidBrush_IRB,e=1,sl=1)
			mc.artAttrCtx('artAttrContext',e=1,stP='solid')
		mc.setParent('..')
		
		# Size / Opacity / Value sliders
		#--------------------------------
		# Get current context values
		paintRad = mc.artAttrCtx('artAttrContext',q=1,r=1)
		paintOpac = mc.artAttrCtx('artAttrContext',q=1,op=1)
		paintVal = mc.artAttrCtx('artAttrContext',q=1,val=1)
		# Generate sliders
		ssPaintInfWeightsBrushSize_FSG = mc.floatSliderGrp('ssPaintInfWeightsBrushSize_FSG',label='Size',f=1,min=0,max=1,fmn=0,fmx=100,pre=2,v=0,cw=[(1,50),(2,35)])
		ssPaintInfWeightsBrushOpacity_FSG = mc.floatSliderGrp('ssPaintInfWeightsBrushOpacity_FSG',label='Opacity',f=1,min=0,max=1,fmn=0,fmx=100,pre=2,v=paintOpac,cw=[(1,50),(2,35)])
		ssPaintInfWeightsBrushValue_FSG = mc.floatSliderGrp('ssPaintInfWeightsBrushValue_FSG',label='Value',f=1,min=0,max=1,fmn=0,fmx=100,pre=2,v=paintVal,cw=[(1,50),(2,35)])
		mc.floatSliderGrp(ssPaintInfWeightsBrushSize_FSG,e=1,v=paintRad)
		# Set change commands
		mc.floatSliderGrp(ssPaintInfWeightsBrushSize_FSG,e=1,cc='mc.artAttrCtx("artAttrContext",e=1,r=mc.floatSliderGrp(\"ssPaintInfWeightsBrushSize_FSG",q=1,v=1))')
		mc.floatSliderGrp(ssPaintInfWeightsBrushOpacity_FSG,e=1,cc='mc.artAttrCtx("artAttrContext",e=1,op=mc.floatSliderGrp(\"ssPaintInfWeightsBrushOpacity_FSG",q=1,v=1))')
		mc.floatSliderGrp(ssPaintInfWeightsBrushValue_FSG,e=1,cc='mc.artAttrCtx("artAttrContext",e=1,val=mc.floatSliderGrp(\"ssPaintInfWeightsBrushValue_FSG",q=1,v=1))')
		
		# Separator
		ssPaintInfWeightsPaintMode_SEP = mc.separator(style='in')
		
		# Paint mode radio buttons
		ssPaintInfWeightsPaintMode_RBC = mc.radioCollection('ssPaintInfWeightsPaintMode_RBC')
		ssPaintInfWeightsPaintReplace_RB = mc.radioButton('ssPaintInfWeightsPaintReplace_RB',onc='mc.artAttrCtx("artAttrContext",e=1,sao="absolute")',al='left',l='Replace')
		ssPaintInfWeightsPaintAdd_RB = mc.radioButton('ssPaintInfWeightsPaintAdd_RB',onc='mc.artAttrCtx("artAttrContext",e=1,sao="additive")',al='left',l='Add')
		ssPaintInfWeightsPaintScale_RB = mc.radioButton('ssPaintInfWeightsPaintScale_RB',onc='mc.artAttrCtx("artAttrContext",e=1,sao="scale")',al='left',l='Scale')
		ssPaintInfWeightsPaintSmooth_RB = mc.radioButton('ssPaintInfWeightsPaintSmooth_RB',onc='mc.artAttrCtx("artAttrContext",e=1,sao="smooth")',al='left',l='Smooth')
		# Query and set UI paint mode
		paintMode = mc.artAttrCtx('artAttrContext',q=1,sao=1)
		if paintMode == 'absolute': mc.radioButton(ssPaintInfWeightsPaintReplace_RB,e=1,sl=1)
		elif paintMode == 'additive': mc.radioButton(ssPaintInfWeightsPaintAdd_RB,e=1,sl=1)
		elif paintMode == 'scale': mc.radioButton(ssPaintInfWeightsPaintScale_RB,e=1,sl=1)
		elif paintMode == 'absolute': mc.radioButton(ssPaintInfWeightsPaintSmooth_RB,e=1,sl=1)
		else:
			mc.radioButton(ssPaintInfWeightsPaintReplace_RB,e=1,sl=1)
			mc.artAttrCtx('artAttrContext',e=1,sao='absolute')
		mc.setParent('..')
		
		# Flood Button
		ssPaintInfWeightsPaintFlood_BTN = mc.button(l='Flood',c='mc.artAttrCtx("artAttrContext",e=1,clear=1)')
		
		# Separator
		ssPaintInfWeightsPaintFlood_SEP = mc.separator(style='in')
		
		# Paint Button
		paintEnable = 'ENABLE'
		if mc.currentCtx == 'artAttrContext': paintEnable = 'DISABLE'
		ssPaintInfWeightsPaint_BTN = mc.button('ssPaintInfWeightsPaint_BTN',l='PAINT: '+paintEnable,c='glTools.surfaceSkin.SurfaceSkinUI().toggleArtAttrCtx()')
		
		# Form Layout:============================
		
		# ssPaintInfWeightsSurfaceSkin_OMG
		mc.formLayout(ssPaintInfWeights_FRM,e=1,af=[(ssPaintInfWeightsSurfaceSkin_OMG,'left',5),(ssPaintInfWeightsSurfaceSkin_OMG,'top',5)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ap=[(ssPaintInfWeightsSurfaceSkin_OMG,'right',5,40)])
		
		# ssPaintInfWeightsPaint_BTN
		mc.formLayout(ssPaintInfWeights_FRM,e=1,af=[(ssPaintInfWeightsPaint_BTN,'left',5),(ssPaintInfWeightsPaint_BTN,'right',5),(ssPaintInfWeightsPaint_BTN,'bottom',5)])
		
		# ssPaintInfWeightsInfluence_TSL
		mc.formLayout(ssPaintInfWeights_FRM,e=1,af=[(ssPaintInfWeightsInfluence_TSL,'left',5)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsInfluence_TSL,'top',5,ssPaintInfWeightsSurfaceSkin_OMG),(ssPaintInfWeightsInfluence_TSL,'bottom',5,ssPaintInfWeightsPaint_BTN)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ap=[(ssPaintInfWeightsInfluence_TSL,'right',5,40)])
		
		# ssPaintInfWeightsProfile_IRC
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsProfile_TXT,'left',5,ssPaintInfWeightsInfluence_TSL),(ssPaintInfWeightsProfile_TXT,'right',5,ssPaintInfWeightsGaussianBrush_IRB),(ssPaintInfWeightsProfile_TXT,'bottom',5,ssPaintInfWeightsInfluence_TSL)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,af=[(ssPaintInfWeightsGaussianBrush_IRB,'top',5),(ssPaintInfWeightsPolyBrush_IRB,'top',5),(ssPaintInfWeightsSolidBrush_IRB,'top',5),(ssPaintInfWeightsSquareBrush_IRB,'top',5)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,af=[(ssPaintInfWeightsSquareBrush_IRB,'right',5)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsSolidBrush_IRB,'right',5,ssPaintInfWeightsSquareBrush_IRB),(ssPaintInfWeightsPolyBrush_IRB,'right',5,ssPaintInfWeightsSolidBrush_IRB),(ssPaintInfWeightsGaussianBrush_IRB,'right',5,ssPaintInfWeightsPolyBrush_IRB)])
		
		# ssPaintInfWeightsBrishSize_FSG
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsBrushSize_FSG,'left',5,ssPaintInfWeightsInfluence_TSL),(ssPaintInfWeightsBrushSize_FSG,'top',5,ssPaintInfWeightsGaussianBrush_IRB)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsBrushOpacity_FSG,'left',5,ssPaintInfWeightsInfluence_TSL),(ssPaintInfWeightsBrushOpacity_FSG,'top',5,ssPaintInfWeightsBrushSize_FSG)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsBrushValue_FSG,'left',5,ssPaintInfWeightsInfluence_TSL),(ssPaintInfWeightsBrushValue_FSG,'top',5,ssPaintInfWeightsBrushOpacity_FSG)])
		
		# ssPaintInfWeightsPaintMode_RBC
		mc.formLayout(ssPaintInfWeights_FRM,e=1,af=[(ssPaintInfWeightsPaintMode_SEP,'right',5)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsPaintMode_SEP,'top',5,ssPaintInfWeightsBrushValue_FSG,),(ssPaintInfWeightsPaintMode_SEP,'left',5,ssPaintInfWeightsInfluence_TSL)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsPaintReplace_RB,'top',5,ssPaintInfWeightsPaintMode_SEP),(ssPaintInfWeightsPaintAdd_RB,'top',5,ssPaintInfWeightsPaintMode_SEP)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsPaintScale_RB,'top',5,ssPaintInfWeightsPaintAdd_RB),(ssPaintInfWeightsPaintSmooth_RB,'top',5,ssPaintInfWeightsPaintAdd_RB)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ap=[(ssPaintInfWeightsPaintReplace_RB,'left',5,50),(ssPaintInfWeightsPaintAdd_RB,'left',5,75)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ap=[(ssPaintInfWeightsPaintScale_RB,'left',5,50),(ssPaintInfWeightsPaintSmooth_RB,'left',5,75)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,af=[(ssPaintInfWeightsPaintFlood_BTN,'right',5)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsPaintFlood_BTN,'top',5,ssPaintInfWeightsPaintScale_RB,),(ssPaintInfWeightsPaintFlood_BTN,'left',5,ssPaintInfWeightsInfluence_TSL)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,af=[(ssPaintInfWeightsPaintFlood_SEP,'right',5)])
		mc.formLayout(ssPaintInfWeights_FRM,e=1,ac=[(ssPaintInfWeightsPaintFlood_SEP,'top',5,ssPaintInfWeightsPaintFlood_BTN,),(ssPaintInfWeightsPaintFlood_SEP,'left',5,ssPaintInfWeightsInfluence_TSL)])
		
		# Update influence list
		self.updateInfList(ssPaintInfWeightsInfluence_TSL,ssPaintInfWeightsSurfaceSkin_OMG)
		mc.textScrollList(ssPaintInfWeightsInfluence_TSL,e=1,sii=1)
		
		# showWindow
		mc.window(win,e=1,w=430,h=350)
		mc.showWindow(win)
	
	def pruneWeightsByMembershipUI(self):
		'''
		Generate the UI for pruning influence weights based on influence membership
		'''
		# Initialize UI variables
		cw1 = 100
		
		# window
		win = 'surfaceSkin_pruneWeightsByMembershipUI'
		if mc.window(win,ex=1): mc.deleteUI(win)
		mc.window(win,t='Surface Skin: Prune Weights By Membership',mb=1,w=370,h=250,s=0)
		
		# Menu
		mc.menu(label='Edit',tearOff=1)
		mc.menuItem(label='Reset Settings',c='surfaceSkinUI_pruneWeightsByMembership()')
		
		# FormLayout
		ssPruneWeightByMember_FRM = mc.formLayout('surfaceSkin_pruneWeightByMember_FRM',numberOfDivisions=100)
		
		# SurfaceSkin drop-down menu
		ssPruneWeightByMemberSurfaceSkin_OMG = mc.optionMenuGrp('ssPruneWeightByMemberSurfaceSkin_OMG',label='SurfaceSkin',cw=(1,cw1))
		for node in mc.ls(type='surfaceSkin'): mc.menuItem(node)
		
		# SurfaceSkin Influence List
		ssPruneWeightByMemberInfluence_TSL = mc.textScrollList('ssPruneWeightByMemberInfluence_TSL',numberOfRows=8,allowMultiSelection=1,en=0)
		ssPruneWeightByMemberInfluence_CBG = mc.checkBoxGrp('ssPruneWeightByMemberInfluence_CBG',numberOfCheckBoxes=1,l='ALL Influences',v1=1,cw=(1,cw1+20))
		# SurfaceSkin Affected Geometry List
		ssPruneWeightByMemberAffected_TSL = mc.textScrollList('ssPruneWeightByMemberAffected_TSL',numberOfRows=8,allowMultiSelection=1,en=0)
		ssPruneWeightByMemberAffected_CBG = mc.checkBoxGrp('ssPruneWeightByMemberAffected_CBG',numberOfCheckBoxes=1,l='ALL Geometry',v1=1,cw=(1,cw1+20))
		
		# Add change command for optionMenuGrp
		mc.optionMenuGrp(ssPruneWeightByMemberSurfaceSkin_OMG,e=1,cc='glTools.surfaceSkin.SurfaceSkinUI().updateInfList("'+ssPruneWeightByMemberInfluence_TSL+'","'+ssPruneWeightByMemberSurfaceSkin_OMG+'");rig.surfaceSkin.SurfaceSkinUI().updateGeoList("'+ssPruneWeightByMemberAffected_TSL+'","'+ssPruneWeightByMemberSurfaceSkin_OMG+'")')
		# Add change command for checkBoxGrp's
		mc.checkBoxGrp('ssPruneWeightByMemberInfluence_CBG',e=1,cc='mc.textScrollList("ssPruneWeightByMemberInfluence_TSL",e=1,da=1,en=abs(1-(mc.checkBoxGrp("ssPruneWeightByMemberInfluence_CBG",q=1,v1=1))))')
		mc.checkBoxGrp('ssPruneWeightByMemberAffected_CBG',e=1,cc='mc.textScrollList("ssPruneWeightByMemberAffected_TSL",e=1,da=1,en=abs(1-(mc.checkBoxGrp("ssPruneWeightByMemberAffected_CBG",q=1,v1=1))))')
		
		# Button
		ssPruneWeightByMemberPrune_BTN = mc.button('ssPruneWeightByMemberPrune_BTN',l='Prune Weights',c='glTools.surfaceSkin.SurfaceSkinUI().pruneNonMemberWeightsFromUI()')
		
		# Form Layout:============================
		
		# ssPruneWeightByMemberSurfaceSkin_OMG
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,af=[(ssPruneWeightByMemberSurfaceSkin_OMG,'left',5),(ssPruneWeightByMemberSurfaceSkin_OMG,'top',5)])
		
		# ssPruneWeightByMemberPrune_BTN
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,af=[(ssPruneWeightByMemberPrune_BTN,'bottom',5)])
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,ap=[(ssPruneWeightByMemberPrune_BTN,'left',5,25),(ssPruneWeightByMemberPrune_BTN,'right',5,75)])
		
		# ssPruneWeightByMemberInfluence_CBG
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,af=[(ssPruneWeightByMemberInfluence_CBG,'left',5)])
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,ac=[(ssPruneWeightByMemberInfluence_CBG,'top',5,ssPruneWeightByMemberSurfaceSkin_OMG)])
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,ap=[(ssPruneWeightByMemberInfluence_CBG,'right',5,50)])
		# ssPruneWeightByMemberInfluence_TSL
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,af=[(ssPruneWeightByMemberInfluence_TSL,'left',5)])
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,ac=[(ssPruneWeightByMemberInfluence_TSL,'top',5,ssPruneWeightByMemberInfluence_CBG),(ssPruneWeightByMemberInfluence_TSL,'bottom',5,ssPruneWeightByMemberPrune_BTN)])
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,ap=[(ssPruneWeightByMemberInfluence_TSL,'right',5,50)])
		
		# ssPruneWeightByMemberAffected_CBG
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,ac=[(ssPruneWeightByMemberAffected_CBG,'top',5,ssPruneWeightByMemberSurfaceSkin_OMG)])
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,ap=[(ssPruneWeightByMemberAffected_CBG,'left',5,50)])
		# ssPruneWeightByMemberAffected_TSL
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,af=[(ssPruneWeightByMemberAffected_TSL,'right',5)])
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,ac=[(ssPruneWeightByMemberAffected_TSL,'top',5,ssPruneWeightByMemberAffected_CBG),(ssPruneWeightByMemberAffected_TSL,'bottom',5,ssPruneWeightByMemberPrune_BTN)])
		mc.formLayout(ssPruneWeightByMember_FRM,e=1,ap=[(ssPruneWeightByMemberAffected_TSL,'left',5,50)])
		
		# Update influence/affectedGeo lists
		self.updateInfList(ssPruneWeightByMemberInfluence_TSL,ssPruneWeightByMemberSurfaceSkin_OMG)
		self.updateGeoList(ssPruneWeightByMemberAffected_TSL,ssPruneWeightByMemberSurfaceSkin_OMG)
		
		# showWindow
		mc.window(win,e=1,w=370,h=250)
		mc.showWindow(win)
	
	def pruneMembershipByWeightsUI(self):
		'''
		Generate the UI for pruning influence membership based on influence weights
		'''
		# Initialize UI variables
		cw1 = 100
		
		# window
		win = 'surfaceSkin_pruneMembershipByWeightsUI'
		if mc.window(win,ex=1): mc.deleteUI(win)
		mc.window(win,t='Surface Skin: Prune Membership By Weights',mb=1,w=370,h=250,s=0)
		
		# Menu
		mc.menu(label='Edit',tearOff=1)
		mc.menuItem(label='Reset Settings',c='surfaceSkinUI_pruneMembershipByWeights()')
		
		# FormLayout
		ssPruneMemberByWeight_FRM = mc.formLayout('surfaceSkin_pruneMemberByWeight_FRM',numberOfDivisions=100)
		
		# SurfaceSkin drop-down menu
		ssPruneMemberByWeightSurfaceSkin_OMG = mc.optionMenuGrp('ssPruneMemberByWeightSurfaceSkin_OMG',label='SurfaceSkin',cw=(1,cw1))
		for node in mc.ls(type='surfaceSkin'): mc.menuItem(node)
		
		# SurfaceSkin Influence List
		ssPruneMemberByWeightInfluence_TSL = mc.textScrollList('ssPruneMemberByWeightInfluence_TSL',numberOfRows=8,allowMultiSelection=1,en=0)
		ssPruneMemberByWeightInfluence_CBG = mc.checkBoxGrp('ssPruneMemberByWeightInfluence_CBG',numberOfCheckBoxes=1,l='ALL Influences',v1=1,cw=(1,cw1+20))
		# SurfaceSkin Affected Geometry List
		ssPruneMemberByWeightAffected_TSL = mc.textScrollList('ssPruneMemberByWeightAffected_TSL',numberOfRows=8,allowMultiSelection=1,en=0)
		ssPruneMemberByWeightAffected_CBG = mc.checkBoxGrp('ssPruneMemberByWeightAffected_CBG',numberOfCheckBoxes=1,l='ALL Geometry',v1=1,cw=(1,cw1+20))
		
		# Add change command for optionMenuGrp
		mc.optionMenuGrp(ssPruneMemberByWeightSurfaceSkin_OMG,e=1,cc='glTools.surfaceSkin.SurfaceSkinUI().updateInfList("'+ssPruneMemberByWeightInfluence_TSL+'","'+ssPruneMemberByWeightSurfaceSkin_OMG+'");rig.surfaceSkin.SurfaceSkinUI().updateGeoList("'+ssPruneMemberByWeightAffected_TSL+'","'+ssPruneMemberByWeightSurfaceSkin_OMG+'")')
		# Add change command for checkBoxGrp's
		mc.checkBoxGrp('ssPruneMemberByWeightInfluence_CBG',e=1,cc='mc.textScrollList("ssPruneMemberByWeightInfluence_TSL",e=1,da=1,en=abs(1-(mc.checkBoxGrp("ssPruneMemberByWeightInfluence_CBG",q=1,v1=1))))')
		mc.checkBoxGrp('ssPruneMemberByWeightAffected_CBG',e=1,cc='mc.textScrollList("ssPruneMemberByWeightAffected_TSL",e=1,da=1,en=abs(1-(mc.checkBoxGrp("ssPruneMemberByWeightAffected_CBG",q=1,v1=1))))')
		
		# Weight Threshold
		ssPruneMemberByWeightThreshold_FSG = mc.floatSliderGrp('ssPruneMemberByWeightThreshold_FSG',label='Threshold Weight',f=1,min=0,max=1,fmn=0,fmx=1,pre=3,v=0,cw=(1,cw1+20))
		
		# Button
		ssPruneMemberByWeightPrune_BTN = mc.button('ssPruneMemberByWeightPrune_BTN',l='Prune Membership',c='glTools.surfaceSkin.SurfaceSkinUI().pruneMemberByWeightsFromUI()')
		
		# Form Layout:============================
		
		# ssPruneMemberByWeightSurfaceSkin_OMG
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,af=[(ssPruneMemberByWeightSurfaceSkin_OMG,'left',5),(ssPruneMemberByWeightSurfaceSkin_OMG,'top',5)])
		
		# ssPruneMemberByWeightPrune_BTN
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,af=[(ssPruneMemberByWeightPrune_BTN,'bottom',5)])
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,ap=[(ssPruneMemberByWeightPrune_BTN,'left',5,25),(ssPruneMemberByWeightPrune_BTN,'right',5,75)])
		
		# ssPruneMemberByWeightThreshold_FSG
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,af=[(ssPruneMemberByWeightThreshold_FSG,'left',5),(ssPruneMemberByWeightThreshold_FSG,'right',5)])
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,ac=[(ssPruneMemberByWeightThreshold_FSG,'bottom',5,ssPruneMemberByWeightPrune_BTN)])
		
		# ssPruneMemberByWeightInfluence_CBG
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,af=[(ssPruneMemberByWeightInfluence_CBG,'left',5)])
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,ac=[(ssPruneMemberByWeightInfluence_CBG,'top',5,ssPruneMemberByWeightSurfaceSkin_OMG)])
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,ap=[(ssPruneMemberByWeightInfluence_CBG,'right',5,50)])
		# ssPruneMemberByWeightInfluence_TSL
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,af=[(ssPruneMemberByWeightInfluence_TSL,'left',5)])
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,ac=[(ssPruneMemberByWeightInfluence_TSL,'top',5,ssPruneMemberByWeightInfluence_CBG),(ssPruneMemberByWeightInfluence_TSL,'bottom',5,ssPruneMemberByWeightThreshold_FSG)])
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,ap=[(ssPruneMemberByWeightInfluence_TSL,'right',5,50)])
		
		# ssPruneMemberByWeightAffected_CBG
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,ac=[(ssPruneMemberByWeightAffected_CBG,'top',5,ssPruneMemberByWeightSurfaceSkin_OMG)])
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,ap=[(ssPruneMemberByWeightAffected_CBG,'left',5,50)])
		# ssPruneMemberByWeightAffected_TSL
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,af=[(ssPruneMemberByWeightAffected_TSL,'right',5)])
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,ac=[(ssPruneMemberByWeightAffected_TSL,'top',5,ssPruneMemberByWeightAffected_CBG),(ssPruneMemberByWeightAffected_TSL,'bottom',5,ssPruneMemberByWeightThreshold_FSG)])
		mc.formLayout(ssPruneMemberByWeight_FRM,e=1,ap=[(ssPruneMemberByWeightAffected_TSL,'left',5,50)])
		
		# Update influence/affectedGeo lists
		self.updateInfList(ssPruneMemberByWeightInfluence_TSL,ssPruneMemberByWeightSurfaceSkin_OMG)
		self.updateGeoList(ssPruneMemberByWeightAffected_TSL,ssPruneMemberByWeightSurfaceSkin_OMG)
		
		# showWindow
		mc.window(win,e=1,w=370,h=250)
		mc.showWindow(win)
	
	def coordinateUtilitiesUI(self):
		'''
		'''
		# Initialize UI variables
		cw1 = 80
		
		# window
		win = 'ssCoordUtilsUI'
		if mc.window(win,ex=1): mc.deleteUI(win)
		mc.window(win,t='Surface Skin: Coordinate Utilities',mb=1,s=0)
		
		# Menu
		mc.menu(label='Edit',tearOff=1)
		mc.menuItem(label='Reset Settings',c='glTools.surfaceSkin.ui.SurfaceSkinUI().coordinateUtilitiesUI()')
		
		# FormLayout
		ssCoordUtilsFRM = mc.formLayout('ssCoordUtilsFRM',numberOfDivisions=100)
		
		# SurfaceSkin drop-down menu
		ssCoordUtilsOMG = mc.optionMenuGrp('ssCoordUtilsOMG',label='SurfaceSkin',cw=(1,cw1))
		surfaceSkinList = mc.ls(type='surfaceSkin')
		for node in surfaceSkinList: mc.menuItem(node)
		
		# Separator
		ssCoordUtilsTopSEP = mc.separator(style='single')
		
		# SurfaceSkin Influence List
		ssCoordUtilsInfTXT = mc.text(l=' -- Influence List:',al='left')
		ssCoordUtilsInfTSL = mc.textScrollList('ssCoordUtilsTSL',numberOfRows=8,allowMultiSelection=False)
		
		# Coordinate selection buttons
		ssCoordUtilsSelectB = mc.button(l='Selected Surface Coord',c='glTools.surfaceSkin.ui.SurfaceSkinUI().selectCoordFromUI()')
		ssCoordUtilsCopyB = mc.button(l='Copy Target Coord',c='glTools.surfaceSkin.ui.SurfaceSkinUI().copyCoordFromUI()')
		ssCoordUtilsAverageB = mc.button(l='Average Target Coord',c='glTools.surfaceSkin.ui.SurfaceSkinUI().averageCoordFromUI()')
		ssCoordUtilsPasteB = mc.button(l='Paste Target Coord',c='glTools.surfaceSkin.ui.SurfaceSkinUI().pasteCoordFromUI()')
		ssCoordUtilsCoordFFG = mc.floatFieldGrp('ssCoordUtilsCoordFFG',numberOfFields=2,v1=0.0,v2=0.0,pre=7,en=True,h=20,cw=[(1,cw1*1.85),(2,cw1*1.85)],cal=[(1,'center'),(2,'center')])
		
		# Separator
		ssCoordUtilsSEP = mc.separator(style='single')
		
		# Neighbour Average
		ssCoordUtilsRBG = mc.radioButtonGrp('ssCoordUtilsNeighbourRBG',nrb=3,label='Mode:',labelArray3=['Horizontal','Vertical','Both'],sl=3,h=20,cw=[(1,50),(2,cw1+20),(3,cw1),(4,cw1)])
		ssCoordUtilsNeighbourAvgB = mc.button(l='Neighbour Average',c='glTools.surfaceSkin.ui.SurfaceSkinUI().neighbourAverageCoordFromUI()')
		
		# Popup menu
		mc.popupMenu(parent=ssCoordUtilsOMG)
		mc.menuItem(label='Get connected',c='glTools.surfaceSkin.ui.SurfaceSkinUI().getConnectedSurfaceSkin("'+ssCoordUtilsOMG+'")')
		
		# Setup UI callbacks
		mc.optionMenuGrp(ssCoordUtilsOMG,e=True,cc='glTools.surfaceSkin.ui.SurfaceSkinUI().updateInfList("'+ssCoordUtilsInfTSL+'","'+ssCoordUtilsOMG+'")')
		
		# Form Layout: MAIN ---------
		
		# ssCoordUtilsOMG
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsOMG,'left',5),(ssCoordUtilsOMG,'top',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsOMG,'right',5,50)])
		
		# Separator
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsTopSEP,'left',5),(ssCoordUtilsTopSEP,'right',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsTopSEP,'top',5,ssCoordUtilsOMG)])
		
		# ssCoordUtilsInfTXT
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsInfTXT,'left',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsInfTXT,'right',5,50)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsInfTXT,'top',5,ssCoordUtilsTopSEP)])
		
		# ssCoordUtilsInfTSL
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsInfTSL,'left',5),(ssCoordUtilsInfTSL,'bottom',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsInfTSL,'right',5,50)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsInfTSL,'top',5,ssCoordUtilsInfTXT)])
		
		# ssCoordUtilsSelectB
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsSelectB,'right',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsSelectB,'left',5,50)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsSelectB,'top',5,ssCoordUtilsTopSEP)])
		
		# ssCoordUtilsCopyB
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsCopyB,'right',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsCopyB,'left',5,50)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsCopyB,'top',5,ssCoordUtilsSelectB)])
		
		# ssCoordUtilsAverageB
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsAverageB,'right',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsAverageB,'left',5,50)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsAverageB,'top',5,ssCoordUtilsCopyB)])
		
		# ssCoordUtilsCoordFFG
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsCoordFFG,'right',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsCoordFFG,'left',5,50)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsCoordFFG,'top',5,ssCoordUtilsAverageB)])
		
		# ssCoordUtilsPasteB
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsPasteB,'right',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsPasteB,'left',5,50)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsPasteB,'top',5,ssCoordUtilsCoordFFG)])
		
		# Separator
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsSEP,'right',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsSEP,'left',5,50)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsSEP,'top',5,ssCoordUtilsPasteB)])
		
		# ssCoordUtilsRBC
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsRBG,'right',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsRBG,'left',5,50)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsRBG,'top',5,ssCoordUtilsSEP)])
		
		# ssCoordUtilsRBC
		mc.formLayout(ssCoordUtilsFRM,e=1,af=[(ssCoordUtilsNeighbourAvgB,'right',5)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ap=[(ssCoordUtilsNeighbourAvgB,'left',5,50)])
		mc.formLayout(ssCoordUtilsFRM,e=1,ac=[(ssCoordUtilsNeighbourAvgB,'top',5,ssCoordUtilsRBG)])
	
		# showWindow
		mc.window(win,e=1,w=1,h=1)
		mc.showWindow(win)
		
		# Refresh window
		mc.window(win,e=1,w=610,h=280)
		if surfaceSkinList: mc.optionMenuGrp(ssCoordUtilsOMG,e=True,sl=1)
		self.updateInfList(ssCoordUtilsInfTSL,ssCoordUtilsOMG)
	
	def curveCoordinateUI(self):
		'''
		'''
		# Initialize UI variables
		cw1 = 80
		
		# window
		win = 'ssCurveCoordUI'
		if mc.window(win,ex=1): mc.deleteUI(win)
		mc.window(win,t='Surface Skin: Curve Coordinates',mb=1,s=0)
		
		# Menu
		mc.menu(label='Edit',tearOff=1)
		mc.menuItem(label='Reset Settings',c='glTools.surfaceSkin.ui.SurfaceSkinUI().coordinateUtilitiesUI()')
		
		# FormLayout
		ssCurveCoordFRM = mc.formLayout('ssCurveCoordFRM',numberOfDivisions=100)
		
		# SurfaceSkin drop-down menu
		ssCurveCoordOMG = mc.optionMenuGrp('ssCurveCoordOMG',label='SurfaceSkin',cw=(1,cw1))
		surfaceSkinList = mc.ls(type='surfaceSkin')
		for node in surfaceSkinList: mc.menuItem(node)
		
		# Separator
		ssCurveCoordTopSEP = mc.separator(style='single')
		
		# SurfaceSkin Influence List
		ssCurveCoordInfTXT = mc.text(l=' -- Influence List:',al='left')
		ssCurveCoordInfTSL = mc.textScrollList('ssCurveCoordTSL',numberOfRows=8,allowMultiSelection=False)
		
		# Curve Type
		ssCurveCoordTypeRBG = mc.radioButtonGrp('ssCurveCoordTypeRBG',nrb=2,label='Curve Type:',labelArray2=['Curve','Isoparm'],sl=1,h=20,cw=[(1,cw1),(2,cw1),(3,cw1)])
		
		# Curve selection
		mc.textFieldButtonGrp(label='Curve',text='',buttonLabel='Select',bc='')
		
		
	#===========================================================
	# UI Manipulation Methods
	#===========================================================
	
	def addToInfList(self,TSL,filterType=''):
		'''
		Add selection list strings as entries into a specified textScrollList UI element
		@param TSL: TextScrollList to append names to
		@type TSL: str
		@param filterType: Only append objects of the specified type to the textScrollList. If left at default, will accept all types.
		@type filterType: str or list
		'''
		# Check filter type
		if not filterType: filterType = ''
		
		# Get current influence list
		currentInfList = mc.textScrollList(TSL,q=True,ai=True)
		if not currentInfList: currentInfList = []
		
		# Get current selection
		influenceList = mc.ls(sl=True,type='transform')
		for inf in influenceList:
			# Test inf exists in current list
			if currentInfList.count(inf): continue
			# Check filter type
			infShape = mc.listRelatives(inf,s=True,ni=True,pa=True)
			if not infShape: continue
			infType = mc.objectType(infShape[0])
			if filterType and not (filterType == infType): continue
			# Append to list
			mc.textScrollList(TSL,e=True,a=inf)
	
	def removeFromInfList(self,TSL):
		'''
		Removed selection list strings as entries from a specified textScrollList UI element
		@param TSL: TextScrollList to remove names from
		@type TSL: str
		'''
		# Get influence list from textScrollList
		influenceList = mc.textScrollList(TSL,q=1,si=1)
		if type(influenceList) == list:
			for inf in influenceList:
				mc.textScrollList(TSL,e=1,ri=inf)
	
	def selectAllInList(self,TSL):
		'''
		Select all items in a textScrollList
		@param TSL: TextScrollList to select items in
		@type TSL: str
		'''
		listItems = mc.textScrollList(TSL,q=1,ai=1)
		mc.select(listItems)
		mc.textScrollList(TSL,e=1,si=listItems)
	
	def editInfluenceMembership_switchSurfaceSkin(self):
		'''
		Trigger Edit Influence Membership UI to update when a surfaceSkin node is selected in the interface
		'''
		# Update influence list
		self.updateInfList('ssEditInfMemberInf_TSL','ssEditInfMemberSurfSkin_TSL')
		# Select first influence in list
		mc.textScrollList('ssEditInfMemberInf_TSL',e=True,sii=1)
		# Update influence member list
		self.editInfluenceMembership_switchInfluence()
	
	def editInfluenceMembership_switchInfluence(self):
		'''
		Trigger Edit Influence Membership UI to update when an influence is selected in the interface
		'''
		# Get current surfaceSkin node
		surfaceSkinNode = mc.textScrollList('ssEditInfMemberSurfSkin_TSL',q=True,si=True)[0] # Get first selected item in list
		# Get influence list
		influenceList = mc.textScrollList('ssEditInfMemberInf_TSL',q=True,si=True)
		
		# Clear memebr list
		mc.textScrollList('ssEditInfMemberMember_TSL',e=True,ra=True)
		
		# Update influence member list
		memberList = []
		for influence in influenceList:
			memberList.extend(self.surfaceSkinUtils.getInfluenceMembership(influence,surfaceSkinNode))
		if memberList: memberList = mc.ls(memberList,fl=True)
		
		# Re-populate member list
		mc.textScrollList('ssEditInfMemberMember_TSL',e=True,a=memberList)
		
	def updateInfList(self,TSL,UIelem,sort=1):
		'''
		Update a named textScrollList with the current influence list of a surfaceSkin node 
		specified by a named optionMenuGrp.
		@param TSL: textScrollList to update
		@type TSL: str
		@param UIelem: UI element that will supply the name of the surfaceSkinNode
		@type UIelem: str
		@param sort: Sort option for influence list. 0=None, 1=Index, 2=Alpha
		@type sort: int
		'''
		# Clear influence list
		mc.textScrollList(TSL,e=1,ra=1)
		
		# Determine UI element type
		try: mc.objectTypeUI(UIelem)
		except: raise UserInputError('UI element '+UIelem+' connot be found!')
		
		# Get selected surfaceSkin node
		surfaceSkinNode = ''
		UIelemType = mc.objectTypeUI(UIelem)
		if UIelemType == 'textScrollList':
			surfaceSkinNode = mc.textScrollList(UIelem,q=1,si=1)[0]
		elif UIelemType == 'rowGroupLayout':
			surfaceSkinNode = mc.optionMenuGrp(UIelem,q=1,v=1)
		
		if not mc.objExists(surfaceSkinNode): return
		
		# get influence list for surfaceSkin node
		influenceList = self.surfaceSkinUtils.getInfluenceList(surfaceSkinNode)
		if sort == 2: influenceList.sort()
		
		# Add influences to list
		validTransformList = ['transform','joint']
		for influence in influenceList:
			if not validTransformList.count(mc.objectType(influence)):
				influence = mc.listRelatives(influence,p=True,pa=True)[0]
			mc.textScrollList(TSL,e=1,a=influence)
		
		# Highlight current paintable influence
		paintInf = self.surfaceSkinUtils.getPaintInfluence(surfaceSkinNode)
		mc.textScrollList(TSL,e=1,si=paintInf)
	
	def updateGeoList(self,TSL,OMG):
		'''
		Update the affected geometry list when a surfaceSkin node is selected
		@param TSL: textScrollList to update
		@type TSL: str
		@param OMG: OptionMenuGrp to query the surfaceSkin node from
		@type OMG: str
		'''
		# Clear influence list
		mc.textScrollList(TSL,e=1,ra=1)
		# Get selected surfaceSkin node
		surfaceSkinNode = mc.optionMenuGrp(OMG,q=1,v=1)
		if not mc.objExists(surfaceSkinNode): return
		# Get influence list for surfaceSkin node
		affectedGeoList = self.surfaceSkinUtils.getAffectedGeometry(surfaceSkinNode).keys()
		# Add influences to list
		for geo in affectedGeoList:
			if mc.objectType(geo) != 'transform': geo = mc.listRelatives(geo,p=True,pa=True)[0]
			mc.textScrollList(TSL,e=1,a=geo)
	
	def editInfluenceMembership_selectMembersInList(self):
		'''
		Highlight the components selected in the editInfluenceMembership interface.
		'''
		# Get selected items from the textScrollList
		selecetedMembers = mc.textScrollList('ssEditInfMemberMember_TSL',q=1,si=1)
		# Select components
		mc.select(selecetedMembers)
	
	def paintInfWeights_switchInf(self):
		'''
		Update the influence connections for the current surfaceSkin node when an influence is selected in the paint influence interface
		'''
		# Get surfaceSkin node
		surfaceSkinNode = mc.optionMenuGrp('ssPaintInfWeightsSurfaceSkin_OMG',q=1,v=1)
		influenceList = self.surfaceSkinUtils.getInfluenceList(surfaceSkinNode)
		
		# Get influence
		influence = mc.textScrollList('ssPaintInfWeightsInfluence_TSL',q=1,si=1)[0]
		if not influenceList.count(influence):
			influence = glTools.utils.selection.getShapes(influence)[0]
		
		# Make paint attr connections
		if influence != mc.listConnections(surfaceSkinNode+'.paintTrans',s=1,d=0,sh=1)[0]:
			mc.connectAttr(influence+'.message',surfaceSkinNode+'.paintTrans',f=1)
		
		if mc.currentCtx() == 'artAttrContext':
			mm.eval('artSetToolAndSelectAttr "artAttrCtx" "surfaceSkin.'+surfaceSkinNode+'.paintWeight"')
		
	def getConnectedSurfaceSkin(self,OMG):
		'''
		Set optionMenuGrp selection based on the first connected surfaceSkin to the selected geometry
		@param OMG: OptionMenuGrp to set selection for
		@type OMG: str
		'''
		# Get user selection
		sel = mc.ls(sl=True,fl=True)
		if not sel: return
		
		# Get connected surfaceSkin nodes
		nodeHistoryList = mc.listHistory(sel[0])
		surfaceSkinList = mc.ls(nodeHistoryList,type='surfaceSkin')
		if not surfaceSkinList:
			raise UserInputError('No surfaceSkin attached to object "'+sel[0]+'"!')
		
		# Set optionMenuGrp selection
		try: mc.optionMenuGrp(OMG,e=True,v=surfaceSkinList[0])
		except: raise UserInputError('SurfaceSkin "'+surfaceSkinList[0]+'" not found in menu list!!')
		else: glTools.surfaceSkin.ui.SurfaceSkinUI().updateInfList('ssCoordUtilsTSL',OMG)
	
	#===========================================================
	# UI Wrapper Methods
	#===========================================================
	
	def createFromUI(self):
		'''
		Method called from Create SurfaceSkin UI
		Passes argument values from UI elements to the surfaceSkin.utils.create() method
		'''
		# Get UI info
		name = mc.textFieldGrp('ssCreateName_TFG',q=True,text=True)
		defaultWeight = mc.floatSliderGrp('ssCreateWeight_FSG',q=True,v=True)
		maxDist = mc.floatSliderGrp('ssCreateMaxDist_FSG',q=True,v=True)
		influenceList = mc.textScrollList('ssCreateInf_TSL',q=True,ai=True)
		
		# Get affected objects from selection
		affectedGeo = mc.ls(sl=True,type='transform')
		for obj in affectedGeo:
			# Get object shape
			objShape = mc.listRelatives(obj,s=True,ni=True,pa=True)
			if not objShape:
				print('No valid shapes found for object '+obj+'! Skipping object and removing from affected geometry list!!')
				affectedGeo.remove(obj)
			# Check geometry type
			objType = mc.objectType(objShape[0])
			if (objType != 'mesh') and (objType != 'nurbsCurve') and (objType != 'nurbsSurface'):
				affectedGeo.remove(obj)
			# Check affectedGeo doesn't appear in influence list
			if influenceList.count(obj):
				print('Object '+obj+' cant be bound as it is listed as an influence! Removing from affected geometry list!!')
				affectedGeo.remove(obj)
		
		# Create deformer
		if len(affectedGeo):
			surfaceSkinNode = self.surfaceSkinUtils.create(affectedGeo,influenceList,defaultWeight,maxDist,name)
			print('surfaceSkin node '+surfaceSkinNode+' created successfully!')
			mc.deleteUI(self.createWin)
		else:
			print('Select valid geometry to bind to listed influences!')
		
	def addInfluenceFromUI(self):
		'''
		Method called from Add Influence UI
		Passes argument values from UI elements to the surfaceSkin.utils.addInfluence() method
		'''
		# Get UI info
		surfaceSkinNode = mc.optionMenuGrp('ssAddInfSurfSkin_OMG',q=True,v=True)
		influenceList = mc.textScrollList('ssAddInf_TSL',q=True,ai=True)
		defaultWeight = mc.floatSliderGrp('ssAddInfWeight_FSG',q=True,v=True)
		maxDist = mc.floatSliderGrp('ssAddInfMaxDist_FSG',q=True,v=True)
		preBind = mc.checkBoxGrp('ssAddInfPreBind_CBG',q=True,vTrue=True)
		
		# Add Influence
		self.surfaceSkinUtils.addInfluence(influenceList,surfaceSkinNode,defaultWeight,maxDist,preBind)
		print('Influences added to surfaceSkin node '+surfaceSkinNode+' successfully!')
		mc.deleteUI(self.addInfluenceWin)
	
	def addTransformInfluenceFromUI(self):
		'''
		Method called from Add Transform Influence UI
		Passes argument values from UI elements to the surfaceSkin.utils.addTransformInfluence() method
		'''
		# Get UI info
		surfaceSkinNode = mc.optionMenuGrp('ssAddTransInfSurfSkin_OMG',q=True,v=True)
		influenceList = mc.textScrollList('ssAddTransInf_TSL',q=True,ai=True)
		defaultWeight = mc.floatSliderGrp('ssAddTransInfWeight_FSG',q=True,v=True)
		maxDist = mc.floatSliderGrp('ssAddTransInfMaxDist_FSG',q=True,v=True)
		calcPreBind = mc.checkBoxGrp('ssAddTransInfPreBind_CBG',q=True,vTrue=True)
		createPreBindMatrix = mc.checkBoxGrp('ssAddTransInfCreateBase_CBG',q=True,vTrue=True)
		
		# Add Transform Influence
		self.surfaceSkinUtils.addTransformInfluence(influenceList,surfaceSkinNode,defaultWeight,maxDist,calcPreBind,createPreBindMatrix)
		print('Influences added to surfaceSkin node '+surfaceSkinNode+' successfully!')
		mc.deleteUI(self.addTransInfluenceWin)
	
	def removeInfluenceFromUI(self):
		'''
		Method called from Remove Influence UI
		Passes argument values from UI elements to the surfaceSkin.utils.removeInfluence() method
		'''
		# Get UI info
		surfaceSkinNode = mc.optionMenuGrp('ssRemoveInfSurfSkin_OMG',q=True,v=True)
		influenceList = mc.textScrollList('ssRemoveInf_TSL',q=True,si=True)
		
		# Verify info
		if not mc.objExists(surfaceSkinNode): return
		if type(influenceList) != list: return
		
		# Remove influences
		for influence in influenceList:
			self.surfaceSkinUtils.removeInfluence(influence, surfaceSkinNode)
		
		# Update UI influence list
		self.updateInfList('ssRemoveInf_TSL','ssRemoveInfSurfSkin_OMG')
	
	def editInfluenceMembership_add(self):
		'''
		Add the selected components to the member list of the current influence
		'''
		# Get surfaceSkin node
		surfaceSkinNode = mc.textScrollList('ssEditInfMemberSurfSkin_TSL',q=True,si=True)[0] # Get first selected item in list
		# Get influence
		influenceList = mc.textScrollList('ssEditInfMemberInf_TSL',q=True,si=True)
		# calculatePreBind
		calcPreBind = mc.menuItem('ssEditMemberCalcPreBind',q=True,checkBox=True)
		# Get selected components
		componentList = glTools.utils.component.getSingleIndexComponentList()
		# Iterate through each influence
		for influence in influenceList:
			# Iterate through each object
			for obj in componentList.keys():
				# Add components surface data
				self.surfaceSkinUtils.setSurfaceCoordArray(obj,componentList[obj],influence,surfaceSkinNode,0,calcPreBind,mode=1)
		# Update UI
		self.editInfluenceMembership_switchInfluence()
		
	def editInfluenceMembership_remove(self):
		'''
		Remove the selected components from the member list of the current influence
		'''
		# Get surfaceSkin node
		surfaceSkinNode = mc.textScrollList('ssEditInfMemberSurfSkin_TSL',q=True,si=True)[0] # Get first selected item in list
		# Get influence
		influenceList = mc.textScrollList('ssEditInfMemberInf_TSL',q=True,si=True)
		# Get selected members
		componentList = glTools.utils.component.getSingleIndexComponentList()
		# Iterate through each influence
		for influence in influenceList:
			# Iterate through each object
			for obj in componentList.keys():
				# Remove components surface data
				self.surfaceSkinUtils.setSurfaceCoordArray(obj,componentList[obj],influence,surfaceSkinNode,mode=3)
		# Update UI
		self.editInfluenceMembership_switchInfluence()
	
	def editInfluenceMembership_set(self):
		'''
		Set the selected components as the member list for the current influence
		'''
		# Get surfaceSkin node
		surfaceSkinNode = mc.textScrollList('ssEditInfMemberSurfSkin_TSL',q=True,si=True)[0] # Get first selected item in list
		# Get influence
		influenceList = mc.textScrollList('ssEditInfMemberInf_TSL',q=True,si=True)
		# calculatePreBind
		calcPreBind = mc.menuItem('ssEditMemberCalcPreBind',q=True,checkBox=True)
		# Get selected components
		componentList = glTools.utils.component.getSingleIndexComponentList()
		# Iterate through each influence
		for influence in influenceList:
			# Iterate through each object
			for obj in componentList.keys():
				# Set components surface data
				self.surfaceSkinUtils.setSurfaceCoordArray(obj,componentList[obj],influence,surfaceSkinNode,0,calcPreBind,mode=2)
		# Update UI
		self.editInfluenceMembership_switchInfluence()
	
	def editInfluenceMembership_reset(self):
		'''
		Reset the coordinates of selected components in the member list of the current influence
		'''
		# Get surfaceSkin node
		surfaceSkinNode = mc.textScrollList('ssEditInfMemberSurfSkin_TSL',q=True,si=True)[0] # Get first selected item in list
		# Get influence
		influenceList = mc.textScrollList('ssEditInfMemberInf_TSL',q=True,si=True)
		# calculatePreBind
		calcPreBind = mc.menuItem('ssEditMemberCalcPreBind',q=True,checkBox=True)
		# Get selected components
		componentList = glTools.utils.component.getSingleIndexComponentList()
		# Iterate through each influence
		for influence in influenceList:
			# Iterate through each object
			for obj in componentList.keys():
				# Add components surface data
				self.surfaceSkinUtils.setSurfaceCoordArray(obj,componentList[obj],influence,surfaceSkinNode,0,calcPreBind,mode=0)
		# Update UI
		self.editInfluenceMembership_switchInfluence()
	
	def pruneNonMemberWeightsFromUI(self):
		'''
		Method called from Prune Non Member Weights UI
		Passes argument values from UI elements to the surfaceSkin.utils.removeInfluence() method
		'''
		# SurfaceSkin
		surfaceSkinNode = mc.optionMenuGrp('ssPruneWeightByMemberSurfaceSkin_OMG',q=1,v=1)
		
		# Affected Geometry List
		affectedGeoList = []
		if not mc.checkBoxGrp('ssPruneWeightByMemberAffected_CBG',q=1,v1=1):
			affectedGeoList = mc.textScrollList('ssPruneWeightByMemberAffected_TSL',q=1,si=1)
			if not len(affectedGeoList): return
		
		# Influence List
		influenceList = []
		if not mc.checkBoxGrp('ssPruneWeightByMemberInfluence_CBG',q=1,v1=1):
			influenceList = mc.textScrollList('ssPruneWeightByMemberInfluence_TSL',q=1,si=1)
			if not len(influenceList): return
		
		# Prune Weights
		self.surfaceSkinUtils.pruneWeightsByMembership(affectedGeoList,influenceList,surfaceSkinNode)
	
	def pruneMemberByWeightsFromUI(self):
		'''
		Method called from Prune Membership By Weights
		Passes argument values from UI elements to the surfaceSkin.utils.pruneMembershipByWeightsUI() method
		'''
		# SurfaceSkin
		surfaceSkinNode = mc.optionMenuGrp('ssPruneMemberByWeightSurfaceSkin_OMG',q=1,v=1)
		
		# Influence List
		influenceList = []
		if not mc.checkBoxGrp('ssPruneMemberByWeightInfluence_CBG',q=1,v1=1):
			influenceList = mc.textScrollList('ssPruneMemberByWeightInfluence_TSL',q=1,si=1)
			if not len(influenceList): return
		
		# Affected Geometry List
		affectedGeoList = []
		if not mc.checkBoxGrp('ssPruneMemberByWeightAffected_CBG',q=1,v1=1):
			affectedGeoList = mc.textScrollList('ssPruneMemberByWeightAffected_TSL',q=1,si=1)
			if not len(affectedGeoList): return
		
		# Threshold
		threshold = mc.floatSliderGrp('ssPruneMemberByWeightThreshold_FSG',q=1,v=1)
		
		# Prune Membership
		self.surfaceSkinUtils.pruneMembershipByWeights(affectedGeoList,influenceList,surfaceSkinNode,threshold)
	
	def toggleArtAttrCtx(self):
		'''
		Toggle the artAttrContext from paintInfluenceWeightsUI
		'''
		# Check current tool
		currentTool = mc.currentCtx()
		if currentTool == 'artAttrContext':
			mc.setToolTo('selectSuperContext')
			mc.button('ssPaintInfWeightsPaint_BTN',e=1,l='PAINT: ENABLE')
			return
		
		# Get surfaceSkin node
		surfaceSkinNode = mc.optionMenuGrp('ssPaintInfWeightsSurfaceSkin_OMG',q=1,v=1)
		
		# Set tool
		mc.setToolTo('artAttrContext')
		# Open Property Window
		#mc.toolPropertyWindow()
		
		# Set artAttrContext
		mm.eval('artSetToolAndSelectAttr "artAttrCtx" "surfaceSkin.'+surfaceSkinNode+'.paintWeight"')
		
		# Update UI button
		mc.button('ssPaintInfWeightsPaint_BTN',e=1,l='PAINT: DISABLE')
	
	def selectCoordFromUI(self):
		'''
		Select the target influence surface coordinate from the UI
		'''
		# Get selected surfaceSkin node
		surfaceSkin = mc.optionMenuGrp('ssCoordUtilsOMG',q=True,v=True)
		# Check surfaceSkin node
		if not self.surfaceSkinUtils.verifyNode(surfaceSkin):
			raise UIError('SurfaceSkin node "'+surfaceSkin+'" does not exist!')
		
		# Get selected influence
		influence = mc.textScrollList('ssCoordUtilsTSL',q=True,si=True)
		if not influence: raise UIError('No influence specified for operation!')
		else: influence = influence[0]
		
		# Get selected surface point
		surfacePoint = mc.filterExpand(sm=41)
		if not surfacePoint: raise UserInputError('No valid surface point selected!!')
		else: surfacePoint = surfacePoint[0]
		# Get surface and coordinate components
		surface = surfacePoint.split('.')[0]
		coord = surfacePoint.split('[')
		coord[0] = float(coord[1].replace(']',''))
		coord[1] = float(coord[2].replace(']',''))
		
		# Compare selection against influence list item
		if surface != influence:
			# Check surface affects surfaceSkin node
			if not self.surfaceSkinUtils.isInfluence(surface,surfaceSkin):
				raise UserInputError('Surface "'+surface+'" does not affect surfaceSkin node "'+surfaceSkin+'"!!')
			# Adjust influence list selection
			mc.textScrollList('ssCoordUtilsTSL',e=True,si=surface)
			print('WARNING: Surface point selected does not match the influence list selection!\nInfluence list selection adjusted!')
		
		# Set coordinate values
		mc.floatFieldGrp('ssCoordUtilsCoordFFG',e=True,v1=coord[0],v2=coord[1])
	
	def copyCoordFromUI(self):
		'''
		Copy the target coordinate for the selected component from the UI
		'''
		# Get selected surfaceSkin node
		surfaceSkin = mc.optionMenuGrp('ssCoordUtilsOMG',q=True,v=True)
		
		# Get selected influence
		try: influence = mc.textScrollList('ssCoordUtilsTSL',q=True,si=True)[0]
		except: raise UIError('No influence specified for operation!')
		
		# Get selected component and geometry
		componentSel = mc.filterExpand(sm=(31,28,46))[0] # First selected component
		
		# Get target coordinate
		coord = glTools.surfaceSkin.coordinateUtilities.getCoord(surfaceSkin,influence,componentSel)
		
		# Set coordinate values
		mc.floatFieldGrp('ssCoordUtilsCoordFFG',e=True,v1=coord[0],v2=coord[1])
	
	def averageCoordFromUI(self):
		'''
		Average the target coordinate for the selected component(s) from the UI
		'''
		# Get selected surfaceSkin node
		surfaceSkin = mc.optionMenuGrp('ssCoordUtilsOMG',q=True,v=True)
		
		# Get selected influence
		try: influence = mc.textScrollList('ssCoordUtilsTSL',q=True,si=True)[0]
		except: raise UIError('No influence specified for operation!')
		
		# Get selected components
		componentSelList = mc.filterExpand(sm=(31,28,46))
		
		# Get average target coordinate
		coord = glTools.surfaceSkin.coordinateUtilities.averageCoord(surfaceSkin,influence,componentSelList)
		
		# Set coordinate values
		mc.floatFieldGrp('ssCoordUtilsCoordFFG',e=True,v1=coord[0],v2=coord[1])
	
	def pasteCoordFromUI(self):
		'''
		Paste the current stored target coordinate to the selected component(s) from the UI
		'''
		# Get selected surfaceSkin node
		surfaceSkin = mc.optionMenuGrp('ssCoordUtilsOMG',q=True,v=True)
		
		# Get selected influence
		try: influence = mc.textScrollList('ssCoordUtilsTSL',q=True,si=True)[0]
		except: raise UIError('No influence specified for operation!')
		
		# Get selected components
		componentSelList = mc.filterExpand(sm=(31,28,46))
		
		# Get coordinate from UI
		coordU = mc.floatFieldGrp('ssCoordUtilsCoordFFG',q=True,v1=True)
		coordV = mc.floatFieldGrp('ssCoordUtilsCoordFFG',q=True,v2=True)
		
		# Apply the target coordinates to the selected components
		for component in componentSelList:
			try: glTools.surfaceSkin.coordinateUtilities.applyCoord(surfaceSkin,influence,component,[coordU,coordV])
			except: print('Unable to apply target coordinate for component "'+component+'"!')
	
	def neighbourAverageCoordFromUI(self):
		'''
		Perform neighbour target coordinate average from the UI
		'''
		# Get selected surfaceSkin node
		surfaceSkin = mc.optionMenuGrp('ssCoordUtilsOMG',q=True,v=True)
		
		# Get selected influence
		try: influence = mc.textScrollList('ssCoordUtilsTSL',q=True,si=True)[0]
		except: raise UIError('No influence specified for operation!')
		
		# Get user selection
		sel = mc.ls(sl=True)
		# Get selected components
		componentSelList = mc.filterExpand(sm=(31,28,46))
		
		# Get neighbour option
		neighbour = mc.radioButtonGrp('ssCoordUtilsNeighbourRBG',q=True,sl=True)
		
		# Iterate through selected components
		for component in componentSelList:
			nList = []
			# Horizontal
			if (neighbour == 1) or (neighbour == 3):
				nList.append(mc.pickWalk(component,d='left')[0])
				nList.append(mc.pickWalk(component,d='right')[0])
			# Vertical
			if (neighbour == 2) or (neighbour == 3):
				nList.append(mc.pickWalk(component,d='up')[0])
				nList.append(mc.pickWalk(component,d='down')[0])
			# Average coord
			coord = glTools.surfaceSkin.coordinateUtilities.averageCoord(surfaceSkin,influence,nList)
			# Apply coord
			glTools.surfaceSkin.coordinateUtilities.applyCoord(surfaceSkin,influence,component,coord)
		
		# Restore user selection
		mc.select(sel)