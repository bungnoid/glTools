import maya.mel as mm
import maya.cmds as mc

import glTools.tools.crowd

import chunkified.maya.crowd
import chunkified.massive.file.callsheet as csh
import chunkified.helper.alphanum as alpha

import os.path

def loadAgentUI():
	'''
	'''
	# Build Window
	window = 'loadAgentUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Load Massive Agent')
	
	# Layout
	FL = mc.formLayout()
	
	# UI Elements
	callsheetTBG = mc.textFieldButtonGrp('loadAgent_callsheetTBG',label='Callsheet',buttonLabel='...',text='')
	agentTSL = mc.textScrollList('loadAgent_agentTBG',ams=True)
	agentInfoSF = mc.scrollField('loadAgent_agentInfoSF',editable=False,wordWrap=False,text='')
	
	#loadRigCBG = mc.checkBoxGrp('loadAgent_loadRigCBG',numberOfCheckBoxes=1,label='Load Agent Rig',v1=True)
	#bakeAnimCBG = mc.checkBoxGrp('loadAgent_bakeAnimCBG',numberOfCheckBoxes=1,label='Bake Agent Anim',v1=True)
	#saveSceneCBG = mc.checkBoxGrp('loadAgent_saveSceneCBG',numberOfCheckBoxes=1,label='Save Workfile',v1=False)
	
	loadB = mc.button('loadAgent_loadB',label='Load',c='glTools.tools.loadAgent.loadAgentFromUI()')
	closeB = mc.button('loadAgent_closeB',label='Close',c='mc.deleteUI("'+window+'")')
	
	# UI Callbacks
	mc.textFieldButtonGrp(callsheetTBG,e=True,bc='glTools.tools.loadAgent.importCallsheet()')
	mc.textFieldButtonGrp(callsheetTBG,e=True,cc='glTools.tools.loadAgent.loadCallsheetData()')
	mc.textScrollList(agentTSL,e=True,sc='glTools.tools.loadAgent.updateAgentInfo()')
		
	# Form Layout
	mc.formLayout(FL,e=True,af=[(callsheetTBG,'top',5),(callsheetTBG,'left',5),(callsheetTBG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(agentTSL,'top',5,callsheetTBG),(agentTSL,'bottom',5,loadB)],af=[(agentTSL,'left',5)],ap=[(agentTSL,'right',5,50)])
	mc.formLayout(FL,e=True,ac=[(agentInfoSF,'top',5,callsheetTBG),(agentInfoSF,'bottom',5,loadB)],af=[(agentInfoSF,'right',5)],ap=[(agentInfoSF,'left',5,50)])
	mc.formLayout(FL,e=True,ac=[(loadB,'bottom',5,closeB)],af=[(loadB,'left',5),(loadB,'right',5)])
	mc.formLayout(FL,e=True,af=[(closeB,'left',5),(closeB,'right',5),(closeB,'bottom',5)])
		
	# Show Window
	mc.showWindow(window)
	
def importCallsheet():
	'''
	Import a callsheet to the load agent UI
	'''
	# Define textField
	callsheetTBG = 'loadAgent_callsheetTBG'
	
	# Load Callsheet
	glTools.ui.utils.loadFilePath(	textField=callsheetTBG,
									fileFilter='*.txt',
									caption='Load Callsheet',
									startDir=None)
	
	# Load Callsheet Data
	loadCallsheetData()

def loadCallsheetData():
	'''
	'''
	# Define textField
	callsheetTBG = 'loadAgent_callsheetTBG'
	agentTSL = 'loadAgent_agentTBG'
	
	# Get Callsheet File
	callsheetFile = mc.textFieldButtonGrp(callsheetTBG,q=True,text=True)
	if not os.path.isfile(callsheetFile):
		print('Invalid callsheet file path...')
		return
	
	# Get Callsheet Data
	callsheet = csh.Callsheet()
	try: callsheet.open(callsheetFile)
	except:
		print('Unable to load callsheet!')
		return
	
	# Get Agent List
	agents = callsheet.agents()
	if not agents:
		print('No agents found in callsheet data!')
		return
	
	# Clear List
	mc.textScrollList(agentTSL,e=True,ra=True)
	
	# List Agents
	for agent in agents:
		if 'reverse_agent' in agent: continue
		if 'avoid_agent' in agent: continue
		if 'util_agent' in agent: continue
		mc.textScrollList(agentTSL,e=True,a=agent)

def agentVars(callsheetFile,agent):
	'''
	'''
	# Get Agent Data
	callsheet = csh.Callsheet()
	callsheet.open(callsheetFile)
	
	# Check Agent
	agents = callsheet.agents()
	agent_vars = callsheet.vars()
	if not agent in agents:
		raise Exception('Agent "'+agent+'" not found in callsheet ("'+callsheetFile+'")!')
	if not agent_vars.has_key(agent):
		raise Exception(' No agent data for "'+agent+'" in callsheet ("'+callsheetFile+'")!')
	
	# Return Result
	return agent_vars[agent]

def updateAgentInfo():
	'''
	'''
	# Define Agent Info Panel
	agentInfoSF = 'loadAgent_agentInfoSF'
	# Clear Agent Info
	mc.scrollField(agentInfoSF,e=True,text='')
	
	# Get Callsheet File
	callsheetTBG = 'loadAgent_callsheetTBG'
	callsheetFile = mc.textFieldButtonGrp(callsheetTBG,q=True,text=True)
	
	# Get Selected Agents
	agentTSL = 'loadAgent_agentTBG'
	agentList = mc.textScrollList(agentTSL,q=True,si=True)
	
	# Build Agent Info String
	agentInfo = ''
	for agent in agentList:
		
		# Get Agent Variables
		agentVar = agentVars(callsheetFile,agent)
		
		agentInfo += '# == '+agent+' ==\n\n'
		if agentVar.has_key('costume_VAR'):
			agentInfo += 'Costume Typ: '+str(int(agentVar['costume_VAR']))+'\n'
		if agentVar.has_key('costume_colour_VAR'): 
			agentInfo += 'Costume Col: '+str(int(agentVar['costume_colour_VAR']))+'\n'
		if agentVar.has_key('hair_colour_VAR'):
			agentInfo += 'Groom/Hair Col: '+str(int(agentVar['hair_colour_VAR']))+'\n'
		if agentVar.has_key('scale_VAR'):
			agentInfo += 'Agent Scale: '+str(agentVar['scale_VAR'])+'\n'
		if agentVar.has_key('prop_active_VAR'):
			agentInfo += 'Agent Prop: '+str(bool(int(agentVar['prop_active_VAR'])))+'\n'
		if agentVar.has_key('prop_L_VAR'):
			agentInfo += 'Left Hand Prop ID: '+str(int(agentVar['prop_L_VAR']))+'\n'
		if agentVar.has_key('prop_R_VAR'):
			agentInfo += 'Left Hand Prop ID: '+str(int(agentVar['prop_R_VAR']))+'\n'
		agentInfo += '\n\n'
	
	# Update Agent Info
	mc.scrollField(agentInfoSF,e=True,text=agentInfo)

def loadAgentFromUI():
	'''
	'''
	callsheetTBG = 'loadAgent_callsheetTBG'
	agentTSL = 'loadAgent_agentTBG'
	
	callsheetFile = mc.textFieldButtonGrp(callsheetTBG,q=True,text=True)
	agentList = mc.textScrollList(agentTSL,q=True,si=True)
	animStart = None
	animEnd = None
	animOffset = 0
	bakeAnim = True
	saveScene = False
	exportScenegraph = False
	bpf = True
	
	if not os.path.isfile(callsheetFile):
		raise Exception('Callsheet file "'+callsheetFile+'" does not exist!')
	
	# Load Agents
	for agent in agentList:
		
		# Rebuild Agent
		agentNS = glTools.tools.crowd.mayaAgentSetupApf(	agent,
														callsheetFile=callsheetFile,
														animStart=animStart,
														animEnd=animEnd,
														animOffset=animOffset,
														bakeAnim=bakeAnim,
														saveScene=saveScene,
														exportScenegraph=exportScenegraph,
														bpf=bpf	)
