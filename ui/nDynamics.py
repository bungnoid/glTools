import maya.cmds as mc
import maya.mel as mm

import glTools.utils.attrPreset
import glTools.utils.base
import glTools.utils.mesh
import glTools.utils.nDynamics

import glTools.ui.utils

# =====================
# - Main UI functions -
# =====================

def create():
	'''
	'''
	# Window
	win = 'nDynamicsUI'
	if mc.window(win,ex=True): mc.deleteUI(win)
	win = mc.window(win,t='nDynamics',s=True,mb=True,wh=[650,390])
	
	# ---------------
	# - Main Window -
	# ---------------
	
	# Menu
	mc.menu(label='Edit',tearOff=1)
	mc.menuItem(label='Reset',c='glTools.ui.nDynamics.create()')
	
	# FormLayout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements 
	nucleusTXT = mc.text(l='Nucleus List:',al='left')
	nucleusTSL = mc.textScrollList('nDyn_nucleusTSL', allowMultiSelection=False )
	
	nucleus_createB = mc.button(label='Create', c='glTools.ui.nDynamics.createNucleusFromUI()' )
	nucleus_deleteB = mc.button(label='Delete', c='glTools.ui.nDynamics.deleteNucleusFromUI()' )
	nucleus_enableB = mc.button(label='Enable', c='glTools.ui.nDynamics.toggleNucleusFromUI(1)' )
	nucleus_disableB = mc.button(label='Disable', c='glTools.ui.nDynamics.toggleNucleusFromUI(0)' )
	
	nDyn_refreshB = mc.button(label='Refresh', c='glTools.ui.nDynamics.create()' )
	nDyn_closeB = mc.button(label='Close', c='mc.deleteUI("'+win+'")' )
	
	# TabLayout
	nDynTabLayout = mc.tabLayout('nDynTabLayout', innerMarginWidth=5, innerMarginHeight=5 )
	
	# Layout
	mc.formLayout(FL,e=True,af=[(nucleusTXT,'left',5),(nucleusTXT,'top',5)],ap=[(nucleusTXT,'right',5,35)])
	mc.formLayout(FL,e=True,af=[(nucleusTSL,'left',5)],ap=[(nucleusTSL,'right',5,35)],ac=[(nucleusTSL,'top',5,nucleusTXT),(nucleusTSL,'bottom',5,nucleus_createB)])
	
	mc.formLayout(FL,e=True,af=[(nucleus_createB,'left',5)],ap=[(nucleus_createB,'right',5,18)],ac=[(nucleus_createB,'bottom',5,nucleus_enableB)])
	mc.formLayout(FL,e=True,ac=[(nucleus_deleteB,'left',5,nucleus_createB),(nucleus_deleteB,'right',5,nDynTabLayout),(nucleus_deleteB,'bottom',5,nucleus_disableB)])
	
	mc.formLayout(FL,e=True,af=[(nucleus_enableB,'left',5)],ap=[(nucleus_enableB,'right',5,18)],ac=[(nucleus_enableB,'bottom',5,nDyn_refreshB)])
	mc.formLayout(FL,e=True,ac=[(nucleus_disableB,'left',5,nucleus_enableB),(nucleus_disableB,'right',5,nDynTabLayout),(nucleus_disableB,'bottom',5,nDyn_refreshB)])
	
	mc.formLayout(FL,e=True,af=[(nDyn_refreshB,'left',5),(nDyn_refreshB,'bottom',5)],ap=[(nDyn_refreshB,'right',5,50)])
	mc.formLayout(FL,e=True,af=[(nDyn_closeB,'right',5),(nDyn_closeB,'bottom',5)],ap=[(nDyn_closeB,'left',5,50)])
	
	mc.formLayout(FL,e=True,af=[(nDynTabLayout,'top',5),(nDynTabLayout,'right',5)],ac=[(nDynTabLayout,'left',5,nucleusTSL),(nDynTabLayout,'bottom',5,nDyn_closeB)])
	
	# UI Callbacks
	
	mc.textScrollList(nucleusTSL,e=True,sc='glTools.ui.nDynamics.setCurrentNucleus()')
	mc.textScrollList(nucleusTSL,e=True,dcc='glTools.ui.utils.selectFromTSL("'+nucleusTSL+'")')
	mc.textScrollList(nucleusTSL,e=True,dkc='glTools.ui.nDynamics.deleteNucleusFromUI()')
	
	# Popup menu
	nClothPUM = mc.popupMenu(parent=nucleusTSL)
	mc.menuItem(l='Select Hilited Nodes',c='glTools.ui.utils.selectFromTSL("'+nucleusTSL+'")')
	mc.menuItem(l='Select Connected nCloth',c='glTools.ui.nDynamics.selectConnectedMeshFromUI("'+nucleusTSL+'")')
	mc.menuItem(l='Select Connected nRigid',c='glTools.ui.nDynamics.selectConnectedSolverFromUI("'+nucleusTSL+'")')
	# Attr Presets
	nucleusPresetList = glTools.utils.attrPreset.listNodePreset('nucleus')
	if nucleusPresetList:
		mc.menuItem(allowOptionBoxes=False, label='Apply Preset',subMenu=True,tearOff=False)
		for nucleusPreset in nucleusPresetList:
			mc.menuItem(l=nucleusPreset,c='glTools.ui.nDynamics.applyPreset("'+nucleusTSL+'","'+nucleusPreset+'")')
	
	# -----------------
	# - nCloth Layout -
	# -----------------
	
	mc.setParent(nDynTabLayout)
	
	# FormLayout
	nClothFL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements 
	nClothVisRB = mc.radioButtonGrp( 'nClothVisRB', cw=[(1,60),(2,60),(3,80)], label='Display:', labelArray2=['All','Current'], numberOfRadioButtons=2, sl=1, cc='glTools.ui.nDynamics.toggleNClothVis()' )

	nClothTSL = mc.textScrollList('nDyn_nClothTSL', allowMultiSelection=True )
	nCloth_createB = mc.button( label = 'Create from Mesh', c='glTools.ui.nDynamics.createNClothFromUI()' )
	nCloth_deleteB = mc.button( label = 'Delete Selected', c='glTools.ui.nDynamics.deleteNClothFromUI()' )
	nCloth_addToNucleusB = mc.button( label = 'Assign to Nucleus', c='glTools.ui.nDynamics.addNClothToNucleusFromUI()' )
	nCloth_enableB = mc.button( label = 'Enable', c='glTools.ui.nDynamics.toggleNClothStateFromUI(1)' )
	nCloth_disableB = mc.button( label = 'Disable', c='glTools.ui.nDynamics.toggleNClothStateFromUI(0)' )
	nCloth_saveCacheB = mc.button( label = 'Save Cache', c='glTools.ui.nDynamics.saveNClothCacheFromUI()' )
	nCloth_loadCacheB = mc.button( label = 'Load Cache', c='glTools.ui.nDynamics.loadNClothCacheFromUI()' )
	
	# Layout
	mc.formLayout(nClothFL,e=True,af=[(nClothVisRB,'top',5),(nClothVisRB,'left',5),(nClothVisRB,'right',5)])
	mc.formLayout(nClothFL,e=True,af=[(nClothTSL,'left',5),(nClothTSL,'bottom',5)],ap=[(nClothTSL,'right',5,55)],ac=[(nClothTSL,'top',5,nClothVisRB)])
	
	mc.formLayout(nClothFL,e=True,af=[(nCloth_createB,'right',5)],ac=[(nCloth_createB,'left',5,nClothTSL),(nCloth_createB,'top',5,nClothVisRB)])
	mc.formLayout(nClothFL,e=True,af=[(nCloth_deleteB,'right',5)],ac=[(nCloth_deleteB,'left',5,nClothTSL),(nCloth_deleteB,'top',5,nCloth_createB)])
	mc.formLayout(nClothFL,e=True,af=[(nCloth_addToNucleusB,'right',5)],ac=[(nCloth_addToNucleusB,'left',5,nClothTSL),(nCloth_addToNucleusB,'top',5,nCloth_deleteB)])
	
	mc.formLayout(nClothFL,e=True,af=[(nCloth_enableB,'right',5)],ac=[(nCloth_enableB,'left',5,nClothTSL),(nCloth_enableB,'top',5,nCloth_addToNucleusB)])
	mc.formLayout(nClothFL,e=True,af=[(nCloth_disableB,'right',5)],ac=[(nCloth_disableB,'left',5,nClothTSL),(nCloth_disableB,'top',5,nCloth_enableB)])
	
	mc.formLayout(nClothFL,e=True,af=[(nCloth_saveCacheB,'right',5)],ac=[(nCloth_saveCacheB,'left',5,nClothTSL),(nCloth_saveCacheB,'top',5,nCloth_disableB)])
	mc.formLayout(nClothFL,e=True,af=[(nCloth_loadCacheB,'right',5)],ac=[(nCloth_loadCacheB,'left',5,nClothTSL),(nCloth_loadCacheB,'top',5,nCloth_saveCacheB)])
	
	# UI Callbacks
	mc.textScrollList(nClothTSL,e=True,dcc='glTools.ui.utils.selectFromTSL("'+nClothTSL+'")')
	mc.textScrollList(nClothTSL,e=True,dkc='glTools.ui.nDynamics.deleteNClothFromUI()')
	mc.radioButtonGrp(nClothVisRB,e=True,cc='glTools.ui.nDynamics.refreshNodeList("'+nClothTSL+'","nCloth","'+nClothVisRB+'")')
	
	mc.setParent('..')
	
	# Popup menu
	nClothPUM = mc.popupMenu(parent=nClothTSL)
	mc.menuItem(l='Select Hilited Nodes',c='glTools.ui.utils.selectFromTSL("'+nClothTSL+'")')
	mc.menuItem(l='Select Connected Mesh',c='glTools.ui.nDynamics.selectConnectedMesh("'+nClothTSL+'")')
	mc.menuItem(l='Select Connected Solver',c='glTools.ui.nDynamics.selectConnectedSolver("'+nClothTSL+'")')
	# Attr Presets
	nClothPresetList = glTools.utils.attrPreset.listNodePreset('nCloth')
	if nClothPresetList:
		mc.menuItem(allowOptionBoxes=False, label='Apply Preset',subMenu=True,tearOff=False)
		for nClothPreset in nClothPresetList:
			mc.menuItem(l=nClothPreset,c='glTools.ui.nDynamics.applyPreset("'+nClothTSL+'","'+nClothPreset+'")')
	
	# -----------------
	# - nRigid Layout -
	# -----------------
	
	mc.setParent(nDynTabLayout)
	
	# FormLayout
	nRigidFL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements 
	nRigidVisRB = mc.radioButtonGrp( 'nRigidVisRB', cw=[(1,60),(2,60),(3,80)], label='Display:', labelArray2=['All','Current'], numberOfRadioButtons=2, sl=1, cc='glTools.ui.nDynamics.toggleNClothVis()' )

	nRigidTSL = mc.textScrollList('nDyn_nRigidTSL', allowMultiSelection=True )
	nRigid_createB = mc.button( label = 'Create from Mesh', c='glTools.ui.nDynamics.createNRigidFromUI()' )
	nRigid_deleteB = mc.button( label = 'Delete Selected', c='glTools.ui.nDynamics.deleteNRigidFromUI()' )
	nRigid_addToNucleusB = mc.button( label = 'Add to Nucleus', c='glTools.ui.nDynamics.addNRigidToNucleusFromUI()' )
	
	nRigid_enableB = mc.button( label = 'Enable', c='glTools.ui.nDynamics.toggleNRigidStateFromUI(1)' )
	nRigid_disableB = mc.button( label = 'Disable', c='glTools.ui.nDynamics.toggleNRigidStateFromUI(0)' )
	
	# Layout
	mc.formLayout(nRigidFL,e=True,af=[(nRigidVisRB,'top',5),(nRigidVisRB,'left',5),(nRigidVisRB,'right',5)])
	mc.formLayout(nRigidFL,e=True,af=[(nRigidTSL,'left',5),(nRigidTSL,'bottom',5)],ap=[(nRigidTSL,'right',5,55)],ac=[(nRigidTSL,'top',5,nRigidVisRB)])
	
	mc.formLayout(nRigidFL,e=True,af=[(nRigid_createB,'right',5)],ac=[(nRigid_createB,'left',5,nRigidTSL),(nRigid_createB,'top',5,nRigidVisRB)])
	mc.formLayout(nRigidFL,e=True,af=[(nRigid_deleteB,'right',5)],ac=[(nRigid_deleteB,'left',5,nRigidTSL),(nRigid_deleteB,'top',5,nRigid_createB)])
	mc.formLayout(nRigidFL,e=True,af=[(nRigid_addToNucleusB,'right',5)],ac=[(nRigid_addToNucleusB,'left',5,nRigidTSL),(nRigid_addToNucleusB,'top',5,nRigid_deleteB)])
	
	mc.formLayout(nRigidFL,e=True,af=[(nRigid_enableB,'right',5)],ac=[(nRigid_enableB,'left',5,nRigidTSL),(nRigid_enableB,'top',5,nRigid_addToNucleusB)])
	mc.formLayout(nRigidFL,e=True,af=[(nRigid_disableB,'right',5)],ac=[(nRigid_disableB,'left',5,nRigidTSL),(nRigid_disableB,'top',5,nRigid_enableB)])
	
	# UI Callbacks
	mc.textScrollList(nRigidTSL,e=True,dcc='glTools.ui.utils.selectFromTSL("'+nRigidTSL+'")')
	mc.textScrollList(nRigidTSL,e=True,dkc='glTools.ui.nDynamics.deleteNRigidFromUI()')
	mc.radioButtonGrp(nRigidVisRB,e=True,cc='glTools.ui.nDynamics.refreshNodeList("'+nRigidTSL+'","nRigid","'+nRigidVisRB+'")')
	
	mc.setParent('..')
	
	# Popup menu
	nRigidPUM = mc.popupMenu(parent=nRigidTSL)
	mc.menuItem(l='Select Hilited Nodes',c='glTools.ui.utils.selectFromTSL("'+nRigidTSL+'")')
	mc.menuItem(l='Select Connected Mesh',c='glTools.ui.nDynamics.selectConnectedMesh("'+nRigidTSL+'")')
	mc.menuItem(l='Select Connected Solver',c='glTools.ui.nDynamics.selectConnectedSolver("'+nRigidTSL+'")')
	# Attr Presets
	nRigidPresetList = glTools.utils.attrPreset.listNodePreset('nRigid')
	if nRigidPresetList:
		mc.menuItem(allowOptionBoxes=False, label='Apply Preset',subMenu=True,tearOff=False)
		for nRigidPreset in nRigidPresetList:
			mc.menuItem(l=nRigidPreset,c='glTools.ui.nDynamics.applyPreset("'+nRigidTSL+'","'+nRigidPreset+'")')
	
	# --------------------
	# - nParticle Layout -
	# --------------------
	
	mc.setParent(nDynTabLayout)
	
	# FormLayout
	nParticleFL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements 
	nParticleVisRB = mc.radioButtonGrp( 'nParticleVisRB', cw=[(1,60),(2,60),(3,80)], label='Display:', labelArray2=['All','Current'], numberOfRadioButtons=2, sl=1, cc='glTools.ui.nDynamics.toggleNClothVis()' )

	nParticleTSL = mc.textScrollList('nDyn_nParticleTSL', allowMultiSelection=True )
	nParticle_createB = mc.button( label = 'Fill Mesh', c='glTools.ui.nDynamics.createNParticleFromUI()' )
	nParticle_deleteB = mc.button( label = 'Delete Selected', c='glTools.ui.nDynamics.deleteNParticleFromUI()' )
	nParticle_addToNucleusB = mc.button( label = 'Add to Nucleus', c='glTools.ui.nDynamics.addNParticleToNucleusFromUI()' )
	
	# Layout
	mc.formLayout(nParticleFL,e=True,af=[(nParticleVisRB,'top',5),(nParticleVisRB,'left',5),(nParticleVisRB,'right',5)])
	mc.formLayout(nParticleFL,e=True,af=[(nParticleTSL,'left',5),(nParticleTSL,'bottom',5)],ap=[(nParticleTSL,'right',5,55)],ac=[(nParticleTSL,'top',5,nParticleVisRB)])
	
	mc.formLayout(nParticleFL,e=True,af=[(nParticle_createB,'right',5)],ac=[(nParticle_createB,'left',5,nParticleTSL),(nParticle_createB,'top',5,nParticleVisRB)])
	mc.formLayout(nParticleFL,e=True,af=[(nParticle_deleteB,'right',5)],ac=[(nParticle_deleteB,'left',5,nParticleTSL),(nParticle_deleteB,'top',5,nParticle_createB)])
	mc.formLayout(nParticleFL,e=True,af=[(nParticle_addToNucleusB,'right',5)],ac=[(nParticle_addToNucleusB,'left',5,nParticleTSL),(nParticle_addToNucleusB,'top',5,nParticle_deleteB)])
	
	# UI Callbacks
	mc.textScrollList(nParticleTSL,e=True,dcc='glTools.ui.utils.selectFromTSL("'+nParticleTSL+'")')
	mc.textScrollList(nParticleTSL,e=True,dkc='glTools.ui.nDynamics.deleteNParticleFromUI()')
	mc.radioButtonGrp(nParticleVisRB,e=True,cc='glTools.ui.nDynamics.refreshNodeList("'+nParticleTSL+'","nParticle","'+nParticleVisRB+'")')
	
	mc.setParent('..')
	
	# Popup menu
	nParticlePUM = mc.popupMenu(parent=nParticleTSL)
	mc.menuItem(l='Select Hilited Nodes',c='glTools.ui.utils.selectFromTSL("'+nParticleTSL+'")')
	mc.menuItem(l='Select Connected Mesh',c='glTools.ui.nDynamics.selectConnectedMesh("'+nParticleTSL+'")')
	mc.menuItem(l='Select Connected Solver',c='glTools.ui.nDynamics.selectConnectedSolver("'+nParticleTSL+'")')
	# Attr Presets
	nParticlePresetList = glTools.utils.attrPreset.listNodePreset('nParticleTSL')
	if nParticlePresetList:
		mc.menuItem(allowOptionBoxes=False, label='Apply Preset',subMenu=True,tearOff=False)
		for nParticlePreset in nParticlePresetList:
			mc.menuItem(l=nParticlePreset,c='glTools.ui.nDynamics.applyPreset("'+nParticleTSL+'","'+nParticlePreset+'")')
	
	# -----------------
	# - nCache Layout -
	# -----------------
	
	mc.setParent(nDynTabLayout)
	
	# FormLayout
	nCacheFL = mc.formLayout(numberOfDivisions=100)
	
	mc.setParent('..')
	
	# --------------
	# - End Layout -
	# --------------
	
	# Set TabLayout Labels
	mc.tabLayout( nDynTabLayout,e=True,tabLabel=((nClothFL,'nCloth'),(nRigidFL,'nRigid'),(nParticleFL,'nParticle'),(nCacheFL,'nCache')) )
	
	# Display UI 
	mc.showWindow(win)
	refreshUI()

