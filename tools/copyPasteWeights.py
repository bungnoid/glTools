import maya.mel as mm
import maya.cmds as mc

import glTools.utils.component
import glTools.utils.selection
import glTools.utils.skinCluster

import gl_globals

class UserInterupted(Exception): pass

def copyPasteWeightsUI():
	'''
	CopyPaste weights tool UI
	'''
	# Define Window
	win = 'copyPasteWeightsUI'
	# Check Window
	if mc.window(win,q=True,ex=True): mc.deleteUI(win)
	
	# Build Window
	mc.window(win,t='Copy/Paste Skin Weights')
	
	# layout
	mc.columnLayout()
	
	# Buttons
	mc.button(w=200,l='Copy Weights',c='glTools.tools.copyPasteWeights.copyWeights()')
	mc.button(w=200,l='Paste Weights',c='glTools.tools.copyPasteWeights.pasteWeights()')
	mc.button(w=200,l='Average Weights',c='glTools.tools.copyPasteWeights.averageWeights()')
	mc.button(w=200,l='Auto Average',c='glTools.tools.copyPasteWeights.autoAverageWeights()')
	mc.button(w=200,l='Close',c=('mc.deleteUI("'+win+'")'))
	
	# Show Window
	mc.showWindow(win)

def copyWeights(tol=0.000001):
	'''
	Copy weights of selected vertices
	@param tol: Minimum influence weight tolerance
	@type tol: float
	'''
	# Get Component Selection
	sel = mc.filterExpand(ex=True,sm=[28,31,46])
	if not sel: return
	cv = sel[0]
	
	# Get Geometry from Component
	geo = mc.ls(cv,o=True)[0]
	
	# Get SkinCluster from Geometry
	skin = glTools.utils.skinCluster.findRelatedSkinCluster(geo)
	if not skin: raise Exception('Geometry "'+geo+'" is not attached to a valid skinCluster!')
	
	# Get Influence List
	joints = mc.skinCluster(skin,q=True,inf=True)
	
	# Copy Weights
	wt = mc.skinPercent(skin,cv,q=True,v=True)
	cmd = 'skinPercent'
	for jnt in joints:
		
		# Get Influence Weight
		wt = mc.skinPercent(skin,cv,q=True,v=True,transform=jnt)
		
		# Check Weight Tolerance
		if wt < tol: continue
		
		# Append skinPercent Command
		cmd += (' -tv '+jnt+' '+str(round(wt,5)));
	
	# Finalize skinPercent Command
	cmd += ' -zri true ###'
	
	# Set Global Weight Value
	gl_globals.glCopyPasteWeightCmd = cmd
	print gl_globals.glCopyPasteWeightCmd

def pasteWeights(showProgress=True):
	'''
	@param showProgress: Show operation progress using the main progress bar
	@type showProgress: bool
	'''
	# Global Weight Value
	wt = gl_globals.glCopyPasteWeightCmd
	
	# Get Component Selection
	sel = mc.filterExpand(ex=True,sm=[28,31,46])
	if not sel: return
	
	# Begin Progress Bar
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	if showProgress:
		mc.progressBar( gMainProgressBar,e=True,bp=True,ii=True,status=('Pasting Skin Weights...'),maxValue=len(sel) )
	
	selComp = glTools.utils.selection.componentListByObject(sel)
	for objComp in selComp:
		
		# Get Object from Component
		geo = mc.ls(objComp[0],o=True)[0]
		
		# Get SkinCluster from Geometry
		skin = glTools.utils.skinCluster.findRelatedSkinCluster(geo)
		if not skin: raise Exception('Geometry "'+geo+'" is not attached to a valid skinCluster!')
		# Disable Weight Normalization
		mc.setAttr(skin+'.normalizeWeights',0)
		
		# For Each Component
		for cv in objComp:
			
			# Update skinPercent Command
			cmd = wt.replace('###',skin)
			
			# Evaluate skinPercent Command
			try: 
				mm.eval(cmd)
				#print(cmd)
			except Exception, e:
				if showProgress: mc.progressBar(gMainProgressBar,e=True,endProgress=True)
				raise Exception(str(s))
			
			# Update Progress Bar
			cvLen = len(mc.ls(cv,fl=True))
			if showProgress:
				if mc.progressBar(gMainProgressBar,q=True,isCancelled=True):
					mc.progressBar(gMainProgressBar,e=True,endProgress=True)
					raise UserInterupted('Operation cancelled by user!')
				mc.progressBar(gMainProgressBar,e=True,step=cvLen)
			
		# Normalize Weights
		mc.setAttr(skin+'.normalizeWeights',1)
		mc.skinPercent(skin,normalize=True)
	
	# End Current Progress Bar
	if showProgress: mc.progressBar(gMainProgressBar,e=True,endProgress=True)

