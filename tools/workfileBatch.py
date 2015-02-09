import maya.mel as mm
import maya.cmds as mc

import glTools.ui.utils

import os

def workfileBatchUI():
	'''
	Workfile Batch Window
	'''
	# Window
	window = 'workfileBatchUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Workfile Batch Manager')
	
	# Layout
	FL = mc.formLayout()
	
	# ===============
	# - UI Elements -
	# ===============
	
	cw = 100
	
	# WorkFile List
	workfileTXT = mc.text(label='Workfile List')
	workfileTSL = mc.textScrollList('workfileBatchTSL',allowMultiSelection=True)
	workfileAddB = mc.button(label='Add',c='glTools.tools.workfileBatch.workfileBatchUI_addFiles("'+workfileTSL+'")')
	workfileDelB = mc.button(label='Remove',c='glTools.ui.utils.removeFromTSL("'+workfileTSL+'")')
	
	workfileListSep = mc.separator(style='single')
	
	pyCmdFileTFB = mc.textFieldButtonGrp('wfBatch_pyCmdFileTFB',label='PyCmdFile',text='',buttonLabel='...',cw=(1,cw))
	mc.textFieldButtonGrp(pyCmdFileTFB,e=True,bc='glTools.tools.workfileBatch.workfileBatchUI_addPyCmd("'+pyCmdFileTFB+'")')
	
	pyCmdFileSep = mc.separator(style='single')
	
	versionUpCBG = mc.checkBoxGrp('wfBatch_versionUpCBG',numberOfCheckBoxes=1,label='Version Up',v1=False,cw=(1,cw))
	snapshotCBG = mc.checkBoxGrp('wfBatch_snapshotCBG',numberOfCheckBoxes=1,label='Snapshot',v1=False,cw=(1,cw))
	publishCBG = mc.checkBoxGrp('wfBatch_publishCBG',numberOfCheckBoxes=1,label='Publish',v1=False,cw=(1,cw),en=False)
	
	publishNotesTXT = mc.text(label='Snapshot/Publish Notes')
	publishNotesSF = mc.scrollField('wfBatch_publishNoteSF',editable=True,wordWrap=True,text='Snapshot generated from workfile batch process.',en=False)
	
	workfileBatchB = mc.button(label='Batch',c='glTools.tools.workfileBatch.workfileBatchFromUI()')
	workfileCloseB = mc.button(label='Close',c='mc.deleteUI("'+window+'")')
	
	# ========================
	# - UI Callback Commands -
	# ========================
	
	mc.checkBoxGrp(snapshotCBG,e=True,cc='glTools.tools.workfileBatch.workfileBatchUI_toggleSnapshot()')
	
	# ================
	# - Form Layouts -
	# ================
	
	mc.formLayout(FL,e=True,af=[(workfileTXT,'top',5),(workfileTXT,'left',5),(workfileTXT,'right',5)])
	mc.formLayout(FL,e=True,af=[(workfileTSL,'left',5),(workfileTSL,'right',5)],ac=[(workfileTSL,'top',5,workfileTXT),(workfileTSL,'bottom',5,workfileAddB)])
	mc.formLayout(FL,e=True,af=[(workfileAddB,'left',5)],ac=[(workfileAddB,'bottom',5,workfileListSep)],ap=[(workfileAddB,'right',5,50)])
	mc.formLayout(FL,e=True,af=[(workfileDelB,'right',5)],ac=[(workfileDelB,'bottom',5,workfileListSep)],ap=[(workfileDelB,'left',5,50)])
	mc.formLayout(FL,e=True,af=[(workfileListSep,'left',5),(workfileListSep,'right',5)],ac=[(workfileListSep,'bottom',5,pyCmdFileTFB)])
	mc.formLayout(FL,e=True,af=[(pyCmdFileTFB,'left',5),(pyCmdFileTFB,'right',5)],ac=[(pyCmdFileTFB,'bottom',5,pyCmdFileSep)])
	mc.formLayout(FL,e=True,af=[(pyCmdFileSep,'left',5),(pyCmdFileSep,'right',5)],ac=[(pyCmdFileSep,'bottom',5,versionUpCBG)])
	mc.formLayout(FL,e=True,af=[(versionUpCBG,'left',5),(versionUpCBG,'right',5)],ac=[(versionUpCBG,'bottom',5,snapshotCBG)])
	mc.formLayout(FL,e=True,af=[(snapshotCBG,'left',5),(snapshotCBG,'right',5)],ac=[(snapshotCBG,'bottom',5,publishCBG)])
	mc.formLayout(FL,e=True,af=[(publishCBG,'left',5),(publishCBG,'right',5)],ac=[(publishCBG,'bottom',5,publishNotesTXT)])
	mc.formLayout(FL,e=True,af=[(publishNotesTXT,'left',5),(publishNotesTXT,'right',5)],ac=[(publishNotesTXT,'bottom',5,publishNotesSF)])
	mc.formLayout(FL,e=True,af=[(publishNotesSF,'left',5),(publishNotesSF,'right',5)],ac=[(publishNotesSF,'bottom',5,workfileBatchB)])
	mc.formLayout(FL,e=True,af=[(workfileBatchB,'left',5),(workfileBatchB,'bottom',5)],ap=[(workfileBatchB,'right',5,50)])
	mc.formLayout(FL,e=True,af=[(workfileCloseB,'right',5),(workfileCloseB,'bottom',5)],ap=[(workfileCloseB,'left',5,50)])
	
	# ===============
	# - Show Window -
	# ===============
	
	mc.showWindow(window)