def checkUI():
	'''
	'''
	# Check UI
	win = 'nDynamicsUI'
	if not mc.window(win,ex=True):
		raise Exception('nDynamics window does not exist!')

def refreshUI():
	'''
	'''
	# Check UI
	checkUI()
	
	# Resize UI - force refresh elements
	win = 'nDynamicsUI'
	[w,h] = mc.window(win,q=True,wh=True)
	mc.window(win,e=True,wh=[w+1,h+1])
	mc.window(win,e=True,wh=[w,h])
	
	# Refresh UI Elements
	refreshNodeList('nDyn_nucleusTSL','nucleus')
	refreshNodeList('nDyn_nClothTSL','nCloth','nClothVisRB')
	refreshNodeList('nDyn_nRigidTSL','nRigid','nRigidVisRB')
	refreshNodeList('nDyn_nParticleTSL','nParticle','nParticleVisRB')
	
def refreshNodeList(TSL,nodeType,RB=''):
	'''
	Refresh the nucleus node textScrollList
	@param TSL: textScrollList to refresh
	@type TSL: str
	@param nodeType: Object type to populate the textScrollList
	@type nodeType: str
	'''
	# Check UI
	checkUI()
	
	# Check visibility mode
	# - Value is 1 based, subtract 1 to get 0 or 1 value
	visMode = 0
	if RB: visMode = mc.radioButtonGrp(RB,q=True,sl=True) - 1
	
	# Get current nucleus
	nucleus = mc.textScrollList('nDyn_nucleusTSL',q=True,si=True)
	
	# Clear textScrollList
	mc.textScrollList(TSL,e=True,ra=True)
	
	# Check visibility
	if visMode and nucleus:
		# Get connected nDynamics nodes
		nNodeList = glTools.utils.nDynamics.getConnectedNNode(nucleus[0],nodeType)
	else:
		# Get all existing nDynamics nodes
		nNodeList = mc.ls(type=nodeType)
	
	# Sort list
	nNodeList.sort()
	
	# Refresh List
	for node in nNodeList: mc.textScrollList(TSL,e=True,a=node)
	
	# Update current nucleus
	if nodeType == 'nucleus':
		nucleus = glTools.utils.nDynamics.getActiveNucleus()
		if nucleus: mc.textScrollList('nDyn_nucleusTSL',e=True,si=nucleus)