def averageWeights(tol=0.000001):
	'''
	Average weights of selected vertices
	@param tol: Minimum influence weight tolerance
	@type tol: float
	'''
	# Get Component Selection
	sel = mc.filterExpand(ex=True,sm=[28,31,46])
	if not sel: return
	
	# Get Component Selection by Object
	sel = glTools.utils.selection.componentListByObject(sel)
	if not sel: return
	sel = sel[0]
	
	# Get Object from Components
	geo = mc.ls(sel[0],o=True)[0]

	# Get SkinCluster
	skin = glTools.utils.skinCluster.findRelatedSkinCluster(geo)
	if not skin: raise Exception('Geometry "'+geo+'" is not attached to a valid skinCluster!')

	# Get Influence List
	joints = mc.skinCluster(skin,q=True,inf=True)
	
	# Initialize skinPercent Command
	cmd = 'skinPercent'
	
	# For Each SkinCluster Influence
	for jnt in joints:
		
		# Initialize Average Influence Weight 
		wt = 0.0
		
		# For each CV
		for cv in sel:
			wt += mc.skinPercent(skin,cv,q=True,transform=jnt)
		
		# Average Weight
		wt /= len(joints)
		
		# Check Weight Tolerance
		if wt < tol: continue
		
		# Append to skinPercent Command
		cmd += (' -tv '+jnt+' '+str(round(wt,5)))

	# Finalize skinPercent Command
	cmd += (' -zri true ### ')
	
	# Return Result
	gl_globals.glCopyPasteWeightCmd = cmd
	print gl_globals.glCopyPasteWeightCmd

def autoAverageWeights():
	'''
	'''
	# Get Component Selection
	sel = mc.filterExpand(ex=True,sm=[28,31,46])
	if not sel: return
	
	# For Each Vertex
	for vtx in sel:
		
		# Select Vert
		mc.select(vtx)
		
		# Expand Selection
		mm.eval('PolySelectTraverse 1')
		mc.select(vtx,d=True)
		
		# Calculate Average Weights from Neighbours
		averageWeights()
		mc.select(vtx)
		# Paste Average Weights
		pasteWeights()
	
def hotkeySetup():
	'''
	'''
	# ====================
	# - Runtime Commands -
	# ====================
	
	# Copy Weights
	if mm.eval('runTimeCommand -q -ex rt_copyWeights'):
		mm.eval('runTimeCommand -e -del rt_copyWeights')
	mm.eval('runTimeCommand -annotation "" -category "User" -commandLanguage "python" -command "import glTools.tools.copyPasteWeights;reload(glTools.tools.copyPasteWeights);glTools.tools.copyPasteWeights.copyWeights()" rt_copyWeights')
	
	# Paste Weights
	if mm.eval('runTimeCommand -q -ex rt_pasteWeights'):
		mm.eval('runTimeCommand -e -del rt_pasteWeights')
	mm.eval('runTimeCommand -annotation "" -category "User" -commandLanguage "python" -command "import glTools.tools.copyPasteWeights;reload(glTools.tools.copyPasteWeights);glTools.tools.copyPasteWeights.pasteWeights()" rt_pasteWeights')
	
	# Average Weights
	if mm.eval('runTimeCommand -q -ex rt_averageWeights'):
		mm.eval('runTimeCommand -e -del rt_averageWeights')
	mm.eval('runTimeCommand -annotation "" -category "User" -commandLanguage "python" -command "import glTools.tools.copyPasteWeights;reload(glTools.tools.copyPasteWeights);glTools.tools.copyPasteWeights.averageWeights()" rt_averageWeights')
	
	# Auto Average Weights
	if mm.eval('runTimeCommand -q -ex rt_autoAverageWeights'):
		mm.eval('runTimeCommand -e -del rt_autoAverageWeights')
	mm.eval('runTimeCommand -annotation "" -category "User" -commandLanguage "python" -command "import glTools.tools.copyPasteWeights;reload(glTools.tools.copyPasteWeights);glTools.tools.copyPasteWeights.autoAverageWeights()" rt_autoAverageWeights')
	
	# ========================
	# - Create Name Commands -
	# ========================
	
	copyWtCmd = mc.nameCommand(		'copyWeightsNameCommand',
									ann='copyWeightsNameCommand',
									sourceType='mel',
									c='rt_copyWeights' )
	
	pasteWtCmd = mc.nameCommand(	'pasteWeightsNameCommand',
									ann='pasteWeightsNameCommand',
									sourceType='mel',
									c='rt_pasteWeights' )
	
	averageWtCmd = mc.nameCommand(	'averageWeightsNameCommand',
									ann='averageWeightsNameCommand',
									sourceType='mel',
									c='rt_averageWeights' )
	
	autoAverageWtCmd = mc.nameCommand(	'autoAverageWeightsNameCommand',
										ann='autoAverageWeightsNameCommand',
										sourceType='mel',
										c='rt_autoAverageWeights' )
	
	# =============================
	# - Create Hotkey Assignments -
	# =============================
	
	mc.hotkey(keyShortcut='c',alt=True,name=copyWtCmd)
	mc.hotkey(keyShortcut='v',alt=True,name=pasteWtCmd)
	mc.hotkey(keyShortcut='x',alt=True,name=averageWtCmd)
	mc.hotkey(keyShortcut='a',alt=True,name=autoAverageWtCmd)
	
