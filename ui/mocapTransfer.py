import maya.cmds as mc

import glTools.anim.mocap_utils
import glTools.ui.utils

def create():
	'''
	Mocap Transfer UI.
	'''
	# ============
	# - Build UI -
	# ============
	
	# Window
	window = 'mocapTransferUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,title='Mocap/Anim Transfer',sizeable=True)
	
	# FormLayout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# Buttons
	transferB = mc.button(label='Transfer',c='glTools.ui.mocapTransfer.transferFromUI()')
	closeB = mc.button(label='Close',c='mc.deleteUI("'+window+'")')
	
	# FrameLayout
	mc.setParent(FL)
	rangeLayout = mc.frameLayout(label='Bake Range',borderStyle='in')
	
	# TabLayout
	mc.setParent(FL)
	tabLayout = mc.tabLayout('mocapXferTabLayout',innerMarginWidth=5,innerMarginHeight=5)
	
	mc.formLayout(FL,e=True,af=[(closeB,'left',5),(closeB,'right',5),(closeB,'bottom',5)])
	mc.formLayout(FL,e=True,af=[(transferB,'left',5),(transferB,'right',5)],ac=[(transferB,'bottom',5,closeB)])
	mc.formLayout(FL,e=True,af=[(tabLayout,'left',5),(tabLayout,'right',5),(tabLayout,'top',5)])
	mc.formLayout(FL,e=True,af=[(rangeLayout,'left',5),(rangeLayout,'right',5)],ac=[(rangeLayout,'top',5,tabLayout),(rangeLayout,'bottom',5,transferB)])
	
	# ----------------
	# - Range Layout -
	# ----------------
	
	mc.setParent(rangeLayout)
	
	# FormLayout
	bakeRangeFL = mc.formLayout(numberOfDivisions=100)
	
	mocap_rangeCBG = mc.checkBoxGrp('xferMocap_bakeRangeCBG',label='Specify Bake Range:',numberOfCheckBoxes=1,value1=0)
	mocap_startEndIFG = mc.intFieldGrp('xferMocap_startEndCBG',label='Bake Range Start/End:',numberOfFields=2,value1=0,value2=0,en=False)
	mocap_staticChanCBG = mc.checkBoxGrp('xferMocap_staticChanCBG',label='Delete Static Channels:',numberOfCheckBoxes=1,value1=0)
	
	mc.formLayout(bakeRangeFL,e=True,af=[(mocap_rangeCBG,'left',5),(mocap_rangeCBG,'right',5),(mocap_rangeCBG,'top',5)])
	mc.formLayout(bakeRangeFL,e=True,af=[(mocap_startEndIFG,'left',5),(mocap_startEndIFG,'right',5)],ac=[(mocap_startEndIFG,'top',5,mocap_rangeCBG)])
	mc.formLayout(bakeRangeFL,e=True,af=[(mocap_staticChanCBG,'left',5),(mocap_staticChanCBG,'right',5)],ac=[(mocap_staticChanCBG,'top',5,mocap_startEndIFG)])
	
	# UI Element Callbacks
	mc.checkBoxGrp(mocap_rangeCBG,e=True,cc='glTools.ui.mocapTransfer.toggleBakeRange()')
	
	# ---------------------
	# - FROM Mocap Layout -
	# ---------------------
	
	mc.setParent(tabLayout)
	
	# FormLayout
	fromMocapFL = mc.formLayout(numberOfDivisions=100)
	
	# Layout Elements
	fromMocap_mocapTFB = mc.textFieldButtonGrp('fromMocap_mocapTFB',label='Mocap NS:',text='',buttonLabel='<<<')
	fromMocap_rigTFB = mc.textFieldButtonGrp('fromMocap_rigTFB',label='Rig NS:',text='',buttonLabel='<<<')
	fromMocap_SEP = mc.separator(height=10,style='single')
	fromMocap_xferToRBG = mc.radioButtonGrp('fromMocap_xferToRBG',label='Transfer To:',numberOfRadioButtons=2,labelArray2=['Controls','Overrides'],select=2)
	fromMocap_xferHandCBG = mc.checkBoxGrp('fromMocap_xferHandCBG',label='Transfer Fingers:',numberOfCheckBoxes=1,value1=0)
	
	mc.formLayout(fromMocapFL,e=True,af=[(fromMocap_mocapTFB,'left',5),(fromMocap_mocapTFB,'right',5),(fromMocap_mocapTFB,'top',5)])
	mc.formLayout(fromMocapFL,e=True,af=[(fromMocap_rigTFB,'left',5),(fromMocap_rigTFB,'right',5)],ac=[(fromMocap_rigTFB,'top',5,fromMocap_mocapTFB)])
	mc.formLayout(fromMocapFL,e=True,af=[(fromMocap_SEP,'left',5),(fromMocap_SEP,'right',5)],ac=[(fromMocap_SEP,'top',5,fromMocap_rigTFB)])
	mc.formLayout(fromMocapFL,e=True,af=[(fromMocap_xferToRBG,'left',5),(fromMocap_xferToRBG,'right',5)],ac=[(fromMocap_xferToRBG,'top',5,fromMocap_SEP)])
	mc.formLayout(fromMocapFL,e=True,af=[(fromMocap_xferHandCBG,'left',5),(fromMocap_xferHandCBG,'right',5)],ac=[(fromMocap_xferHandCBG,'top',5,fromMocap_xferToRBG)])
	
	# UI Element Callbacks
	mc.textFieldButtonGrp(fromMocap_mocapTFB,e=True,bc='glTools.ui.utils.loadNsSel("'+fromMocap_mocapTFB+'",topOnly=False)')
	mc.textFieldButtonGrp(fromMocap_rigTFB,e=True,bc='glTools.ui.utils.loadNsSel("'+fromMocap_rigTFB+'",topOnly=False)')
	
	# -------------------
	# - TO Mocap Layout -
	# -------------------
	
	mc.setParent(tabLayout)
	
	# FormLayout
	toMocapFL = mc.formLayout(numberOfDivisions=100)
	
	# Layout Elements
	toMocap_rigTFB = mc.textFieldButtonGrp('toMocap_rigTFB',label='Rig NS:',text='',buttonLabel='<<<')
	toMocap_mocapTFB = mc.textFieldButtonGrp('toMocap_mocapTFB',label='Mocap NS:',text='',buttonLabel='<<<')
	
	mc.formLayout(toMocapFL,e=True,af=[(toMocap_rigTFB,'left',5),(toMocap_rigTFB,'right',5),(toMocap_rigTFB,'top',5)])
	mc.formLayout(toMocapFL,e=True,af=[(toMocap_mocapTFB,'left',5),(toMocap_mocapTFB,'right',5)],ac=[(toMocap_mocapTFB,'top',5,toMocap_rigTFB)])
	
	# UI Element Callbacks
	mc.textFieldButtonGrp(toMocap_rigTFB,e=True,bc='glTools.ui.utils.loadNsSel("'+toMocap_rigTFB+'",topOnly=False)')
	mc.textFieldButtonGrp(toMocap_mocapTFB,e=True,bc='glTools.ui.utils.loadNsSel("'+toMocap_mocapTFB+'",topOnly=False)')
	
	# ---------------------
	# - Rig TO Rig Layout -
	# ---------------------
	
	mc.setParent(tabLayout)
	
	# FormLayout
	rigToRigFL = mc.formLayout(numberOfDivisions=100)
	
	# Layout Elements
	rigToRig_srcTFB = mc.textFieldButtonGrp('rigToRig_srcTFB',label='Source Rig NS:',text='',buttonLabel='<<<')
	rigToRig_dstTFB = mc.textFieldButtonGrp('rigToRig_dstTFB',label='Destination Rig NS:',text='',buttonLabel='<<<')
	rigToRig_SEP = mc.separator(height=10,style='single')
	rigToRig_xferToRBG = mc.radioButtonGrp('rigToRig_xferToRBG',label='Transfer To:',numberOfRadioButtons=2,labelArray2=['Controls','Overrides'],select=1)
	rigToRig_xferHandCBG = mc.checkBoxGrp('rigToRig_xferHandCBG',label='Transfer Fingers:',numberOfCheckBoxes=1,value1=0)
	rigToRig_xferAllTransCBG = mc.checkBoxGrp('rigToRig_xferAllTransCBG',label='Transfer AllTrans:',numberOfCheckBoxes=1,value1=0)
	
	mc.formLayout(rigToRigFL,e=True,af=[(rigToRig_srcTFB,'left',5),(rigToRig_srcTFB,'right',5),(rigToRig_srcTFB,'top',5)])
	mc.formLayout(rigToRigFL,e=True,af=[(rigToRig_dstTFB,'left',5),(rigToRig_dstTFB,'right',5)],ac=[(rigToRig_dstTFB,'top',5,rigToRig_srcTFB)])
	mc.formLayout(rigToRigFL,e=True,af=[(rigToRig_SEP,'left',5),(rigToRig_SEP,'right',5)],ac=[(rigToRig_SEP,'top',5,rigToRig_dstTFB)])
	mc.formLayout(rigToRigFL,e=True,af=[(rigToRig_xferToRBG,'left',5),(rigToRig_xferToRBG,'right',5)],ac=[(rigToRig_xferToRBG,'top',5,rigToRig_SEP)])
	mc.formLayout(rigToRigFL,e=True,af=[(rigToRig_xferHandCBG,'left',5),(rigToRig_xferHandCBG,'right',5)],ac=[(rigToRig_xferHandCBG,'top',5,rigToRig_xferToRBG)])
	mc.formLayout(rigToRigFL,e=True,af=[(rigToRig_xferAllTransCBG,'left',5),(rigToRig_xferAllTransCBG,'right',5)],ac=[(rigToRig_xferAllTransCBG,'top',5,rigToRig_xferHandCBG)])
	
	# UI Element Callbacks
	mc.textFieldButtonGrp(rigToRig_srcTFB,e=True,bc='glTools.ui.utils.loadNsSel("'+rigToRig_srcTFB+'",topOnly=False)')
	mc.textFieldButtonGrp(rigToRig_dstTFB,e=True,bc='glTools.ui.utils.loadNsSel("'+rigToRig_dstTFB+'",topOnly=False)')
	
	# ---------------------
	# - Label Layout Tabs -
	# ---------------------
	
	mc.tabLayout(tabLayout,e=True,tabLabel=((fromMocapFL,'From Mocap'),(toMocapFL,'To Mocap'),(rigToRigFL,'Rig To Rig')))
	
	# ==============
	# - Display UI -
	# ==============
	
	initializeBakeRange()
	
	mc.window(window,e=True,wh=[445,330])
	mc.showWindow(window)