# ==================
# - Misc Functions -
# ==================

def setCurrentNucleus():
	'''
	'''
	# Get selected nucleus
	nucleus = mc.textScrollList('nDyn_nucleusTSL',q=True,si=True)
	if not nucleus: nucleus = glTools.utils.nDynamics.getActiveNucleus()
	else: nucleus = nucleus[0]
	
	# Set active nucleus
	glTools.utils.nDynamics.setActiveNucleus(nucleus)
	
	# Refresh UI Elements
	refreshNodeList('nDyn_nClothTSL','nCloth','nClothVisRB')
	refreshNodeList('nDyn_nRigidTSL','nRigid','nRigidVisRB')
	refreshNodeList('nDyn_nParticleTSL','nParticle','nParticleVisRB')

def applyPreset(TSL,preset):
	'''
	Apply an attribute preset to a list of selected nodes from the specified textScrollList
	@param TSL: textScrollList to get list of node to apply preset to
	@type TSL: str
	@param preset: Object type to populate the textScrollList
	@type preset: str
	'''
	# Get node list
	nodeList = mc.textScrollList(TSL,q=True,si=True)
	
	# Apply Preset
	glTools.utils.attrPreset.apply(nodeList,preset,1.0)

def selectConnectedSolver(TSL):
	'''
	Select the nucleus nodes connected to the nDynamics hilited in the given textScrolList.
	@param TSL: textScrollList to get list of node to find conencted nucleus nodes for
	@type TSL: str
	'''
	# Get node list
	nodeList = mc.textScrollList(TSL,q=True,si=True)
	
	# Get list of connected nucleus
	nucleusList = []
	for node in nodeList:
		nucleus = glTools.utils.nDynamics.getConnectedNucleus(node)
		if nucleus: nucleusList.append(nucleus)
	
	# Select connected nucleus
	mc.select(nucleusList)
	
	# Hilite items in nucleus textScrollList
	nucleusItemList = mc.textScrollList('nDyn_nucleusTSL',q=True,ai=True)
	nucleusList = [n for n in nucleusList if nucleusItemList.count(n)]
	mc.textScrollList('nDyn_nucleusTSL',e=True,da=True)
	mc.textScrollList('nDyn_nucleusTSL',e=True,si=nucleusList)
	
	# Return result
	return nucleusList