def workfileBatchUI_addFiles(TSL):
	'''
	Open file dialog to select files to add to workfile batch list
	@param TSL: TextScrollList to add files to
	@type TSL: str
	'''
	# Get Existing Workfile List
	workfileList = mc.textScrollList(TSL,q=True,ai=True) or []
	
	# Get Workfile List
	fileFilter = 'Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)'
	workfileSel = mc.fileDialog2(fileFilter=fileFilter,dialogStyle=2,fileMode=4,cap='Workfile Batch - Add Files')
	
	# Add Files to List
	for workfile in workfileSel:
		if not workfile in workfileList:
			mc.textScrollList(TSL,e=True,a=workfile)

def workfileBatchUI_addPyCmd(TFB):
	'''
	Open file dialog to select python comand file to run on workfiles
	@param TFB: textFieldButtonGrp to add file to
	@type TFB: str
	'''
	# Get Python Command File
	pyCmdFile = mc.fileDialog2(fileFilter='*.py',dialogStyle=2,fileMode=1,cap='Workfile Batch - Select Command File')
	
	# Update textFieldButtonGrp
	if pyCmdFile: mc.textFieldButtonGrp(TFB,e=True,text=pyCmdFile[0])

def workfileBatchUI_toggleSnapshot():
	'''
	'''
	snapshot = mc.checkBoxGrp('wfBatch_snapshotCBG',q=True,v1=True)
	mc.checkBoxGrp('wfBatch_publishCBG',e=True,en=snapshot)
	mc.scrollField('wfBatch_publishNoteSF',e=True,en=snapshot)

def workfileBatchFromUI():
	'''
	Workfile Batch From UI
	'''
	# Get Workfile List
	workfileList = mc.textScrollList('workfileBatchTSL',q=True,ai=True)
	
	# Get Workfile Batch Data
	cmdsFile = mc.textFieldButtonGrp('wfBatch_pyCmdFileTFB',q=True,text=True)
	versionUp = mc.checkBoxGrp('wfBatch_versionUpCBG',q=True,v1=True)
	snapshot = mc.checkBoxGrp('wfBatch_snapshotCBG',q=True,v1=True)
	publish = mc.checkBoxGrp('wfBatch_publishCBG',q=True,v1=True)
	publishNote = mc.scrollField('wfBatch_publishNoteSF',q=True,text=True)
	
	# For Each Workfile
	for workfile in workfileList:
		
		workfileBatch(	workfile=workfile,
						cmdsFile=cmdsFile,
						versionUp=versionUp,
						snapshot=snapshot,
						publish=publish,
						publishNote=publishNote	)
	

def workfileBatch(workfile,cmdsFile='',versionUp=False,snapshot=False,publish=False,publishNote=''):
	'''
	Workfile batch.
	@param workfile: Workfile to batch process
	@type workfile: str
	@param cmdsFile: Optional python command file to run on workfile
	@type cmdsFile: str
	@param versionUp: Version up workfile
	@type versionUp: bool
	@param snapshot: Snapshot workfile
	@type snapshot: bool
	@param publish: Publish workfile
	@type publish: bool
	@param publishNote: Snapshot/Publish notes
	@type publishNote: str
	'''
	# Build Workfile Batch Command
	workfileBatchCmd = "workfileBatch"
	workfileBatchCmd += " "+workfile
	workfileBatchCmd += " "+cmdsFile
	workfileBatchCmd += " "+str(int(versionUp))
	workfileBatchCmd += " "+str(int(snapshot))
	workfileBatchCmd += " "+str(int(publish))
	workfileBatchCmd += " '"+publishNote+"'"
	
	# Get Workfile Basename
	fileName = os.path.basename(workfile)
	
	# Execute Workfile Batch Command
	os.system('xterm -hold -T "'+fileName+'" -e "'+workfileBatchCmd+'" &')

def workfileBatchSubmit(workfile,cmdsFile='',versionUp=False,snapshot=False,publish=False,publishNote=''):
	'''
	Workfile batch submit to qube.
	@param workfile: Workfile to batch process
	@type workfile: str
	@param cmdsFile: Optional python command file to run on workfile
	@type cmdsFile: str
	@param versionUp: Version up workfile
	@type versionUp: bool
	@param snapshot: Snapshot workfile
	@type snapshot: bool
	@param publish: Publish workfile
	@type publish: bool
	@param publishNote: Snapshot/Publish notes
	@type publishNote: str
	'''
	# Build Workfile Batch Command
	workfileBatchCmd = "/" ######!!!!!
	workfileBatchCmd += " "+workfile
	workfileBatchCmd += " "+cmdsFile
	workfileBatchCmd += " "+str(int(versionUp))
	workfileBatchCmd += " "+str(int(snapshot))
	workfileBatchCmd += " "+str(int(publish))
	workfileBatchCmd += " '"+publishNote+"'"
	
	# Submit Workfile Batch Command to Qube
	os.system('qbsub --name maya_workfile_batch --shell /bin/tcsh --cluster /ent/hbm/vfx  -e "'+workfileBatchCmd)
