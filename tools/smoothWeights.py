import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.component
import glTools.utils.mesh
import glTools.utils.selection
import glTools.utils.skinCluster

class UserInterupted(Exception): pass

def smoothWeights(vtxList=[],faceConnectivity=False,showProgress=False,debug=False):
	'''
	Smooth skincluster weights for the specified vertex list.
	Only works for valid mesh vertices bound to an existing skinCluster.
	Weights are smoothed by averaging the weight values of connected vertices.
	@param vtxList: Vertex list to smooth skinCluster weights for.
	@type vtxList: list
	@param faceConnectivity: Use face connectivity to determine connected vertices.
	@type faceConnectivity: bool
	@param showProgress: Show operation progress using the main progress bar
	@type showProgress: bool
	@param debug: Print debug messages to script editor
	@type debug: bool
	'''
	# Get Main Progress Bar
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	
	# ==========================
	# - Check Vertex Selection -
	# ==========================
	
	if not vtxList: vtxList = mc.ls(sl=1)
	
	vtxList = mc.filterExpand(vtxList,ex=True,sm=31)
	vtxSelList = glTools.utils.selection.componentListByObject(vtxList)
	if not vtxSelList: raise Exception('No valid mesh vertices specified!')
	
	# =====================================
	# - For Each Selection Element (mesh) -
	# =====================================
	
	for vtxSel in vtxSelList:
		
		vtxSel = mc.ls(vtxSel,fl=True)
		
		# Get Expanded Vertex Selection
		expSel = glTools.utils.component.expandVertexSelection(vtxSel,useFace=faceConnectivity)
		expSelComp = glTools.utils.selection.getSelectionElement(expSel,0)
		
		# Get Mesh and Connected SkinCluster
		mesh = mc.ls(vtxSel[0],o=True)[0]
		skin = glTools.utils.skinCluster.findRelatedSkinCluster(mesh)
		skinFn = glTools.utils.skinCluster.getSkinClusterFn(skin)
		
		# Get Vertex IDs and Connectivity
		vtxIDs = glTools.utils.component.singleIndexList(vtxSel)
		expIDs = glTools.utils.component.singleIndexList(expSel)
		vtxConnDict = glTools.utils.mesh.vertexConnectivityDict(	mesh=mesh,
																vtxIDs=vtxIDs,
																faceConnectivity=faceConnectivity,
																showProgress=showProgress	)
		
		# Get SkinCluster Influence List
		infList = OpenMaya.MIntArray()
		influences = mc.skinCluster(skin,q=True,inf=True)
		for inf in influences:
			infList.append(glTools.utils.skinCluster.getInfluenceIndex(skin,inf))
		infCnt = infList.length()
		
		# Get SkinCluster Weights
		wtList = OpenMaya.MDoubleArray()
		skinFn.getWeights(expSelComp[0],expSelComp[1],infList,wtList)
		
		# DEBUG
		if debug:
			print('Skin Mesh: '+mesh)
			print('SkinCluster: '+skin)
			print('SkinCluster Influence Count: '+str(infCnt))
			print('SkinCluster Influence List:')
			for inf in influences: print('\t'+inf)
		
		# ==================
		# - Smooth Weights -
		# ==================
		
		# Initialize Smooth Weights Array
		sWtList = OpenMaya.MDoubleArray(wtList)
		
		# Begin Progress Bar
		if showProgress:
			mc.progressBar( gMainProgressBar,e=True,bp=True,ii=True,status=('Smoothing Weights for "'+mesh+'" ...'),maxValue=len(vtxIDs) )
		
		# For Each Vertex
		for vtxID in vtxIDs:
			
			# Get Vertex WeightList Index
			vtxInd = expIDs.index(vtxID)
			
			# For Each Influence
			for inf in range(infCnt):
				
				# Initialize Debug String
				debugStr = ''
				
				# Get Current Influence Weight Value
				wt = wtList[(vtxInd*infCnt)+inf]
				if debug: debugStr += ('['+str(vtxID)+'] - '+influences[inf]+': '+str(wt)+'\n')
				
				# For Each Connected Vertex
				if debug: debugStr += ('['+str(vtxID)+'] - connected vertex IDs:'+str(vtxConnDict[vtxID])+'\n')
				for connID in vtxConnDict[vtxID]:
					
					# Get Connected Vertex WeightList Index
					connInd = expIDs.index(connID)
					
					# Add Connected Vertex Weight
					wt += wtList[(connInd*infCnt)+inf]
					if debug: debugStr += ('\t['+str(connID)+'] - '+influences[inf]+': '+str(wtList[(connInd*infCnt)+inf])+'\n')
				
				# Normalize Weight Value
				wt /= len(vtxConnDict[vtxID])+1
				
				# Print Debug Message
				if debug: debugStr += ('['+str(vtxID)+'] - smoothed value: '+str(wt)+'\n')
				if wt > 0.00001: print(debugStr)
				
				# Set Smoothed Weight
				sWtList.set(wt,((vtxInd*infCnt)+inf))
			
			# Update Progress Bar
			if showProgress:
				if mc.progressBar(gMainProgressBar,q=True,isCancelled=True):
					mc.progressBar(gMainProgressBar,e=True,endProgress=True)
					raise UserInterupted('Operation cancelled by user!')
				mc.progressBar(gMainProgressBar,e=True,step=1)
		
		# End Current Progress Bar
		if showProgress: mc.progressBar(gMainProgressBar,e=True,endProgress=True)
	
		# ==========================
		# - Apply Smoothed Weights -
		# ==========================
		
		# Set SkinCluster Weights
		try:
			skinFn.setWeights(expSelComp[0],expSelComp[1],infList,sWtList,True,None)
		except:
			setWeights(vtxSel,skin,list(infList),list(sWtList))
		
	# =================
	# - Return Result -
	# =================
	
	return