def selectConnectedMesh(TSL):
	'''
	Select the meshes connected to the nDynamics hilited in the given textScrolList.
	@param TSL: textScrollList to get list of node to find conencted meshes for
	@type TSL: str
	'''
	# Get node list
	nodeList = mc.textScrollList(TSL,q=True,si=True)
	
	# Get list of connected meshes
	meshList = []
	for node in nodeList:
		mesh = glTools.utils.nDynamics.getConnectedMesh(node,returnShape=False)
		if mesh: meshList.append(mesh)
	
	# Select connected meshes
	mc.select(meshList)
	
	# Return result
	return meshList

# ====================
# - nucleus functions -
# ====================

def createNucleusFromUI():
	'''
	'''
	# Check UI
	checkUI()
	
	# Create nucleus
	nucleus = glTools.utils.nDynamics.createNucleus('')
	
	# Set as current
	refreshNodeList('nDyn_nucleusTSL','nucleus')

def deleteNucleusFromUI():
	'''
	'''
	# Check UI
	checkUI()
	tsl = 'nDyn_nucleusTSL'
	
	# Get selected nucleus
	nodeSel = mc.textScrollList(tsl,q=True,si=True)
	if not nodeSel: return
	
	# Check current nucleus
	for node in nodeSel:
		if not mc.objExists(node):
			raise Exception('Nucleus node "'+node+'" does not exist!')
	
	# Select nucleus
	mc.delete(nodeSel)
	
	# Refresh Nucleus List
	refreshNodeList(tsl,'nucleus')

