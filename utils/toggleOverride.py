#################################################################################################################
##<OPEN>
##<KEEP_FORMAT>
##<FILE NAME>
##			toggleOverride.mel
##</FILE NAME>
##
##<VERSION HISTORY>
##			05/15/07 : Ramiro Gomez : added header
##			04/24/08 : Ramiro Gomez : initial conversion to Python
##</VERSION HISTORY>
##
##<DESCRIPTION>
##			Toggles override display state of selected element surfaces
##</DESCRIPTION>
##
##<USAGE>
##			Open existing asset scene, select a control on your
##			asset(example - supermover)
##			Launch toggleOverride_GUI from the rigTools menu, select
##			the options you want and execute.
##</USAGE>
##
##<DOCUMENTATION>
##			<+> https://wiki.laika.com/bin/view/Main/Entertainment/Jack_Ben/JnbRiggingProceduresToggleOverrideUI
##</DOCUMENTATION>
##
##<NOTES>
##			the rigTools maya menu contains the toggleOverride_GUI
##</NOTES>
##
##
##<DEPARTMENTS>
##                      <+> rig
##			<+> cfin
##</DEPARTMENTS>
##
##<KEYWORDS>
##			<+> rig
##			<+> cfin
##			<+> utility
##			<+> gui
##			<+> interface
##			<+> window
##</KEYWORDS>
##
##<APP>
##			Maya
##</APP>
##
##<APP VERSION>
##			7.0.1, 8.5
##</APP VERSION>
##
##<CLOSE>
#################################################################################################################

import maya.cmds as mc

class UserInputError(Exception): pass

#################################################################################################################

def ui():
	
	'''
	Toggles override display state of selected element surfaces
	Open existing asset scene, select a control on your asset(example - supermover)
	Launch toggleOverride_GUI from the rigTools menu, select the options you want and execute.
	
	@keyword: rig, cfin, utilities, gui, interface, window
    
    @appVersion: 8.5, 2008
	'''
	
	if mc.window('toggleUIwin', q=1, ex=1):
		mc.deleteUI('toggleUIwin')

	uiWidth = 500
	uiHeight = 200

	# VERY IMPORTANT TO TURN OFF "REMEMBER SIZE AND POSITION" IN PREFERENCES

	# define the interface

	toggleUI = mc.window('toggleUIwin', title='toggleOverride_GUI - v.5', iconName='toggleOverride_GUI', w=uiWidth, h=uiHeight, resizeToFitChildren=False)

	mc.frameLayout(marginHeight=30, labelVisible=0, borderStyle='out')
		
	genForm = mc.formLayout(numberOfDivisions=100)
				
	genColumn =mc.columnLayout(adjustableColumn=True, rowSpacing=5)

	mc.rowLayout(nc=4, cat=[(1, 'right', 5), (2, 'both', 5), (3, 'right', 5), (4, 'both', 5)], cw=[(1,100),(2,110),(3,100),(4,100)])

	mc.text(label ='Toggle To', annotation='select PolyCage toggle type.')

	mc.optionMenu('polyToggleTypeDropdown', label='')

	## should read these values to find the current state
	mc.menuItem(label='Normal')
	mc.menuItem(label='Template')
	mc.menuItem(label='Reference')

	# back up to Column Layout
	mc.setParent('..')

	mc.rowLayout(nc=2, cat=[(1, 'right', 116)], cw=[(1,305),(2,305)])

	radioPolyEnableOverrides = mc.checkBox('polyEnable', v=True, label='overrides', h=30)

	# back up to Column Layout
	mc.setParent('..') 

	mc.rowLayout(nc=2, cat=[(1, 'right', 128)],cw=[(1,305),(2,305)])

	radioPolyEnableShadingOverrides = mc.checkBox('polyEnableShading', v=True, label='shading', h=30)

	# back up to Column Layout
	mc.setParent('..') 

	mc.rowLayout(nc=2, cat=[(1, 'right', 116), (2, 'right', 290)], cw=[(1,305),(2,305)])

	ok = mc.button(w=85, h=30, backgroundColor=(0, 1, 0), al='center', command='glTools.utils.toggleOverride.toggleOverride_WRP()', label='OK')

	cancel = mc.button(w=85, h=30, backgroundColor=(1, 0, 0), al='center', command='mc.deleteUI("'+toggleUI+'")', label='Cancel')
	
	# tell Maya to draw the window
	mc.showWindow('toggleUIwin')

#################################################################################################################

def toggleOverride_WRP():
	'''
	Wrapper to execute toggleOverride with inputs from
	toggleOverride_GUI
	
	@keyword: rig, cfin, utilities, gui, interface, window
    
    @appVersion: 8.5, 2008
	
	'''
	
	sel=mc.ls(sl=True)
   
	mEnableOverrides = mc.checkBox('polyEnable', q=True, v=True)
	mDisplayMode = mc.optionMenu('polyToggleTypeDropdown', q=True, select=True)
	mEnableShading = mc.checkBox('polyEnableShading', q=True, v=True)
   
	if not len(sel):
		raise UserInputError('error You must select a control in order to toggle display override on!')
		
	toggleOverride(sel[0], 'model', mEnableOverrides, (mDisplayMode - 1), mEnableShading)
	
#################################################################################################################

def toggleOverride(assetNode, geoGroup, enableOverrides, displayMode, enableShading):
	
	'''
	executable for toggleOverride. The executable needs to be given a node
	from the asset in your scene to perform the operation on
	available modes are as follows: 
		Normal(0) - geometry is selectable 
		Template(1) - geometry is in template mode 
		Reference(2) - geometry is in reference mode 
	
	@param assetNode: Node on the asset on which to toggleOverrides
	@type assetNode: str
	@param geoGroup: Node which contains all meshes for asset
	@type geoGroup: str
	@param enableOverrides: 1 or 0 to enable the overrides. Default is on
	@type enableOverrides: int
	@param displayNode: 0, 1, or 2 to define modes
	@type displayNode: int
	@param enableShading: 1 or 0 to enable the shading. Default is on.
	@type: displayNode: int
	
	@keyword: rig, cfin, utilities, gui, interface, window
	
	@example: toggleOverride jack:cn_hed01_ccc model 1 2 1;
    
    @appVersion: 8.5, 2008
	'''
	
	##find all the geo in that group
	if not mc.objExists(assetNode): raise UserInputError('')
	if assetNode.count(':'):
		geoGroup = assetNode.split(':')[0] + ':' + geoGroup
	
	if not mc.objExists(geoGroup): raise UserInputError('')
	geo = mc.listRelatives(geoGroup, ad=1, ni=1, typ=['mesh','nurbsSurface'])
	
	##cycle through that geo and set its state based on the mode, overrides, and shading
	for shape in geo:
		mc.setAttr(shape + ".overrideEnabled",enableOverrides)
		if(enableOverrides):
			mc.setAttr(shape + ".overrideShading",enableShading)
			mc.setAttr(shape + ".overrideDisplayType",displayMode)
	
	##finished
	print 'Done toggling overrides'
