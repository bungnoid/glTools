import maya.mel as mm
import maya.cmds as mc

import glTools.tools.constraint
import glTools.utils.transform

def create(	target,
			slaveList,
			slaveAimUp=None,
			weightList=None,
			bakeAnim=False,
			bakeStartEnd=[None,None],
			offsetAnim=None,
			offset=(0,0,0),
			cleanup=False	):
	'''
	Create a lookAt constraint setup based in the input arguments
	@param target: LookAt target transform.
	@type target: str
	@param slaveList: LookAt slave transform list.
	@type slaveList: list
	@param slaveAimUp: List of slave lookAt aim and up vectors. [(aim,up),('z',x),...]
	@type slaveAimUp: list
	@param weightList: LookAt weight list. If None, use default weight list (evenly distributed).
	@type weightList: list
	@param bakeAnim: Bake lookAt animation to controls.
	@type bakeAnim: bool
	@param bakeStartEnd: Tuple containing start and end frame value.
	@type bakeStartEnd: tuple
	@param offsetAnim: Offset baked lookAt animation.
	@type offsetAnim: float or None
	@param offset: Constraint offset.
	@type offset: tuple
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Target
	if not glTools.utils.transform.isTransform(target):
		raise Exception('LookAt target "'+target+'" is not a valid transform! Unable to create lookAt setup...')
	
	# Slave List
	if not slaveList:
		raise Exception('Invalid lookAt slave list! Unable to create lookAt setup...')
	
	# Weight List
	if not weightList:
		print('Invalid lookAt weight list! Generating default lookAt weight list...')
		weightList = range(0,101,100.0/len(slaveList))[1:]
	if len(weightList) != len(slaveList):
		print('Invalid lookAt weight list! Generating default lookAt weight list...')
		weightList = range(0,101,100.0/len(slaveList))[1:]
	
	# Slave Aim/Up Vectors
	if not slaveAimUp:
		print('Invalid lookAt slave aim/up vector values! Using default lookAt vectors (aim="z",up="y")...')
		slaveAimUp = [('z','y') for slave in slaveList]
	if len(slaveAimUp) != len(slaveList):
		print('Invalid lookAt slave aim/up vector values! Using default lookAt vectors (aim="z",up="y")...')
		slaveAimUp = [('z','y') for slave in slaveList]
	
	# ===========
	# - Look At -
	# ===========
	
	slaveReferenceList = []
	slaveLookAtList = []
	slaveLookAt_aimList = []
	slaveLookAt_orientList = []
	
	slaveBakeList = []
	
	for i in range(len(slaveList)):
		
		# Check Slave Object
		if not mc.objExists(slaveList[i]):
			print('Slave object "'+slaveList[i]+'" not found! Skipping...')
			continue
		
		# Get Slave Short Name
		slaveSN = slaveList[i].split(':')[0]
		
		# Duplicate Slave to get Reference and LookAt Targets
		slaveReference = mc.duplicate(slaveList[i],po=True,n=slaveSN+'_reference')[0]
		slaveLookAt = mc.duplicate(slaveList[i],po=True,n=slaveSN+'_lookAt')[0]
		
		# Transfer Anim to Reference
		slaveKeys = mc.copyKey(slaveList[i])
		if slaveKeys: mc.pasteKey(slaveReference)
		
		# Delete Slave Rotation Anim
		mc.cutKey(slaveList[i],at=['rx','ry','rz'])
		
		# Create Slave LookAt
		slaveLookAt_aim = glTools.tools.constraint.aimConstraint(	target=target,
																	slave=slaveLookAt,
																	aim=slaveAimUp[i][0],
																	up=slaveAimUp[i][1],
																	worldUpType='scene',
																	offset=offset,
																	mo=False	)[0]
		
		# Weighted Orient Constraint
		slaveLookAt_orient = mc.orientConstraint([slaveReference,slaveLookAt],slaveList[i],mo=False)[0]
		slaveLookAt_targets = glTools.utils.constraint.targetAliasList(slaveLookAt_orient)
		
		# Set Constraint Target Weights
		mc.setAttr(slaveLookAt_orient+'.'+slaveLookAt_targets[0],1.0-(weightList[i]*0.01))
		mc.setAttr(slaveLookAt_orient+'.'+slaveLookAt_targets[1],weightList[i]*0.01)
		mc.setAttr(slaveLookAt_orient+'.interpType',2) # Shortest
		
		# Add Message Connections
		mc.addAttr(slaveList[i],ln='lookAtTarget',at='message')
		mc.addAttr(slaveList[i],ln='lookAtAnmSrc',at='message')
		mc.connectAttr(slaveLookAt+'.message',slaveList[i]+'.lookAtTarget',f=True)
		mc.connectAttr(slaveReference+'.message',slaveList[i]+'.lookAtAnmSrc',f=True)
		
		# Append Lists
		slaveReferenceList.append(slaveReference)
		slaveLookAtList.append(slaveLookAt)
		slaveLookAt_aimList.append(slaveLookAt_aim)
		slaveLookAt_orientList.append(slaveLookAt_orient)
		
		slaveBakeList.append(slaveList[i])
	
	# =============
	# - Bake Anim -
	# =============
	
	if bakeAnim:
		
		# Get Bake Range
		start = bakeStartEnd[0]
		end = bakeStartEnd[1]
		if start == None: start = mc.playbackOptions(q=True,min=True)
		if end == None: end = mc.playbackOptions(q=True,max=True)
		
		# Bake Results
		mc.refresh(suspend=True)
		#for slave in slaveBakeList:
		mc.bakeResults(slaveBakeList,t=(start,end),at=['rx','ry','rz'],simulation=True)
		mc.refresh(suspend=False)
		
		# Post Bake Cleanup
		if cleanup:
			try: mc.delete(slaveLookAt_orientList)
			except: pass
			try: mc.delete(slaveLookAt_aimList)
			except: pass
			try: mc.delete(slaveReferenceList)
			except: pass
			try: mc.delete(slaveLookAtList)
			except: pass
	
	# ====================
	# - Bake Anim Offset -
	# ====================
	
	if offsetAnim != None:
		
		# For Each Slave Object
		for slave in slaveList:
			
			# Check Slave Object
			if not mc.objExists(slave):
				print('Slave object "'+slave+'" not found! Skipping...')
				continue
			
			# Offset Rotate Channels
			for r in ['rx','ry','rz']:
				mc.keyframe(slave+'.'+r,e=True,relative=True,timeChange=offsetAnim)
	
	# =================
	# - Return Result -
	# =================
	
	return slaveList

def isApplied(slaveList):
	'''
	'''
	pass

def remove(slaveList):
	'''
	'''
	pass