def toggleNucleusFromUI(state):
	'''
	'''
	# Check UI
	checkUI()
	nucleus_tsl = 'nDyn_nucleusTSL'
	
	# Get selected nucleus
	nucleusSel = mc.textScrollList(nucleus_tsl,q=True,si=True)
	if not nucleusSel:
		raise Exception('No valid nucleus node selected!')
	
	# Enable/Disable nucleus nodes
	for nucleus in nucleusSel:
		mc.setAttr(nucleus+'.enable',state)
		
# ====================
# - nCloth functions -
# ====================
	
def createNClothFromUI():
	'''
	'''
	# Check UI
	checkUI()
	nucleus_tsl = 'nDyn_nucleusTSL'
	nCloth_tsl = 'nDyn_nClothTSL'
	
	# Get selected mesh
	objSel = mc.ls(sl=1)
	if not objSel:
		raise Exception('Nothing selected!')
	meshList = [obj for obj in objSel if glTools.utils.mesh.isMesh(obj)]
	if not meshList:
		raise Exception('No valid mesh in selection!')
	
	# Get selected nucleus
	nucleusSel = mc.textScrollList(nucleus_tsl,q=True,si=True)
	if not nucleusSel:
		raise Exception('No valid nucleus node selected!')
	nucleus = nucleusSel[0]
	
	# Create nCloth
	# !!!!!!!!!!!! Always in Local Space until option is added!!!!!!!!!!!
	for mesh in meshList:
		glTools.utils.nDynamics.createNCloth(mesh,nucleus,worldSpace=False,prefix='')
	
	# Refresh UI
	refreshNodeList(nCloth_tsl,'nCloth')
	refreshNodeList(nucleus_tsl,'nucleus')