def setWeights(vtxList,skinCluster,infList,wtList):
	'''
	Set skinCluster weights based on the incoming arguments.
	This is a backup method for smoothWeights, if the skinFn.setWeights() command fails
	@param vtxList: Vertex list to set skinCluster weights for.
	@type vtxList: list
	@param skinCluster: The skinClsuter to set weights for.
	@type skinCluster: str
	@param infList: The influence index list to apply to the weights for.
	@type infList: list
	@param wtList: The weight list to apply to the skinCluster.
	@type wtList: list
	'''
	# Get Influence List
	#infList = mc.skinCluster(skinCluster,q=True,inf=True)
	
	# For Each Vertex
	for v in range(len(vtxList)):
		
		# Get Vertex
		vtx = vtxList[v]
		
		cmd = 'skinPercent'
		
		# For Each Influence
		infCnt = len(infList)
		for i in range(infCnt):
			
			# Get Weight Value
			wt = wtList[(v*infCnt)+i]
			if wt<0.00001: continue
			
			# Get Influence
			inf = glTools.utils.skinCluster.getInfluenceAtIndex(skinCluster,i)
			
			# Build Weight Command
			cmd += (' -tv '+inf+' '+str(round(wt,5)))
		
		# Finalize Weight Command
		cmd += (' '+skinCluster+' '+vtx)
		
		# Execute Command
		mm.eval(cmd)
		print(cmd)
	
	# Return Result
	return

def smoothFlood(skinCluster,iterations=1):
	'''
	Smooth flood all influences using artisan.
	@param skinCluster: The skinCluster to smooth flood influence weights on
	@type skinCluster: str
	@param iterations: Number of smooth iterations
	@type iterations: int
	'''
	# Check zero iterations
	if not iterations: return
	
	# Get current tool
	currentTool = mc.currentCtx()
	
	# Select geometry
	geometry = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()
	mc.select(geometry)
	
	# Get skinCluster influence list
	influenceList = mc.skinCluster(skinCluster,q=True,inf=True)
	
	# Unlock influence weights
	for influence in influenceList: mc.setAttr(influence+'.lockInfluenceWeights',0)
	
	# Initialize paint context
	skinPaintTool = 'artAttrSkinContext'
	if not mc.artAttrSkinPaintCtx(skinPaintTool,ex=True):
		mc.artAttrSkinPaintCtx(skinPaintTool,i1='paintSkinWeights.xpm',whichTool='skinWeights')
	mc.setToolTo(skinPaintTool)
	mc.artAttrSkinPaintCtx(skinPaintTool,edit=True,sao='smooth')
	
	# Smooth Weights
	for i in range(iterations):
		print(skinCluster+': Smooth Iteration - '+str(i+1))
		for influence in influenceList:
			# Lock current influence weights
			mc.setAttr(influence+'.lockInfluenceWeights',1)
			# Smooth Flood
			mm.eval('artSkinSelectInfluence artAttrSkinPaintCtx "'+influence+'" "'+influence+'"')
			mc.artAttrSkinPaintCtx(skinPaintTool,e=True,clear=True)
			# Unlock current influence weights
			mc.setAttr(influence+'.lockInfluenceWeights',0)
	
	# Reset current tool
	mc.setToolTo(currentTool)

def hotkeySetup():
	'''
	'''
	# ====================
	# - Runtime Commands -
	# ====================
	
	# Smooth Weights
	if mm.eval('runTimeCommand -q -ex rt_smoothWeights'):
		mm.eval('runTimeCommand -e -del rt_smoothWeights')
	mm.eval('runTimeCommand -annotation "" -category "User" -commandLanguage "python" -command "import glTools.tools.smoothWeights;reload(glTools.tools.smoothWeights);glTools.tools.smoothWeights.smoothWeights(mc.ls(sl=1),True,True)" rt_smoothWeights')
	
	# ========================
	# - Create Name Commands -
	# ========================
	
	smoothWtCmd = mc.nameCommand(		'smoothWeightsNameCommand',
										ann='smoothWeightsNameCommand',
										sourceType='mel',
										c='rt_smoothWeights' )
	
	# =============================
	# - Create Hotkey Assignments -
	# =============================
	
	mc.hotkey(keyShortcut='s',alt=True,name=smoothWtCmd)