def transferFromUI():
	'''
	Transfer mocap animation from UI input.
	'''
	# Get Selected Tab
	selTab = mc.tabLayout('mocapXferTabLayout',q=True,selectTabIndex=True)
	
	# Get Bake Range
	start = mc.intFieldGrp('xferMocap_startEndCBG',q=True,v1=True)
	end = mc.intFieldGrp('xferMocap_startEndCBG',q=True,v2=True)
	deleteStaticChannels = mc.checkBoxGrp('xferMocap_staticChanCBG',q=True,v1=True)
	if not mc.checkBoxGrp('xferMocap_bakeRangeCBG',q=True,value1=True):
		start = mc.playbackOptions(q=True,min=True)
		end = mc.playbackOptions(q=True,max=True)
	
	# FROM Mocap
	if selTab == 1:
		
		# Get Mocap to Rig Input
		mocapNS = mc.textFieldButtonGrp('fromMocap_mocapTFB',q=True,text=True)
		rigNS = mc.textFieldButtonGrp('fromMocap_rigTFB',q=True,text=True)
		toCtrls = mc.radioButtonGrp('fromMocap_xferToRBG',q=True,select=True) == 1
		toHands = mc.checkBoxGrp('fromMocap_xferHandCBG',q=True,value1=True)
		
		# Transfer Mocap to Rig
		glTools.anim.mocap_utils.transferMocapToRig(	mocapNS		= mocapNS,
													rigNS		= rigNS,
													toCtrls		= toCtrls,
													bakeAnim	= True,
													bakeSim		= True,
													start		= start,
													end			= end,
													deleteStaticChannels = deleteStaticChannels )
		
		if toHands:
			glTools.anim.mocap_utils.transferHandAnim(	mocapNS	= mocapNS,
														rigNS	= rigNS,
														start	= start,
														end		= end,
														deleteStaticChannels = deleteStaticChannels )
	
	# TO Mocap
	elif selTab == 2:
		
		# Get Anim to Mocap Input
		rigNS = mc.textFieldButtonGrp('toMocap_rigTFB',q=True,text=True)
		mocapNS = mc.textFieldButtonGrp('toMocap_mocapTFB',q=True,text=True)
		
		# Transfer Anim to Mocap
		glTools.anim.mocap_utils.transferAnimToMocap(	rigNS		= rigNS,
														mocapNS		= mocapNS,
														bakeAnim	= True,
														bakeSim		= True,
														start		= start,
														end			= end,
														deleteStaticChannels = deleteStaticChannels )
	
	# Rig TO Rig
	elif selTab == 3:
		
		# Get Anim to Mocap Input
		srcNS = mc.textFieldButtonGrp('rigToRig_srcTFB',q=True,text=True)
		dstNS = mc.textFieldButtonGrp('rigToRig_dstTFB',q=True,text=True)
		toCtrls = mc.radioButtonGrp('rigToRig_xferToRBG',q=True,select=True) == 1
		toHands = mc.checkBoxGrp('rigToRig_xferHandCBG',q=True,value1=True)
		toAllTrans = mc.checkBoxGrp('rigToRig_xferAllTransCBG',q=True,value1=True)
		
		# Transfer Anim to Mocap
		glTools.anim.mocap_utils.transferAnimToRig(	srcNS			= srcNS,
													dstNS			= dstNS,
													attachCtrl		= toCtrls,
													attachFingers	= toHands,
													attachAllTrans	= toAllTrans,
													start			= start,
													end				= end,
													deleteStaticChannels = deleteStaticChannels )
	
	# Invalid Tab
	else: raise Exception('Invalid tab index!')
	
	# Return Result
	return

def initializeBakeRange():
	'''
	Initialize bake anim range based on playback timeline min/max.
	'''
	start = mc.playbackOptions(q=True,min=True)
	end = mc.playbackOptions(q=True,max=True)
	mc.intFieldGrp('xferMocap_startEndCBG',e=True,v1=start,v2=end)
	
def toggleBakeRange():
	'''
	Toggle bake anim range input.
	'''
	enable = mc.checkBoxGrp('xferMocap_bakeRangeCBG',q=True,value1=True)
	mc.intFieldGrp('xferMocap_startEndCBG',e=True,en=enable)
	if not enable: initializeBakeRange()