def deleteNClothFromUI():
	'''
	'''
	# Check UI
	checkUI()
	tsl = 'nDyn_nClothTSL'
	
	# Get nCloth selection
	nClothSel = mc.textScrollList(tsl,q=True,si=True)
	if not nClothSel:
		raise Exception('No nCloth specified!')
	
	# Delete nCloth
	for nCloth in nClothSel:
		glTools.utils.nDynamics.deleteNCloth(nCloth)
	
	# Refresh UI
	refreshNodeList(tsl,'nCloth')
	
def addNClothToNucleusFromUI():
	'''
	'''
	# Check UI
	checkUI()
	nucleus_tsl = 'nDyn_nucleusTSL'
	nCloth_tsl = 'nDyn_nClothTSL'
	
	# Get selected nucleus
	nucleusSel = mc.textScrollList(nucleus_tsl,q=True,si=True)
	if not nucleusSel:
		raise Exception('No valid nucleus node selected!')
	nucleus = nucleusSel[0]
	
	# Get selected nCloth
	nClothSel = mc.textScrollList(nCloth_tsl,q=True,si=True)
	if not nClothSel:
		raise Exception('No nCloth specified!')
	
	# Connect to nucleus
	for nCloth in nClothSel:
		#glTools.utils.nDynamics.connect_nClothToNucleus(nCloth,nucleus)
		glTools.utils.nDynamics.connectToNucleus(nCloth,nucleus)

