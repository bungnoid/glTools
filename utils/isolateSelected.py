import maya.cmds as mc

def getPanel():
	'''
	Get current model panel with focus
	'''
	# Get Panel with Focus
	panel = mc.getPanel(wf=True)
	
	# Check Model Panel
	if not mc.modelPanel(panel,q=True,ex=True):
		panel = mc.getPanel(type='modelPanel')[0]
	
	# Return Result
	return panel

def isolate(state,sel=None,panel=None):
	'''
	Isolated selected objects in the specified model panel
	@param state: Rig namespace to bake mocap override keys for.
	@type state: bool
	@param sel: List of objects to isolate in the viewport. If [], use current selection. If None, show nothing.
	@type sel: list
	@param panel: The model viewport to enable isolateSelected for. If empty, use model panel with focus.
	@type panel: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Selection
	if (sel != None) and (not sel): sel = mc.ls(sl=1)
	
	# Check Panel
	if not panel:
		try: panel = getPanel()
		except:
			print('Unable to determine model panel! Aborting...')
			return
	
	# ====================
	# - Isolate Selected -
	# ====================
	
	if state:
	
		# Clear Selection
		mc.select(cl=True)
		
		# Isolate Selected - Enable
		mc.isolateSelect(panel,state=True)
		
		# Update Selection
		if sel: mc.select(sel)
		
		# Load Selected
		mc.isolateSelect(panel,loadSelected=True)
		
		# Update Isolate Set
		mc.isolateSelect(panel,update=True)
	
	else:
		
		# Isolate Selected - Disable
		mc.isolateSelect(panel,state=False)

def getPanelVis(panel=None):
	'''
	Get list of viewport display options.
	@param panel: The model viewport to get visibility options from.
	@type panel: str
	'''
	# Check Panel
	if not panel: panel = getPanel()
	
	# Get Panel Vis
	panelVis = []
	panelVis.append(mc.modelEditor(panel,q=True,nurbsCurves=True))
	panelVis.append(mc.modelEditor(panel,q=True,nurbsSurfaces=True))
	panelVis.append(mc.modelEditor(panel,q=True,polymeshes=True))
	panelVis.append(mc.modelEditor(panel,q=True,subdivSurfaces=True))
	panelVis.append(mc.modelEditor(panel,q=True,planes=True))
	panelVis.append(mc.modelEditor(panel,q=True,lights=True))
	panelVis.append(mc.modelEditor(panel,q=True,cameras=True))
	panelVis.append(mc.modelEditor(panel,q=True,controlVertices=True))
	panelVis.append(mc.modelEditor(panel,q=True,grid=True))
	panelVis.append(mc.modelEditor(panel,q=True,hulls=True))
	panelVis.append(mc.modelEditor(panel,q=True,joints=True))
	panelVis.append(mc.modelEditor(panel,q=True,ikHandles=True))
	panelVis.append(mc.modelEditor(panel,q=True,deformers=True))
	panelVis.append(mc.modelEditor(panel,q=True,dynamics=True))
	panelVis.append(mc.modelEditor(panel,q=True,fluids=True))
	panelVis.append(mc.modelEditor(panel,q=True,hairSystems=True))
	panelVis.append(mc.modelEditor(panel,q=True,follicles=True))
	panelVis.append(mc.modelEditor(panel,q=True,nCloths=True))
	panelVis.append(mc.modelEditor(panel,q=True,nParticles=True))
	panelVis.append(mc.modelEditor(panel,q=True,nRigids=True))
	panelVis.append(mc.modelEditor(panel,q=True,dynamicConstraints=True))
	panelVis.append(mc.modelEditor(panel,q=True,locators=True))
	panelVis.append(mc.modelEditor(panel,q=True,manipulators=True))
	panelVis.append(mc.modelEditor(panel,q=True,dimensions=True))
	panelVis.append(mc.modelEditor(panel,q=True,handles=True))
	panelVis.append(mc.modelEditor(panel,q=True,pivots=True))
	panelVis.append(mc.modelEditor(panel,q=True,textures=True))
	panelVis.append(mc.modelEditor(panel,q=True,strokes=True))
	return panelVis

def setPanelVis(panel,panelVis):
	'''
	Set specified viewport display options based on the provided list of values.
	@param panel: The model viewport to set visibility options for.
	@type panel: str
	@param panelVis: List of panel visibility option values. See getPanelVis() for list order.
	@type panelVis: list
	'''
	mc.modelEditor(panel,e=True,nurbsCurves=panelVis[0])
	mc.modelEditor(panel,e=True,nurbsSurfaces=panelVis[1])
	mc.modelEditor(panel,e=True,polymeshes=panelVis[2])
	mc.modelEditor(panel,e=True,subdivSurfaces=panelVis[3])
	mc.modelEditor(panel,e=True,planes=panelVis[4])
	mc.modelEditor(panel,e=True,lights=panelVis[5])
	mc.modelEditor(panel,e=True,cameras=panelVis[6])
	mc.modelEditor(panel,e=True,controlVertices=panelVis[7])
	mc.modelEditor(panel,e=True,grid=panelVis[8])
	mc.modelEditor(panel,e=True,hulls=panelVis[9])
	mc.modelEditor(panel,e=True,joints=panelVis[10])
	mc.modelEditor(panel,e=True,ikHandles=panelVis[11])
	mc.modelEditor(panel,e=True,deformers=panelVis[12])
	mc.modelEditor(panel,e=True,dynamics=panelVis[13])
	mc.modelEditor(panel,e=True,fluids=panelVis[14])
	mc.modelEditor(panel,e=True,hairSystems=panelVis[15])
	mc.modelEditor(panel,e=True,follicles=panelVis[16])
	mc.modelEditor(panel,e=True,nCloths=panelVis[17])
	mc.modelEditor(panel,e=True,nParticles=panelVis[18])
	mc.modelEditor(panel,e=True,nRigids=panelVis[19])
	mc.modelEditor(panel,e=True,dynamicConstraints=panelVis[20])
	mc.modelEditor(panel,e=True,locators=panelVis[21])
	mc.modelEditor(panel,e=True,manipulators=panelVis[22])
	mc.modelEditor(panel,e=True,dimensions=panelVis[23])
	mc.modelEditor(panel,e=True,handles=panelVis[24])
	mc.modelEditor(panel,e=True,pivots=panelVis[25])
	mc.modelEditor(panel,e=True,textures=panelVis[26])
	mc.modelEditor(panel,e=True,strokes=panelVis[27])

def disablePanelVis(panel):
	'''
	Disable all viewport display options for the specified viewport panel.
	@param panel: The model viewport to disable visibility options for.
	@type panel: str
	'''
	mc.modelEditor(panel,e=True,nurbsCurves=False)
	mc.modelEditor(panel,e=True,nurbsSurfaces=False)
	mc.modelEditor(panel,e=True,polymeshes=False)
	mc.modelEditor(panel,e=True,subdivSurfaces=False)
	mc.modelEditor(panel,e=True,planes=False)
	mc.modelEditor(panel,e=True,lights=False)
	mc.modelEditor(panel,e=True,cameras=False)
	mc.modelEditor(panel,e=True,controlVertices=False)
	mc.modelEditor(panel,e=True,grid=False)
	mc.modelEditor(panel,e=True,hulls=False)
	mc.modelEditor(panel,e=True,joints=False)
	mc.modelEditor(panel,e=True,ikHandles=False)
	mc.modelEditor(panel,e=True,deformers=False)
	mc.modelEditor(panel,e=True,dynamics=False)
	mc.modelEditor(panel,e=True,fluids=False)
	mc.modelEditor(panel,e=True,hairSystems=False)
	mc.modelEditor(panel,e=True,follicles=False)
	mc.modelEditor(panel,e=True,nCloths=False)
	mc.modelEditor(panel,e=True,nParticles=False)
	mc.modelEditor(panel,e=True,nRigids=False)
	mc.modelEditor(panel,e=True,dynamicConstraints=False)
	mc.modelEditor(panel,e=True,locators=False)
	mc.modelEditor(panel,e=True,manipulators=False)
	mc.modelEditor(panel,e=True,dimensions=False)
	mc.modelEditor(panel,e=True,handles=False)
	mc.modelEditor(panel,e=True,pivots=False)
	mc.modelEditor(panel,e=True,textures=False)
	mc.modelEditor(panel,e=True,strokes=False)

def disableAllPanelVis():
	'''
	Disable and store visibilty of all items for all model panels.
	'''
	# Get Visible Panels
	panels = mc.getPanel(type='modelPanel') or []
	
	# Store/Disable Panel Vis States
	panelVis = {}
	for panel in panels:
		panelVis[panel] = getPanelVis(panel=panel)
		disablePanelVis(panel)
	
	# Return Result
	return panelVis

def enableAllPanelVis(panelVis):
	'''
	Restore and enable visibilty of all items for all model panels.
	@param panelVis: The model panel visibility state dictionary.
	@type panelVis: dict
	'''
	# Get Stored Panel List
	panels = panelVis.keys() or []
	
	# Restore/Enable Panel Vis States
	for panel in panels:
		if mc.modelPanel(panel,q=True,ex=True):
			setPanelVis(panel,panelVis[panel])
	
	# Return Result
	return panels