def toggleNClothStateFromUI(state):
	'''
	'''
	# Check UI
	checkUI()
	tsl = 'nDyn_nClothTSL'
	
	# Get selected nucleus
	nClothSel = mc.textScrollList(tsl,q=True,si=True)
	if not nClothSel: raise Exception('No valid nCloth node selected!')
	
	# Enable/Disable nCloth nodes
	for nCloth in nClothSel: mc.setAttr(nCloth+'.isDynamic',state)

def saveNClothCacheFromUI():
	'''
	'''
	# Check UI
	checkUI()

def loadNClothCacheFromUI():
	'''
	'''
	# Check UI
	checkUI()

def toggleNClothVis():
	'''
	'''
	# Check UI
	checkUI()

# ====================
# - nRigid functions -
# ====================

def createNRigidFromUI():
	'''
	'''
	# Check UI
	checkUI()
	nucleus_tsl = 'nDyn_nucleusTSL'
	nRigid_tsl = 'nDyn_nRigidTSL'
	
	# Get selected mesh
	objSel = mc.ls(sl=1)
	if not objSel:
		raise Exception('Nothing selected!')
	meshList = [obj for obj in objSel if glTools.utils.mesh.isMesh(obj)]
	if not meshList:
		raise Exception('No valid mesh in selection!')
	
	# Get selected nucleus
	nucleusSel = mc.textScrollList(nucleus_tsl,q=True,si=True)
	if not nucleusSel:
		raise Exception('No valid nucleus node selected!')
	nucleus = nucleusSel[0]
	
	# Create nRigid
	for mesh in meshList:
		glTools.utils.nDynamics.createNRigid(mesh,nucleus)
	
	# Refresh UI
	refreshNodeList(nRigid_tsl,'nRigid')
	refreshNodeList(nucleus_tsl,'nucleus')
	
def deleteNRigidFromUI():
	'''
	'''
	# Check UI
	checkUI()
	nucleus_tsl = 'nDyn_nucleusTSL'
	nRigid_tsl = 'nDyn_nRigidTSL'
	
	# Get selected nRigid nodes
	nRigidSel = mc.textScrollList(nRigid_tsl,q=True,si=True)
	
	# Delete nRigid nodes
	for nRigid in nRigidSel:
		glTools.utils.nDynamics.deleteNCloth(nRigid)
	
	# Refresh UI
	refreshNodeList(nRigid_tsl,'nRigid')
	
def addNRigidToNucleusFromUI():
	'''
	'''
	# Check UI
	checkUI()
	nucleus_tsl = 'nDyn_nucleusTSL'
	nRigid_tsl = 'nDyn_nRigidTSL'
	
	# Get selected nucleus
	nucleusSel = mc.textScrollList(nucleus_tsl,q=True,si=True)
	if not nucleusSel:
		raise Exception('No valid nucleus node selected!')
	nucleus = nucleusSel[0]
	
	# Get selected nRigid
	nRigidSel = mc.textScrollList(nRigid_tsl,q=True,si=True)
	if not nRigidSel:
		raise Exception('No nCloth specified!')
	
	# Connect to nucleus
	for nRigid in nRigidSel:
		#glTools.utils.nDynamics.connect_nRigidToNucleus(nRigid,nucleus)
		glTools.utils.nDynamics.connectToNucleus(nRigid,nucleus)
	
def toggleNRigidStateFromUI(state):
	'''
	'''
	# Check UI
	checkUI()
	tsl = 'nDyn_nRigidTSL'
	
	# Get selected nucleus
	nRigidSel = mc.textScrollList(tsl,q=True,si=True)
	if not nRigidSel: raise Exception('No valid nCloth node selected!')
	
	# Enable/Disable nCloth nodes
	for nRigid in nRigidSel: mc.setAttr(nRigid+'.isDynamic',state)

# =======================
# - nParticle functions -
# =======================



# ====================
# - nCache functions -
# ====================


